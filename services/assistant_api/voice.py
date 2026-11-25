"""Nghe (faster-whisper, tiếng Việt, chạy CPU mặc định) và nói (edge-tts → OGG/Opus qua ffmpeg). Tùy chọn bật/tắt."""
from __future__ import annotations

import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path

from shared.config import env, env_bool, models_dir

log = logging.getLogger("voice")
_whisper = None


def enabled() -> bool:
    return env_bool("VOICE_ENABLED", False)


def transcribe(audio_path: str | Path) -> str:
    global _whisper
    from faster_whisper import WhisperModel

    if _whisper is None:
        device = env("WHISPER_DEVICE", "cpu")
        _whisper = WhisperModel(env("WHISPER_MODEL", "small"), device=device,
                                compute_type="int8" if device == "cpu" else "float16",
                                download_root=str(models_dir() / "whisper"))
    segments, _ = _whisper.transcribe(str(audio_path), language="vi", vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()


def synthesize_ogg(text: str) -> Path | None:
    """Trả file .ogg (Opus) hoặc None nếu edge-tts/ffmpeg lỗi (khi đó chỉ gửi chữ)."""
    try:
        import edge_tts

        tmp = Path(tempfile.mkdtemp())
        mp3, ogg = tmp / "a.mp3", tmp / "a.ogg"
        asyncio.run(edge_tts.Communicate(text[:800], env("TTS_VOICE", "vi-VN-HoaiMyNeural")).save(str(mp3)))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-c:a", "libopus", "-b:a", "32k", str(ogg)],
                       check=True, timeout=30)
        return ogg
    except Exception as e:  # noqa: BLE001
        log.warning("TTS lỗi, chỉ trả lời bằng chữ: %s", e)
        return None
