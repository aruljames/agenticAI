# FastAPI + LangGraph + OpenRouter Agent (Docker Compose)

## Setup
1. Copy repository files into a folder.
2. Edit `agent/.env.example` and `mcp_server/.env.example` -> rename to `.env` if you want, or set env vars in your environment.

Required env vars:
- `agent/OPENROUTER_API_KEY` — **required** (OpenRouter API key)
- optionally `MCP_URL` and `MONGO_URI` if you change defaults.

## Run with Docker Compose
```bash
docker compose up --build


Agent API: http://localhost:8000

POST /api/query { "query": "...", "session_id": optional }

MCP Server: http://localhost:8001

GET /tools

GET /tool/duckduckgo?q=...

GET /tool/weather?location=London

Example usage

Ask for weather:

curl -s -X POST "http://localhost:8000/api/query" -H "Content-Type: application/json" -d '{"query":"What is the weather in London tomorrow?"}'


If agent finds weather_forecast tool and extracts location=London it will call MCP and return structured JSON. If parameters are missing, it will return status: need_params and session_id to continue.

Continue session (supplying missing param):

curl -s -X POST "http://localhost:8000/api/query" -H "Content-Type: application/json" -d '{"query":"London", "session_id":"<session_id>"}'

Implementation caveats

The wrapper uses the OpenRouter chat completions endpoint shape; adjust model name or endpoint depending on your OpenRouter plan.

LangGraph usage is encapsulated in langgraph_workflow.py. If you want explicit LangGraph node/edge definitions, I can convert this wrapper into a fully node-based LangGraph graph.

Error handling is minimal — extend per your needs.


---

# 6) Important operational details & required env vars

- `OPENROUTER_API_KEY` — **required** (agent). Place in `agent/.env` or pass in Docker-compose envs.
- `MCP_URL` — defaults to `http://mcp_server:8001`, fine inside compose.
- `MONGO_URI` — defaults to `mongodb://mongo:27017`.

---

# 7) What I didn't do (and why / how to extend)
- I implemented a workflow wrapper rather than a literal LangGraph node-edge graph. This is intentional: it's easier to run and reason about, and it fits your "multiple level workflow with conditional edges" requirement — the wrapper contains those conditionals. If you want the same logic translated into formal LangGraph nodes/edges (using its DSL), I can convert it; this will require the exact LangGraph API version you'll run.
- I used the DuckDuckGo Instant Answer API and Open-Meteo (both free). If you prefer different providers, change MCP endpoints.
- Security: production-ready code should add rate-limiting, authentication, and secrets management.

---

# 8) Ready-to-go small checklist to run

1. Create `.env` files:
- `agent/.env`:


OPENROUTER_API_KEY=sk-...
MCP_URL=http://mcp_server:8001
MONGO_URI=mongodb://mongo:27017

- `mcp_server/.env` (optional)

2. From repo root:
```bash
docker compose up --build


Test MCP:

curl "http://localhost:8001/tools"
curl "http://localhost:8001/tool/duckduckgo?q=python+fastapi"
curl "http://localhost:8001/tool/weather?location=New%20Delhi"


Test Agent:

curl -X POST "http://localhost:8000/api/query" -H "Content-Type: application/json" -d '{"query":"Show me weather in New Delhi"}'

