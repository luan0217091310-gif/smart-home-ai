# smart-home-ai — Camera AI Thông Minh

Biến một camera thường thành "người trông nhà" có AI: **nhận ra người nhà và báo người lạ**, **nhớ chỗ để đồ** ("Chìa khóa của tôi đâu?"), **phát hiện té ngã**, và **trả lời câu hỏi bằng tiếng Việt** qua Telegram hoặc Dashboard. Toàn bộ xử lý hình ảnh chạy trên máy trong nhà.

- Đặc tả đầy đủ: [docs/SPEC.md](docs/SPEC.md) · Biên bản nghiệm thu: [docs/acceptance/](docs/acceptance/)

## Kiến trúc

```
camera (webcam / RTSP / file) ─► stream_producer ─► Redis (frame:{cam}:latest, chỉ khung mới nhất)
                                                        │
                    ┌───────────────┬───────────────────┼─────────────────┐
                worker_face    worker_object        worker_fall        dashboard (Streamlit :8501)
               (InsightFace)   (YOLOE-26)         (YOLO26-pose)            │
                    └───────────────┴──────► SQLite (WAL) ◄───── assistant_api (FastAPI :8000)
                    cảnh báo ─► shared/notifier.py ─► Telegram ◄─► bot long polling (Gemini/Ollama)
```

Mỗi worker đọc khung mới nhất ở tốc độ riêng; worker chậm chỉ bỏ khung cũ, không làm chậm camera hay worker khác.

## Yêu cầu phần cứng

- PC/laptop có GPU NVIDIA (đã thử: T1200 4 GB VRAM). RAM ≥ 16 GB, ổ trống ≥ 30 GB (image Docker + mô hình).
- Webcam USB (Chặng A) hoặc camera IP có RTSP (Chặng B).
- Docker + NVIDIA Container Toolkit (Linux) hoặc Docker Desktop + WSL2 (Windows). Python 3.11.

## Cài đặt từng bước

```bash
git clone https://github.com/luan0217091310-gif/smart-home-ai.git
cd smart-home-ai
cp .env.example .env            # rồi điền các giá trị (xem bảng dưới)
docker compose build            # lần đầu mất 15–30 phút (PyTorch, InsightFace)
docker compose up -d
```

Mở Dashboard: `http://<IP-máy-chủ>:8501` (mật khẩu = `DASHBOARD_PASSWORD`).

### Windows (webcam USB)

Docker Desktop không cho container đọc webcam USB, nên chạy `stream_producer` bằng Python trên Windows, các service còn lại trong Docker:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
# trong .env dùng giá trị "chạy ngoài Docker": REDIS_URL=redis://localhost:6379/0, DATABASE_URL=sqlite:///data/smarthome.db, DATA_DIR=data
docker compose up -d redis worker_face worker_object worker_fall assistant_api dashboard maintenance
.venv\Scripts\python services\stream_producer\main.py
```

Các container đã được ép dùng đường dẫn và Redis bên trong Docker (khối `environment` trong `docker-compose.yml`), nên một file `.env` dùng được cho cả hai phía.

> Nếu Windows báo *"An Application Control policy has blocked this file"* khi nạp PyTorch/SQLAlchemy trong venv: đó là Smart App Control. Các worker YOLO chạy trong Docker nên không bị ảnh hưởng; SQLAlchemy đã ghim bản 2.0.x tự chuyển sang chế độ thuần Python.

### Linux

Bỏ comment dòng `devices: ["/dev/video0:/dev/video0"]` của `stream_producer` trong `docker-compose.yml`, rồi `docker compose up -d`.

## Biến `.env`

| Biến | Ý nghĩa |
| --- | --- |
| `CAMERA_ID` | Tên camera, gắn vào mọi khung hình và bản ghi (vd. `cam_test`, `cam_phongkhach`) |
| `CAMERA_SOURCE` | `0` = webcam; `rtsp://user:pass@IP:554/stream1` = camera IP; `data/test_videos/x.mp4` = file video (phát lặp) |
| `STREAM_FPS`, `STREAM_WIDTH`, `JPEG_QUALITY` | Tốc độ, độ rộng ảnh và chất lượng JPEG ghi vào Redis |
| `REDIS_URL`, `DATABASE_URL`, `DATA_DIR` | Hạ tầng; trong Docker được ghi đè tự động |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Bot gửi cảnh báo; chat nhận cảnh báo (có thể là ID nhóm gia đình) |
| `TELEGRAM_ALLOWED_CHAT_IDS` | Các chat_id được phép hỏi trợ lý (phân cách dấu phẩy); trống = chỉ `TELEGRAM_CHAT_ID` |
| `LLM_PROVIDER` | `gemini` \| `ollama` \| `rules` (offline, không cần khóa — để demo) |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Khóa và tên model Gemini |
| `OLLAMA_URL`, `OLLAMA_MODEL` | Phương án riêng tư chạy trên máy |
| `FACE_MODEL`, `OBJECT_MODEL`, `POSE_MODEL` | Mô hình AI (đổi không cần sửa code) |
| `VOICE_ENABLED`, `WHISPER_MODEL`, `TTS_VOICE` | Giọng nói: bật/tắt, model Whisper, giọng `vi-VN-HoaiMyNeural` (nữ) / `vi-VN-NamMinhNeural` (nam) |
| `DASHBOARD_PASSWORD` | Mật khẩu Dashboard (bắt buộc, trống = khóa) |

