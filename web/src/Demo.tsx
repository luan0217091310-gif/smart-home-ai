import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { chat, getHomeUrl, health, imageUrl, setHomeUrl, snapshotUrl } from "./api";
import { accessLog, ago, initialAlerts, initialObjects, members, SERVICES, type Alert, type TrackedObject } from "./data";
import { demoAnswer } from "./demoAssistant";
import { LiveFeed } from "./LiveFeed";

type Tab = "live" | "members" | "objects" | "chat";
const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "live", label: "Live & Cảnh báo", icon: "◉" },
  { id: "members", label: "Thành viên", icon: "☺" },
  { id: "objects", label: "Đồ vật & Vùng", icon: "⌖" },
  { id: "chat", label: "Trợ lý", icon: "✦" },
];
const ALERT_META = {
  stranger: { label: "Người lạ", cls: "warn" },
  fall: { label: "Té ngã", cls: "danger" },
  system: { label: "Hệ thống", cls: "info" },
} as const;
const STATUS_VN = { new: "Mới", sent: "Đã gửi", acknowledged: "Đã xem", false_alarm: "Báo giả" };

interface Msg { role: "user" | "bot"; text: string; image?: string; tool?: string }
interface Toast { id: number; tone: "warn" | "danger" | "info"; title: string; body: string }
type SimKind = "stranger" | "fall" | "phone";

