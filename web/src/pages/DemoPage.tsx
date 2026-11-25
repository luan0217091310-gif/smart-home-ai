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
      <PageHero kicker="Demo trực tuyến" title="Dùng thử Dashboard với dữ liệu mẫu">
        Mọi thứ dưới đây chạy ngay trong trình duyệt của bạn với dữ liệu giả lập — không có camera hay dữ liệu thật của gia đình nào.
      </PageHero>
      <div className="tips" aria-label="Gợi ý thử">
        {TIPS.map(([t, d]) => <div key={t}><b>{t}</b><small>{d}</small></div>)}
      </div>
      <Demo />
      <p className="fineprint">Chạy trên chính máy nhà (<span className="mono">cd web && npm run dev</span>) rồi bấm “Chế độ demo” → nhập <span className="mono">/home-api</span> để xem camera và hỏi hệ thống thật.</p>
    </>
  );
}
