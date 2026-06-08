# Deploy AlertSense to Vercel

## Vercel UI — what to click

### Root Directory modal
Select **`AlertSense` (root)** — the top option with the repo name.

Do **NOT** select `frontend`, `backend`, or `api` alone.

### Framework
When Vercel shows **Services** with frontend + backend, that is correct.
Click **Refresh** after pushing the latest `vercel.json`.

---

## Why `/_/backend` fails

Vercel may auto-suggest:

```json
"backend": { "routePrefix": "/_/backend" }
```

AlertSense frontend calls **`/api/health`** and **`/api/investigate`**.

Backend must use **`"routePrefix": "/api"`** (see root `vercel.json`).

---

## Deploy steps

### 1. Push to GitHub

```bash
git add vercel.json api/ requirements.txt
git commit -m "Fix Vercel experimentalServices routing for /api"
git push
```

### 2. Import on Vercel

1. [vercel.com](https://vercel.com) → **Add New Project**
2. Import GitHub repo **AlertSense**
3. **Root Directory:** `AlertSense` (repo root) → **Continue**
4. Vercel should detect **Services** (Vite frontend + FastAPI backend)
5. Click **Refresh** if it asks for `vercel.json`

### 3. Environment Variables (Settings → Environment Variables)

| Variable | Value |
|----------|-------|
| `GOOGLE_API_KEY` | your Gemini key |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `ELASTIC_MCP_URL` | your Elastic MCP URL |
| `ELASTIC_API_KEY` | your Elastic API key |
| `ELASTICSEARCH_URL` | your ES cluster URL |
| `ELASTICSEARCH_API_KEY` | same API key |
| `DEMO_MODE` | `false` |

**Never commit `.env` to GitHub.**

### 4. Deploy

Your URL:

```
https://your-project.vercel.app
```

Test:

```
https://your-project.vercel.app/api/health
```

---

## Architecture on Vercel

```
/              → Vite React UI (frontend service)
/api/*         → FastAPI via api/index.py (backend service)
```

---

## Important limits

| Item | Note |
|------|------|
| **Function timeout** | `/api/investigate` ~30s — needs `maxDuration: 60` (Pro). Hobby = 10s may fail |
| **Cold start** | First request can be slow |
| **Hackathon** | Cloud Run is also valid for hosted URL |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| "vercel.json required" | Push latest `vercel.json`, click **Refresh** |
| Wrong root selected | Use repo root, not `frontend/` or `backend/` |
| 404 on `/api/*` | Backend `routePrefix` must be `/api`, not `/_/backend` |
| Module not found `backend` | Keep `api/index.py` at repo root |
| Investigate timeout | Vercel Pro or Cloud Run |

---

## Alternative: Cloud Run

```bash
gcloud run deploy alertsense --source . --region us-central1 --allow-unauthenticated
```

Use Cloud Run URL as Devpost **Try it out** link.
