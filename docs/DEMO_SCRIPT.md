# AlertSense — 3-Minute Demo Script

Use this script for your Devpost submission video.

## Setup before recording

1. Run app locally or on Cloud Run
2. Open UI in browser (dark theme looks good on video)
3. Close unrelated tabs
4. Optional: show Kibana in second tab (Elastic MCP connected)

## Script (≈ 2:45)

### 0:00 — Hook (15 sec)

> "Small teams get hundreds of Elastic alerts every day. But which ones actually need fixing?
> AlertSense is an AI agent that searches your logs, finds the root cause, and tells you exactly what to do."

### 0:15 — Problem (20 sec)

> "When customers say checkout is slow, engineers spend hours jumping between Kibana, deploy logs, and Slack.
> Elastic finds the anomalies — but it doesn't give you an action plan. That's the gap AlertSense fills."

Show: empty UI or noisy Kibana alerts (optional screenshot)

### 0:35 — Live demo (90 sec)

1. Click example chip: **"Customers say checkout is slow — what broke?"**
2. Click **Run Agent**
3. Narrate as timeline appears:
   - "Step 1 — agent detects incident intent"
   - "Step 2 — searches logs via **Elastic MCP**"
   - "Step 3 — Gemini analyzes the pattern"
   - "Step 4 — severity **P1** with fix steps"

4. Scroll to show:
   - Root cause: payment-api timeouts
   - Evidence logs with trace IDs
   - 3 fix steps (rollback, monitor, add test)

> "In under 30 seconds we went from user complaint to root cause and remediation — not just an answer, but action."

### 2:05 — Tech stack (25 sec)

> "Built for the Google Cloud Rapid Agent Hackathon — **Gemini** for reasoning, **Elastic MCP** for log retrieval,
> multi-step orchestration with human oversight. Deployed on **Cloud Run**."

Show: architecture diagram from README (optional)

### 2:30 — Impact + close (15 sec)

> "Alert fatigue hits every small SaaS team. AlertSense turns log noise into on-call clarity.
> Open source, Elastic track, ready for production."

Show: GitHub repo URL + hosted demo URL on screen

## Recording tips

- Use OBS or Loom, 1080p
- Speak clearly, moderate pace
- Highlight **Elastic MCP** and **multi-step timeline** — judges look for this
- Keep under 3 minutes
