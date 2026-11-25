import { useEffect, useRef } from "react";

// Khung hình camera MÔ PHỎNG theo kiểu CCTV thật: ảnh đơn sắc có hạt nhiễu, OSD ngày giờ, khung nhận diện mảnh.
// Hiệu năng: căn phòng (phần tĩnh) vẽ 1 lần vào bộ đệm; mỗi khung chỉ vẽ người + nhiễu + OSD.
// Chỉ chạy khi khung đang hiện trên màn hình, tab đang mở và trang đã tải xong.
const pad = (n: number) => String(n).padStart(2, "0");
const DOW = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
const MONO = "'JetBrains Mono', ui-monospace, monospace";

function drawRoom(ctx: CanvasRenderingContext2D, h: number) {
  let gr = ctx.createLinearGradient(0, 0, 0, h);
  gr.addColorStop(0, "#5d6462"); gr.addColorStop(0.58, "#4a504e"); gr.addColorStop(0.58, "#3a3e3c"); gr.addColorStop(1, "#262928");
  ctx.fillStyle = gr; ctx.fillRect(0, 0, 640, h);
  ctx.strokeStyle = "rgba(255,255,255,.05)"; ctx.lineWidth = 1;
  for (let i = -6; i <= 6; i++) { ctx.beginPath(); ctx.moveTo(320 + i * 30, h * 0.58); ctx.lineTo(320 + i * 140, h); ctx.stroke(); }
  gr = ctx.createRadialGradient(505, 95, 10, 505, 95, 150);
  gr.addColorStop(0, "rgba(235,240,238,.55)"); gr.addColorStop(1, "rgba(235,240,238,0)");
  ctx.fillStyle = gr; ctx.fillRect(330, 0, 310, 260);
  ctx.fillStyle = "#c9cfcc"; ctx.fillRect(445, 45, 120, 105);
  ctx.fillStyle = "#4a504e"; ctx.fillRect(503, 45, 4, 105); ctx.fillRect(445, 96, 120, 3);
  ctx.fillStyle = "#3f4442"; ctx.fillRect(22, 70, 70, 155);
  ctx.fillStyle = "#6d7471"; ctx.fillRect(80, 150, 5, 5);
  ctx.fillStyle = "#7d8582"; ctx.fillRect(120, 234, 150, 9);
  ctx.fillStyle = "#1f2221"; ctx.fillRect(126, 243, 7, 64); ctx.fillRect(257, 243, 7, 64);
  ctx.fillStyle = "#151817"; ctx.fillRect(158, 204, 50, 30); ctx.fillRect(180, 230, 6, 5);
  ctx.fillStyle = "#0e100f"; ctx.fillRect(222, 228, 20, 6);
  ctx.fillStyle = "#6f7673"; ctx.beginPath(); ctx.roundRect(400, 214, 190, 40, 10); ctx.fill();
  ctx.fillStyle = "#8a918e"; ctx.beginPath(); ctx.roundRect(392, 250, 206, 30, 8); ctx.fill();
  ctx.fillStyle = "#565c5a"; ctx.fillRect(392, 278, 206, 22);
  ctx.fillStyle = "#1c1f1e"; ctx.fillRect(400, 300, 8, 8); ctx.fillRect(582, 300, 8, 8);
  gr = ctx.createRadialGradient(320, h / 2, h * 0.35, 320, h / 2, h * 0.95);
  gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(0,0,0,.45)");
  ctx.fillStyle = gr; ctx.fillRect(0, 0, 640, h);
}

function box(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, hh: number, color: string, text: string, above = true) {
  ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, w, hh);
  ctx.font = `500 10px ${MONO}`;
  const tw = ctx.measureText(text).width + 8;
  const ty = above ? y - 14 : y + hh;
  ctx.fillStyle = color; ctx.fillRect(x - 0.75, ty, tw, 14);
  ctx.fillStyle = "#0c0e0d"; ctx.fillText(text, x + 3, ty + 10.5);
}

