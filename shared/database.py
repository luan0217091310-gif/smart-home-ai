"""5 bảng CSDL (mục 5.1 đặc tả) bằng SQLAlchemy. SQLite bật WAL + busy_timeout."""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text,
                        create_engine, event, inspect, select)
from sqlalchemy.orm import declarative_base, sessionmaker

from shared.config import data_dir, env, now

Base = declarative_base()


class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), default="family")  # owner | family | guest
    embedding = Column(LargeBinary)              # 512 float32
    num_images = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)

    def vector(self) -> np.ndarray | None:
        return None if self.embedding is None else np.frombuffer(self.embedding, dtype=np.float32)


class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True)
    camera_id = Column(String(50), index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    member_name = Column(String(100))            # tên hoặc "Stranger"
    confidence = Column(Float)
    image_path = Column(String(255))
    timestamp = Column(DateTime, default=now, index=True)


class TrackedObject(Base):
    __tablename__ = "tracked_objects"
    id = Column(Integer, primary_key=True)
    object_name = Column(String(100), nullable=False)    # tiếng Việt
    prompt_keyword = Column(String(100), nullable=False)  # tiếng Anh
    last_zone = Column(String(100))
    last_camera_id = Column(String(50))
    last_confidence = Column(Float)
    last_seen_at = Column(DateTime)
    image_path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    camera_id = Column(String(50), index=True)
    alert_type = Column(String(20))              # stranger | fall | system
    message = Column(Text)
    image_path = Column(String(255))
    timestamp = Column(DateTime, default=now, index=True)
    status = Column(String(20), default="new")   # new | sent | acknowledged | false_alarm


class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True)
    camera_id = Column(String(50), index=True)
    zone_name = Column(String(100))
    zone_type = Column(String(20))               # furniture | safe_rest | floor | door
    polygon_coords = Column(Text)                # JSON


ALERT_STATUSES = ("new", "sent", "acknowledged", "false_alarm")
STRANGER = "Stranger"

_engines: dict[str, object] = {}


def default_url() -> str:
    return env("DATABASE_URL", f"sqlite:///{(data_dir() / 'smarthome.db').as_posix()}")


def get_engine(url: str | None = None):
    url = url or default_url()
    if url not in _engines:
        is_sqlite = url.startswith("sqlite")
        engine = create_engine(url, future=True, connect_args={"timeout": 5, "check_same_thread": False}
                               if is_sqlite else {})
        if is_sqlite:
            @event.listens_for(engine, "connect")
            def _pragma(dbapi_conn, _):  # noqa: ANN001
                cur = dbapi_conn.cursor()
                cur.execute("PRAGMA journal_mode=WAL")
                cur.execute("PRAGMA busy_timeout=5000")
                cur.execute("PRAGMA foreign_keys=ON")
                cur.close()
        Base.metadata.create_all(engine)
        _engines[url] = engine
    return _engines[url]


def table_names(url: str | None = None) -> list[str]:
    return sorted(inspect(get_engine(url)).get_table_names())


class HostDBError(RuntimeError):
    pass


def guard_host_access(url: str) -> None:
    """Docker Desktop (Windows): SQLite WAL KHÔNG an toàn khi Windows và container cùng mở một file qua bind mount
    (file -shm/-wal lệch nhau → mất dữ liệu). Chặn tiến trình Windows mở CSDL thật, trừ khi ALLOW_HOST_DB=1
    (chỉ dùng khi mọi container đã dừng)."""
    import os
    from pathlib import Path
    if os.name != "nt" or env("ALLOW_HOST_DB") == "1" or not url.startswith("sqlite"):
        return
    target = Path(url.split(":///", 1)[-1])
    if not target.is_absolute():
        from shared.config import ROOT
        target = ROOT / target
    if target.resolve() == (data_dir() / "smarthome.db").resolve():
        raise HostDBError("Không mở CSDL thật từ Windows khi hệ thống chạy trong Docker. Chạy script trong container, vd.: "
                          "docker compose run --rm worker_face python scripts/enroll_faces.py")


