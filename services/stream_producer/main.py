"""stream_producer: đọc camera đúng một lần, ghi khung mới nhất vào Redis ở STREAM_FPS.

Mất kết nối → thử lại 1, 2, 4… giây (tối đa 30 giây). Mất quá 5 phút → cảnh báo `system` qua Telegram.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.stream_producer.capture import LatestGrabber, backoff_delay, mask_source, resize_to_width  # noqa: E402
from shared.config import camera_id, env, env_int, settings, setup_logging  # noqa: E402
from shared.database import DB  # noqa: E402
from shared.frame_bus import FrameBus, run_at_fps  # noqa: E402
from shared.notifier import Notifier  # noqa: E402

SERVICE = "stream_producer"
log = setup_logging(SERVICE)


class OfflineTracker:
    """Logic thuần: báo một lần khi mất kết nối liên tục quá `alert_after_s`."""

    def __init__(self, alert_after_s: float):
        self.alert_after_s = alert_after_s
        self.lost_since: float | None = None
        self.alerted = False

    def mark_ok(self) -> bool:
        """Trả về True nếu vừa hồi phục sau khi đã báo."""
        recovered = self.alerted
        self.lost_since, self.alerted = None, False
        return recovered

    def mark_lost(self, t: float) -> bool:
        """Trả về True đúng một lần khi cần gửi cảnh báo."""
        if self.lost_since is None:
            self.lost_since = t
        if not self.alerted and t - self.lost_since >= self.alert_after_s:
            self.alerted = True
            return True
        return False


def main() -> None:
    cam = camera_id()
    src = env("CAMERA_SOURCE", "0")
    fps = env_int("STREAM_FPS", 15)
    width = env_int("STREAM_WIDTH", 1280)
    cfg = settings().get("stream", {})
    bus, notifier, db = FrameBus(), Notifier(), DB()
    tracker = OfflineTracker(cfg.get("offline_alert_after_s", 300))
    max_backoff = cfg.get("reconnect_max_backoff_s", 30)
    log.info("Khởi động camera_id=%s nguồn=%s fps=%s width=%s", cam, mask_source(src), fps, width)

    attempt = 0
    while True:
        grabber = LatestGrabber(src)
        if not grabber.alive:
            grabber.release()
            delay = backoff_delay(attempt, max_backoff)
            log.warning("Không mở được camera, thử lại sau %.0fs (lần %d)", delay, attempt + 1)
            if tracker.mark_lost(time.time()):
                msg = f"⚠️ Mất kết nối camera {cam} quá {tracker.alert_after_s // 60:.0f} phút"
                db.add_alert(cam, "system", msg, status="sent")
                notifier.alert(f"system:{cam}", 600, msg)
            bus.heartbeat(SERVICE)
            time.sleep(delay)
            attempt += 1
            continue

        log.info("Đã kết nối camera")
        if tracker.mark_ok():
            notifier.client.send_text(f"✅ Camera {cam} đã kết nối lại")
        attempt = 0
        last_seq, stale_since, n, t0 = -1, time.time(), 0, time.time()
        for _ in run_at_fps(fps):
            frame, ts, seq = grabber.read()
            if not grabber.alive or (time.time() - stale_since > 10):
                log.warning("Mất tín hiệu camera, kết nối lại")
                break
            if frame is None or seq == last_seq:
                continue
            last_seq, stale_since = seq, time.time()
            bus.publish(cam, resize_to_width(frame, width), ts=ts)
            n += 1
            if time.time() - t0 >= 5:
                bus.heartbeat(SERVICE)
                log.debug("FPS thực: %.1f", n / (time.time() - t0))
                n, t0 = 0, time.time()
        grabber.release()
        tracker.mark_lost(time.time())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
