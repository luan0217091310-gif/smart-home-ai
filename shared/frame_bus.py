"""Ghi/đọc khung hình mới nhất qua Redis. Khóa: frame:{camera_id}:latest (hash: jpg, frame_id, ts)."""
from __future__ import annotations

import time
from dataclasses import dataclass

import cv2
import numpy as np
import redis

from shared.config import env, settings


@dataclass
class Frame:
    camera_id: str
    frame_id: int
    ts: float          # epoch giây lúc chụp
    image: np.ndarray


def make_redis(url: str | None = None) -> redis.Redis:
    return redis.Redis.from_url(url or env("REDIS_URL", "redis://localhost:6379/0"))


def frame_key(camera_id: str) -> str:
    return f"frame:{camera_id}:latest"


class FrameBus:
    def __init__(self, client: redis.Redis | None = None, jpeg_quality: int | None = None):
        self.r = client or make_redis()
        self.jpeg_quality = jpeg_quality or int(env("JPEG_QUALITY", "80"))
        self._counter: dict[str, int] = {}

    # ---- producer
    def publish(self, camera_id: str, frame: np.ndarray, ts: float | None = None) -> int:
        """Ghi đè khung mới nhất. Trả về frame_id."""
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        if not ok:
            raise RuntimeError("Nén JPEG thất bại")
        frame_id = self._counter.get(camera_id, 0) + 1
        self._counter[camera_id] = frame_id
        self.r.hset(frame_key(camera_id), mapping={
            "jpg": buf.tobytes(), "frame_id": frame_id, "ts": ts if ts is not None else time.time()})
        return frame_id

    # ---- consumer
    def get_latest_jpeg(self, camera_id: str) -> tuple[bytes, int, float] | None:
        data = self.r.hgetall(frame_key(camera_id))
        if not data or b"jpg" not in data:
            return None
        return data[b"jpg"], int(data[b"frame_id"]), float(data[b"ts"])

    def get_latest(self, camera_id: str) -> Frame | None:
        raw = self.get_latest_jpeg(camera_id)
        if raw is None:
            return None
        img = cv2.imdecode(np.frombuffer(raw[0], np.uint8), cv2.IMREAD_COLOR)
        return None if img is None else Frame(camera_id, raw[1], raw[2], img)

    # ---- heartbeat & tín hiệu
    def heartbeat(self, service: str) -> None:
        self.r.set(f"heartbeat:{service}", time.time(), ex=int(settings().get("heartbeat_ttl_s", 30)))

    def heartbeats(self, services: list[str]) -> dict[str, float | None]:
        return {s: (float(v) if (v := self.r.get(f"heartbeat:{s}")) else None) for s in services}

    def objects_version(self) -> int:
        v = self.r.get("objects:version")
        return int(v) if v else 0

    def bump_objects_version(self) -> int:
        return int(self.r.incr("objects:version"))

    # cảnh báo từ tiến trình không được mở CSDL (producer trên Windows) → assistant_api ghi vào CSDL
    def push_alert(self, camera_id: str, alert_type: str, message: str, status: str = "new") -> None:
        import json
        self.r.rpush("alerts:pending", json.dumps({"camera_id": camera_id, "alert_type": alert_type,
                                                   "message": message, "status": status, "ts": time.time()}))

    def pop_alerts(self) -> list[dict]:
        import json
        out = []
        while (v := self.r.lpop("alerts:pending")) is not None:
            out.append(json.loads(v))
        return out

    # members:version — worker_face nạp lại thành viên; faces:enroll_queue — tên thành viên cần đăng ký lại
    def members_version(self) -> int:
        v = self.r.get("members:version")
        return int(v) if v else 0

    def bump_members_version(self) -> int:
        return int(self.r.incr("members:version"))

    def request_enroll(self, name: str, role: str = "family") -> None:
        self.r.rpush("faces:enroll_queue", f"{name}|{role}")

    def pop_enroll_request(self) -> tuple[str, str] | None:
        v = self.r.lpop("faces:enroll_queue")
        if not v:
            return None
        name, _, role = v.decode().partition("|")
        return name, role or "family"


class LatestFrameReader:
    """Cho worker: chỉ trả khung MỚI, bỏ qua nếu frame_id trùng lần trước. Không bao giờ xếp hàng."""

    def __init__(self, bus: FrameBus, camera_id: str):
        self.bus, self.camera_id, self.last_id = bus, camera_id, None

    def next(self) -> Frame | None:
        f = self.bus.get_latest(self.camera_id)
        if f is None or f.frame_id == self.last_id:
            return None
        self.last_id = f.frame_id
        return f


def run_at_fps(fps: float):
    """Generator nhịp: yield mỗi 1/fps giây (bù thời gian xử lý)."""
    period = 1.0 / max(fps, 0.01)
    nxt = time.monotonic()
    while True:
        yield
        nxt += period
        delay = nxt - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        else:
            nxt = time.monotonic()
