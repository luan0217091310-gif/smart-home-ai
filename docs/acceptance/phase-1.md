# Biên bản nghiệm thu GĐ 1 — Khung xương hệ thống và luồng video

Ngày: 25/11/2026

## Đã làm

- `docker-compose.yml`: `redis:7-alpine` (không lưu đĩa, `maxmemory 256mb`), mạng chung, `./data` → `/app/data`, `restart: unless-stopped`, health check, giới hạn log 3×10 MB.
- `shared/config.py` (đọc `.env` + `settings.yaml`, báo rõ biến thiếu), `shared/database.py` (5 bảng, WAL, `busy_timeout=5000`), `shared/frame_bus.py` (`publish`, `get_latest`, heartbeat, `objects:version`), `shared/zones.py`, `shared/notifier.py`.
- `services/stream_producer`: webcam / RTSP (ép TCP) / file video (phát lặp); luồng đọc riêng chỉ giữ khung mới nhất; thu nhỏ theo `STREAM_WIDTH`; backoff 1, 2, 4… ≤ 30 s; mất > 5 phút → cảnh báo `system`.
- `scripts/view_stream.py` (`--snapshot`, `--headless --seconds N`).
- `tests/test_core.py`: 9 bài pytest (frame bus, bỏ khung trùng, WAL, CRUD 5 bảng, cooldown, backoff, theo dõi mất kết nối, vùng nhỏ nhất).

## Kết quả đo

| Chỉ số | Kết quả |
| --- | --- |
| pytest | 9/9 đạt |
| FPS thực (webcam, STREAM_FPS=15) | 14,9 |
| Độ trễ trong hệ thống (now − ts) | TB 24–28 ms, p95 ≈ 46 ms (**< 200 ms ✅**) |
| Producer trong Docker (nguồn file video) | Chạy được, nối Redis qua mạng compose |
| Backoff khi không mở được nguồn | 1 → 2 → 4 → 8 → 16 s (đã thấy trong log) |

## Nghiệm thu

- [ ] Chạy 30 phút, RAM phút 30 ≤ phút 5 + 10% — **chủ dự án chạy** (lệnh dưới).
- [x] Độ trễ trong hệ thống < 200 ms. Độ trễ đầu–cuối: **chủ dự án đo** bằng cách quay webcam vào đồng hồ bấm giờ.
- [ ] Rút webcam 1 phút rồi cắm lại → tự nối lại — **chủ dự án thử** (webcam laptop tích hợp không rút được; có thể thử bằng cách tắt camera trong Device Manager).
- [ ] Dừng container producer → Docker tự bật lại (`docker kill smart-home-ai-stream_producer-1`) — trên Windows producer chạy ngoài Docker; kiểm tra với `redis`.
- [x] `smarthome.db` có đủ 5 bảng (kiểm bằng pytest `test_database_tables`).

## Lệnh để chủ dự án tự chạy

```powershell
docker compose up -d redis
.venv\Scripts\python services\stream_producer\main.py      # cửa sổ 1
.venv\Scripts\python scripts\view_stream.py                 # cửa sổ 2, xem hình + độ trễ
```
