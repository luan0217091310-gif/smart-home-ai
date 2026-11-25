"""Lưu ảnh chụp vào data/snapshots/. CSDL lưu đường dẫn TƯƠNG ĐỐI so với data/ để dùng được cả trong và ngoài Docker."""
from __future__ import annotations

import time
import unicodedata
from pathlib import Path

import cv2
import numpy as np

from shared.config import data_dir, now


def ascii_text(s: str) -> str:
    """OpenCV không vẽ được dấu tiếng Việt → bỏ dấu khi vẽ lên ảnh."""
    s = s.replace("đ", "d").replace("Đ", "D")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def save_snapshot(kind: str, image: np.ndarray, suffix: str = "", fixed_name: str | None = None) -> str:
    """Lưu ảnh, trả về đường dẫn tương đối (vd. 'snapshots/stranger/20261125_203105_123.jpg')."""
    folder = data_dir() / "snapshots" / kind
    folder.mkdir(parents=True, exist_ok=True)
    name = fixed_name or f"{now():%Y%m%d_%H%M%S}_{int(time.time() * 1000) % 1000:03d}{suffix}.jpg"
    path = folder / name
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if ok:
        buf.tofile(str(path))
    return path.relative_to(data_dir()).as_posix()


def resolve(rel_path: str | None) -> Path | None:
    if not rel_path:
        return None
    p = Path(rel_path)
    return p if p.is_absolute() else data_dir() / p


def draw_box(image: np.ndarray, bbox, label: str, color=(0, 0, 255)) -> np.ndarray:
    x1, y1, x2, y2 = (int(v) for v in bbox)
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    cv2.putText(image, ascii_text(label), (x1, max(15, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return image


def crop(image: np.ndarray, bbox, pad: float = 0.25) -> np.ndarray:
    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox
    pw, ph = (x2 - x1) * pad, (y2 - y1) * pad
    x1, y1 = max(0, int(x1 - pw)), max(0, int(y1 - ph))
    x2, y2 = min(w, int(x2 + pw)), min(h, int(y2 + ph))
    return image[y1:y2, x1:x2].copy()
