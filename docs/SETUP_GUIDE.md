# AlertSense — Hackathon Setup Guide (Step by Step)

Ei guide follow korle **4 ta gap** fix hobe:
1. Gemini powered (`GOOGLE_API_KEY`)
2. Gemini 3 model
3. Google Cloud Agent Builder
4. Elastic MCP (real, not demo)

**Order matter kore** — niche theke upore koro.

---

## Step 0 — `.env` file banao

Project root-e:

```powershell
cd C:\Users\Opi-AI\Desktop\logdataringcenterl\Google
copy .env.example .env
```

`.env` file notepad/Cursor diye edit korbe.

---

## Step 1 — Gemini API Key (15 min) ⚡

### Ki korbe
1. Browser-e jao: [Google AI Studio — API Keys](https://aistudio.google.com/apikey)
2. Google account diye login
3. **Create API key** click koro
4. Key copy koro

### `.env`-e add koro

```env
GOOGLE_API_KEY=AIzaSy...tomar-key...
GEMINI_MODEL=gemini-3.5-flash
DEMO_MODE=true
```

### Model choose (Gemini 3)

| Model | Use case |
|-------|----------|
| `gemini-3.5-flash` | **Recommended** — fast, agent workflows, hackathon match |
| `gemini-3.1-pro-preview` | Beshi smart, slow, costly |
| `gemini-3-flash-preview` | Preview version |

Hackathon bole **Gemini 3** — `gemini-3.5-flash` use koro.

### Test koro

```powershell
cd C:\Users\Opi-AI\Desktop\logdataringcenterl\Google
py -m uvicorn backend.main:app --port 8080
```

Browser: http://localhost:5173 → query run → report Gemini theke asbe (fallback na).

---

## Step 2 — Elastic Cloud + MCP (45–60 min) 🔍

Hackathon **Elastic track** — real MCP connect korte hobe.

### 2.1 Elastic account

1. Jao: [Elastic Cloud](https://cloud.elastic.co/registration)
2. **Serverless** project create koro (free trial)
3. Deployment ready hole **Open Kibana** click koro

Resources: [Hackathon Elastic resources](https://rapid-agent.devpost.com/details/elastic-resources)

### 2.2 Agent Builder enable

1. Kibana → search **Agent Builder**
2. First time setup complete koro
3. **Tools** menu-te jao

### 2.3 Log tool banao

1. **Tools** → **+ New tool**
2. Type: **Search** (ba ES|QL)
3. Name: `search_error_logs`
4. Description: `Search application error and warn logs for incident triage`
5. Index: `logs-alertsense` (ba `logs-*`)
6. Save koro

### 2.4 Sample logs upload

Terminal-e (Elastic API key lagbe — step 2.5 theke pabe, ba Kibana Dev Tools):

```powershell
$env:ELASTICSEARCH_URL="https://YOUR-DEPLOYMENT.es.region.cloud.es.io:443"
$env:ELASTICSEARCH_API_KEY="YOUR_API_KEY"
py scripts/seed_elastic.py
```

### 2.5 API Key create

1. Kibana → **Stack Management** → **API Keys**
2. **Create API key**
3. Name: `alertsense-mcp`
4. Role: read access to log indices + Agent Builder
5. Key copy koro (ekbar-i dekhabe!)

### 2.6 MCP URL copy

1. Kibana → **Agent Builder** → **Tools**
2. Top-e **Manage MCP** dropdown
3. **Copy MCP Server URL** click koro

URL erokom hobe:
```
https://YOUR-PROJECT.kb.region.gcp.cloud.es.io/api/agent_builder/mcp
```

### 2.7 `.env`-e Elastic add koro

```env
ELASTIC_MCP_URL=https://YOUR-PROJECT.kb.region.gcp.cloud.es.io/api/agent_builder/mcp
ELASTIC_API_KEY=YOUR_BASE64_API_KEY

# Optional direct ES fallback
ELASTICSEARCH_URL=https://YOUR-DEPLOYMENT.es.region.cloud.es.io:443
ELASTICSEARCH_API_KEY=YOUR_API_KEY

# IMPORTANT: demo off koro
DEMO_MODE=false
```

### Test koro

App restart → UI-te **Mode: elastic** dekhabe (demo na).

Reference: [Elastic MCP server blog](https://www.elastic.co/search-labs/blog/elastic-mcp-server-agent-builder-tools)

---

## Step 3 — Google Cloud Agent Builder (45–60 min) ☁️

Hackathon **mandatory** — shudhu FastAPI na, **GCP Agent Builder** lagbe.

### Option A — Agent Studio (low-code, judges-friendly) ✅ Recommended

1. Jao: [Google Cloud Console](https://console.cloud.google.com/)
2. New project create koro (e.g. `alertsense-hackathon`)
3. Enable APIs:
   - **Vertex AI API**
   - **Gemini Enterprise Agent Platform API** (thakle)
4. Jao: **Vertex AI** → **Agent Builder** / **Agent Studio**
5. **Create Agent**:
   - Name: `AlertSense`
   - Model: **Gemini 3.5 Flash** (ba Gemini 3.1 Pro)
6. **System instruction** (copy from `backend/agent/prompts.py`):

```
You are AlertSense, an incident triage agent. You MUST use Elastic MCP tools to search logs before answering.

Workflow:
1. Detect incident from user message
2. Call Elastic search tool for ERROR/WARN logs (last 24h)
3. Analyze patterns (timeouts, deploys, circuit breakers)
4. Return: severity (P0/P1/P2), root cause, evidence, 3 fix steps

Never guess log content — always use tools first.
Human approves all actions.
```

7. **Add MCP Tool**:
   - Tool type: **MCP Server**
   - URL: tomar `ELASTIC_MCP_URL`
   - Auth header: `Authorization: ApiKey YOUR_ELASTIC_API_KEY`
8. **Test** in Agent Studio playground:
   - Ask: *"Customers say checkout is slow — what broke?"*
   - Verify Elastic tool call hocche
9. **Deploy** agent → hosted chat URL pabe → eta Devpost **Project URL** hote pare

Docs: [Agent Platform overview](https://cloud.google.com/products/gemini-enterprise-agent-platform)

### Option B — ADK code agent (developers)

Google **Agent Development Kit (ADK)** diye code-e agent + Elastic MCP:

```bash
pip install google-adk
adk create alertsense_agent
```

`agent.py`-te Elastic MCP add koro ([ADK MCP docs](https://adk.dev/tools-custom/mcp-tools/)):

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

elastic_mcp = MCPToolset(
    connection_params=SseServerParams(
        url="YOUR_ELASTIC_MCP_URL",
        headers={"Authorization": "ApiKey YOUR_KEY"},
    )
)

root_agent = Agent(
    model="gemini-3.5-flash",
    name="alertsense",
    instruction="...",  # same as above
    tools=[elastic_mcp],
)
```

Run: `adk web` → test → deploy Cloud Run.

### Tomar AlertSense app er shathe link

| Layer | Role |
|-------|------|
| **GCP Agent Builder** | Hackathon requirement — judges ekhane test korbe |
| **AlertSense UI (Cloud Run)** | Hosted demo URL — sundor UI + timeline |

**Best combo:** Agent Builder-e agent + AlertSense UI same Elastic MCP use kore — video-te dui ta show koro.

---

## Step 4 — Full `.env` example (sab milano)

```env
# === Gemini 3 ===
GOOGLE_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3.5-flash

# === Elastic MCP (partner track) ===
ELASTIC_MCP_URL=https://xxx.kb.us-central1.gcp.cloud.es.io/api/agent_builder/mcp
ELASTIC_API_KEY=base64-api-key-here
ELASTICSEARCH_URL=https://xxx.es.us-central1.gcp.cloud.es.io:443
ELASTICSEARCH_API_KEY=same-or-other-key

# === Demo OFF when Elastic connected ===
DEMO_MODE=false

PORT=8080
CORS_ORIGINS=http://localhost:5173,http://localhost:8080
```

---

## Step 5 — Verify checklist ✅

Run koro:

```powershell
py -m uvicorn backend.main:app --port 8080
```

Browser-e check:

| Check | Expected |
|-------|----------|
| UI mode pill | `elastic` (not demo) |
| `/api/health` | `gemini_configured: true`, `elastic_configured: true` |
| Investigate query | Real Gemini analysis + Elastic logs |
| Agent Builder playground | Elastic tool call visible |

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/health
```

---

## Step 6 — Submit items (baki)

| Item | Kivabe |
|------|--------|
| Hosted URL | Cloud Run deploy (see `docs/AGENT_BUILDER.md`) |
| GitHub public | Push repo + LICENSE in About |
| Demo video | `docs/DEMO_SCRIPT.md` follow koro |
| Devpost | Track: **Elastic** |

---

## Common problems

### `gemini_configured: false`
→ `GOOGLE_API_KEY` `.env`-e set hoyni ba server restart koro

### Still `demo` mode
→ `DEMO_MODE=false` + `ELASTIC_MCP_URL` + `ELASTIC_API_KEY` dui set koro

### Elastic MCP 401/403
→ API key-e `feature_agentBuilder.read` privilege check koro

### Gemini model error
→ `gemini-3.5-flash` try koro; na hole `gemini-2.5-flash`

---

## Quick order summary

```
1. GOOGLE_API_KEY + gemini-3.5-flash     (15 min)
2. Elastic Cloud + MCP URL + API key     (45 min)
3. GCP Agent Builder + Elastic MCP tool  (45 min)
4. DEMO_MODE=false + test                (10 min)
5. Cloud Run + GitHub + video + Devpost  (3 hr)
```

Kono step-e stuck hole bolo — kon step (1/2/3) e problem, screenshot/error path dile fix kore dibo.
