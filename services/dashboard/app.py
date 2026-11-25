"""Dashboard Streamlit: Live & Cảnh báo · Thành viên · Đồ vật & Vùng · Trò chuyện. Có mật khẩu, chỉ dùng trong mạng nhà.

Chạy:  streamlit run services/dashboard/app.py
"""
from __future__ import annotations

import base64
import hmac
import shutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd  # noqa: E402
import requests  # noqa: E402
import streamlit as st  # noqa: E402

from shared.config import camera_id, data_dir, env, now  # noqa: E402
from shared.database import DB  # noqa: E402
from shared.frame_bus import FrameBus  # noqa: E402
from shared.snapshots import resolve  # noqa: E402

SERVICES = ["stream_producer", "worker_face", "worker_object", "worker_fall", "assistant_api"]
ALERT_ICON = {"stranger": "🚨 Người lạ", "fall": "🆘 Té ngã", "system": "⚠️ Hệ thống"}
STATUS_VN = {"new": "Mới", "sent": "Đã gửi", "acknowledged": "Đã xem", "false_alarm": "Báo giả"}

st.set_page_config(page_title="Camera AI Thông Minh", page_icon="🏠", layout="wide")


# ---------- đăng nhập
def check_password() -> bool:
    pw = env("DASHBOARD_PASSWORD")
    if not pw:
        st.error("Chưa đặt DASHBOARD_PASSWORD trong .env — Dashboard bị khóa.")
        return False
    if st.session_state.get("auth"):
        return True
    with st.form("login"):
        st.subheader("🏠 Camera AI Thông Minh")
        entered = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("Đăng nhập"):
            if hmac.compare_digest(entered.encode(), pw.encode()):
                st.session_state.auth = True
                st.rerun()
            st.error("Sai mật khẩu")
            time.sleep(1)
    return False


if not check_password():
    st.stop()


@st.cache_resource
def get_db() -> DB:
    return DB()


@st.cache_resource
def get_bus():
    try:
        b = FrameBus()
        b.r.ping()
        return b
    except Exception:  # noqa: BLE001
        return None


db, bus, cam = get_db(), get_bus(), camera_id()
api = env("ASSISTANT_URL", "http://localhost:8000")


def show_image(rel: str | None, **kw) -> None:
    p = resolve(rel)
    if p and p.exists():
        st.image(str(p), **kw)


