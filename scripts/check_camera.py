"""GĐ 0: mở CAMERA_SOURCE bằng OpenCV, đọc 1 khung hình, lưu data/camera_check.jpg."""
import _bootstrap  # noqa: F401
import sys

import cv2

from shared.config import data_dir, env, setup_logging
from services.stream_producer.capture import open_capture

log = setup_logging("check_camera")
src = env("CAMERA_SOURCE", "0")
cap = open_capture(src)
ok, frame = cap.read() if cap.isOpened() else (False, None)
cap.release()
if not ok:
    sys.exit(f"Không đọc được khung hình từ nguồn: {src if not str(src).startswith('rtsp') else 'rtsp://***'}")
out = data_dir() / "camera_check.jpg"
cv2.imwrite(str(out), frame)
log.info("Đọc được khung %dx%d, đã lưu %s", frame.shape[1], frame.shape[0], out)
