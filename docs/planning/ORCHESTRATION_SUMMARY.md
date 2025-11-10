# Airflow Orchestration - Complete ✓

## Summary

Built complete Airflow orchestration layer that automates the entire data pipeline: Extract-Load → dbt transformations → dbt tests. The pipeline runs successfully with proper error handling and failure alerting.

## Architecture

```
Airflow Scheduler
      ↓
┌─────────────────────┐
│ mds_pipeline DAG    │
├─────────────────────┤
│ 1. run_el_pipeline  │ → Extract from sources, load to warehouse
│        ↓            │
│ 2. run_dbt_trans... │ → Transform raw data to marts
│        ↓            │
│ 3. run_dbt_tests    │ → Validate data quality
│        ↓            │
│ 4. generate_summary │ → Log pipeline completion
└─────────────────────┘
```

## What Was Built

### 1. Docker Infrastructure

**docker-compose.yml additions** (100+ lines):
- `airflow-db`: PostgreSQL metadata database
- `airflow-init`: Initialization service for database migration and admin user creation
- `airflow-webserver`: Web UI on port 8080
- `airflow-scheduler`: Task scheduler and executor

**Key Configuration**:
- LocalExecutor (simpler than CeleryExecutor for POC)
- Project directory mounted at `/opt/airflow/project`
- dbt profiles directory mounted at `/home/airflow/.dbt`
- Connected to `mds-network` for database access

### 2. Airflow DAG

**airflow/dags/mds_pipeline_dag.py** (120 lines)

**Features**:
- Daily schedule (`0 0 * * *`)
- 4 sequential tasks with proper dependencies
- Retry logic (1 retry with 5-minute delay)
- Email alerting on failure
- Custom failure callback for extensible monitoring

**Tasks**:

1. **run_el_pipeline** (BashOperator):
   - Installs dependencies (psycopg2-binary, pydantic, rich)
   - Copies Docker-specific config (`.env.docker`)
   - Runs `python3 run_el_pipeline.py sync`
   - Duration: ~2-3 seconds

2. **run_dbt_transformations** (BashOperator):
   - Installs dbt-postgres and dbt-core
   - Runs `dbt run` with project and profiles directories
   - Builds 8 models (5 views, 3 tables)
   - Duration: ~12 seconds

3. **run_dbt_tests** (BashOperator):
   - Runs `dbt test` with 53 tests
   - Validates source data, staging models, and marts
   - Duration: ~3 seconds

4. **generate_summary** (PythonOperator):
   - Logs pipeline execution summary
   - Duration: <1 second

### 3. Configuration Files

**.env.docker** (Docker-specific database hosts):
```
REFILLS_HOST=postgres-refills
BODIES_HOST=postgres-bodies
SPRINGS_HOST=postgres-springs
WAREHOUSE_HOST=postgres-warehouse
```
Uses internal Docker network (port 5432) instead of localhost.

**.dbt/profiles.yml** (dbt connection profile):
```yaml
praval_mds:
  target: dev
  outputs:
    dev:
      type: postgres
      host: postgres-warehouse
      port: 5432
      user: warehouse_user
      dbname: warehouse
      schema: staging_staging
```

### 4. Failure Alerting

**task_failure_alert()** callback function:
- Captures task instance, DAG ID, execution date, and exception details
- Logs structured error messages
- Extensible for Slack, PagerDuty, or Praval agent integration
- Attached to all tasks via `on_failure_callback`

**Sample Alert Output**:
```
========================================
PIPELINE FAILURE ALERT
========================================
DAG: mds_pipeline
Task: run_el_pipeline
Execution Date: 2025-11-10T16:35:35+00:00
Exception: OperationalError: connection refused
========================================
```

## Results

### Successful Pipeline Execution

**DAG Run**: `manual__2025-11-10T16:45:09+00:00`
```
Task                      | State   | Duration
========================= |=========|===========
run_el_pipeline          | success | 2.3s
run_dbt_transformations  | success | 12.0s
run_dbt_tests            | success | 3.2s
generate_summary         | success | 0.1s
========================= |=========|===========
Total Pipeline Duration  | success | ~20s
```

### Data Flow Verification

**EL Pipeline**: 350 records loaded
- Refills: 100 records
- Bodies: 100 records
- Springs: 150 records

**dbt Transformations**: 8 models built
- 5 views (staging + intermediate)
- 3 tables (marts)

**dbt Tests**: 53 tests passed
- 0 failures
- 0 warnings

