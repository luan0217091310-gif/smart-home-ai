import { Demo } from "../Demo";
import { PageHero } from "../Layout";

const TIPS = [
  ["Live & Cảnh báo", "Bấm “Đã xem” hoặc “Báo giả” trên từng cảnh báo — trạng thái đổi ngay."],
  ["Đồ vật & Vùng", "Thêm “Mũ bảo hiểm” / helmet, hoặc ngừng theo dõi một món."],
  ["Trợ lý", "Thử: “Điện thoại của tôi đâu?”, “Chụp ảnh nhà hiện tại”, gõ không dấu cũng được."],
];

export default function DemoPage() {
  return (
    <>
      <PageHero kicker="Demo trực tuyến" title={<>Dashboard thật,<br /><em>dữ liệu mẫu.</em></>}>
        Mọi thứ dưới đây chạy ngay trong trình duyệt của bạn với dữ liệu giả lập — không có camera hay dữ liệu thật của gia đình nào.
      </PageHero>
      <div className="tips reveal">
        {TIPS.map(([t, d], i) => <div key={t}><span className="step-n">{i + 1}</span><b>{t}</b><small>{d}</small></div>)}
      </div>
      <div className="reveal"><Demo /></div>
      <p className="fineprint reveal">Chạy trên chính máy nhà (<span className="mono">cd web && npm run dev</span>) rồi bấm “Chế độ demo” → nhập <span className="mono">/home-api</span> để xem camera và hỏi hệ thống thật.</p>
    </>
  );
}
