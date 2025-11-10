# Phase 6: Agentic Analytics UI - Quick Start

## Overview

Chat-first analytics interface where you ask questions in natural language and AI agents return insights with visualizations.

## Architecture

```
Frontend (Next.js) → Backend (FastAPI + 2 Agents) → Cube.js → Warehouse
Port 3000            Port 8000                       Port 4000
```

## Services

| Service | Port | Status |
|---------|------|--------|
| Frontend UI | 3000 | http://localhost:3000 |
| Agents API | 8000 | http://localhost:8000 |
| Cube.js | 4000 | http://localhost:4000 |
| Warehouse | 5435 | PostgreSQL |

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

### 2. Verify Services

```bash
# Check all services running
docker-compose ps

# Check agents health
curl http://localhost:8000/health

# Expected: {"status":"healthy","version":"0.1.0","cubejs_connected":true}
```

### 3. Access Frontend

Open browser: http://localhost:3000

### 4. Try Example Questions

- "What is the overall pass rate?"
- "Which component has the best quality?"
- "Show me quality trends over time"
- "Which material has the best quality?"
- "Compare materials by pass rate"

## API Usage

### Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the overall pass rate?"}'
```

**Response**:
```json
{
  "message": "• Springs highest at 95.33%...",
  "session_id": "uuid",
  "chart": {
    "chart_type": "table",
    "data": [...],
    "title": "Pass Rate by Component"
  },
  "insights": [
    "Springs have highest pass rate...",
    "Bodies need attention at 91%..."
  ],
  "suggested_questions": [
    "Which material has best quality?",
    "Show trends over time"
  ]
}
```

## Development

### Backend (Agents)

```bash
# Install dependencies
cd agents
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start dev server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Install dependencies
cd frontend
npm install

# Run dev server
npm run dev

# Build production
npm run build
npm start
```

## Environment Variables

Required in `.env`:

```bash
OPENAI_API_KEY=your-key-here
```

## Troubleshooting

### Agents service fails to start
```bash
# Check logs
docker logs analytics-agents

# Common fix: Cube.js not ready
docker-compose restart agents
```

### Frontend can't reach backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Restart frontend
docker-compose restart frontend
```

### "No data available" in UI
```bash
# Verify pipeline ran
docker logs airflow-scheduler | grep manufacturing_dag

# Re-run dbt if needed
docker-compose exec airflow-webserver bash
airflow dags trigger manufacturing_dag
```

## Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f analytics-agents
docker logs -f analytics-frontend

# Recent logs
docker logs analytics-agents --tail 50
```

## Testing

### Backend Tests
```bash
cd agents
pytest tests/ -v --cov
```

### Integration Test
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which material has best quality?"}'
```

## Key Features

✓ Natural language questions
✓ AI-powered query translation
✓ Cube.js integration
✓ Chart visualizations (bar, line, table)
✓ Conversation context
✓ Insight generation
✓ Follow-up suggestions
✓ Session management

## Tech Stack

- **Backend**: FastAPI, OpenAI GPT-4o-mini, Praval, Python 3.11
- **Frontend**: Next.js 14, React 18, TypeScript, Chart.js
- **Data**: Cube.js, PostgreSQL
- **Container**: Docker, Docker Compose

## Documentation

- Full implementation: `AGENTIC_UI_SUMMARY.md`
- Overall progress: `plan.md`
- System foundation: `current_state.md`

## Next Steps

Access UI at http://localhost:3000 and start asking questions about your manufacturing data!
