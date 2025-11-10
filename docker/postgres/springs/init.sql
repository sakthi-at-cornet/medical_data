-- Springs Manufacturing Database - Enhanced with 90 days historical data
-- Springs production line data

CREATE TABLE IF NOT EXISTS springs_production (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    line_id VARCHAR(50) NOT NULL,
    machine_id VARCHAR(50) NOT NULL,
    batch_id VARCHAR(100) NOT NULL,
    shift_id VARCHAR(20) NOT NULL,
    operator_id VARCHAR(20) NOT NULL,

    -- Original metrics
    diameter_mm DECIMAL(4,2) NOT NULL,
    tensile_strength_mpa DECIMAL(6,1) NOT NULL,
    material VARCHAR(50) NOT NULL,
    compression_ratio DECIMAL(5,3) NOT NULL,
    quality_status VARCHAR(20) NOT NULL,

    -- New metrics
    cycle_time_seconds DECIMAL(6,2) NOT NULL,
    first_pass_yield BOOLEAN NOT NULL DEFAULT TRUE,
    defect_type VARCHAR(50),
    rework_required BOOLEAN NOT NULL DEFAULT FALSE,
    material_cost_per_unit DECIMAL(8,4) NOT NULL,
    labor_cost_per_unit DECIMAL(8,4) NOT NULL,
    energy_cost_per_unit DECIMAL(8,4) NOT NULL,

    -- Environmental factors
    temperature_celsius DECIMAL(4,1) NOT NULL,
    humidity_percent DECIMAL(4,1) NOT NULL,

    -- Performance metrics
    oee DECIMAL(5,3) NOT NULL,
    availability DECIMAL(5,3) NOT NULL,
    performance DECIMAL(5,3) NOT NULL,
    quality_rate DECIMAL(5,3) NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_springs_timestamp ON springs_production(timestamp);
CREATE INDEX idx_springs_batch_id ON springs_production(batch_id);
CREATE INDEX idx_springs_line_id ON springs_production(line_id);
CREATE INDEX idx_springs_machine_id ON springs_production(machine_id);
CREATE INDEX idx_springs_shift_id ON springs_production(shift_id);
CREATE INDEX idx_springs_quality ON springs_production(quality_status);
CREATE INDEX idx_springs_material ON springs_production(material);
CREATE INDEX idx_springs_defect_type ON springs_production(defect_type);

-- Generate 90 days of hourly data (2160 records per component)
-- Realistic patterns: shifts, seasonality, anomalies, weekends
INSERT INTO springs_production (
    timestamp, line_id, machine_id, batch_id, shift_id, operator_id,
    diameter_mm, tensile_strength_mpa, material, compression_ratio,
    quality_status,
    cycle_time_seconds, first_pass_yield, defect_type, rework_required,
    material_cost_per_unit, labor_cost_per_unit, energy_cost_per_unit,
    temperature_celsius, humidity_percent,
    oee, availability, performance, quality_rate
)
SELECT
    -- Timestamp: 90 days ago, hourly
    (CURRENT_DATE - INTERVAL '90 days') + (hour_num * INTERVAL '1 hour') as timestamp,

    -- Line: 3 lines for springs (higher capacity)
    (ARRAY['LINE-SPRINGS-001', 'LINE-SPRINGS-002', 'LINE-SPRINGS-003'])[floor(random() * 3 + 1)] as line_id,

    -- Machine: 5 machines per line (M1-M5)
    'MACHINE-S-' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as machine_id,

    -- Batch: Changes every 6 hours (faster production)
    'BATCH-S-' || LPAD((floor(hour_num / 6)::int)::text, 5, '0') as batch_id,

    -- Shift: Morning (6-14), Afternoon (14-22), Night (22-6)
    CASE
        WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 6 AND 13 THEN 'SHIFT-MORNING'
        WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 14 AND 21 THEN 'SHIFT-AFTERNOON'
        ELSE 'SHIFT-NIGHT'
    END as shift_id,

    -- Operator: 30 operators rotating
    'OP-' || LPAD((floor(random() * 30 + 1)::int)::text, 3, '0') as operator_id,

    -- Original metrics with realistic variance
    -- Diameter: errors 2% of time
    CASE
        WHEN random() < (0.02 + CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.01 ELSE 0 END)
            THEN ROUND((0.60 + random() * 0.20)::numeric, 2)
        ELSE ROUND((0.95 + random() * 0.15)::numeric, 2)
    END as diameter_mm,

    -- Tensile strength: varies by material
    CASE
        WHEN random() < (0.02 + CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.01 ELSE 0 END)
            THEN ROUND((800 + random() * 100)::numeric, 1)
        ELSE ROUND((980 + random() * 50)::numeric, 1)
    END as tensile_strength_mpa,

    -- Material: chrome_vanadium 45%, stainless_steel 35%, music_wire 20%
    (ARRAY['chrome_vanadium', 'chrome_vanadium', 'stainless_steel', 'stainless_steel', 'music_wire'])[floor(random() * 5 + 1)] as material,

    ROUND((0.90 + random() * 0.10)::numeric, 3) as compression_ratio,

    -- Quality status: errors more likely on weekends and night shift
    CASE
        WHEN random() < (0.02 +
                        CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.01 ELSE 0 END +
                        CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 0.01 ELSE 0 END)
            THEN 'error'
        ELSE 'ok'
    END as quality_status,

    -- NEW METRICS

    -- Cycle time: 30-50 seconds (springs are faster to produce)
    ROUND((30 + random() * 20 +
           CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 8 ELSE 0 END)::numeric, 2) as cycle_time_seconds,

    -- First pass yield: 95-97%
    random() > 0.04 as first_pass_yield,

    -- Defect type: only if quality_status is error
    CASE
        WHEN random() < 0.04 THEN
            (ARRAY['dimension_out_of_spec', 'tensile_failure', 'compression_failure', 'material_defect', 'coil_spacing'])[floor(random() * 5 + 1)]
        ELSE NULL
    END as defect_type,

    -- Rework: 3% require rework
    random() < 0.03 as rework_required,

    -- Costs: chrome_vanadium most expensive, stainless moderate, music_wire cheapest
    ROUND((0.05 + random() * 0.03)::numeric, 4) as material_cost_per_unit,
    ROUND((0.12 +
           CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 0.02 ELSE 0 END)::numeric, 4) as labor_cost_per_unit,
    ROUND((0.015 + random() * 0.01)::numeric, 4) as energy_cost_per_unit,

    -- Environmental: temperature varies by time of day
    ROUND((18 + 8 * sin((EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) + random() * 2) * 3.14159 / 12) +
           3 * sin((hour_num / 24.0) * 2 * 3.14159 / 365))::numeric, 1) as temperature_celsius,
    ROUND((40 + 20 * sin((hour_num / 24.0) * 2 * 3.14159 / 365) + random() * 10)::numeric, 1) as humidity_percent,

    -- OEE and components: Overall Equipment Effectiveness
    -- Springs have better OEE than other components (more mature process)
    ROUND((0.75 + random() * 0.22 -
           CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.03 ELSE 0 END)::numeric, 3) as oee,
    ROUND((0.88 + random() * 0.10)::numeric, 3) as availability,
    ROUND((0.85 + random() * 0.13)::numeric, 3) as performance,
    ROUND((0.95 + random() * 0.04)::numeric, 3) as quality_rate

