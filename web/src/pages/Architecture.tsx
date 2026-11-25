import { CtaBand, PageHero } from "../Layout";

const SERVICES = [
  ["stream_producer", "Đọc webcam/RTSP, tự nối lại, nén JPEG", "15–20 FPS"],
  ["worker_face", "Phát hiện & nhận diện khuôn mặt", "2–3 FPS"],
  ["worker_object", "Tìm đồ vật theo từ khóa, xác định vùng", "4 giây/lần"],
  ["worker_fall", "Ước lượng tư thế, phát hiện té ngã", "10–15 FPS"],
  ["assistant_api", "Chat, giọng nói, LLM gọi công cụ CSDL", "Theo yêu cầu"],
  ["dashboard", "Giao diện quản lý trên trình duyệt", "Theo yêu cầu"],
  ["redis", "Bộ đệm khung hình mới nhất trong RAM", "—"],
];

const PRINCIPLES = [
  ["Chỉ khung mới nhất", "Worker chậm bỏ qua khung cũ, không bao giờ xếp hàng làm đầy bộ nhớ."],
  ["Cấu hình, không viết cứng", "Nguồn camera, ngưỡng, khóa API nằm trong .env và settings.yaml."],
  ["Tự phục hồi", "Docker tự bật lại service lỗi; mỗi service có health check và heartbeat."],
  ["Đổi mô hình dễ", "Mô hình AI bọc sau một lớp chung — đổi bằng một biến môi trường."],
];

const STACK = [
  ["Hạ tầng", ["Python 3.11", "Docker Compose", "Redis 7", "SQLite WAL"]],
  ["Thị giác", ["OpenCV", "InsightFace", "YOLOE-26", "YOLO26-pose"]],
  ["Trợ lý", ["FastAPI", "Gemini", "Ollama", "faster-whisper", "edge-tts"]],
  ["Giao diện", ["Streamlit", "Telegram Bot", "React + Vite"]],
] as const;

const PHASES = [
  ["GĐ 0", "Chuẩn bị môi trường", "GPU, Docker, webcam, Telegram, Gemini", true],
  ["GĐ 1", "Khung xương & luồng video", "Redis, SQLite WAL, tự nối lại", true],
  ["GĐ 2", "Người nhà & người lạ", "Theo dấu IoU, ngưỡng 2 mức", true],
  ["GĐ 3", "Đồ vật theo vùng", "Nạp nóng, chống nhảy vùng", true],
  ["GĐ 4", "Té ngã", "Chuỗi trạng thái 3 lớp", true],
  ["GĐ 5", "Trợ lý ảo", "Function calling, giọng nói", true],
  ["GĐ 6", "Dashboard & đóng gói", "Một lệnh docker compose", true],
  ["GĐ 7", "Camera gia đình", "Đổi .env sang RTSP, chạy 72 giờ", false],
] as const;

export default function Architecture() {
  return (
    <>
      <PageHero kicker="Kiến trúc" title={<>Đọc camera một lần,<br /><em>mỗi AI một nhịp riêng.</em></>}>
        Kiến trúc Producer–Consumer quanh Redis: thêm tính năng mới chỉ là thêm một service, một service lỗi không kéo cả hệ thống dừng theo.
      </PageHero>

      <section className="arch reveal" aria-label="Sơ đồ kiến trúc">
        <div className="lane">
          <Node k="Camera" v="Webcam · RTSP · video" />
          <Arrow />
          <Node k="stream_producer" v="Chỉ giữ khung mới nhất" />
          <Arrow />
          <Node k="Redis" v="frame:{cam}:latest" cls="hub" />
        </div>
        <div className="fan" />
        <div className="lane workers">
          <Node k="worker_face" v="InsightFace · 3 FPS" />
          <Node k="worker_object" v="YOLOE-26 · 4 s" />
          <Node k="worker_fall" v="YOLO26-pose · 15 FPS" />
        </div>
        <div className="fan" />
        <div className="lane">
          <Node k="SQLite" v="5 bảng · WAL" cls="db" />
          <Arrow />
          <Node k="assistant_api" v="FastAPI · Gemini" />
          <Arrow />
          <Node k="Telegram · Dashboard" v="Cảnh báo & hỏi đáp" cls="out" />
        </div>
      </section>

      <section className="section">
        <div className="sec-head reveal"><span className="kicker">Các service</span><h2>Bảy khối, mỗi khối một việc</h2></div>
        <div className="table-wrap reveal">
          <table className="svc-table">
            <thead><tr><th>Service</th><th>Nhiệm vụ</th><th>Nhịp xử lý</th></tr></thead>
            <tbody>{SERVICES.map(([a, b, c]) => <tr key={a}><td className="mono">{a}</td><td>{b}</td><td>{c}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="section">
        <div className="sec-head reveal"><span className="kicker">Nguyên tắc thiết kế</span><h2>Ổn định trước, thông minh sau</h2></div>
        <div className="mini-grid">{PRINCIPLES.map(([t, d]) => <div key={t} className="mini reveal"><h3>{t}</h3><p>{d}</p></div>)}</div>
      </section>

      <section className="section">
        <div className="sec-head reveal"><span className="kicker">Công nghệ</span><h2>Ghép từ những mảnh tốt nhất</h2></div>
        <div className="stack-groups reveal">
          {STACK.map(([g, items]) => <div key={g}><h4>{g}</h4><div className="stack">{items.map((s) => <span key={s}>{s}</span>)}</div></div>)}
        </div>
      </section>

      <section className="section">
        <div className="sec-head reveal"><span className="kicker">Lộ trình</span><h2>Tám giai đoạn, mỗi giai đoạn một điểm duyệt</h2></div>
        <ol className="timeline">
          {PHASES.map(([n, t, d, done]) => (
            <li key={n} className={`reveal ${done ? "done" : ""}`}>
              <span className="mono ph">{n}</span>
              <div><b>{t}</b><small>{d}</small></div>
              <span className={`state ${done ? "ok" : ""}`}>{done ? "Đã có code" : "Chờ camera"}</span>
            </li>
          ))}
        </ol>
      </section>
      <CtaBand />
    </>
  );
}

function Node({ k, v, cls = "" }: { k: string; v: string; cls?: string }) {
  return <div className={`node ${cls}`}><b className="mono">{k}</b><small>{v}</small></div>;
}
function Arrow() {
  return <div className="arrow" aria-hidden />;
}
