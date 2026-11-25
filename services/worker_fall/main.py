"""worker_fall: YOLO26-pose + theo dấu người, bộ lọc 3 lớp, cảnh báo khẩn khi xác nhận té ngã."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402

from services.worker_fall.logic import CONFIRMED, FallDetector, FallParams  # noqa: E402
from shared.config import camera_id, data_dir, env, models_dir, now, settings, setup_logging  # noqa: E402
from shared.database import DB  # noqa: E402
from shared.frame_bus import FrameBus, LatestFrameReader, run_at_fps  # noqa: E402
from shared.notifier import Notifier  # noqa: E402
from shared.snapshots import draw_box, save_snapshot  # noqa: E402
from shared.zones import ZoneMap  # noqa: E402

SERVICE = "worker_fall"
log = setup_logging(SERVICE)


class PoseEstimator:
    """Lớp bọc mô hình tư thế. Đổi mô hình qua POSE_MODEL trong .env."""

    def __init__(self, model_name: str | None = None):
        os.environ.setdefault("YOLO_CONFIG_DIR", str(models_dir() / "ultralytics"))
        from ultralytics import YOLO

        name = model_name or env("POSE_MODEL", "yolo26n-pose.pt")
        local = models_dir() / name
        cwd = os.getcwd()
        os.chdir(models_dir())
        try:
            self.model = YOLO(str(local) if local.exists() else name)
        finally:
            os.chdir(cwd)
        log.info("Đã nạp mô hình tư thế %s", name)

    def track(self, image):
        """Trả danh sách (track_id, bbox, keypoints[17,3])."""
        r = self.model.track(image, persist=True, verbose=False, classes=[0])[0]
        out = []
        if r.boxes is None or r.keypoints is None or r.boxes.id is None:
            return out
        ids = r.boxes.id.int().tolist()
        boxes = r.boxes.xyxy.tolist()
        kxy = r.keypoints.xy.cpu().numpy()
        kconf = r.keypoints.conf.cpu().numpy() if r.keypoints.conf is not None else np.ones(kxy.shape[:2])
        for tid, b, xy, c in zip(ids, boxes, kxy, kconf):
            out.append((tid, tuple(b), np.concatenate([xy, c[:, None]], axis=1)))
        return out


def main() -> None:
    cfg = settings().get("fall", {})
    cam = camera_id()
    bus, db, notifier = FrameBus(), DB(), Notifier()
    zones_path = data_dir() / "zones.json"
    zones, zones_mtime = ZoneMap.load(zones_path), None

    def zone_type_at(x, y):
        z = zones.find_zone(x, y)
        return z.type if z else None

    det = FallDetector(FallParams.from_settings(cfg), zone_type_at)
    pose = PoseEstimator()
    reader = LatestFrameReader(bus, cam)
    last_hb = 0.0
    log.info("Bắt đầu, camera=%s fps=%s ngưỡng rơi=%s", cam, cfg.get("fps", 15), det.p.drop_speed_threshold)

    for _ in run_at_fps(cfg.get("fps", 15)):
        if time.time() - last_hb > 5:
            bus.heartbeat(SERVICE)
            last_hb = time.time()
            if zones_path.exists() and (m := zones_path.stat().st_mtime) != zones_mtime:
                zones_mtime, zones = m, ZoneMap.load(zones_path)
        frame = reader.next()
        if frame is None:
            continue
        h, w = frame.image.shape[:2]
        for tid, bbox, kps in pose.track(frame.image):
            if det.update(tid, frame.ts, bbox, kps, (w, h)) == CONFIRMED:
                ts = now()
                img = draw_box(frame.image.copy(), bbox, "NGA", (0, 0, 255))
                rel = save_snapshot("fall", img)
                msg = f"🆘 KHẨN: phát hiện người té ngã và nằm yên lúc {ts:%H:%M:%S}, camera {cam}"
                sent = notifier.alert(f"fall:{cam}:{tid}", cfg.get("alert_cooldown_s", 60), msg, data_dir() / rel)
                db.add_alert(cam, "fall", msg, rel, status="sent" if sent else "new", ts=ts)
                log.warning("TÉ NGÃ đã xác nhận (người #%s)", tid)
        det.forget_stale(frame.ts)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
