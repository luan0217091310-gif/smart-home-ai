import { useEffect, useState, type ReactNode } from "react";
import { Link, usePath } from "./router";

export const REPO = "https://github.com/luan0217091310-gif/smart-home-ai";

export const PAGES = [
  { to: "/", label: "Trang chủ" },
  { to: "/tinh-nang", label: "Tính năng" },
  { to: "/demo", label: "Demo" },
  { to: "/kien-truc", label: "Kiến trúc" },
  { to: "/cai-dat", label: "Cài đặt" },
  { to: "/rieng-tu", label: "Riêng tư" },
];

export function Layout({ children }: { children: ReactNode }) {
  const path = usePath();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const on = () => setScrolled(scrollY > 8);
    on();
    addEventListener("scroll", on, { passive: true });
    return () => removeEventListener("scroll", on);
  }, []);
  useEffect(() => { setOpen(false); }, [path]);
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    addEventListener("keydown", onKey);
    return () => { removeEventListener("keydown", onKey); };
  }, [open]);

  // hiệu ứng hiện dần khi cuộn tới
  useEffect(() => {
    const show = (el: Element) => el.classList.add("in");
    const io = "IntersectionObserver" in window
      ? new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && show(e.target)), { threshold: 0.08 })
      : null;
    const scan = () => document.querySelectorAll(".reveal:not(.in)").forEach((el) => {
      if (!io || el.getBoundingClientRect().top < innerHeight) show(el); // đang trong màn hình → hiện ngay
      else io.observe(el);
    });
    const t = setTimeout(scan, 20);
    const mo = new MutationObserver(() => scan()); // trang tải lazy → quét lại
    const mainEl = document.getElementById("main");
    if (mainEl) mo.observe(mainEl, { childList: true, subtree: true });
    // lưới an toàn: không bao giờ để nội dung bị ẩn nếu observer không chạy
    const safety = () => document.querySelectorAll(".reveal:not(.in)").forEach((el) => {
      if (el.getBoundingClientRect().top < innerHeight + 200) show(el);
    });
    addEventListener("scroll", safety, { passive: true });
    return () => { clearTimeout(t); mo.disconnect(); io?.disconnect(); removeEventListener("scroll", safety); };
  }, [path]);

  return (
    <>
      <a href="#main" className="skip">Bỏ qua tới nội dung</a>
      <div className="bg-grid" aria-hidden />
      <header className={`nav ${scrolled ? "scrolled" : ""} ${open ? "menu-open" : ""}`}>
        <div className="nav-in">
          <Link to="/" className="brand" aria-label="Trang chủ">
            <Logo />
            <span>Camera AI <em>Thông Minh</em></span>
          </Link>
          <nav className={open ? "open" : ""} aria-label="Điều hướng chính">
            {PAGES.slice(1).map((p) => (
              <Link key={p.to} to={p.to} className={path === p.to ? "active" : ""}>{p.label}</Link>
            ))}
          </nav>
          <div className="nav-cta">
            <a className="icon-btn" href={REPO} target="_blank" rel="noreferrer" aria-label="GitHub"><GitHubIcon /></a>
            <Link to="/demo" className="btn sm">Dùng thử</Link>
            <button className="burger" aria-label="Mở menu" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
              <i /><i /><i />
            </button>
          </div>
        </div>
      </header>

      <main id="main" key={path} className="page-enter" tabIndex={-1}>{children}</main>

      <footer className="footer">
        <div className="footer-in">
          <div className="f-brand">
            <Link to="/" className="brand"><Logo /><span>Camera AI <em>Thông Minh</em></span></Link>
            <p>Người trông nhà có AI, chạy hoàn toàn trên máy trong gia đình. Dự án cá nhân, phi thương mại.</p>
          </div>
          <div>
            <h5>Sản phẩm</h5>
            <Link to="/tinh-nang">Tính năng</Link>
            <Link to="/demo">Demo trực tuyến</Link>
            <Link to="/kien-truc">Kiến trúc</Link>
          </div>
          <div>
            <h5>Bắt đầu</h5>
            <Link to="/cai-dat">Hướng dẫn cài đặt</Link>
            <Link to="/cai-dat#camera">Camera tương thích</Link>
            <Link to="/rieng-tu">Quyền riêng tư</Link>
          </div>
          <div>
            <h5>Mã nguồn</h5>
            <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
            <a href={`${REPO}/blob/main/docs/SPEC.md`} target="_blank" rel="noreferrer">Đặc tả dự án</a>
            <a href={`${REPO}/tree/main/docs/acceptance`} target="_blank" rel="noreferrer">Biên bản nghiệm thu</a>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} smart-home-ai</span>
          <span>Video xử lý 100% trong nhà · Không quảng cáo · Không theo dõi</span>
        </div>
      </footer>
    </>
  );
}

export function Logo() {
  return (
    <svg className="logo" viewBox="0 0 32 32" aria-hidden>
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#34d399" /><stop offset="1" stopColor="#38bdf8" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="url(#lg)" />
      <path d="M8 15.5 16 9l8 6.5V23a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 8 23z" fill="none" stroke="#052018" strokeWidth="2" strokeLinejoin="round" />
      <circle cx="16" cy="18" r="3" fill="none" stroke="#052018" strokeWidth="2" />
    </svg>
  );
}

export function GitHubIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden fill="currentColor">
      <path d="M12 .5a11.5 11.5 0 0 0-3.64 22.42c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z" />
    </svg>
  );
}

export function PageHero({ kicker, title, children }: { kicker: string; title: ReactNode; children?: ReactNode }) {
  return (
    <section className="page-hero">
      <span className="kicker">{kicker}</span>
      <h1>{title}</h1>
      {children && <p className="lead">{children}</p>}
    </section>
  );
}

export function CtaBand() {
  return (
    <section className="cta-band reveal">
      <div>
        <h2>Xem tận mắt trong 30 giây</h2>
        <p>Dashboard demo chạy ngay trên trình duyệt — bấm thử cảnh báo, đồ vật và hỏi trợ lý bằng tiếng Việt.</p>
      </div>
      <div className="cta-row">
        <Link to="/demo" className="btn">Mở demo</Link>
        <Link to="/cai-dat" className="btn ghost-btn">Hướng dẫn cài đặt</Link>
      </div>
    </section>
  );
}
