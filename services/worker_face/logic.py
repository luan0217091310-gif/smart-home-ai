"""Logic thuần cho nhận diện mặt: cosine, theo dấu IoU, quy tắc quyết định thành viên / người lạ."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def l2_normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def mean_embedding(vectors: list[np.ndarray]) -> np.ndarray:
    """Chuẩn hóa từng vector, lấy trung bình, chuẩn hóa lại."""
    return l2_normalize(l2_normalize(np.stack(vectors)).mean(axis=0))


def best_match(embedding: np.ndarray, gallery: np.ndarray, names: list) -> tuple[int, float]:
    """Trả về (chỉ số thành viên giống nhất, cosine). gallery: (M,512) đã chuẩn hóa. Rỗng → (-1, 0)."""
    if gallery is None or len(gallery) == 0:
        return -1, 0.0
    sims = gallery @ l2_normalize(embedding)
    i = int(np.argmax(sims))
    return i, float(sims[i])


def iou(a, b) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    iw, ih = max(0.0, min(ax2, bx2) - max(ax1, bx1)), max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / union if union > 0 else 0.0


@dataclass
class FaceTrack:
    track_id: int
    bbox: tuple
    below_count: int = 0      # số khung liên tiếp dưới ngưỡng
    missed: int = 0
    stranger_reported: bool = False


@dataclass
class Decision:
    kind: str                 # member | stranger | undecided
    track_id: int
    member_index: int = -1
    score: float = 0.0
    bbox: tuple = ()


@dataclass
class FaceDecider:
    """Theo dấu mặt qua các khung bằng IoU và áp quy tắc:
    - score ≥ threshold → member (reset bộ đếm dưới ngưỡng).
    - score < stranger_threshold `stranger_frames` khung liên tiếp (cùng track) → stranger (1 lần / track).
    - ở giữa hai ngưỡng (quay đầu, đi xa, mờ) → undecided và reset bộ đếm: không kết luận.
    """
    threshold: float = 0.55
    stranger_threshold: float | None = None   # None = bằng threshold (hành vi 2 vùng cũ)
    stranger_frames: int = 3
    iou_threshold: float = 0.3
    max_missed: int = 6
    tracks: dict = field(default_factory=dict)
    _next_id: int = 1

    def _assign(self, bboxes: list) -> list[int]:
        ids, used = [], set()
        for b in bboxes:
            best, best_iou = None, self.iou_threshold
            for tid, t in self.tracks.items():
                if tid in used:
                    continue
                v = iou(b, t.bbox)
                if v >= best_iou:
                    best, best_iou = tid, v
            if best is None:
                best = self._next_id
                self._next_id += 1
                self.tracks[best] = FaceTrack(best, tuple(b))
            used.add(best)
            self.tracks[best].bbox, self.tracks[best].missed = tuple(b), 0
            ids.append(best)
        for tid in list(self.tracks):
            if tid not in used:
                self.tracks[tid].missed += 1
                if self.tracks[tid].missed > self.max_missed:
                    del self.tracks[tid]
        return ids

    def update(self, faces: list[tuple[tuple, int, float]]) -> list[Decision]:
        """faces: danh sách (bbox, member_index, score) của các mặt hợp lệ trong khung."""
        ids = self._assign([f[0] for f in faces])
        out = []
        for (bbox, idx, score), tid in zip(faces, ids):
            t = self.tracks[tid]
            if idx >= 0 and score >= self.threshold:
                t.below_count, t.stranger_reported = 0, False
                out.append(Decision("member", tid, idx, score, bbox))
                continue
            st = self.threshold if self.stranger_threshold is None else self.stranger_threshold
            if score >= st:
                t.below_count = 0
                out.append(Decision("undecided", tid, idx, score, bbox))
                continue
            t.below_count += 1
            if t.below_count >= self.stranger_frames and not t.stranger_reported:
                t.stranger_reported = True
                out.append(Decision("stranger", tid, idx, score, bbox))
            else:
                out.append(Decision("undecided", tid, idx, score, bbox))
        return out


def face_big_enough(bbox, min_px: int) -> bool:
    x1, y1, x2, y2 = bbox
    return min(x2 - x1, y2 - y1) >= min_px
