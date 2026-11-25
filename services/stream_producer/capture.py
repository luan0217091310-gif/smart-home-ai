"""Mở nguồn video (webcam / RTSP / file) và đọc khung trong luồng riêng, chỉ giữ khung mới nhất."""
from __future__ import annotations

import os
import threading
import time

import cv2
import numpy as np


def parse_source(src: str | int) -> tuple[str, str | int]:
    """Trả về (kind, value): kind ∈ webcam | rtsp | file."""
    s = str(src).strip()
    if s.isdigit():
        return "webcam", int(s)
    if s.lower().startswith(("rtsp://", "rtsps://", "http://", "https://")):
        return "rtsp", s
    return "file", s


def open_capture(src: str | int) -> cv2.VideoCapture:
    kind, value = parse_source(src)
    if kind == "rtsp":
        os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp")  # ép TCP cho ổn định
        cap = cv2.VideoCapture(value, cv2.CAP_FFMPEG)
    elif kind == "webcam":
        cap = cv2.VideoCapture(value, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(value)
    else:
        cap = cv2.VideoCapture(value)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:  # noqa: BLE001
        pass
    return cap


def mask_source(src: str) -> str:
    """Ẩn user:pass trong link RTSP khi ghi log."""
    s = str(src)
    if "@" in s and "://" in s:
        scheme, rest = s.split("://", 1)
        return f"{scheme}://***@{rest.split('@', 1)[1]}"
    return s


def resize_to_width(frame: np.ndarray, width: int) -> np.ndarray:
    h, w = frame.shape[:2]
    if width <= 0 or w <= width:
        return frame
    return cv2.resize(frame, (width, int(h * width / w)), interpolation=cv2.INTER_AREA)


def backoff_delay(attempt: int, max_s: float = 30.0) -> float:
    """1, 2, 4, 8… giây, tối đa max_s."""
    return float(min(max_s, 2 ** max(0, attempt)))


class LatestGrabber:
    """Luồng nền đọc liên tục; read() trả khung mới nhất + thời điểm chụp. File video thì phát lặp theo FPS gốc."""

    def __init__(self, src: str | int):
        self.src = src
        self.kind, _ = parse_source(src)
        self.cap = open_capture(src)
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._ts = 0.0
        self._seq = 0
        self.alive = self.cap.isOpened()
        self._stop = False
        self._file_period = 0.0
        if self.kind == "file" and self.alive:
            fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
            self._file_period = 1.0 / fps
        self._t = threading.Thread(target=self._loop, daemon=True)
        if self.alive:
            self._t.start()

    def _loop(self) -> None:
        fails = 0
        while not self._stop:
            ok, frame = self.cap.read()
            if not ok:
                if self.kind == "file":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # phát lặp
                    fails += 1
                    if fails > 5:
                        self.alive = False
                        return
                    continue
                fails += 1
                if fails >= 30:
                    self.alive = False
                    return
                time.sleep(0.05)
                continue
            fails = 0
            with self._lock:
                self._frame, self._ts, self._seq = frame, time.time(), self._seq + 1
            if self._file_period:
                time.sleep(self._file_period)

    def read(self) -> tuple[np.ndarray | None, float, int]:
        with self._lock:
            return self._frame, self._ts, self._seq

    def release(self) -> None:
        self._stop = True
        if self._t.is_alive():
            self._t.join(timeout=2)
        self.cap.release()