export function LiveFeed({ snapshotSrc, label = "CAM01 · PHÒNG KHÁCH" }: { snapshotSrc?: string; label?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (snapshotSrc) return;
    const c = ref.current;
    const ctx = c?.getContext("2d");
    if (!c || !ctx) return;
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Hạt nhiễu: một ô nhỏ dựng 1 lần, lát kín bằng pattern
    const tile = document.createElement("canvas");
    tile.width = tile.height = 96;
    const tctx = tile.getContext("2d")!;
    const img = tctx.createImageData(96, 96);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.random() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 24;
    }
    tctx.putImageData(img, 0, 0);
    const grain = ctx.createPattern(tile, "repeat");

    // Bộ đệm căn phòng — chỉ dựng lại khi kích thước đổi
    const room = document.createElement("canvas");
    let W = 0, H = 0, s = 1, h = 400;

    const resize = () => {
      const dpr = Math.min(devicePixelRatio || 1, 1.5);
      const nw = Math.max(1, Math.round(c.clientWidth * dpr));
      const nh = Math.max(1, Math.round(c.clientHeight * dpr));
      if (nw === W && nh === H) return;
      W = c.width = room.width = nw;
      H = c.height = room.height = nh;
      s = W / 640; h = H / s;
      const rctx = room.getContext("2d")!;
      rctx.setTransform(s, 0, 0, s, 0, 0);
      drawRoom(rctx, h);
    };

    const t0 = performance.now();
    const frame = (now: number) => {
      const t = reduce ? 4 : (now - t0) / 1000;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(room, 0, 0);
      ctx.setTransform(s, 0, 0, s, 0, 0);
      // người đi lại (bóng tối)
      const px = 330 + Math.sin(t * 0.35) * 70;
      const step = Math.sin(t * 2.2) * 3;
      ctx.fillStyle = "#171a19";
      ctx.beginPath(); ctx.arc(px, 152, 13, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.roundRect(px - 19, 168, 38, 72, 9); ctx.fill();
      ctx.fillRect(px - 15, 236, 12, 66 + step); ctx.fillRect(px + 3, 236, 12, 66 - step);
      // nhiễu + vệt quét
      if (grain) {
        const ox = Math.floor(Math.random() * 96), oy = Math.floor(Math.random() * 96);
        ctx.save(); ctx.translate(-ox, -oy); ctx.fillStyle = grain; ctx.fillRect(0, 0, 640 + 96, h + 96); ctx.restore();
      }
      ctx.fillStyle = "rgba(255,255,255,.035)"; ctx.fillRect(0, ((t * 40) % (h + 60)) - 30, 640, 18);
      box(ctx, px - 16, 136, 32, 34, "#7fd1ae", "Bé Na 0.81");
      box(ctx, 216, 225, 32, 16, "#9cc3ff", "điện thoại 0.71", false);
      // OSD: ngày giờ trên-trái, tên camera dưới-phải
      const d = new Date();
      const osd = `${pad(d.getDate())}-${pad(d.getMonth() + 1)}-${d.getFullYear()} ${DOW[d.getDay()]} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
      ctx.font = `500 13px ${MONO}`;
      ctx.lineWidth = 3; ctx.strokeStyle = "rgba(0,0,0,.75)"; ctx.fillStyle = "#f2f4f3";
      ctx.strokeText(osd, 14, 24); ctx.fillText(osd, 14, 24);
      const lw = ctx.measureText(label).width;
      ctx.strokeText(label, 626 - lw, h - 14); ctx.fillText(label, 626 - lw, h - 14);
    };

    let raf = 0, last = 0, visible = false, started = false;
    const loop = (now: number) => {
      raf = 0;
      if (!visible || document.hidden) return;
      if (now - last >= 100) { last = now; resize(); frame(now); } // 10 FPS là đủ cho cảm giác camera
      raf = requestAnimationFrame(loop);
    };
    const kick = () => { if (started && visible && !document.hidden && !raf && !reduce) raf = requestAnimationFrame(loop); };

    // Vẽ ngay 1 khung tĩnh để trang có hình từ đầu
    resize(); frame(performance.now());

    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; kick(); });
    io.observe(c);
    const onVis = () => kick();
    document.addEventListener("visibilitychange", onVis);
    const onResize = () => { resize(); frame(performance.now()); };
    addEventListener("resize", onResize);
    // Chỉ bắt đầu chuyển động khi trang đã tải xong và trình duyệt rảnh
    const begin = () => { started = true; kick(); };
    const idle = (window as Window & { requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number }).requestIdleCallback;
    const onLoad = () => (idle ? idle(begin, { timeout: 2500 }) : setTimeout(begin, 1200));
    if (document.readyState === "complete") onLoad(); else addEventListener("load", onLoad, { once: true });
    if (document.fonts) document.fonts.ready.then(() => frame(performance.now())); // vẽ lại OSD khi font mono đã sẵn sàng

    return () => {
      if (raf) cancelAnimationFrame(raf);
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      removeEventListener("resize", onResize);
      removeEventListener("load", onLoad);
      started = false;
    };
  }, [snapshotSrc, label]);

  return (
    <figure className="feed">
      {snapshotSrc ? <img src={snapshotSrc} alt="Ảnh hiện tại từ camera trong nhà" /> : <canvas ref={ref} role="img" aria-label="Khung hình camera mô phỏng: một người đi trong phòng khách, hệ thống nhận ra là Bé Na và thấy điện thoại trên bàn" />}
      <figcaption className="feed-cap">
        <span className="rec" aria-hidden />{snapshotSrc ? "Trực tiếp" : "Mô phỏng"} · 15 FPS
      </figcaption>
    </figure>
  );
}
