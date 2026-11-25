"""Đăng ký khuôn mặt từ data/faces/<ten>/: bỏ ảnh không có mặt hoặc nhiều mặt, lấy vector trung bình."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from services.worker_face.logic import l2_normalize, mean_embedding

log = logging.getLogger("enroll")
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass
class EnrollResult:
    name: str
    used: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    embedding: np.ndarray | None = None
    vectors: list[np.ndarray] = field(default_factory=list)

    def self_similarity(self) -> list[float]:
        if self.embedding is None:
            return []
        return [float(v @ self.embedding) for v in self.vectors]


def read_image(path: Path) -> np.ndarray | None:
    # imdecode để đọc được đường dẫn có dấu tiếng Việt trên Windows
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def enroll_person(engine, folder: Path) -> EnrollResult:  # noqa: ANN001
    res = EnrollResult(folder.name)
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in IMG_EXT:
            continue
        img = read_image(p)
        if img is None:
            res.skipped.append((p.name, "không đọc được ảnh"))
            continue
        faces = engine.detect(img)
        if len(faces) == 0:
            res.skipped.append((p.name, "không thấy khuôn mặt"))
        elif len(faces) > 1:
            res.skipped.append((p.name, f"có {len(faces)} khuôn mặt"))
        else:
            res.used.append(p.name)
            res.vectors.append(l2_normalize(faces[0].embedding))
    if res.vectors:
        res.embedding = mean_embedding(res.vectors)
    return res


def enroll_and_save(engine, db, folder: Path, role: str = "family", min_images: int = 1) -> EnrollResult:  # noqa: ANN001
    res = enroll_person(engine, folder)
    if res.embedding is not None and len(res.used) >= min_images:
        db.upsert_member(res.name, res.embedding, len(res.used), role)
    return res


def cross_similarity(results: list[EnrollResult]) -> list[tuple[str, str, float]]:
    out = []
    for i, a in enumerate(results):
        for b in results[i + 1:]:
            if a.embedding is not None and b.embedding is not None:
                out.append((a.name, b.name, float(a.embedding @ b.embedding)))
    return out
