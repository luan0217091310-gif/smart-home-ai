import { useEffect, useRef } from "react";

// Khung hình camera MÔ PHỎNG (vẽ bằng canvas): phòng khách, người đi lại, khung nhận diện và vùng.
export function LiveFeed({ snapshotSrc }: { snapshotSrc?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (snapshotSrc) return;
    const c = ref.current!;
    const ctx = c.getContext("2d")!;
    let raf = 0;
    const t0 = performance.now();
    const draw = (now: number) => {
      const t = (now - t0) / 1000;
      const W = (c.width = c.clientWidth * devicePixelRatio);
      const H = (c.height = c.clientHeight * devicePixelRatio);
      const s = W / 640;
      ctx.setTransform(s, 0, 0, s, 0, 0);
      const h = H / s;
      // phòng
      const g = ctx.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, "#1c2538");
      g.addColorStop(0.62, "#232e45");
      g.addColorStop(0.62, "#2b2a33");
      g.addColorStop(1, "#1d1c22");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, 640, h);
      // cửa sổ + đèn
      ctx.fillStyle = "rgba(125,170,255,.10)";
      ctx.fillRect(420, 40, 150, 120);
      ctx.strokeStyle = "rgba(160,190,255,.25)";
      ctx.strokeRect(420, 40, 150, 120);
      ctx.beginPath();
      ctx.moveTo(495, 40);
      ctx.lineTo(495, 160);
      ctx.stroke();
      const lamp = ctx.createRadialGradient(120, 50, 2, 120, 50, 90);
      lamp.addColorStop(0, "rgba(255,214,140,.55)");
      lamp.addColorStop(1, "rgba(255,214,140,0)");
      ctx.fillStyle = lamp;
      ctx.fillRect(20, 0, 200, 150);
      // vùng (zones)
      const zone = (x: number, y: number, w: number, hh: number, color: string, label: string) => {
        ctx.fillStyle = color.replace("1)", ".10)");
        ctx.fillRect(x, y, w, hh);
        ctx.setLineDash([6, 5]);
        ctx.strokeStyle = color.replace("1)", ".7)");
        ctx.strokeRect(x, y, w, hh);
        ctx.setLineDash([]);
        ctx.fillStyle = color;
        ctx.font = "600 11px 'Be Vietnam Pro', sans-serif";
        ctx.fillText(label, x + 6, y + 15);
      };
      zone(40, 250, 170, 70, "rgba(251,146,60,1)", "Bàn làm việc");
      zone(390, 235, 210, 95, "rgba(52,211,153,1)", "Ghế sofa · safe_rest");
      // nội thất
      ctx.fillStyle = "#3a3340";
      ctx.fillRect(50, 280, 150, 12);
      ctx.fillRect(60, 292, 8, 50);
      ctx.fillRect(182, 292, 8, 50);
      ctx.fillStyle = "#33424a";
      ctx.beginPath();
      ctx.roundRect(400, 265, 190, 60, 12);
      ctx.fill();
      // điện thoại trên bàn
      ctx.fillStyle = "#0f172a";
      ctx.fillRect(140, 272, 22, 9);
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(134, 266, 34, 20);
      ctx.fillStyle = "#38bdf8";
      ctx.font = "600 10px 'JetBrains Mono', monospace";
      ctx.fillText("cell phone 0.71", 172, 280);
      // người đi lại
      const px = 250 + Math.sin(t * 0.45) * 90;
      ctx.fillStyle = "#c7a58a";
      ctx.beginPath();
      ctx.arc(px, 175, 15, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#4f6d9a";
      ctx.beginPath();
      ctx.roundRect(px - 22, 192, 44, 78, 10);
      ctx.fill();
      ctx.fillStyle = "#2c3a52";
      ctx.fillRect(px - 17, 268, 13, 62 + Math.sin(t * 3) * 4);
      ctx.fillRect(px + 4, 268, 13, 62 - Math.sin(t * 3) * 4);
      // khung mặt + khung người
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#34d399";
      ctx.strokeRect(px - 20, 156, 40, 40);
      ctx.fillStyle = "#34d399";
      ctx.fillRect(px - 20, 138, 108, 18);
      ctx.fillStyle = "#04130d";
      ctx.font = "700 11px 'Be Vietnam Pro', sans-serif";
      ctx.fillText("Bé Na · 0.81", px - 15, 151);
      ctx.strokeStyle = "rgba(167,139,250,.8)";
      ctx.setLineDash([3, 4]);
      ctx.strokeRect(px - 30, 155, 60, 180);
      ctx.setLineDash([]);
      // khung xương (pose)
      ctx.strokeStyle = "rgba(167,139,250,.9)";
      ctx.beginPath();
      ctx.moveTo(px - 16, 200);
      ctx.lineTo(px + 16, 200);
      ctx.moveTo(px, 200);
      ctx.lineTo(px, 262);
      ctx.moveTo(px - 11, 262);
      ctx.lineTo(px + 11, 262);
      ctx.stroke();
      // đường quét
      const sy = ((t * 70) % (h + 40)) - 20;
      const sg = ctx.createLinearGradient(0, sy - 30, 0, sy);
      sg.addColorStop(0, "rgba(56,189,248,0)");
      sg.addColorStop(1, "rgba(56,189,248,.16)");
      ctx.fillStyle = sg;
      ctx.fillRect(0, sy - 30, 640, 30);
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [snapshotSrc]);

  return (
    <div className="feed">
      {snapshotSrc ? <img src={snapshotSrc} alt="Ảnh camera hiện tại từ máy nhà" /> : <canvas ref={ref} aria-label="Khung hình camera mô phỏng" />}
      <div className="feed-hud">
        <span className="rec">● LIVE</span>
        <span className="mono">cam_phongkhach · 15 FPS · 24 ms</span>
      </div>
      {!snapshotSrc && <span className="feed-tag">Mô phỏng</span>}
    </div>
  );
}
