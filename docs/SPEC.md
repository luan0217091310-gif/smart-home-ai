# Camera AI Thông Minh — Đặc tả & Lộ trình Dự án

Nov 25, 2026 · @Luân Phùng · Phiên bản v1.1 (dựa trên bản nháp v1.0)

## 1. Cách đọc tài liệu này

Đây là bản đặc tả để bất kỳ ai, người hay AI coding agent, đọc xong là hiểu ý tưởng và làm được dự án. Lộ trình đi từ bản test trên máy tính đến camera thật trong gia đình.

Tài liệu có hai vai trò:

- **Chủ dự án**: bạn, người đặt yêu cầu, cung cấp dữ liệu và duyệt kết quả.
- **Người thực hiện**: bạn, người làm cùng hoặc AI coding agent viết code theo tài liệu này.

| Ký hiệu | Ý nghĩa | Ai làm |
| --- | --- | --- |
| **\[CUNG CẤP\]** | Thông tin hoặc dữ liệu chủ dự án phải đưa trước khi bắt đầu bước đó | Chủ dự án |
| **\[DUYỆT\]** | Điểm dừng: chủ dự án xem kết quả, đồng ý thì mới làm tiếp | Chủ dự án |
| **\[NGHIỆM THU\]** | Bài kiểm tra cụ thể, đạt hết mới coi là xong giai đoạn | Hai bên cùng chạy |
| **\[LƯU Ý\]** | Rủi ro hoặc điểm dễ làm sai | Người thực hiện |
| **\[ĐỀ XUẤT\]** | Con số hoặc lựa chọn mặc định, chủ dự án có thể đổi | Chủ dự án quyết |

Mỗi giai đoạn trình bày theo cùng một khuôn: Mục tiêu → Cần cung cấp → Các bước → Bàn giao → Nghiệm thu → Duyệt.

Quy tắc: không bắt đầu giai đoạn sau khi giai đoạn trước chưa được duyệt. Mỗi giai đoạn kết thúc bằng một Pull Request trên GitHub để dễ xem lại.

## 2. Tóm tắt dự án và phạm vi

Dự án biến một camera thường thành "người trông nhà" có AI. Hệ thống nhận ra người nhà, báo người lạ, nhớ chỗ để đồ, phát hiện té ngã và trả lời câu hỏi bằng tiếng Việt.

Tên repo đề xuất: `smart-home-ai`. Toàn bộ xử lý hình ảnh chạy trên máy của bạn, không gửi video lên máy chủ ngoài.

### 2.1. Bốn nhóm tính năng cốt lõi

| # | Tính năng | Câu hỏi nó trả lời | Giai đoạn |
| --- | --- | --- | --- |
| 1 | Nhận diện người nhà, cảnh báo người lạ | "Ai vừa vào nhà? Có người lạ không?" | GĐ 2 |
| 2 | Ghi nhớ vị trí đồ vật theo vùng | "Chìa khóa của tôi đâu rồi?" | GĐ 3 |
| 3 | Phát hiện té ngã | "Có ai ngã mà không dậy được không?" | GĐ 4 |
| 4 | Trợ lý ảo chat và giọng nói | Hỏi đáp tất cả điều trên bằng tiếng Việt | GĐ 5 |

GĐ 6 bổ sung giao diện quản lý (Dashboard) và đóng gói chạy bằng một lệnh.

### 2.2. Hai chặng triển khai

1. **Chặng A — Bản test trên máy tính (GĐ 0 đến GĐ 6).** Một PC hoặc laptop có GPU NVIDIA, nguồn video là webcam USB. Mục đích: chứng minh cả 4 tính năng chạy đúng và ổn định trong môi trường dễ kiểm soát.
2. **Chặng B — Triển khai lên camera gia đình (GĐ 7).** Giữ nguyên code, chỉ đổi nguồn video sang luồng RTSP của camera IP trong nhà. Sau đó vẽ lại vùng, hiệu chỉnh ngưỡng, chạy thử liên tục 72 giờ.

Code phải được viết để chuyển từ Chặng A sang Chặng B chỉ bằng cách sửa file `.env`, không sửa code.

### 2.3. Trong phạm vi bản test

- 1 camera, 1 máy chủ xử lý, chạy trong mạng nội bộ gia đình.
- 2 đến 3 thành viên đăng ký khuôn mặt, 3 đến 5 đồ vật theo dõi, tối thiểu 3 vùng trong phòng.
- Cảnh báo qua Telegram, trả lời bằng tiếng Việt.
- Dashboard chạy trên trình duyệt trong mạng nhà.

### 2.4. Ngoài phạm vi bản test

- Nhiều camera cùng lúc, ứng dụng di động riêng.
- Chống giả mạo khuôn mặt bằng ảnh hoặc video (liveness).
- Ghi hình liên tục 24/7 như đầu ghi NVR.
- Mở cổng truy cập từ Internet vào Dashboard.
- Điều khiển thiết bị nhà thông minh, chạy trên Jetson. Các mục này nằm ở Phụ lục, hướng mở rộng.

### 2.5. Định nghĩa "xong dự án"

**\[ĐỀ XUẤT\] \[DUYỆT\]** Dự án xong khi đạt cả ba điều kiện:

- Tất cả mục nghiệm thu từ GĐ 0 đến GĐ 7 đều đạt.
- Hệ thống chạy 72 giờ liên tục trên camera gia đình mà không service nào dừng hẳn.
- Trong 72 giờ đó, báo giả người lạ không quá 2 lần mỗi ngày và không có báo giả té ngã.

## 3. Kiến trúc hệ thống và công nghệ

Hệ thống đọc camera đúng một lần rồi phát hình qua Redis, để mỗi tính năng AI chạy thành một service riêng ở tốc độ riêng (kiến trúc Producer–Consumer). Một service lỗi không kéo các service khác dừng theo. Thêm tính năng mới chỉ là thêm một service.

&#91;embedded content: kiến trúc hệ thống · 6 service quanh Redis\]

Worker nào chậm cũng chỉ bỏ qua khung cũ, không làm chậm camera hay worker khác. Cảnh báo đi thẳng tới Telegram, còn câu hỏi của bạn đi qua `assistant_api`.

### 3.1. Vai trò từng service

| Service | Làm gì | Đọc từ | Ghi vào | Tốc độ xử lý |
| --- | --- | --- | --- | --- |
| `stream_producer` | Đọc webcam hoặc RTSP, tự kết nối lại khi rớt, nén JPEG | Camera | Redis | 15–20 FPS |
| `worker_face` | Phát hiện và nhận diện khuôn mặt | Redis | CSDL, Telegram | 2–3 FPS |
| `worker_object` | Tìm đồ vật theo từ khóa, xác định vùng | Redis, CSDL | CSDL | 1 lần mỗi 3–5 giây |
| `worker_fall` | Ước lượng tư thế, phát hiện té ngã | Redis | CSDL, Telegram | 10–15 FPS |
| `assistant_api` | Chat và voice, LLM gọi công cụ tra CSDL, nhận tin Telegram | CSDL | CSDL | Khi có yêu cầu |
| `dashboard` | Giao diện web quản lý | CSDL, Redis, API | Qua API | Khi có yêu cầu |
| `redis` | Bộ đệm hình ảnh trong RAM | — | — | — |

### 3.2. Nguyên tắc thiết kế bắt buộc

1. Mọi cấu hình (nguồn camera, ngưỡng, FPS, khóa API) nằm trong `.env` hoặc `config/settings.yaml`, không viết cứng trong code.
2. Worker luôn lấy khung hình mới nhất và bỏ qua khung cũ. Worker chậm không được làm đầy bộ nhớ.
3. Mỗi khung hình mang `camera_id`, `frame_id` và thời điểm chụp ngay từ đầu. Sau này thêm camera không phải sửa code.
4. Mọi service ghi log ra màn hình cùng một định dạng, có mức INFO, WARNING, ERROR.
5. Docker tự khởi động lại service khi nó dừng (`restart: unless-stopped`), mỗi service có health check.
6. Mọi thời gian lưu theo múi giờ `Asia/Ho_Chi_Minh`.
7. Mọi cảnh báo đi qua một module chung (`shared/notifier.py`), nơi duy nhất xử lý chống spam (cooldown).
8. Mô hình AI được bọc sau một lớp chung (ví dụ `ObjectDetector`). Đổi mô hình chỉ cần đổi biến trong `.env`.

### 3.3. Công nghệ sử dụng

| Thành phần | Công nghệ đề xuất | Ghi chú |
| --- | --- | --- |
| Ngôn ngữ | Python 3.11 (tối thiểu 3.10) | Ghim phiên bản thư viện trong `requirements.txt` |
| Đóng gói | Docker, Docker Compose, NVIDIA Container Toolkit | Windows có hạn chế webcam, xem mục 8 |
| Phân phối hình | OpenCV + Redis 7 |  |
| Khuôn mặt | InsightFace `buffalo_l` trên onnxruntime-gpu, vector 512 chiều | Mô hình chỉ cho mục đích phi thương mại, xem mục 9 |
| Đồ vật | YOLOE-26 (`yoloe-26s-seg.pt`), dự phòng YOLO-World (`yolov8s-worldv2.pt`) | Đổi danh sách đồ vật bằng `set_classes()`, không train lại |
| Tư thế, té ngã | YOLO26-pose (`yolo26n-pose.pt`) | Thay `yolov8n-pose` của bản nháp, cùng thư viện Ultralytics ≥ 8.4.0 |
| Nghe (STT) | faster-whisper, model `small`, ngôn ngữ `vi` | Tùy chọn bật/tắt |
| Nói (TTS) | edge-tts, giọng `vi-VN-HoaiMyNeural` hoặc `vi-VN-NamMinhNeural` | Dịch vụ không chính thức, có thể ngừng bất cứ lúc nào |
| Trò chuyện | Gemini API (function calling), tên model đặt trong `.env` | Phương án riêng tư: Ollama chạy trên máy |
| Cơ sở dữ liệu | SQLite chế độ WAL → PostgreSQL khi mở rộng | Dùng SQLAlchemy để đổi dễ |
| API | FastAPI |  |
| Cảnh báo | Telegram Bot API | Có thể tái sử dụng bot Telegram bạn đã làm |
| Giao diện | Streamlit (bản test) → React/Next.js (bản chính thức) |  |

