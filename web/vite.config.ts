import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Khi chạy trên chính máy nhà (npm run dev / npm run preview), "/home-api" được chuyển tiếp nội bộ tới assistant_api.
// Trình duyệt chỉ nói chuyện với cùng một địa chỉ → không cần mở CORS, không mở gì ra Internet.
const homeApi = { "/home-api": { target: "http://localhost:8000", changeOrigin: true, rewrite: (p: string) => p.replace(/^\/home-api/, "") } };

export default defineConfig({
  plugins: [react()],
  server: { proxy: homeApi },
  preview: { proxy: homeApi },
});
