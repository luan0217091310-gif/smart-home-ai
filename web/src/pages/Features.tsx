import { CtaBand, PageHero } from "../Layout";
import { Icon } from "./Home";

const DETAILS = [
  {
    id: "nguoi-nha", icon: "face", color: "green", title: "Nhận diện người nhà & cảnh báo người lạ",
    lead: "Camera phân biệt thành viên gia đình với người lạ, ghi sổ ra vào và gửi ảnh người lạ qua Telegram.",
    how: [
      "Phát hiện khuôn mặt 3 lần/giây bằng InsightFace (vector 512 chiều).",
      "So độ tương đồng cosine với từng thành viên đã đăng ký từ 5–20 ảnh mẫu.",
      "Theo dấu từng khuôn mặt qua các khung (IoU) — nhiều người trong hình vẫn đếm đúng.",
      "Ngưỡng 2 mức: ≥ 0,45 là thành viên; < 0,25 trong 3 khung liên tiếp là người lạ; ở giữa (quay đầu, mờ) không kết luận.",
    ],
    specs: [["Mô hình", "InsightFace buffalo_l"], ["Tốc độ", "3 khung/giây"], ["Chống spam", "Log 1 lần/120 s/người · cảnh báo 1 lần/60 s"], ["Mặt tối thiểu", "60 px"]],
    note: "Chưa chống giả mạo bằng ảnh — không dùng để mở khóa cửa.",
  },
  {
    id: "do-vat", icon: "target", color: "blue", title: "Ghi nhớ vị trí đồ vật theo vùng",
    lead: "Camera theo dõi đồ vật bạn chỉ định và nhớ nó nằm ở vùng nào, thấy lần cuối khi nào.",
    how: [
      "Mỗi 4 giây quét khung mới nhất bằng YOLOE-26 với danh sách từ khóa tiếng Anh (cell phone, keys…).",
      "Tâm khung bao → vùng bạn đã vẽ (Bàn làm việc, Ghế sofa…). Điểm thuộc nhiều vùng chọn vùng nhỏ nhất.",
      "Chỉ đổi vùng khi thấy ở vùng mới 2 chu kỳ liên tiếp — tránh nhảy vùng do nhiễu.",
      "Thêm đồ vật mới bằng một câu nói hoặc trên Dashboard — nạp nóng, không khởi động lại, không train.",
    ],
    specs: [["Mô hình", "YOLOE-26 (dự phòng YOLO-World)"], ["Chu kỳ", "4 giây"], ["Vùng", "Đa giác, tọa độ 0–1"], ["Không thấy", "Giữ vị trí lần cuối"]],
    note: "Vật nhỏ ở xa (chìa khóa) khó nhận hơn — có thể dùng luồng camera nét hơn.",
  },
  {
    id: "te-nga", icon: "alert", color: "red", title: "Phát hiện té ngã",
    lead: "Phát hiện người ngã xuống sàn và không dậy, gửi cảnh báo khẩn — không báo khi ngồi, cúi hay nằm nghỉ.",
    how: [
      "Ước lượng tư thế 15 lần/giây bằng YOLO26-pose, theo dấu từng người.",
      "Lớp 1 — vận tốc rơi của thân (vai–hông) đi xuống nhanh, chuẩn hóa theo chiều cao người.",
      "Lớp 2 — tư thế nằm: thân nghiêng > 60° hoặc khung bao bè ngang.",
      "Lớp 3 — nằm ngoài vùng nghỉ (sofa, giường) và bất động 4 giây. Đứng dậy trước đó → huỷ.",
    ],
    specs: [["Mô hình", "YOLO26-pose"], ["Tốc độ", "15 khung/giây"], ["Xác nhận", "Bất động 4 giây"], ["Kiểm thử", "9 kịch bản tự động"]],
    note: "Người quỵ xuống từ từ có thể không qua lớp vận tốc rơi.",
  },
  {
    id: "tro-ly", icon: "spark", color: "violet", title: "Trợ lý ảo tiếng Việt",
    lead: "Hỏi bằng chữ hoặc giọng nói qua Dashboard và Telegram; trợ lý tra dữ liệu thật rồi trả lời ngắn gọn.",
    how: [
      "Gemini (hoặc Ollama chạy trên máy) gọi 7 công cụ: người ra vào, tìm đồ, thêm/ngừng đồ vật, cảnh báo, chụp ảnh nhà.",
      "Không bao giờ tự viết SQL; mọi tham số được kiểm tra kiểu và giới hạn.",
      "Hiểu tiếng Việt có dấu và không dấu; “nãy giờ” = 2 giờ, “hôm nay” = từ 0h.",
      "Tin nhắn thoại: faster-whisper chuyển giọng thành chữ, edge-tts đọc câu trả lời.",
    ],
    specs: [["LLM", "Gemini Flash-Lite / Ollama"], ["Kênh", "Dashboard · Telegram · API"], ["Kiểm thử", "7/7 câu mẫu đúng"], ["Bảo vệ", "Chỉ trả lời chat_id được phép"]],
    note: "Chế độ offline “rules” vẫn trả lời được khi chưa có khóa API.",
  },
];

const EXTRA = [
  { icon: "bell", title: "Cảnh báo Telegram", text: "Ảnh, giờ phút giây, tên camera. Chống spam ở một module chung." },
  { icon: "cam", title: "Tự nối lại camera", text: "Thử lại 1→30 giây; mất quá 5 phút thì báo hệ thống." },
  { icon: "cpu", title: "Dashboard quản lý", text: "Live, trạng thái service, cảnh báo, thành viên, đồ vật, trò chuyện." },
  { icon: "lock", title: "Dọn & sao lưu", text: "Xóa ảnh sau 30 ngày, nhật ký sau 90 ngày; sao lưu hằng tuần." },
];

export default function Features() {
  return (
    <>
      <PageHero kicker="Tính năng" title={<>Bốn năng lực AI,<br /><em>một hệ thống gọn nhẹ.</em></>}>
        Mỗi tính năng trả lời một câu hỏi thật của gia đình — và đều có kiểm thử tự động, ngưỡng chỉnh được trong một file cấu hình.
      </PageHero>
      <nav className="jump reveal" aria-label="Đi tới tính năng">
        {DETAILS.map((d) => <a key={d.id} href={`#${d.id}`} className={d.color}><Icon name={d.icon} />{d.title.split(" &")[0].split(" theo")[0]}</a>)}
      </nav>

      {DETAILS.map((d, i) => (
        <section key={d.id} id={d.id} className={`detail reveal ${d.color} ${i % 2 ? "flip" : ""}`}>
          <div className="detail-copy">
            <div className="f-ico"><Icon name={d.icon} /></div>
            <h2>{d.title}</h2>
            <p className="lead">{d.lead}</p>
            <ol className="how">{d.how.map((h) => <li key={h}>{h}</li>)}</ol>
            <p className="caveat">⚠ {d.note}</p>
          </div>
          <div className="spec-card">
            <h4>Thông số</h4>
            <dl>{d.specs.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
          </div>
        </section>
      ))}

      <section className="section">
        <div className="sec-head center reveal"><span className="kicker">Và còn nữa</span><h2>Những thứ chạy ngầm để bạn yên tâm</h2></div>
        <div className="mini-grid">
          {EXTRA.map((e) => (
            <div key={e.title} className="mini reveal"><div className="f-ico"><Icon name={e.icon} /></div><h3>{e.title}</h3><p>{e.text}</p></div>
          ))}
        </div>
      </section>
      <CtaBand />
    </>
  );
}