**\[ĐỀ XUẤT\] \[DUYỆT\]** Bản nháp dùng YOLOv8. Ultralytics ra mắt YOLO26 vào tháng 1/2026, kèm YOLOE-26 nhận diện đồ vật theo từ khóa ([thông báo](https://community.ultralytics.com/t/new-release-ultralytics-v8-4-0/1747), [tài liệu YOLOE](https://docs.ultralytics.com/models/yoloe)). Đề xuất dùng bản mới, giữ YOLO-World làm dự phòng vì cách gọi gần như giống nhau.

**\[ĐỀ XUẤT\] \[DUYỆT\]** Model Gemini: bắt đầu với bản Flash-Lite cho nhanh và rẻ, nếu gọi công cụ sai nhiều thì đổi sang Flash. Danh sách hiện tại có `gemini-3.5-flash-lite` và `gemini-3.8-flash` ([danh sách model](https://ai.google.dev/gemini-api/docs/models)); kiểm tra lại lúc bắt đầu code.

## 4. Cấu trúc repo GitHub và quy ước làm việc

Repo đặt chế độ Private. Ảnh khuôn mặt, ảnh chụp, file CSDL và file `.env` tuyệt đối không được đưa lên GitHub.

### 4.1. Cây thư mục

```text
smart-home-ai/
├── README.md                  # Giới thiệu, cách cài, cách chạy
├── docker-compose.yml         # Chạy toàn bộ service bằng 1 lệnh
├── .env.example               # Mẫu cấu hình, KHÔNG chứa mật khẩu thật
├── .gitignore
├── config/
│   └── settings.yaml          # Ngưỡng, FPS, cooldown (không chứa bí mật)
├── data/                      # KHÔNG đưa lên GitHub (chỉ giữ .gitkeep)
│   ├── faces/<ten_thanh_vien>/ # 5–10 ảnh mỗi người
│   ├── snapshots/             # Ảnh người lạ, té ngã, đồ vật
│   ├── zones.json             # Tọa độ các vùng trong phòng
│   └── smarthome.db           # CSDL SQLite
├── shared/
│   ├── config.py              # Đọc .env + settings.yaml
│   ├── database.py            # Định nghĩa bảng, kết nối CSDL
│   ├── frame_bus.py           # Ghi/đọc khung hình qua Redis
│   ├── notifier.py            # Gửi Telegram + chống spam
│   └── zones.py               # Đọc zones.json, kiểm tra điểm thuộc vùng nào
├── services/
│   ├── stream_producer/       # mỗi service: main.py, Dockerfile, requirements.txt
│   ├── worker_face/
│   ├── worker_object/
│   ├── worker_fall/
│   ├── assistant_api/
│   └── dashboard/
├── scripts/
│   ├── enroll_faces.py        # Đăng ký khuôn mặt từ data/faces/
│   ├── draw_zones.py          # Vẽ vùng bằng chuột trên ảnh tĩnh
│   ├── test_telegram.py       # Gửi tin nhắn thử
│   └── view_stream.py         # Xem hình từ Redis, đo độ trễ
├── tests/                     # pytest cho logic thuần: cosine, vùng, té ngã
└── docs/
    ├── SPEC.md                # Tài liệu này, xuất ra Markdown
    └── acceptance/            # Biên bản nghiệm thu từng giai đoạn
```

So với bản nháp: `dashboard/` chuyển vào `services/`, thêm `config/`, `scripts/`, `tests/`, `docs/`.

### 4.2. File `.gitignore` bắt buộc

```text
.env
data/*
!data/.gitkeep
*.pt
*.onnx
models/
__pycache__/
.venv/
```

**\[LƯU Ý\]** Nếu lỡ đưa token lên GitHub, xóa commit là chưa đủ. Phải thu hồi token ngay: Telegram dùng lệnh `/revoke` với BotFather, Gemini thì xóa khóa cũ và tạo khóa mới.

### 4.3. Quy ước nhánh, commit và Pull Request

1. Nhánh `main` luôn chạy được. Mỗi giai đoạn làm trên nhánh riêng: `phase-0-setup`, `phase-1-core`, `phase-2-face`, `phase-3-object`, `phase-4-fall`, `phase-5-assistant`, `phase-6-dashboard`, `phase-7-home-camera`.
2. Commit theo chuẩn Conventional Commits, ví dụ `feat(face): thêm cooldown ghi log`, `fix(producer): tự kết nối lại RTSP`.
3. Cuối giai đoạn, mở Pull Request vào `main` kèm biên bản `docs/acceptance/phase-N.md`: kết quả từng tiêu chí, ảnh chụp màn hình, đoạn log.
4. Chủ dự án duyệt và merge PR, sau đó gắn tag `v0.N` (ví dụ `v0.2` sau GĐ 2).
5. Mỗi đầu việc trong tài liệu là một GitHub Issue. Mỗi giai đoạn là một Milestone.

**\[CUNG CẤP\]** Tài khoản GitHub, tên repo, chế độ Private hay Public, danh sách người được mời vào repo.

**\[DUYỆT\]** Mỗi Pull Request cuối giai đoạn.

## 5. Thiết kế dữ liệu và cấu hình

Năm bảng CSDL lưu toàn bộ trạng thái lâu dài. Redis chỉ giữ khung hình mới nhất và tín hiệu giữa các service, không lưu gì lâu dài.

### 5.1. Năm bảng cơ sở dữ liệu

| Bảng | Các cột | Ai ghi | Ai đọc |
| --- | --- | --- | --- |
| `members` | `id`, `name`, `role` (`owner`, `family`, `guest`), `embedding` (BLOB, 512 số float32), `num_images`, `created_at` | `enroll_faces.py`, dashboard | `worker_face` |
| `access_logs` | `id`, `camera_id`, `member_id` (rỗng nếu người lạ), `member_name` hoặc `Stranger`, `confidence`, `image_path`, `timestamp` | `worker_face` | `assistant_api`, dashboard |
| `tracked_objects` | `id`, `object_name` (tên tiếng Việt), `prompt_keyword` (từ khóa tiếng Anh), `last_zone`, `last_camera_id`, `last_confidence`, `last_seen_at`, `image_path`, `is_active`, `created_at` | `worker_object`, `assistant_api` | `worker_object`, `assistant_api` |
| `alerts` | `id`, `camera_id`, `alert_type` (`stranger`, `fall`, `system`), `message`, `image_path`, `timestamp`, `status` (`new`, `sent`, `acknowledged`, `false_alarm`) | Các worker | `assistant_api`, dashboard |
| `zones` | `id`, `camera_id`, `zone_name`, `zone_type` (`furniture`, `safe_rest`, `floor`, `door`), `polygon_coords` (JSON) | Đồng bộ từ `zones.json` | `worker_object`, `worker_fall` |

Thay đổi so với bản nháp: thêm `camera_id` ở mọi bảng để sau này có nhiều camera. Thêm trạng thái `false_alarm` để đánh dấu báo giả và đếm tỷ lệ báo giả ở GĐ 7.

Quy tắc SQLite: bật chế độ WAL, đặt `busy_timeout` 5000 ms, giao dịch ngắn. Nhiều container cùng ghi vào một file nên thiếu các cài đặt này sẽ gặp lỗi `database is locked`.

**\[DUYỆT\]** File `data/zones.json` là nguồn gốc vì dễ sửa tay. Khi khởi động, hệ thống đọc file và đồng bộ vào bảng `zones`. Bản nháp có cả hai nhưng chưa nói cái nào là chính.

### 5.2. Các khóa trong Redis

| Khóa | Nội dung | Ai ghi | Ghi chú |
| --- | --- | --- | --- |
| `frame:{camera_id}:latest` | Hash gồm `jpg`, `frame_id`, `ts` | `stream_producer` | Ghi đè mỗi khung, worker bỏ qua nếu `frame_id` trùng lần trước |
| `objects:version` | Số nguyên tăng dần | `assistant_api`, dashboard | `worker_object` thấy số đổi thì nạp lại danh sách đồ vật |
| `heartbeat:{service}` | Thời điểm gần nhất còn sống, hết hạn sau 30 giây | Mọi service | Dashboard hiển thị service nào đang chạy |

Redis chạy không lưu xuống đĩa, giới hạn 256 MB RAM. Worker té ngã tính vận tốc theo `ts` thật của khung hình, không theo số thứ tự khung, vì có thể bị bỏ sót khung.

### 5.3. Định dạng `zones.json`

```json
{
  "camera_id": "cam_test",
  "zones": [
    {"name": "Bàn làm việc", "type": "furniture", "polygon": [[0.10, 0.55], [0.45, 0.55], [0.45, 0.80], [0.10, 0.80]]},
    {"name": "Ghế sofa", "type": "safe_rest", "polygon": [[0.55, 0.50], [0.95, 0.50], [0.95, 0.85], [0.55, 0.85]]},
    {"name": "Sàn nhà", "type": "floor", "polygon": [[0.00, 0.60], [1.00, 0.60], [1.00, 1.00], [0.00, 1.00]]}
  ]
}
```

Tọa độ ghi theo tỷ lệ 0 đến 1 so với chiều rộng và cao của ảnh, không ghi theo pixel. Nhờ vậy đổi độ phân giải camera không phải vẽ lại vùng.

Khi một điểm nằm trong nhiều vùng, chọn vùng có diện tích nhỏ nhất. Ví dụ đồ vật trên bàn được tính là "Bàn làm việc" chứ không phải "Sàn nhà".

### 5.4. File `.env.example`

```text
# Camera
CAMERA_ID=cam_test
CAMERA_SOURCE=0            # 0 = webcam; hoặc rtsp://user:pass@192.168.1.50:554/stream1
STREAM_FPS=15
STREAM_WIDTH=1280
JPEG_QUALITY=80

# Hạ tầng
REDIS_URL=redis://redis:6379/0
DATABASE_URL=sqlite:////app/data/smarthome.db
TZ=Asia/Ho_Chi_Minh

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Trò chuyện
LLM_PROVIDER=gemini        # gemini | ollama
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=

# Mô hình AI
FACE_MODEL=buffalo_l
OBJECT_MODEL=yoloe-26s-seg.pt
POSE_MODEL=yolo26n-pose.pt

# Giọng nói
VOICE_ENABLED=false
WHISPER_MODEL=small
TTS_VOICE=vi-VN-HoaiMyNeural

# Dashboard
DASHBOARD_PASSWORD=
```

### 5.5. Ngưỡng trong `config/settings.yaml`

```yaml
face:
  fps: 3
  match_threshold: 0.55          # hiệu chỉnh lại ở GĐ 2 và GĐ 7
  stranger_consecutive_frames: 3
  member_log_cooldown_s: 120
  stranger_alert_cooldown_s: 60
  min_face_size_px: 60           # mặt quá nhỏ thì bỏ qua, không kết luận
object:
  interval_s: 4
  min_confidence: 0.25
fall:
  fps: 15
  drop_speed_threshold: null     # đo thật rồi điền ở GĐ 4
  lying_aspect_ratio: 1.2
  still_seconds: 4
  alert_cooldown_s: 60
```

**\[ĐỀ XUẤT\] \[DUYỆT\]** Các con số trên lấy từ bản nháp. Chúng là điểm xuất phát, sẽ được đo và chỉnh lại bằng dữ liệu thật trong từng giai đoạn.

## 6. Những gì chủ dự án cần cung cấp

Bảng dưới gom mọi mục **\[CUNG CẤP\]** của cả dự án, xếp theo giai đoạn cần dùng; riêng mục 18 nên có trước GĐ 2. Cột Trạng thái để bạn tự cập nhật.

| # | Cần cung cấp | Cần trước | Định dạng hoặc cách lấy | Trạng thái |
| --- | --- | --- | --- | --- |
| 1 | Thông tin máy test: tên GPU NVIDIA, dung lượng VRAM, RAM, hệ điều hành | GĐ 0 | Chạy `nvidia-smi`, chụp màn hình kết quả | Chưa có |
| 2 | Nguồn video cho Chặng A: webcam USB hay camera IP | GĐ 0 | Tên webcam, hoặc link RTSP đã xem được bằng VLC | Chưa có |
| 3 | Tài khoản GitHub, tên repo, Private hay Public | GĐ 0 | Tạo repo trống, mời người làm cùng | Chưa có |
| 4 | Telegram `BOT_TOKEN` và `CHAT_ID` | GĐ 0 | Dùng lại bot đã có hoặc tạo bot mới qua @BotFather | Chưa có |
| 5 | `GEMINI_API_KEY`, hoặc quyết định dùng Ollama | GĐ 0 | Tạo khóa trong Google AI Studio | Chưa có |
| 6 | Ảnh khuôn mặt 2–3 thành viên, mỗi người 5–10 ảnh, kèm tên hiển thị và vai trò | GĐ 2 | JPG, mỗi người một thư mục `data/faces/<ten>/`, mỗi ảnh chỉ một khuôn mặt | Chưa có |
| 7 | Ảnh tĩnh toàn cảnh từ đúng góc camera | GĐ 3 | Chụp bằng `scripts/view_stream.py --snapshot` | Chưa có |
| 8 | Danh sách vùng: tên và loại (đồ nội thất, chỗ nằm nghỉ, sàn, cửa) | GĐ 3 | Ví dụ: "Ghế sofa — chỗ nằm nghỉ" | Chưa có |
| 9 | 3–5 đồ vật cần theo dõi, kèm vật thật để thử | GĐ 3 | Tên tiếng Việt + từ khóa tiếng Anh, ví dụ "Chìa khóa — keys" | Chưa có |
| 10 | Người diễn thử té ngã và nệm hoặc thảm êm | GĐ 4 | Người khỏe, ngã có kiểm soát, không dùng người già | Chưa có |
| 11 | 5–10 câu hỏi mẫu muốn hỏi trợ lý | GĐ 5 | Viết đúng cách bạn hay nói hằng ngày | Chưa có |
| 12 | Bật giọng nói hay không, chọn giọng nam hay nữ | GĐ 5 | `vi-VN-HoaiMyNeural` (nữ) hoặc `vi-VN-NamMinhNeural` (nam) | Chưa có |
| 13 | Mật khẩu đăng nhập Dashboard | GĐ 6 | Điền thẳng vào `.env` | Chưa có |
| 14 | Thông tin camera gia đình: hãng, model, cắm điện hay dùng pin | GĐ 7 | Ảnh nhãn dán dưới đáy camera | Chưa có |
| 15 | Tài khoản RTSP của camera và link luồng đã xem được bằng VLC | GĐ 7 | Tạo trong ứng dụng của hãng camera, điền thẳng vào `.env` | Chưa có |
| 16 | Quyền quản trị router để đặt IP cố định cho camera và máy chủ | GĐ 7 | Mật khẩu trang quản trị router | Chưa có |
| 17 | Máy chạy 24/7 cho Chặng B: dùng lại PC test hay máy khác | GĐ 7 | Giống mục 1 | Chưa có |
| 18 | Sự đồng ý của các thành viên gia đình về camera nhận diện khuôn mặt | GĐ 2 | Xác nhận bằng lời hoặc tin nhắn, ghi lại ngày | Chưa có |

**\[LƯU Ý\]** Token, khóa API và mật khẩu RTSP điền thẳng vào file `.env` trên máy. Không dán vào Issue, Pull Request, tin nhắn hay prompt giao việc.

## GĐ 0 — Chuẩn bị môi trường và dữ liệu mẫu

**Mục tiêu.** Máy, phần mềm, tài khoản và dữ liệu đầu vào sẵn sàng, để các giai đoạn sau không bị kẹt vì lỗi môi trường.

**\[CUNG CẤP\]** Mục 1–5 ở bảng mục 6. Bắt đầu chuẩn bị luôn mục 6 (ảnh khuôn mặt) và mục 18 (sự đồng ý).

### Các bước

1. **Kiểm tra GPU.** Cài driver NVIDIA mới nhất, chạy `nvidia-smi`. Ghi lại tên GPU và dung lượng VRAM.
2. **Chọn hệ điều hành chạy hệ thống.**
   - Khuyến nghị Ubuntu 22.04 hoặc 24.04: Docker dùng được cả GPU lẫn webcam dễ nhất.
   - Nếu dùng Windows: Docker Desktop chạy được GPU qua WSL2 nhưng container không đọc được webcam USB. Khi đó chạy `stream_producer` bằng Python trực tiếp trên Windows, các service còn lại trong Docker, nối Redis qua `localhost:6379`.
3. **Cài Docker và NVIDIA Container Toolkit.** Kiểm tra bằng `docker run --rm --gpus all ubuntu nvidia-smi`; lệnh phải in ra đúng GPU.
4. **Cài công cụ.** Python 3.11, Git, VLC.
5. **Tạo repo.** Tạo repo trên GitHub, clone về máy, tạo cây thư mục rỗng theo mục 4.1, thêm `.gitignore` (mục 4.2), `.env.example` (mục 5.4) và `README.md`.
6. **Kiểm tra camera.** Webcam: mở bằng OpenCV và đọc được 1 khung hình. Camera IP: mở link RTSP bằng VLC (Media → Open Network Stream).
7. **Kiểm tra Telegram.** Viết `scripts/test_telegram.py`, gửi 1 tin nhắn chữ và 1 ảnh vào Telegram của bạn.
8. **Kiểm tra Gemini.** Gọi thử 1 câu hỏi tiếng Việt bằng đoạn code nhỏ, dùng khóa trong `.env`.
9. **Thu thập ảnh khuôn mặt.** Mỗi người 5–10 ảnh, theo hướng dẫn:
   - Góc thẳng, nghiêng trái, nghiêng phải, hơi ngẩng và hơi cúi.
   - Ánh sáng ban ngày và đèn buổi tối trong phòng; có và không đeo kính nếu người đó hay đeo.
   - Khuôn mặt rộng từ 150 pixel trở lên, không dùng bộ lọc làm đẹp, mỗi ảnh chỉ một người.
10. **Ghi lại VRAM còn trống** để quyết định Gemini hay Ollama. Mô hình Ollama cỡ 7–8B cần thêm khoảng 5 GB VRAM (ước tính), nên GPU dưới 8 GB nên dùng Gemini.

### Bàn giao

- Repo trên GitHub đã có cây thư mục, `.gitignore`, `.env.example`, `README.md`.
- `docs/acceptance/phase-0.md`: ảnh `nvidia-smi`, ảnh tin nhắn Telegram, kết quả kiểm tra camera và Gemini.
- Thư mục `data/faces/` trên máy (không đưa lên GitHub).

### Nghiệm thu

- [ ] `nvidia-smi` hiển thị đúng GPU, cả trên máy và trong container.
- [ ] Đọc được hình từ nguồn video đã chọn.
- [ ] Telegram nhận được tin nhắn chữ và ảnh từ script.
- [ ] Gemini trả lời được 1 câu tiếng Việt.
- [ ] `git status` không hiện bất kỳ file nào trong `data/` hoặc `.env`.

### Duyệt

**\[DUYỆT\]** Hệ điều hành (Ubuntu hay Windows), lựa chọn Gemini hay Ollama, chất lượng và số lượng ảnh khuôn mặt.

## GĐ 1 — Khung xương hệ thống và luồng video

**Mục tiêu.** Dựng xong Redis, CSDL và service đọc camera, chạy ổn định. Mọi tính năng sau chỉ việc cắm vào.

**\[CUNG CẤP\]** Không có mục mới, dùng lại kết quả GĐ 0.

### Các bước

1. **`docker-compose.yml`** có service `redis` (image `redis:7-alpine`, không lưu xuống đĩa, giới hạn 256 MB), một mạng chung, thư mục `./data` gắn vào `/app/data` của mọi service.
2. **`shared/config.py`** đọc `.env` và `settings.yaml`. Thiếu biến bắt buộc thì dừng ngay và báo rõ thiếu biến nào.
3. **`shared/database.py`** định nghĩa 5 bảng ở mục 5.1 bằng SQLAlchemy. Tự tạo bảng khi chưa có, bật WAL và `busy_timeout`, có hàm tiện ích cho từng thao tác ghi.
4. **`shared/frame_bus.py`** có hai hàm: `publish(camera_id, frame)` và `get_latest(camera_id)` trả về ảnh, `frame_id`, `ts`.
5. **`services/stream_producer`**:
   - Mở `CAMERA_SOURCE`: số là webcam, chuỗi `rtsp://` là camera IP (ép RTSP qua TCP cho ổn định).
   - Đọc khung trong một luồng riêng và chỉ giữ khung mới nhất, để bộ đệm không dồn làm hình bị trễ dần.
   - Thu nhỏ theo `STREAM_WIDTH`, nén JPEG, ghi Redis đúng `STREAM_FPS`.
   - Mất kết nối: thử lại sau 1, 2, 4… giây, tối đa 30 giây mỗi lần. Mất quá 5 phút thì gửi một cảnh báo `system` qua Telegram.
   - Ghi `heartbeat:stream_producer` vào Redis.
6. **`scripts/view_stream.py`** đọc hình từ Redis, hiển thị cửa sổ, in FPS thực và độ trễ. Tùy chọn `--snapshot` lưu một ảnh tĩnh.
7. **Kiểm thử tự động** bằng pytest cho `frame_bus` và `database`.
8. **Chạy thử 30 phút**, ghi RAM của producer mỗi phút bằng `docker stats`.

**\[LƯU Ý\]** Đo độ trễ hai lớp. Lớp trong hệ thống: thời điểm hiện tại trừ `ts`. Lớp đầu–cuối: quay camera vào đồng hồ bấm giờ trên màn hình, so con số trên hình với đồng hồ thật.

### Bàn giao

- `docker compose up -d` chạy được `redis` và `stream_producer`.
- `scripts/view_stream.py` và các bài kiểm thử pytest.
- `docs/acceptance/phase-1.md`: bảng RAM theo thời gian, hai con số độ trễ, ảnh chụp cửa sổ xem hình.

### Nghiệm thu

- [ ] Producer chạy 30 phút liên tục. **\[ĐỀ XUẤT\]** RAM ở phút 30 không cao hơn phút 5 quá 10%.
- [ ] Độ trễ trong hệ thống dưới 200 ms. Độ trễ đầu–cuối được đo và ghi lại.
- [ ] Rút webcam (hoặc ngắt mạng camera IP) 1 phút rồi cắm lại: producer tự nối lại, không phải khởi động lại.
- [ ] Dừng hẳn container producer: Docker tự bật lại.
- [ ] Mở `smarthome.db` bằng DB Browser for SQLite thấy đủ 5 bảng.

### Duyệt

**\[DUYỆT\]** Xem ảnh chụp cửa sổ xem hình, bảng RAM và hai con số độ trễ trong biên bản, sau đó merge Pull Request.

## GĐ 2 — Nhận diện người nhà và cảnh báo người lạ

**Mục tiêu.** Camera phân biệt được thành viên gia đình với người lạ, ghi sổ ra vào và gửi ảnh người lạ qua Telegram.

**\[CUNG CẤP\]** Mục 6 (ảnh khuôn mặt, tên, vai trò) và mục 18 (sự đồng ý). Một người ngoài danh sách để đóng vai người lạ.

### Các bước

1. **`scripts/enroll_faces.py`** quét `data/faces/<ten>/`:
   - Phát hiện mặt trong từng ảnh. Bỏ ảnh không có mặt hoặc có hơn một mặt, liệt kê các ảnh bị bỏ.
   - Lấy vector đã chuẩn hóa của từng ảnh, lấy trung bình rồi chuẩn hóa lại, lưu vào `members`.
   - In báo cáo độ tương đồng: ảnh cùng người so với trung bình, và giữa các người khác nhau. Hai con số này giúp chọn ngưỡng.
2. **`services/worker_face`** đọc Redis ở 2–3 FPS, phát hiện mặt, bỏ mặt nhỏ hơn `min_face_size_px`. Mỗi mặt còn lại được so cosine với mọi thành viên.
3. **Theo dấu mặt giữa các khung** bằng độ chồng lấp khung bao (IoU), để đếm "3 khung liên tiếp" đúng cho từng người khi có nhiều người trong hình.
4. **Quy tắc quyết định:**
   - Độ tương đồng cao nhất từ ngưỡng trở lên (mặc định 0,55): là thành viên đó. Ghi `access_logs` nếu người này chưa được ghi trong 120 giây gần nhất.
   - Dưới ngưỡng 3 khung liên tiếp: là người lạ. Lưu ảnh toàn khung có vẽ khung mặt và ảnh cắt mặt, ghi `alerts`, gửi Telegram. Không gửi lại trong 60 giây.
   - Mặt mờ, quá nhỏ hoặc chỉ xuất hiện 1–2 khung: không kết luận gì.
5. **Tin nhắn Telegram** gồm ảnh, giờ phút giây, tên camera, độ tương đồng cao nhất. Ví dụ: "Cảnh báo: phát hiện người lạ lúc 20:31:05, camera cam\_test".
6. **Ghi log độ tương đồng** của mọi lần so khớp ra file CSV trong `data/`, phục vụ hiệu chỉnh.
7. **Hiệu chỉnh ngưỡng.** Mỗi thành viên đi lại trước camera 2 phút, người lạ 2 phút. Vẽ phân bố điểm của hai nhóm, chọn ngưỡng nằm giữa.
8. **Kiểm thử tự động** cho logic quyết định và cooldown, dùng vector giả.

**\[LƯU Ý\]** Hệ thống chưa chống giả mạo: giơ ảnh của một thành viên sẽ được nhận là thành viên đó. Ghi rõ điều này trong README.

### Bàn giao

- `enroll_faces.py`, `worker_face` trong Docker Compose, file CSV điểm tương đồng.
- `docs/acceptance/phase-2.md`: biểu đồ phân bố điểm, ngưỡng đề xuất, ảnh tin nhắn Telegram, trích đoạn `access_logs`.

### Nghiệm thu

- [ ] `enroll_faces.py` có ít nhất 5 ảnh dùng được cho mỗi người.
- [ ] Mỗi thành viên đi vào khung hình 5 lần ở các góc khác nhau. **\[ĐỀ XUẤT\]** Ghi đúng tên ít nhất 4/5 lần, không lần nào bị báo là người lạ.
- [ ] Thành viên đứng trước camera 5 phút: không quá 3 dòng log.
- [ ] Người lạ (hoặc ảnh người không có trong dữ liệu) xuất hiện: Telegram nhận ảnh rõ mặt trong 3–5 giây.
- [ ] Người lạ đứng 3 phút: không quá 3 cảnh báo.
- [ ] Không thấy mặt (quay lưng, đi xa): không ghi log, không cảnh báo.

### Duyệt

**\[DUYỆT\]** Ngưỡng cuối cùng, nội dung và chất lượng ảnh tin nhắn Telegram, số lần nhận đúng của từng thành viên.

## GĐ 3 — Nhận diện đồ vật và ghi nhớ vị trí theo vùng

**Mục tiêu.** Camera theo dõi các đồ vật bạn chỉ định, nhớ vùng và thời điểm thấy lần cuối. Thêm đồ vật mới không cần train lại mô hình.

**\[CUNG CẤP\]** Mục 7 (ảnh tĩnh toàn cảnh), mục 8 (danh sách vùng), mục 9 (đồ vật và vật thật để thử).

### Các bước

1. **`scripts/draw_zones.py`** mở ảnh tĩnh, cho click chuột để vẽ từng đa giác, nhập tên và loại vùng, lưu `data/zones.json` theo tọa độ 0–1. Xuất thêm một ảnh tô màu các vùng để kiểm tra bằng mắt.
2. **`shared/zones.py`** đọc `zones.json`, đồng bộ vào bảng `zones`, có hàm `find_zone(x, y)` dùng `cv2.pointPolygonTest()`. Điểm thuộc nhiều vùng thì chọn vùng nhỏ nhất.
3. **Nạp danh sách đồ vật ban đầu** vào `tracked_objects`, ví dụ `keys` → Chìa khóa, `glasses` → Mắt kính, `wallet` → Ví tiền.
4. **`services/worker_object`** mỗi 3–5 giây lấy khung mới nhất, chạy YOLOE-26 với `set_classes()` là danh sách từ khóa tiếng Anh.
5. **Tải trước mô hình.** Lần gọi `set_classes()` đầu tiên tải thêm bộ mã hóa chữ khoảng 254 MB và cần mạng. Lưu sẵn vào thư mục `models/` gắn vào container để không tải lại mỗi lần khởi động.
6. **Nạp nóng danh sách.** Mỗi chu kỳ đọc `objects:version` trong Redis. Số đổi thì đọc lại bảng và gọi lại `set_classes()`, không khởi động lại service.
7. **Xác định vị trí.** Với mỗi đồ vật đạt `min_confidence`, lấy tâm khung bao (cₓ, cᵧ), tìm vùng. Cập nhật `last_seen_at`, `last_confidence`, ghi đè ảnh cắt mới nhất của đồ vật đó.
8. **Chống nhảy vùng do nhiễu.** **\[ĐỀ XUẤT\]** Chỉ đổi `last_zone` khi thấy đồ vật ở vùng mới 2 chu kỳ liên tiếp.
9. **Khi không thấy đồ vật** thì giữ nguyên vị trí cũ, vì đó chính là "lần cuối thấy". Thấy ở ngoài mọi vùng thì ghi "Ngoài các vùng đã đặt tên".
10. **Thử từ khóa.** Với mỗi đồ vật, thử vài từ khóa tiếng Anh (ví dụ `keys`, `key ring`) và giữ từ nhận tốt nhất.

**\[LƯU Ý\]** Vật nhỏ như chìa khóa, ở xa camera sẽ khó nhận. Nếu tỷ lệ nhận thấp, cho `worker_object` đọc ảnh độ phân giải cao hơn hoặc chỉ quét trong các vùng đồ nội thất.

### Bàn giao

- `draw_zones.py`, `data/zones.json` kèm ảnh tô vùng, `worker_object` trong Docker Compose.
- `docs/acceptance/phase-3.md`: bảng tỷ lệ nhận đúng của từng đồ vật, từ khóa cuối cùng.

### Nghiệm thu

- [ ] `zones.json` có ít nhất 3 vùng, ảnh tô vùng khớp với đồ vật thật trong phòng.
- [ ] Đặt kính, ví hoặc điện thoại lên bàn rồi lấy đi sau 10 giây: CSDL ghi đúng "Bàn làm việc", thời điểm lệch không quá một chu kỳ quét.
- [ ] Chuyển đồ vật từ bàn sang sofa: `last_zone` đổi thành "Ghế sofa".
- [ ] Thêm dòng `cup` → Cốc nước khi hệ thống đang chạy: được nhận ở chu kỳ kế tiếp, không khởi động lại, không train.
- [ ] Mỗi đồ vật được đặt thử 10 lần. **\[ĐỀ XUẤT\]** Nhận đúng ít nhất 7/10 lần.

### Duyệt

**\[DUYỆT\]** Danh sách đồ vật và từ khóa cuối cùng (bỏ vật nhận kém), tên và ranh giới các vùng.

## GĐ 4 — Phát hiện té ngã (giảm báo giả)

**Mục tiêu.** Phát hiện người ngã xuống sàn và không dậy, gửi cảnh báo khẩn. Không báo khi người ngồi, cúi hoặc nằm nghỉ trên sofa, giường.

**\[CUNG CẤP\]** Mục 10 (người diễn thử và nệm). Ai sẽ nhận cảnh báo té ngã: chỉ bạn, hay một nhóm Telegram cả gia đình.

### Các bước

1. **Cho producer đọc được file video** (`CAMERA_SOURCE=data/test_videos/nga_01.mp4`, phát lặp). Nhờ đó chỉnh ngưỡng bằng video đã quay, không phải ngã thật nhiều lần.
2. **Quay bộ video kiểm thử:** 10 cảnh ngã trên nệm và 10 cảnh dễ nhầm (ngồi phịch xuống ghế, nằm lên sofa, cúi nhặt đồ, ngồi xổm, tập thể dục). Lưu trong `data/test_videos/`, không đưa lên GitHub.
3. **`services/worker_fall`** đọc Redis ở 10–15 FPS, chạy YOLO26-pose kèm theo dấu người (mỗi người một ID) để xét riêng từng người. Bỏ qua điểm khớp có độ tin cậy dưới 0,5.
4. **Bộ lọc 3 lớp**, xếp thành chuỗi trạng thái Bình thường → Đang ngã → Đang nằm → Xác nhận:
   1. *Vận tốc rơi.* Trung điểm vai–hông đi XUỐNG nhanh trong 0,5–1,0 giây. Trong tọa độ ảnh, trục Y hướng xuống nên ngã là Y TĂNG (bản nháp ghi "giảm" là ngược). Chia quãng rơi cho chiều cao người lúc đứng để không phụ thuộc xa hay gần camera.
   2. *Tư thế nằm.* Trong 2 giây sau đó, tỷ lệ rộng/cao của khung bao lớn hơn 1,2. **\[ĐỀ XUẤT\]** Thêm điều kiện thân người (hông → vai) nghiêng quá 60° so với phương thẳng đứng, vì camera nhìn chéo làm khung bao méo.
   3. *Vùng và bất động.* Điểm hông không nằm trong vùng `safe_rest`, và các điểm khớp gần như không dịch chuyển trong 4 giây.
5. **Huỷ bỏ** nếu người đứng dậy trước khi đủ 4 giây.
6. **Khi xác nhận:** ghi `alerts` loại `fall`, gửi Telegram tin khẩn kèm ảnh, không gửi lại trong 60 giây cho cùng một người.
7. **Hiệu chỉnh** `drop_speed_threshold` bằng bộ video kiểm thử, ghi kết quả vào `settings.yaml`.
8. **Kiểm thử tự động** cho chuỗi trạng thái bằng chuỗi điểm khớp giả.

**\[LƯU Ý\]** Người quỵ xuống từ từ (trượt dần theo tường) có thể không qua lớp 1. Ghi rõ giới hạn này trong README. Người diễn thử phải ngã trên nệm, có người đứng cạnh.

**\[DUYỆT\]** Phát âm thanh cảnh báo tại chỗ: phát từ trong container Docker khá rắc rối. Đề xuất phát trên trình duyệt đang mở Dashboard, hoặc bỏ qua ở bản test.

### Bàn giao

- `worker_fall` trong Docker Compose, producer đọc được file video.
- `docs/acceptance/phase-4.md`: bảng kết quả 20 video kiểm thử, ngưỡng đã chọn, ảnh tin nhắn khẩn.

### Nghiệm thu

- [ ] Ngồi xuống ghế, nằm lên sofa, cúi nhặt đồ, ngồi xổm (mỗi cảnh 3 lần): không báo động.
- [ ] Từ từ nằm xuống sàn (không phải ngã): không báo động.
- [ ] Trượt ngã xuống sàn và nằm yên 5 giây: Telegram nhận cảnh báo khẩn kèm ảnh.
- [ ] Ngã rồi đứng dậy ngay trong 2 giây: không báo động.
- [ ] Bộ 20 video. **\[ĐỀ XUẤT\]** Bắt đúng ít nhất 9/10 cảnh ngã, báo nhầm 0/10 cảnh dễ nhầm.

### Duyệt

**\[DUYỆT\]** Bảng kết quả 20 video, người nhận cảnh báo té ngã, quyết định về âm thanh tại chỗ.

## GĐ 5 — Trợ lý ảo trò chuyện với camera (chat và giọng nói)

**Mục tiêu.** Bạn nhắn tin qua Telegram hoặc Dashboard, hoặc gửi tin nhắn thoại, để hỏi thông tin và dạy camera theo dõi đồ vật mới.

**\[CUNG CẤP\]** Mục 11 (câu hỏi mẫu) và mục 12 (giọng nói). Cách trợ lý xưng hô với bạn.

### Các bước

1. **`services/assistant_api` bằng FastAPI** với các đường dẫn: `POST /chat` (nhận chữ, trả câu trả lời kèm ảnh nếu có), `POST /voice` (nhận file âm thanh), `GET /health`.
2. **Lớp LLM chung** có hai bản cài đặt Gemini và Ollama, chọn bằng `LLM_PROVIDER`.
3. **Lời nhắc hệ thống (system prompt) tiếng Việt:** chỉ trả lời từ kết quả công cụ, không có dữ liệu thì nói không biết, câu trả lời ngắn, ngày giờ hiện tại theo giờ Việt Nam được chèn vào mỗi lượt.
4. **Bộ công cụ cho LLM gọi:**

| Công cụ | Tham số | Trả về |
| --- | --- | --- |
| `get_visitors` | `since_hours` (mặc định 24), `member_name` (tuỳ chọn) | Tên, giờ vào đầu và cuối, số lần; số lần có người lạ |
| `find_object` | `object_name` (tiếng Việt) | Vùng, thời điểm thấy cuối, "cách đây bao lâu", đường dẫn ảnh |
| `register_new_object` | `vn_name`, `en_keyword` | Xác nhận đã thêm, hoặc báo đã có sẵn |
| `get_recent_alerts` | `since_hours` (mặc định 24), `alert_type` (tuỳ chọn) | Danh sách cảnh báo kèm giờ và ảnh |
| `list_tracked_objects` **\[ĐỀ XUẤT\]** | không có | Các đồ vật đang theo dõi |
| `remove_object` **\[ĐỀ XUẤT\]** | `vn_name` | Ngừng theo dõi một đồ vật (`is_active = false`) |

5. **An toàn công cụ.** LLM không bao giờ tự viết câu lệnh SQL; mọi tham số được kiểm tra kiểu và giới hạn. `find_object` so tên không phân biệt hoa thường và dấu ("chia khoa" vẫn khớp "Chìa khóa"). `register_new_object` tăng `objects:version` trong Redis.
6. **Telegram bot** dùng long polling, không cần mở cổng ra Internet. Chỉ trả lời các `chat_id` trong danh sách cho phép, tin từ tài khoản khác bị bỏ qua và ghi log.
7. **Nghe:** tin nhắn thoại Telegram → faster-whisper (`language="vi"`) → chữ → `/chat`. Thiếu VRAM thì cho Whisper chạy CPU.
8. **Nói:** câu trả lời → edge-tts → chuyển sang OGG/Opus bằng ffmpeg → gửi lại dạng tin nhắn thoại. edge-tts lỗi thì vẫn gửi câu trả lời bằng chữ.
9. **Bộ câu hỏi kiểm thử:** script chạy các câu hỏi mẫu của bạn trên dữ liệu CSDL giả đã biết trước, so với đáp án mong đợi.

**\[DUYỆT\]** Quy ước thời gian trong câu hỏi: "nãy giờ" là 2 giờ qua, "hôm nay" tính từ 00:00 giờ Việt Nam, "gần đây" là 24 giờ qua.

### Bàn giao

- `assistant_api` và Telegram bot trong Docker Compose, file system prompt riêng để dễ sửa.
- `docs/acceptance/phase-5.md`: bảng câu hỏi, câu trả lời thật, đúng hay sai; ảnh chụp hội thoại Telegram.

### Nghiệm thu

- [ ] "Nãy giờ có ai vào nhà không?" → đúng tên thành viên và giờ vào theo CSDL.
- [ ] "Chìa khóa của tôi đâu rồi?" → đúng vùng, thời điểm thấy cuối, kèm ảnh.
- [ ] "Hãy giúp tôi theo dõi thêm cái mũ bảo hiểm" → CSDL có dòng mới (`helmet`), `worker_object` nhận ở chu kỳ sau.
- [ ] "Hôm nay có cảnh báo gì không?" → đúng danh sách trong CSDL.
- [ ] Hỏi về đồ vật chưa theo dõi ("Cái ô của tôi đâu?") → nói chưa theo dõi và gợi ý thêm, không bịa vị trí.
- [ ] Tài khoản Telegram không có trong danh sách nhắn tin → không được trả lời.
- [ ] Tin nhắn thoại tiếng Việt → nhận lại câu trả lời bằng chữ và giọng nói (nếu bật).
- [ ] **\[ĐỀ XUẤT\]** Câu hỏi bằng chữ được trả lời trong dưới 5 giây.

### Duyệt

**\[DUYỆT\]** System prompt và cách xưng hô, quy ước thời gian, bảng kết quả bộ câu hỏi.

## GĐ 6 — Dashboard và đóng gói

**Mục tiêu.** Quản lý mọi thứ trên trình duyệt, không cần gõ lệnh. Cả hệ thống khởi động bằng một lệnh `docker compose up -d`. Đây là giai đoạn khép lại Chặng A.

**\[CUNG CẤP\]** Mục 13 (mật khẩu Dashboard).

### Các bước

1. **`services/dashboard` bằng Streamlit**, có đăng nhập bằng mật khẩu, chỉ mở trong mạng nhà. Gồm 4 tab:
   - *Live và Cảnh báo:* ảnh mới nhất từ Redis, đèn trạng thái từng service, danh sách cảnh báo với nút "Đã xem" và "Báo giả".
   - *Thành viên:* danh sách, tải ảnh lên để thêm người mới, xóa thành viên (xóa cả vector và ảnh), lịch sử ra vào lọc theo ngày.
   - *Đồ vật và Vùng:* bảng đồ vật (vùng, lần cuối thấy, ảnh), nút thêm và ngừng theo dõi, ảnh tô vùng.
   - *Trò chuyện:* khung chat gọi `/chat`, gửi file hoặc bản ghi âm tới `/voice`.
2. **Hoàn thiện `docker-compose.yml`:** đủ mọi service, health check, thứ tự khởi động, cấp GPU cho các worker, gắn `data/` và `models/`, `restart: unless-stopped`, giới hạn log mỗi service 3 file × 10 MB để không đầy ổ.
3. **Dọn dữ liệu tự động. \[ĐỀ XUẤT\]** Xóa ảnh chụp cũ hơn 30 ngày, `access_logs` cũ hơn 90 ngày, chạy mỗi đêm.
4. **Sao lưu hằng tuần** `smarthome.db`, `zones.json` và `faces/` sang ổ hoặc thư mục khác trên máy.
5. **README đầy đủ:** yêu cầu phần cứng, cài đặt từng bước, giải thích từng biến `.env`, lệnh chạy, lỗi thường gặp, giới hạn đã biết.
6. **Thử cài từ đầu:** clone repo vào một thư mục mới (hoặc máy khác), chỉ làm theo README.

### Bàn giao

- Dashboard, `docker-compose.yml` hoàn chỉnh, script dọn dữ liệu và sao lưu, README.
- `docs/acceptance/phase-6.md`: ảnh chụp 4 tab, kết quả thử cài từ đầu. Gắn tag `v0.6` đánh dấu xong Chặng A.

### Nghiệm thu

- [ ] `docker compose up -d` bật toàn bộ. **\[ĐỀ XUẤT\]** Mọi service báo khỏe trong vòng 3 phút.
- [ ] Thêm thành viên mới qua trình duyệt: người đó được nhận ra mà không phải chạy lệnh nào.
- [ ] Thêm hoặc ngừng theo dõi đồ vật qua trình duyệt: worker cập nhật ở chu kỳ kế tiếp.
- [ ] Bấm "Báo giả" một cảnh báo: trạng thái trong CSDL đổi thành `false_alarm`.
- [ ] Sai mật khẩu: không vào được Dashboard.
- [ ] Khởi động lại máy: hệ thống tự chạy lại.
- [ ] Thử cài từ đầu theo README thành công.

### Duyệt

**\[DUYỆT\]** Giao diện 4 tab, README. Chủ dự án quyết định chuyển sang Chặng B (camera gia đình).

## GĐ 7 — Chuyển từ máy tính sang camera gia đình (Chặng B)

**Mục tiêu.** Chạy hệ thống đã kiểm chứng với camera thật trong nhà, ổn định 72 giờ liên tục. Chỉ sửa cấu hình, không sửa code.

**\[CUNG CẤP\]** Mục 14–18 ở bảng mục 6.

### 7.1. Kiểm tra camera có dùng được không

1. **Xác định camera có hỗ trợ RTSP.** Đây là điều kiện bắt buộc. Ví dụ với Tapo: camera cắm điện hỗ trợ RTSP và ONVIF, phần lớn camera dùng pin thì không ([hướng dẫn Tapo](https://tapo.com/vn/faqs/how-to-view-tapo-camera-on-pc-nas-or-nvr-using-rtsponvif)). Hãng khác thì tra hướng dẫn RTSP của đúng model.
2. **Tạo tài khoản RTSP** trong ứng dụng của hãng. Với Tapo là "Tài khoản camera" trong Cài đặt nâng cao, khác với tài khoản Tapo, link có dạng `rtsp://<IP>:554/stream1` (nét) hoặc `/stream2` (nhẹ).
3. **Mở link bằng VLC** trên chính máy chủ. Không mở được thì dừng lại xử lý trước khi làm tiếp.
4. **Chọn luồng. \[ĐỀ XUẤT\]** Thử luồng nhẹ trước vì đỡ tốn máy. Nếu khuôn mặt ở khoảng cách thật nhỏ hơn 60 pixel thì chuyển sang luồng nét.

**\[LƯU Ý\]** Camera chỉ phục vụ được một số luồng cùng lúc. Nếu đang xem bằng app điện thoại hoặc đầu ghi khác mà hệ thống mất hình, thử tắt bớt các nơi đang xem. Camera không có RTSP thì cần đổi sang camera khác.

### 7.2. Mạng và bảo mật

1. Đặt IP cố định (DHCP reservation) cho camera và máy chủ trong router, để link RTSP không đổi sau khi khởi động lại.
2. Máy chủ nối dây mạng nếu được. Camera Wi-Fi đặt nơi sóng mạnh.
3. Đổi mật khẩu mặc định, cập nhật firmware camera.
4. Không mở cổng (port forwarding) cho camera hay Dashboard ra Internet. Telegram bot chỉ kết nối ra ngoài nên không cần mở cổng.

### 7.3. Vị trí lắp đặt

**\[DUYỆT\]** Một camera khó tối ưu cả ba việc. Nhìn mặt cần góc ngang tầm người hướng ra cửa; té ngã cần thấy nhiều sàn; đồ vật cần thấy rõ mặt bàn. Bạn chọn tính năng ưu tiên cho camera đầu tiên.

- Gợi ý chung: đặt cao khoảng 2–2,5 m ở góc phòng khách, nhìn chéo thấy cửa ra vào, sàn và bàn.
- Tránh ngược sáng: không để cửa sổ sáng phía sau người cần nhận mặt.
- Không hướng ra đường, khu vực chung hay nhà hàng xóm; không lắp trong phòng ngủ, nhà tắm.
- Ban đêm camera chuyển sang hồng ngoại (ảnh đen trắng), nhận diện mặt sẽ kém hơn, cần kiểm tra riêng.

### 7.4. Chuyển cấu hình và hiệu chỉnh lại

1. Sửa `.env`: `CAMERA_ID=cam_phongkhach`, `CAMERA_SOURCE=rtsp://...`. Nếu phải sửa code mới chạy được, đó là lỗi của Chặng A: sửa, ghi vào biên bản, thêm bài kiểm thử.
2. Chụp ảnh tĩnh mới, vẽ lại `zones.json`.
3. **Đăng ký bổ sung khuôn mặt từ chính camera này.** Thêm `scripts/capture_faces.py`: chọn tên thành viên, đứng trước camera, script tự lưu 5–10 ảnh mặt rõ nhất rồi chạy lại `enroll_faces.py`.
4. Hiệu chỉnh lại ngưỡng khuôn mặt như GĐ 2 bước 7, cả ban ngày và ban đêm.
5. Diễn lại vài cảnh ngã trên nệm ở góc mới, kiểm tra ngưỡng té ngã.
6. Kiểm tra lại từ khóa đồ vật ở khoảng cách mới.

### 7.5. Chạy thử 72 giờ

- Theo dõi hằng ngày: số cảnh báo, số báo giả (đánh dấu trên Dashboard), số lần mất kết nối camera, RAM, VRAM, nhiệt độ GPU, dung lượng ổ còn trống.
- Ghi nhật ký vận hành mỗi ngày vào `docs/acceptance/phase-7.md`.
- Máy chủ tắt chế độ ngủ. **\[ĐỀ XUẤT\]** Dùng bộ lưu điện (UPS) nếu có.

### Nghiệm thu

- [ ] Link RTSP mở được bằng VLC và trong `view_stream.py`.
- [ ] Hệ thống chạy với camera mới chỉ bằng cách sửa `.env`.
- [ ] Rút điện camera 2 phút rồi cắm lại: tự nối lại. Mất quá 5 phút thì có cảnh báo `system`.
- [ ] Lặp lại mỗi tính năng của GĐ 2–5 ít nhất một kịch bản ở góc camera mới, đều đạt.
- [ ] Ban đêm: ghi lại tỷ lệ nhận đúng mặt, không có hàng loạt báo giả người lạ.
- [ ] 72 giờ liên tục đạt định nghĩa "xong dự án" ở mục 2.5.
- [ ] Dùng 4G bên ngoài mạng nhà: không vào được Dashboard hay camera, Telegram vẫn nhận cảnh báo và trả lời.

### Duyệt

**\[DUYỆT\]** Vị trí và góc camera, luồng sử dụng, báo cáo 72 giờ. Duyệt xong thì gắn tag `v1.0`.

## 7. Tổng hợp các điểm duyệt

Dự án có 6 quyết định cần chốt trước khi code và 8 điểm duyệt, mỗi giai đoạn một điểm. Chưa qua điểm duyệt thì không sang giai đoạn sau.

&#91;embedded content: lộ trình · 8 giai đoạn, 8 điểm duyệt\]

Mỗi hình thoi là một Pull Request chờ bạn duyệt; điểm cuối sau GĐ 7 là nghiệm thu cả dự án và gắn tag `v1.0`.

### 7.1. Quyết định cần chốt trước khi code

| # | Quyết định | Đề xuất mặc định | Xem mục | Kết quả |
| --- | --- | --- | --- | --- |
| Q1 | Định nghĩa "xong dự án" | 72 giờ ổn định, báo giả người lạ ≤ 2 lần/ngày, không báo giả té ngã | 2.5 | Chưa duyệt |
| Q2 | Thế hệ mô hình YOLO | YOLO26-pose và YOLOE-26, YOLO-World dự phòng | 3.3 | Chưa duyệt |
| Q3 | LLM cho trợ lý | Gemini Flash-Lite, Ollama là phương án riêng tư | 3.3 | Chưa duyệt |
| Q4 | Repo Private hay Public | Private | 4 | Chưa duyệt |
| Q5 | Nguồn gốc dữ liệu vùng | `zones.json` là gốc, đồng bộ vào bảng `zones` | 5.1 | Chưa duyệt |
| Q6 | Ngưỡng khởi điểm | Theo bản nháp, đo lại từng giai đoạn | 5.5 | Chưa duyệt |

### 7.2. Điểm duyệt cuối mỗi giai đoạn

| Điểm | Chủ dự án xem gì | Quyết định cần đưa ra | Kết quả |
| --- | --- | --- | --- |
| Sau GĐ 0 | Ảnh `nvidia-smi`, tin nhắn Telegram, kiểm tra camera, ảnh khuôn mặt | Ubuntu hay Windows; Gemini hay Ollama | Chưa duyệt |
| Sau GĐ 1 | Bảng RAM 30 phút, hai con số độ trễ | Merge Pull Request | Chưa duyệt |
| Sau GĐ 2 | Phân bố điểm tương đồng, ảnh cảnh báo Telegram | Ngưỡng nhận diện mặt | Chưa duyệt |
| Sau GĐ 3 | Tỷ lệ nhận từng đồ vật, ảnh tô vùng | Danh sách đồ vật, từ khóa, vùng | Chưa duyệt |
| Sau GĐ 4 | Kết quả 20 video kiểm thử | Người nhận cảnh báo, âm thanh tại chỗ | Chưa duyệt |
| Sau GĐ 5 | Bảng câu hỏi và câu trả lời | System prompt, xưng hô, quy ước thời gian | Chưa duyệt |
| Sau GĐ 6 | Ảnh 4 tab Dashboard, README, thử cài từ đầu | Sang Chặng B hay chưa | Chưa duyệt |
| Sau GĐ 7 | Báo cáo 72 giờ trên camera gia đình | Vị trí camera; nghiệm thu `v1.0` | Chưa duyệt |

## 8. Rủi ro và điều chỉnh kỹ thuật so với bản nháp

Ba điểm đầu là lỗi trong bản nháp v1.0, đã sửa trong tài liệu này. Các điểm còn lại là rủi ro người thực hiện cần biết trước.

| # | Vấn đề | Nếu bỏ qua | Cách xử lý | Giai đoạn |
| --- | --- | --- | --- | --- |
| 1 | Bản nháp ghi ngã là tọa độ Y "giảm", nhưng trục Y của ảnh hướng xuống | Lớp 1 của bộ lọc té ngã không bao giờ đúng | Ngã là Y tăng, chia cho chiều cao người | GĐ 4 |
| 2 | Docker Desktop trên Windows không cho container đọc webcam USB | `stream_producer` không chạy được | Dùng Ubuntu, hoặc chạy producer ngoài Docker | GĐ 0–1 |
| 3 | Bản nháp có cả `zones.json` lẫn bảng `zones` mà không nói cái nào là gốc | Hai nơi lệch nhau | File là gốc, đồng bộ vào bảng | GĐ 1, 3 |
| 4 | Nhiều container cùng ghi một file SQLite | Lỗi `database is locked` | WAL, `busy_timeout`, giao dịch ngắn | GĐ 1 |
| 5 | Worker chậm hơn camera | Hàng đợi phình to, tràn RAM, hình trễ dần | Chỉ giữ khung mới nhất trong Redis | GĐ 1 |
| 6 | Ngưỡng 0,55 chưa kiểm chứng với camera thật | Báo giả hoặc bỏ sót người lạ | Hiệu chỉnh bằng dữ liệu thật | GĐ 2, 7 |
| 7 | Không chống giả mạo khuôn mặt | Ảnh của thành viên qua mặt được hệ thống | Ghi rõ giới hạn; không dùng hệ thống để mở khóa cửa | Mọi giai đoạn |
| 8 | Camera chuyển hồng ngoại ban đêm | Nhận mặt kém, dễ báo giả người lạ | Kiểm tra riêng ban đêm, có thể cần nhiều khung hơn trước khi báo | GĐ 7 |
| 9 | Vật nhỏ ở xa camera | Không nhận ra chìa khóa, kính | Thử từ khóa, độ phân giải cao hơn, bỏ vật nhận kém | GĐ 3 |
| 10 | Ba mô hình thị giác, Whisper và có thể Ollama cùng dùng GPU | Hết VRAM, service bị tắt | Đo VRAM mỗi giai đoạn; Whisper chạy CPU; dùng Gemini | GĐ 0, 5 |
| 11 | Mô hình tải thêm dữ liệu lần đầu chạy | Khởi động chậm, lỗi khi mất mạng | Tải sẵn vào `models/` | GĐ 3–4 |
| 12 | edge-tts là dịch vụ không chính thức; tên model Gemini đổi theo thời gian | Trợ lý mất tiếng hoặc ngừng trả lời | Trả lời bằng chữ khi TTS lỗi; tên model để trong `.env` | GĐ 5 |
| 13 | LLM tự bịa câu trả lời | Thông tin sai về người và đồ vật | Chỉ trả lời từ kết quả công cụ, có câu hỏi bẫy trong bộ kiểm thử | GĐ 5 |
| 14 | Mất điện, mất mạng, máy chủ ngủ | Hệ thống ngừng giám sát mà không ai biết | Heartbeat, cảnh báo `system`, tắt chế độ ngủ, UPS | GĐ 1, 7 |

## 9. Quyền riêng tư, bảo mật và giấy phép

Hệ thống xử lý khuôn mặt người thân, nên mặc định mọi hình ảnh nằm trên máy trong nhà, chỉ gửi ra ngoài phần tối thiểu. Mục này không phải tư vấn pháp lý.

### 9.1. Dữ liệu nào đi đâu

| Dữ liệu | Lưu ở đâu | Có rời khỏi nhà không |
| --- | --- | --- |
| Video trực tiếp | RAM (Redis), không lưu lại | Không |
| Ảnh mẫu và vector khuôn mặt | `data/` trên máy chủ | Không |
| Ảnh người lạ, ảnh té ngã | `data/snapshots/` | Có: gửi qua Telegram cho người nhận cảnh báo |
| Tên thành viên, giờ ra vào, vị trí đồ vật | CSDL | Có: gửi dạng chữ tới Gemini khi bạn hỏi trợ lý (trừ khi dùng Ollama) |
| Giọng nói của bạn | Chuyển thành chữ ngay trên máy (Whisper) | Không |
| Câu trả lời của trợ lý | — | Có: gửi dạng chữ tới dịch vụ đọc của edge-tts |

### 9.2. Gemini và dữ liệu cá nhân

Theo [điều khoản Gemini API](https://ai.google.dev/gemini-api/terms), khi dùng hạn mức miễn phí, Google dùng nội dung gửi lên để cải thiện sản phẩm và có thể có người duyệt đọc. Google khuyên không gửi thông tin cá nhân lên dịch vụ miễn phí. Khi bật tài khoản thanh toán Cloud Billing, mọi lượt dùng được xử lý dữ liệu như dịch vụ trả phí.

**\[DUYỆT\]** Chọn một cách:

1. Bật Cloud Billing cho khóa Gemini.
2. Dùng Ollama chạy trên máy, không gửi gì ra ngoài.
3. Thay tên thật bằng mã ("Thành viên 1") trước khi gửi Gemini, đổi lại tên thật khi hiển thị.

### 9.3. Gia đình và pháp luật

Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 có hiệu lực từ 01/01/2026 ([SBV](https://sbv.gov.vn/en/w/tri%E1%BB%83n-khai-thi-h%C3%A0nh-lu%E1%BA%ADt-b%E1%BA%A3o-v%E1%BB%87-d%E1%BB%AF-li%E1%BB%87u-c%C3%A1-nh%C3%A2n-1)), kèm [Nghị định 356/2025/NĐ-CP](https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Nghi-dinh-356-2025-ND-CP-huong-dan-Luat-Bao-ve-du-lieu-ca-nhan-687428.aspx). Dữ liệu sinh trắc học như khuôn mặt được bảo vệ chặt. Tối thiểu nên làm:

- Hỏi và có sự đồng ý của từng thành viên trước khi đăng ký khuôn mặt. Xóa ngay khi họ yêu cầu.
- Báo cho khách, người giúp việc biết trong nhà có camera AI.
- Không quay ra đường, khu vực chung hay nhà hàng xóm.
- Giữ ảnh và log có thời hạn (GĐ 6, bước 3).

### 9.4. Bảo mật

- Không mở cổng nào ra Internet. Dashboard có mật khẩu. Telegram bot chỉ trả lời các `chat_id` được phép.
- Bí mật chỉ nằm trong `.env`. Mật khẩu RTSP riêng, khác mật khẩu tài khoản camera.
- **\[ĐỀ XUẤT\]** Mã hóa ổ đĩa máy chủ (BitLocker trên Windows, LUKS trên Ubuntu) vì máy chứa ảnh khuôn mặt.

### 9.5. Giấy phép

| Thành phần | Giấy phép | Dùng trong gia đình | Nếu sau này bán sản phẩm |
| --- | --- | --- | --- |
| Mã nguồn InsightFace | MIT | Được | Được |
| Mô hình InsightFace `buffalo_l` | Chỉ cho nghiên cứu phi thương mại ([InsightFace](https://github.com/deepinsight/insightface)) | Dự án cá nhân, học tập, không thu tiền | Phải mua giấy phép, hoặc đổi sang YuNet + SFace của OpenCV (Apache-2.0) ([so sánh](https://huggingface.co/mudler/face-detect-gguf)) |
| Ultralytics YOLO26, YOLOE-26 | AGPL-3.0 hoặc Enterprise ([Ultralytics](https://docs.ultralytics.com/models/yolo26/)) | Được | Phải công khai mã nguồn theo AGPL, hoặc mua giấy phép Enterprise |
| edge-tts | Dùng dịch vụ đọc chữ của Microsoft Edge không chính thức | Được, chấp nhận rủi ro ngừng | Nên thay bằng dịch vụ TTS chính thức |

Nếu sau này muốn biến dự án thành sản phẩm, hai dòng InsightFace và Ultralytics phải xử lý trước tiên.

## 10. Prompt mẫu để giao việc

Xuất tài liệu này ra Markdown, lưu vào repo tại `docs/SPEC.md`. Sau đó dùng ba mẫu dưới đây: mẫu 10.1 một lần khi bắt đầu, mẫu 10.2 đầu mỗi giai đoạn, mẫu 10.3 khi giới thiệu dự án cho người khác.

### 10.1. Prompt khởi động cho AI coding agent

```text
Bạn là kỹ sư Python và thị giác máy tính trong dự án "Camera AI Thông Minh" (repo smart-home-ai).
Đặc tả đầy đủ nằm ở docs/SPEC.md. Đọc hết trước khi viết code.

Bối cảnh:
- Chạy trên 1 máy có GPU NVIDIA với 1 camera: webcam ở Chặng A, camera IP qua RTSP ở Chặng B.
- Kiến trúc Producer–Consumer: stream_producer ghi khung hình mới nhất vào Redis;
  worker_face, worker_object, worker_fall đọc ở tốc độ riêng và ghi kết quả vào SQLite;
  assistant_api (FastAPI + Gemini function calling) trả lời câu hỏi qua Telegram;
  dashboard Streamlit để quản lý. Tất cả chạy bằng Docker Compose.

Quy tắc bắt buộc:
1. Chỉ làm đúng giai đoạn được giao, không làm trước giai đoạn sau.
2. Mọi cấu hình đọc từ .env hoặc config/settings.yaml. Không viết cứng ngưỡng, đường dẫn, khóa.
3. Không đọc, in ra hay commit nội dung .env, thư mục data/ hay ảnh khuôn mặt.
4. Mỗi khung hình mang camera_id, frame_id, ts. Thời gian theo Asia/Ho_Chi_Minh.
5. Logic thuần (cosine, vùng, té ngã, cooldown) tách khỏi phần đọc/ghi và có test pytest.
6. Tên biến, hàm bằng tiếng Anh; docstring, README và biên bản bằng tiếng Việt.
7. Con số gắn [ĐỀ XUẤT] trong đặc tả là mặc định, đặt trong settings.yaml để chỉnh được.
8. Ghim phiên bản thư viện. Muốn dùng thư viện ngoài đặc tả thì nêu lý do và chờ tôi đồng ý.
9. Đặc tả chưa rõ hoặc mâu thuẫn: dừng lại, liệt kê phương án và hỏi tôi, không tự đoán.

Cách làm mỗi giai đoạn:
a. Nhắc lại mục tiêu, các bước và tiêu chí nghiệm thu bằng lời của bạn; liệt kê thông tin còn thiếu từ tôi.
b. Đưa kế hoạch: file sẽ tạo, file sẽ sửa. Chờ tôi đồng ý.
c. Code trên nhánh phase-N-..., commit nhỏ theo Conventional Commits.
d. Tự chạy kiểm thử, viết docs/acceptance/phase-N.md: từng tiêu chí đạt hay chưa, kèm bằng chứng.
e. Mở Pull Request: tóm tắt việc đã làm, việc tôi cần kiểm tra bằng tay, rủi ro còn lại.

Trả lời ngắn gọn bằng tiếng Việt.
```

### 10.2. Prompt giao một giai đoạn

```text
Bắt đầu GĐ <số> — <tên giai đoạn>, theo mục "GĐ <số>" trong docs/SPEC.md.

Tôi đã chuẩn bị:
- <ví dụ: data/faces/ có 3 người: bo, me, minh, mỗi người 8 ảnh>
- <ví dụ: TELEGRAM_* và GEMINI_API_KEY đã điền trong .env>

Quyết định đã chốt ở các giai đoạn trước:
- <ví dụ: Ubuntu 24.04; Gemini Flash-Lite; ngưỡng mặt 0,52>

Yêu cầu:
1. Nhắc lại mục tiêu, các bước và tiêu chí nghiệm thu của giai đoạn này.
2. Liệt kê những gì còn thiếu từ phía tôi.
3. Đưa kế hoạch file sẽ tạo và sửa, chờ tôi đồng ý rồi mới code.
4. Xong thì chạy kiểm thử, viết docs/acceptance/phase-<số>.md, mở Pull Request.
Không làm sang giai đoạn sau.
```

### 10.3. Giới thiệu nhanh cho người làm cùng

```text
Mình đang làm dự án Camera AI Thông Minh cho gia đình: một camera thường + một máy có GPU,
nhận ra người nhà và báo người lạ qua Telegram, nhớ chỗ để chìa khóa, kính, ví,
phát hiện người bị ngã, và trả lời câu hỏi bằng tiếng Việt ("Chìa khóa của tôi đâu?").
Video xử lý hoàn toàn trong nhà, không đưa lên máy chủ ngoài.
Làm theo 8 giai đoạn: test trên máy tính với webcam trước (GĐ 0–6), rồi chuyển sang camera gia đình (GĐ 7).
Công nghệ: Python, Docker, Redis, InsightFace, YOLO26/YOLOE, FastAPI, Gemini, Streamlit.
Tài liệu đầy đủ ở docs/SPEC.md trong repo; mỗi giai đoạn có bước làm, tiêu chí nghiệm thu và điểm duyệt.
```

## 11. Phụ lục

### 11.1. Ba câu hỏi của bản nháp đã được đưa vào đâu

| Câu hỏi trong bản nháp | Trả lời ở đâu |
| --- | --- |
| Phần cứng test hiện tại (GPU, webcam hay camera IP) | Mục 6, dòng 1–2; duyệt sau GĐ 0 |
| Gemini API hay Ollama | Mục 7.1 (Q3) và 9.2 |
| Giữ thứ tự GĐ 1 → GĐ 6 hay đổi | Giữ nguyên, thêm GĐ 7. **\[DUYỆT\]** Nếu nhà có người cao tuổi, có thể làm GĐ 4 (té ngã) trước GĐ 3 |

### 11.2. Thuật ngữ

| Thuật ngữ | Giải thích ngắn |
| --- | --- |
| RTSP | Giao thức truyền video trực tiếp từ camera IP qua mạng, link dạng `rtsp://...` |
| ONVIF | Chuẩn chung để phần mềm làm việc với camera IP của nhiều hãng |
| FPS | Số khung hình mỗi giây |
| Redis | Cơ sở dữ liệu chạy trong RAM, ở đây dùng để chuyền ảnh giữa các service |
| Producer–Consumer | Một bên tạo dữ liệu (đọc camera), nhiều bên dùng dữ liệu (các AI) |
| Docker, Docker Compose | Đóng mỗi service vào một "hộp" riêng, chạy cả hệ thống bằng một lệnh |
| Vector khuôn mặt (embedding) | Dãy 512 số đại diện một khuôn mặt; cùng người thì hai dãy gần nhau |
| Cosine similarity | Độ giống nhau giữa hai vector, càng gần 1 càng giống |
| Ngưỡng | Mốc để quyết định "đủ giống" hay "khác" |
| Cooldown | Thời gian chờ trước khi ghi hoặc báo lại cùng một sự việc |
| Vùng (polygon) | Đa giác vẽ trên ảnh để đặt tên khu vực, ví dụ "Ghế sofa" |
| Điểm khớp (keypoints) | Vị trí vai, hông, gối… do mô hình tư thế ước lượng |
| Open-vocabulary | Nhận diện đồ vật theo từ khóa chữ, không cần train lại |
| Function calling | LLM gọi hàm có sẵn (tra CSDL) thay vì tự đoán câu trả lời |
| STT, TTS | Giọng nói thành chữ, chữ thành giọng nói |
| Heartbeat, health check | Tín hiệu định kỳ cho biết service còn sống |
| WAL | Chế độ ghi của SQLite giúp đọc và ghi cùng lúc ít bị khóa |
| Pull Request | Yêu cầu gộp code của một nhánh vào `main`, để người khác xem và duyệt |

### 11.3. Hướng mở rộng sau bản test

- **Nhiều camera:** đã có `camera_id` ở Redis và mọi bảng, chỉ cần thêm producer cho từng camera.
- **Worker mới dạng plugin:** báo cháy và khói, nhận diện thú cưng, đọc biển số xe ở cổng.
- **Nhà thông minh:** gửi sự kiện qua MQTT sang Home Assistant, ví dụ chủ nhà về buổi tối thì bật đèn.
- **Thiết bị biên:** xuất mô hình sang TensorRT để chạy 24/7 trên Jetson Orin Nano. Lưu ý YOLOE sau khi xuất sẽ cố định danh sách đồ vật, đổi đồ vật phải xuất lại.
- **Chống giả mạo khuôn mặt** nếu sau này dùng để mở cửa.

### 11.4. Nguồn tham khảo

Các trang đã mở khi soạn tài liệu này, ngày 25/11/2026:

- [Ultralytics v8.4.0 — ra mắt YOLO26 và YOLOE-26](https://community.ultralytics.com/t/new-release-ultralytics-v8-4-0/1747)
- [Tài liệu YOLO26 (mô hình pose, giấy phép)](https://docs.ultralytics.com/models/yolo26/)
- [Tài liệu YOLOE (tên mô hình, `set_classes`, giới hạn khi xuất)](https://docs.ultralytics.com/models/yoloe)
- [Danh sách model Gemini API](https://ai.google.dev/gemini-api/docs/models)
- [Điều khoản bổ sung Gemini API](https://ai.google.dev/gemini-api/terms)
- [InsightFace — giấy phép mã nguồn và mô hình](https://github.com/deepinsight/insightface)
- [Tapo — xem camera qua RTSP/ONVIF](https://tapo.com/vn/faqs/how-to-view-tapo-camera-on-pc-nas-or-nvr-using-rtsponvif)
- [Docker Forums — webcam trong container trên Windows](https://forums.docker.com/t/how-to-use-a-host-usb-device-in-a-container-in-docker-desktop/138905)
- [NHNN — triển khai Luật Bảo vệ dữ liệu cá nhân](https://sbv.gov.vn/en/w/tri%E1%BB%83n-khai-thi-h%C3%A0nh-lu%E1%BA%ADt-b%E1%BA%A3o-v%E1%BB%87-d%E1%BB%AF-li%E1%BB%87u-c%C3%A1-nh%C3%A2n-1)
- [Nghị định 356/2025/NĐ-CP](https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Nghi-dinh-356-2025-ND-CP-huong-dan-Luat-Bao-ve-du-lieu-ca-nhan-687428.aspx)
