import sys
from pathlib import Path

import fakeredis
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def db(tmp_path):
    from shared.database import DB
    return DB(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")


@pytest.fixture
def bus():
    from shared.frame_bus import FrameBus
    return FrameBus(client=fakeredis.FakeRedis(), jpeg_quality=90)
