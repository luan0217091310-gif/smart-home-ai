"""Bộ công cụ cho LLM gọi. LLM KHÔNG viết SQL; mọi tham số được kiểm tra kiểu và giới hạn."""
from __future__ import annotations

import unicodedata
from datetime import datetime, timedelta
from typing import Any

from shared.config import now
from shared.database import DB, STRANGER

MAX_HOURS = 24 * 30


def fold(s: str) -> str:
    """Bỏ dấu + chữ thường: 'Chìa Khóa' → 'chia khoa'."""
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(s.split())


def _hours(v: Any, default: float) -> float:
    try:
        h = float(v) if v not in (None, "") else default
    except (TypeError, ValueError):
        h = default
    return min(max(h, 0.05), MAX_HOURS)


def ago(t: datetime | None, ref: datetime | None = None) -> str:
    if t is None:
        return "chưa từng thấy"
    s = int(((ref or now()) - t).total_seconds())
    if s < 60:
        return "vừa xong"
    if s < 3600:
        return f"cách đây {s // 60} phút"
    if s < 86400:
        return f"cách đây {s // 3600} giờ {s % 3600 // 60} phút"
    return f"cách đây {s // 86400} ngày"


def _fmt(t: datetime) -> str:
    return t.strftime("%H:%M %d/%m")


