"""GĐ 1: frame_bus, database, cooldown, backoff, vùng."""
import numpy as np

from services.stream_producer.capture import backoff_delay, mask_source, parse_source, resize_to_width
from services.stream_producer.main import OfflineTracker
from shared.config import now
from shared.database import table_names
from shared.frame_bus import LatestFrameReader
from shared.notifier import CooldownGate
from shared.zones import ZoneMap


def test_frame_bus_roundtrip(bus):
    img = np.zeros((120, 160, 3), np.uint8)
    img[:, :80] = (0, 0, 255)
    fid = bus.publish("cam_test", img, ts=123.5)
    f = bus.get_latest("cam_test")
    assert f.frame_id == fid == 1 and f.ts == 123.5 and f.image.shape == img.shape
    assert abs(int(f.image[60, 20, 2]) - 255) < 10


def test_latest_reader_skips_duplicates(bus):
    r = LatestFrameReader(bus, "cam_test")
    assert r.next() is None
    bus.publish("cam_test", np.zeros((10, 10, 3), np.uint8))
    assert r.next() is not None
    assert r.next() is None  # cùng frame_id → bỏ qua
    bus.publish("cam_test", np.zeros((10, 10, 3), np.uint8))
    bus.publish("cam_test", np.zeros((10, 10, 3), np.uint8))
    assert r.next().frame_id == 3  # chỉ lấy khung mới nhất


def test_heartbeat_and_version(bus):
    bus.heartbeat("x")
    assert bus.heartbeats(["x", "y"])["y"] is None and bus.heartbeats(["x"])["x"] > 0
    assert bus.objects_version() == 0 and bus.bump_objects_version() == 1


def test_database_tables(db):
    assert table_names(str(db.engine.url)) == ["access_logs", "alerts", "members", "tracked_objects", "zones"]
    with db.engine.connect() as c:
        assert c.exec_driver_sql("PRAGMA journal_mode").scalar().lower() == "wal"
        assert c.exec_driver_sql("PRAGMA busy_timeout").scalar() == 5000


def test_database_crud(db):
    m = db.upsert_member("Bo", np.ones(512, np.float32), 6, "owner")
    assert db.list_members()[0].vector().shape == (512,)
    db.add_access_log("cam_test", m.id, "Bo", 0.8)
    assert len(db.access_logs_since(now().replace(hour=0, minute=0))) == 1
    aid = db.add_alert("cam_test", "stranger", "x")
    assert db.set_alert_status(aid, "false_alarm")
    assert db.alerts_since(now().replace(hour=0, minute=0))[0].status == "false_alarm"
    o, created = db.add_object("Chìa khóa", "keys")
    assert created and not db.add_object("Chìa khóa", "keys")[1]
    db.update_object_seen(o.id, "Bàn", "cam_test", 0.5, None)
    assert db.active_objects()[0].last_zone == "Bàn"
    assert db.delete_member(m.id) == "Bo"


def test_cooldown():
    t = [0.0]
    g = CooldownGate(clock=lambda: t[0])
    assert g.allow("a", 60) and not g.allow("a", 60) and g.allow("b", 60)
    t[0] = 61
    assert g.allow("a", 60)


def test_backoff_and_source():
    assert [backoff_delay(i) for i in range(7)] == [1, 2, 4, 8, 16, 30, 30]
    assert parse_source("0") == ("webcam", 0)
    assert parse_source("rtsp://u:p@1.2.3.4/s")[0] == "rtsp"
    assert parse_source("data/x.mp4")[0] == "file"
    assert "p@" not in mask_source("rtsp://u:p@1.2.3.4/s")
    assert resize_to_width(np.zeros((720, 1920, 3), np.uint8), 1280).shape == (480, 1280, 3)


def test_offline_tracker():
    tr = OfflineTracker(300)
    assert not tr.mark_lost(0) and not tr.mark_lost(299) and tr.mark_lost(300) and not tr.mark_lost(400)
    assert tr.mark_ok() and not tr.mark_ok()


def test_zones_smallest_wins(db):
    zm = ZoneMap.from_dict({"camera_id": "cam_test", "zones": [
        {"name": "Bàn làm việc", "type": "furniture", "polygon": [[0.10, 0.55], [0.45, 0.55], [0.45, 0.80], [0.10, 0.80]]},
        {"name": "Ghế sofa", "type": "safe_rest", "polygon": [[0.55, 0.50], [0.95, 0.50], [0.95, 0.85], [0.55, 0.85]]},
        {"name": "Sàn nhà", "type": "floor", "polygon": [[0.0, 0.6], [1.0, 0.6], [1.0, 1.0], [0.0, 1.0]]},
    ]})
    assert zm.find_zone(0.3, 0.7).name == "Bàn làm việc"
    assert zm.find_zone(0.5, 0.9).name == "Sàn nhà"
    assert zm.find_zone(0.7, 0.55).name == "Ghế sofa"
    assert zm.find_zone(0.5, 0.1) is None
    assert zm.find_zone_px(960, 400, 1280, 720).name == "Ghế sofa"
    zm.sync_to_db(db)
    assert len(db.list_zones("cam_test")) == 3
