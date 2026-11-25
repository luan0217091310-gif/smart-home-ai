"""GĐ 5: công cụ trợ lý, so tên không dấu, bộ câu hỏi chạy với LLM offline (rules), API FastAPI."""
import pytest

from services.assistant_api.agent import Agent
from services.assistant_api.fixtures import QUESTIONS, seed_demo
from services.assistant_api.llm import RulesLLM
from services.assistant_api.tools import Tools, fold


@pytest.fixture
def tools(db, bus):
    seed_demo(db)
    return Tools(db, bus)


def test_fold():
    assert fold("Chìa Khóa") == "chia khoa" and fold("Đồng hồ") == "dong ho"


def test_find_object_accent_insensitive(tools):
    for name in ("Chìa khóa", "chia khoa", "CHÌA KHOÁ", "keys"):
        r = tools.find_object(name)
        assert r["found"] and r["zone"] == "Bàn làm việc", name


def test_untracked_object_not_invented(tools):
    r = tools.find_object("cái ô")
    assert not r["found"] and not r["tracked"]


def test_register_bumps_version(tools, bus):
    v = bus.objects_version()
    r = tools.register_new_object("Mũ bảo hiểm", "helmet")
    assert r["ok"] and not r["already_tracked"] and bus.objects_version() == v + 1
    assert tools.register_new_object("mu bao hiem", "helmet")["already_tracked"]
    assert not tools.register_new_object("Ô", "ô dù")["ok"]  # từ khóa phải tiếng Anh không dấu


def test_param_validation(tools):
    assert tools.get_visitors(since_hours="abc")["since_hours"] == 24
    assert tools.get_visitors(since_hours=10 ** 9)["since_hours"] == 24 * 30
    assert "error" in tools.call("drop_table", {})
    assert "error" in tools.call("find_object", {"bad": 1})


def test_visitors_and_alerts(tools):
    v = tools.get_visitors(since_hours=2)
    assert [x["name"] for x in v["visitors"]] == ["Bố"] and v["stranger_count"] == 1
    assert tools.get_recent_alerts(24)["count"] == 1
    assert tools.get_recent_alerts(24 * 3, "fall")["count"] == 1


def test_remove_object(tools):
    assert tools.remove_object("mắt kính")["ok"]
    assert "Mắt kính" not in [o["name"] for o in tools.list_tracked_objects()["objects"]]


def test_question_set_with_rules_llm(tools):
    agent = Agent(tools, RulesLLM())
    for q, tool, must in QUESTIONS:
        a = agent.ask(q)
        assert tool in [c["name"] for c in a.tool_calls], q
        assert all(m in fold(a.text) for m in must), (q, a.text)


def test_api(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'api.db').as_posix()}")
    monkeypatch.setenv("LLM_PROVIDER", "rules")
    monkeypatch.setenv("TELEGRAM_BOT_ENABLED", "false")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:1/0")
    import importlib

    from fastapi.testclient import TestClient
    import services.assistant_api.main as m
    importlib.reload(m)
    with TestClient(m.app) as c:
        assert c.get("/health").json()["status"] == "ok"
        r = c.post("/chat", json={"message": "Cái ô của tôi đâu?"}).json()
        assert "chua" in fold(r["answer"])
        assert c.get("/image", params={"path": "../.env"}).status_code == 404


def test_live_snapshot(tools, bus):
    import numpy as np
    from services.assistant_api.agent import Agent
    assert not tools.get_live_snapshot()["ok"]
    bus.publish("cam_test", np.zeros((48, 64, 3), np.uint8))
    a = Agent(tools, RulesLLM()).ask("Chụp ảnh nhà hiện tại cho tôi")
    assert a.images and a.images[0].startswith("snapshots/live/")
