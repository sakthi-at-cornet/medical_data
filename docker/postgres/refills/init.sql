-- Refills Manufacturing Database - Enhanced with 90 days historical data
-- Ink refills production line data

CREATE TABLE IF NOT EXISTS refills_production (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    line_id VARCHAR(50) NOT NULL,
    machine_id VARCHAR(50) NOT NULL,
    batch_id VARCHAR(100) NOT NULL,
    shift_id VARCHAR(20) NOT NULL,
    operator_id VARCHAR(20) NOT NULL,

    -- Original metrics
    ink_viscosity_pas DECIMAL(5,2) NOT NULL,
    write_distance_km DECIMAL(5,2) NOT NULL,
    tip_diameter_mm DECIMAL(4,2) NOT NULL,
    ink_color VARCHAR(20) NOT NULL,
    flow_consistency DECIMAL(5,3) NOT NULL,
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
CREATE INDEX idx_refills_timestamp ON refills_production(timestamp);
CREATE INDEX idx_refills_batch_id ON refills_production(batch_id);
CREATE INDEX idx_refills_line_id ON refills_production(line_id);
CREATE INDEX idx_refills_machine_id ON refills_production(machine_id);
CREATE INDEX idx_refills_shift_id ON refills_production(shift_id);
CREATE INDEX idx_refills_quality ON refills_production(quality_status);
CREATE INDEX idx_refills_defect_type ON refills_production(defect_type);

-- Generate 90 days of hourly data (2160 records per component)
-- Realistic patterns: shifts, seasonality, anomalies, weekends
INSERT INTO refills_production (
    timestamp, line_id, machine_id, batch_id, shift_id, operator_id,
    ink_viscosity_pas, write_distance_km, tip_diameter_mm, ink_color,
    flow_consistency, quality_status,
    cycle_time_seconds, first_pass_yield, defect_type, rework_required,
    material_cost_per_unit, labor_cost_per_unit, energy_cost_per_unit,
    temperature_celsius, humidity_percent,
    oee, availability, performance, quality_rate
)
SELECT
    -- Timestamp: 90 days ago, hourly
    (CURRENT_DATE - INTERVAL '90 days') + (hour_num * INTERVAL '1 hour') as timestamp,

    -- Line: 2 lines
    CASE WHEN random() < 0.5 THEN 'LINE-REFILLS-001' ELSE 'LINE-REFILLS-002' END as line_id,

    -- Machine: 5 machines per line (M1-M5)
    'MACHINE-R-' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as machine_id,

    -- Batch: Changes every 8 hours
    'BATCH-R-' || LPAD((floor(hour_num / 8)::int)::text, 5, '0') as batch_id,

    -- Shift: Morning (6-14), Afternoon (14-22), Night (22-6)
    CASE
        WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 6 AND 13 THEN 'SHIFT-MORNING'
        WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 14 AND 21 THEN 'SHIFT-AFTERNOON'
        ELSE 'SHIFT-NIGHT'
    END as shift_id,

    -- Operator: 30 operators rotating
    'OP-' || LPAD((floor(random() * 30 + 1)::int)::text, 3, '0') as operator_id,

    -- Original metrics with realistic variance
    ROUND((1.10 + random() * 0.3 +
           CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.05 ELSE 0 END)::numeric, 2) as ink_viscosity_pas,

    -- Write distance: errors 3% of time, weekend degradation
    CASE
        WHEN random() < (0.03 + CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.02 ELSE 0 END)
            THEN ROUND((0.5 + random() * 1.5)::numeric, 2)
        ELSE ROUND((3.2 + random() * 0.6)::numeric, 2)
    END as write_distance_km,

    ROUND((0.65 + random() * 0.15)::numeric, 2) as tip_diameter_mm,

    (ARRAY['black', 'blue', 'red', 'green', 'purple'])[floor(random() * 5 + 1)] as ink_color,

    ROUND((0.90 + random() * 0.10)::numeric, 3) as flow_consistency,

    -- Quality status: errors more likely on weekends and night shift
    CASE
        WHEN random() < (0.03 +
                        CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.02 ELSE 0 END +
                        CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 0.01 ELSE 0 END)
            THEN 'error'
        ELSE 'ok'
    END as quality_status,

    -- NEW METRICS

    -- Cycle time: 45-75 seconds, slower on night shift
    ROUND((45 + random() * 30 +
           CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 10 ELSE 0 END)::numeric, 2) as cycle_time_seconds,

    -- First pass yield: 92-95%
    random() > 0.07 as first_pass_yield,

    -- Defect type: only if quality_status is error
    CASE
        WHEN random() < 0.05 THEN
            (ARRAY['ink_leak', 'viscosity_out_of_spec', 'tip_defect', 'flow_inconsistent', 'dimensional_error'])[floor(random() * 5 + 1)]
        ELSE NULL
    END as defect_type,

    -- Rework: 5% require rework
    random() < 0.05 as rework_required,

    -- Costs: material varies by color, labor by shift, energy by time
    ROUND((0.08 + random() * 0.04)::numeric, 4) as material_cost_per_unit,
    ROUND((0.15 +
           CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 0.03 ELSE 0 END)::numeric, 4) as labor_cost_per_unit,
    ROUND((0.02 + random() * 0.01)::numeric, 4) as energy_cost_per_unit,

    -- Environmental: temperature varies by time of day, humidity by season
    ROUND((18 + 8 * sin((EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) + random() * 2) * 3.14159 / 12) +
           3 * sin((hour_num / 24.0) * 2 * 3.14159 / 365))::numeric, 1) as temperature_celsius,
    ROUND((40 + 20 * sin((hour_num / 24.0) * 2 * 3.14159 / 365) + random() * 10)::numeric, 1) as humidity_percent,

    -- OEE and components: Overall Equipment Effectiveness
    -- OEE = Availability × Performance × Quality
    ROUND((0.70 + random() * 0.25 -
           CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.05 ELSE 0 END)::numeric, 3) as oee,
    ROUND((0.85 + random() * 0.12)::numeric, 3) as availability,
    ROUND((0.80 + random() * 0.15)::numeric, 3) as performance,
    ROUND((0.92 + random() * 0.07)::numeric, 3) as quality_rate

