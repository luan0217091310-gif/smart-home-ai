"""Dữ liệu giả đã biết trước, dùng cho bộ câu hỏi kiểm thử và demo."""
from __future__ import annotations

from datetime import timedelta

import numpy as np

from shared.config import now
from shared.database import DB, STRANGER


def seed_demo(db: DB) -> dict:
    n = now()
    bo = db.upsert_member("Bố", np.ones(512, np.float32) / np.sqrt(512), 8, "owner")
    me = db.upsert_member("Mẹ", -np.ones(512, np.float32) / np.sqrt(512), 7, "family")
    db.add_access_log("cam_test", bo.id, "Bố", 0.71, ts=n - timedelta(minutes=50))
    db.add_access_log("cam_test", me.id, "Mẹ", 0.66, ts=n - timedelta(hours=5))
    db.add_access_log("cam_test", None, STRANGER, 0.21, ts=n - timedelta(minutes=30))
    db.add_alert("cam_test", "stranger", "Cảnh báo: phát hiện người lạ", None, "sent", n - timedelta(minutes=30))
    db.add_alert("cam_test", "fall", "KHẨN: té ngã (diễn thử)", None, "false_alarm", n - timedelta(days=2))
    keys, _ = db.add_object("Chìa khóa", "keys")
    db.add_object("Mắt kính", "glasses")
    db.update_object_seen(keys.id, "Bàn làm việc", "cam_test", 0.62, "snapshots/objects/object_1.jpg",
                          n - timedelta(minutes=12))
    return {"keys_zone": "Bàn làm việc"}


# (câu hỏi, công cụ mong đợi, chuỗi phải có trong câu trả lời — không dấu, chữ thường)
QUESTIONS = [
    ("Nãy giờ có ai vào nhà không?", "get_visitors", ["bo"]),
    ("Chìa khóa của tôi đâu rồi?", "find_object", ["ban lam viec"]),
    ("chia khoa cua toi o dau", "find_object", ["ban lam viec"]),
    ("Hãy giúp tôi theo dõi thêm cái mũ bảo hiểm", "register_new_object", ["mu bao hiem"]),
    ("Hôm nay có cảnh báo gì không?", "get_recent_alerts", ["nguoi la"]),
    ("Cái ô của tôi đâu?", "find_object", ["chua"]),
    ("Kính của tôi đâu?", "find_object", ["chua"]),
]
