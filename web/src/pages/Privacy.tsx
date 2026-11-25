import { CtaBand, PageHero } from "../Layout";
import { Icon } from "../icons";

const FLOW = [
  ["Video trực tiếp", "RAM (Redis), không lưu", "no"],
  ["Ảnh mẫu & vector khuôn mặt", "Ổ đĩa máy chủ trong nhà", "no"],
  ["Giọng nói của bạn", "Chuyển thành chữ ngay trên máy", "no"],
  ["Ảnh người lạ, té ngã", "data/snapshots", "yes", "Gửi qua Telegram cho người nhận cảnh báo"],
  ["Câu hỏi & kết quả tra cứu (chữ)", "—", "yes", "Gửi tới Gemini — dùng Ollama nếu không muốn"],
];

const PROMISES = [
  { icon: "lock", t: "Không mở cổng ra Internet", d: "Dashboard và camera chỉ truy cập được trong mạng nhà. Telegram bot chỉ kết nối ra ngoài." },
  { icon: "face", t: "Đồng ý trước khi đăng ký", d: "Mỗi thành viên phải đồng ý trước khi đăng ký khuôn mặt; xóa ngay khi họ yêu cầu." },
  { icon: "bell", t: "Chỉ người được phép", d: "Bot chỉ trả lời các tài khoản Telegram trong danh sách cho phép." },
  { icon: "cpu", t: "Tự xóa theo hạn", d: "Ảnh chụp xóa sau 30 ngày, nhật ký ra vào sau 90 ngày, chạy tự động mỗi đêm." },
];

const LICENSES = [
  ["Mã nguồn InsightFace", "MIT", "Được"],
  ["Mô hình InsightFace buffalo_l", "Phi thương mại", "Chỉ dùng cá nhân"],
  ["Ultralytics YOLO26 / YOLOE-26", "AGPL-3.0", "Được"],
  ["edge-tts", "Dịch vụ không chính thức", "Có thể ngừng bất cứ lúc nào"],
];

export default function Privacy() {
  return (
    <>
      <PageHero kicker="Quyền riêng tư" title="Hình ảnh trong nhà bạn ở lại trong nhà bạn">
        Hệ thống xử lý khuôn mặt người thân, nên mặc định mọi hình ảnh nằm trên máy trong nhà — chỉ phần tối thiểu được gửi ra ngoài.
      </PageHero>

      <section className="section first">
        <div className="sec-head"><span className="kicker">Dữ liệu đi đâu</span><h2>Minh bạch từng loại dữ liệu</h2></div>
        <div className="flow">
          {FLOW.map(([k, where, out, why]) => (
            <div key={k} className={`flow-row ${out}`}>
              <b>{k}</b><small>{where}</small>
              <span className={`pill ${out === "no" ? "ok" : "warn"}`}>{out === "no" ? "Không rời nhà" : "Rời nhà"}</span>
              {why && <small className="why">{why}</small>}
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="mini-grid">
          {PROMISES.map((p) => <div key={p.t} className="mini"><div className="f-ico"><Icon name={p.icon} /></div><h3>{p.t}</h3><p>{p.d}</p></div>)}
        </div>
      </section>

      <section className="section split">
        <div>
          <span className="kicker">Pháp luật</span>
          <h2>Tôn trọng người xung quanh</h2>
          <p className="muted">Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 bảo vệ chặt dữ liệu sinh trắc học như khuôn mặt. Báo cho khách và người giúp việc biết trong nhà có camera AI; không quay ra đường, khu vực chung hay nhà hàng xóm; không lắp trong phòng ngủ, nhà tắm.</p>
        </div>
        <div className="table-wrap">
          <table className="svc-table">
            <thead><tr><th>Thành phần</th><th>Giấy phép</th><th>Dùng trong gia đình</th></tr></thead>
            <tbody>{LICENSES.map(([a, b, c]) => <tr key={a}><td>{a}</td><td>{b}</td><td>{c}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
      <CtaBand />
    </>
  );
}
