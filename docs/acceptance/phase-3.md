# Biên bản nghiệm thu GĐ 3 — Đồ vật và vị trí theo vùng

Ngày: 25/11/2026

## Đã làm

- `scripts/draw_zones.py`: click vẽ đa giác, nhập tên + loại vùng, lưu `data/zones.json` (tọa độ 0–1) và `data/zones_preview.jpg`. `--preview` chỉ xuất ảnh tô vùng. Cần `opencv-python` bản có GUI.
- `shared/zones.py`: `find_zone(x, y)` bằng `cv2.pointPolygonTest`, điểm thuộc nhiều vùng → vùng nhỏ nhất; `zones.json` là gốc, đồng bộ vào bảng `zones` khi khởi động và khi file đổi.
- `services/worker_object`: mỗi 4 s, YOLOE-26 (`set_classes()` theo từ khóa tiếng Anh; dự phòng YOLO-World), tâm khung bao → vùng, ghi `last_zone/last_seen_at/last_confidence` + ảnh cắt mới nhất; không thấy → giữ vị trí cũ; ngoài vùng → "Ngoài các vùng đã đặt tên".
- Chống nhảy vùng: chỉ đổi vùng khi thấy ở vùng mới 2 chu kỳ liên tiếp.
- Nạp nóng: `objects:version` đổi → đọc lại bảng, gọi lại `set_classes()`.
- Danh sách ban đầu (`settings.yaml`): Chìa khóa/keys, Mắt kính/glasses, Ví tiền/wallet.
- Mô hình và bộ mã hóa chữ tải vào `models/` (gắn vào container) để không tải lại.
- Mẫu vùng: `config/zones.example.json` (3 vùng theo đặc tả).

## Kết quả

| Mục | Kết quả |
| --- | --- |
| pytest (vùng nhỏ nhất, chống nhảy vùng, lọc độ tin cậy, nạp nóng) | đạt |
| Ảnh tô vùng mẫu | `data/zones_preview.jpg` tạo được |

**[LƯU Ý]** Trên máy này PyTorch bị **Windows Application Control (Smart App Control)** chặn nạp DLL, nên YOLO chỉ chạy trong Docker (image `worker_object`, `worker_fall`).

## Nghiệm thu — cần chủ dự án

- [ ] **[CUNG CẤP]** Ảnh tĩnh đúng góc camera (`python scripts/view_stream.py --snapshot`), danh sách vùng, vẽ bằng `draw_zones.py`.
- [ ] **[CUNG CẤP]** 3–5 đồ vật thật để thử, tên tiếng Việt + từ khóa tiếng Anh.
- [ ] Đặt kính/ví lên bàn → CSDL ghi "Bàn làm việc", lệch ≤ 1 chu kỳ.
- [ ] Chuyển sang sofa → `last_zone` = "Ghế sofa".
- [ ] Thêm `cup` → Cốc nước khi đang chạy (Dashboard hoặc trợ lý) → nhận ở chu kỳ kế tiếp.
- [ ] Mỗi đồ vật đặt thử 10 lần, đúng ≥ 7/10.
