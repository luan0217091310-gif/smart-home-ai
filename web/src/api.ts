// Kết nối tới máy chủ trong nhà (assistant_api). Địa chỉ lưu trong trình duyệt, không gửi đi đâu khác.
const KEY = "sha.homeUrl";

export function getHomeUrl(): string {
  return localStorage.getItem(KEY) ?? "";
}

export function setHomeUrl(url: string) {
  const clean = url.trim().replace(/\/+$/, "");
  if (clean) localStorage.setItem(KEY, clean);
  else localStorage.removeItem(KEY);
}

async function withTimeout<T>(p: (signal: AbortSignal) => Promise<T>, ms = 15000): Promise<T> {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try {
    return await p(c.signal);
  } finally {
    clearTimeout(t);
  }
}

export async function health(base: string): Promise<{ status: string; llm: string }> {
  return withTimeout(async (signal) => {
    const r = await fetch(`${base}/health`, { signal });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }, 6000);
}

export interface ChatReply {
  answer: string;
  images: string[];
  elapsed_s?: number;
  llm?: string;
}

export async function chat(base: string, message: string): Promise<ChatReply> {
  return withTimeout(async (signal) => {
    const r = await fetch(`${base}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal,
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
}

export const imageUrl = (base: string, rel: string) => `${base}/image?path=${encodeURIComponent(rel)}`;
export const snapshotUrl = (base: string) => `${base}/snapshot?t=${Date.now()}`;
