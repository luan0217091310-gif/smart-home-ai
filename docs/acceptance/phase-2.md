# Biên bản nghiệm thu GĐ 2 — Nhận diện người nhà, cảnh báo người lạ

Ngày: 25/11/2026

## Đã làm

- `scripts/enroll_faces.py`: quét `data/faces/<ten>/`, bỏ ảnh không có mặt / nhiều mặt (liệt kê lý do), vector trung bình đã chuẩn hóa → bảng `members`; in tương đồng cùng người và giữa các người để chọn ngưỡng. Vai trò đọc từ `data/faces/<ten>/role.txt`.
- `services/worker_face`: 3 FPS, bỏ mặt < `min_face_size_px`, so cosine với mọi thành viên, theo dấu bằng IoU (mỗi người một track).
  - ≥ ngưỡng → thành viên, ghi `access_logs` tối đa 1 lần/120 s/người.
  - < ngưỡng 3 khung liên tiếp cùng track → người lạ: lưu ảnh toàn khung có khung mặt + ảnh cắt mặt, ghi `alerts`, gửi Telegram (cooldown 60 s).
  - Ghi mọi lần so khớp vào `data/face_scores.csv` để hiệu chỉnh ngưỡng.
  - Nạp lại thành viên khi `members:version` đổi; nhận yêu cầu đăng ký từ Dashboard qua hàng đợi Redis (dùng ở GĐ 6).
- `tests/test_face.py`: 9 bài (cosine, IoU, 3 khung liên tiếp, reset khi có khung khớp, 2 người tách track, track hết hạn, cỡ mặt).

## Kết quả chạy thử

| Mục | Kết quả |
| --- | --- |
| pytest | 18/18 đạt |
| Mô hình `buffalo_l` | Nạp được; CPU ≈ 350 ms/khung (640×480) — đủ cho 3 FPS |
| worker_face + webcam | Chạy không lỗi; mặt trong cảnh 19 px < 60 px nên **không kết luận** (đúng quy tắc) |

## Nghiệm thu — cần chủ dự án

- [ ] **[CUNG CẤP]** Ảnh 2–3 thành viên vào `data/faces/<ten>/` (5–10 ảnh/người), rồi `python scripts/enroll_faces.py`.
- [ ] Mỗi thành viên vào khung 5 lần: đúng ≥ 4/5, không lần nào bị báo người lạ.
- [ ] Thành viên đứng 5 phút: ≤ 3 dòng log.
- [ ] Người lạ: Telegram nhận ảnh trong 3–5 giây; đứng 3 phút ≤ 3 cảnh báo.
- [ ] Quay lưng / đi xa: không log, không cảnh báo.
- [ ] Hiệu chỉnh ngưỡng từ `data/face_scores.csv` (cột `score` của thành viên và người lạ).

**[LƯU Ý]** Hệ thống chưa chống giả mạo: giơ ảnh thành viên sẽ được nhận là thành viên đó.
