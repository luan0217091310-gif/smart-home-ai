"""assistant_api: FastAPI — POST /chat, POST /voice, GET /health, GET /image. Kèm Telegram bot long polling.

Chạy:  uvicorn services.assistant_api.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, File, HTTPException, UploadFile  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from services.assistant_api import voice  # noqa: E402
from services.assistant_api.agent import Agent  # noqa: E402
from services.assistant_api.telegram_bot import TelegramBot  # noqa: E402
from services.assistant_api.tools import Tools  # noqa: E402
from shared.config import data_dir, env_bool, setup_logging  # noqa: E402
from shared.database import DB  # noqa: E402
from shared.frame_bus import FrameBus  # noqa: E402

SERVICE = "assistant_api"
log = setup_logging(SERVICE)


def _make_bus():
    try:
        b = FrameBus()
        b.r.ping()
        return b
    except Exception:  # noqa: BLE001
        log.warning("Không kết nối được Redis — nạp nóng đồ vật sẽ không báo cho worker")
        return None


db, bus = DB(), _make_bus()
agent = Agent(Tools(db, bus))
app = FastAPI(title="smart-home-ai assistant")


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


@app.on_event("startup")
def _startup() -> None:
    log.info("Trợ lý dùng LLM: %s", agent.llm.name)
    if env_bool("TELEGRAM_BOT_ENABLED", True):
        TelegramBot(agent).start()
    if bus is not None:
        def hb():
            while True:
                try:
                    bus.heartbeat(SERVICE)
                    for a in bus.pop_alerts():
                        from datetime import datetime
                        from shared.config import TZ
                        ts = datetime.fromtimestamp(a["ts"], TZ).replace(tzinfo=None)
                        db.add_alert(a["camera_id"], a["alert_type"], a["message"], status=a["status"], ts=ts)
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(10)
        threading.Thread(target=hb, daemon=True).start()


@app.get("/health")
def health():
    return {"status": "ok", "llm": agent.llm.name, "voice": voice.enabled()}


@app.post("/chat")
def chat(body: ChatIn):
    a = agent.ask(body.message)
    return {"answer": a.text, "images": a.images, "tool_calls": [{"name": c["name"], "args": c["args"]} for c in a.tool_calls],
            "elapsed_s": a.elapsed_s, "llm": a.provider}


@app.post("/voice")
async def voice_endpoint(file: UploadFile = File(...)):
    if not voice.enabled():
        raise HTTPException(400, "Giọng nói đang tắt (VOICE_ENABLED=false)")
    path = Path(tempfile.mkdtemp()) / (Path(file.filename or "in.ogg").name)
    path.write_bytes(await file.read())
    text = voice.transcribe(path)
    a = agent.ask(text)
    return {"transcript": text, "answer": a.text, "images": a.images, "elapsed_s": a.elapsed_s}


@app.get("/snapshot")
def snapshot():
    """Ảnh hiện tại từ camera (JPEG)."""
    from fastapi.responses import Response
    from shared.config import camera_id
    raw = bus.get_latest_jpeg(camera_id()) if bus else None
    if raw is None:
        raise HTTPException(503, "Camera chưa có hình")
    return Response(raw[0], media_type="image/jpeg")


@app.get("/image")
def image(path: str):
    """Trả ảnh trong data/snapshots — chặn truy cập ra ngoài thư mục."""
    base = (data_dir() / "snapshots").resolve()
    p = (data_dir() / path).resolve()
    if base not in p.parents or not p.is_file():
        raise HTTPException(404)
    return FileResponse(p)
