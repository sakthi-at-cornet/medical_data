# Praval Manufacturing Analytics System - Complete Project Analysis

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Databases Used](#2-databases-used)
3. [AI Agent System](#3-ai-agent-system)
4. [Data Pipeline Architecture](#4-data-pipeline-architecture)
5. [Semantic Layer (Cube.js)](#5-semantic-layer-cubejs)
6. [Frontend Application](#6-frontend-application)
7. [How to Run the Application](#7-how-to-run-the-application)
8. [Configuration & Environment Variables](#8-configuration--environment-variables)
9. [Project Structure](#9-project-structure)
10. [Troubleshooting Guide](#10-troubleshooting-guide)

---

## 1. Project Overview

**Praval Manufacturing Analytics System** is an AI-powered analytics platform for **automotive press manufacturing**. It uses a multi-agent AI architecture built on the [Praval Framework](https://pravalagents.com) - an event-driven multi-agent framework.

### Key Features:
- **Natural Language Querying**: Ask questions in plain English about manufacturing data
- **5 Specialized AI Agents**: Work together without central orchestration
- **Event-Driven Communication**: Agents communicate through Praval's Reef/Spore architecture
- **End-to-End Data Pipeline**: From source databases to frontend visualization
- **Manufacturing Domain Intelligence**: Deep understanding of press shop terminology, OEE calculations

### Technologies Used:
| Category | Technology |
|----------|------------|
| AI Framework | Praval 0.7.16 (Reef/Spores architecture) |
| LLM | OpenAI GPT-4o-mini |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 15 |
| Data Transformation | dbt 1.7 |
| Orchestration | Apache Airflow 2.7 |
| Semantic Layer | Cube.js |
| Frontend | Next.js 14, React, TypeScript |
| Infrastructure | Docker, Docker Compose |

---

## 2. Databases Used

The system uses **5 PostgreSQL databases** running in Docker containers:

### 2.1. Source Databases (Simulated MES Systems)

| Database | Container Name | Port | Purpose | Data |
|----------|---------------|------|---------|------|
| **Press Line A** | `postgres-press-line-a` | 5436 | 800T Press for Door panels | 2,160 records (90 days hourly) |
| **Press Line B** | `postgres-press-line-b` | 5437 | 1200T Press for Bonnet panels | 2,160 records (90 days hourly) |
| **Die Management** | `postgres-die-management` | 5438 | Die lifecycle data | 4 dies + assessments |

### 2.2. Data Warehouse

| Database | Container Name | Port | Purpose |
|----------|---------------|------|---------|
| **Warehouse** | `postgres-warehouse` | 5435 | Consolidated analytics data warehouse |

### 2.3. Infrastructure Database

| Database | Container Name | Port | Purpose |
|----------|---------------|------|---------|
| **Airflow DB** | `airflow-db` | 5432 (internal) | Airflow metadata storage |

### Database Credentials:

```yaml
# Press Line A
Host: localhost:5436
Database: press_line_a
User: press_a_user
Password: press_a_pass

# Press Line B
Host: localhost:5437
Database: press_line_b
User: press_b_user
Password: press_b_pass

# Die Management
Host: localhost:5438
Database: die_management
User: die_mgmt_user
Password: die_mgmt_pass

# Warehouse
Host: localhost:5435
Database: warehouse
User: warehouse_user
Password: warehouse_pass
```

---

## 3. AI Agent System

The system uses **5 specialized AI agents** built on the Praval framework. Agents communicate through **Spores** (JSON messages) on a **Reef** (message queue network).

### 3.1. Agent Architecture

```
User Query → Manufacturing Advisor → Analytics Specialist → [Visualization + Quality] → Report Writer → Response
```

### 3.2. The 5 Agents

| Agent | File | Responds To | Broadcasts | Purpose |
|-------|------|-------------|------------|---------|
| **Manufacturing Advisor** | `manufacturing_advisor.py` | `user_query` | `domain_enriched_request` | Domain expertise, terminology mapping, guardrails |
| **Analytics Specialist** | `analytics_specialist.py` | `domain_enriched_request` | `data_ready` | Query translation, Cube.js execution |
| **Visualization Specialist** | `visualization_specialist.py` | `data_ready` | `chart_ready` | Chart type selection, Chart.js specs |
| **Quality Inspector** | `quality_inspector.py` | `data_ready` | `insights_ready` | Anomaly detection, root cause analysis |
| **Report Writer** | `report_writer.py` | `chart_ready`, `insights_ready` | `final_response_ready` | Narrative composition |

### 3.3. Spore Message Flow

1. **User Query** → FastAPI receives question, broadcasts `user_query` Spore
2. **Domain Enrichment** → Manufacturing Advisor maps terms to entities (e.g., "doors" → Door_Outer_Left)
3. **Query Execution** → Analytics Specialist translates to Cube.js query and executes
4. **Parallel Processing** → Visualization Specialist AND Quality Inspector run simultaneously
5. **Response Composition** → Report Writer waits for both, composes final narrative

### 3.4. Key Spore Schemas (from `spore_schemas.py`)

```python
# User Query (Frontend → Manufacturing Advisor)
UserQueryKnowledge:
  - message: str        # User's natural language query
  - session_id: str     # Unique session identifier
  - context: List[Dict] # Previous conversation

# Domain Enriched Request (Manufacturing Advisor → Analytics Specialist)
DomainEnrichedRequestKnowledge:
  - user_intent: str          # Classified intent
  - part_families: List[str]  # Part families involved
  - metrics: List[str]        # Metrics requested
  - dimensions: List[str]     # Dimensions for breakdown
  - cube_recommendation: str  # Recommended Cube.js cube

# Data Ready (Analytics Specialist → Viz + Quality)
DataReadyKnowledge:
  - query_results: List[Dict] # Query result rows
  - cube_used: str           # Cube.js cube queried
  - measures: List[str]      # Measures queried
  - dimensions: List[str]    # Dimensions queried

# Final Response (Report Writer → Frontend)
FinalResponseReadyKnowledge:
  - narrative: str           # Composed narrative
  - chart_spec: Dict         # Chart.js specification
  - follow_ups: List[str]    # Suggested follow-up questions
```

### 3.5. Key Design Decisions

- **No Orchestrator**: Agents self-coordinate via pub/sub messaging on the Reef
- **Parallel Execution**: Visualization + Quality agents run simultaneously
- **Session Correlation**: Report Writer uses `session_id` to match chart and insights
- **Graceful Degradation**: System works even if one agent fails

---

## 4. Data Pipeline Architecture

```
Source DBs (Press A, B, Die Mgmt)
    ↓
EL Pipeline (Extract-Load)
    ↓
Data Warehouse (PostgreSQL)
    ↓
dbt Transformations (staging → intermediate → marts)
    ↓
Cube.js Semantic Layer
    ↓
AI Agents (Praval)
    ↓
Frontend (Next.js)
```

### 4.1. EL Pipeline (`el_pipeline/`)

| File | Purpose |
|------|---------|
| `extractor.py` | Extracts data from source databases |
| `loader.py` | Loads data into warehouse |
| `pipeline.py` | Orchestrates extract-load flow |
| `config.py` | Database connection settings |

### 4.2. dbt Transformations (`dbt_transform/`)

```
models/
├── staging/      # Raw data cleaning
├── intermediate/ # Business logic
└── marts/        # Analytics-ready tables
```

**Run dbt transformations:**
```bash
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform
```

---

## 5. Semantic Layer (Cube.js)

Cube.js provides a semantic layer on top of the data warehouse. It defines **3 cubes** for querying:

### 5.1. Available Cubes

| Cube | File | Purpose |
|------|------|---------|
| `PressOperations` | `PressOperations.js` | Production-level data with full traceability |
| `PartFamilyPerformance` | `PartFamilyPerformance.js` | Aggregated performance by part type |
| `PressLineUtilization` | `PressLineUtilization.js` | Line capacity and shift analysis |

### 5.2. Cube.js Configuration

```yaml
Container: cubejs
Port: 4000
API URL: http://localhost:4000/cubejs-api/v1
Playground: http://localhost:4000
```

### 5.3. Key Metrics Available

- **OEE** (Availability × Performance × Quality Rate)
- **Defect rates** by type (springback, burr, surface scratch, etc.)
- **Cycle time**, tonnage, material costs
- **Shift and operator performance**

---

## 6. Frontend Application

### 6.1. Technology Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI**: React components
- **Charts**: Chart.js

### 6.2. Access URL

```
http://localhost:3000
```

### 6.3. Sample Queries to Try

- "What's the OEE for each press line?"
- "Compare Door_Outer_Left vs Door_Outer_Right by defect type"
- "Show me quality trends over the last 30 days"
- "Which shift has the best performance?"
- "What are the main defect types for bonnet panels?"

---

## 7. How to Run the Application

### Prerequisites
- **Docker Desktop** (running)
- **OpenAI API Key**

### Step 1: Clone and Configure

```bash
# Clone repository
git clone https://github.com/<your-org>/praval_mds_analytics.git
cd praval_mds_analytics

# Create environment file
cp .env.example .env
```

### Step 2: Add OpenAI API Key

Edit `.env` and add your key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Start All Services

```bash
# Start all 10+ services (takes ~2 minutes)
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### Step 4: Run dbt Transformations

```bash
# Run dbt models (staging → intermediate → mart tables)
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform

# Verify models ran successfully
docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform
```

### Step 5: Verify the System

```bash
# Check agents API health
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"0.1.0","cubejs_connected":true}

# Check agents are registered
curl http://localhost:8000/agents
```

### Step 6: Access the Application

| Application | URL | Description |
|-------------|-----|-------------|
| **Frontend** | http://localhost:3000 | Chat interface |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Cube Playground** | http://localhost:4000 | Query builder |
| **Airflow** | http://localhost:8080 | DAG monitoring (admin/admin) |

---

## 8. Configuration & Environment Variables

### 8.1. Required Environment Variables (`.env`)

```bash
# Required - OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# Optional - Override defaults
OPENAI_MODEL=gpt-4o-mini
CUBEJS_API_URL=http://localhost:4000/cubejs-api/v1
CUBEJS_API_SECRET=your-cubejs-secret
LOG_LEVEL=INFO
```

### 8.2. Docker Compose Environment Variables

These are set in `docker-compose.yml`:

```yaml
# Agents Service
- OPENAI_API_KEY=${OPENAI_API_KEY}
- CUBEJS_API_URL=http://cubejs:4000/cubejs-api/v1
- CUBEJS_API_SECRET=mysecretkey1234567890abcdefghijkl
- OPENAI_MODEL=gpt-4o-mini
- LOG_LEVEL=INFO
```

---

## 9. Project Structure

```
praval_mds_analytics/
├── agents/                     # AI agents (FastAPI + Praval)
│   ├── app.py                  # FastAPI main application
│   ├── manufacturing_advisor.py # Domain expertise agent
│   ├── analytics_specialist.py  # Query translation agent
│   ├── visualization_specialist.py # Chart generation agent
│   ├── quality_inspector.py     # Anomaly detection agent
│   ├── report_writer.py         # Narrative composition agent
│   ├── reef_config.py           # Praval Reef configuration
│   ├── spore_schemas.py         # Spore message schemas
│   ├── cubejs_client.py         # Cube.js API client
│   ├── config.py                # Settings management
│   └── Dockerfile               # Agent container build
│
├── airflow/                    # Orchestration DAGs
│   └── dags/                   # Airflow DAG definitions
│
├── cubejs/                     # Semantic layer schemas
│   └── schema/                 # Cube.js cube definitions
│       ├── PressOperations.js
│       ├── PartFamilyPerformance.js
│       └── PressLineUtilization.js
│
├── dbt_transform/              # dbt models
│   ├── dbt_project.yml         # dbt project configuration
│   └── models/
│       ├── staging/            # Raw data cleaning
│       ├── intermediate/       # Business logic
│       └── marts/              # Analytics-ready tables
│
├── docker/                     # Database initialization scripts
│   └── postgres/
│       ├── press-line-a/init.sql
│       ├── press-line-b/init.sql
│       ├── die-management/init.sql
│       └── warehouse/init.sql
│
├── el_pipeline/                # Extract-Load pipeline
│   ├── extractor.py
│   ├── loader.py
│   └── pipeline.py
│
├── frontend/                   # Next.js UI
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── tests/                      # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                       # Documentation
│
├── docker-compose.yml          # Service orchestration
├── Makefile                    # Common commands
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # Project documentation
```

---

## 10. Troubleshooting Guide

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
# Find what's using the port (Linux/Mac)
lsof -i :8000

# Find what's using the port (Windows)
netstat -ano | findstr :8000

# Kill the process or change port in docker-compose.yml
```

---

## Quick Reference Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Run dbt
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform

# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/agents

# Run tests
make test
```

---

## Services Summary

| Service | Port | Container | Technology |
|---------|------|-----------|------------|
| Frontend | 3000 | analytics-frontend | Next.js |
| Agents API | 8000 | analytics-agents | FastAPI + Praval |
| Cube.js | 4000 | cubejs | Cube.js |
| Airflow | 8080 | airflow-webserver | Apache Airflow |
| Warehouse DB | 5435 | postgres-warehouse | PostgreSQL |
| Press Line A DB | 5436 | postgres-press-line-a | PostgreSQL |
| Press Line B DB | 5437 | postgres-press-line-b | PostgreSQL |
| Die Management DB | 5438 | postgres-die-management | PostgreSQL |

---

*Generated on: 2026-01-08*
