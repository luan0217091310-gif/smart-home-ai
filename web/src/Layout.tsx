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

type Theme = "system" | "light" | "dark";
const THEME_LABEL: Record<Theme, string> = { system: "Theo hệ thống", light: "Sáng", dark: "Tối" };

function readTheme(): Theme {
  try {
    const v = localStorage.getItem("sha.theme");
    return v === "light" || v === "dark" ? v : "system";
  } catch {
    return "system";
  }
}

function applyTheme(t: Theme) {
  const root = document.documentElement;
  if (t === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", t);
  try {
    if (t === "system") localStorage.removeItem("sha.theme");
    else localStorage.setItem("sha.theme", t);
  } catch { /* trình duyệt chặn lưu trữ: vẫn đổi được trong phiên này */ }
}

export function Layout({ children }: { children: ReactNode }) {
  const path = usePath();
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>(readTheme);

  useEffect(() => { applyTheme(theme); }, [theme]);
  useEffect(() => { setOpen(false); }, [path]);
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    addEventListener("keydown", onKey);
    return () => { removeEventListener("keydown", onKey); };
  }, [open]);

  const nextTheme = () => setTheme((t) => (t === "system" ? "light" : t === "light" ? "dark" : "system"));

  return (
    <>
      <a href="#main" className="skip">Bỏ qua tới nội dung</a>
      <header className={`nav ${open ? "menu-open" : ""}`}>
        <div className="nav-in">
          <Link to="/" className="brand" aria-label="Camera AI Thông Minh — trang chủ">
            <Logo />
            <span>Camera AI <b>Thông Minh</b></span>
          </Link>
          <nav id="site-nav" className={open ? "open" : ""} aria-label="Điều hướng chính">
            {PAGES.slice(1).map((p) => (
              <Link key={p.to} to={p.to} aria-current={path === p.to ? "page" : undefined}>{p.label}</Link>
            ))}
          </nav>
          <div className="nav-cta">
            <button className="icon-btn" onClick={nextTheme} aria-label={`Giao diện: ${THEME_LABEL[theme]}. Bấm để đổi`} title={`Giao diện: ${THEME_LABEL[theme]}`}>
              <ThemeIcon theme={theme} />
            </button>
            <a className="icon-btn hide-sm" href={REPO} target="_blank" rel="noreferrer" aria-label="Mã nguồn trên GitHub"><GitHubIcon /></a>
            <Link to="/demo" className="btn sm">Dùng thử</Link>
            <button className="burger" aria-label={open ? "Đóng menu" : "Mở menu"} aria-expanded={open} aria-controls="site-nav" onClick={() => setOpen((v) => !v)}>
              <i /><i /><i />
            </button>
          </div>
        </div>
      </header>

      <main id="main" key={path} tabIndex={-1}>{children}</main>

      <footer className="footer">
        <div className="footer-in">
          <div className="f-brand">
            <Link to="/" className="brand"><Logo /><span>Camera AI <b>Thông Minh</b></span></Link>
            <p>Người trông nhà có AI, chạy hoàn toàn trên máy trong gia đình. Dự án cá nhân, phi thương mại.</p>
          </div>
          <div>
            <h2 className="f-h">Sản phẩm</h2>
            <Link to="/tinh-nang">Tính năng</Link>
            <Link to="/demo">Demo trực tuyến</Link>
            <Link to="/kien-truc">Kiến trúc</Link>
          </div>
          <div>
            <h2 className="f-h">Bắt đầu</h2>
            <Link to="/cai-dat">Hướng dẫn cài đặt</Link>
            <Link to="/cai-dat#camera">Camera tương thích</Link>
            <Link to="/rieng-tu">Quyền riêng tư</Link>
          </div>
          <div>
            <h2 className="f-h">Mã nguồn</h2>
            <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
            <a href={`${REPO}/blob/main/docs/SPEC.md`} target="_blank" rel="noreferrer">Đặc tả dự án</a>
            <a href={`${REPO}/tree/main/docs/acceptance`} target="_blank" rel="noreferrer">Biên bản nghiệm thu</a>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} smart-home-ai</span>
          <span>Không quảng cáo · Không cookie theo dõi</span>
        </div>
      </footer>
    </>
  );
}

export function Logo() {
  // Ống kính camera đặt trong hình ngôi nhà — một màu, theo màu chữ
  return (
    <svg className="logo" viewBox="0 0 32 32" aria-hidden>
      <path d="M4 14.5 16 5l12 9.5V26a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinejoin="round" />
      <circle cx="16" cy="18.5" r="4.6" fill="none" stroke="currentColor" strokeWidth="2.2" />
      <circle cx="16" cy="18.5" r="1.6" fill="var(--accent)" />
    </svg>
  );
}

function ThemeIcon({ theme }: { theme: Theme }) {
  const p = { fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const };
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      {theme === "light" && <g {...p}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></g>}
      {theme === "dark" && <path {...p} d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" />}
      {theme === "system" && <g {...p}><rect x="3" y="4" width="18" height="13" rx="2" /><path d="M8 21h8M12 17v4" /></g>}
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
      <p className="kicker">{kicker}</p>
      <h1>{title}</h1>
      {children && <div className="lead">{children}</div>}
    </section>
  );
}

export function CtaBand() {
  return (
    <section className="cta-band" aria-labelledby="cta-h">
      <div>
        <h2 id="cta-h">Thử trên trình duyệt trước khi cài</h2>
        <p>Dashboard demo chạy bằng dữ liệu mẫu: bấm cảnh báo, thêm đồ vật, hỏi trợ lý bằng tiếng Việt.</p>
      </div>
      <div className="cta-row">
        <Link to="/demo" className="btn">Mở demo</Link>
        <Link to="/cai-dat" className="btn secondary">Hướng dẫn cài đặt</Link>
      </div>
    </section>
  );
}
