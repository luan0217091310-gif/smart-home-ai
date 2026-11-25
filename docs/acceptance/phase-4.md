# Biên bản nghiệm thu GĐ 4 — Phát hiện té ngã

Ngày: 25/11/2026

## Đã làm

- Producer đọc được file video và phát lặp (`CAMERA_SOURCE=data/test_videos/nga_01.mp4`).
- `services/worker_fall`: YOLO26-pose + `track(persist=True)` (mỗi người một ID), bỏ điểm khớp < 0,5.
- Chuỗi trạng thái Bình thường → Đang ngã → Đang nằm → Xác nhận (`services/worker_fall/logic.py`):
  1. Vận tốc rơi của trung điểm vai–hông: **Y TĂNG** là đi xuống (sửa lỗi bản nháp), chia cho chiều cao người lúc đứng, tính theo `ts` thật của khung.
  2. Trong 2 s: rộng/cao > 1,2 **hoặc** thân nghiêng > 60°.
  3. Hông không thuộc vùng `safe_rest`, điểm khớp gần như đứng yên 4 s (đo so với điểm mốc).
  - Đứng dậy trước 4 s → huỷ. Xác nhận → `alerts` loại `fall`, Telegram khẩn kèm ảnh, cooldown 60 s/người.
- `scripts/eval_fall_videos.py`: chạy bộ video `data/test_videos/{fall,normal}/`, in bảng đúng/sai và tốc độ rơi lớn nhất từng video để chọn `drop_speed_threshold`.

## Kết quả kiểm thử tự động (`tests/test_fall.py`, 9 bài, đều đạt)

| Kịch bản giả lập | Kết quả |
| --- | --- |
| Ngã nhanh, nằm yên 6 s | Báo đúng 1 lần, ~4 s sau khi nằm |
| Từ từ nằm xuống sàn trong 4 s | Không báo |
| Ngã rồi đứng dậy trong 1,5 s | Không báo |
| Ngã lên vùng `safe_rest` (sofa) | Không báo |
| Ngồi phịch xuống | Không báo |
| Nằm nhưng còn cử động | Chỉ báo sau khi đứng yên đủ 4 s |
| Mất khung trong lúc ngã | Vẫn tính đúng theo `ts` |
| Người bị che nửa dưới, hông lúc thấy lúc mất | Không báo |

worker_fall chạy thật trong Docker (GPU) với webcam đặt trong quán cà phê: nạp `yolo26n-pose.pt`, theo dấu người, healthy.

**Ca báo nhầm thật (22:47, 25/11) và cách sửa.** Một khách ngồi sau lưng ghế sofa, chỉ thấy đầu–vai, bị xác nhận "ngã".
Nguyên nhân: (1) điểm hông lúc thấy lúc mất làm trung điểm vai–hông nhảy xuống → giả "vận tốc rơi"; (2) chiều cao người
đo từ khung bao bị cắt nên rất nhỏ → vận tốc chuẩn hóa bị phóng đại; (3) khung bao bè ngang được coi là "nằm".
Đã sửa: chỉ dùng trung điểm khi thấy **cả vai lẫn hông**; chỉ đo chiều cao khi **thấy thân dưới** (gối/cổ chân);
khung bao bè ngang chỉ tính là nằm khi **thân nghiêng > 30°**. Thêm bài kiểm thử hồi quy
`test_occluded_person_behind_sofa_no_alarm` (thất bại với code cũ, đạt với code mới). Cảnh báo đó đã đánh dấu `false_alarm`.

`drop_speed_threshold` tạm đặt **0,8 chiều cao người/giây** — phải hiệu chỉnh bằng video thật.

## Nghiệm thu — cần chủ dự án

- [ ] **[CUNG CẤP]** Người diễn thử + nệm; quay 10 video ngã và 10 video dễ nhầm vào `data/test_videos/fall/` và `normal/`.
- [ ] `docker compose run --rm worker_fall python scripts/eval_fall_videos.py` → bắt ≥ 9/10, báo nhầm 0/10.
- [ ] Người nhận cảnh báo té ngã (chỉ bạn hay nhóm gia đình — đổi `TELEGRAM_CHAT_ID` thành ID nhóm).
- [ ] Âm thanh tại chỗ: đề xuất phát trên trình duyệt đang mở Dashboard (đã làm ở GĐ 6).

**[LƯU Ý]** Người quỵ xuống từ từ (trượt theo tường) có thể không qua lớp 1.
