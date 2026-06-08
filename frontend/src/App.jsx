import { useEffect, useState } from "react";
import { apiRequest, checkBackend } from "./api";

const SEV = {
  P0: { c: "#ff5c5c", g: "rgba(255,92,92,0.15)", l: "Critical" },
  P1: { c: "#ff9f43", g: "rgba(255,159,67,0.15)", l: "High" },
  P2: { c: "#ffd93d", g: "rgba(255,217,61,0.12)", l: "Medium" },
  INFO: { c: "#8b9cb3", g: "rgba(139,156,179,0.1)", l: "Info" },
};

const STEPS = ["Detect", "Search", "Analyze", "Recommend"];

const EXAMPLES = [
  { label: "Slow checkout", query: "Customers say checkout is slow — what broke?" },
  { label: "Payment failures", query: "Why did payment failures spike in the last hour?" },
  { label: "Post-deploy errors", query: "Are there errors after the latest deploy?" },
];

function fmtTime(ts) {
  if (!ts) return "—";
  const s = typeof ts === "string" ? ts : String(ts);
  return s.length >= 19 ? s.slice(11, 19) : s.slice(0, 8);
}

function IconRadar() {
  return (
    <svg className="idle-icon" viewBox="0 0 80 80" fill="none">
      <circle cx="40" cy="40" r="32" stroke="url(#rg)" strokeWidth="1.5" opacity="0.35" />
      <circle cx="40" cy="40" r="20" stroke="url(#rg)" strokeWidth="1.5" opacity="0.25" />
      <circle cx="40" cy="40" r="8" stroke="url(#rg)" strokeWidth="1.5" opacity="0.2" />
      <line x1="40" y1="40" x2="40" y2="8" stroke="#22d3ee" strokeWidth="2" strokeLinecap="round" className="sweep" />
      <circle cx="52" cy="28" r="3" fill="#ff9f43" opacity="0.9" />
      <defs>
        <linearGradient id="rg" x1="0" y1="0" x2="80" y2="80">
          <stop stopColor="#22d3ee" />
          <stop offset="1" stopColor="#6366f1" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function IdleState() {
  return (
    <div className="idle">
      <IconRadar />
      <p>No active investigation</p>
    </div>
  );
}

function LoadingState({ step }) {
  return (
    <div className="load">
      <div className="load-track">
        {STEPS.map((s, i) => (
          <div key={s} className={`load-step ${i <= step ? "done" : ""} ${i === step ? "active" : ""}`}>
            <div className="load-dot">{i + 1}</div>
            <span>{s}</span>
          </div>
        ))}
      </div>
      <div className="load-bar">
        <div className="load-fill" style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
      </div>
    </div>
  );
}

function Metric({ label, value, accent }) {
  return (
    <div className="metric">
      <span className="metric-label">{label}</span>
      <span className="metric-value" style={accent ? { color: accent } : undefined}>{value}</span>
    </div>
  );
}

function Dashboard({ result }) {
  const [logsOpen, setLogsOpen] = useState(true);
  const r = result.report;
  if (!r) return null;

  const s = SEV[r.severity] || SEV.INFO;
  const pct = Math.round((r.confidence || 0) * 100);
  const live = result.mode === "elasticsearch" || result.mode === "elastic_mcp";
  const logs = r.evidence || [];

  return (
    <div className="dash">
      <div className="metrics">
        <Metric label="Severity" value={r.severity} accent={s.c} />
        <Metric label="Confidence" value={`${pct}%`} />
        <Metric label="Logs" value={result.raw_log_count ?? logs.length} />
        <Metric label="Source" value={live ? "Elastic" : "Sample"} accent={live ? "#34d399" : undefined} />
      </div>

      <article className="incident" style={{ "--sev": s.c, "--sev-bg": s.g }}>
        <div className="incident-accent" />
        <div className="incident-body">
          <div className="incident-top">
            <span className="sev-tag" style={{ color: s.c, background: s.g, borderColor: `${s.c}40` }}>
              {r.severity} · {s.l}
            </span>
            <h2>{r.title}</h2>
            {r.summary && <p className="incident-sum">{r.summary}</p>}
          </div>
        </div>
      </article>

      <div className="grid">
        <section className="card">
          <header className="card-h">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1v6M8 11v1M3 8H1M15 8h-2M4.2 4.2l-1.4-1.4M13.2 13.2l-1.4-1.4M4.2 11.8l-1.4 1.4M13.2 2.8l-1.4 1.4" stroke="#22d3ee" strokeWidth="1.5" strokeLinecap="round"/></svg>
            Root cause
          </header>
          <p>{r.root_cause}</p>
          {r.affected_services?.length > 0 && (
            <div className="pills">
              {r.affected_services.map((svc) => (
                <span key={svc} className="pill">{svc}</span>
              ))}
            </div>
          )}
        </section>

        <section className="card">
          <header className="card-h">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 8l4 4 8-8" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Fix steps
          </header>
          <ul className="fixes">
            {r.fix_steps?.map((step, i) => (
              <li key={i}>
                <span className="fix-n">{i + 1}</span>
                <span>{step}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {logs.length > 0 && (
        <section className="card logs-card">
          <button type="button" className="card-h card-h-btn" onClick={() => setLogsOpen((v) => !v)}>
            <span className="card-h-left">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="1.5" stroke="#8b9cb3" strokeWidth="1.5"/><path d="M5 6h6M5 8.5h4" stroke="#8b9cb3" strokeWidth="1.5" strokeLinecap="round"/></svg>
              Evidence
              <em>{logs.length}</em>
            </span>
            <svg className={`chev ${logsOpen ? "open" : ""}`} width="14" height="14" viewBox="0 0 14 14"><path d="M3 5l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none"/></svg>
          </button>
          {logsOpen && (
            <div className="log-table">
              <div className="log-head">
                <span>Time</span><span>Service</span><span>Level</span><span>Message</span>
              </div>
              {logs.map((log, i) => (
                <div key={i} className={`log-row ${log.level?.toLowerCase()}`}>
                  <span className="mono">{fmtTime(log.timestamp)}</span>
                  <span className="mono dim">{log.service}</span>
                  <span className={`mono lvl ${log.level?.toLowerCase()}`}>{log.level}</span>
                  <span>{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const [result, setResult] = useState(null);
  const [backend, setBackend] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    checkBackend().then(setBackend);
  }, []);

  useEffect(() => {
    if (!loading) return undefined;
    setLoadStep(0);
    const t = setInterval(() => setLoadStep((s) => (s < 3 ? s + 1 : s)), 1200);
    return () => clearInterval(t);
  }, [loading]);

  async function run(text) {
    const q = text || query;
    if (!q.trim() || loading) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await apiRequest("/investigate", {
        method: "POST",
        body: JSON.stringify({ query: q, time_window_hours: 24 }),
      }));
      setQuery(q);
    } catch (e) {
      setError(e.message || "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <div className="mesh" aria-hidden="true" />

      <header className="bar">
        <div className="bar-brand">
          <div className="bar-logo">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 2L20 6.5V17.5L12 22L4 17.5V6.5L12 2Z" stroke="url(#lg)" strokeWidth="1.8"/>
              <circle cx="12" cy="12" r="3" fill="#22d3ee"/>
              <defs><linearGradient id="lg" x1="4" y1="2" x2="20" y2="22"><stop stopColor="#22d3ee"/><stop offset="1" stopColor="#818cf8"/></linearGradient></defs>
            </svg>
          </div>
          <div>
            <strong>AlertSense</strong>
            <span>Incident triage</span>
          </div>
        </div>
        <div className={`bar-pill ${backend?.online ? "on" : "off"}`}>
          <i />{backend?.online ? "Live" : "Offline"}
        </div>
      </header>

      <section className="shell">
        <div className="search">
          <div className="search-chips">
            {EXAMPLES.map((ex) => (
              <button key={ex.label} type="button" className="chip" onClick={() => run(ex.query)} disabled={loading}>
                {ex.label}
              </button>
            ))}
          </div>
          <div className="search-box">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What broke?"
              rows={2}
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); run(); }
              }}
            />
            <button type="button" className="go" onClick={() => run()} disabled={loading || !query.trim()}>
              {loading ? (
                <span className="go-spin" />
              ) : (
                <>
                  Investigate
                  <svg width="16" height="16" viewBox="0 0 16 16"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </>
              )}
            </button>
          </div>
          {error && (
            <p className="err">
              {error}
              <button type="button" onClick={() => run()} disabled={loading}>Retry</button>
            </p>
          )}
        </div>

        <div className="view">
          {loading && <LoadingState step={loadStep} />}
          {!loading && !result && <IdleState />}
          {!loading && result && <Dashboard result={result} />}
        </div>
      </section>
    </div>
  );
}
