import { useState, useEffect } from "react";

const PRIORITIES = ["高", "中", "低"];
const CATEGORIES = ["経営", "営業", "財務", "人事", "その他"];
const STATUS_LIST = ["未着手", "進行中", "完了"];

const STATUS_COLORS = {
  "未着手": { bg: "#f5d6e8", border: "#d4a0c0", text: "#8a4a6a" },
  "進行中": { bg: "#dce8f5", border: "#90b8e0", text: "#2a6090" },
  "完了": { bg: "#d8f0e0", border: "#80c8a0", text: "#2a7a50" },
};

const PRIORITY_COLORS = {
  "高": "#ff4d6d",
  "中": "#ffb347",
  "低": "#4db8ff",
};

function getDaysUntil(dateStr) {
  const today = new Date(); today.setHours(0,0,0,0);
  const due = new Date(dateStr); due.setHours(0,0,0,0);
  return Math.ceil((due - today) / (1000 * 60 * 60 * 24));
}

function DeadlineBadge({ dateStr }) {
  const days = getDaysUntil(dateStr);
  let color = "#4db8ff", label = `${days}日後`;
  if (days < 0) { color = "#888"; label = `${Math.abs(days)}日超過`; }
  else if (days === 0) { color = "#ff4d6d"; label = "本日締切"; }
  else if (days <= 3) { color = "#ff4d6d"; }
  else if (days <= 7) { color = "#ffb347"; }
  return (
    <span style={{ color, fontSize: "0.72rem", fontFamily: "'Noto Sans JP', sans-serif", fontWeight: 600, letterSpacing: "0.03em" }}>
      {label}
    </span>
  );
}

const initialTasks = [
  { id: 1, title: "第2四半期 経営会議資料作成", deadline: new Date(Date.now() + 2 * 86400000).toISOString().split("T")[0], priority: "高", category: "経営", status: "進行中", memo: "" },
  { id: 2, title: "新規取引先との契約書確認", deadline: new Date(Date.now() + 5 * 86400000).toISOString().split("T")[0], priority: "高", category: "営業", status: "未着手", memo: "" },
  { id: 3, title: "スタッフ給与計算・振込", deadline: new Date(Date.now() + 10 * 86400000).toISOString().split("T")[0], priority: "中", category: "財務", status: "未着手", memo: "" },
];

