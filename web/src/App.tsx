import { useEffect } from "react";
import { Demo } from "./Demo";

const REPO = "https://github.com/luan0217091310-gif/smart-home-ai";

const FEATURES = [
  { icon: "☺", color: "green", title: "Nhận diện người nhà", q: "“Ai vừa vào nhà? Có người lạ không?”",
    text: "InsightFace so khuôn mặt với thành viên đã đăng ký. Người lạ 3 khung liên tiếp → ảnh gửi Telegram trong vài giây, có chống spam." },
  { icon: "⌖", color: "blue", title: "Nhớ chỗ để đồ", q: "“Điện thoại của tôi đâu rồi?”",
    text: "YOLOE-26 tìm đồ vật theo từ khóa, gán vào vùng trong phòng (bàn, sofa…). Thêm đồ vật mới bằng một câu nói, không cần train lại." },
  { icon: "⚠", color: "red", title: "Phát hiện té ngã", q: "“Có ai ngã mà không dậy được không?”",
    text: "YOLO26-pose + bộ lọc 3 lớp: vận tốc rơi, tư thế nằm, bất động 4 giây ngoài vùng nghỉ. Ngồi, cúi, nằm sofa không báo." },
  { icon: "✦", color: "violet", title: "Trợ lý tiếng Việt", q: "“Chụp ảnh nhà hiện tại cho tôi”",
    text: "Gemini gọi công cụ tra CSDL — không tự viết SQL, không bịa. Hỏi qua Dashboard, Telegram hoặc tin nhắn thoại." },
];

const PIPE = [
  { k: "Camera", v: "Webcam · RTSP · file" },
  { k: "stream_producer", v: "Chỉ giữ khung mới nhất" },
  { k: "Redis", v: "frame:{cam}:latest" },
];
const WORKERS = [
  { k: "worker_face", v: "InsightFace · 3 FPS" },
  { k: "worker_object", v: "YOLOE-26 · 4 s" },
  { k: "worker_fall", v: "YOLO26-pose · 15 FPS" },
];

const PHASES = [
  ["GĐ 0", "Chuẩn bị môi trường", "GPU, Docker, webcam, Telegram, Gemini"],
  ["GĐ 1", "Khung xương & luồng video", "Redis, SQLite WAL, tự nối lại camera"],
  ["GĐ 2", "Người nhà & người lạ", "Theo dấu IoU, ngưỡng 2 mức"],
  ["GĐ 3", "Đồ vật theo vùng", "Nạp nóng, chống nhảy vùng"],
  ["GĐ 4", "Té ngã", "Chuỗi trạng thái 3 lớp"],
  ["GĐ 5", "Trợ lý ảo", "Function calling, giọng nói"],
  ["GĐ 6", "Dashboard & đóng gói", "Một lệnh docker compose up"],
  ["GĐ 7", "Camera gia đình", "Chỉ đổi .env sang RTSP"],
];

const STACK = ["Python 3.11", "Docker Compose", "Redis 7", "SQLite WAL", "OpenCV", "InsightFace", "YOLOE-26", "YOLO26-pose", "FastAPI", "Gemini", "Streamlit", "Telegram Bot", "faster-whisper", "React + Vite"];

const STATS = [
  ["15 FPS", "luồng video"],
  ["~25 ms", "độ trễ hệ thống"],
  ["47", "bài kiểm thử tự động"],
  ["0", "byte video rời khỏi nhà"],
];

