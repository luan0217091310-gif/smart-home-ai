"""Lớp bọc mô hình khuôn mặt (InsightFace). Đổi mô hình chỉ cần đổi FACE_MODEL trong .env."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from shared.config import env, models_dir, settings

log = logging.getLogger("face_engine")


@dataclass
class DetectedFace:
    bbox: tuple          # x1, y1, x2, y2 (pixel)
    det_score: float
    embedding: np.ndarray  # 512, đã chuẩn hóa


class FaceEngine:
    def __init__(self, model_name: str | None = None, det_size: int | None = None):
        from insightface.app import FaceAnalysis  # import muộn để test logic không cần insightface

        model_name = model_name or env("FACE_MODEL", "buffalo_l")
        det_size = det_size or int(settings().get("face", {}).get("det_size", 640))
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.app = FaceAnalysis(name=model_name, root=str(models_dir() / "insightface"), providers=providers,
                                allowed_modules=["detection", "recognition"])
        self.app.prepare(ctx_id=0, det_size=(det_size, det_size))
        log.info("Đã nạp mô hình khuôn mặt %s (det_size=%d)", model_name, det_size)

    def detect(self, image_bgr: np.ndarray) -> list[DetectedFace]:
        out = []
        for f in self.app.get(image_bgr):
            out.append(DetectedFace(tuple(float(x) for x in f.bbox), float(f.det_score),
                                    np.asarray(f.normed_embedding, dtype=np.float32)))
        return out
