"""GĐ 6: Dashboard — sai mật khẩu không vào được; đúng mật khẩu thấy 4 tab; nút 'Báo giả' đổi trạng thái."""
from datetime import datetime

import pytest

from streamlit.testing.v1 import AppTest

APP = "../services/dashboard/app.py"


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret-pw")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'd.db').as_posix()}")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("REDIS_URL", "redis://localhost:1/0")
    monkeypatch.setenv("DASHBOARD_REFRESH_S", "0")
    return tmp_path


def test_wrong_password_blocked(env):
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.text_input[0].input("wrong")
    at.button[0].click().run()
    assert any("Sai mật khẩu" in e.value for e in at.error)
    assert len(at.tabs) == 0


def test_login_and_false_alarm(env):
    from shared.database import DB
    db = DB()
    aid = db.add_alert("cam_test", "stranger", "Người lạ thử", status="sent")
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.text_input[0].input("secret-pw")
    at.button[0].click().run()
    assert not at.exception
    assert [t.label for t in at.tabs] == ["📹 Live & Cảnh báo", "👪 Thành viên", "🔑 Đồ vật & Vùng", "💬 Trò chuyện"]
    at.button(key=f"fa{aid}").click().run()
    assert db.alerts_since(datetime(2000, 1, 1))[0].status == "false_alarm"
