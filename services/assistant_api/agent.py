"""Ghép system prompt + LLM + công cụ. Dùng chung cho /chat, Telegram và bộ câu hỏi kiểm thử."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from services.assistant_api.llm import BaseLLM, make_llm
from services.assistant_api.tools import Tools
from shared.config import now

log = logging.getLogger("agent")
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_vi.txt"
WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def system_prompt() -> str:
    n = now()
    return PROMPT_PATH.read_text(encoding="utf-8").format(
        now=n.strftime("%H:%M ngày %d/%m/%Y"), weekday=WEEKDAYS[n.weekday()],
        hours_today=round(n.hour + n.minute / 60, 1))


@dataclass
class Answer:
    text: str
    images: list[str] = field(default_factory=list)   # đường dẫn tương đối trong data/
    tool_calls: list[dict] = field(default_factory=list)
    elapsed_s: float = 0.0
    provider: str = ""


class Agent:
    def __init__(self, tools: Tools, llm: BaseLLM | None = None):
        self.tools = tools
        self.llm = llm or make_llm()

    def ask(self, question: str) -> Answer:
        t0 = time.time()
        question = (question or "").strip()[:1000]
        try:
            text, calls = self.llm.run(system_prompt(), question, Tools.SPECS, self.tools.call)
        except Exception as e:  # noqa: BLE001
            log.error("LLM lỗi: %s", e)
            text, calls = "Xin lỗi, trợ lý đang gặp sự cố kết nối. Anh/chị thử lại sau nhé.", []
        images = []
        for c in calls:
            r = c.get("result") or {}
            if r.get("image_path"):
                images.append(r["image_path"])
            for a in (r.get("alerts") or [])[:3]:
                if a.get("image_path"):
                    images.append(a["image_path"])
        return Answer(text or "Xin lỗi, em chưa có câu trả lời.", list(dict.fromkeys(images)), calls,
                      round(time.time() - t0, 2), self.llm.name)
