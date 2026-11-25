"""Chạy bộ câu hỏi mẫu trên CSDL giả (tạm, không đụng data/smarthome.db), so với đáp án mong đợi.

  python scripts/eval_assistant.py                 # dùng LLM_PROVIDER trong .env (Gemini / Ollama / rules)
  python scripts/eval_assistant.py --provider rules
  python scripts/eval_assistant.py --questions my_questions.txt   # thêm câu của bạn (mỗi dòng 1 câu, không chấm điểm)
"""
import _bootstrap  # noqa: F401
import argparse
import tempfile
from pathlib import Path

from services.assistant_api.agent import Agent
from services.assistant_api.fixtures import QUESTIONS, seed_demo
from services.assistant_api.llm import make_llm
from services.assistant_api.tools import Tools, fold
from shared.config import setup_logging
from shared.database import DB

setup_logging("eval_assistant")
ap = argparse.ArgumentParser()
ap.add_argument("--provider")
ap.add_argument("--questions")
args = ap.parse_args()

tmp = Path(tempfile.mkdtemp()) / "eval.db"
db = DB(f"sqlite:///{tmp.as_posix()}")
seed_demo(db)
agent = Agent(Tools(db, None), make_llm(args.provider))
print(f"LLM: {agent.llm.name}\n")
ok_count, rows = 0, []
for q, tool, must in QUESTIONS:
    a = agent.ask(q)
    used = [c["name"] for c in a.tool_calls]
    ok = tool in used and all(m in fold(a.text) for m in must)
    ok_count += ok
    rows.append((q, a.text, used, a.elapsed_s, ok))
    print(f"[{'ĐÚNG' if ok else 'SAI '}] {q}\n   → {a.text}\n   công cụ: {used} · {a.elapsed_s}s\n")
print(f"Kết quả: {ok_count}/{len(QUESTIONS)} đúng")
print(f"Sau câu 'theo dõi mũ bảo hiểm', CSDL có: {[o.prompt_keyword for o in db.active_objects()]}")
if args.questions:
    print("\n== Câu hỏi của bạn ==")
    for line in Path(args.questions).read_text(encoding="utf-8").splitlines():
        if line.strip():
            a = agent.ask(line.strip())
            print(f"? {line.strip()}\n→ {a.text}  ({a.elapsed_s}s)\n")