FROM generate_series(0, 2159) as hour_num;

-- Add some realistic anomalies
-- Machine M03 had issues on day 45
UPDATE refills_production
SET
    quality_status = 'error',
    defect_type = 'machine_calibration',
    oee = oee * 0.6,
    availability = availability * 0.7
WHERE
    machine_id = 'MACHINE-R-03'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '45 days') AND (CURRENT_DATE - INTERVAL '44 days');

-- Line 2 had excellent performance week 8
UPDATE refills_production
SET
    oee = LEAST(oee * 1.15, 0.99),
    quality_rate = LEAST(quality_rate * 1.08, 0.99),
    quality_status = 'ok'
WHERE
    line_id = 'LINE-REFILLS-002'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '34 days') AND (CURRENT_DATE - INTERVAL '27 days');

-- Holiday reduced production (day 60-62)
UPDATE refills_production
SET
    oee = oee * 0.5,
    availability = availability * 0.6,
    performance = performance * 0.8
WHERE
    timestamp BETWEEN (CURRENT_DATE - INTERVAL '62 days') AND (CURRENT_DATE - INTERVAL '59 days');

-- Summary statistics view
CREATE OR REPLACE VIEW refills_summary AS
SELECT
    line_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    COUNT(*) FILTER (WHERE quality_status = 'error') as failed_units,
    ROUND(AVG(ink_viscosity_pas)::numeric, 2) as avg_viscosity,
    ROUND(AVG(write_distance_km)::numeric, 2) as avg_write_distance,
    ROUND(AVG(tip_diameter_mm)::numeric, 2) as avg_tip_diameter,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_total_cost
FROM refills_production
GROUP BY line_id;

-- Hourly trends view
CREATE OR REPLACE VIEW refills_hourly_trends AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    line_id,
    COUNT(*) as units_produced,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time
FROM refills_production
GROUP BY DATE_TRUNC('hour', timestamp), line_id
ORDER BY hour DESC;

-- Shift performance view
CREATE OR REPLACE VIEW refills_shift_performance AS
SELECT
    shift_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_cost_per_unit
FROM refills_production
GROUP BY shift_id
ORDER BY pass_rate DESC;

-- Machine performance view
CREATE OR REPLACE VIEW refills_machine_performance AS
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
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time
FROM refills_production
GROUP BY machine_id, line_id
ORDER BY avg_oee DESC;

-- Defect analysis view
CREATE OR REPLACE VIEW refills_defect_analysis AS
SELECT
    defect_type,
    COUNT(*) as defect_count,
    ROUND((COUNT(*)::numeric / (SELECT COUNT(*) FROM refills_production WHERE defect_type IS NOT NULL) * 100), 2) as pct_of_defects,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time_when_defect
FROM refills_production
WHERE defect_type IS NOT NULL
GROUP BY defect_type
ORDER BY defect_count DESC;

COMMENT ON TABLE refills_production IS 'Ink refills manufacturing line production data - 90 days historical with rich dimensions';
COMMENT ON VIEW refills_summary IS 'Summary statistics for refills production by line';
COMMENT ON VIEW refills_hourly_trends IS 'Hourly production trends with quality metrics';
COMMENT ON VIEW refills_shift_performance IS 'Performance comparison across shifts';
COMMENT ON VIEW refills_machine_performance IS 'Machine-level performance and OEE metrics';
COMMENT ON VIEW refills_defect_analysis IS 'Defect type distribution and impact analysis';
