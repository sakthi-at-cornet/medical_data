# Praval Medical Radiology Analytics System

AI-powered analytics platform for medical radiology audits, built on [Praval](https://pravalagents.com) - an event-driven multi-agent framework. The system uses 5 specialized AI agents that collaborate through Praval's Reef/Spore architecture to answer natural language questions about radiology quality scores, turnaround times, and radiologist performance.

## What This Project Demonstrates

- **Multi-Agent AI Architecture**: 5 agents (Domain Expert, Analytics Specialist, Visualization Specialist, Quality Inspector, Report Writer) working together without central orchestration
- **Event-Driven Communication**: Agents communicate through Praval's Spore messages, enabling parallel execution and graceful degradation
- **Medical Domain Intelligence**: Deep understanding of radiology terminology (CAT ratings, modalities), quality metrics, and audit workflows
- **End-to-End Data Pipeline**: Source databases → EL Pipeline → dbt transformations → Cube.js semantic layer → AI agents → Frontend

## Quick Start (6 Steps)

### Prerequisites
- Docker Desktop (running)
- OpenAI/Groq API key

### Step 1: Clone and Configure

```bash
# Clone repository
git clone https://github.com/<your-org>/praval_mds_analytics.git
cd praval_mds_analytics

# Create environment file from template
cp .env.example .env
```

Edit `.env` and add your API keys.

### Step 2: Start the System

```bash
# Start all services (takes ~2 minutes for databases to initialize)
docker-compose up -d

# Verify all services are running
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

- "What is the average quality score by modality?"
- "Compare CT vs MRI safety scores"
- "Show me the trend of CAT5 cases over the last month"
- "Which body part category has the lowest quality rating?"
- "Analyze radiologist performance for Neuro studies"

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
| cubejs | 4000 | Semantic layer (Radiology Cube) |
| postgres-medical | 5432 | Medical Metrics Database |
| postgres-warehouse | 5435 | Data warehouse |
| airflow-webserver | 8080 | Orchestration UI |


### AI Agents (Praval Framework)

The system uses 5 specialized agents built on [Praval](https://pravalagents.com), an event-driven multi-agent framework. Agents communicate through Praval's Reef/Spore architecture - Spores are JSON messages that flow between agents without central orchestration.

#### Agent Pipeline

```
User Query → Domain Expert → Analytics Specialist → [Visualization + Quality] → Report Writer → Response
```

| Agent | Responds To | Broadcasts | Purpose |
|-------|-------------|------------|---------|
| **Domain Expert** | `user_query` | `domain_enriched_request` | Medical terminology mapping, intent classification |
| **Analytics Specialist** | `domain_enriched_request` | `data_ready` | Query translation, Cube.js execution |
| **Visualization Specialist** | `data_ready` | `chart_ready` | Chart type selection, Chart.js specs |
| **Quality Inspector** | `data_ready` | `insights_ready` | Anomaly detection, root cause analysis |
| **Report Writer** | `chart_ready`, `insights_ready` | `final_response_ready` | Narrative composition |

#### How It Works

1. **User Query**: FastAPI receives a natural language question and broadcasts a `user_query` Spore
2. **Domain Enrichment**: Domain Expert maps user terms to medical entities (e.g., "head scan" → CT/MRI Brain)
3. **Query Execution**: Analytics Specialist translates to Cube.js query and executes against the semantic layer
4. **Parallel Processing**: Visualization Specialist and Quality Inspector run simultaneously on the data
5. **Response Composition**: Report Writer waits for both agents, then composes a narrative with chart and insights

#### Key Design Decisions

- **No Orchestrator**: Agents self-coordinate via pub/sub messaging on the Reef
- **Parallel Execution**: Visualization + Quality agents run simultaneously for faster response
- **Session Correlation**: Report Writer uses `session_id` to match chart and insights from the same query
- **Graceful Degradation**: System works even if one agent fails (e.g., returns chart without insights)
- **LLM Integration**: Each agent uses Groq/OpenAI for its specific domain task

See [docs/AGENT_ARCHITECTURE.md](docs/AGENT_ARCHITECTURE.md) for detailed implementation and Spore schemas.

### Data Model

**Medical Data:**
- **Radiology Audits**: Detailed audit logs including Modality, Body Part, Quality Score (0-100), Safety Score, and CAT Ratings.

**Key Metrics:**
- **Quality Score**: Composite score of report accuracy and clarity.
- **Safety Score**: Metric focused on patient safety and critical findings.
- **CAT Rating**: Peer review category (CAT1=Good, CAT5=Severe Discrepancy).
- **Turnaround Time (TAT)**: Assignment to Report generation time.

**Cube.js Semantic Layer:**
- `RadiologyAudits`: Comprehensive cube covering all audit metrics and dimensions.

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
docker exec postgres-medical psql -U medical_user -d medical_metrics -c "SELECT COUNT(*) FROM medical.radiology_audits"
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
- [Medical Data Schema](docs/MEDICAL_DATA_SCHEMA.md) - Dataset specification and use cases

---

## License

MIT

## Support

For issues and questions, please open a GitHub issue.