FROM generate_series(0, 2159) as hour_num;

-- Add some realistic anomalies and patterns
-- Chrome vanadium material performs slightly better
UPDATE springs_production
SET
    tensile_strength_mpa = tensile_strength_mpa * 1.05,
    quality_rate = LEAST(quality_rate * 1.03, 0.99)
WHERE material = 'chrome_vanadium';

-- Machine S02 had calibration issues on day 55
UPDATE springs_production
SET
    quality_status = 'error',
    defect_type = 'dimension_out_of_spec',
    oee = oee * 0.70,
    availability = availability * 0.80
WHERE
    machine_id = 'MACHINE-S-02'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '55 days') AND (CURRENT_DATE - INTERVAL '54 days');

-- Line 3 had excellent performance week 7
UPDATE springs_production
SET
    oee = LEAST(oee * 1.10, 0.99),
    quality_rate = LEAST(quality_rate * 1.04, 0.99),
    quality_status = 'ok'
WHERE
    line_id = 'LINE-SPRINGS-003'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '41 days') AND (CURRENT_DATE - INTERVAL '34 days');

-- Holiday reduced production (day 60-62)
UPDATE springs_production
SET
    oee = oee * 0.60,
    availability = availability * 0.70,
    performance = performance * 0.85
WHERE
    timestamp BETWEEN (CURRENT_DATE - INTERVAL '62 days') AND (CURRENT_DATE - INTERVAL '59 days');

