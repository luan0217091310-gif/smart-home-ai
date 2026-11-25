# Biên bản nghiệm thu GĐ 6 — Dashboard và đóng gói

Ngày: 25/11/2026

## Đã làm

- `services/dashboard` (Streamlit, cổng 8501, mật khẩu so sánh an toàn `hmac.compare_digest`; trống mật khẩu = khóa):
  - **Live & Cảnh báo**: ảnh mới nhất từ Redis (tự làm mới 2 s, hiện độ trễ), đèn trạng thái 5 service + Redis (heartbeat), danh sách cảnh báo lọc theo ngày/loại, nút **Đã xem** / **Báo giả**; **âm báo trên trình duyệt** khi có té ngã mới.
  - **Thành viên**: danh sách, tải ảnh lên để thêm (bắt buộc tick "đã đồng ý"), worker_face tự đăng ký qua hàng đợi Redis — không cần chạy lệnh; xóa thành viên (xóa vector + thư mục ảnh); lịch sử ra vào theo ngày.
  - **Đồ vật & Vùng**: bảng đồ vật (vùng, lần cuối, ảnh), thêm / ngừng / theo dõi lại (tăng `objects:version`), ảnh tô vùng.
  - **Trò chuyện**: khung chat gọi `/chat`, ghi âm gửi `/voice`.
- `docker-compose.yml` hoàn chỉnh: 8 service, health check từng service, `depends_on` Redis khỏe, GPU cho 3 worker, gắn `data/` `models/` `config/`, `restart: unless-stopped`, log 3 × 10 MB.
- `scripts/maintenance.py` + service `maintenance`: 02:00 mỗi đêm xóa ảnh > 30 ngày, `access_logs` > 90 ngày; Chủ nhật sao lưu `smarthome.db` (API backup an toàn với WAL), `zones.json`, `faces/` vào `backups/`.
- README đầy đủ (phần cứng, cài từng bước, Windows/Linux, bảng biến `.env`, lệnh, lỗi thường gặp, giới hạn).

## Kết quả chạy thật trên máy test

| Mục | Kết quả |
| --- | --- |
| `docker compose up -d` (redis, worker_face, assistant_api, dashboard, maintenance) | Tất cả **healthy** trong < 1 phút |
| worker_face trong Docker | Dùng GPU (531 MiB VRAM) |
| Dashboard `/_stcore/health` | 200 |
| pytest Dashboard (AppTest) | Sai mật khẩu → không vào; đúng → 4 tab; "Báo giả" → `false_alarm` trong CSDL |
| pytest toàn bộ | xem commit |

## Nghiệm thu — cần chủ dự án

- [ ] **[CUNG CẤP]** Đặt `DASHBOARD_PASSWORD` thật trong `.env` (hiện máy test đang dùng mật khẩu demo `demo123` — **đổi ngay**).
- [ ] Thêm thành viên qua trình duyệt → được nhận ra mà không chạy lệnh.
- [ ] Khởi động lại máy → hệ thống tự chạy lại (Docker Desktop: bật "Start Docker Desktop when you sign in"; producer trên Windows: tạo Task Scheduler chạy `services\stream_producer\main.py` lúc đăng nhập).
- [ ] Thử cài từ đầu theo README ở thư mục mới.
- [ ] Ảnh chụp 4 tab đưa vào biên bản.
