"""GĐ 0: hỏi LLM (Gemini hoặc Ollama) 1 câu tiếng Việt."""
import _bootstrap  # noqa: F401

from services.assistant_api.llm import make_llm
from shared.config import setup_logging

log = setup_logging("check_llm")
llm = make_llm()
reply = llm.simple("Xin chào! Trả lời đúng một câu ngắn bằng tiếng Việt: thủ đô Việt Nam là gì?")
print(reply)
