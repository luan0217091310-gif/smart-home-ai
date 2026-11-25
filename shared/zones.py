"""Đọc data/zones.json (nguồn gốc), đồng bộ vào bảng zones, tìm vùng chứa một điểm.

Tọa độ theo tỷ lệ 0–1. Điểm thuộc nhiều vùng → chọn vùng có diện tích nhỏ nhất.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from shared.config import data_dir

ZONE_TYPES = ("furniture", "safe_rest", "floor", "door")


@dataclass
class ZoneDef:
    name: str
    type: str
    polygon: np.ndarray  # (N,2) float32, tỷ lệ 0–1

    @property
    def area(self) -> float:
        return float(abs(cv2.contourArea(self.polygon)))

    def contains(self, x: float, y: float) -> bool:
        return cv2.pointPolygonTest(self.polygon, (float(x), float(y)), False) >= 0


class ZoneMap:
    def __init__(self, camera_id: str, zones: list[ZoneDef]):
        self.camera_id = camera_id
        self.zones = sorted(zones, key=lambda z: z.area)  # nhỏ trước

    @classmethod
    def from_dict(cls, data: dict) -> "ZoneMap":
        zones = []
        for z in data.get("zones", []):
            if z.get("type", "furniture") not in ZONE_TYPES:
                raise ValueError(f"Loại vùng không hợp lệ: {z.get('type')}")
            zones.append(ZoneDef(z["name"], z.get("type", "furniture"),
                                 np.asarray(z["polygon"], dtype=np.float32).reshape(-1, 2)))
        return cls(data.get("camera_id", "cam_test"), zones)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "ZoneMap":
        path = Path(path or data_dir() / "zones.json")
        if not path.exists():
            return cls("cam_test", [])
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def find_zone(self, x: float, y: float) -> ZoneDef | None:
        """x, y theo tỷ lệ 0–1. Trả vùng nhỏ nhất chứa điểm, hoặc None."""
        for z in self.zones:
            if z.contains(x, y):
                return z
        return None

    def find_zone_px(self, x: float, y: float, width: int, height: int) -> ZoneDef | None:
        return self.find_zone(x / width, y / height)

    def to_dict(self) -> dict:
        return {"camera_id": self.camera_id,
                "zones": [{"name": z.name, "type": z.type, "polygon": z.polygon.round(4).tolist()} for z in self.zones]}

    def sync_to_db(self, db) -> None:  # noqa: ANN001
        db.replace_zones(self.camera_id, self.to_dict()["zones"])

    def draw(self, image: np.ndarray, alpha: float = 0.35) -> np.ndarray:
        """Tô màu các vùng lên ảnh để kiểm tra bằng mắt."""
        colors = {"furniture": (0, 165, 255), "safe_rest": (0, 200, 0), "floor": (200, 120, 0), "door": (180, 0, 180)}
        h, w = image.shape[:2]
        overlay, out = image.copy(), image.copy()
        for z in sorted(self.zones, key=lambda z: -z.area):
            pts = (z.polygon * [w, h]).astype(np.int32)
            cv2.fillPoly(overlay, [pts], colors.get(z.type, (128, 128, 128)))
        out = cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0)
        for z in self.zones:
            pts = (z.polygon * [w, h]).astype(np.int32)
            cv2.polylines(out, [pts], True, colors.get(z.type, (128, 128, 128)), 2)
            cx, cy = pts.mean(axis=0).astype(int)
            cv2.putText(out, f"{z.name} ({z.type})", (cx - 60, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        return out
