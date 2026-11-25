"""worker_face: đọc khung mới nhất ở 2–3 FPS, nhận diện thành viên, ghi access_logs, cảnh báo người lạ."""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402

from services.worker_face.engine import FaceEngine  # noqa: E402
from services.worker_face.enroll import enroll_and_save  # noqa: E402
from services.worker_face.logic import FaceDecider, best_match, face_big_enough  # noqa: E402
from shared.config import camera_id, data_dir, now, settings, setup_logging  # noqa: E402
from shared.database import DB, STRANGER  # noqa: E402
from shared.frame_bus import FrameBus, LatestFrameReader, run_at_fps  # noqa: E402
from shared.notifier import CooldownGate, Notifier  # noqa: E402
from shared.snapshots import crop, draw_box, save_snapshot  # noqa: E402

SERVICE = "worker_face"
log = setup_logging(SERVICE)


class Gallery:
    def __init__(self, db: DB):
        self.db = db
        self.reload()

    def reload(self) -> None:
        members = [m for m in self.db.list_members() if m.embedding is not None]
        self.members = members
        self.matrix = np.stack([m.vector() for m in members]) if members else np.zeros((0, 512), np.float32)
        log.info("Đã nạp %d thành viên: %s", len(members), ", ".join(m.name for m in members) or "(trống)")


def main() -> None:
    cfg = settings().get("face", {})
    cam = camera_id()
    bus, db, notifier = FrameBus(), DB(), Notifier()
    member_gate = CooldownGate()
    engine = FaceEngine()
    gallery = Gallery(db)
    members_ver = bus.members_version()
    decider = FaceDecider(threshold=cfg.get("match_threshold", 0.55),
                          stranger_threshold=cfg.get("stranger_threshold"),
                          stranger_frames=cfg.get("stranger_consecutive_frames", 3),
                          iou_threshold=cfg.get("track_iou_threshold", 0.3),
                          max_missed=cfg.get("track_max_missed_frames", 6))
    min_px = cfg.get("min_face_size_px", 60)
    reader = LatestFrameReader(bus, cam)
    csv_path = data_dir() / "face_scores.csv"
    new_csv = not csv_path.exists()
    csv_f = open(csv_path, "a", newline="", encoding="utf-8")
    writer = csv.writer(csv_f)
    if new_csv:
        writer.writerow(["timestamp", "camera_id", "frame_id", "track_id", "best_member", "score", "face_px", "decision"])
    last_hb = 0.0
    log.info("Bắt đầu, camera=%s fps=%s ngưỡng=%.2f", cam, cfg.get("fps", 3), decider.threshold)

    for _ in run_at_fps(cfg.get("fps", 3)):
        if time.time() - last_hb > 5:
            bus.heartbeat(SERVICE)
            last_hb = time.time()
            # yêu cầu đăng ký từ Dashboard
            while (req := bus.pop_enroll_request()) is not None:
                name, role = req
                folder = data_dir() / "faces" / name
                if folder.is_dir():
                    r = enroll_and_save(engine, db, folder, role)
                    log.info("Đăng ký %s: %d ảnh dùng được, %d ảnh bỏ", name, len(r.used), len(r.skipped))
                    bus.bump_members_version()
            if (v := bus.members_version()) != members_ver:
                members_ver = v
                gallery.reload()

        frame = reader.next()
        if frame is None:
            continue
        faces = []
        for f in engine.detect(frame.image):
            if not face_big_enough(f.bbox, min_px):
                continue  # mặt quá nhỏ: không kết luận
            idx, score = best_match(f.embedding, gallery.matrix, gallery.members)
            faces.append((f.bbox, idx, score))

        ts = now()
        for d in decider.update(faces):
            name = gallery.members[d.member_index].name if d.member_index >= 0 else ""
            writer.writerow([ts.isoformat(timespec="seconds"), cam, frame.frame_id, d.track_id, name,
                             f"{d.score:.4f}", int(min(d.bbox[2] - d.bbox[0], d.bbox[3] - d.bbox[1])), d.kind])
            if d.kind == "member":
                m = gallery.members[d.member_index]
                if member_gate.allow(f"member:{m.id}", cfg.get("member_log_cooldown_s", 120)):
                    img = draw_box(frame.image.copy(), d.bbox, f"{m.name} {d.score:.2f}", (0, 200, 0))
                    rel = save_snapshot("access", img)
                    db.add_access_log(cam, m.id, m.name, d.score, rel, ts)
                    log.info("Thành viên: %s (%.2f)", m.name, d.score)
            elif d.kind == "stranger":
                full = draw_box(frame.image.copy(), d.bbox, f"Nguoi la {d.score:.2f}")
                rel = save_snapshot("stranger", full)
                save_snapshot("stranger", crop(frame.image, d.bbox), suffix="_face")
                msg = (f"🚨 Cảnh báo: phát hiện người lạ lúc {ts:%H:%M:%S}, camera {cam} "
                       f"(độ tương đồng cao nhất {d.score:.2f})")
                db.add_access_log(cam, None, STRANGER, d.score, rel, ts)
                if notifier.alert(f"stranger:{cam}", cfg.get("stranger_alert_cooldown_s", 60), msg, data_dir() / rel):
                    db.add_alert(cam, "stranger", msg, rel, status="sent", ts=ts)
                    log.warning("Người lạ! đã gửi cảnh báo (%.2f)", d.score)
        csv_f.flush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
