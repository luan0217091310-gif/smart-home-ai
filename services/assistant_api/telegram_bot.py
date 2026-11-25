"""Telegram bot long polling (không cần mở cổng). Chỉ trả lời các chat_id được phép."""
from __future__ import annotations

import logging
import tempfile
import threading
import time
from pathlib import Path

import requests

from services.assistant_api import voice
from services.assistant_api.agent import Agent
from shared.config import env
from shared.notifier import TelegramClient
from shared.snapshots import resolve

log = logging.getLogger("telegram_bot")


def allowed_chat_ids() -> set[str]:
    raw = env("TELEGRAM_ALLOWED_CHAT_IDS") or env("TELEGRAM_CHAT_ID") or ""
    return {x.strip() for x in raw.split(",") if x.strip()}


class TelegramBot:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.client = TelegramClient()
        self.allowed = allowed_chat_ids()
        self.offset = 0
        self._stop = False

    def _api(self, method: str, **params):
        r = requests.get(self.client._url(method), params=params, timeout=params.get("timeout", 10) + 10)
        r.raise_for_status()
        return r.json().get("result")

    def handle(self, msg: dict) -> None:
        chat_id = str(msg.get("chat", {}).get("id"))
        if chat_id not in self.allowed:
            log.warning("Bỏ qua tin từ chat_id không được phép: %s", chat_id)
            return
        text = msg.get("text")
        is_voice = "voice" in msg or "audio" in msg
        if is_voice:
            if not voice.enabled():
                self.client.send_text("Chức năng giọng nói đang tắt (VOICE_ENABLED=false).", chat_id)
                return
            fid = (msg.get("voice") or msg.get("audio"))["file_id"]
            info = self._api("getFile", file_id=fid)
            data = requests.get(f"https://api.telegram.org/file/bot{self.client.token}/{info['file_path']}", timeout=30)
            path = Path(tempfile.mkdtemp()) / "in.ogg"
            path.write_bytes(data.content)
            text = voice.transcribe(path)
            self.client.send_text(f"🎙️ {text}", chat_id)
        if not text:
            return
        if text.strip() in ("/start", "/help"):
            self.client.send_text("Xin chào! Hỏi em: 'Nãy giờ có ai vào nhà không?', 'Chìa khóa của tôi đâu?', "
                                  "'Hôm nay có cảnh báo gì không?'", chat_id)
            return
        ans = self.agent.ask(text)
        self.client.send_text(ans.text, chat_id)
        for rel in ans.images[:2]:
            p = resolve(rel)
            if p and p.exists():
                self.client.send_photo(p, "", chat_id)
        if is_voice and (ogg := voice.synthesize_ogg(ans.text)):
            self.client.send_voice(ogg, chat_id)

    def loop(self) -> None:
        log.info("Telegram bot chạy, chat_id được phép: %d", len(self.allowed))
        while not self._stop:
            try:
                updates = self._api("getUpdates", offset=self.offset, timeout=25) or []
                for u in updates:
                    self.offset = u["update_id"] + 1
                    if "message" in u:
                        try:
                            self.handle(u["message"])
                        except Exception as e:  # noqa: BLE001
                            log.error("Lỗi xử lý tin nhắn: %s", e)
            except Exception as e:  # noqa: BLE001
                log.warning("getUpdates lỗi (%s), thử lại sau 5s", type(e).__name__)
                time.sleep(5)

    def start(self) -> threading.Thread | None:
        if not self.client.token or not self.allowed:
            log.warning("Chưa cấu hình Telegram → không chạy bot")
            return None
        t = threading.Thread(target=self.loop, daemon=True)
        t.start()
        return t
