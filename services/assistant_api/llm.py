"""Lớp LLM chung: Gemini (REST, function calling), Ollama (/api/chat + tools), và 'rules' (offline, demo không cần khóa).

Chọn bằng LLM_PROVIDER = gemini | ollama | rules.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Callable

import requests

from shared.config import env

log = logging.getLogger("llm")
MAX_TOOL_ROUNDS = 5
ToolRunner = Callable[[str, dict], dict]


class LLMError(RuntimeError):
    pass


class BaseLLM:
    name = "base"

    def run(self, system: str, user: str, tools: list[dict], call_tool: ToolRunner) -> tuple[str, list[dict]]:
        """Trả về (câu trả lời, danh sách lượt gọi công cụ [{name,args,result}])."""
        raise NotImplementedError

    def simple(self, text: str) -> str:
        return self.run("Trả lời ngắn gọn bằng tiếng Việt.", text, [], lambda n, a: {})[0]


class GeminiLLM(BaseLLM):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float = 30):
        self.key = api_key or env("GEMINI_API_KEY", required=True)
        self.model = model or env("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.timeout = timeout

    def _post(self, body: dict) -> dict:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        r = requests.post(url, json=body, headers={"x-goog-api-key": self.key}, timeout=self.timeout)
        if r.status_code != 200:
            raise LLMError(f"Gemini HTTP {r.status_code}: {r.text[:300]}")
        return r.json()

    def run(self, system, user, tools, call_tool):
        contents = [{"role": "user", "parts": [{"text": user}]}]
        body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents,
                "generationConfig": {"temperature": 0.2}}
        if tools:
            body["tools"] = [{"functionDeclarations": tools}]
        calls = []
        for _ in range(MAX_TOOL_ROUNDS + 1):
            data = self._post(body)
            cands = data.get("candidates") or []
            if not cands:
                raise LLMError(f"Gemini không trả lời: {str(data)[:200]}")
            content = cands[0].get("content", {"role": "model", "parts": []})
            parts = content.get("parts", [])
            fcalls = [p["functionCall"] for p in parts if "functionCall" in p]
            if not fcalls:
                return "".join(p.get("text", "") for p in parts).strip(), calls
            contents.append(content)  # giữ nguyên (kể cả thoughtSignature)
            responses = []
            for fc in fcalls:
                args = fc.get("args") or {}
                result = call_tool(fc["name"], args)
                calls.append({"name": fc["name"], "args": args, "result": result})
                responses.append({"functionResponse": {"name": fc["name"], "response": {"result": result}}})
            contents.append({"role": "user", "parts": responses})
        return "Xin lỗi, tôi chưa trả lời được câu này.", calls


class OllamaLLM(BaseLLM):
    name = "ollama"

    def __init__(self, url: str | None = None, model: str | None = None, timeout: float = 60):
        self.url = (url or env("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or env("OLLAMA_MODEL", required=True)
        self.timeout = timeout

    def run(self, system, user, tools, call_tool):
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        calls = []
        for _ in range(MAX_TOOL_ROUNDS + 1):
            body = {"model": self.model, "messages": msgs, "stream": False, "options": {"temperature": 0.2}}
            if tools:
                body["tools"] = [{"type": "function", "function": t} for t in tools]
            r = requests.post(f"{self.url}/api/chat", json=body, timeout=self.timeout)
            if r.status_code != 200:
                raise LLMError(f"Ollama HTTP {r.status_code}: {r.text[:300]}")
            msg = r.json().get("message", {})
            tcs = msg.get("tool_calls") or []
            if not tcs:
                return (msg.get("content") or "").strip(), calls
            msgs.append(msg)
            for tc in tcs:
                fn = tc.get("function", {})
                args = fn.get("arguments") or {}
                if isinstance(args, str):
                    args = json.loads(args or "{}")
                result = call_tool(fn.get("name", ""), args)
                calls.append({"name": fn.get("name"), "args": args, "result": result})
                msgs.append({"role": "tool", "tool_name": fn.get("name"), "content": json.dumps(result, ensure_ascii=False)})
        return "Xin lỗi, tôi chưa trả lời được câu này.", calls


class RulesLLM(BaseLLM):
    """Bộ định tuyến từ khóa, KHÔNG gọi dịch vụ ngoài — dùng để demo/kiểm thử khi chưa có khóa API."""
    name = "rules"

    def run(self, system, user, tools, call_tool):
        from services.assistant_api.tools import fold

        q = fold(user)
        calls = []

        def call(name, args):
            res = call_tool(name, args)
            calls.append({"name": name, "args": args, "result": res})
            return res

        hours = 2 if "nay gio" in q else (None if "hom nay" in q else 24)
        if "hom nay" in q:
            from shared.config import now
            n = now()
            hours = round(n.hour + n.minute / 60 + 0.01, 2)
        m = re.search(r"theo doi (them )?(cai |chiec |con )?(.+)", q)
        if m and any(w in q for w in ("them", "giup", "hay theo doi")):
            vn_raw = m.group(3).strip(" ?.!")
            vn = _restore_case(user, vn_raw)
            kw = _GUESS_EN.get(vn_raw, vn_raw.split()[-1])
            res = call("register_new_object", {"vn_name": vn, "en_keyword": kw})
            if res.get("ok"):
                return (f"Đã có sẵn trong danh sách theo dõi: {res['object_name']}." if res.get("already_tracked")
                        else f"Đã thêm '{res['object_name']}' (từ khóa '{res['keyword']}'), camera sẽ tìm ở chu kỳ tới."), calls
            return f"Chưa thêm được: {res.get('error')}", calls
        if any(w in q for w in ("canh bao", "bao dong", "nga")):
            res = call("get_recent_alerts", {"since_hours": hours or 24})
            if not res["alerts"]:
                return "Không có cảnh báo nào trong khoảng thời gian này.", calls
            lines = [f"- {a['time']}: {a['message']}" for a in res["alerts"][:5]]
            return f"Có {res['count']} cảnh báo:\n" + "\n".join(lines), calls
        if any(w in q for w in ("ai vao", "ai den", "co ai", "ai o nha", "nguoi la")):
            res = call("get_visitors", {"since_hours": hours or 24})
            if not res["visitors"] and not res["stranger_count"]:
                return "Không thấy ai trong khoảng thời gian này.", calls
            parts = [f"{v['name']} (lần cuối {v['last_seen']}, {v['last_seen_ago']})" for v in res["visitors"]]
            s = ("Có " + ", ".join(parts) + ".") if parts else "Không có thành viên nào."
            if res["stranger_count"]:
                s += f" Có {res['stranger_count']} lần phát hiện người lạ."
            return s, calls
        if any(w in q for w in ("dang theo doi", "danh sach do")):
            res = call("list_tracked_objects", {})
            return "Đang theo dõi: " + ", ".join(o["name"] for o in res["objects"]), calls
        m = re.search(r"(cai |chiec |con )?(.+?) (cua toi |cua em |cua minh )?(dau|o dau|de dau)", q)
        if m:
            name = m.group(2).replace("cai ", "").strip()
            res = call("find_object", {"object_name": name})
            if res.get("found"):
                return f"{res['object_name']} thấy lần cuối ở {res['zone']} lúc {res['last_seen']} ({res['last_seen_ago']}).", calls
            if res.get("tracked"):
                return f"Tôi đang theo dõi {res['object_name']} nhưng camera chưa thấy lần nào.", calls
            return (f"Tôi chưa theo dõi '{_restore_case(user, name).lower()}' nên không biết nó ở đâu. "
                    f"Bạn có muốn tôi theo dõi thêm không?"), calls
        return "Xin lỗi, tôi chưa hiểu. Bạn có thể hỏi: ai vào nhà, đồ vật ở đâu, có cảnh báo gì không.", calls


_GUESS_EN = {"mu bao hiem": "helmet", "chia khoa": "keys", "kinh": "glasses", "mat kinh": "glasses",
             "vi": "wallet", "vi tien": "wallet", "dien thoai": "cell phone", "coc": "cup", "coc nuoc": "cup",
             "o": "umbrella", "cai o": "umbrella", "dieu khien": "remote", "balo": "backpack", "tui xach": "handbag",
             "laptop": "laptop", "sach": "book", "chai nuoc": "bottle"}


def _restore_case(original: str, folded_part: str) -> str:
    """Lấy lại đoạn có dấu tương ứng từ câu gốc (cùng số từ ở cuối)."""
    from services.assistant_api.tools import fold
    words = original.strip(" ?.!").split()
    n = len(folded_part.split())
    for i in range(len(words) - n + 1):
        if fold(" ".join(words[i:i + n])) == folded_part:
            return " ".join(words[i:i + n]).capitalize()
    return folded_part.capitalize()


def make_llm(provider: str | None = None) -> BaseLLM:
    p = (provider or env("LLM_PROVIDER", "gemini")).lower()
    if p == "gemini":
        if not env("GEMINI_API_KEY"):
            log.warning("Chưa có GEMINI_API_KEY → dùng chế độ 'rules' (offline) để demo")
            return RulesLLM()
        return GeminiLLM()
    if p == "ollama":
        return OllamaLLM()
    return RulesLLM()
