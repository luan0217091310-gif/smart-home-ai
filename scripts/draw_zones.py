"""Vẽ vùng bằng chuột trên ảnh tĩnh, lưu data/zones.json (tọa độ 0–1) + ảnh tô màu để kiểm tra.

  python scripts/view_stream.py --snapshot            # chụp ảnh tĩnh trước
  python scripts/draw_zones.py                        # vẽ trên data/snapshot_<camera>.jpg
  python scripts/draw_zones.py --preview              # chỉ xuất ảnh tô vùng từ zones.json có sẵn

Cách vẽ: click trái để thêm đỉnh · Enter: xong một vùng (nhập tên + loại ở terminal) · Backspace: xóa đỉnh cuối
         · S: lưu và thoát · Esc: thoát không lưu.
Cần OpenCV có giao diện:  pip install opencv-python  (bản headless không mở được cửa sổ).
"""
import _bootstrap  # noqa: F401
import argparse
import json

import cv2
import numpy as np

from shared.config import camera_id, data_dir, setup_logging
from shared.snapshots import ascii_text
from shared.zones import ZONE_TYPES, ZoneMap

log = setup_logging("draw_zones")
ap = argparse.ArgumentParser()
ap.add_argument("--image")
ap.add_argument("--camera", default=camera_id())
ap.add_argument("--preview", action="store_true")
args = ap.parse_args()

img_path = args.image or str(data_dir() / f"snapshot_{args.camera}.jpg")
img = cv2.imdecode(np.fromfile(img_path, np.uint8), cv2.IMREAD_COLOR)
if img is None:
    raise SystemExit(f"Không đọc được ảnh {img_path}. Chạy: python scripts/view_stream.py --snapshot")
h, w = img.shape[:2]
zones_path = data_dir() / "zones.json"
preview_path = data_dir() / "zones_preview.jpg"


def save_preview(zm: ZoneMap) -> None:
    cv2.imencode(".jpg", zm.draw(img))[1].tofile(str(preview_path))
    log.info("Đã lưu ảnh tô vùng: %s", preview_path)


if args.preview:
    save_preview(ZoneMap.load(zones_path))
    raise SystemExit(0)

zones, pts = [], []


def on_mouse(event, x, y, *_):
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x, y))


cv2.namedWindow("draw_zones")
cv2.setMouseCallback("draw_zones", on_mouse)
types_hint = " | ".join(f"{i}={t}" for i, t in enumerate(ZONE_TYPES))
while True:
    view = ZoneMap.from_dict({"camera_id": args.camera, "zones": zones}).draw(img)
    for p in pts:
        cv2.circle(view, p, 4, (0, 255, 255), -1)
    if len(pts) > 1:
        cv2.polylines(view, [np.array(pts)], False, (0, 255, 255), 2)
    cv2.putText(view, ascii_text(f"{len(zones)} vung | Enter: xong vung | S: luu | Esc: thoat"), (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("draw_zones", view)
    k = cv2.waitKey(30) & 0xFF
    if k == 13 and len(pts) >= 3:
        name = input("Tên vùng (vd. Ghế sofa): ").strip()
        t = input(f"Loại vùng [{types_hint}]: ").strip()
        ztype = ZONE_TYPES[int(t)] if t.isdigit() and int(t) < len(ZONE_TYPES) else (t if t in ZONE_TYPES else "furniture")
        zones.append({"name": name, "type": ztype, "polygon": [[round(x / w, 4), round(y / h, 4)] for x, y in pts]})
        pts.clear()
    elif k == 8 and pts:
        pts.pop()
    elif k in (ord("s"), ord("S")):
        with open(zones_path, "w", encoding="utf-8") as f:
            json.dump({"camera_id": args.camera, "zones": zones}, f, ensure_ascii=False, indent=2)
        log.info("Đã lưu %d vùng vào %s", len(zones), zones_path)
        save_preview(ZoneMap.load(zones_path))
        break
    elif k == 27:
        break
cv2.destroyAllWindows()
