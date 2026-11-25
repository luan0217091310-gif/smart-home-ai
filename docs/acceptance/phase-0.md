# Biên bản nghiệm thu GĐ 0 — Chuẩn bị môi trường

Ngày: 25/11/2026 · Người thực hiện: AI coding agent

## Môi trường đo được

| Mục | Kết quả |
| --- | --- |
| GPU | NVIDIA T1200 Laptop GPU, **4 GB VRAM** |
| Hệ điều hành | Windows 11 Pro (Docker Desktop + WSL2, có runtime `nvidia`) |
| Python | 3.11.0 (venv `.venv`) |
| Docker | 29.9.2 |
| Nguồn video Chặng A | Webcam laptop (`CAMERA_SOURCE=0`), 640×480 |

## Nghiệm thu

- [x] `nvidia-smi` hiển thị đúng GPU trên máy và trong container (`docker run --rm --gpus all ubuntu nvidia-smi` → `NVIDIA T1200 Laptop GPU, 4096 MiB`).
- [x] Đọc được hình từ webcam (`python scripts/check_camera.py` → khung 640×480, lưu `data/camera_check.jpg`).
- [ ] Telegram nhận tin chữ và ảnh — **chờ chủ dự án điền `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` vào `.env`** rồi chạy `python scripts/test_telegram.py`.
- [ ] LLM trả lời 1 câu tiếng Việt — **chờ `GEMINI_API_KEY`**, chạy `python scripts/check_llm.py`.
- [x] `git status` không hiện file nào trong `data/` hoặc `.env` (đã có `.gitignore`).

## Đề xuất cần duyệt

- **Hệ điều hành:** giữ Windows. Theo mục 8 dòng 2, `stream_producer` chạy bằng Python trực tiếp trên Windows (đọc webcam), các service còn lại trong Docker, nối Redis qua `localhost:6379`.
- **LLM:** GPU chỉ có 4 GB VRAM, không đủ cho Ollama 7–8B cùng các mô hình thị giác → **dùng Gemini**.
- **VRAM 4 GB** là điểm nghẽn: InsightFace + YOLOE + YOLO-pose cùng lúc có thể vượt. Đề xuất: Whisper chạy CPU; nếu thiếu VRAM thì cho `worker_object` chạy CPU (nó chỉ quét 4 giây/lần).
- **Repo hiện là Public**, đặc tả đề xuất Private (Q4). Vì repo không chứa dữ liệu cá nhân nên Public vẫn an toàn, nhưng nên cân nhắc chuyển Private.
