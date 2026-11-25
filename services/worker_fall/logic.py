"""Logic thuần phát hiện té ngã: Bình thường → Đang ngã → Đang nằm → Xác nhận.

Lớp 1 — vận tốc rơi: trung điểm vai–hông đi XUỐNG nhanh (trục Y ảnh hướng xuống ⇒ Y TĂNG),
        chia cho chiều cao người lúc đứng; tính theo `ts` thật của khung.
Lớp 2 — tư thế nằm (trong `lying_window_s`): tỷ lệ rộng/cao > `lying_aspect_ratio` HOẶC thân nghiêng > `torso_tilt_deg`.
Lớp 3 — vùng và bất động: hông KHÔNG nằm trong vùng `safe_rest`, điểm khớp gần như đứng yên `still_seconds` giây.
Đứng dậy trước khi đủ thời gian → huỷ.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

# Chỉ số COCO-17
L_SH, R_SH, L_HIP, R_HIP = 5, 6, 11, 12

NORMAL, FALLING, LYING, CONFIRMED = "normal", "falling", "lying", "confirmed"


@dataclass
class FallParams:
    keypoint_min_conf: float = 0.5
    drop_speed_threshold: float = 0.8   # chiều cao người / giây
    drop_window_s: float = 1.0
    lying_window_s: float = 2.0
    lying_aspect_ratio: float = 1.2
    torso_tilt_deg: float = 60.0
    still_seconds: float = 4.0
    still_motion_ratio: float = 0.08

    @classmethod
    def from_settings(cls, cfg: dict) -> "FallParams":
        kw = {k: cfg[k] for k in cls.__dataclass_fields__ if k in cfg and cfg[k] is not None}
        return cls(**kw)


def _mean_pt(kps: np.ndarray, idx: list[int], min_conf: float) -> np.ndarray | None:
    pts = [kps[i, :2] for i in idx if kps[i, 2] >= min_conf]
    return np.mean(pts, axis=0) if pts else None


def torso_tilt_deg(kps: np.ndarray, min_conf: float) -> float | None:
    """Góc thân (hông → vai) so với phương thẳng đứng, 0° = đứng thẳng, 90° = nằm ngang."""
    sh = _mean_pt(kps, [L_SH, R_SH], min_conf)
    hip = _mean_pt(kps, [L_HIP, R_HIP], min_conf)
    if sh is None or hip is None:
        return None
    dx, dy = sh[0] - hip[0], sh[1] - hip[1]
    if dx == 0 and dy == 0:
        return None
    return math.degrees(math.atan2(abs(dx), abs(dy)))


@dataclass
class PersonState:
    state: str = NORMAL
    height: float | None = None               # chiều cao người lúc đứng (px)
    history: deque = field(default_factory=lambda: deque(maxlen=64))  # (ts, mid_y)
    t_fall: float = 0.0
    still_since: float = 0.0
    anchor_kps: np.ndarray | None = None      # điểm khớp mốc để đo bất động
    last_seen: float = 0.0


class FallDetector:
    def __init__(self, params: FallParams, zone_type_at: Callable[[float, float], str | None] | None = None):
        """zone_type_at(x_norm, y_norm) → loại vùng ('safe_rest', 'floor', …) hoặc None."""
        self.p = params
        self.zone_type_at = zone_type_at or (lambda x, y: None)
        self.people: dict[int, PersonState] = {}

    def _is_lying(self, bbox, kps) -> bool:
        x1, y1, x2, y2 = bbox
        w, h = x2 - x1, max(1e-6, y2 - y1)
        tilt = torso_tilt_deg(kps, self.p.keypoint_min_conf)
        return (w / h) > self.p.lying_aspect_ratio or (tilt is not None and tilt > self.p.torso_tilt_deg)

    def _motion(self, st: PersonState, kps: np.ndarray) -> float:
        """Dịch chuyển trung bình so với điểm mốc, theo đơn vị chiều cao người."""
        if st.anchor_kps is None or not st.height:
            return 0.0
        m = (kps[:, 2] >= self.p.keypoint_min_conf) & (st.anchor_kps[:, 2] >= self.p.keypoint_min_conf)
        if not m.any():
            return 0.0
        return float(np.linalg.norm(kps[m, :2] - st.anchor_kps[m, :2], axis=1).mean() / st.height)

    def update(self, track_id: int, ts: float, bbox, kps: np.ndarray, frame_wh: tuple[int, int]) -> str | None:
        """Cập nhật 1 người. Trả về 'confirmed' đúng một lần khi xác nhận ngã, ngược lại None."""
        kps = np.asarray(kps, dtype=np.float32)
        st = self.people.setdefault(track_id, PersonState())
        st.last_seen = ts
        x1, y1, x2, y2 = bbox
        bw, bh = x2 - x1, y2 - y1
        lying = self._is_lying(bbox, kps)
        # chiều cao lúc đứng: cập nhật khi người đứng thẳng
        if not lying and bh > bw and st.state == NORMAL:
            st.height = bh if st.height is None else 0.8 * st.height + 0.2 * bh
        mid = _mean_pt(kps, [L_SH, R_SH, L_HIP, R_HIP], self.p.keypoint_min_conf)
        if mid is not None:
            st.history.append((ts, float(mid[1])))
        hip = _mean_pt(kps, [L_HIP, R_HIP], self.p.keypoint_min_conf)
        motion = self._motion(st, kps)
        event = None

        if st.state == NORMAL:
            if st.height and self._drop_speed(st, ts) >= self.p.drop_speed_threshold:
                st.state, st.t_fall = FALLING, ts
        if st.state == FALLING:
            if lying:
                st.state, st.still_since, st.anchor_kps = LYING, ts, kps
            elif ts - st.t_fall > self.p.lying_window_s:
                st.state = NORMAL
        elif st.state == LYING:
            in_safe = hip is not None and self.zone_type_at(hip[0] / frame_wh[0], hip[1] / frame_wh[1]) == "safe_rest"
            if not lying or in_safe:
                st.state = NORMAL          # đứng dậy hoặc nằm trên sofa/giường → huỷ
                st.history.clear()
            else:
                if motion > self.p.still_motion_ratio:
                    st.still_since, st.anchor_kps = ts, kps
                if ts - st.still_since >= self.p.still_seconds:
                    st.state, event = CONFIRMED, CONFIRMED
        elif st.state == CONFIRMED and not lying:
            st.state = NORMAL
            st.history.clear()
        return event

    def _drop_speed(self, st: PersonState, ts: float) -> float:
        """Tốc độ đi xuống lớn nhất trong cửa sổ drop_window_s, theo đơn vị chiều-cao-người/giây."""
        if len(st.history) < 2 or not st.height:
            return 0.0
        t_now, y_now = st.history[-1]
        best = 0.0
        for t, y in st.history:
            dt = t_now - t
            if dt <= 0.15 or dt > self.p.drop_window_s:
                continue
            best = max(best, (y_now - y) / st.height / dt)   # Y tăng = đi xuống
        return best

    def forget_stale(self, now_ts: float, max_age_s: float = 10.0) -> None:
        for tid in [t for t, s in self.people.items() if now_ts - s.last_seen > max_age_s]:
            del self.people[tid]
