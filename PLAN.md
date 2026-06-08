# AlertSense — Build Plan

> **Hackathon:** [Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/)  
> **Track:** Elastic  
> **Deadline:** Jun 11, 2026 @ 2:00pm PDT  

## Problem (still unsolved)

Small dev/SaaS teams get **alert fatigue** — hundreds of Elastic logs daily, but no one knows which incidents are **P0 vs noise**. Elastic finds anomalies; it doesn't give a **plain-language action plan**.

## Solution

**AlertSense** — a Gemini-powered agent that:

1. **Detects** incident intent from natural language
2. **Searches** logs via **Elastic MCP** (Agent Builder tools)
3. **Analyzes** patterns with Gemini
4. **Recommends** severity (P0/P1/P2) + evidence + fix steps

Human stays in control — agent **acts**, doesn't just chat.

---

## Architecture

```
User (React UI)
    │
    ▼
FastAPI Backend (Cloud Run)
    │
    ├── Gemini 2.0/2.5 (Vertex AI or Google AI)
    │
    └── Elastic MCP Client
            │
            ▼
        Elastic Agent Builder MCP Endpoint (Kibana)
            │
            ▼
        Elasticsearch (application logs index)
```

**Hackathon requirement:** Google Cloud Agent Builder + Gemini + Elastic MCP.

- **Primary path:** Connect GCP Agent Builder to Elastic MCP (see `docs/AGENT_BUILDER.md`)
- **Hosted app:** This repo provides UI + orchestration API deployable to Cloud Run

---

## 3-Day Sprint

### Day 1 — Core agent ✅ (this build)

- [x] Project scaffold + LICENSE + README
- [x] Multi-step agent orchestrator (detect → search → analyze → recommend)
- [x] Elastic MCP client + mock demo mode
- [x] Sample checkout-incident logs for demo

### Day 2 — Polish + deploy

- [ ] Elastic Serverless free trial + seed sample logs
- [ ] Connect real Elastic MCP endpoint
- [ ] Cloud Run deploy → hosted URL
- [ ] UI polish (timeline, severity badges)

### Day 3 — Submission

- [ ] 3-min demo video (see `docs/DEMO_SCRIPT.md`)
- [ ] Public GitHub repo + license visible in About
- [ ] Devpost: hosted URL, repo, Elastic track

---

## MCP Tools Used (Elastic Agent Builder)

| Tool | Purpose |
|------|---------|
| Search / hybrid retrieval | Find error logs in time window |
| ES\|QL (if exposed) | Aggregate error counts by service |
| Custom log search tool | Query `logs-*` for checkout errors |

---

## Demo Scenario (3-min video)

1. **Hook (15s):** "2 hours reading logs — or 2 minutes with AlertSense"
2. **Problem (20s):** Show Kibana alert noise / customer complaint
3. **Live demo (90s):** User asks: *"Customers say checkout is slow — what broke?"*
4. **Agent acts:** Search → spike at 14:32 → payment-api timeout → P1
5. **Output:** Timeline + 3 fix steps + evidence log lines
6. **Impact (15s):** Small teams, real alert fatigue, Elastic MCP integration

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes* | Google AI Studio key for Gemini |
| `GEMINI_MODEL` | No | Default `gemini-2.0-flash` |
| `ELASTIC_MCP_URL` | No | Elastic Agent Builder MCP endpoint |
| `ELASTIC_API_KEY` | No | Elasticsearch API key |
| `ELASTICSEARCH_URL` | No | Direct ES URL (fallback search) |
| `DEMO_MODE` | No | `true` = use mock logs (default if no Elastic) |

---

## Judging Alignment

| Criteria | How AlertSense scores |
|----------|----------------------|
| **Tech implementation** | Multi-step agent + Elastic MCP + Gemini on GCP |
| **Design** | Chat + incident timeline + severity badges |
| **Impact** | Alert fatigue for every small SaaS team |
| **Idea quality** | Gap: search ≠ actionable triage |
