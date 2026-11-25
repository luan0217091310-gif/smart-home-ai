"""Đọc cấu hình từ .env và config/settings.yaml, thiết lập log chung."""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

ROOT = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(ROOT / ".env", override=False)

TZ = ZoneInfo(os.getenv("TZ", "Asia/Ho_Chi_Minh") or "Asia/Ho_Chi_Minh")


class ConfigError(RuntimeError):
    pass


def env(name: str, default: str | None = None, required: bool = False) -> str | None:
    """Lấy biến môi trường; bỏ phần chú thích '#' phía sau. Thiếu biến bắt buộc thì dừng."""
    raw = os.getenv(name)
    if raw is not None:
        raw = raw.split(" #")[0].strip()
    value = raw if raw not in (None, "") else default
    if required and value in (None, ""):
        raise ConfigError(f"Thiếu biến bắt buộc trong .env: {name}")
    return value


def env_int(name: str, default: int) -> int:
    return int(env(name, str(default)))


def env_bool(name: str, default: bool = False) -> bool:
    return str(env(name, str(default))).lower() in ("1", "true", "yes", "on")


@lru_cache(maxsize=1)
def settings() -> dict:
    path = Path(env("SETTINGS_PATH", str(ROOT / "config" / "settings.yaml")))
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def data_dir() -> Path:
    p = Path(env("DATA_DIR", str(ROOT / "data")))
    if not p.is_absolute():
        p = ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def models_dir() -> Path:
    p = Path(env("MODELS_DIR", str(ROOT / "models")))
    if not p.is_absolute():
        p = ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def camera_id() -> str:
    return env("CAMERA_ID", "cam_test")


def now() -> datetime:
    """Thời điểm hiện tại theo giờ Việt Nam (naive, để lưu SQLite thống nhất)."""
    return datetime.now(TZ).replace(tzinfo=None)


def setup_logging(service: str) -> logging.Logger:
    level = env("LOG_LEVEL", "INFO")
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format=f"%(asctime)s | %(levelname)-7s | {service} | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
    logging.Formatter.converter = lambda *a: datetime.now(TZ).timetuple()
    return logging.getLogger(service)
