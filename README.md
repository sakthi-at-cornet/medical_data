# Praval Manufacturing Analytics System

AI-powered analytics platform for automotive press manufacturing, built on [Praval](https://pravalagents.com) - an event-driven multi-agent framework. The system uses 5 specialized AI agents that collaborate through Praval's Reef/Spore architecture to answer natural language questions about production metrics, quality trends, and manufacturing performance.

## What This Project Demonstrates

- **Multi-Agent AI Architecture**: 5 agents (Manufacturing Advisor, Analytics Specialist, Visualization Specialist, Quality Inspector, Report Writer) working together without central orchestration
- **Event-Driven Communication**: Agents communicate through Praval's Spore messages, enabling parallel execution and graceful degradation
- **Manufacturing Domain Intelligence**: Deep understanding of press shop terminology, OEE calculations, defect analysis, and die management
- **End-to-End Data Pipeline**: Source databases → EL Pipeline → dbt transformations → Cube.js semantic layer → AI agents → Frontend

## Quick Start (6 Steps)

### Prerequisites
- Docker Desktop (running)
- OpenAI API key

### Step 1: Clone and Configure

```bash
# Clone repository
git clone https://github.com/<your-org>/praval_mds_analytics.git
cd praval_mds_analytics

# Create environment file from template
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Step 2: Start the System

```bash
# Start all services (takes ~2 minutes for databases to initialize)
docker-compose up -d

# Verify all 10 services are running
docker-compose ps
```

### Step 3: Run dbt Transformations

```bash
# Run dbt models (creates staging → intermediate → mart tables)
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform

# Verify models ran successfully
docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform
```

### Step 4: Verify the System

```bash
# Check agents API health
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"0.1.0","cubejs_connected":true}

# Check agents are registered
curl http://localhost:8000/agents
```

### Step 5: Access the Application

| Application | URL | Description |
|-------------|-----|-------------|
| **Frontend** | http://localhost:3000 | Chat interface |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Cube Playground** | http://localhost:4000 | Query builder |
| **Airflow** | http://localhost:8080 | DAG monitoring (admin/admin) |

### Step 6: Try Sample Queries

In the frontend chat (http://localhost:3000), try these queries:

- "What's the OEE for each press line?"
- "Compare Door_Outer_Left vs Door_Outer_Right by defect type"
- "Show me quality trends over the last 30 days"
- "Which shift has the best performance?"
- "What are the main defect types for bonnet panels?"

---

## Architecture

### Data Pipeline
```
Source DBs → EL Pipeline → Data Warehouse (PostgreSQL)
    ↓
dbt Transformations → Staging → Marts
    ↓
Cube.js Semantic Layer
    ↓
