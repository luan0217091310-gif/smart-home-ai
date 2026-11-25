// Áp chế độ sáng/tối đã chọn TRƯỚC khi trang hiển thị để không bị nháy màu.
try { var t = localStorage.getItem("sha.theme"); if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t); } catch (e) {}
