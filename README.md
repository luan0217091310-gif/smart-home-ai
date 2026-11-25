# smart-home-ai — Camera AI Thông Minh

Biến một camera thường thành "người trông nhà" có AI: **nhận ra người nhà và báo người lạ**, **nhớ chỗ để đồ** ("Chìa khóa của tôi đâu?"), **phát hiện té ngã**, và **trả lời câu hỏi bằng tiếng Việt** qua Telegram hoặc Dashboard. Toàn bộ xử lý hình ảnh chạy trên máy trong nhà.

- Đặc tả đầy đủ: [docs/SPEC.md](docs/SPEC.md) · Biên bản nghiệm thu: [docs/acceptance/](docs/acceptance/)

## Bắt đầu nhanh (Windows, máy hiện tại)

```powershell
cd D:\Camera-AI
powershell -ExecutionPolicy Bypass -File start.ps1          # bật toàn bộ (Docker + đọc webcam)
powershell -ExecutionPolicy Bypass -File start.ps1 -Stop    # tắt
```

- Dashboard: http://localhost:8501 (mật khẩu trong `.env` → `DASHBOARD_PASSWORD`)
- Ảnh nhà hiện tại: http://localhost:8000/snapshot
- Cảnh báo người lạ / té ngã / mất camera tự gửi vào Telegram.
- Hỏi trợ lý: tab 💬 Trò chuyện, ví dụ "Nãy giờ có ai vào nhà không?", "Điện thoại của tôi đâu?", "Chụp ảnh nhà hiện tại".
- Thêm khuôn mặt: tab 👪 Thành viên, hoặc bỏ ảnh vào `data/faces/<tên>/` rồi
  `docker compose run --rm worker_face python scripts/enroll_faces.py`
  (**không** chạy script đụng CSDL trực tiếp trên Windows khi hệ thống đang chạy — xem "Lỗi thường gặp").

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

## Nâng cấp sau này

### A. Thay webcam bằng camera IP (Tapo, Imou, Ezviz, Hikvision…)

Không sửa code — chỉ sửa `.env`. Điều kiện: camera **hỗ trợ RTSP/ONVIF**.

| Hãng | Dùng được | Ghi chú |
| --- | --- | --- |
| TP-Link Tapo (C200, C210, C220, C310…) | ✅ dễ nhất | App Tapo → Cài đặt nâng cao → Tài khoản camera; link `rtsp://user:pass@IP:554/stream1` (nét) hoặc `/stream2` (nhẹ) |
| Imou | ✅ phần lớn | `rtsp://admin:<mã an toàn>@IP:554/cam/realmonitor?channel=1&subtype=1` |
| Ezviz | ✅ | Mật khẩu RTSP = mã xác minh dưới đáy camera; `rtsp://admin:<mã>@IP:554/H.264` |
| Hikvision / Dahua / KBVision | ✅ rất tốt | Camera an ninh chuyên dụng |
| Xiaomi / Mi Home | ⚠️ đa số không | Thường không có RTSP |
| Camera dùng pin (mọi hãng) | ❌ | Hầu hết không có RTSP |

Trước khi mua: tìm "<tên model> RTSP".

Các bước:
1. Cài camera bằng app hãng, bật RTSP, tạo tài khoản RTSP riêng; đặt IP cố định cho camera trong router.
2. Mở link bằng VLC (Media → Open Network Stream) — thấy hình mới làm tiếp.
3. Sửa `.env`:
   ```
   CAMERA_ID=cam_phongkhach
   CAMERA_SOURCE=rtsp://user:matkhau@192.168.1.50:554/stream2
   ```
4. Camera IP không cần chạy producer trên Windows: bật luôn trong Docker  
   `docker compose up -d` (gồm cả `stream_producer`) và **không** chạy `start.ps1` phần webcam.
5. Chụp ảnh tĩnh mới `python scripts/view_stream.py --snapshot`, vẽ lại vùng `python scripts/draw_zones.py`.
6. Lấy mẫu mặt từ camera mới:  
   `docker compose run --rm worker_face python scripts/capture_faces.py --name "<Tên>" --role owner`
7. Kiểm tra lại ngưỡng mặt (ngày + đêm) từ `data/face_scores.csv`, thử vài cảnh ngã, chạy thử 72 giờ — mẫu biên bản ở `docs/acceptance/phase-7.md`.

Mẹo: thử luồng nhẹ (`stream2`) trước; nếu mặt ở xa nhỏ hơn 60 px thì đổi sang `stream1`. Camera giới hạn số người xem cùng lúc — tắt bớt app điện thoại nếu mất hình.

### B. Nhiều camera

Hiện chạy **1 camera** (phạm vi bản test). Mọi khung hình, bảng CSDL và khóa Redis đã có `camera_id`, nên mở rộng chỉ cần: một `stream_producer` cho mỗi camera và cho các worker đọc danh sách camera. Việc này chưa làm. GPU 4 GB chịu được khoảng 1–2 camera; nhiều hơn cần GPU mạnh hơn hoặc giảm FPS mỗi camera.

### C. Hỏi trợ lý ngay trong Telegram

Bot Telegram có sẵn đang nhận tin bằng long polling, nên hệ thống camera chỉ **gửi cảnh báo** qua bot đó (`TELEGRAM_BOT_ENABLED=false`). Để hỏi đáp/`/chup`/tin nhắn thoại trong Telegram:
1. Tạo bot mới: nhắn `/newbot` cho @BotFather.
2. Trong `.env`: `TELEGRAM_BOT_TOKEN=<token mới>`, `TELEGRAM_BOT_ENABLED=true`.
3. `docker compose up -d --force-recreate assistant_api`.

### D. Khác

- Giọng nói: `VOICE_ENABLED=true`, chọn `TTS_VOICE`.
- Riêng tư hoàn toàn: `LLM_PROVIDER=ollama` (cần GPU nhiều VRAM hơn).
- Đồ vật: thêm/ngừng trong tab Đồ vật hoặc nhắn trợ lý "theo dõi thêm cái …" — không cần train lại.
- Ngưỡng té ngã: quay video vào `data/test_videos/fall/` và `normal/`, chạy `docker compose run --rm worker_fall python scripts/eval_fall_videos.py`, sửa `fall.drop_speed_threshold` trong `config/settings.yaml`.

## Lỗi thường gặp

- **Mất dữ liệu / `unable to open database file`**: trên Windows + Docker Desktop, SQLite không được mở cùng lúc từ Windows và từ container. Script đụng CSDL phải chạy trong container (`docker compose run --rm worker_face python scripts/...`). Nếu đã lỡ: `docker compose stop` rồi `docker compose up -d`.
- **Hình trên Dashboard đứng yên**: chương trình đọc webcam đã tắt → chạy lại `start.ps1`.

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
