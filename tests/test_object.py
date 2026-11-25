"""GĐ 3: logic đồ vật và vùng."""
from services.worker_object.logic import Detection, ZoneStabilizer, best_per_keyword


def test_best_per_keyword_filters_and_picks_max():
    dets = [Detection("keys", 0.2, (0, 0, 1, 1)), Detection("keys", 0.6, (0, 0, 2, 2)),
            Detection("wallet", 0.1, (0, 0, 1, 1)), Detection("glasses", 0.3, (0, 0, 4, 4))]
    out = best_per_keyword(dets, 0.25)
    assert set(out) == {"keys", "glasses"} and out["keys"].confidence == 0.6
    assert out["glasses"].center == (2, 2)


def test_first_sighting_accepted_immediately():
    s = ZoneStabilizer(2)
    assert s.observe(1, "Bàn làm việc") == "Bàn làm việc"


def test_zone_change_needs_two_cycles():
    s = ZoneStabilizer(2)
    s.seed(1, "Bàn làm việc")
    assert s.observe(1, "Ghế sofa") is None
    assert s.observe(1, "Ghế sofa") == "Ghế sofa"
    assert s.current[1] == "Ghế sofa"


def test_noise_does_not_switch_zone():
    s = ZoneStabilizer(2)
    s.seed(1, "Bàn làm việc")
    seq = ["Ghế sofa", "Bàn làm việc", "Sàn nhà", "Bàn làm việc"]
    assert all(s.observe(1, z) is None for z in seq)
    assert s.current[1] == "Bàn làm việc"


def test_hot_reload_via_version(db, bus):
    """Thêm đồ vật → tăng objects:version → worker thấy số đổi."""
    v0 = bus.objects_version()
    db.add_object("Cốc nước", "cup")
    bus.bump_objects_version()
    assert bus.objects_version() == v0 + 1
    assert "cup" in [o.prompt_keyword for o in db.active_objects()]
