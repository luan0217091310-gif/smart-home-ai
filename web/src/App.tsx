import { useEffect, type ComponentType } from "react";
import { Layout, PageHero } from "./Layout";
import Architecture from "./pages/Architecture";
import DemoPage from "./pages/DemoPage";
import Features from "./pages/Features";
import Home from "./pages/Home";
import Privacy from "./pages/Privacy";
import Setup from "./pages/Setup";
import { Link, usePath } from "./router";

const ROUTES: Record<string, { el: ComponentType; title: string }> = {
  "/": { el: Home, title: "Camera AI Thông Minh — người trông nhà có AI" },
  "/tinh-nang": { el: Features, title: "Tính năng · Camera AI Thông Minh" },
  "/demo": { el: DemoPage, title: "Demo · Camera AI Thông Minh" },
  "/kien-truc": { el: Architecture, title: "Kiến trúc · Camera AI Thông Minh" },
  "/cai-dat": { el: Setup, title: "Cài đặt · Camera AI Thông Minh" },
  "/rieng-tu": { el: Privacy, title: "Quyền riêng tư · Camera AI Thông Minh" },
};

export default function App() {
  const path = usePath();
  const route = ROUTES[path];
  useEffect(() => {
    document.title = route?.title ?? "Không tìm thấy · Camera AI Thông Minh";
    if (location.hash) setTimeout(() => document.querySelector(location.hash)?.scrollIntoView({ behavior: "smooth" }), 80);
  }, [path, route]);
  const Page = route?.el;
  return (
    <Layout>
      {Page ? <Page /> : (
        <PageHero kicker="404" title={<>Trang này <em>không tồn tại.</em></>}>
          <Link to="/" className="btn">Về trang chủ</Link>
        </PageHero>
      )}
    </Layout>
  );
}