class Tools:
    def __init__(self, db: DB, bus=None):  # noqa: ANN001
        self.db, self.bus = db, bus

    # --- định nghĩa cho LLM (JSON schema chung cho Gemini / Ollama)
    SPECS = [
        {"name": "get_visitors",
         "description": "Ai đã vào nhà / xuất hiện trước camera trong khoảng thời gian gần đây, kể cả số lần có người lạ.",
         "parameters": {"type": "object", "properties": {
             "since_hours": {"type": "number", "description": "Số giờ nhìn lại. 'nãy giờ'=2, 'gần đây'=24. Mặc định 24."},
             "member_name": {"type": "string", "description": "Tên thành viên cần lọc (tuỳ chọn)."}}}},
        {"name": "find_object",
         "description": "Tìm vị trí (vùng) và thời điểm thấy lần cuối của một đồ vật đang theo dõi.",
         "parameters": {"type": "object", "properties": {
             "object_name": {"type": "string", "description": "Tên đồ vật bằng tiếng Việt, vd. 'chìa khóa'."}},
             "required": ["object_name"]}},
        {"name": "register_new_object",
         "description": "Thêm một đồ vật mới để camera theo dõi.",
         "parameters": {"type": "object", "properties": {
             "vn_name": {"type": "string", "description": "Tên tiếng Việt, vd. 'Mũ bảo hiểm'."},
             "en_keyword": {"type": "string", "description": "Từ khóa tiếng Anh ngắn cho mô hình, vd. 'helmet'."}},
             "required": ["vn_name", "en_keyword"]}},
        {"name": "get_recent_alerts",
         "description": "Danh sách cảnh báo (người lạ, té ngã, hệ thống) gần đây.",
         "parameters": {"type": "object", "properties": {
             "since_hours": {"type": "number", "description": "Số giờ nhìn lại, mặc định 24."},
             "alert_type": {"type": "string", "enum": ["stranger", "fall", "system"]}}}},
        {"name": "list_tracked_objects", "description": "Liệt kê các đồ vật đang được theo dõi.",
         "parameters": {"type": "object", "properties": {}}},
        {"name": "remove_object", "description": "Ngừng theo dõi một đồ vật.",
         "parameters": {"type": "object", "properties": {"vn_name": {"type": "string"}}, "required": ["vn_name"]}},
    ]

    def call(self, name: str, args: dict | None) -> dict:
        fn = {s["name"] for s in self.SPECS}
        if name not in fn:
            return {"error": f"Không có công cụ {name}"}
        try:
            return getattr(self, name)(**{k: v for k, v in (args or {}).items() if isinstance(k, str)})
        except TypeError as e:
            return {"error": f"Tham số không hợp lệ: {e}"}

    # --- các công cụ
    def get_visitors(self, since_hours=24, member_name=None) -> dict:
        h = _hours(since_hours, 24)
        since = now() - timedelta(hours=h)
        name_filter = None
        if member_name:
            wanted = fold(str(member_name))
            for m in self.db.list_members():
                if fold(m.name) == wanted:
                    name_filter = m.name
            if name_filter is None:
                return {"since_hours": h, "visitors": [], "note": f"Không có thành viên tên '{member_name}'"}
        logs = self.db.access_logs_since(since, name_filter)
        people: dict[str, dict] = {}
        strangers = 0
        for lg in logs:
            if lg.member_name == STRANGER:
                strangers += 1
                continue
            p = people.setdefault(lg.member_name, {"name": lg.member_name, "first_seen": lg.timestamp,
                                                   "last_seen": lg.timestamp, "count": 0})
            p["last_seen"], p["count"] = lg.timestamp, p["count"] + 1
        visitors = [{"name": p["name"], "first_seen": _fmt(p["first_seen"]), "last_seen": _fmt(p["last_seen"]),
                     "last_seen_ago": ago(p["last_seen"]), "count": p["count"]} for p in people.values()]
        return {"since_hours": h, "visitors": visitors, "stranger_count": strangers}

    def _match_object(self, name: str, active_only=True):
        wanted = fold(name)
        objs = self.db.active_objects() if active_only else self.db.all_objects()
        for o in objs:
            if fold(o.object_name) == wanted or fold(o.prompt_keyword) == wanted:
                return o
        # khớp theo từ nguyên vẹn: "chìa khóa xe" ~ "chìa khóa", "kính" ~ "mắt kính" (bỏ từ đệm "cái", "chiếc")
        w = set(wanted.split()) - {"cai", "chiec", "con", "cua", "toi"}
        for o in objs:
            a = set(fold(o.object_name).split())
            if w and (w <= a or a <= w):
                return o
        return None

    def find_object(self, object_name: str) -> dict:
        o = self._match_object(str(object_name)[:100])
        if o is None:
            return {"found": False, "tracked": False, "object_name": object_name,
                    "tracked_objects": [x.object_name for x in self.db.active_objects()],
                    "note": "Đồ vật này chưa được theo dõi. Có thể đề nghị thêm bằng register_new_object."}
        if o.last_seen_at is None:
            return {"found": False, "tracked": True, "object_name": o.object_name,
                    "note": "Đang theo dõi nhưng camera chưa từng thấy."}
        return {"found": True, "tracked": True, "object_name": o.object_name, "zone": o.last_zone,
                "last_seen": _fmt(o.last_seen_at), "last_seen_ago": ago(o.last_seen_at),
                "confidence": round(o.last_confidence or 0, 2), "image_path": o.image_path}

    def register_new_object(self, vn_name: str, en_keyword: str) -> dict:
        vn, en = str(vn_name).strip()[:60], str(en_keyword).strip().lower()[:40]
        if not vn or not en or not all(c.isascii() for c in en):
            return {"ok": False, "error": "Cần tên tiếng Việt và từ khóa tiếng Anh (không dấu)."}
        existing = self._match_object(vn) or self._match_object(en)
        if existing is not None:
            return {"ok": True, "already_tracked": True, "object_name": existing.object_name}
        o, created = self.db.add_object(vn, en)
        if self.bus is not None:
            self.bus.bump_objects_version()
        return {"ok": True, "already_tracked": not created, "object_name": o.object_name, "keyword": o.prompt_keyword}

    def get_recent_alerts(self, since_hours=24, alert_type=None) -> dict:
        h = _hours(since_hours, 24)
        if alert_type not in (None, "", "stranger", "fall", "system"):
            alert_type = None
        rows = self.db.alerts_since(now() - timedelta(hours=h), alert_type or None)
        return {"since_hours": h, "count": len(rows), "alerts": [
            {"type": a.alert_type, "time": _fmt(a.timestamp), "ago": ago(a.timestamp), "message": a.message,
             "status": a.status, "image_path": a.image_path} for a in rows[:20]]}

    def list_tracked_objects(self) -> dict:
        return {"objects": [{"name": o.object_name, "keyword": o.prompt_keyword, "zone": o.last_zone,
                             "last_seen_ago": ago(o.last_seen_at)} for o in self.db.active_objects()]}

    def remove_object(self, vn_name: str) -> dict:
        o = self._match_object(str(vn_name))
        if o is None:
            return {"ok": False, "error": "Không tìm thấy đồ vật đang theo dõi với tên này."}
        self.db.set_object_active(o.id, False)
        if self.bus is not None:
            self.bus.bump_objects_version()
        return {"ok": True, "removed": o.object_name}
