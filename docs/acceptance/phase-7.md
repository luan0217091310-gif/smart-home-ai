# Biên bản nghiệm thu GĐ 7 — Camera gia đình (Chặng B)

> Mẫu để chủ dự án điền khi triển khai. Phần code đã sẵn sàng: chỉ cần sửa `.env`.

## Đã chuẩn bị sẵn (code)

- Chuyển nguồn chỉ bằng `.env`: `CAMERA_ID=cam_phongkhach`, `CAMERA_SOURCE=rtsp://<user>:<pass>@<IP>:554/stream2`. RTSP ép TCP, mật khẩu được che trong log (`rtsp://***@…`).
- Tự nối lại 1 → 30 s; mất > 5 phút → cảnh báo `system` (đã kiểm chứng ở GĐ 1–5) và tin "đã kết nối lại".
- `scripts/capture_faces.py`: chụp 5–10 ảnh mặt tốt nhất, đa dạng góc, từ chính camera mới rồi đăng ký lại.
- Dashboard nút **Báo giả** để đếm tỷ lệ báo giả; `face_scores.csv` để hiệu chỉnh ngưỡng ngày/đêm.

## 7.1 Kiểm tra camera

| Mục | Kết quả |
| --- | --- |
| Hãng / model / cắm điện hay pin | |
| Hỗ trợ RTSP | |
| Mở bằng VLC trên máy chủ | |
| Luồng dùng (`stream1` nét / `stream2` nhẹ) | |
| Cỡ mặt ở khoảng cách thật (px) | |

## 7.2 Mạng và bảo mật

- [ ] IP cố định (DHCP reservation) cho camera và máy chủ
- [ ] Đổi mật khẩu mặc định, cập nhật firmware
- [ ] Không port-forward camera/Dashboard

## 7.4 Hiệu chỉnh lại

| Mục | Ban ngày | Ban đêm (hồng ngoại) |
| --- | --- | --- |
| Ngưỡng mặt đề xuất | | |
| Tỷ lệ nhận đúng thành viên | | |
| Ngã diễn lại trên nệm (bắt / tổng) | | — |
| Từ khóa đồ vật còn dùng được | | |

## 7.5 Nhật ký 72 giờ

| Ngày | Cảnh báo người lạ | Báo giả người lạ | Báo té ngã | Báo giả té ngã | Mất kết nối camera | RAM | VRAM | Nhiệt GPU | Ổ trống |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |

## Nghiệm thu

- [ ] RTSP mở được bằng VLC và `view_stream.py`
- [ ] Chạy với camera mới chỉ bằng sửa `.env`
- [ ] Rút điện camera 2 phút → tự nối lại; > 5 phút → cảnh báo `system`
- [ ] Mỗi tính năng GĐ 2–5 đạt ≥ 1 kịch bản ở góc mới
- [ ] Ban đêm: không hàng loạt báo giả người lạ
- [ ] 72 giờ: không service nào dừng hẳn; báo giả người lạ ≤ 2/ngày; 0 báo giả té ngã
- [ ] 4G ngoài nhà: không vào được Dashboard/camera, Telegram vẫn hoạt động
