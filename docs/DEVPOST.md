# Devpost Submission — AlertSense

Copy each section into the matching field on your [Devpost project overview](https://devpost.com/submit-to/29711-google-cloud-rapid-agent-hackathon/manage/submissions/1044390-alertsense/project-overview).

---

## Project name

```
AlertSense
```

---

## Tagline / Elevator pitch (≤200 chars)

```
Turn Elastic alert noise into P0/P1/P2 fix steps — a multi-step Gemini agent that searches logs via Elastic MCP and tells you what to fix first.
```

---

## The problem it solves (short — gallery / summary)

```
Small teams drown in Elastic alerts. Search finds logs — but nobody tells you what to fix first. AlertSense closes that gap in under 40 seconds.
```

---

## About the project (main description)

```markdown
## AlertSense — AI Incident Triage for Alert Fatigue

**Live demo:** https://alert-sense.vercel.app  
**API health:** https://alert-sense.vercel.app/api/health  
**Source code:** https://github.com/taopi74/AlertSense

When customers say *"checkout is slow"*, engineers spend hours jumping between Kibana, deploy logs, and Slack. Elastic finds anomalies — it doesn't give you an **action plan**.

**AlertSense** is a multi-step AI agent that:

1. **Detects** incident intent from plain English (Gemini)
2. **Searches** live logs via **Elastic Agent Builder MCP** (`search_error_logs`)
3. **Analyzes** root cause via **Google Cloud Agent Builder** (ADK + Gemini + MCP)
4. **Recommends** P0/P1/P2 severity, evidence logs, and ranked fix steps

### Try it

1. Open https://alert-sense.vercel.app
2. Click **Slow checkout** or type your incident
3. Click **Investigate** (~30–40 seconds)
4. See severity, root cause, fix steps, and Elastic evidence

### Hackathon compliance

All three required technologies are **invoked at runtime** on every investigation:

| Technology | Implementation |
|------------|----------------|
| **Gemini** | Detect + recommend steps |
| **Google Cloud Agent Builder** | ADK 2.2.0 agent with Elastic MCP tools |
| **Elastic MCP** | `search_error_logs` on `logs-alertsense` index |

Verify: https://alert-sense.vercel.app/api/health → all `true`, `adk_version: "2.2.0"`
```

---

## Inspiration

```markdown
Every small SaaS team I've seen faces the same pain: Elastic fires hundreds of alerts, on-call engineers grep logs for hours, and leadership still asks "what broke and what do we fix first?"

Search tools answer *what happened* — not *what to do*. I built AlertSense to be the missing layer: an agent that **acts** on Elastic data and returns an on-call-ready incident report, not a chatbot reply.
```

---

## What it does

```markdown
AlertSense accepts a natural-language incident description and returns a structured report:

- **Severity** — P0 / P1 / P2 with confidence score
- **Root cause** — which service broke and why
- **Fix steps** — ranked remediation actions
- **Evidence** — real ERROR/WARN logs from Elastic Cloud

Example input: *"Customers say checkout is slow — what broke?"*

Example output: P0 incident — payment-api stripe-api timeouts after deploy v2.14.0, circuit breaker OPEN, checkout completion down 28%. Fix: rollback payment-api, monitor stripe latency, add regression test.

The agent runs four steps automatically: Detect → Search (Elastic MCP) → Analyze (Agent Builder ADK) → Recommend (Gemini).
```

---

## How we built it

```markdown
**Architecture**

```
React UI (Vercel)
    ↓
FastAPI orchestrator
    ├── Gemini API — detect intent + generate report
    ├── Elastic MCP client — search_error_logs tool
    └── Google ADK Agent — Agent Builder analysis (Gemini + MCP tools)
            ↓
    Elastic Cloud (logs-alertsense index)
```

**Key implementation details:**

- **Elastic MCP:** Custom Streamable HTTP client with proper `Accept: application/json, text/event-stream` headers; calls `search_error_logs` ES|QL tool on Agent Builder
- **Agent Builder:** Google ADK 2.2.0 `LlmAgent` with `McpToolset` connected to Elastic MCP endpoint
- **Orchestrator:** Four-step pipeline in `backend/agent/orchestrator.py` — each step logged in agent timeline
- **Frontend:** React + Vite dashboard — incident input, severity metrics, root cause / fix cards, collapsible evidence logs
- **Deploy:** Vercel experimentalServices — Vite frontend + FastAPI Python serverless at `/api`

**Elastic setup:** Serverless Observability project on GCP, Agent Builder custom tool `search_error_logs`, seeded checkout incident logs via `scripts/seed_elastic.py`.
```

---

## Challenges we ran into

```markdown
1. **Elastic MCP 406 errors** — MCP Streamable HTTP spec requires `Accept: application/json, text/event-stream`. Fixed with a dedicated MCP client instead of raw httpx defaults.

2. **Wrong MCP tool name** — Generic `search` failed; Elastic Agent Builder exposes custom tools by name. Switched to `search_error_logs`.

3. **Agent Builder on Vercel** — ADK version mismatch (`McpToolset` vs `MCPToolset`) and missing `Deprecated` + `mcp` packages on serverless. Fixed with compatibility layer + pinned `google-adk==2.2.0`.

4. **Serverless timeouts** — Full investigation takes ~30–40s (ADK + Gemini + MCP). Increased Vercel `maxDuration` to 120s.

5. **Alert fatigue UX** — Iterated UI from marketing-heavy to minimal incident dashboard so judges see results, not boilerplate.
```

---

## Accomplishments that we're proud of

```markdown
- End-to-end **live demo** with real Elastic Cloud logs — not mock data in production
- All three hackathon technologies (**Gemini + Agent Builder + Elastic MCP**) verified at runtime via `/api/health`
- Multi-step agent with visible pipeline: Detect → Search → Analyze → Recommend
- Custom Elastic MCP tool (`search_error_logs`) returning 25+ live ERROR/WARN entries per query
- Deployed and working hosted URL judges can test immediately
- Open source MIT repo with full setup docs
```

---

## What we learned

```markdown
- **MCP is strict** — Streamable HTTP transport has spec requirements that break silently (406) if headers are wrong
- **Agent Builder + MCP** — Google ADK makes it straightforward to wire Elastic tools into a Gemini agent; the hard part is deployment compatibility across environments
- **Search ≠ triage** — The biggest value isn't finding logs — it's ranking severity and suggesting fixes from evidence
- **Serverless agents need timeouts** — Multi-step AI pipelines on Vercel require explicit duration limits and graceful fallbacks
```

---

## What's next for AlertSense

```markdown
- **Slack / PagerDuty integration** — auto-investigate when alerts fire
- **GCP Agent Builder console agent** — parallel agent in Vertex AI Agent Engine for enterprise teams
- **Runbook memory** — store past incidents and fix outcomes to improve recommendations
- **Multi-tenant Elastic** — support multiple log indices and environments per team
- **Cloud Run deployment** — alternative to Vercel for longer-running investigations
```

---

## Built with (tags)

Add these one at a time in Devpost (whole phrases, not single letters):

```
Gemini
Google Cloud
Google Cloud Agent Builder
Elastic
Elastic Cloud
Elastic MCP
FastAPI
Python
React
Vite
Vercel
JavaScript
AI
Machine Learning
```

---

## Links

| Field | URL |
|-------|-----|
| **Try it out / Hosted project** | `https://alert-sense.vercel.app` |
| **GitHub repository** | `https://github.com/taopi74/AlertSense` |
| **API health (optional in description)** | `https://alert-sense.vercel.app/api/health` |

---

## Video demo

```
[Paste your YouTube public URL here after recording]
```

Title suggestion: `AlertSense — AI Incident Triage | Google Cloud Rapid Agent Hackathon | Elastic Track`

---

## Gallery image caption

```
AlertSense dashboard: describe an incident in plain English, get P0/P1/P2 severity, root cause, fix steps, and Elastic evidence logs in under 40 seconds.
```

---

## Additional info (judges only)

| Field | Value |
|-------|-------|
| Submitter Type | Individual |
| Organization | N/A |
| Government employee | No |
| Country | Bangladesh |
| Canada province | N/A |
| Partner track | **Elastic** |
| New or existing (after May 5, 2026) | **New** |
| Open source repo | https://github.com/taopi74/AlertSense |
| Hosted project URL | https://alert-sense.vercel.app |
| Google Cloud products | Gemini API, Google Cloud Agent Builder (ADK 2.2.0) |
| Other tools | Elastic Cloud, Elasticsearch, Elastic Agent Builder MCP, FastAPI, React, Vite, Vercel |
| First time Arize | Yes |
| First time Elastic | Yes |
| First time Fivetran | Yes |
| First time GitLab | Yes |
| First time MongoDB | Yes |
| First time Dynatrace | Yes |

### Judge testing steps

```
1. Open https://alert-sense.vercel.app
2. Click "Slow checkout" → Investigate (~30–40s)
3. Verify: P0/P1 severity, root cause, fix steps, evidence logs
4. Health check: https://alert-sense.vercel.app/api/health
   → gemini_configured, elastic_configured, agent_builder_configured all true
5. Source: https://github.com/taopi74/AlertSense (MIT license)
```

---

## Checklist before Final Submit

- [ ] All text fields filled (copy from above)
- [ ] Gallery image uploaded (`alertsense-devpost-gallery.png`)
- [ ] Video URL added (YouTube **public**)
- [ ] Hosted URL: https://alert-sense.vercel.app
- [ ] Repo URL: https://github.com/taopi74/AlertSense
- [ ] Elastic track selected
- [ ] GitHub About section shows MIT license
- [ ] Live investigate tested on production
