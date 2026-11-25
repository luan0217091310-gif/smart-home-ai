import type { ReactNode } from "react";
import { CtaBand } from "../Layout";
import { LiveFeed } from "../LiveFeed";
import { Link } from "../router";
import { Icon } from "../icons";

export const FEATURES = [
  { id: "nguoi-nha", icon: "face", title: "Nhận diện người nhà", q: "Ai vừa vào nhà? Có người lạ không?",
    text: "So khuôn mặt với thành viên đã đăng ký. Gặp người lạ, ảnh được gửi qua Telegram sau vài giây." },
  { id: "do-vat", icon: "target", title: "Nhớ chỗ để đồ", q: "Điện thoại của tôi đâu rồi?",
    text: "Tìm đồ vật theo từ khóa, nhớ nó nằm ở vùng nào và thấy lần cuối khi nào. Thêm đồ mới không cần huấn luyện lại." },
  { id: "te-nga", icon: "alert", title: "Phát hiện té ngã", q: "Có ai ngã mà không dậy được không?",
    text: "Xét vận tốc rơi, tư thế nằm và thời gian bất động. Ngồi xuống, cúi nhặt đồ hay nằm sofa đều không báo." },
  { id: "tro-ly", icon: "chat", title: "Trợ lý tiếng Việt", q: "Chụp ảnh nhà hiện tại cho tôi.",
    text: "Hỏi bằng chữ hoặc giọng nói qua Dashboard và Telegram. Trợ lý chỉ trả lời từ dữ liệu camera ghi được." },
] as const;


// Nhật ký mẫu — giống những gì hệ thống thật ghi vào CSDL trong một buổi tối
const LOG = [
  { t: "21:42", kind: "member", text: "Bé Na về nhà", meta: "khớp 0,81" },
  { t: "21:18", kind: "object", text: "Điện thoại → Bàn làm việc", meta: "YOLOE 0,71" },
  { t: "20:55", kind: "stranger", text: "Người lạ ở cửa chính", meta: "đã gửi Telegram" },
  { t: "19:47", kind: "member", text: "Mẹ về nhà", meta: "khớp 0,69" },
] as const;
const KIND_LABEL = { member: "Thành viên", object: "Đồ vật", stranger: "Người lạ" };

const STEPS: { title: string; text: ReactNode }[] = [
  { title: "Gắn camera bạn đang có", text: "Webcam USB, hoặc camera IP hỗ trợ RTSP như Tapo, Imou, Ezviz, Hikvision." },
  { title: "Bật hệ thống trên máy nhà", text: <>Một máy có GPU NVIDIA chạy toàn bộ AI, bật bằng một lệnh <code>docker compose up -d</code>.</> },
  { title: "Nhận cảnh báo, hỏi khi cần", text: "Cảnh báo về Telegram. Hỏi trợ lý qua Dashboard hoặc tin nhắn." },
];

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="kicker">Camera AI cho gia đình · Mã nguồn mở</p>
          <h1>Camera trong nhà bạn, giờ biết ai vừa về và đồ để ở đâu.</h1>
          <p className="lead">Nhận ra người nhà, báo người lạ, nhớ chỗ bạn để điện thoại, phát hiện té ngã, và trả lời câu hỏi bằng tiếng Việt. Mọi hình ảnh xử lý trên máy trong nhà.</p>
          <div className="cta-row">
            <Link to="/demo" className="btn">Dùng thử demo</Link>
            <Link to="/tinh-nang" className="btn secondary">Xem tính năng</Link>
          </div>
          <dl className="facts">
            <div><dt>Độ trễ xử lý</dt><dd>~25 ms</dd></div>
            <div><dt>Phí hằng tháng</dt><dd>0 đ</dd></div>
            <div><dt>Video gửi lên mây</dt><dd>Không</dd></div>
          </dl>
        </div>

        <div className="monitor" aria-label="Ví dụ màn hình giám sát">
          <LiveFeed />
          <div className="log">
            <div className="log-head"><span>Nhật ký hôm nay</span><span className="mono">cam_phongkhach</span></div>
            <ol>
              {LOG.map((e) => (
                <li key={e.t} className={`k-${e.kind}`}>
                  <time className="mono">{e.t}</time>
                  <span className="tag">{KIND_LABEL[e.kind]}</span>
                  <span className="what">{e.text}</span>
                  <span className="meta mono">{e.meta}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="f-h">
        <div className="sec-head">
          <p className="kicker">Bốn việc camera làm thay bạn</p>
          <h2 id="f-h">Mỗi tính năng trả lời một câu hỏi thật trong nhà</h2>
        </div>
        <div className="features">
          {FEATURES.map((f) => (
            <Link key={f.id} to={`/tinh-nang#${f.id}`} className="feature">
              <span className="f-ico"><Icon name={f.icon} /></span>
              <h3>{f.title}</h3>
              <p className="q">“{f.q}”</p>
              <p>{f.text}</p>
              <span className="more">Cách hoạt động →</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section split" aria-labelledby="a-h">
        <div>
          <p className="kicker">Trợ lý ảo</p>
          <h2 id="a-h">Hỏi như hỏi người trong nhà</h2>
          <p className="muted">Trợ lý tra cứu nhật ký ra vào, vị trí đồ vật và cảnh báo rồi trả lời ngắn gọn. Đồ vật chưa theo dõi thì nó nói là chưa biết và đề nghị theo dõi thêm, không đoán bừa.</p>
          <Link to="/demo" className="btn secondary">Hỏi thử trợ lý</Link>
        </div>
        <div className="chat-preview" aria-label="Ví dụ hội thoại">
          <div className="msg user"><p>Nãy giờ có ai vào nhà không?</p></div>
          <div className="msg bot"><p>Dạ, có Bé Na lúc 21:42 và Bố lúc 21:18. Có 1 lần phát hiện người lạ lúc 20:55.</p></div>
          <div className="msg user"><p>chia khoa cua toi o dau</p></div>
          <div className="msg bot"><p>Dạ, chìa khóa thấy lần cuối ở kệ cửa ra vào, cách đây 1 giờ 4 phút.</p></div>
          <div className="msg user"><p>Theo dõi thêm cái mũ bảo hiểm</p></div>
          <div className="msg bot"><p>Dạ, em đã thêm “Mũ bảo hiểm”. Camera sẽ tìm ở lượt quét tiếp theo.</p></div>
        </div>
      </section>

      <section className="section" aria-labelledby="s-h">
        <div className="sec-head">
          <p className="kicker">Bắt đầu</p>
          <h2 id="s-h">Ba bước, không cần thuê bao đám mây</h2>
        </div>
        <ol className="steps">
          {STEPS.map((s) => (
            <li key={s.title}>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <CtaBand />
    </>
  );
}