AI Agents (Praval) → Frontend (Next.js)
```

### Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| analytics-agents | 8000 | FastAPI + Praval 5-agent system |
| analytics-frontend | 3000 | Next.js chat UI |
| cubejs | 4000 | Semantic layer (3 cubes) |
| postgres-press-line-a | 5436 | Door panel production (2,160 records) |
| postgres-press-line-b | 5437 | Bonnet panel production (2,160 records) |
| postgres-die-management | 5438 | Die data (4 dies + assessments) |
| postgres-warehouse | 5435 | Data warehouse |
| airflow-webserver | 8080 | Orchestration UI |


### AI Agents (Praval Framework)

The system uses 5 specialized agents built on [Praval](https://pravalagents.com), an event-driven multi-agent framework. Agents communicate through Praval's Reef/Spore architecture - Spores are JSON messages that flow between agents without central orchestration.

#### Agent Pipeline

```
User Query → Manufacturing Advisor → Analytics Specialist → [Visualization + Quality] → Report Writer → Response
```

| Agent | Responds To | Broadcasts | Purpose |
|-------|-------------|------------|---------|
| **Manufacturing Advisor** | `user_query` | `domain_enriched_request` | Domain expertise, terminology mapping |
| **Analytics Specialist** | `domain_enriched_request` | `data_ready` | Query translation, Cube.js execution |
| **Visualization Specialist** | `data_ready` | `chart_ready` | Chart type selection, Chart.js specs |
| **Quality Inspector** | `data_ready` | `insights_ready` | Anomaly detection, root cause analysis |
| **Report Writer** | `chart_ready`, `insights_ready` | `final_response_ready` | Narrative composition |

#### How It Works

1. **User Query**: FastAPI receives a natural language question and broadcasts a `user_query` Spore
2. **Domain Enrichment**: Manufacturing Advisor maps user terms to domain entities (e.g., "doors" → Door_Outer_Left, Door_Outer_Right)
3. **Query Execution**: Analytics Specialist translates to Cube.js query and executes against the semantic layer
4. **Parallel Processing**: Visualization Specialist and Quality Inspector run simultaneously on the data
5. **Response Composition**: Report Writer waits for both agents, then composes a narrative with chart and insights

#### Key Design Decisions

- **No Orchestrator**: Agents self-coordinate via pub/sub messaging on the Reef
- **Parallel Execution**: Visualization + Quality agents run simultaneously for faster response
- **Session Correlation**: Report Writer uses `session_id` to match chart and insights from the same query
- **Graceful Degradation**: System works even if one agent fails (e.g., returns chart without insights)
- **LLM Integration**: Each agent uses GPT-4o-mini for its specific domain task

See [docs/AGENT_ARCHITECTURE.md](docs/AGENT_ARCHITECTURE.md) for detailed implementation and Spore schemas.

### Data Model

**Press Lines:**
- **Line A (800T)**: Door outer panels (Left/Right) - 90 days of hourly data
- **Line B (1200T)**: Bonnet outer panels - 90 days of hourly data

**Key Metrics:**
- OEE (Availability × Performance × Quality Rate)
- Defect rates by type (springback, burr, surface scratch, etc.)
- Cycle time, tonnage, material costs
- Shift and operator performance

**Cube.js Semantic Layer:**
- `PressOperations`: Production-level data with full traceability
- `PartFamilyPerformance`: Aggregated performance by part type
- `PressLineUtilization`: Line capacity and shift analysis

---

## Development

### Project Structure
```
praval_mds_analytics/
├── agents/              # AI agents (FastAPI + Praval)
├── airflow/             # Orchestration DAGs
├── cubejs/              # Semantic layer schemas
├── dbt_transform/       # dbt models
├── docker/              # Database initialization scripts
├── el_pipeline/         # Extract-Load pipeline
├── frontend/            # Next.js UI
├── tests/               # Test suites
└── docs/                # Documentation
```

### Running Tests

```bash
# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
./venv/bin/pytest

# Run with coverage
./venv/bin/pytest --cov=agents --cov=el_pipeline --cov-report=html
```

### Adding New Data Sources

1. Create database init script in `docker/postgres/<source-name>/`
2. Add service to `docker-compose.yml`
3. Create Foreign Data Wrapper in warehouse `init.sql`
4. Add source to `dbt_transform/models/staging/sources.yml`
5. Create staging model in dbt
6. Create Cube.js schema

---

## Troubleshooting

### Docker containers not starting

```bash
# Check container logs
docker-compose logs <service-name>

# Restart all services
docker-compose down && docker-compose up -d

# Full reset (removes data volumes)
docker-compose down -v && docker-compose up -d
```

### Database connection errors

```bash
# Verify databases are healthy
docker-compose ps

# Check if data was loaded
docker exec postgres-press-line-a psql -U press_a_user -d press_line_a -c "SELECT COUNT(*) FROM press_line_a_production"
```

### Agents API not responding

```bash
# Check agent logs
docker logs analytics-agents --tail 100

# Verify OpenAI API key is set
docker exec analytics-agents env | grep OPENAI
```

### Cube.js not returning data

```bash
# Check Cube.js logs
docker logs cubejs --tail 100

# Verify cubes are loaded
curl http://localhost:4000/cubejs-api/v1/meta
```

### dbt transformations failing

```bash
# Run with debug output
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform --debug

# Check warehouse connection
docker exec analytics-agents ./venv/bin/dbt debug --project-dir=dbt_transform
```

### Port already in use

```bash
# Find what's using the port
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

---

## Technologies

- **AI Framework:** [Praval](https://pravalagents.com) 0.7.16 (Reef/Spores event-driven architecture)
- **LLM:** OpenAI GPT-4o-mini
- **Backend:** FastAPI, Python 3.11
- **Database:** PostgreSQL 15
- **Data Transformation:** dbt 1.7
- **Orchestration:** Apache Airflow 2.7
- **Semantic Layer:** Cube.js
- **Frontend:** Next.js 14, React, TypeScript
- **Infrastructure:** Docker, Docker Compose

---

## Documentation

- [Data Architecture](docs/DATA_ARCHITECTURE.md) - End-to-end system architecture (source DBs, dbt, Cube.js, Airflow, agents)
- [Agent Architecture](docs/AGENT_ARCHITECTURE.md) - Detailed Praval multi-agent implementation and Spore schemas
- [Automotive Dataset](docs/AUTOMOTIVE_DATASET.md) - Dataset specification and use cases

---

## License

MIT

## Support

For issues and questions, please open a GitHub issue.
