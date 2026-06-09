# AlertSense

**AI incident triage agent for alert fatigue** — built for the [Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/) (**Elastic track**).

AlertSense turns *"customers say checkout is slow"* into **severity + root cause + fix steps** by searching Elastic logs via MCP and analyzing patterns with Gemini.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Track](https://img.shields.io/badge/track-Elastic-005571)
![Live](https://img.shields.io/badge/demo-live-success)

## Live demo

| | Link |
|---|------|
| **App** | [https://alert-sense.vercel.app](https://alert-sense.vercel.app/) |
| **API health** | [https://alert-sense.vercel.app/api/health](https://alert-sense.vercel.app/api/health) |
| **GitHub** | [https://github.com/taopi74/AlertSense](https://github.com/taopi74/AlertSense) |

Try it: open the app → click **Slow checkout** → **Investigate** (~30–40s).

Health check should return:

```json
{
  "status": "ok",
  "gemini_configured": true,
  "elastic_configured": true,
  "agent_builder_configured": true,
  "adk_version": "2.2.0"
}
```

## The problem

Small SaaS teams drown in Elastic alerts. Search finds logs — but **nobody tells you what to fix first**. AlertSense closes that gap with a multi-step agent that **acts**, not just answers.

## How it works

Ask: **"Customers say checkout is slow — what broke?"**

The agent will:

1. **Detect** — parse incident intent (Gemini)
2. **Search** — query logs via **Elastic Agent Builder MCP** (`search_error_logs`)
3. **Analyze** — root cause via **Google Cloud Agent Builder** (ADK + Gemini + MCP)
4. **Recommend** — P0/P1/P2 severity, fix steps, evidence logs

## Tech stack

| Layer | Technology |
|-------|------------|
| AI reasoning | Google Gemini (`gemini-2.5-flash`) |
| Agent platform | Google Cloud Agent Builder (ADK 2.2.0) |
| Log search | Elastic Cloud + Agent Builder MCP |
| Backend | FastAPI, Python 3.12 |
| Frontend | React, Vite |
| Hosting | Vercel |

## Quick start (local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- Google AI Studio API key
- Elastic Cloud project with Agent Builder MCP (optional — demo fallback available)

### 1. Clone and configure

```bash
git clone https://github.com/taopi74/AlertSense.git
cd AlertSense
cp .env.example .env
# Fill in GOOGLE_API_KEY, ELASTIC_MCP_URL, ELASTIC_API_KEY, etc.
```

### 2. Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8081
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 4. Docker

```bash
docker compose up --build
```

Open http://localhost:8080

## API

**Health**

```bash
curl https://alert-sense.vercel.app/api/health
```

**Investigate**

```bash
curl -X POST https://alert-sense.vercel.app/api/investigate \
  -H "Content-Type: application/json" \
  -d '{"query": "Customers say checkout is slow — what broke?"}'
```

Local:

```bash
curl -X POST http://localhost:8081/api/investigate \
  -H "Content-Type: application/json" \
  -d '{"query": "Customers say checkout is slow — what broke?"}'
```

## Elastic MCP + Agent Builder setup

See [docs/AGENT_BUILDER.md](docs/AGENT_BUILDER.md) and [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for:

- Elastic Serverless + Agent Builder MCP
- Custom tool `search_error_logs` on `logs-alertsense`
- Google ADK integration
- Vercel deployment env vars

## Project structure

```
├── backend/
│   ├── agent/          # Orchestrator, Gemini, Agent Builder (ADK)
│   ├── elastic/        # MCP client + Elasticsearch fallback
│   └── main.py         # FastAPI API
├── frontend/           # React dashboard UI
├── api/                # Vercel serverless entrypoint
├── docs/               # Setup, demo script, submission checklist
└── scripts/            # Seed Elastic, inject live incidents
```

## Hackathon compliance

Every `/api/investigate` call invokes all three required technologies at runtime:

| Requirement | Implementation |
|-------------|----------------|
| **Gemini** | `backend/agent/gemini.py` |
| **Google Cloud Agent Builder** | `backend/agent/agent_builder.py` (ADK) |
| **Elastic MCP** | `backend/elastic/mcp_client.py` |

### Vercel environment variables

```
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
ELASTIC_MCP_URL=
ELASTIC_API_KEY=
ELASTIC_MCP_TOOL_NAME=search_error_logs
ELASTICSEARCH_URL=
ELASTICSEARCH_API_KEY=
DEMO_MODE=false
```

## Judging alignment

- **Technological implementation** — Elastic MCP + Gemini + ADK multi-step agent
- **Design** — Clean incident dashboard with severity, root cause, fix steps
- **Potential impact** — Alert fatigue for every small ops team
- **Quality of idea** — Search ≠ actionable triage

## License

MIT — see [LICENSE](LICENSE)
