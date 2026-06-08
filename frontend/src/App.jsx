import { useEffect, useState } from "react";

const SEVERITY = {
  P0: { color: "#ef4444", label: "Critical", bg: "rgba(239,68,68,0.12)" },
  P1: { color: "#f97316", label: "High", bg: "rgba(249,115,22,0.12)" },
  P2: { color: "#eab308", label: "Medium", bg: "rgba(234,179,8,0.12)" },
  INFO: { color: "#64748b", label: "Info", bg: "rgba(100,116,139,0.12)" },
};

const STEPS = [
  { key: "detect", num: 1, title: "Detect", desc: "Understand incident" },
  { key: "search", num: 2, title: "Search", desc: "Query Elastic logs" },
  { key: "analyze", num: 3, title: "Analyze", desc: "Find root cause" },
  { key: "recommend", num: 4, title: "Recommend", desc: "Severity + fixes" },
];

const EXAMPLES = [
  {
    label: "Slow checkout",
    query: "Customers say checkout is slow — what broke?",
  },
  {
    label: "Payment spike",
    query: "Why did payment failures spike in the last hour?",
  },
  {
    label: "After deploy",
    query: "Are there errors after the latest deploy?",
  },
];

function formatTime(ts) {
  if (!ts) return "—";
  const str = typeof ts === "string" ? ts : String(ts);
  if (str.length >= 19) return str.slice(11, 19);
  return str.slice(0, 8);
}

function SeverityBadge({ severity }) {
  const s = SEVERITY[severity] || SEVERITY.INFO;
  return (
    <span className="severity-badge" style={{ color: s.color, background: s.bg, borderColor: `${s.color}44` }}>
      {severity} · {s.label}
    </span>
  );
}

function StatusBar({ config, resultMode }) {
  const live = resultMode === "elasticsearch" || resultMode === "elastic_mcp";
  const isDemo = resultMode === "demo" || resultMode === "demo_fallback";

  return (
    <div className="status-bar">
      <div className={`status-dot ${config?.mode !== "demo" ? "online" : ""}`} />
      <span>
        {live ? "Live Elastic data" : config?.mode === "demo" ? "Demo mode" : "Elastic Cloud connected"}
      </span>
      {config?.elastic_mcp_configured && <span className="status-tag">MCP</span>}
      {resultMode && (
        <span className={`status-tag ${live ? "status-tag-live" : isDemo ? "status-tag-warn" : ""}`}>
          {live ? "Real logs" : isDemo ? "Sample data" : resultMode}
        </span>
      )}
    </div>
  );
}

