# EL Pipeline

Python-based Extract-Load pipeline for manufacturing data.

## Overview

This pipeline extracts production data from three source databases (refills, bodies, springs) and loads it into the warehouse's raw schema.

## Architecture

```
Source DBs          EL Pipeline          Warehouse
┌─────────┐        ┌──────────┐        ┌─────────┐
│ Refills │───────▶│          │        │   Raw   │
└─────────┘        │          │───────▶│ Schema  │
┌─────────┐        │ Extract  │        └─────────┘
│ Bodies  │───────▶│   +      │
└─────────┘        │  Load    │
┌─────────┐        │          │
│ Springs │───────▶│          │
└─────────┘        └──────────┘
```

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The pipeline uses `.env.el` for configuration:

```bash
# Source databases
REFILLS_HOST=localhost
REFILLS_PORT=5432
...

# Warehouse
WAREHOUSE_HOST=localhost
WAREHOUSE_PORT=5435
...
```

## Usage

### Run Full Sync

```bash
python run_el_pipeline.py sync
```

This will:
1. Extract all data from source databases
2. Truncate warehouse raw tables
3. Load data into warehouse
4. Display sync statistics

### Check Warehouse

```bash
python run_el_pipeline.py check
```

Shows current record counts in warehouse.

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# With coverage
pytest --cov=el_pipeline --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
└── el_pipeline/
    ├── test_config.py            # Configuration tests
    ├── test_database.py          # Database connection tests
    ├── test_extractor.py         # Data extraction tests
    └── test_pipeline.py          # End-to-end pipeline tests
```

## Module Structure

```
el_pipeline/
├── __init__.py
├── config.py         # Configuration management
├── database.py       # Database connection utilities
├── extractor.py      # Data extraction logic
├── loader.py         # Data loading logic
├── pipeline.py       # Pipeline orchestration
└── cli.py           # Command-line interface
```

## Key Features

### Modular Design
- Separate extractors for each source
- Reusable database connection manager
- Configurable batch sizes

### Incremental Support
- Full sync: Complete data refresh
- Incremental sync: Only new/modified records (future)

### Error Handling
- Transaction rollback on errors
- Detailed logging
- Connection cleanup

### Testing
- Unit tests for each module
- Integration tests with real databases
- High test coverage

## Development

### Adding a New Source

1. Create extractor in `extractor.py`:
```python
class NewSourceExtractor(DataExtractor):
    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "new_source")
```

2. Add loader method in `loader.py`:
```python
def load_new_source(self, data: List[Dict[str, Any]], truncate: bool = False):
    # Implementation
```

3. Update pipeline in `pipeline.py`:
```python
def run_full_sync(self):
    new_source_data = self.new_source_extractor.extract()
    self.loader.load_new_source(new_source_data)
```

4. Add tests

### Running in Production

For production use:
1. Set up proper credentials in `.env.el`
2. Use logging configuration for monitoring
3. Set up scheduling (cron, Airflow, etc.)
4. Monitor warehouse growth
5. Set up alerts for failures

## Next Steps

1. **dbt Integration**: Transform raw data into dimensional models
2. **Airflow DAGs**: Schedule EL pipeline runs
3. **Praval Agents**: Add AI-driven data quality checks
4. **Incremental Sync**: Implement timestamp-based incremental loads
5. **Change Data Capture**: Real-time data sync

## Troubleshooting

### Connection Errors

```bash
# Test database connectivity
python -c "from el_pipeline.config import PipelineConfig; config = PipelineConfig.from_env(); print('Config loaded successfully')"
```

### Data Mismatch

```bash
# Check source counts
docker exec postgres-refills psql -U refills_user -d refills -c "SELECT COUNT(*) FROM refills_production;"

# Check warehouse counts
python run_el_pipeline.py check
```

### Permission Errors

Ensure warehouse user has INSERT permissions:
```sql
GRANT INSERT, SELECT, DELETE ON ALL TABLES IN SCHEMA raw TO warehouse_user;
```
