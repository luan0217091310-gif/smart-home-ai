# Biên bản nghiệm thu GĐ 5 — Trợ lý ảo (chat và giọng nói)

Ngày: 25/11/2026

## Đã làm

- `services/assistant_api` (FastAPI): `POST /chat`, `POST /voice`, `GET /health`, `GET /image` (chỉ phục vụ ảnh trong `data/snapshots/`, chặn `../`).
- Lớp LLM chung (`llm.py`): **Gemini** (REST function calling, model đặt trong `GEMINI_MODEL`), **Ollama** (`/api/chat` + tools), và **rules** — bộ định tuyến từ khóa offline để demo/kiểm thử khi chưa có khóa. Thiếu `GEMINI_API_KEY` thì tự dùng `rules`.
- System prompt tiếng Việt tách file riêng: `services/assistant_api/prompts/system_vi.txt` (xưng "em", gọi "anh/chị", chèn giờ Việt Nam mỗi lượt, chỉ trả lời từ công cụ).
- 6 công cụ: `get_visitors`, `find_object`, `register_new_object`, `get_recent_alerts`, `list_tracked_objects`, `remove_object`. Không có SQL từ LLM; tham số kiểm tra kiểu và giới hạn; so tên không dấu, không phân biệt hoa thường; thêm đồ vật tăng `objects:version`.
- Telegram bot long polling chạy trong `assistant_api`, chỉ trả lời `TELEGRAM_ALLOWED_CHAT_IDS` (mặc định = `TELEGRAM_CHAT_ID`), tin từ tài khoản khác bị bỏ qua và ghi log. Gửi kèm ảnh đồ vật / cảnh báo.
- Giọng nói (`VOICE_ENABLED=true`): tin thoại → faster-whisper (`language="vi"`, CPU) → chữ → trả lời; edge-tts → ffmpeg OGG/Opus → tin thoại; TTS lỗi vẫn gửi chữ.
- Bộ câu hỏi kiểm thử: `python scripts/eval_assistant.py` trên CSDL giả biết trước.

## Kết quả (LLM = rules, offline)

| Câu hỏi | Trả lời | Đúng |
| --- | --- | --- |
| Nãy giờ có ai vào nhà không? | Có Bố (lần cuối …, cách đây 50 phút). Có 1 lần phát hiện người lạ. | ✅ |
| Chìa khóa của tôi đâu rồi? | Chìa khóa thấy lần cuối ở Bàn làm việc lúc … (cách đây 12 phút). + ảnh | ✅ |
| chia khoa cua toi o dau | (như trên — không dấu vẫn khớp) | ✅ |
| Hãy giúp tôi theo dõi thêm cái mũ bảo hiểm | Đã thêm 'Mũ bảo hiểm' (từ khóa 'helmet') → CSDL có `helmet` | ✅ |
| Hôm nay có cảnh báo gì không? | Có 1 cảnh báo: … phát hiện người lạ | ✅ |
| Cái ô của tôi đâu? | Chưa theo dõi 'ô', gợi ý thêm — không bịa vị trí | ✅ |
| Kính của tôi đâu? | Đang theo dõi Mắt kính nhưng camera chưa thấy | ✅ |

**7/7 đúng**, thời gian trả lời < 0,1 s. `assistant_api` chạy trong Docker, `/health` khỏe, `/chat` trả lời đúng trên CSDL thật.
pytest: 40/40 đạt (gồm kiểm tra chặn công cụ lạ, tham số sai, đường dẫn ảnh `../.env`).

Bằng chứng phụ cho GĐ 1: một container producer thử với đường dẫn video sai chạy ngầm > 5 phút đã tự ghi cảnh báo `system` "Mất kết nối camera cam_test quá 5 phút" — đúng thiết kế.

## Kết quả với Gemini thật (25/11, 23:57)

Bộ 7 câu hỏi: **7/7 đúng**, câu trả lời tự nhiên, xưng "em", không bịa vị trí đồ vật chưa theo dõi.

**Telegram dùng chung bot có sẵn của chủ dự án.** Bot đó đang nhận tin bằng long polling, mà Telegram chỉ cho một chương trình nhận tin trên mỗi token.
Vì vậy `TELEGRAM_BOT_ENABLED=false`: hệ thống camera chỉ **gửi** cảnh báo qua bot này, phần hỏi đáp qua Telegram tạm tắt (hỏi qua tab Trò chuyện của Dashboard).
Muốn hỏi đáp qua Telegram: tạo bot thứ hai bằng @BotFather, đặt token đó vào `TELEGRAM_BOT_TOKEN` và `TELEGRAM_BOT_ENABLED=true`.

## Nghiệm thu — cần chủ dự án

- [ ] **[CUNG CẤP]** `GEMINI_API_KEY` → chạy lại `python scripts/eval_assistant.py` với Gemini, đo thời gian < 5 s.
- [ ] **[CUNG CẤP]** 5–10 câu hỏi mẫu của bạn → ghi vào `my_questions.txt`, chạy `python scripts/eval_assistant.py --questions my_questions.txt`.
- [ ] **[CUNG CẤP]** Bật giọng nói? Giọng nam/nữ? (`VOICE_ENABLED`, `TTS_VOICE`).
- [ ] Tài khoản Telegram lạ nhắn → không được trả lời.
- [ ] Tin nhắn thoại tiếng Việt → chữ + giọng nói.

**[DUYỆT]** Quyền riêng tư Gemini (mục 9.2): bản miễn phí có thể dùng nội dung để cải thiện sản phẩm. Chọn: bật Cloud Billing / dùng Ollama / chấp nhận.
