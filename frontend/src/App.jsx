import { useEffect, useState } from "react";

const SEVERITY_COLORS = {
  P0: "#ef4444",
  P1: "#f97316",
  P2: "#eab308",
  INFO: "#64748b",
};

const STEP_ICONS = {
  detect: "◎",
  search: "⌕",
  analyze: "◈",
  recommend: "✓",
};

const EXAMPLE_QUERIES = [
  "Customers say checkout is slow — what broke?",
  "Why did payment failures spike in the last hour?",
  "Are there errors after the latest deploy?",
];

function SeverityBadge({ severity }) {
  const color = SEVERITY_COLORS[severity] || SEVERITY_COLORS.INFO;
  return (
    <span className="severity-badge" style={{ background: `${color}22`, color, borderColor: `${color}55` }}>
      {severity}
    </span>
  );
}

function Timeline({ events }) {
  if (!events?.length) return null;
  return (
    <div className="timeline">
      <h3>Agent Timeline</h3>
      {events.map((event, i) => (
        <div key={i} className="timeline-item">
          <div className="timeline-marker">{STEP_ICONS[event.step] || "•"}</div>
          <div className="timeline-content">
            <div className="timeline-title">{event.title}</div>
            <div className="timeline-detail">{event.detail}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function EvidenceList({ logs }) {
  if (!logs?.length) return null;
  return (
    <div className="evidence">
      <h3>Evidence Logs</h3>
      <div className="log-list">
        {logs.map((log, i) => (
          <div key={i} className={`log-row level-${log.level?.toLowerCase()}`}>
            <span className="log-time">{log.timestamp?.slice(11, 19) || "—"}</span>
            <span className="log-service">{log.service}</span>
            <span className="log-level">{log.level}</span>
            <span className="log-message">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Report({ report }) {
  if (!report) return null;
  return (
    <div className="report">
      <div className="report-header">
        <h2>{report.title}</h2>
        <SeverityBadge severity={report.severity} />
      </div>
      <p className="report-summary">{report.summary}</p>
      <div className="report-section">
        <h4>Root Cause</h4>
        <p>{report.root_cause}</p>
      </div>
      <div className="report-section">
        <h4>Affected Services</h4>
        <div className="tags">
          {report.affected_services?.map((s) => (
            <span key={s} className="tag">{s}</span>
          ))}
        </div>
      </div>
      <div className="report-section">
        <h4>Recommended Fix Steps</h4>
        <ol className="fix-steps">
          {report.fix_steps?.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>
      <div className="confidence">Confidence: {Math.round((report.confidence || 0) * 100)}%</div>
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
    if (!q.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("/api/investigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, time_window_hours: 24 }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
      setQuery(q);
    } catch (e) {
      setError(e.message || "Investigation failed");
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
            <p>AI incident triage · Elastic MCP + Gemini</p>
          </div>
        </div>
        {config && (
          <div className="mode-pill">
            Source: <strong>{config.mode === "demo" ? "Demo" : "Elastic Cloud"}</strong>
            {config.elastic_mcp_configured && " · MCP configured"}
          </div>
        )}
      </header>

      <main className="main">
        <section className="chat-panel">
          <div className="panel-title">Investigate Incident</div>
          <p className="panel-desc">
            Describe what users are experiencing. The agent searches Elastic logs,
            analyzes patterns, and returns severity + fix steps.
          </p>

          <div className="examples">
            {EXAMPLE_QUERIES.map((ex) => (
              <button key={ex} className="example-chip" onClick={() => investigate(ex)} disabled={loading}>
                {ex}
              </button>
            ))}
          </div>

          <div className="input-row">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Customers say checkout is slow — what broke?"
              rows={3}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  investigate();
                }
              }}
            />
            <button className="primary-btn" onClick={() => investigate()} disabled={loading || !query.trim()}>
              {loading ? "Investigating…" : "Run Agent"}
            </button>
          </div>

          {error && <div className="error">{error}</div>}
        </section>

        {result && (
          <section className="results">
            <Timeline events={result.timeline} />
            <Report report={result.report} />
            <EvidenceList logs={result.report?.evidence} />
            <div className="meta">
              Retrieved {result.raw_log_count} logs ·{" "}
              {result.mode === "elasticsearch"
                ? "🟢 Live from your Elastic Cloud cluster"
                : result.mode === "elastic_mcp"
                  ? "🟢 Live via Elastic MCP"
                  : result.mode === "demo_fallback"
                    ? "⚠️ Demo fallback (Elastic query failed)"
                    : "Demo data"}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        Google Cloud Rapid Agent Hackathon · Elastic Track · AlertSense v1.0
      </footer>
    </div>
  );
}
