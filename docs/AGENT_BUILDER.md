# AlertSense — Google Cloud Agent Builder + Elastic MCP Setup

This guide connects AlertSense to the **Elastic partner track** requirements for the
[Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/).

## Architecture (submission-ready)

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  AlertSense UI  │────▶│  FastAPI Orchestrator │────▶│  Gemini (Google AI) │
│  (Cloud Run)    │     │  multi-step agent     │     │  analyze + recommend│
└─────────────────┘     └──────────┬───────────┘     └─────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Elastic MCP Server  │
                        │  (Agent Builder/Kibana)│
                        └──────────┬───────────┘
                                   ▼
                        ┌──────────────────────┐
                        │  Elasticsearch logs  │
                        └──────────────────────┘
```

## Step 1 — Elastic Serverless (free trial)

1. Create an [Elastic Cloud Serverless](https://cloud.elastic.co/) project
2. Enable **Agent Builder** in Kibana
3. Ingest sample logs:

```bash
export ELASTICSEARCH_URL=https://your-deployment.es.region.cloud.es.io
export ELASTICSEARCH_API_KEY=your-api-key
python scripts/seed_elastic.py
```

Resources: [Elastic hackathon resources](https://rapid-agent.devpost.com/details/elastic-resources)

## Step 2 — Get Elastic MCP endpoint

1. Open Kibana → **Agent Builder** → **Tools**
2. Copy the **MCP server URL**
3. Create an Elasticsearch API key with read access to log indices

Add to `.env`:

```env
ELASTIC_MCP_URL=https://your-kibana-url/api/agent_builder/mcp
ELASTIC_API_KEY=your-api-key
DEMO_MODE=false
```

Reference: [Elastic MCP server docs](https://www.elastic.co/search-labs/blog/elastic-mcp-server-agent-builder-tools)

## Step 3 — Google Gemini API

1. Get a key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Add to `.env`:

```env
GOOGLE_API_KEY=your-key
GEMINI_MODEL=gemini-2.0-flash
```

For production, use **Vertex AI** on Google Cloud with the same Gemini models.

## Step 4 — Google Cloud Agent Builder (hackathon requirement)

You can satisfy the Agent Builder requirement in two ways:

### Option A — Agent Builder orchestrates Elastic MCP (recommended for judging)

1. Open [Google Cloud Agent Builder](https://cloud.google.com/products/agent-builder)
2. Create an agent with **Gemini 3 / 2.5**
3. Add **MCP tool source** → paste Elastic MCP URL + API key auth
4. Use the system prompt from `backend/agent/prompts.py`
5. Deploy agent and link from Devpost submission

### Option B — This repo as hosted orchestrator

This repo implements the same multi-step workflow:

1. **Detect** incident intent
2. **Search** logs via Elastic MCP
3. **Analyze** with Gemini
4. **Recommend** severity + fix steps

Deploy to Cloud Run and submit the hosted URL.

## Step 5 — Deploy to Cloud Run

```bash
gcloud run deploy alertsense \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=xxx,ELASTIC_MCP_URL=xxx,ELASTIC_API_KEY=xxx,DEMO_MODE=false"
```

Hosted URL = your Devpost **Project URL**.

## Judging checklist

- [x] Multi-step agent (not chat-only)
- [x] Elastic MCP integration
- [x] Gemini-powered analysis
- [x] Real-world problem (alert fatigue)
- [ ] 3-min demo video
- [ ] Public GitHub + MIT license
- [ ] Devpost Elastic track selected