export default function App() {
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && e.target.classList.add("in")), { threshold: 0.12 });
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <>
      <div className="bg-grid" aria-hidden />
      <header className="nav">
        <a href="#top" className="brand"><img src="/favicon.svg" alt="" />Camera AI <span>Thông Minh</span></a>
        <nav>
          <a href="#features">Tính năng</a>
          <a href="#demo-section">Demo</a>
          <a href="#architecture">Kiến trúc</a>
          <a href="#roadmap">Lộ trình</a>
          <a href="#privacy">Riêng tư</a>
        </nav>
        <a className="btn small" href={REPO} target="_blank" rel="noreferrer">GitHub ↗</a>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow"><i />Chạy 100% trong nhà · Không gửi video ra ngoài</span>
            <h1>Biến camera thường thành <em>người trông nhà</em> có AI</h1>
            <p className="lead">Nhận ra người nhà, báo người lạ qua Telegram, nhớ chỗ bạn để điện thoại, phát hiện té ngã — và trả lời mọi câu hỏi bằng tiếng Việt.</p>
            <div className="cta">
              <a className="btn" href="#demo-section">Dùng thử demo</a>
              <a className="btn ghost-btn" href={REPO} target="_blank" rel="noreferrer">Xem mã nguồn</a>
            </div>
            <div className="hero-stats">
              {STATS.map(([n, l]) => <div key={l}><b>{n}</b><small>{l}</small></div>)}
            </div>
          </div>
          <div className="hero-visual">
            <div className="bubble b1"><span className="chip warn">Telegram</span> Phát hiện người lạ lúc 20:31:05</div>
            <div className="bubble b2"><b>Bạn:</b> Điện thoại của tôi đâu?<br /><b>Trợ lý:</b> Ở Bàn làm việc, 3 phút trước.</div>
            <div className="orb" />
          </div>
        </section>

        <section id="features" className="section">
          <div className="sec-head reveal">
            <span className="kicker">4 tính năng cốt lõi</span>
            <h2>Một camera, bốn “con mắt” AI</h2>
          </div>
          <div className="features">
            {FEATURES.map((f) => (
              <article key={f.title} className={`feature reveal ${f.color}`}>
                <div className="f-ico">{f.icon}</div>
                <h3>{f.title}</h3>
                <p className="q">{f.q}</p>
                <p>{f.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="demo-section" className="section">
          <div className="sec-head reveal">
            <span className="kicker">Dashboard tương tác</span>
            <h2>Thử ngay — không cần cài đặt</h2>
            <p>Bản demo chạy bằng dữ liệu mẫu ngay trong trình duyệt. Bấm <b>“Chế độ demo”</b> để nối với máy chủ thật trong nhà bạn.</p>
          </div>
          <div className="reveal"><Demo /></div>
        </section>

        <section id="architecture" className="section">
          <div className="sec-head reveal">
            <span className="kicker">Kiến trúc Producer–Consumer</span>
            <h2>Đọc camera một lần, mỗi AI chạy theo nhịp riêng</h2>
            <p>Worker chậm chỉ bỏ qua khung cũ — không làm chậm camera hay worker khác. Một service lỗi, Docker tự bật lại.</p>
          </div>
          <div className="arch reveal">
            <div className="lane">
              {PIPE.map((p, i) => (
                <div key={p.k} className="node-wrap">
                  <div className={`node ${i === 2 ? "hub" : ""}`}><b className="mono">{p.k}</b><small>{p.v}</small></div>
                  {i < PIPE.length - 1 && <div className="arrow" />}
                </div>
              ))}
            </div>
            <div className="fan" />
            <div className="lane workers">
              {WORKERS.map((w) => <div key={w.k} className="node"><b className="mono">{w.k}</b><small>{w.v}</small></div>)}
            </div>
            <div className="fan" />
            <div className="lane">
              <div className="node db"><b className="mono">SQLite</b><small>5 bảng · WAL</small></div>
              <div className="arrow" />
              <div className="node"><b className="mono">assistant_api</b><small>FastAPI · Gemini</small></div>
              <div className="arrow" />
              <div className="node out"><b>Telegram · Dashboard</b><small>Cảnh báo & hỏi đáp</small></div>
            </div>
          </div>
        </section>

        <section id="roadmap" className="section">
          <div className="sec-head reveal">
            <span className="kicker">Lộ trình 8 giai đoạn</span>
            <h2>Từ webcam trên bàn đến camera cả nhà</h2>
          </div>
          <ol className="timeline">
            {PHASES.map(([n, t, d], i) => (
              <li key={n} className="reveal" style={{ transitionDelay: `${i * 40}ms` }}>
                <span className="mono ph">{n}</span>
                <div><b>{t}</b><small>{d}</small></div>
              </li>
            ))}
          </ol>
        </section>

        <section className="section">
          <div className="sec-head reveal"><span className="kicker">Công nghệ</span><h2>Ghép từ những mảnh tốt nhất</h2></div>
          <div className="stack reveal">{STACK.map((s) => <span key={s}>{s}</span>)}</div>
        </section>

        <section id="privacy" className="section">
          <div className="privacy reveal">
            <div>
              <span className="kicker">Quyền riêng tư</span>
              <h2>Hình ảnh ở lại trong nhà bạn</h2>
              <p>Video chỉ nằm trong RAM. Khuôn mặt, ảnh chụp, CSDL không bao giờ lên GitHub. Chỉ ảnh cảnh báo (Telegram) và chữ câu hỏi (Gemini) rời khỏi nhà — muốn tuyệt đối riêng tư thì dùng Ollama chạy trên máy.</p>
              <ul className="checks">
                <li>Không mở cổng nào ra Internet</li>
                <li>Bot Telegram chỉ trả lời tài khoản được phép</li>
                <li>Hỏi ý kiến từng thành viên trước khi đăng ký khuôn mặt</li>
                <li>Tự xóa ảnh sau 30 ngày, nhật ký sau 90 ngày</li>
              </ul>
            </div>
            <pre className="code mono">{`# Bật cả hệ thống
git clone ${REPO}.git
cd smart-home-ai
cp .env.example .env
docker compose up -d

# Chuyển sang camera IP: chỉ sửa .env
CAMERA_SOURCE=rtsp://user:pass@192.168.1.50:554/stream2`}</pre>
          </div>
        </section>
      </main>

      <footer>
        <span>© {new Date().getFullYear()} smart-home-ai · Dự án cá nhân, phi thương mại</span>
        <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
      </footer>
    </>
  );
}
