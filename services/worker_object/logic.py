"""Logic thuần cho đồ vật: chọn phát hiện tốt nhất, chống nhảy vùng do nhiễu."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Detection:
    keyword: str
    confidence: float
    bbox: tuple  # x1, y1, x2, y2 pixel

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return (x1 + x2) / 2, (y1 + y2) / 2


def best_per_keyword(dets: list[Detection], min_conf: float) -> dict[str, Detection]:
    out: dict[str, Detection] = {}
    for d in dets:
        if d.confidence < min_conf:
            continue
        if d.keyword not in out or d.confidence > out[d.keyword].confidence:
            out[d.keyword] = d
    return out


@dataclass
class ZoneStabilizer:
    """Chỉ đổi vùng khi thấy đồ vật ở vùng MỚI `confirm_cycles` chu kỳ liên tiếp.
    Lần đầu thấy (chưa có vùng) thì nhận ngay."""
    confirm_cycles: int = 2
    current: dict = field(default_factory=dict)     # object_id -> zone
    pending: dict = field(default_factory=dict)     # object_id -> (zone, count)

    def seed(self, object_id: int, zone: str | None) -> None:
        if zone:
            self.current[object_id] = zone

    def observe(self, object_id: int, zone: str) -> str | None:
        """Trả về vùng mới nếu vùng thay đổi được xác nhận (hoặc lần đầu), ngược lại None."""
        cur = self.current.get(object_id)
        if cur is None:
            self.current[object_id] = zone
            self.pending.pop(object_id, None)
            return zone
        if zone == cur:
            self.pending.pop(object_id, None)
            return None
        pz, cnt = self.pending.get(object_id, (zone, 0))
        cnt = cnt + 1 if pz == zone else 1
        if cnt >= self.confirm_cycles:
            self.current[object_id] = zone
            self.pending.pop(object_id, None)
            return zone
        self.pending[object_id] = (zone, cnt)
        return None