def beep_html() -> str:
    """Âm báo trên trình duyệt (quyết định 'âm thanh tại chỗ' của GĐ 4)."""
    import io
    import math
    import struct
    import wave
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(16000)
        w.writeframes(b"".join(struct.pack("<h", int(12000 * math.sin(2 * math.pi * 880 * i / 16000)) if (i // 2400) % 2 == 0 else 0)
                               for i in range(16000 * 2)))
    return f'<audio autoplay src="data:audio/wav;base64,{base64.b64encode(buf.getvalue()).decode()}"></audio>'


st.title("🏠 Camera AI Thông Minh")
tab_live, tab_members, tab_objects, tab_chat = st.tabs(["📹 Live & Cảnh báo", "👪 Thành viên", "🔑 Đồ vật & Vùng", "💬 Trò chuyện"])

# ---------- TAB 1: Live & Cảnh báo
with tab_live:
    @st.fragment(run_every=float(env("DASHBOARD_REFRESH_S", "2")) or None)
    def live():
        c1, c2 = st.columns([3, 1])
        with c1:
            raw = bus.get_latest_jpeg(cam) if bus else None
            if raw:
                jpg, fid, ts = raw
                st.image(jpg, caption=f"{cam} · khung #{fid} · trễ {(time.time() - ts) * 1000:.0f} ms", use_container_width=True)
            else:
                st.info("Chưa có hình từ camera (stream_producer chưa chạy hoặc Redis không kết nối).")
        with c2:
            st.markdown("**Trạng thái service**")
            hbs = bus.heartbeats(SERVICES) if bus else {}
            for s in SERVICES:
                t = hbs.get(s)
                ok = t is not None and time.time() - t < 30
                st.markdown(f"{'🟢' if ok else '🔴'} `{s}`" + (f" · {time.time() - t:.0f}s" if t else ""))
            st.markdown(f"{'🟢' if bus else '🔴'} `redis`")
        # âm báo khi có cảnh báo té ngã mới
        falls = [a for a in db.alerts_since(now() - timedelta(minutes=2), "fall") if a.status in ("new", "sent")]
        last = st.session_state.get("last_fall_id", 0)
        if falls and falls[0].id > last:
            st.session_state.last_fall_id = falls[0].id
            if last:
                st.html(beep_html())
            st.error(f"🆘 {falls[0].message}")
    live()

    st.subheader("Cảnh báo")
    c1, c2 = st.columns(2)
    days = c1.selectbox("Khoảng thời gian", [1, 7, 30], format_func=lambda d: f"{d} ngày qua")
    types = c2.multiselect("Loại", list(ALERT_ICON), default=list(ALERT_ICON), format_func=ALERT_ICON.get)
    alerts = [a for a in db.alerts_since(now() - timedelta(days=days)) if a.alert_type in types]
    if not alerts:
        st.caption("Không có cảnh báo.")
    for a in alerts[:50]:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 1.4])
            with c1:
                show_image(a.image_path, use_container_width=True)
            with c2:
                st.markdown(f"**{ALERT_ICON.get(a.alert_type, a.alert_type)}** · {a.timestamp:%H:%M:%S %d/%m/%Y} · "
                            f"`{STATUS_VN.get(a.status, a.status)}`")
                st.write(a.message)
            with c3:
                if st.button("✅ Đã xem", key=f"ack{a.id}", disabled=a.status == "acknowledged"):
                    db.set_alert_status(a.id, "acknowledged")
                    st.rerun()
                if st.button("🚫 Báo giả", key=f"fa{a.id}", disabled=a.status == "false_alarm"):
                    db.set_alert_status(a.id, "false_alarm")
                    st.rerun()

