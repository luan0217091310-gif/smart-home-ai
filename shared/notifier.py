"""Module DUY NHẤT gửi cảnh báo (Telegram) và xử lý chống spam (cooldown)."""
from __future__ import annotations

import logging
import time
from pathlib import Path

import requests

from shared.config import env

log = logging.getLogger("notifier")


class CooldownGate:
    """Cho phép một sự kiện theo khóa tối đa 1 lần mỗi `cooldown_s` giây. Logic thuần, dễ test."""

    def __init__(self, clock=time.monotonic):
        self._last: dict[str, float] = {}
        self._clock = clock

    def allow(self, key: str, cooldown_s: float) -> bool:
        t = self._clock()
        last = self._last.get(key)
        if last is not None and t - last < cooldown_s:
            return False
        self._last[key] = t
        return True

    def reset(self, key: str) -> None:
        self._last.pop(key, None)


class TelegramClient:
    def __init__(self, token: str | None = None, chat_id: str | None = None, timeout: float = 15):
        self.token = token if token is not None else env("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id if chat_id is not None else env("TELEGRAM_CHAT_ID")
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def _url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def send_text(self, text: str, chat_id: str | None = None) -> bool:
        if not self.enabled:
            log.warning("Telegram chưa cấu hình, bỏ qua tin: %s", text)
            return False
        try:
            r = requests.post(self._url("sendMessage"),
                              data={"chat_id": chat_id or self.chat_id, "text": text}, timeout=self.timeout)
            r.raise_for_status()
            return True
        except Exception as e:  # noqa: BLE001
            log.error("Gửi Telegram thất bại: %s", type(e).__name__)
            return False

    def send_photo(self, image_path: str | Path, caption: str = "", chat_id: str | None = None) -> bool:
        if not self.enabled:
            log.warning("Telegram chưa cấu hình, bỏ qua ảnh: %s", caption)
            return False
        try:
            with open(image_path, "rb") as f:
                r = requests.post(self._url("sendPhoto"),
                                  data={"chat_id": chat_id or self.chat_id, "caption": caption[:1000]},
                                  files={"photo": f}, timeout=self.timeout)
            r.raise_for_status()
            return True
        except Exception as e:  # noqa: BLE001
            log.error("Gửi ảnh Telegram thất bại: %s", type(e).__name__)
            return False

    def send_voice(self, ogg_path: str | Path, chat_id: str | None = None) -> bool:
        if not self.enabled:
            return False
        try:
            with open(ogg_path, "rb") as f:
                r = requests.post(self._url("sendVoice"), data={"chat_id": chat_id or self.chat_id},
                                  files={"voice": f}, timeout=self.timeout)
            r.raise_for_status()
            return True
        except Exception as e:  # noqa: BLE001
            log.error("Gửi voice Telegram thất bại: %s", type(e).__name__)
            return False


class Notifier:
    """Gửi cảnh báo qua Telegram với cooldown theo khóa (vd. 'stranger:cam_test')."""

    def __init__(self, client: TelegramClient | None = None, gate: CooldownGate | None = None):
        self.client = client or TelegramClient()
        self.gate = gate or CooldownGate()

    def alert(self, key: str, cooldown_s: float, text: str, image_path: str | Path | None = None) -> bool:
        """Trả về True nếu cảnh báo được phép gửi (qua cooldown) — kể cả khi Telegram lỗi."""
        if not self.gate.allow(key, cooldown_s):
            log.info("Cooldown, không gửi lại: %s", key)
            return False
        if image_path and Path(image_path).exists():
            self.client.send_photo(image_path, text)
        else:
            self.client.send_text(text)
        return True
