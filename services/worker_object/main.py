"""worker_object: mỗi 3–5 giây tìm các đồ vật đang theo dõi, xác định vùng, cập nhật CSDL.

Nạp nóng: thấy `objects:version` đổi thì đọc lại bảng và gọi lại set_classes(), không khởi động lại.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.worker_object.detector import ObjectDetector  # noqa: E402
from services.worker_object.logic import ZoneStabilizer, best_per_keyword  # noqa: E402
from shared.config import camera_id, data_dir, now, settings, setup_logging  # noqa: E402
from shared.database import DB  # noqa: E402
from shared.frame_bus import FrameBus  # noqa: E402
from shared.snapshots import crop, save_snapshot  # noqa: E402
from shared.zones import ZoneMap  # noqa: E402

SERVICE = "worker_object"
log = setup_logging(SERVICE)


def seed_initial_objects(db: DB, cfg: dict) -> None:
    if db.all_objects():
        return
    for o in cfg.get("initial_objects", []):
        db.add_object(o["vn"], o["en"])
    log.info("Đã nạp danh sách đồ vật ban đầu")


def main() -> None:
    cfg = settings().get("object", {})
    cam = camera_id()
    bus, db = FrameBus(), DB()
    seed_initial_objects(db, cfg)
    zones_path = data_dir() / "zones.json"
    zones, zones_mtime = ZoneMap.load(zones_path), None
    zones.sync_to_db(db)
    detector = ObjectDetector()
    stab = ZoneStabilizer(cfg.get("zone_confirm_cycles", 2))
    outside = cfg.get("outside_zone_label", "Ngoài các vùng đã đặt tên")
    version, objects = None, []
    interval = float(cfg.get("interval_s", 4))
    log.info("Bắt đầu, camera=%s chu kỳ=%.0fs", cam, interval)

    while True:
        t0 = time.time()
        bus.heartbeat(SERVICE)
        # nạp nóng danh sách đồ vật
        if (v := bus.objects_version()) != version:
            version = v
            objects = db.active_objects()
            for o in objects:
                stab.seed(o.id, o.last_zone)
            detector.set_classes([o.prompt_keyword for o in objects])
        # nạp lại vùng khi file đổi
        if zones_path.exists() and (m := zones_path.stat().st_mtime) != zones_mtime:
            zones_mtime = m
            zones = ZoneMap.load(zones_path)
            zones.sync_to_db(db)
            log.info("Đã nạp %d vùng từ zones.json", len(zones.zones))

        frame = bus.get_latest(cam)
        if frame is not None and objects:
            h, w = frame.image.shape[:2]
            found = best_per_keyword(detector.detect(frame.image), cfg.get("min_confidence", 0.25))
            ts = now()
            for o in objects:
                d = found.get(o.prompt_keyword)
                if d is None:
                    continue  # không thấy: giữ nguyên vị trí cũ (lần cuối thấy)
                cx, cy = d.center
                z = zones.find_zone_px(cx, cy, w, h)
                zone_name = z.name if z else outside
                changed = stab.observe(o.id, zone_name)
                rel = save_snapshot("objects", crop(frame.image, d.bbox, 0.5), fixed_name=f"object_{o.id}.jpg")
                db.update_object_seen(o.id, changed, cam, d.confidence, rel, ts)
                if changed:
                    log.info("%s → %s (%.2f)", o.object_name, zone_name, d.confidence)
        time.sleep(max(0.0, interval - (time.time() - t0)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
