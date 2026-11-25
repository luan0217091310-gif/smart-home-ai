"""Lớp bọc ObjectDetector (YOLOE-26, dự phòng YOLO-World). Đổi mô hình qua OBJECT_MODEL trong .env."""
from __future__ import annotations

import logging
import os

import numpy as np

from services.worker_object.logic import Detection
from shared.config import env, models_dir

log = logging.getLogger("object_detector")


def _resolve_weights(name: str) -> str:
    p = models_dir() / name
    return str(p) if p.exists() else name


class ObjectDetector:
    def __init__(self, model_name: str | None = None, device: str | None = None):
        os.environ.setdefault("YOLO_CONFIG_DIR", str(models_dir() / "ultralytics"))
        from ultralytics import YOLO

        self.model_name = model_name or env("OBJECT_MODEL", "yoloe-26s-seg.pt")
        self.device = device or env("OBJECT_DEVICE", None)
        cwd = os.getcwd()
        os.chdir(models_dir())  # tải trọng số + bộ mã hóa chữ vào models/ để không tải lại
        try:
            try:
                self.model = YOLO(_resolve_weights(self.model_name))
            except Exception as e:  # noqa: BLE001
                log.warning("Không nạp được %s (%s) → dự phòng yolov8s-worldv2.pt", self.model_name, e)
                self.model_name = "yolov8s-worldv2.pt"
                self.model = YOLO(_resolve_weights(self.model_name))
        finally:
            os.chdir(cwd)
        self.classes: list[str] = []
        log.info("Đã nạp mô hình đồ vật %s", self.model_name)

    def set_classes(self, keywords: list[str]) -> None:
        keywords = [k for k in dict.fromkeys(keywords) if k]
        if keywords == self.classes:
            return
        cwd = os.getcwd()
        os.chdir(models_dir())
        try:
            if "yoloe" in self.model_name.lower():
                try:
                    self.model.set_classes(keywords, self.model.get_text_pe(keywords))
                except (AttributeError, TypeError):
                    self.model.set_classes(keywords)
            else:
                self.model.set_classes(keywords)
        finally:
            os.chdir(cwd)
        self.classes = keywords
        log.info("Danh sách từ khóa: %s", ", ".join(keywords))

    def detect(self, image_bgr: np.ndarray, conf: float = 0.1) -> list[Detection]:
        if not self.classes:
            return []
        res = self.model.predict(image_bgr, conf=conf, verbose=False, device=self.device)[0]
        out = []
        for box in res.boxes:
            cls = int(box.cls[0])
            kw = self.classes[cls] if cls < len(self.classes) else str(cls)
            out.append(Detection(kw, float(box.conf[0]), tuple(float(v) for v in box.xyxy[0].tolist())))
        return out
