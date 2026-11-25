import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
// Font tự host (Fontsource): không chặn hiển thị, không phụ thuộc máy chủ ngoài; trình duyệt chỉ tải phần chữ Việt/Latin cần dùng.
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource/be-vietnam-pro/400.css";
import "@fontsource/be-vietnam-pro/500.css";
import "@fontsource/be-vietnam-pro/600.css";
import "@fontsource/be-vietnam-pro/700.css";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/500.css";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
