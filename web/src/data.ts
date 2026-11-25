// Dữ liệu MẪU cho bản demo công khai — không phải dữ liệu thật của gia đình nào.
export type AlertType = "stranger" | "fall" | "system";
export type AlertStatus = "new" | "sent" | "acknowledged" | "false_alarm";

export interface Alert {
  id: number;
  type: AlertType;
  message: string;
  minutesAgo: number;
  status: AlertStatus;
}

export interface Member {
  name: string;
  role: "owner" | "family" | "guest";
  images: number;
  lastSeenMin: number;
}

export interface TrackedObject {
  name: string;
  keyword: string;
  zone: string | null;
  lastSeenMin: number | null;
  confidence: number;
  active: boolean;
}

export const SERVICES = [
  { id: "stream_producer", label: "Đọc camera", fps: "15 FPS" },
  { id: "worker_face", label: "Nhận diện mặt", fps: "3 FPS" },
  { id: "worker_object", label: "Tìm đồ vật", fps: "4 s/lần" },
  { id: "worker_fall", label: "Phát hiện té ngã", fps: "15 FPS" },
  { id: "assistant_api", label: "Trợ lý AI", fps: "theo yêu cầu" },
  { id: "redis", label: "Redis", fps: "RAM" },
];

export const initialAlerts: Alert[] = [
  { id: 4, type: "stranger", message: "Phát hiện người lạ ở cửa chính (độ tương đồng 0,12)", minutesAgo: 18, status: "sent" },
  { id: 3, type: "system", message: "Camera mất kết nối 6 phút, đã tự nối lại", minutesAgo: 140, status: "acknowledged" },
  { id: 2, type: "fall", message: "KHẨN: người té ngã và nằm yên ở phòng khách (diễn tập)", minutesAgo: 1500, status: "false_alarm" },
  { id: 1, type: "stranger", message: "Phát hiện người lạ (shipper giao hàng)", minutesAgo: 2900, status: "acknowledged" },
];

export const members: Member[] = [
  { name: "Bố", role: "owner", images: 9, lastSeenMin: 42 },
  { name: "Mẹ", role: "family", images: 8, lastSeenMin: 95 },
  { name: "Bé Na", role: "family", images: 10, lastSeenMin: 7 },
];

export const initialObjects: TrackedObject[] = [
  { name: "Điện thoại", keyword: "cell phone", zone: "Bàn làm việc", lastSeenMin: 3, confidence: 0.71, active: true },
  { name: "Chìa khóa", keyword: "keys", zone: "Kệ cửa ra vào", lastSeenMin: 64, confidence: 0.48, active: true },
  { name: "Mắt kính", keyword: "glasses", zone: "Ghế sofa", lastSeenMin: 210, confidence: 0.55, active: true },
  { name: "Ví tiền", keyword: "wallet", zone: null, lastSeenMin: null, confidence: 0, active: true },
];

export const accessLog = [
  { time: "21:42", name: "Bé Na", score: 0.81 },
  { time: "21:18", name: "Bố", score: 0.74 },
  { time: "20:55", name: "Người lạ", score: 0.12 },
  { time: "19:47", name: "Mẹ", score: 0.69 },
  { time: "18:03", name: "Bố", score: 0.77 },
];

export function ago(min: number | null): string {
  if (min === null) return "chưa từng thấy";
  if (min < 1) return "vừa xong";
  if (min < 60) return `${min} phút trước`;
  if (min < 1440) return `${Math.floor(min / 60)} giờ ${min % 60} phút trước`;
  return `${Math.floor(min / 1440)} ngày trước`;
}

export function fold(s: string): string {
  return s
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();
}