export default function App() {
  const [tasks, setTasks] = useState(() => {
    try { const s = localStorage.getItem("ceo_tasks"); return s ? JSON.parse(s) : initialTasks; } catch { return initialTasks; }
  });
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [filterStatus, setFilterStatus] = useState("すべて");
  const [filterPriority, setFilterPriority] = useState("すべて");
  const [sortBy, setSortBy] = useState("deadline");
  const [form, setForm] = useState({ title: "", deadline: "", priority: "高", category: "経営", status: "未着手", memo: "" });
  const [nextId, setNextId] = useState(100);
  const [confirmDelete, setConfirmDelete] = useState(null);

  useEffect(() => {
    try { localStorage.setItem("ceo_tasks", JSON.stringify(tasks)); } catch {}
  }, [tasks]);

  const openAdd = () => {
    setForm({ title: "", deadline: "", priority: "高", category: "経営", status: "未着手", memo: "" });
    setEditId(null);
    setShowForm(true);
  };

  const openEdit = (task) => {
    setForm({ ...task });
    setEditId(task.id);
    setShowForm(true);
  };

  const saveTask = () => {
    if (!form.title.trim() || !form.deadline) return;
    if (editId !== null) {
      setTasks(t => t.map(x => x.id === editId ? { ...form, id: editId } : x));
    } else {
      setTasks(t => [...t, { ...form, id: nextId }]);
      setNextId(n => n + 1);
    }
    setShowForm(false);
  };

  const deleteTask = (id) => {
    setTasks(t => t.filter(x => x.id !== id));
    setConfirmDelete(null);
  };

  const cycleStatus = (id) => {
    setTasks(t => t.map(x => {
      if (x.id !== id) return x;
      const i = STATUS_LIST.indexOf(x.status);
      return { ...x, status: STATUS_LIST[(i + 1) % STATUS_LIST.length] };
    }));
  };

  let filtered = tasks.filter(t =>
    (filterStatus === "すべて" || t.status === filterStatus) &&
    (filterPriority === "すべて" || t.priority === filterPriority)
  );

  filtered = [...filtered].sort((a, b) => {
    if (sortBy === "deadline") return new Date(a.deadline) - new Date(b.deadline);
    if (sortBy === "priority") return PRIORITIES.indexOf(a.priority) - PRIORITIES.indexOf(b.priority);
    return 0;
  });

  const stats = {
    total: tasks.length,
    urgent: tasks.filter(t => t.status !== "完了" && getDaysUntil(t.deadline) <= 3).length,
    inProgress: tasks.filter(t => t.status === "進行中").length,
    done: tasks.filter(t => t.status === "完了").length,
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #f8d8ec 0%, #f2c8e4 50%, #f8d0e8 100%)",
      fontFamily: "'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif",
      color: "#3a1a2e",
      padding: "0",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Cormorant+Garamond:wght@300;400;600&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #f8d8ec; } ::-webkit-scrollbar-thumb { background: #d4a0c0; border-radius: 2px; }
        .task-row:hover { background: #fce8f4 !important; }
        .btn-icon:hover { opacity: 0.7; }
        .status-pill:hover { cursor: pointer; opacity: 0.85; }
        .filter-btn { background: none; border: 1px solid #d4a0c0; color: #9a5a7a; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; font-family: inherit; }
        .filter-btn.active { border-color: #c060a0; background: #f0c0dc; color: #7a2060; }
        input, select, textarea { background: #fff0f8; border: 1px solid #d4a0c0; color: #3a1a2e; border-radius: 6px; padding: 8px 12px; font-family: inherit; font-size: 0.85rem; outline: none; transition: border 0.2s; }
        input:focus, select:focus, textarea:focus { border-color: #c060a0; }
        select option { background: #fff0f8; color: #3a1a2e; }
        .overlay { position: fixed; inset: 0; background: rgba(180,80,140,0.25); z-index: 100; display: flex; align-items: center; justify-content: center; }
        .modal { background: #fdf0f8; border: 1px solid #d4a0c0; border-radius: 12px; padding: 32px; width: 480px; max-width: 95vw; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeIn 0.3s ease; }
      `}</style>

      <div style={{ borderBottom: "1px solid #d4a0c0", padding: "20px 32px", display: "flex", alignItems: "center", justifyContent: "space-between", position: "sticky", top: 0, background: "rgba(248,216,236,0.92)", backdropFilter: "blur(8px)", zIndex: 10 }}>
        <div>
          <div style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: "1.6rem", fontWeight: 300, letterSpacing: "0.12em", color: "#7a2060" }}>EXECUTIVE TASKS</div>
          <div style={{ fontSize: "0.7rem", color: "#b080a0", letterSpacing: "0.2em", marginTop: 2 }}>スケジュール管理</div>
        </div>
        <button onClick={openAdd} style={{ background: "linear-gradient(135deg, #c060a0, #a04080)", border: "1px solid #a04080", color: "#fff", padding: "10px 22px", borderRadius: "8px", cursor: "pointer", fontSize: "0.82rem", letterSpacing: "0.08em", fontFamily: "inherit", display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: "1.1rem", lineHeight: 1 }}>＋</span> タスク追加
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, padding: "20px 32px 0" }}>
        {[
          { label: "総タスク", value: stats.total, color: "#9a6080" },
          { label: "要注意（3日以内）", value: stats.urgent, color: "#ff4d6d" },
          { label: "進行中", value: stats.inProgress, color: "#2a6090" },
          { label: "完了", value: stats.done, color: "#2a7a50" },
        ].map(s => (
          <div key={s.label} style={{ background: "rgba(255,255,255,0.55)", border: "1px solid #d4a0c0", borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: "1.8rem", fontFamily: "'Cormorant Garamond', serif", fontWeight: 600, color: s.color, lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: "0.68rem", color: "#9a6080", marginTop: 5, letterSpacing: "0.08em" }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ padding: "16px 32px", display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: "0.7rem", color: "#9a6080", marginRight: 4, letterSpacing: "0.1em" }}>ステータス：</span>
        {["すべて", ...STATUS_LIST].map(s => (
          <button key={s} className={`filter-btn${filterStatus === s ? " active" : ""}`} onClick={() => setFilterStatus(s)}>{s}</button>
        ))}
        <span style={{ fontSize: "0.7rem", color: "#9a6080", marginLeft: 12, marginRight: 4, letterSpacing: "0.1em" }}>優先度：</span>
        {["すべて", ...PRIORITIES].map(p => (
          <button key={p} className={`filter-btn${filterPriority === p ? " active" : ""}`} onClick={() => setFilterPriority(p)}>{p}</button>
        ))}
        <span style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: "0.7rem", color: "#9a6080", letterSpacing: "0.1em" }}>並び替え：</span>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)} style={{ padding: "4px 8px", fontSize: "0.75rem" }}>
            <option value="deadline">締め切り順</option>
            <option value="priority">優先度順</option>
          </select>
        </span>
      </div>

      <div style={{ padding: "0 32px 40px" }}>
        {filtered.length === 0 ? (
          <div style={{ textAlign: "center", color: "#9a6080", padding: "60px 0", fontSize: "0.9rem" }}>タスクがありません</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {filtered.map(task => {
              const sc = STATUS_COLORS[task.status];
              const days = getDaysUntil(task.deadline);
              const isUrgent = task.status !== "完了" && days <= 3 && days >= 0;
              return (
                <div key={task.id} className="task-row fade-in" style={{
                  background: "rgba(255,255,255,0.5)",
                  border: `1px solid ${isUrgent ? "#e06080" : "#d4a0c0"}`,
                  borderLeft: `3px solid ${PRIORITY_COLORS[task.priority]}`,
                  borderRadius: 10,
                  padding: "14px 18px",
                  display: "grid",
                  gridTemplateColumns: "1fr auto auto auto",
                  gap: 12,
                  alignItems: "center",
                  transition: "background 0.15s",
                }}>
                  <div>
                    <div style={{ fontSize: "0.9rem", fontWeight: 500, color: task.status === "完了" ? "#c0a0b0" : "#3a1a2e", textDecoration: task.status === "完了" ? "line-through" : "none", marginBottom: 5 }}>{task.title}</div>
                    <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                      <span style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.05em" }}>📅 {task.deadline}</span>
                      <DeadlineBadge dateStr={task.deadline} />
                      <span style={{ fontSize: "0.7rem", background: "#f0d0e4", color: "#8a4a6a", padding: "1px 8px", borderRadius: 10 }}>{task.category}</span>
                      {task.memo && <span style={{ fontSize: "0.7rem", color: "#b08090" }}>📝 メモあり</span>}
                    </div>
                  </div>
                  <div className="status-pill" onClick={() => cycleStatus(task.id)} style={{
                    background: sc.bg, border: `1px solid ${sc.border}`, color: sc.text,
                    padding: "4px 12px", borderRadius: 20, fontSize: "0.72rem", fontWeight: 600,
                    letterSpacing: "0.05em", whiteSpace: "nowrap", userSelect: "none",
                  }} title="クリックでステータス変更">{task.status}</div>
                  <button className="btn-icon" onClick={() => openEdit(task)} style={{ background: "none", border: "none", color: "#5050a0", cursor: "pointer", fontSize: "1rem", padding: "4px 6px" }} title="編集">✏️</button>
                  <button className="btn-icon" onClick={() => setConfirmDelete(task.id)} style={{ background: "none", border: "none", color: "#6a2030", cursor: "pointer", fontSize: "1rem", padding: "4px 6px" }} title="削除">🗑️</button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {showForm && (
        <div className="overlay" onClick={e => { if (e.target === e.currentTarget) setShowForm(false); }}>
          <div className="modal fade-in">
            <div style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: "1.2rem", fontWeight: 300, color: "#7a2060", marginBottom: 24, letterSpacing: "0.1em" }}>
              {editId !== null ? "タスクを編集" : "新規タスク"}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.1em", display: "block", marginBottom: 5 }}>タスク名 *</label>
                <input style={{ width: "100%" }} value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="タスクのタイトルを入力" />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div>
                  <label style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.1em", display: "block", marginBottom: 5 }}>締め切り *</label>
                  <input type="date" style={{ width: "100%" }} value={form.deadline} onChange={e => setForm(f => ({ ...f, deadline: e.target.value }))} />
                </div>
                <div>
                  <label style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.1em", display: "block", marginBottom: 5 }}>優先度</label>
                  <select style={{ width: "100%" }} value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}>
                    {PRIORITIES.map(p => <option key={p}>{p}</option>)}
                  </select>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div>
                  <label style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.1em", display: "block", marginBottom: 5 }}>カテゴリ</label>
                  <select style={{ width: "100%" }} value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}>
                    {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.1em", display: "block", marginBottom: 5 }}>ステータス</label>
                  <select style={{ width: "100%" }} value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                    {STATUS_LIST.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label style={{ fontSize: "0.72rem", color: "#9a6080", letterSpacing: "0.1em", display: "block", marginBottom: 5 }}>メモ</label>
                <textarea style={{ width: "100%", height: 72, resize: "vertical" }} value={form.memo} onChange={e => setForm(f => ({ ...f, memo: e.target.value }))} placeholder="備考・メモを入力" />
              </div>
            </div>
            <div style={{ display: "flex", gap: 10, marginTop: 24, justifyContent: "flex-end" }}>
              <button onClick={() => setShowForm(false)} style={{ background: "none", border: "1px solid #d4a0c0", color: "#9a6080", padding: "9px 20px", borderRadius: 8, cursor: "pointer", fontFamily: "inherit", fontSize: "0.82rem" }}>キャンセル</button>
              <button onClick={saveTask} disabled={!form.title.trim() || !form.deadline} style={{ background: "linear-gradient(135deg, #c060a0, #a04080)", border: "1px solid #a04080", color: "#fff", padding: "9px 24px", borderRadius: 8, cursor: "pointer", fontFamily: "inherit", fontSize: "0.82rem", opacity: (!form.title.trim() || !form.deadline) ? 0.4 : 1 }}>
                {editId !== null ? "更新" : "追加"}
              </button>
            </div>
          </div>
        </div>
      )}

      {confirmDelete !== null && (
        <div className="overlay" onClick={e => { if (e.target === e.currentTarget) setConfirmDelete(null); }}>
          <div className="modal fade-in" style={{ maxWidth: 360, textAlign: "center" }}>
            <div style={{ fontSize: "1.8rem", marginBottom: 12 }}>🗑️</div>
            <div style={{ fontSize: "0.9rem", color: "#3a1a2e", marginBottom: 8 }}>このタスクを削除しますか？</div>
            <div style={{ fontSize: "0.75rem", color: "#9a6080", marginBottom: 24 }}>この操作は元に戻せません。</div>
            <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
              <button onClick={() => setConfirmDelete(null)} style={{ background: "none", border: "1px solid #d4a0c0", color: "#9a6080", padding: "9px 20px", borderRadius: 8, cursor: "pointer", fontFamily: "inherit", fontSize: "0.82rem" }}>キャンセル</button>
              <button onClick={() => deleteTask(confirmDelete)} style={{ background: "#fde0e8", border: "1px solid #e06080", color: "#c02040", padding: "9px 24px", borderRadius: 8, cursor: "pointer", fontFamily: "inherit", fontSize: "0.82rem" }}>削除する</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}