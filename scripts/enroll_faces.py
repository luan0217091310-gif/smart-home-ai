"""Đăng ký khuôn mặt từ data/faces/<ten_thanh_vien>/ (5–10 ảnh mỗi người, mỗi ảnh một mặt).

Vai trò: tạo file data/faces/<ten>/role.txt chứa owner | family | guest (mặc định family).
  python scripts/enroll_faces.py            # đăng ký tất cả
  python scripts/enroll_faces.py --only Bo  # chỉ 1 người
"""
import _bootstrap  # noqa: F401
import argparse

import numpy as np

from services.worker_face.engine import FaceEngine
from services.worker_face.enroll import cross_similarity, enroll_and_save
from shared.config import data_dir, setup_logging
from shared.database import DB

log = setup_logging("enroll_faces")
ap = argparse.ArgumentParser()
ap.add_argument("--only")
ap.add_argument("--min-images", type=int, default=5)
args = ap.parse_args()

faces_dir = data_dir() / "faces"
folders = [p for p in sorted(faces_dir.iterdir()) if p.is_dir()] if faces_dir.exists() else []
if args.only:
    folders = [p for p in folders if p.name == args.only]
if not folders:
    raise SystemExit(f"Không có thư mục nào trong {faces_dir}. Tạo data/faces/<ten>/ và bỏ 5–10 ảnh vào.")

engine, db, results = FaceEngine(), DB(), []
for folder in folders:
    role_file = folder / "role.txt"
    role = role_file.read_text(encoding="utf-8").strip() if role_file.exists() else "family"
    r = enroll_and_save(engine, db, folder, role, args.min_images)
    results.append(r)
    status = "ĐÃ LƯU" if len(r.used) >= args.min_images else f"CHƯA LƯU (cần ≥ {args.min_images} ảnh dùng được)"
    print(f"\n== {r.name} ({role}): {len(r.used)} ảnh dùng được — {status}")
    for name, why in r.skipped:
        print(f"   bỏ {name}: {why}")
    sims = r.self_similarity()
    if sims:
        print(f"   tương đồng ảnh ↔ trung bình: min {min(sims):.3f} | TB {np.mean(sims):.3f} | max {max(sims):.3f}")

pairs = cross_similarity(results)
if pairs:
    print("\n== Tương đồng giữa các người khác nhau (càng thấp càng tốt):")
    for a, b, s in pairs:
        print(f"   {a} ↔ {b}: {s:.3f}")
    same = [s for r in results for s in r.self_similarity()]
    if same:
        print(f"\nGợi ý ngưỡng nằm giữa: max(khác người)={max(s for *_, s in pairs):.3f} và min(cùng người)={min(same):.3f}")

try:
    from shared.frame_bus import FrameBus
    FrameBus().bump_members_version()
    print("\nĐã báo worker_face nạp lại thành viên.")
except Exception:  # noqa: BLE001
    print("\n(Redis không chạy — worker_face sẽ đọc thành viên khi khởi động.)")
