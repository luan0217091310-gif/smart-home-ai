import { CtaBand } from "../Layout";
import { LiveFeed } from "../LiveFeed";
import { Link } from "../router";

export const FEATURES = [
  { id: "nguoi-nha", icon: "face", color: "green", title: "Nhận diện người nhà", q: "Ai vừa vào nhà? Có người lạ không?",
    text: "So khuôn mặt với thành viên đã đăng ký. Người lạ → ảnh gửi Telegram trong vài giây." },
  { id: "do-vat", icon: "target", color: "blue", title: "Nhớ chỗ để đồ", q: "Điện thoại của tôi đâu rồi?",
    text: "Tìm đồ vật theo từ khóa, nhớ vùng và thời điểm thấy lần cuối. Thêm đồ mới không cần train." },
  { id: "te-nga", icon: "alert", color: "red", title: "Phát hiện té ngã", q: "Có ai ngã mà không dậy được không?",
    text: "Bộ lọc 3 lớp: vận tốc rơi, tư thế nằm, bất động. Ngồi, cúi, nằm sofa không báo." },
  { id: "tro-ly", icon: "spark", color: "violet", title: "Trợ lý tiếng Việt", q: "Chụp ảnh nhà hiện tại cho tôi",
    text: "Hỏi bằng chữ hoặc giọng nói qua Dashboard, Telegram. Chỉ trả lời từ dữ liệu thật." },
] as const;

export function Icon({ name }: { name: string }) {
  const p = { fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden>
      {name === "face" && <g {...p}><circle cx="12" cy="12" r="9" /><path d="M9 10h.01M15 10h.01M8.5 15a4.5 4.5 0 0 0 7 0" /></g>}
      {name === "target" && <g {...p}><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3M2 12h3M19 12h3" /></g>}
      {name === "alert" && <g {...p}><path d="M12 3 2.5 20h19z" /><path d="M12 10v4M12 17h.01" /></g>}
      {name === "spark" && <g {...p}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" /></g>}
      {name === "cam" && <g {...p}><rect x="3" y="6" width="13" height="12" rx="2" /><path d="m16 10 5-3v10l-5-3" /></g>}
      {name === "cpu" && <g {...p}><rect x="6" y="6" width="12" height="12" rx="2" /><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4" /></g>}
      {name === "bell" && <g {...p}><path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z" /><path d="M10 21h4" /></g>}
      {name === "lock" && <g {...p}><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 1 1 8 0v3" /></g>}
    </svg>
  );
}

const STEPS = [
  { icon: "cam", title: "Camera bất kỳ", text: "Webcam USB hoặc camera IP có RTSP (Tapo, Imou, Ezviz, Hikvision…)." },
  { icon: "cpu", title: "AI chạy trong nhà", text: "Một máy có GPU NVIDIA xử lý toàn bộ hình ảnh. Video không rời khỏi nhà." },
  { icon: "bell", title: "Báo & trả lời", text: "Cảnh báo qua Telegram, hỏi đáp tiếng Việt qua Dashboard hoặc tin nhắn." },
];

const STATS = [["15 FPS", "luồng video"], ["~25 ms", "độ trễ xử lý"], ["47", "bài kiểm thử tự động"], ["0 byte", "video rời khỏi nhà"]];

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow"><i />Mã nguồn mở · Chạy 100% trong nhà</span>
          <h1>Camera thường,<br /><em>trí tuệ người trông nhà.</em></h1>
          <p className="lead">Nhận ra người nhà, báo người lạ, nhớ chỗ bạn để đồ, phát hiện té ngã — và trả lời mọi câu hỏi bằng tiếng Việt. Không cần mua camera đắt tiền.</p>
          <div className="cta-row">
            <Link to="/demo" className="btn">Dùng thử demo →</Link>
            <Link to="/tinh-nang" className="btn ghost-btn">Xem tính năng</Link>
          </div>
          <ul className="hero-points">
            <li>Không phí thuê bao</li><li>Không gửi video lên mây</li><li>Đổi camera chỉ cần sửa 1 dòng</li>
          </ul>
        </div>
        <div className="hero-visual">
          <div className="device">
            <LiveFeed />
          </div>
          <div className="float f1"><span className="dot red" />Người lạ ở cửa chính · 20:31:05<small>Đã gửi ảnh qua Telegram</small></div>
          <div className="float f2"><b>“Điện thoại của tôi đâu?”</b><small>→ Bàn làm việc, 3 phút trước</small></div>
        </div>
      </section>

      <section className="stats-row reveal">
        {STATS.map(([n, l]) => <div key={l}><b>{n}</b><small>{l}</small></div>)}
      </section>

      <section className="section">
        <div className="sec-head center reveal">
          <span className="kicker">Tính năng</span>
          <h2>Một camera, bốn “con mắt” AI</h2>
          <p>Mỗi tính năng là một service riêng chạy theo nhịp riêng — một phần lỗi, phần khác vẫn chạy.</p>
        </div>
        <div className="features">
          {FEATURES.map((f) => (
            <Link key={f.id} to={`/tinh-nang#${f.id}`} className={`feature reveal ${f.color}`}>
              <div className="f-ico"><Icon name={f.icon} /></div>
              <h3>{f.title}</h3>
              <p className="q">“{f.q}”</p>
              <p>{f.text}</p>
              <span className="more">Chi tiết →</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="sec-head center reveal">
          <span className="kicker">Cách hoạt động</span>
          <h2>Ba bước, không cần đám mây</h2>
        </div>
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li key={s.title} className="reveal">
              <span className="step-n">{i + 1}</span>
              <div className="f-ico"><Icon name={s.icon} /></div>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="section split reveal">
        <div>
          <span className="kicker">Trợ lý ảo</span>
          <h2>Hỏi nhà bạn như hỏi người thân</h2>
          <p className="muted">Trợ lý dùng Gemini gọi các công cụ tra cứu dữ liệu thật — không tự viết SQL, không bịa. Đồ vật chưa theo dõi thì nói chưa biết và gợi ý thêm.</p>
          <Link to="/demo" className="btn ghost-btn">Thử hỏi trợ lý →</Link>
        </div>
        <div className="chat-preview">
          <div className="msg user"><p>Nãy giờ có ai vào nhà không?</p></div>
          <div className="msg bot"><p>Dạ, có Bé Na lúc 21:42 và Bố lúc 21:18. Có 1 lần phát hiện người lạ lúc 20:55.</p><small className="mono">⚙ get_visitors</small></div>
          <div className="msg user"><p>chia khoa cua toi o dau</p></div>
          <div className="msg bot"><p>Dạ, chìa khóa thấy lần cuối ở Kệ cửa ra vào, 1 giờ 4 phút trước.</p><small className="mono">⚙ find_object</small></div>
          <div className="msg user"><p>Theo dõi thêm cái mũ bảo hiểm</p></div>
          <div className="msg bot"><p>Dạ, em đã thêm “Mũ bảo hiểm” (helmet). Camera sẽ tìm ở chu kỳ tới.</p><small className="mono">⚙ register_new_object</small></div>
        </div>
      </section>

      <CtaBand />
    </>
  );
}
