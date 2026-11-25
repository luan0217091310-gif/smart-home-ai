"""Xem hình từ Redis, in FPS thực và độ trễ trong hệ thống (now - ts).

  python scripts/view_stream.py                 # mở cửa sổ (cần opencv-python có GUI)
  python scripts/view_stream.py --snapshot      # lưu 1 ảnh tĩnh vào data/snapshot_<camera>.jpg
  python scripts/view_stream.py --headless --seconds 60   # chỉ đo, không mở cửa sổ
"""
import _bootstrap  # noqa: F401
import argparse
import statistics
import time

import cv2

from shared.config import camera_id, data_dir, setup_logging
from shared.frame_bus import FrameBus, LatestFrameReader

log = setup_logging("view_stream")
ap = argparse.ArgumentParser()
ap.add_argument("--camera", default=camera_id())
ap.add_argument("--snapshot", action="store_true")
ap.add_argument("--headless", action="store_true")
ap.add_argument("--seconds", type=float, default=0)
args = ap.parse_args()

bus = FrameBus()
reader = LatestFrameReader(bus, args.camera)

if args.snapshot:
    deadline = time.time() + 10
    while (f := bus.get_latest(args.camera)) is None and time.time() < deadline:
        time.sleep(0.2)
    if f is None:
        raise SystemExit("Chưa có khung hình trong Redis — stream_producer đã chạy chưa?")
    out = data_dir() / f"snapshot_{args.camera}.jpg"
    cv2.imwrite(str(out), f.image)
    log.info("Đã lưu ảnh tĩnh %s (%dx%d)", out, f.image.shape[1], f.image.shape[0])
    raise SystemExit(0)

lat, n, t0, start = [], 0, time.time(), time.time()
while True:
    f = reader.next()
    if f is None:
        time.sleep(0.005)
    else:
        n += 1
        lat.append((time.time() - f.ts) * 1000)
        if not args.headless:
            img = f.image.copy()
            cv2.putText(img, f"{args.camera} #{f.frame_id} lat {lat[-1]:.0f}ms", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("smart-home-ai", img)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    if time.time() - t0 >= 2 and lat:
        log.info("FPS %.1f | độ trễ TB %.0f ms | p95 %.0f ms", n / (time.time() - t0),
                 statistics.mean(lat), sorted(lat)[int(len(lat) * 0.95) - 1])
        n, t0, lat = 0, time.time(), []
    if args.seconds and time.time() - start > args.seconds:
        break
