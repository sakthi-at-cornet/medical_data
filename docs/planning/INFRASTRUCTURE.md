# Infrastructure Layer - Status

## Overview
Manufacturing data stack infrastructure with 4 PostgreSQL databases for pen manufacturing analytics.

## Running Containers

All containers are up and healthy:

- **postgres-refills**: Ink refills manufacturing data (Port 5432)
- **postgres-bodies**: Pen bodies manufacturing data (Port 5433)
- **postgres-springs**: Springs manufacturing data (Port 5434)
- **postgres-warehouse**: Data warehouse with dimensional model (Port 5435)

## Connection Details

### Refills Database
```bash
Host: localhost
Port: 5432
Database: refills
User: refills_user
Password: refills_pass
```

### Bodies Database
```bash
Host: localhost
Port: 5433
Database: bodies
User: bodies_user
Password: bodies_pass
```

### Springs Database
```bash
Host: localhost
Port: 5434
Database: springs
User: springs_user
Password: springs_pass
```

### Warehouse
```bash
Host: localhost
Port: 5435
Database: warehouse
User: warehouse_user
Password: warehouse_pass
```

## Data Summary

### Refills Production
- **Total Records**: 100
- **Passed**: 95 (95%)
- **Failed**: 5 (5%)
- **Lines**: 2 production lines
- **Metrics**: ink_viscosity, write_distance, tip_diameter, ink_color, flow_consistency

**Sample Query:**
```sql
SELECT * FROM refills_summary;
```

### Bodies Production
- **Total Records**: 100
- **Passed**: 91 (91%)
- **Failed**: 9 (9%)
- **Lines**: 2 production lines
- **Materials**: plastic (40), metal (31), bamboo (29)
- **Metrics**: durability_score, color_match_rating, length, wall_thickness, material

### Springs Production
- **Total Records**: 150
- **Passed**: 143 (95.3%)
- **Failed**: 7 (4.7%)
- **Lines**: 3 production lines
- **Materials**: stainless_steel (52), chrome_vanadium (57), music_wire (41)
- **Metrics**: diameter, tensile_strength, material, compression_ratio

**Sample Query:**
```sql
SELECT * FROM springs_material_stats;
```

### Warehouse
- **Schemas**: raw, staging, marts
- **Dimension Tables**:
  - `dim_date`: 731 days (2024-2025)
  - `dim_production_line`: 7 lines
  - `dim_material`: 11 materials
  - `dim_batch`: Ready for batch tracking
- **Fact Tables**:
  - `fact_production_quality`: Ready for dbt transformations

## Docker Commands

### Start all containers
```bash
docker-compose up -d
```

### Stop all containers
```bash
docker-compose down
```

### View logs
```bash
docker logs postgres-refills
docker logs postgres-bodies
docker logs postgres-springs
docker logs postgres-warehouse
```

### Connect to database
```bash
# Refills
docker exec -it postgres-refills psql -U refills_user -d refills

# Bodies
docker exec -it postgres-bodies psql -U bodies_user -d bodies

# Springs
docker exec -it postgres-springs psql -U springs_user -d springs

# Warehouse
docker exec -it postgres-warehouse psql -U warehouse_user -d warehouse
```

## Sample Queries

### Refills - Quality trends by color
```sql
SELECT ink_color,
       COUNT(*) as total,
       COUNT(*) FILTER (WHERE quality_status = 'ok') as passed
FROM refills_production
GROUP BY ink_color
ORDER BY total DESC;
```

### Bodies - Material performance
```sql
SELECT material,
       ROUND(AVG(durability_score)::numeric, 1) as avg_durability,
       COUNT(*) FILTER (WHERE quality_status = 'error') as failures
FROM bodies_production
GROUP BY material;
```

### Springs - Line performance
```sql
SELECT line_id,
       COUNT(*) as total,
       ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_strength
FROM springs_production
GROUP BY line_id
ORDER BY line_id;
```

### Warehouse - Production lines
```sql
SELECT line_id, line_type, capacity_per_hour, status
FROM marts.dim_production_line
ORDER BY line_type, line_id;
```

## Next Steps

1. **EL Pipeline**: Configure Airbyte to sync source DBs → warehouse
2. **dbt Transformations**: Build staging and mart models
3. **Orchestration**: Set up Airflow DAGs
4. **Metrics Layer**: Define Cube.js schemas
5. **Praval Agents**: Add intelligence layer for data quality, anomaly detection

## Health Check

```bash
# Check all containers are healthy
docker-compose ps

# Expected output: All containers show "healthy" status
```

## Troubleshooting

### If containers fail to start
```bash
# Remove volumes and restart fresh
docker-compose down -v
docker-compose up -d
```

### If data is missing
The init scripts populate data on first startup. If needed, manually insert:
```bash
# See docker/postgres/{refills,bodies,springs}/init.sql for insert statements
```
