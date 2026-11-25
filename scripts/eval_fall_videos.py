"""Chạy bộ video kiểm thử té ngã, in bảng kết quả và tốc độ rơi lớn nhất của từng video (để chọn ngưỡng).

Cấu trúc:  data/test_videos/fall/*.mp4   (cảnh ngã thật trên nệm)
           data/test_videos/normal/*.mp4 (ngồi phịch, nằm sofa, cúi, ngồi xổm, tập thể dục…)
Chạy trong container (cần ultralytics):
  docker compose run --rm worker_fall python scripts/eval_fall_videos.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2  # noqa: E402

from services.worker_fall.logic import CONFIRMED, FallDetector, FallParams  # noqa: E402
from services.worker_fall.main import PoseEstimator  # noqa: E402
from shared.config import data_dir, settings  # noqa: E402
from shared.zones import ZoneMap  # noqa: E402

root = data_dir() / "test_videos"
zones = ZoneMap.load()
params = FallParams.from_settings(settings().get("fall", {}))
rows, pose = [], None
for label in ("fall", "normal"):
    for vid in sorted((root / label).glob("*.mp4")):
        pose = PoseEstimator()  # mô hình mới cho mỗi video để reset bộ theo dấu
        det = FallDetector(params, lambda x, y: (z.type if (z := zones.find_zone(x, y)) else None))
        cap = cv2.VideoCapture(str(vid))
        fps = cap.get(cv2.CAP_PROP_FPS) or 15
        step = max(1, round(fps / settings().get("fall", {}).get("fps", 15)))
        i, alarms, max_speed = 0, 0, 0.0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % step == 0:
                h, w = frame.shape[:2]
                for tid, bbox, kps in pose.track(frame):
                    if det.update(tid, i / fps, bbox, kps, (w, h)) == CONFIRMED:
                        alarms += 1
                    st = det.people.get(tid)
                    if st:
                        max_speed = max(max_speed, det._drop_speed(st, i / fps))
            i += 1
        ok_ = (alarms > 0) == (label == "fall")
        rows.append((label, vid.name, alarms, max_speed, ok_))

print(f"{'loại':7} {'video':30} {'báo':>4} {'tốc độ rơi max':>15}  kết quả")
for label, name, alarms, sp, ok_ in rows:
    print(f"{label:7} {name:30} {alarms:>4} {sp:>15.2f}  {'ĐÚNG' if ok_ else 'SAI'}")
falls = [r for r in rows if r[0] == "fall"]
normals = [r for r in rows if r[0] == "normal"]
print(f"\nBắt đúng ngã: {sum(r[4] for r in falls)}/{len(falls)} | Báo nhầm: {sum(not r[4] for r in normals)}/{len(normals)}")
if falls and normals:
    print(f"Gợi ý drop_speed_threshold nằm giữa max(normal)={max(r[3] for r in normals):.2f} "
          f"và min(fall)={min(r[3] for r in falls):.2f}")