-- Summary statistics view
CREATE OR REPLACE VIEW springs_summary AS
SELECT
    line_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    COUNT(*) FILTER (WHERE quality_status = 'error') as failed_units,
    ROUND(AVG(diameter_mm)::numeric, 2) as avg_diameter,
    ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_tensile_strength,
    ROUND(AVG(compression_ratio)::numeric, 3) as avg_compression_ratio,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_total_cost
FROM springs_production
GROUP BY line_id;

-- Material performance view
CREATE OR REPLACE VIEW springs_material_performance AS
SELECT
    material,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_tensile_strength,
    ROUND(AVG(compression_ratio)::numeric, 3) as avg_compression_ratio,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit)::numeric, 4) as avg_material_cost,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_total_cost,
    -- Cost per passed unit (economic efficiency)
    ROUND((AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit) /
           (COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*)))::numeric, 4) as cost_per_passed_unit
FROM springs_production
GROUP BY material
ORDER BY avg_tensile_strength DESC;

-- Hourly trends view
CREATE OR REPLACE VIEW springs_hourly_trends AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    line_id,
    COUNT(*) as units_produced,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_tensile_strength
FROM springs_production
GROUP BY DATE_TRUNC('hour', timestamp), line_id
ORDER BY hour DESC;

-- Shift performance view
CREATE OR REPLACE VIEW springs_shift_performance AS
SELECT
    shift_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_tensile_strength,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_cost_per_unit
FROM springs_production
GROUP BY shift_id
ORDER BY pass_rate DESC;

-- Machine performance view
CREATE OR REPLACE VIEW springs_machine_performance AS
SELECT
    machine_id,
    line_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(availability)::numeric, 3) as avg_availability,
    ROUND(AVG(performance)::numeric, 3) as avg_performance,
    ROUND(AVG(quality_rate)::numeric, 3) as avg_quality_rate,
    ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_tensile_strength,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time
FROM springs_production
GROUP BY machine_id, line_id
ORDER BY avg_oee DESC;

-- Defect analysis view
CREATE OR REPLACE VIEW springs_defect_analysis AS
SELECT
    defect_type,
    COUNT(*) as defect_count,
    ROUND((COUNT(*)::numeric / (SELECT COUNT(*) FROM springs_production WHERE defect_type IS NOT NULL) * 100), 2) as pct_of_defects,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time_when_defect,
    ROUND(AVG(tensile_strength_mpa)::numeric, 1) as avg_tensile_strength_when_defect
FROM springs_production
WHERE defect_type IS NOT NULL
GROUP BY defect_type
ORDER BY defect_count DESC;

COMMENT ON TABLE springs_production IS 'Springs manufacturing line production data - 90 days historical with rich dimensions';
COMMENT ON VIEW springs_summary IS 'Summary statistics for springs production by line';
COMMENT ON VIEW springs_material_performance IS 'Material comparison with tensile strength analysis';
COMMENT ON VIEW springs_hourly_trends IS 'Hourly production trends with quality metrics';
COMMENT ON VIEW springs_shift_performance IS 'Performance comparison across shifts';
COMMENT ON VIEW springs_machine_performance IS 'Machine-level performance and OEE metrics';
COMMENT ON VIEW springs_defect_analysis IS 'Defect type distribution and impact analysis';