class DB:
    """Các thao tác ghi/đọc thường dùng; mỗi hàm là một giao dịch ngắn."""

    def __init__(self, url: str | None = None):
        guard_host_access(url or default_url())
        self.engine = get_engine(url)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    # ---- members
    def upsert_member(self, name: str, embedding: np.ndarray, num_images: int, role: str = "family") -> Member:
        with self.Session.begin() as s:
            m = s.scalar(select(Member).where(Member.name == name))
            if m is None:
                m = Member(name=name, role=role)
                s.add(m)
            m.embedding = np.asarray(embedding, dtype=np.float32).tobytes()
            m.num_images = num_images
            m.role = role or m.role
            s.flush()
            return m

    def list_members(self) -> list[Member]:
        with self.Session() as s:
            return list(s.scalars(select(Member).order_by(Member.name)))

    def delete_member(self, member_id: int) -> str | None:
        with self.Session.begin() as s:
            m = s.get(Member, member_id)
            if m is None:
                return None
            name = m.name
            s.delete(m)
            return name

    # ---- access logs
    def add_access_log(self, camera_id: str, member_id: int | None, member_name: str,
                       confidence: float, image_path: str | None = None, ts: datetime | None = None) -> int:
        with self.Session.begin() as s:
            row = AccessLog(camera_id=camera_id, member_id=member_id, member_name=member_name,
                            confidence=float(confidence), image_path=image_path, timestamp=ts or now())
            s.add(row)
            s.flush()
            return row.id

    def access_logs_since(self, since: datetime, member_name: str | None = None) -> list[AccessLog]:
        with self.Session() as s:
            q = select(AccessLog).where(AccessLog.timestamp >= since).order_by(AccessLog.timestamp)
            if member_name:
                q = q.where(AccessLog.member_name == member_name)
            return list(s.scalars(q))

    # ---- alerts
    def add_alert(self, camera_id: str, alert_type: str, message: str, image_path: str | None = None,
                  status: str = "new", ts: datetime | None = None) -> int:
        with self.Session.begin() as s:
            row = Alert(camera_id=camera_id, alert_type=alert_type, message=message,
                        image_path=image_path, status=status, timestamp=ts or now())
            s.add(row)
            s.flush()
            return row.id

    def set_alert_status(self, alert_id: int, status: str) -> bool:
        if status not in ALERT_STATUSES:
            raise ValueError(f"Trạng thái không hợp lệ: {status}")
        with self.Session.begin() as s:
            a = s.get(Alert, alert_id)
            if a is None:
                return False
            a.status = status
            return True

    def alerts_since(self, since: datetime, alert_type: str | None = None) -> list[Alert]:
        with self.Session() as s:
            q = select(Alert).where(Alert.timestamp >= since).order_by(Alert.timestamp.desc())
            if alert_type:
                q = q.where(Alert.alert_type == alert_type)
            return list(s.scalars(q))

    # ---- tracked objects
    def active_objects(self) -> list[TrackedObject]:
        with self.Session() as s:
            return list(s.scalars(select(TrackedObject).where(TrackedObject.is_active.is_(True))
                                  .order_by(TrackedObject.id)))

    def all_objects(self) -> list[TrackedObject]:
        with self.Session() as s:
            return list(s.scalars(select(TrackedObject).order_by(TrackedObject.id)))

    def add_object(self, vn_name: str, en_keyword: str) -> tuple[TrackedObject, bool]:
        """Trả về (đồ vật, created). Đã có mà đang ngừng thì bật lại (created=True); đang theo dõi thì created=False."""
        with self.Session.begin() as s:
            for o in s.scalars(select(TrackedObject)):
                if o.prompt_keyword.lower() == en_keyword.lower() or o.object_name.lower() == vn_name.lower():
                    was_active = bool(o.is_active)
                    o.is_active = True
                    return o, not was_active
            o = TrackedObject(object_name=vn_name.strip(), prompt_keyword=en_keyword.strip().lower(), is_active=True)
            s.add(o)
            s.flush()
            return o, True

    def set_object_active(self, object_id: int, active: bool) -> bool:
        with self.Session.begin() as s:
            o = s.get(TrackedObject, object_id)
            if o is None:
                return False
            o.is_active = active
            return True

    def update_object_seen(self, object_id: int, zone: str | None, camera_id: str, confidence: float,
                           image_path: str | None, ts: datetime | None = None) -> None:
        with self.Session.begin() as s:
            o = s.get(TrackedObject, object_id)
            if o is None:
                return
            if zone is not None:
                o.last_zone = zone
            o.last_camera_id = camera_id
            o.last_confidence = float(confidence)
            o.last_seen_at = ts or now()
            if image_path:
                o.image_path = image_path

    # ---- zones
    def replace_zones(self, camera_id: str, zones: list[dict]) -> None:
        with self.Session.begin() as s:
            for z in s.scalars(select(Zone).where(Zone.camera_id == camera_id)):
                s.delete(z)
            for z in zones:
                s.add(Zone(camera_id=camera_id, zone_name=z["name"], zone_type=z.get("type", "furniture"),
                           polygon_coords=json.dumps(z["polygon"])))

    def list_zones(self, camera_id: str | None = None) -> list[Zone]:
        with self.Session() as s:
            q = select(Zone)
            if camera_id:
                q = q.where(Zone.camera_id == camera_id)
            return list(s.scalars(q))

    # ---- retention
    def purge_access_logs(self, older_than_days: int) -> int:
        cutoff = now() - timedelta(days=older_than_days)
        with self.Session.begin() as s:
            rows = list(s.scalars(select(AccessLog).where(AccessLog.timestamp < cutoff)))
            for r in rows:
                s.delete(r)
            return len(rows)