function HowItWorks() {
  return (
    <div className="how-it-works">
      <span className="how-label">How it works</span>
      <div className="how-steps">
        {STEPS.map((s) => (
          <div key={s.key} className="how-step">
            <span className="how-num">{s.num}</span>
            <span className="how-title">{s.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="loading-panel">
      <div className="loading-spinner" />
      <p className="loading-title">Agent is investigating…</p>
      <p className="loading-sub">Searching Elastic logs and analyzing patterns</p>
      <div className="loading-steps">
        {STEPS.map((s, i) => (
          <div key={s.key} className="loading-step" style={{ animationDelay: `${i * 0.4}s` }}>
            <span className="how-num">{s.num}</span>
            {s.title}
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyResults() {
  return (
    <div className="empty-state">
      <div className="empty-icon">⌕</div>
      <h3>Ready to investigate</h3>
      <p>Describe an incident or pick an example above. AlertSense will search your logs and return severity + fix steps.</p>
      <ul className="empty-tips">
        <li>Works with live Elastic Cloud logs</li>
        <li>Returns P0 / P1 / P2 severity</li>
        <li>Includes evidence and fix steps</li>
      </ul>
    </div>
  );
}

function Timeline({ events }) {
  if (!events?.length) return null;
  return (
    <div className="card timeline-card">
      <div className="card-header">
        <h3>Agent Timeline</h3>
        <span className="card-badge">{events.length} steps</span>
      </div>
      <div className="timeline-track">
        {events.map((event, i) => (
          <div key={i} className="timeline-item">
            <div className="timeline-left">
              <div className="timeline-dot">{i + 1}</div>
              {i < events.length - 1 && <div className="timeline-line" />}
            </div>
            <div className="timeline-body">
              <div className="timeline-title">{event.title}</div>
              <div className="timeline-detail">{event.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Report({ report }) {
  if (!report) return null;
  const pct = Math.round((report.confidence || 0) * 100);
  const sev = SEVERITY[report.severity] || SEVERITY.INFO;

  return (
    <div className="card report-card">
      <div className="report-top">
        <div>
          <span className="report-label">Incident Report</span>
          <h2>{report.title}</h2>
        </div>
        <SeverityBadge severity={report.severity} />
      </div>

      <p className="report-summary">{report.summary}</p>

      <div className="report-grid">
        <div className="report-block">
          <h4>Root Cause</h4>
          <p>{report.root_cause}</p>
        </div>
        <div className="report-block">
          <h4>Confidence</h4>
          <div className="confidence-bar-wrap">
            <div className="confidence-bar" style={{ width: `${pct}%`, background: sev.color }} />
          </div>
          <span className="confidence-pct">{pct}%</span>
        </div>
      </div>

      <div className="report-block">
        <h4>Affected Services</h4>
        <div className="tags">
          {report.affected_services?.map((s) => (
            <span key={s} className="tag">{s}</span>
          ))}
        </div>
      </div>

      <div className="report-block">
        <h4>Recommended Fix Steps</h4>
        <div className="fix-cards">
          {report.fix_steps?.map((step, i) => (
            <div key={i} className="fix-card">
              <span className="fix-num">{i + 1}</span>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function EvidenceList({ logs }) {
  if (!logs?.length) return null;
  return (
    <div className="card evidence-card">
      <div className="card-header">
        <h3>Evidence Logs</h3>
        <span className="card-badge">{logs.length} entries</span>
      </div>
      <div className="log-list">
        {logs.map((log, i) => (
          <div key={i} className={`log-row level-${log.level?.toLowerCase()}`}>
            <span className="log-time">{formatTime(log.timestamp)}</span>
            <span className="log-service">{log.service}</span>
            <span className={`log-level level-badge-${log.level?.toLowerCase()}`}>{log.level}</span>
            <span className="log-message">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function DataSourceBanner({ mode, count }) {
  const messages = {
    elasticsearch: { icon: "●", text: `Live from Elastic Cloud · ${count} logs retrieved`, cls: "banner-live" },
    elastic_mcp: { icon: "●", text: `Live via Elastic MCP · ${count} logs retrieved`, cls: "banner-live" },
    demo_fallback: { icon: "!", text: "Using sample data — Elastic query unavailable", cls: "banner-warn" },
    demo: { icon: "○", text: "Demo mode · sample incident data", cls: "banner-demo" },
  };
  const m = messages[mode] || messages.demo;
  return (
    <div className={`data-banner ${m.cls}`}>
      <span className="banner-icon">{m.icon}</span>
      {m.text}
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [config, setConfig] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then(setConfig)
      .catch(() => setConfig({ mode: "demo" }));
  }, []);

  async function investigate(text) {
    const q = text || query;
    if (!q.trim() || loading) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("/api/investigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, time_window_hours: 24 }),
      });
      if (!res.ok) throw new Error("Investigation failed. Check backend is running.");
      setResult(await res.json());
      setQuery(q);
    } catch (e) {
      setError(e.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="logo">AS</div>
          <div>
            <h1>AlertSense</h1>
            <p>Turn alert noise into actionable incident reports</p>
          </div>
        </div>
        {config && <StatusBar config={config} resultMode={result?.mode} />}
      </header>

      <section className="hero">
        <h2>What broke? Ask in plain English.</h2>
        <p>AI agent searches Elastic logs, finds root cause, and tells you what to fix first.</p>
      </section>

      <main className="layout">
        <section className="input-panel card">
          <div className="card-header">
            <h3>Investigate Incident</h3>
          </div>

          <HowItWorks />

          <p className="panel-hint">Try an example or describe what users are experiencing:</p>

          <div className="examples">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                type="button"
                className="example-chip"
                onClick={() => investigate(ex.query)}
                disabled={loading}
                title={ex.query}
              >
                <span className="chip-label">{ex.label}</span>
              </button>
            ))}
          </div>

          <div className="input-wrap">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Customers say checkout is slow — what broke?"
              rows={4}
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  investigate();
                }
              }}
            />
            <span className="input-hint">Enter to run · Shift+Enter for new line</span>
          </div>

          <button
            type="button"
            className="primary-btn"
            onClick={() => investigate()}
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <>
                <span className="btn-spinner" /> Investigating…
              </>
            ) : (
              "Run Agent →"
            )}
          </button>

          {error && (
            <div className="error-box" role="alert">
              <strong>Error</strong>
              <p>{error}</p>
            </div>
          )}
        </section>

        <section className="output-panel">
          {loading && <LoadingState />}
          {!loading && !result && <EmptyResults />}
          {!loading && result && (
            <>
              <DataSourceBanner mode={result.mode} count={result.raw_log_count} />
              <Timeline events={result.timeline} />
              <Report report={result.report} />
              <EvidenceList logs={result.report?.evidence} />
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <span>Google Cloud Rapid Agent Hackathon</span>
        <span className="footer-dot">·</span>
        <span>Elastic Track</span>
        <span className="footer-dot">·</span>
        <span>Gemini + Elastic MCP</span>
      </footer>
    </div>
  );
}