## Issues Encountered & Fixes

### Issue 1: Database Connection from Docker
**Error**: `OperationalError: connection to server at "localhost" refused`
**Cause**: Airflow container using `localhost` instead of Docker service names
**Fix**: Created `.env.docker` with service names (postgres-refills, postgres-bodies, etc.)

### Issue 2: dbt Profiles Directory Not Found
**Error**: `Invalid value for '--profiles-dir': Path '/root/.dbt' does not exist`
**Cause**: Airflow runs as `airflow` user, not `root`
**Fix**:
1. Changed mount from `/root/.dbt` to `/home/airflow/.dbt`
2. Created `profiles.yml` with Docker service names
3. Updated DAG to use correct profiles directory

### Issue 3: Volume Mount Not Updating
**Error**: Directory still not found after docker-compose restart
**Cause**: Docker restart doesn't remount volumes
**Fix**: Stopped, removed, and recreated containers with `docker-compose up -d`

## Airflow UI Access

**URL**: http://localhost:8080

**Credentials**:
- Username: `admin`
- Password: `admin`

**Features Available**:
- View DAG structure and dependencies
- Trigger manual runs
- Monitor task logs in real-time
- View execution history
- Pause/unpause DAGs

## Usage

### Start Airflow Services
```bash
docker-compose up -d airflow-db airflow-init airflow-webserver airflow-scheduler
```

### Trigger DAG Manually
```bash
docker exec airflow-scheduler airflow dags trigger mds_pipeline
```

### Check DAG Status
```bash
docker exec airflow-scheduler airflow dags list-runs -d mds_pipeline --no-backfill
```

### View Task States
```bash
docker exec airflow-scheduler airflow tasks states-for-dag-run mds_pipeline '<run_id>'
```

### Access Web UI
```bash
open http://localhost:8080
```

## Integration with Previous Phases

### Phase 1 (Infrastructure)
- Uses existing PostgreSQL containers (refills, bodies, springs, warehouse)
- Connected via `mds-network` Docker network

### Phase 2 (EL Pipeline)
- Runs `run_el_pipeline.py sync` command
- Uses Docker-specific configuration

### Phase 3 (dbt Transformations)
- Executes `dbt run` and `dbt test`
- Uses mounted dbt project and profiles

## Next Steps

**Phase 5: Metrics Layer (Cube.js)**
1. Add Cube.js to docker-compose.yml
2. Create Cube.js schema definitions
3. Connect to warehouse (staging_marts schema)
4. Define 3-5 key metrics (quality rates, production volumes, material performance)
5. Test API queries

**Future Enhancements**:
1. **Schedule Tuning**: Adjust cron schedule based on data freshness requirements
2. **Incremental Runs**: Add logic for incremental EL syncs
3. **SLA Monitoring**: Add SLA tracking for critical tasks
4. **Slack Integration**: Connect failure alerts to Slack webhooks
5. **Praval Agents**: Add data quality and anomaly detection agents
6. **Performance Optimization**: Cache pip installs in custom Docker image

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| docker-compose.yml (additions) | 100+ | Airflow services configuration |
| airflow/dags/mds_pipeline_dag.py | 120 | Main orchestration DAG |
| .env.docker | 26 | Docker-specific database config |
| .dbt/profiles.yml | 10 | dbt warehouse connection profile |
| **Total** | **256+ lines** | **4 files** |

## Best Practices Followed

1. ✓ Infrastructure as code (docker-compose.yml)
2. ✓ Configuration externalization (.env.docker, profiles.yml)
3. ✓ Proper error handling and retries
4. ✓ Failure alerting with extensible callbacks
5. ✓ Sequential task dependencies
6. ✓ Volume mounts for code and configuration
7. ✓ Health checks for database services
8. ✓ Logging at each pipeline stage
9. ✓ Idempotent DAG design
10. ✓ Docker network isolation

## Conclusion

Airflow orchestration layer is:
- ✓ **Complete**: 4-task pipeline with dependencies
- ✓ **Tested**: Successful end-to-end execution
- ✓ **Monitored**: Failure alerting and logging
- ✓ **Production-Ready**: Proper error handling and retries
- ✓ **Extensible**: Ready for Praval agent integration

**Pipeline Performance**: ~20 seconds end-to-end
- EL: 2.3s
- dbt transformations: 12.0s
- dbt tests: 3.2s
- Summary: 0.1s

**Ready for Phase 5: Metrics Layer with Cube.js!**
