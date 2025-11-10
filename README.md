# Praval Manufacturing Analytics System

AI-powered analytics platform for automotive press manufacturing, featuring multi-agent intelligence and real-time data insights.

## Overview

This system provides comprehensive analytics for automotive stamping operations, tracking production metrics across two press lines:
- **Line A (800T)**: Door outer panels (Left/Right)
- **Line B (1200T)**: Bonnet outer panels

## Architecture

### Data Pipeline
```
Source DBs → EL Pipeline → Data Warehouse (PostgreSQL)
    ↓
dbt Transformations → Staging → Marts
    ↓
Cube.js Semantic Layer
    ↓
AI Agents → Frontend (Next.js)
```

### Key Components

1. **Source Databases (PostgreSQL)**
   - Press Line A production data
   - Press Line B production data
   - Die management system
   - Material coil tracking
   - Legacy pen production (refills, bodies, springs)

2. **Data Warehouse**
   - Unified data storage
   - Foreign Data Wrappers for cross-database queries
   - Staging and mart schemas

3. **dbt Transformation Layer**
   - 4 staging models (data cleansing)
   - 2 intermediate models (business logic)
   - 3 mart models (analytics-ready)

4. **Cube.js Semantic Layer**
   - `PressOperations`: Production-level data with traceability
   - `PartFamilyPerformance`: Aggregated performance by part type
   - `PressLineUtilization`: Line capacity and shift analysis

5. **AI Agents (OpenAI)**
   - Chat Agent: Conversation management
   - Data Analyst Agent: Query translation and insights

6. **Frontend (Next.js)**
   - Interactive chat interface
   - Dynamic visualizations
   - Real-time status monitoring

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd praval_mds_analytics
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start the system**
   ```bash
   docker-compose up -d
   ```

4. **Wait for initialization** (~2 minutes for databases to populate)

5. **Run dbt transformations**
   ```bash
   docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Cube.js Playground: http://localhost:4000
   - Airflow: http://localhost:8080 (admin/admin)
   - Agents API: http://localhost:8000/docs

## Data Model

### Press Operations Fact Table
- **Grain:** One row per part produced
- **Metrics:** OEE, defect counts, costs, cycle time, tonnage
- **Dimensions:** Part family, press line, die, material, shift, operator, defect type

### Part Family Performance (Aggregated)
- **Grain:** One row per part family
- **Metrics:** First pass yield, rework rate, total costs, material correlation
- **Dimensions:** Part family, part type, material grade

### Press Line Utilization (Aggregated)
- **Grain:** One row per press line
- **Metrics:** Overall OEE, shift productivity, weekend/weekday split
- **Dimensions:** Press line, part type

## Manufacturing Metrics

### OEE (Overall Equipment Effectiveness)
```
OEE = Availability × Performance × Quality Rate

- Availability: Uptime / Planned production time
- Performance: Actual output / Target output
- Quality Rate: Good parts / Total parts produced
```

### Key Performance Indicators
- **Pass Rate:** Percentage of parts passing quality inspection
- **First Pass Yield:** Percentage of parts passing without rework
- **Defect Rate:** Percentage of parts with defects by type
- **Cycle Time:** Time per part (Line A: 1.2-1.5s, Line B: 3.5-4.5s)
- **Tonnage:** Press force (Line A: 600-650T, Line B: 900-1100T)

## Example Queries

Ask the AI agents natural language questions:

- "What's the OEE for each press line?"
- "Which part family has the best quality?"
- "Show me defect trends over time"
- "Compare shift performance"
- "What's the cost per part by line?"
- "Show me springback defects for Door_Outer_Left"

## Development

### Project Structure
```
praval_mds_analytics/
├── agents/              # AI agents (FastAPI)
├── airflow/             # Orchestration DAGs
├── cubejs/              # Semantic layer schemas
├── dbt_transform/       # dbt models
├── docker/              # Database initialization scripts
├── el_pipeline/         # Extract-Load pipeline
├── frontend/            # Next.js UI
├── tests/               # Test suites
└── docs/                # Documentation
    ├── AGENT_ARCHITECTURE.md    # Multi-agent system design
    ├── IMPLEMENTATION_PLAN.md   # Development roadmap
    └── planning/                # Historical planning docs
```

### Running Tests
```bash
# Python tests
pytest

# dbt tests
docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform
```

### Adding New Data Sources
1. Create database init script in `docker/postgres/<source-name>/`
2. Add service to `docker-compose.yml`
3. Create Foreign Data Wrapper in warehouse `init.sql`
4. Add source to `dbt_transform/models/staging/sources.yml`
5. Create staging model in dbt
6. Create Cube.js schema

## Technologies

- **Backend:** FastAPI, Python 3.11
- **Database:** PostgreSQL 15
- **Data Transformation:** dbt 1.7
- **Orchestration:** Apache Airflow 2.7
- **Semantic Layer:** Cube.js
- **AI:** OpenAI GPT-4
- **Frontend:** Next.js 14, React, TypeScript
- **Infrastructure:** Docker, Docker Compose

## Architecture Decisions

### Why Foreign Data Wrappers?
Maintains separate source databases (realistic for manufacturing) while enabling centralized analytics without complex ETL.

### Why Cube.js?
Pre-aggregations for fast queries, semantic layer for consistent metrics, REST API for easy integration.

### Why Multi-Agent System?
Specialized agents for different aspects:
- Manufacturing domain expertise
- Query optimization
- Visualization selection
- Quality analysis
- Report writing

See [AGENT_ARCHITECTURE.md](docs/AGENT_ARCHITECTURE.md) for detailed design.

## Roadmap

### Current Implementation (v0.1)
- ✅ Automotive press data pipeline
- ✅ dbt transformations
- ✅ Cube.js semantic layer
- ✅ Basic AI agents (2-agent system)
- ✅ Interactive frontend

### Planned (v0.2)
- [ ] 5-agent architecture (Manufacturing Advisor, Analytics Specialist, Visualization Specialist, Quality Inspector, Report Writer)
- [ ] Advanced query understanding ("doors parts" → Door_Outer_Left + Door_Outer_Right)
- [ ] Root cause analysis with domain knowledge
- [ ] Clarification questions for ambiguous queries
- [ ] Enhanced visualizations (grouped bars, time series)

See [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for full roadmap.

## Contributing

See [AGENT_ARCHITECTURE.md](docs/AGENT_ARCHITECTURE.md) for agent development guidelines.

## License

MIT

## Support

For issues and questions, please open a GitHub issue.
