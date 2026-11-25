"""GĐ 7: đăng ký bổ sung khuôn mặt từ chính camera đang dùng.

Đứng trước camera, xoay nhẹ đầu; script lấy khung từ Redis, chỉ nhận khung có ĐÚNG một mặt đủ lớn,
chấm điểm (độ nét × cỡ mặt × det_score), giữ 5–10 ảnh tốt nhất, khác nhau, lưu vào data/faces/<ten>/ rồi đăng ký lại.

  python scripts/capture_faces.py --name Bo --seconds 30 --keep 8
"""
import _bootstrap  # noqa: F401
import argparse
import time

import cv2
import numpy as np

from services.worker_face.engine import FaceEngine
from services.worker_face.enroll import enroll_and_save
from shared.config import camera_id, data_dir, now, settings, setup_logging
from shared.database import DB
from shared.frame_bus import FrameBus, LatestFrameReader
from shared.snapshots import crop

log = setup_logging("capture_faces")
ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True)
ap.add_argument("--role", default="family")
ap.add_argument("--seconds", type=float, default=30)
ap.add_argument("--keep", type=int, default=8)
args = ap.parse_args()

min_px = max(100, settings().get("face", {}).get("min_face_size_px", 60))
engine, bus = FaceEngine(), FrameBus()
reader = LatestFrameReader(bus, camera_id())
cands = []  # (score, embedding, crop)
log.info("Bắt đầu chụp %s trong %.0f giây — nhìn camera, xoay nhẹ trái/phải/lên/xuống", args.name, args.seconds)
end = time.time() + args.seconds
while time.time() < end:
    f = reader.next()
    if f is None:
        time.sleep(0.05)
        continue
    faces = engine.detect(f.image)
    if len(faces) != 1:
        continue
    face = faces[0]
    x1, y1, x2, y2 = face.bbox
    size = min(x2 - x1, y2 - y1)
    if size < min_px:
        continue
    c = crop(f.image, face.bbox, 0.4)
    sharp = cv2.Laplacian(cv2.cvtColor(c, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    cands.append((sharp * size * face.det_score, face.embedding, c))
    time.sleep(0.3)

cands.sort(key=lambda t: -t[0])
chosen = []
for score, emb, c in cands:  # chọn ảnh tốt nhất nhưng không trùng lặp (đa dạng góc mặt)
    if all(float(emb @ e) < 0.92 for _, e, _ in chosen):
        chosen.append((score, emb, c))
    if len(chosen) >= args.keep:
        break
if len(chosen) < 5:
    raise SystemExit(f"Chỉ được {len(chosen)} ảnh tốt (cần ≥ 5). Đứng gần hơn, đủ sáng, thử lại.")
folder = data_dir() / "faces" / args.name
folder.mkdir(parents=True, exist_ok=True)
stamp = f"{now():%Y%m%d_%H%M%S}"
for i, (_, _, c) in enumerate(chosen):
    cv2.imencode(".jpg", c)[1].tofile(str(folder / f"cam_{stamp}_{i}.jpg"))
(folder / "role.txt").write_text(args.role, encoding="utf-8")
r = enroll_and_save(engine, DB(), folder, args.role)
bus.bump_members_version()
sims = r.self_similarity()
log.info("Đã lưu %d ảnh, đăng ký %s với %d ảnh (tương đồng TB %.3f)", len(chosen), args.name, len(r.used),
         float(np.mean(sims)) if sims else 0)
