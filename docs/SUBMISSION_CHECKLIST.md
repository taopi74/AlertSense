# Hackathon Submission Checklist — AlertSense

Deadline: **June 11, 2026 — 2:00 PM PT**

## Fixed in this repo

| Requirement | Implementation |
|-------------|----------------|
| Gemini at runtime | `backend/agent/gemini.py` |
| Google Cloud Agent Builder at runtime | `backend/agent/agent_builder.py` (Google ADK) |
| Elastic MCP at runtime | `backend/elastic/mcp_client.py` (tool: `search_error_logs`) |
| MCP 406 error | Fixed `Accept: application/json, text/event-stream` header |
| Wrong MCP tool name | Now uses `search_error_logs` (not generic `search`) |
| MCP search order | MCP first, then Elasticsearch fallback |

## Devpost form

| Field | Value |
|-------|-------|
| Track | Elastic |
| New or existing | **New** (first commit Jun 8, 2026) |
| Repo | https://github.com/taopi74/AlertSense |
| Hosted URL | https://alert-sense.vercel.app |
| Google Cloud products | Gemini API, Google Cloud Agent Builder (ADK) |
| Other tools | Elastic Cloud, Elastic Agent Builder MCP, FastAPI, React, Vercel |

## Before final submit

- [ ] GitHub repo **public** + MIT license in About section
- [ ] Vercel env vars set (see README)
- [ ] Test: https://alert-sense.vercel.app/api/health → all `true`
- [ ] Test: Investigate on live site works
- [ ] Demo video on YouTube (**public**, under 3 min)
- [ ] Devpost video URL added
- [ ] Push latest code: `git push`

## Quick test (local)

```powershell
py -m uvicorn backend.main:app --port 8081
curl http://localhost:8081/api/health
```

Expected health response:
```json
{
  "gemini_configured": true,
  "elastic_configured": true,
  "agent_builder_configured": true
}
```

## Vercel redeploy after push

1. Push to GitHub
2. Vercel auto-redeploys
3. Verify `/api/health` on production
4. Run one Investigate on https://alert-sense.vercel.app
