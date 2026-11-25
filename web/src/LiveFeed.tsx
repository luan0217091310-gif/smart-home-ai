import { useEffect, useRef } from "react";

// Khung hình camera MÔ PHỎNG theo kiểu CCTV thật: ảnh đơn sắc có hạt nhiễu, OSD ngày giờ,
// khung nhận diện mảnh. Vẽ bằng canvas, không dùng ảnh ngoài.
const pad = (n: number) => String(n).padStart(2, "0");
const DOW = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];

export function LiveFeed({ snapshotSrc, label = "CAM01 · PHÒNG KHÁCH" }: { snapshotSrc?: string; label?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (snapshotSrc) return;
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    // hạt nhiễu dựng sẵn 1 lần, mỗi khung chỉ dịch vị trí → nhẹ CPU
    const grain = document.createElement("canvas");
    grain.width = grain.height = 160;
    const g = grain.getContext("2d")!;
    const img = g.createImageData(160, 160);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.random() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 22;
    }
    g.putImageData(img, 0, 0);

    let raf = 0;
    let last = 0;
    const t0 = performance.now();
    const draw = (now: number) => {
      raf = requestAnimationFrame(draw);
      if (now - last < 66) return; // ~15 FPS như camera thật
      last = now;
      const t = reduce ? 4 : (now - t0) / 1000;
      const dpr = Math.min(devicePixelRatio || 1, 2);
      const W = Math.max(1, Math.round(c.clientWidth * dpr));
      const H = Math.max(1, Math.round(c.clientHeight * dpr));
      if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
      const s = W / 640;
      ctx.setTransform(s, 0, 0, s, 0, 0);
      const h = H / s;

      // tường + sàn (thang xám hơi lạnh như camera đêm)
      let gr = ctx.createLinearGradient(0, 0, 0, h);
      gr.addColorStop(0, "#5d6462"); gr.addColorStop(0.58, "#4a504e"); gr.addColorStop(0.58, "#3a3e3c"); gr.addColorStop(1, "#262928");
      ctx.fillStyle = gr; ctx.fillRect(0, 0, 640, h);
      // phối cảnh sàn
      ctx.strokeStyle = "rgba(255,255,255,.05)"; ctx.lineWidth = 1;
      for (let i = -6; i <= 6; i++) { ctx.beginPath(); ctx.moveTo(320 + i * 30, h * 0.58); ctx.lineTo(320 + i * 140, h); ctx.stroke(); }
      // cửa sổ sáng (cháy sáng nhẹ như camera thật)
      gr = ctx.createRadialGradient(505, 95, 10, 505, 95, 150);
      gr.addColorStop(0, "rgba(235,240,238,.55)"); gr.addColorStop(1, "rgba(235,240,238,0)");
      ctx.fillStyle = gr; ctx.fillRect(330, 0, 310, 260);
      ctx.fillStyle = "#c9cfcc"; ctx.fillRect(445, 45, 120, 105);
      ctx.fillStyle = "#4a504e"; ctx.fillRect(503, 45, 4, 105); ctx.fillRect(445, 96, 120, 3);
      // cửa ra vào bên trái
      ctx.fillStyle = "#3f4442"; ctx.fillRect(22, 70, 70, 155);
      ctx.fillStyle = "#6d7471"; ctx.fillRect(80, 150, 5, 5);
      // bàn làm việc
      ctx.fillStyle = "#7d8582"; ctx.fillRect(120, 234, 150, 9); // mặt bàn (sáng hơn sàn)
      ctx.fillStyle = "#1f2221"; ctx.fillRect(126, 243, 7, 64); ctx.fillRect(257, 243, 7, 64);
      ctx.fillStyle = "#151817"; ctx.fillRect(158, 204, 50, 30); ctx.fillRect(180, 230, 6, 5); // màn hình
      ctx.fillStyle = "#0e100f"; ctx.fillRect(222, 228, 20, 6); // điện thoại
      // sofa
      ctx.fillStyle = "#6f7673"; // lưng sofa
      ctx.beginPath(); ctx.roundRect(400, 214, 190, 40, 10); ctx.fill();
      ctx.fillStyle = "#8a918e"; // đệm ngồi
      ctx.beginPath(); ctx.roundRect(392, 250, 206, 30, 8); ctx.fill();
      ctx.fillStyle = "#565c5a"; ctx.fillRect(392, 278, 206, 22);
      ctx.fillStyle = "#1c1f1e"; ctx.fillRect(400, 300, 8, 8); ctx.fillRect(582, 300, 8, 8);

      // người đi lại (bóng đen, chuyển động thật chậm)
      const px = 330 + Math.sin(t * 0.35) * 70;
      const step = Math.sin(t * 2.2) * 3;
      ctx.fillStyle = "#171a19";
      ctx.beginPath(); ctx.arc(px, 152, 13, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.roundRect(px - 19, 168, 38, 72, 9); ctx.fill();
      ctx.fillRect(px - 15, 236, 12, 66 + step); ctx.fillRect(px + 3, 236, 12, 66 - step);

      // hạt nhiễu + vệt quét mờ + tối góc
      ctx.drawImage(grain, -((t * 97) % 160), -((t * 53) % 160), 160 * 6, 160 * 4);
      const sy = ((t * 40) % (h + 60)) - 30;
      ctx.fillStyle = "rgba(255,255,255,.035)"; ctx.fillRect(0, sy, 640, 18);
      gr = ctx.createRadialGradient(320, h / 2, h * 0.35, 320, h / 2, h * 0.95);
      gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(0,0,0,.45)");
      ctx.fillStyle = gr; ctx.fillRect(0, 0, 640, h);

      // khung nhận diện (mảnh, màu quy ước của hệ thống)
      const box = (x: number, y: number, w: number, hh: number, color: string, text: string, above = true) => {
        ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, w, hh);
        ctx.font = "500 10px 'JetBrains Mono', ui-monospace, monospace";
        const tw = ctx.measureText(text).width + 8;
        const ty = above ? y - 14 : y + hh;
        ctx.fillStyle = color; ctx.fillRect(x - 0.75, ty, tw, 14);
        ctx.fillStyle = "#0c0e0d"; ctx.fillText(text, x + 3, ty + 10.5);
      };
      box(px - 16, 136, 32, 34, "#7fd1ae", "Bé Na 0.81");
      box(216, 225, 32, 16, "#9cc3ff", "điện thoại 0.71", false);

      // OSD giống đầu ghi: ngày giờ trên-trái, tên camera dưới-phải
      const d = new Date();
      const osd = `${pad(d.getDate())}-${pad(d.getMonth() + 1)}-${d.getFullYear()} ${DOW[d.getDay()]} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
      ctx.font = "500 13px 'JetBrains Mono', ui-monospace, monospace";
      ctx.lineWidth = 3; ctx.strokeStyle = "rgba(0,0,0,.75)"; ctx.fillStyle = "#f2f4f3";
      ctx.strokeText(osd, 14, 24); ctx.fillText(osd, 14, 24);
      const lw = ctx.measureText(label).width;
      ctx.strokeText(label, 626 - lw, h - 14); ctx.fillText(label, 626 - lw, h - 14);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
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
