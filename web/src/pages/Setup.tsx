import { useState } from "react";
import { CtaBand, PageHero, REPO } from "../Layout";

const STEPS = [
  { t: "Tải mã nguồn và tạo cấu hình", d: "Điền token Telegram, khóa Gemini, mật khẩu Dashboard vào file .env.",
    code: `git clone ${REPO}.git\ncd smart-home-ai\ncp .env.example .env` },
  { t: "Bật toàn bộ hệ thống", d: "Lần đầu build mất 15–30 phút (PyTorch, InsightFace). Trên Windows dùng start.ps1 để đọc webcam.",
    code: "docker compose up -d\n# Windows + webcam:\npowershell -ExecutionPolicy Bypass -File start.ps1" },
  { t: "Đăng ký khuôn mặt", d: "Bỏ 5–10 ảnh mỗi người vào data/faces/<tên>/ hoặc tải lên ở tab Thành viên.",
    code: "docker compose run --rm worker_face python scripts/enroll_faces.py" },
  { t: "Vẽ vùng trong phòng", d: "Chụp ảnh tĩnh từ camera rồi click vẽ các vùng: bàn, sofa (vùng nghỉ), sàn, cửa.",
    code: "python scripts/view_stream.py --snapshot\npython scripts/draw_zones.py" },
  { t: "Mở Dashboard", d: "Trong mạng nhà: http://<IP-máy>:8501. Cảnh báo tự gửi vào Telegram.",
    code: "http://localhost:8501" },
];

const REQS = [["GPU", "NVIDIA ≥ 4 GB VRAM"], ["RAM", "≥ 16 GB"], ["Ổ trống", "≥ 30 GB"], ["Phần mềm", "Docker, Python 3.11"]];

const CAMS = [
  ["TP-Link Tapo (C200, C210, C220…)", "ok", "Dễ nhất — bật “Tài khoản camera” trong app"],
  ["Imou (Ranger, Cruiser…)", "ok", "Mật khẩu RTSP là mã an toàn dưới đáy"],
  ["Ezviz (C6N, H6c…)", "ok", "Mật khẩu RTSP là mã xác minh dưới đáy"],
  ["Hikvision · Dahua · KBVision", "ok", "Camera an ninh chuyên dụng, rất ổn định"],
  ["Xiaomi / Mi Home", "warn", "Đa số không có RTSP"],
  ["Camera dùng pin (mọi hãng)", "no", "Hầu hết không có RTSP"],
];

const FAQ = [
  ["Có cần Internet không?", "Xử lý hình ảnh hoàn toàn offline. Chỉ cần mạng để gửi Telegram và hỏi Gemini — dùng Ollama thì không cần."],
  ["Có tốn phí hằng tháng không?", "Không. Gemini có hạn mức miễn phí; Telegram miễn phí. Chi phí duy nhất là điện cho máy chủ."],
  ["Đổi sang camera IP có phải sửa code?", "Không. Chỉ sửa CAMERA_SOURCE trong .env thành link rtsp://… rồi vẽ lại vùng."],
  ["Chạy được bao nhiêu camera?", "Bản hiện tại 1 camera. GPU 4 GB chịu được khoảng 1–2 camera khi mở rộng."],
  ["Xem nhà từ xa được không?", "Cảnh báo và hỏi đáp qua Telegram dùng được ở bất cứ đâu. Dashboard cố ý chỉ mở trong mạng nhà."],
];

export default function Setup() {
  return (
    <>
      <PageHero kicker="Cài đặt" title="Cài đặt xong trong một buổi chiều">
        Năm bước, đều là sao chép một lệnh. README trên GitHub có giải thích chi tiết từng biến cấu hình và lỗi thường gặp.
      </PageHero>

      <div className="reqs">{REQS.map(([k, v]) => <div key={k}><small>{k}</small><b>{v}</b></div>)}</div>

      <h2 className="setup-h">Năm bước cài đặt</h2>
      <ol className="setup">
        {STEPS.map((s, i) => (
          <li key={s.t} >
            <span className="step-num mono" aria-hidden>{String(i + 1).padStart(2, "0")}</span>
            <div className="setup-body">
              <h3>{s.t}</h3>
              <p>{s.d}</p>
              <CodeBlock code={s.code} />
            </div>
          </li>
        ))}
      </ol>

      <section id="camera" className="section">
        <div className="sec-head"><span className="kicker">Camera tương thích</span><h2>Chọn camera có RTSP</h2>
          <p>Trước khi mua, tìm “&lt;tên model&gt; RTSP”. Có hướng dẫn là dùng được — chỉ cần sửa một dòng trong .env.</p></div>
        <div className="table-wrap">
          <table className="svc-table">
            <thead><tr><th>Hãng</th><th>Dùng được</th><th>Ghi chú</th></tr></thead>
            <tbody>{CAMS.map(([n, s, d]) => (
              <tr key={n}><td>{n}</td><td><span className={`pill ${s}`}>{s === "ok" ? "Có" : s === "warn" ? "Tùy model" : "Không"}</span></td><td>{d}</td></tr>
            ))}</tbody>
          </table>
        </div>
        <CodeBlock code={"CAMERA_ID=cam_phongkhach\nCAMERA_SOURCE=rtsp://user:matkhau@192.168.1.50:554/stream2"} />
      </section>

      <section className="section">
        <div className="sec-head"><span className="kicker">Câu hỏi thường gặp</span><h2>Trước khi bắt đầu</h2></div>
        <div className="faq">
          {FAQ.map(([q, a]) => <details key={q} ><summary>{q}</summary><p>{a}</p></details>)}
        </div>
      </section>
      <CtaBand />
    </>
  );
}

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="codeblock">
      <pre className="mono">{code}</pre>
      <button onClick={() => { navigator.clipboard?.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 1500); }}>
        {copied ? "Đã chép" : "Sao chép"}
      </button>
    </div>
  );
}
