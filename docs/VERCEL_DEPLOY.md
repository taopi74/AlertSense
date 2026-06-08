# Deploy AlertSense to Vercel

## Why `experimentalServices` fails

Cursor/Vercel experimental config uses:

```json
"backend": { "routePrefix": "/_/backend" }
```

AlertSense frontend calls **`/api/health`**, **`/api/investigate`** — not `/_/backend`.

That mismatch causes **404 / deployment errors**.

Use the root **`vercel.json`** in this repo instead (already configured).

---

## Deploy steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Add Vercel deployment config"
git push
```

### 2. Import on Vercel

1. [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repo
3. **Root Directory:** project root (`Google` folder)
4. Framework: **Other** (vercel.json handles build)
5. Do **NOT** use experimentalServices backend prefix

### 3. Environment Variables (Vercel Dashboard → Settings → Environment Variables)

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

Click **Deploy**. Your URL will be:

```
https://your-project.vercel.app
```

---

## Architecture on Vercel

```
https://your-app.vercel.app/          → React UI (static)
https://your-app.vercel.app/api/*     → FastAPI (Python serverless)
```

---

## Important limits

| Item | Note |
|------|------|
| **Function timeout** | `/api/investigate` needs ~30s — set `maxDuration: 60` (Pro plan). Hobby = 10s may timeout |
| **Cold start** | First request may be slow |
| **Hackathon** | Cloud Run is also valid for hosted URL |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| 404 on `/api/investigate` | Remove experimentalServices; use repo `vercel.json` |
| Module not found `backend` | Ensure `api/index.py` exists at repo root |
| Build fails | Check `frontend/package.json` and Node 20 |
| Investigate timeout | Upgrade Vercel Pro or use Cloud Run |

---

## Alternative: Cloud Run (recommended for hackathon)

If Vercel times out, deploy with Docker:

```bash
gcloud run deploy alertsense --source . --region us-central1 --allow-unauthenticated
```

Use Cloud Run URL as Devpost **Try it out** link.