export function Demo() {
  const [tab, setTab] = useState<Tab>("live");
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts);
  const [objects, setObjects] = useState<TrackedObject[]>(initialObjects);
  const [home, setHome] = useState(getHomeUrl());
  const [homeState, setHomeState] = useState<"off" | "checking" | "ok" | "error">(home ? "checking" : "off");
  const [homeInfo, setHomeInfo] = useState("");
  const [snap, setSnap] = useState<string | undefined>();
  const [showConnect, setShowConnect] = useState(false);
  const [hb, setHb] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setHb((x) => x + 1), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!home) return setHomeState("off");
    setHomeState("checking");
    health(home)
      .then((h) => { setHomeState("ok"); setHomeInfo(`LLM: ${h.llm}`); })
      .catch((e) => { setHomeState("error"); setHomeInfo(String(e.message ?? e)); });
  }, [home]);

  useEffect(() => {
    if (homeState !== "ok") return setSnap(undefined);
    const load = () => setSnap(snapshotUrl(home));
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, [homeState, home]);

  const counts = useMemo(() => ({
    today: alerts.filter((a) => a.minutesAgo < 1440).length,
    open: alerts.filter((a) => a.status === "new" || a.status === "sent").length,
  }), [alerts]);

  const setStatus = (id: number, status: Alert["status"]) =>
    setAlerts((xs) => xs.map((a) => (a.id === id ? { ...a, status } : a)));

  // ---- Mô phỏng sự kiện + thông báo bật lên (chỉ ở chế độ demo)
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [flash, setFlash] = useState<"" | "warn" | "danger" | "info">("");
  const pushToast = (t: Omit<Toast, "id">) => {
    const id = Date.now() + Math.random();
    setToasts((xs) => [...xs.slice(-2), { ...t, id }]);
    setTimeout(() => setToasts((xs) => xs.filter((x) => x.id !== id)), 4800);
  };
  const simulate = (kind: SimKind) => {
    const now = new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    if (kind === "phone") {
      const zones = ["Bàn làm việc", "Ghế sofa", "Kệ cửa ra vào", "Bàn ăn"];
      const zone = zones[Math.floor(Math.random() * zones.length)];
      setObjects((xs) => xs.map((o) => (o.keyword === "cell phone" ? { ...o, zone, lastSeenMin: 0, confidence: 0.6 + Math.random() * 0.3 } : o)));
      setFlash("info");
      pushToast({ tone: "info", title: "Đã cập nhật vị trí", body: `Điện thoại → ${zone} lúc ${now}` });
    } else {
      const fall = kind === "fall";
      const message = fall ? "KHẨN: người té ngã và nằm yên ở phòng khách" : `Phát hiện người lạ ở cửa chính (độ tương đồng ${(Math.random() * 0.2).toFixed(2)})`;
      setAlerts((xs) => [{ id: Math.max(0, ...xs.map((a) => a.id)) + 1, type: fall ? "fall" : "stranger", message, minutesAgo: 0, status: "sent" }, ...xs]);
      setFlash(fall ? "danger" : "warn");
      pushToast({ tone: fall ? "danger" : "warn", title: fall ? "🆘 Telegram · Cảnh báo khẩn" : "🚨 Telegram · Người lạ", body: `${message} — ${now}` });
    }
    setTimeout(() => setFlash(""), 1600);
  };

  return (
    <div className="demo" id="demo">
      <div className="demo-bar">
        <div className="dots"><i /><i /><i /></div>
        <div className="demo-url mono">{homeState === "ok" ? home : "demo.smart-home-ai · dữ liệu mẫu"}</div>
        <button className={`conn ${homeState}`} onClick={() => setShowConnect((v) => !v)}>
          <span className="pulse" />
          {homeState === "ok" ? "Đã nối máy nhà" : homeState === "checking" ? "Đang kiểm tra…" : homeState === "error" ? "Không nối được" : "Chế độ demo"}
        </button>
      </div>

      {showConnect && (
        <ConnectPanel
          value={home}
          state={homeState}
          info={homeInfo}
          onSave={(u) => { setHomeUrl(u); setHome(u.trim().replace(/\/+$/, "")); }}
        />
      )}

      <div className="demo-body">
        <nav className="side" aria-label="Tab dashboard">
          {TABS.map((t) => (
            <button key={t.id} className={tab === t.id ? "active" : ""} onClick={() => setTab(t.id)}>
              <span className="ico">{t.icon}</span>
              <span>{t.label}</span>
              {t.id === "live" && counts.open > 0 && <b className="badge">{counts.open}</b>}
            </button>
          ))}
        </nav>

        <section className="panel">
          {tab === "live" && (
            <div className="live-grid">
              <div>
                <div className={`feed-wrap ${flash}`}><LiveFeed snapshotSrc={snap} /></div>
                {homeState !== "ok" && (
                  <div className="sim" role="group" aria-label="Mô phỏng sự kiện">
                    <span>Mô phỏng:</span>
                    <button className="ghost" onClick={() => simulate("stranger")}>🚨 Người lạ</button>
                    <button className="ghost" onClick={() => simulate("fall")}>🆘 Té ngã</button>
                    <button className="ghost" onClick={() => simulate("phone")}>📱 Thấy điện thoại</button>
                  </div>
                )}
                <div className="stats">
                  <Stat n={String(counts.today)} label="Cảnh báo hôm nay" />
                  <Stat n={String(members.length)} label="Thành viên" />
                  <Stat n={String(objects.filter((o) => o.active).length)} label="Đồ vật theo dõi" />
                  <Stat n="< 200 ms" label="Độ trễ hệ thống" />
                </div>
              </div>
              <div className="col">
                <h4>Trạng thái service</h4>
                <ul className="svc">
                  {SERVICES.map((s, i) => (
                    <li key={s.id}>
                      <span className="led" />
                      <span className="mono">{s.id}</span>
                      <small>{s.label} · {s.fps} · {((hb + i * 2) % 9) + 1}s</small>
                    </li>
                  ))}
                </ul>
                <h4>Cảnh báo</h4>
                <ul className="alerts">
                  {alerts.map((a) => (
                    <li key={a.id} className={a.status === "false_alarm" ? "muted" : ""}>
                      <div className="row">
                        <span className={`chip ${ALERT_META[a.type].cls}`}>{ALERT_META[a.type].label}</span>
                        <small>{ago(a.minutesAgo)} · {STATUS_VN[a.status]}</small>
                      </div>
                      <p>{a.message}</p>
                      <div className="row gap">
                        <button className="ghost" disabled={a.status === "acknowledged"} onClick={() => setStatus(a.id, "acknowledged")}>✓ Đã xem</button>
                        <button className="ghost" disabled={a.status === "false_alarm"} onClick={() => setStatus(a.id, "false_alarm")}>⊘ Báo giả</button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {tab === "members" && (
            <div className="two">
              <div>
                <h4>Thành viên đã đăng ký</h4>
                <ul className="cards">
                  {members.map((m) => (
                    <li key={m.name} className="member">
                      <div className="avatar">{m.name.split(" ").pop()![0]}</div>
                      <div>
                        <b>{m.name}</b>
                        <small>{m.role} · {m.images} ảnh mẫu · thấy {ago(m.lastSeenMin)}</small>
                      </div>
                    </li>
                  ))}
                </ul>
                <div className="note">Thêm người: tải 5–10 ảnh rõ mặt + xác nhận đồng ý → <span className="mono">worker_face</span> tự đăng ký trong vài giây, không cần gõ lệnh.</div>
              </div>
              <div>
                <h4>Lịch sử ra vào hôm nay</h4>
                <table>
                  <thead><tr><th>Giờ</th><th>Người</th><th>Tương đồng</th></tr></thead>
                  <tbody>
                    {accessLog.map((l, i) => (
                      <tr key={i}>
                        <td className="mono">{l.time}</td>
                        <td>{l.name === "Người lạ" ? <span className="chip warn">Người lạ</span> : l.name}</td>
                        <td><Meter v={l.score} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {tab === "objects" && <Objects objects={objects} setObjects={setObjects} />}

          {tab === "chat" && (
            <Chat home={homeState === "ok" ? home : ""} objects={objects} alerts={alerts}
              addObject={(vn, en) => setObjects((xs) => [...xs, { name: vn, keyword: en, zone: null, lastSeenMin: null, confidence: 0, active: true }])} />
          )}
        </section>
      </div>
      {createPortal(
        <div className="toasts" role="status" aria-live="polite">
          {toasts.map((t) => (
            <div key={t.id} className={`toast ${t.tone}`}><b>{t.title}</b><span>{t.body}</span></div>
          ))}
        </div>,
        document.body,
      )}
    </div>
  );
}

function Stat({ n, label }: { n: string; label: string }) {
  return <div className="stat"><b>{n}</b><small>{label}</small></div>;
}

function Meter({ v }: { v: number }) {
  const cls = v >= 0.45 ? "ok" : v < 0.25 ? "bad" : "mid";
  return (
    <span className="meter"><span className={cls} style={{ width: `${Math.round(v * 100)}%` }} /><em className="mono">{v.toFixed(2)}</em></span>
  );
}

function Objects({ objects, setObjects }: { objects: TrackedObject[]; setObjects: (f: (x: TrackedObject[]) => TrackedObject[]) => void }) {
  const [vn, setVn] = useState("");
  const [en, setEn] = useState("");
  const valid = vn.trim() && /^[\x20-\x7e]+$/.test(en.trim());
  return (
    <div>
      <h4>Đồ vật đang theo dõi <small className="muted-txt">— YOLOE-26, đổi danh sách không cần train lại</small></h4>
      <div className="obj-grid">
        {objects.map((o, i) => (
          <div key={o.name + i} className={`obj ${o.active ? "" : "off"}`}>
            <div className="row"><b>{o.name}</b><span className="mono tag">{o.keyword}</span></div>
            <div className="zone">{o.zone ?? "—"}</div>
            <small>{o.lastSeenMin === null ? "Chưa thấy lần nào" : `Thấy ${ago(o.lastSeenMin)} · ${o.confidence.toFixed(2)}`}</small>
            <button className="ghost" onClick={() => setObjects((xs) => xs.map((x, j) => (j === i ? { ...x, active: !x.active } : x)))}>
              {o.active ? "Ngừng theo dõi" : "Theo dõi lại"}
            </button>
          </div>
        ))}
      </div>
      <form className="add" onSubmit={(e) => {
        e.preventDefault();
        if (!valid) return;
        setObjects((xs) => [...xs, { name: vn.trim(), keyword: en.trim().toLowerCase(), zone: null, lastSeenMin: null, confidence: 0, active: true }]);
        setVn(""); setEn("");
      }}>
        <input placeholder="Tên tiếng Việt — vd. Mũ bảo hiểm" value={vn} onChange={(e) => setVn(e.target.value)} />
        <input placeholder="Từ khóa tiếng Anh — vd. helmet" value={en} onChange={(e) => setEn(e.target.value)} />
        <button className="primary" disabled={!valid}>+ Thêm</button>
      </form>
      <div className="zones-legend">
        <span><i className="z furniture" />furniture</span>
        <span><i className="z safe" />safe_rest — nằm ở đây không báo té ngã</span>
        <span><i className="z floor" />floor</span>
        <span><i className="z door" />door</span>
      </div>
    </div>
  );
}

const SUGGESTIONS = ["Nãy giờ có ai vào nhà không?", "Điện thoại của tôi đâu?", "Hôm nay có cảnh báo gì không?", "Chụp ảnh nhà hiện tại", "Theo dõi thêm cái mũ bảo hiểm", "Cái ô của tôi đâu?"];

function Chat({ home, objects, alerts, addObject }: { home: string; objects: TrackedObject[]; alerts: Alert[]; addObject: (vn: string, en: string) => void }) {
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "bot", text: home ? "Dạ, em đã nối với máy nhà. Anh/chị hỏi gì ạ?" : "Xin chào! Em là trợ lý trông nhà (bản demo, dữ liệu mẫu). Anh/chị thử hỏi em nhé." },
  ]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => {
    // Chrome mới: scrollIntoView() trả về Promise — không được trả nó ra khỏi effect.
    end.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [msgs]);

  const send = async (text: string) => {
    if (!text.trim() || busy) return;
    setMsgs((m) => [...m, { role: "user", text }]);
    setQ("");
    setBusy(true);
    try {
      if (home) {
        const r = await chat(home, text);
        setMsgs((m) => [...m, { role: "bot", text: r.answer, image: r.images?.[0] ? imageUrl(home, r.images[0]) : undefined, tool: r.llm }]);
      } else {
        await new Promise((r) => setTimeout(r, 450));
        const r = demoAnswer(text, objects, alerts, addObject);
        setMsgs((m) => [...m, { role: "bot", text: r.text, tool: r.tool, image: r.snapshot ? "snapshot" : undefined }]);
      }
    } catch (e) {
      setMsgs((m) => [...m, { role: "bot", text: `Không gọi được máy nhà: ${(e as Error).message}` }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="chat">
      <div className="msgs">
        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <p>{m.text}</p>
            {m.image === "snapshot" ? <div className="mini-feed"><LiveFeed /></div> : m.image && <img src={m.image} alt="" />}
            {m.tool && m.role === "bot" && <small className="mono">⚙ {m.tool}</small>}
          </div>
        ))}
        {busy && <div className="msg bot typing"><i /><i /><i /></div>}
        <div ref={end} />
      </div>
      <div className="sugs">
        {SUGGESTIONS.map((s) => <button key={s} className="sug" onClick={() => send(s)}>{s}</button>)}
      </div>
      <form className="ask" onSubmit={(e) => { e.preventDefault(); send(q); }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Hỏi bằng tiếng Việt, có dấu hay không dấu đều được…" />
        <button className="primary" disabled={busy || !q.trim()}>Gửi</button>
      </form>
    </div>
  );
}

function ConnectPanel({ value, state, info, onSave }: { value: string; state: string; info: string; onSave: (u: string) => void }) {
  const [v, setV] = useState(value);
  return (
    <div className="connect">
      <div>
        <b>Kết nối máy chủ trong nhà</b>
        <p>Mở trang này <b>trên chính máy nhà</b> bằng <span className="mono">cd web &amp;&amp; npm run dev</span> (http://localhost:5173), rồi nhập <span className="mono">/home-api</span>. Địa chỉ chỉ lưu trong trình duyệt của bạn.</p>
        {state === "error" && <p className="err">Không kết nối được ({info}). Kiểm tra: hệ thống đã bật (<span className="mono">start.ps1</span>) và bạn đang mở trang tại localhost:5173, không phải bản trên Internet.</p>}
        {state === "ok" && <p className="okk">Đã kết nối · {info}. Tab Live hiện ảnh thật, tab Trợ lý hỏi hệ thống thật.</p>}
      </div>
      <form onSubmit={(e) => { e.preventDefault(); onSave(v); }}>
        <input value={v} onChange={(e) => setV(e.target.value)} placeholder="/home-api" />
        <button className="primary">Lưu</button>
        {value && <button type="button" className="ghost" onClick={() => { setV(""); onSave(""); }}>Về demo</button>}
      </form>
    </div>
  );
}
