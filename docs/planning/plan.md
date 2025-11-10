# Modern Data Stack with Praval

## Goal
Build: Source DBs → Airbyte → PostgreSQL → dbt → Cube.js → UI → Reverse ETL
Add: Praval agents for intelligence layer

**Context**: Manufacturing analytics for ballpoint pen production (refills, bodies, springs)

## Tasks

### 1. Infrastructure ✓
- [x] Docker compose: PostgreSQL (3 source DBs + 1 warehouse)
- [x] Airbyte setup via Docker
- [x] Generate sample data (refills, bodies, springs schemas)

### 2. EL Pipeline ✓
- [x] Built Python-based EL pipeline (simpler than Airbyte for POC)
- [x] Created database connectors for all sources + warehouse
- [x] Implemented extract logic (full & incremental support)
- [x] Implemented load logic to warehouse raw schema
- [x] Added comprehensive tests (config, database, extractor, pipeline)
- [x] Created CLI with sync and check commands
- [x] Verified data lands correctly (350 records total)

### 3. Transformations ✓
- [x] Initialized dbt project with proper structure
- [x] Created staging models for refills, bodies, springs (views)
- [x] Created intermediate models for unified quality metrics
- [x] Created dimensional mart models (tables):
  - fact_production_quality (7 records)
  - agg_material_performance (3 materials)
  - agg_component_quality_trends (31 hourly trends)
- [x] Added 53 dbt tests (all passing)
- [x] Documented sources and models with schema.yml

### 4. Orchestration ✓
- [x] Airflow Docker setup
- [x] DAG: trigger EL pipeline → run dbt → tests
- [x] Basic failure alerting
- [x] End-to-end pipeline tested successfully (20s execution)

### 5. Metrics Layer ✓
- [x] Cube.js Docker setup
- [x] Define schema (3 cubes with 15+ metrics)
- [x] Test API queries successfully

### 6. Agentic UI ✓
- [x] FastAPI backend with 2 Praval agents (Chat + Data Analyst)
- [x] Data Analyst Agent: NL → Cube.js query translation
- [x] Chat Agent: Context management, conversation flow
- [x] Next.js frontend with TypeScript
- [x] Chat interface with message history
- [x] Chart.js visualizations (bar, line, table)
- [x] Backend unit and integration tests
- [x] End-to-end tested with demo queries
- [x] Docker containers for agents and frontend

### 7. Reverse ETL
- [ ] Python service to read warehouse
- [ ] Write enriched data back to source DB

### 8. Testing & Validation
- [x] End-to-end data flow test (Phase 6)
- [x] Agent unit tests
- [ ] Benchmark: with vs without agents (optional)

## Questions
1. Full stack or minimal POC? - Answer: Full Stack
2. Which 2 praval agents to prioritize? - Answer: We need to explore. Start with a data analyst, and a chat agent. Frontend should show a chat interface and the agent should be able to run queries on the dwh
3. Real data or mock data? - Mock data, we have already buit shit earlier, see the source DBs