Ngưỡng (nhận mặt, cooldown, té ngã…) nằm trong `config/settings.yaml`.

## Sử dụng

| Việc | Cách làm |
| --- | --- |
| Kiểm tra Telegram | `python scripts/test_telegram.py` |
| Kiểm tra camera / LLM | `python scripts/check_camera.py` · `python scripts/check_llm.py` |
| Xem hình + đo độ trễ | `python scripts/view_stream.py` (`--snapshot` lưu ảnh tĩnh) |
| Đăng ký khuôn mặt | Bỏ 5–10 ảnh vào `data/faces/<ten>/` rồi `python scripts/enroll_faces.py` — hoặc tải ảnh lên tab **Thành viên** |
| Chụp mặt từ camera | `python scripts/capture_faces.py --name Bo` (cần worker_face trong Docker: `docker compose run --rm worker_face python scripts/capture_faces.py --name Bo`) |
| Vẽ vùng | `python scripts/draw_zones.py` (cần `pip install opencv-python`) |
| Thử bộ video té ngã | `docker compose run --rm worker_fall python scripts/eval_fall_videos.py` |
| Bộ câu hỏi trợ lý | `python scripts/eval_assistant.py [--provider rules]` |
| Dọn dữ liệu + sao lưu ngay | `python scripts/maintenance.py --once` (service `maintenance` tự chạy 02:00 mỗi đêm, sao lưu Chủ nhật vào `backups/`) |
| Kiểm thử | `python -m pytest -q` |

## Lỗi thường gặp

- **Không có hình**: `python scripts/check_camera.py`; với RTSP thử mở bằng VLC trước; camera có thể giới hạn số luồng xem cùng lúc.
- **`database is locked`**: đã bật WAL + `busy_timeout`; đừng mở file DB bằng công cụ ghi khi hệ thống đang chạy.
- **Hết VRAM (4 GB)**: đặt `OBJECT_DEVICE=cpu` cho worker_object (chỉ quét 4 s/lần), Whisper mặc định chạy CPU.
- **Trợ lý trả lời "đang gặp sự cố"**: kiểm tra `GEMINI_API_KEY`, `GEMINI_MODEL` còn tồn tại; tạm dùng `LLM_PROVIDER=rules`.
- **Lần đầu chạy worker YOLO chậm**: mô hình và bộ mã hóa chữ (~254 MB) tải vào `models/`, các lần sau không tải lại.

## Giới hạn đã biết

- **Chưa chống giả mạo khuôn mặt**: giơ ảnh của thành viên sẽ được nhận là thành viên đó. Không dùng hệ thống để mở khóa cửa.
- Người **quỵ xuống từ từ** (trượt theo tường) có thể không qua lớp "vận tốc rơi" của bộ phát hiện té ngã.
- Vật nhỏ ở xa (chìa khóa) khó nhận; ban đêm camera hồng ngoại làm nhận mặt kém hơn.
- edge-tts là dịch vụ không chính thức, có thể ngừng; khi lỗi trợ lý vẫn trả lời bằng chữ.

## Quyền riêng tư và giấy phép

- Ảnh khuôn mặt, ảnh chụp, CSDL và `.env` **không bao giờ** được đưa lên GitHub (`.gitignore`).
- Chỉ ảnh cảnh báo (Telegram) và chữ câu hỏi/kết quả công cụ (Gemini, edge-tts) rời khỏi nhà. Dùng Ollama nếu không muốn gửi gì ra ngoài.
- Hỏi ý kiến từng thành viên trước khi đăng ký khuôn mặt (Luật BVDLCN 91/2025/QH15). Không quay ra đường/nhà hàng xóm.
- Mô hình InsightFace `buffalo_l`: chỉ phi thương mại. Ultralytics YOLO: AGPL-3.0. Xem mục 9 của đặc tả.
