import { useEffect, useState, type AnchorHTMLAttributes, type MouseEvent } from "react";

// Bộ định tuyến nhỏ dùng History API (Cloudflare/Netlify/Vercel đã cấu hình trả index.html cho mọi đường dẫn).
export function navigate(to: string) {
  if (to === location.pathname) return;
  history.pushState(null, "", to);
  window.dispatchEvent(new Event("popstate"));
  window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
}

export function usePath(): string {
  const [path, setPath] = useState(location.pathname);
  useEffect(() => {
    const on = () => setPath(location.pathname);
    window.addEventListener("popstate", on);
    return () => window.removeEventListener("popstate", on);
  }, []);
  return path.replace(/\/+$/, "") || "/";
}

export function Link({ to, onClick, ...rest }: AnchorHTMLAttributes<HTMLAnchorElement> & { to: string }) {
  return (
    <a
      href={to}
      {...rest}
      onClick={(e: MouseEvent<HTMLAnchorElement>) => {
        onClick?.(e);
        if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.button !== 0) return;
        e.preventDefault();
        navigate(to);
      }}
    />
  );
}
