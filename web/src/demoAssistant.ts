// Trợ lý DEMO chạy ngay trong trình duyệt, trả lời từ dữ liệu mẫu — mô phỏng cách bản thật gọi công cụ CSDL.
import { accessLog, ago, fold, members, type Alert, type TrackedObject } from "./data";

export interface DemoReply {
  text: string;
  tool: string;
  snapshot?: boolean;
}

const GUESS_EN: Record<string, string> = {
  "mu bao hiem": "helmet", "o": "umbrella", "cai o": "umbrella", "dieu khien": "remote", "balo": "backpack",
  "coc": "cup", "coc nuoc": "cup", "sach": "book", "laptop": "laptop", "chai nuoc": "bottle",
};

export function demoAnswer(q: string, objects: TrackedObject[], alerts: Alert[],
  addObject: (vn: string, en: string) => void): DemoReply {
  const f = fold(q);

  if (/(chup|xem nha|anh nha|hien tai)/.test(f)) {
    return { text: "Dạ, em gửi anh/chị ảnh nhà vừa chụp ạ.", tool: "get_live_snapshot", snapshot: true };
  }
  const add = f.match(/theo doi (them )?(cai |chiec |con )?(.+)/);
  if (add && /(them|giup)/.test(f)) {
    const raw = add[3].replace(/[?.!]/g, "").trim();
    const vn = q.trim().split(/\s+/).slice(-raw.split(" ").length).join(" ").replace(/[?.!]/g, "");
    const name = vn.charAt(0).toUpperCase() + vn.slice(1);
    if (objects.some((o) => fold(o.name) === raw)) {
      return { text: `${name} đã có trong danh sách theo dõi rồi ạ.`, tool: "register_new_object" };
    }
    const en = GUESS_EN[raw] ?? raw.split(" ").pop()!;
    addObject(name, en);
    return { text: `Dạ, em đã thêm "${name}" (từ khóa "${en}"). Camera sẽ tìm ở chu kỳ quét kế tiếp, không cần train lại.`, tool: "register_new_object" };
  }
  if (/(canh bao|bao dong|nga)/.test(f)) {
    const today = alerts.filter((a) => a.minutesAgo < 24 * 60 && a.status !== "false_alarm");
    if (!today.length) return { text: "Dạ, hôm nay không có cảnh báo nào ạ.", tool: "get_recent_alerts" };
    return { text: `Dạ, hôm nay có ${today.length} cảnh báo: ` + today.map((a) => `${a.message.toLowerCase()} (${ago(a.minutesAgo)})`).join("; ") + ".", tool: "get_recent_alerts" };
  }
  if (/(ai vao|ai den|co ai|ai o nha|nguoi la)/.test(f)) {
    const seen = members.filter((m) => m.lastSeenMin <= 120).sort((a, b) => a.lastSeenMin - b.lastSeenMin);
    const strangers = accessLog.filter((l) => l.name === "Người lạ").length;
    return {
      text: `Dạ, nãy giờ có ${seen.map((m) => `${m.name} (${ago(m.lastSeenMin)})`).join(", ")}.` + (strangers ? ` Có ${strangers} lần phát hiện người lạ.` : ""),
      tool: "get_visitors",
    };
  }
  const where = f.match(/(cai |chiec )?(.+?) (cua toi |cua em |cua minh )?(dau|o dau|de dau)/);
  if (where) {
    const wanted = new Set(where[2].split(" ").filter((w) => !["cai", "chiec", "cua", "toi"].includes(w)));
    const o = objects.find((x) => {
      const a = new Set(fold(x.name).split(" "));
      return x.active && ([...wanted].every((w) => a.has(w)) || [...a].every((w) => wanted.has(w)));
    });
    if (!o) return { text: `Dạ, em chưa theo dõi "${where[2]}" nên không biết nó ở đâu. Anh/chị có muốn em theo dõi thêm không?`, tool: "find_object" };
    if (o.lastSeenMin === null) return { text: `Dạ, em đang theo dõi ${o.name} nhưng camera chưa thấy lần nào ạ.`, tool: "find_object" };
    return { text: `Dạ, ${o.name.toLowerCase()} thấy lần cuối ở ${o.zone}, ${ago(o.lastSeenMin)}.`, tool: "find_object" };
  }
  return { text: "Dạ, anh/chị có thể hỏi: ai vào nhà, đồ vật ở đâu, hôm nay có cảnh báo gì, hoặc chụp ảnh nhà hiện tại.", tool: "—" };
}
