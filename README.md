# AlertSense

**AI incident triage agent for alert fatigue** — built for the [Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/) (**Elastic track**).

AlertSense turns *"customers say checkout is slow"* into **severity + root cause + fix steps** by searching Elastic logs via MCP and analyzing patterns with Gemini.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Track](https://img.shields.io/badge/track-Elastic-005571)

## The problem

Small SaaS teams drown in Elastic alerts. Search finds logs — but **nobody tells you what to fix first**. AlertSense closes that gap with a multi-step agent that **acts**, not just answers.

## Demo

Ask: **"Customers say checkout is slow — what broke?"**

The agent will:

1. **Detect** incident intent
2. **Search** logs via Elastic MCP
3. **Analyze** error patterns with Gemini
4. **Recommend** P0/P1/P2 + evidence + fix steps

Works in **demo mode** out of the box (no Elastic account needed for testing).

## Quick start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Google AI Studio API key (optional — fallback analysis works without it)

### 1. Clone and configure

```bash
cp .env.example .env
# Add GOOGLE_API_KEY for full Gemini analysis
```

### 2. Backend

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8080
```

### 3. Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 4. Docker (production-like)

```bash
docker compose up --build
```

Open http://localhost:8080

## Elastic MCP integration

See [docs/AGENT_BUILDER.md](docs/AGENT_BUILDER.md) for:

- Elastic Serverless setup
- MCP endpoint configuration
- Google Cloud Agent Builder connection
- Cloud Run deployment

## Project structure

```
├── backend/
│   ├── agent/          # Multi-step orchestrator + Gemini
│   ├── elastic/        # MCP client + mock demo data
│   └── main.py         # FastAPI API
├── frontend/           # React UI (chat + timeline + report)
├── data/               # Sample checkout-incident logs
├── docs/               # Agent Builder setup + demo script
└── PLAN.md             # 3-day sprint plan
```

## API

```bash
curl -X POST http://localhost:8080/api/investigate \
  -H "Content-Type: application/json" \
  -d '{"query": "Customers say checkout is slow — what broke?"}'
```

## Hackathon submission

| Item | Status |
|------|--------|
| Hosted project URL | Deploy to Cloud Run |
| Public GitHub repo | This repo + MIT LICENSE |
| ~3 min demo video | See `docs/DEMO_SCRIPT.md` |
| Partner track | **Elastic** |
| Gemini + Agent Builder | See `docs/AGENT_BUILDER.md` |

## Judging alignment

- **Technological implementation** — Elastic MCP + Gemini multi-step agent
- **Design** — Incident timeline, severity badges, evidence logs
- **Potential impact** — Alert fatigue for every small ops team
- **Quality of idea** — Search ≠ actionable triage (unsolved gap)

## License

MIT — see [LICENSE](LICENSE)
