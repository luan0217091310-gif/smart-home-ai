import { lazy, Suspense, useEffect, type ComponentType } from "react";
import { Layout, PageHero } from "./Layout";
import Home from "./pages/Home";
import { Link, usePath } from "./router";

// Trang chủ tải ngay; các trang khác tải khi cần để lần mở đầu nhanh hơn.
const Features = lazy(() => import("./pages/Features"));
const DemoPage = lazy(() => import("./pages/DemoPage"));
const Architecture = lazy(() => import("./pages/Architecture"));
const Setup = lazy(() => import("./pages/Setup"));
const Privacy = lazy(() => import("./pages/Privacy"));

const ROUTES: Record<string, { el: ComponentType; title: string; desc: string }> = {
  "/": { el: Home, title: "Camera AI Thông Minh — người trông nhà có AI",
    desc: "Biến camera thường thành người trông nhà có AI: nhận diện người nhà, báo người lạ, nhớ chỗ để đồ, phát hiện té ngã, trợ lý tiếng Việt." },
  "/tinh-nang": { el: Features, title: "Tính năng · Camera AI Thông Minh",
    desc: "Nhận diện người nhà, ghi nhớ vị trí đồ vật, phát hiện té ngã và trợ lý ảo tiếng Việt — cách hoạt động và thông số." },
  "/demo": { el: DemoPage, title: "Demo trực tuyến · Camera AI Thông Minh",
    desc: "Dùng thử Dashboard với dữ liệu mẫu: cảnh báo, thành viên, đồ vật và trợ lý tiếng Việt ngay trên trình duyệt." },
  "/kien-truc": { el: Architecture, title: "Kiến trúc · Camera AI Thông Minh",
    desc: "Kiến trúc Producer–Consumer quanh Redis, 7 service, công nghệ sử dụng và lộ trình 8 giai đoạn." },
  "/cai-dat": { el: Setup, title: "Cài đặt · Camera AI Thông Minh",
    desc: "Hướng dẫn cài đặt 5 bước, yêu cầu phần cứng, danh sách camera tương thích RTSP và câu hỏi thường gặp." },
  "/rieng-tu": { el: Privacy, title: "Quyền riêng tư · Camera AI Thông Minh",
    desc: "Dữ liệu nào ở lại trong nhà, dữ liệu nào rời nhà, bảo mật và giấy phép các thành phần." },
};

export default function App() {
  const path = usePath();
  const route = ROUTES[path];
  useEffect(() => {
    document.title = route?.title ?? "Không tìm thấy · Camera AI Thông Minh";
    document.querySelector('meta[name="description"]')?.setAttribute("content", route?.desc ?? "");
    if (location.hash) setTimeout(() => document.querySelector(location.hash)?.scrollIntoView({ behavior: "smooth" }), 120);
  }, [path, route]);
  const Page = route?.el;
  return (
    <Layout>
      <Suspense fallback={<div className="page-loading" aria-label="Đang tải"><i /></div>}>
        {Page ? <Page /> : (
          <PageHero kicker="404" title="Không tìm thấy trang này">
            <Link to="/" className="btn">Về trang chủ</Link>
          </PageHero>
        )}
      </Suspense>
    </Layout>
  );
}