# ---------- TAB 2: Thành viên
with tab_members:
    members = db.list_members()
    st.subheader(f"Thành viên ({len(members)})")
    for m in members:
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f"**{m.name}** · {m.role}")
        c2.caption(f"{m.num_images} ảnh · đăng ký {m.created_at:%d/%m/%Y}")
        if c3.button("🗑️ Xóa", key=f"del{m.id}"):
            st.session_state.confirm_del = m.id
        if st.session_state.get("confirm_del") == m.id:
            st.warning(f"Xóa {m.name}? Vector khuôn mặt và toàn bộ ảnh mẫu sẽ bị xóa vĩnh viễn.")
            if st.button("Xác nhận xóa", key=f"cdel{m.id}", type="primary"):
                db.delete_member(m.id)
                shutil.rmtree(data_dir() / "faces" / m.name, ignore_errors=True)
                if bus:
                    bus.bump_members_version()
                st.session_state.confirm_del = None
                st.rerun()

    st.subheader("➕ Thêm thành viên")
    with st.form("add_member", clear_on_submit=True):
        name = st.text_input("Tên hiển thị")
        role = st.selectbox("Vai trò", ["family", "owner", "guest"])
        files = st.file_uploader("5–10 ảnh rõ mặt, mỗi ảnh một người", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        consent = st.checkbox("Người này đã đồng ý đăng ký khuôn mặt")
        if st.form_submit_button("Đăng ký"):
            safe = "".join(ch for ch in name.strip() if ch.isalnum() or ch in " _-").strip()
            if not safe or len(files) < 5 or not consent:
                st.error("Cần tên, ít nhất 5 ảnh và xác nhận đồng ý.")
            elif bus is None:
                st.error("Redis không kết nối — worker_face không nhận được yêu cầu.")
            else:
                folder = data_dir() / "faces" / safe
                folder.mkdir(parents=True, exist_ok=True)
                for i, f in enumerate(files):
                    (folder / f"upload_{int(time.time())}_{i}{Path(f.name).suffix.lower()}").write_bytes(f.getvalue())
                (folder / "role.txt").write_text(role, encoding="utf-8")
                bus.request_enroll(safe, role)
                st.success(f"Đã gửi {len(files)} ảnh của {safe}. worker_face sẽ đăng ký trong vài giây.")

    st.subheader("📒 Lịch sử ra vào")
    day = st.date_input("Ngày", value=now().date())
    start = datetime.combine(day, datetime.min.time())
    logs = [lg for lg in db.access_logs_since(start) if lg.timestamp < start + timedelta(days=1)]
    if logs:
        st.dataframe(pd.DataFrame([{"Giờ": f"{lg.timestamp:%H:%M:%S}", "Người": lg.member_name,
                                    "Độ tương đồng": round(lg.confidence or 0, 2), "Camera": lg.camera_id} for lg in logs]),
                     use_container_width=True, hide_index=True)
    else:
        st.caption("Không có lượt ra vào.")

# ---------- TAB 3: Đồ vật & Vùng
with tab_objects:
    st.subheader("Đồ vật")
    for o in db.all_objects():
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                show_image(o.image_path, width=110)
            with c2:
                st.markdown(f"**{o.object_name}** (`{o.prompt_keyword}`) {'' if o.is_active else '· ⏸️ ngừng theo dõi'}")
                st.caption(f"Vùng: {o.last_zone or '—'} · Lần cuối: "
                           f"{o.last_seen_at:%H:%M %d/%m}" if o.last_seen_at else "Chưa thấy lần nào")
            with c3:
                label = "⏸️ Ngừng" if o.is_active else "▶️ Theo dõi lại"
                if st.button(label, key=f"obj{o.id}"):
                    db.set_object_active(o.id, not o.is_active)
                    if bus:
                        bus.bump_objects_version()
                    st.rerun()
    with st.form("add_obj", clear_on_submit=True):
        c1, c2 = st.columns(2)
        vn = c1.text_input("Tên tiếng Việt", placeholder="Cốc nước")
        en = c2.text_input("Từ khóa tiếng Anh", placeholder="cup")
        if st.form_submit_button("➕ Thêm đồ vật"):
            if vn.strip() and en.strip().isascii() and en.strip():
                db.add_object(vn.strip(), en.strip())
                if bus:
                    bus.bump_objects_version()
                st.success("Đã thêm — worker_object nhận ở chu kỳ kế tiếp.")
                st.rerun()
            else:
                st.error("Cần tên tiếng Việt và từ khóa tiếng Anh không dấu.")
    st.subheader("Vùng")
    zones = db.list_zones(cam)
    st.caption(", ".join(f"{z.zone_name} ({z.zone_type})" for z in zones) or "Chưa có vùng — vẽ bằng scripts/draw_zones.py")
    prev = data_dir() / "zones_preview.jpg"
    if prev.exists():
        st.image(str(prev), caption="Ảnh tô vùng", width=640)

# ---------- TAB 4: Trò chuyện
with tab_chat:
    hist = st.session_state.setdefault("chat", [])
    for role, text, imgs in hist:
        with st.chat_message(role):
            st.write(text)
            for rel in imgs:
                show_image(rel, width=240)

    def ask(payload=None, files=None):
        try:
            if files:
                r = requests.post(f"{api}/voice", files=files, timeout=120)
            else:
                r = requests.post(f"{api}/chat", json=payload, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            return {"answer": f"Không gọi được trợ lý: {e}", "images": []}

    if q := st.chat_input("Hỏi trợ lý, vd. 'Chìa khóa của tôi đâu?'"):
        hist.append(("user", q, []))
        res = ask({"message": q})
        hist.append(("assistant", res.get("answer", ""), res.get("images", [])))
        st.rerun()
    audio = st.audio_input("🎙️ Hoặc ghi âm câu hỏi")
    if audio is not None and st.button("Gửi ghi âm"):
        res = ask(files={"file": ("voice.wav", audio.getvalue(), "audio/wav")})
        hist.append(("user", f"🎙️ {res.get('transcript', '(ghi âm)')}", []))
        hist.append(("assistant", res.get("answer", res.get("detail", "")), res.get("images", [])))
        st.rerun()
