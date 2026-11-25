"""GĐ 0: gửi 1 tin nhắn chữ và 1 ảnh thử vào Telegram.  Chạy: python scripts/test_telegram.py"""
import _bootstrap  # noqa: F401
import sys
import tempfile

import cv2
import numpy as np

from shared.config import now, setup_logging
from shared.notifier import TelegramClient

log = setup_logging("test_telegram")
tg = TelegramClient()
if not tg.enabled:
    sys.exit("Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong .env")

ok1 = tg.send_text(f"✅ smart-home-ai: tin nhắn thử lúc {now():%H:%M:%S %d/%m/%Y}")
img = np.full((240, 480, 3), (40, 120, 40), np.uint8)
cv2.putText(img, "smart-home-ai test", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
path = tempfile.gettempdir() + "/sha_test.jpg"
cv2.imwrite(path, img)
ok2 = tg.send_photo(path, "Ảnh thử từ smart-home-ai")
log.info("Tin chữ: %s | Ảnh: %s", "OK" if ok1 else "LỖI", "OK" if ok2 else "LỖI")
sys.exit(0 if ok1 and ok2 else 1)
