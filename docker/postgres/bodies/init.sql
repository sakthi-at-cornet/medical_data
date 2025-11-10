-- Bodies Manufacturing Database - Enhanced with 90 days historical data
-- Pen bodies production line data

CREATE TABLE IF NOT EXISTS bodies_production (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    line_id VARCHAR(50) NOT NULL,
    machine_id VARCHAR(50) NOT NULL,
    batch_id VARCHAR(100) NOT NULL,
    shift_id VARCHAR(20) NOT NULL,
    operator_id VARCHAR(20) NOT NULL,

    -- Original metrics
    durability_score DECIMAL(5,1) NOT NULL,
    color_match_rating DECIMAL(5,3) NOT NULL,
    length_mm DECIMAL(6,2) NOT NULL,
    wall_thickness_mm DECIMAL(4,2) NOT NULL,
    material VARCHAR(50) NOT NULL,
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
CREATE INDEX idx_bodies_timestamp ON bodies_production(timestamp);
CREATE INDEX idx_bodies_batch_id ON bodies_production(batch_id);
CREATE INDEX idx_bodies_line_id ON bodies_production(line_id);
CREATE INDEX idx_bodies_machine_id ON bodies_production(machine_id);
CREATE INDEX idx_bodies_shift_id ON bodies_production(shift_id);
CREATE INDEX idx_bodies_quality ON bodies_production(quality_status);
CREATE INDEX idx_bodies_material ON bodies_production(material);
CREATE INDEX idx_bodies_defect_type ON bodies_production(defect_type);

-- Generate 90 days of hourly data (2160 records per component)
-- Realistic patterns: shifts, seasonality, anomalies, weekends
INSERT INTO bodies_production (
    timestamp, line_id, machine_id, batch_id, shift_id, operator_id,
    durability_score, color_match_rating, length_mm, wall_thickness_mm,
    material, quality_status,
    cycle_time_seconds, first_pass_yield, defect_type, rework_required,
    material_cost_per_unit, labor_cost_per_unit, energy_cost_per_unit,
    temperature_celsius, humidity_percent,
    oee, availability, performance, quality_rate
)
SELECT
    -- Timestamp: 90 days ago, hourly
    (CURRENT_DATE - INTERVAL '90 days') + (hour_num * INTERVAL '1 hour') as timestamp,

    -- Line: 2 lines
    CASE WHEN random() < 0.5 THEN 'LINE-BODIES-001' ELSE 'LINE-BODIES-002' END as line_id,

    -- Machine: 5 machines per line (M1-M5)
    'MACHINE-B-' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as machine_id,

    -- Batch: Changes every 8 hours
    'BATCH-B-' || LPAD((floor(hour_num / 8)::int)::text, 5, '0') as batch_id,

    -- Shift: Morning (6-14), Afternoon (14-22), Night (22-6)
    CASE
        WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 6 AND 13 THEN 'SHIFT-MORNING'
        WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 14 AND 21 THEN 'SHIFT-AFTERNOON'
        ELSE 'SHIFT-NIGHT'
    END as shift_id,

    -- Operator: 30 operators rotating
    'OP-' || LPAD((floor(random() * 30 + 1)::int)::text, 3, '0') as operator_id,

    -- Original metrics with realistic variance
    -- Durability: errors 4% of time, bamboo performs better
    CASE
        WHEN random() < (0.04 + CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.02 ELSE 0 END)
            THEN ROUND((40 + random() * 30)::numeric, 1)
        ELSE ROUND((77 + random() * 16)::numeric, 1)
    END as durability_score,

    ROUND((0.90 + random() * 0.10)::numeric, 3) as color_match_rating,

    ROUND((148.5 + random() * 3.0)::numeric, 2) as length_mm,

    ROUND((0.80 + random() * 0.40)::numeric, 2) as wall_thickness_mm,

    -- Material: bamboo 40%, plastic 35%, metal 25%
    -- Bamboo has better durability (85-95 vs 77-93)
    (ARRAY['plastic', 'plastic', 'bamboo', 'bamboo', 'metal'])[floor(random() * 5 + 1)] as material,

    -- Quality status: errors more likely on weekends and night shift
    CASE
        WHEN random() < (0.04 +
                        CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.02 ELSE 0 END +
                        CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 0.01 ELSE 0 END)
            THEN 'error'
        ELSE 'ok'
    END as quality_status,

    -- NEW METRICS

    -- Cycle time: 60-90 seconds, slower for metal
    ROUND((60 + random() * 30 +
           CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 12 ELSE 0 END)::numeric, 2) as cycle_time_seconds,

    -- First pass yield: 91-94%
    random() > 0.08 as first_pass_yield,

    -- Defect type: only if quality_status is error
    CASE
        WHEN random() < 0.06 THEN
            (ARRAY['crack', 'dimensional', 'surface_defect', 'color_mismatch', 'wall_thickness', 'material_defect'])[floor(random() * 6 + 1)]
        ELSE NULL
    END as defect_type,

    -- Rework: 6% require rework
    random() < 0.06 as rework_required,

    -- Costs: bamboo more expensive, metal most expensive
    ROUND((0.12 + random() * 0.08)::numeric, 4) as material_cost_per_unit,
    ROUND((0.20 +
           CASE WHEN EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) BETWEEN 22 AND 5 THEN 0.04 ELSE 0 END)::numeric, 4) as labor_cost_per_unit,
    ROUND((0.03 + random() * 0.02)::numeric, 4) as energy_cost_per_unit,

    -- Environmental: temperature varies by time of day, humidity by season
    -- Bamboo sensitive to humidity (optimal 40-60%)
    ROUND((18 + 8 * sin((EXTRACT(HOUR FROM (hour_num * INTERVAL '1 hour')) + random() * 2) * 3.14159 / 12) +
           3 * sin((hour_num / 24.0) * 2 * 3.14159 / 365))::numeric, 1) as temperature_celsius,
    ROUND((40 + 20 * sin((hour_num / 24.0) * 2 * 3.14159 / 365) + random() * 10)::numeric, 1) as humidity_percent,

    -- OEE and components: Overall Equipment Effectiveness
    -- OEE = Availability × Performance × Quality
    ROUND((0.72 + random() * 0.24 -
           CASE WHEN EXTRACT(DOW FROM (hour_num * INTERVAL '1 hour')) IN (0, 6) THEN 0.04 ELSE 0 END)::numeric, 3) as oee,
    ROUND((0.86 + random() * 0.11)::numeric, 3) as availability,
    ROUND((0.82 + random() * 0.14)::numeric, 3) as performance,
    ROUND((0.91 + random() * 0.08)::numeric, 3) as quality_rate

FROM generate_series(0, 2159) as hour_num;

-- Add some realistic anomalies and patterns
-- Bamboo performs better
UPDATE bodies_production
SET
    durability_score = LEAST(durability_score * 1.13, 99.0),
    quality_rate = LEAST(quality_rate * 1.08, 0.99)
WHERE material = 'bamboo';

-- Bamboo quality drops when humidity too low or too high
UPDATE bodies_production
SET
    quality_status = 'error',
    defect_type = 'material_defect',
    durability_score = durability_score * 0.7
WHERE
    material = 'bamboo'
    AND (humidity_percent < 35 OR humidity_percent > 65)
    AND random() < 0.4;

-- Machine B04 had calibration issues on day 50
UPDATE bodies_production
SET
    quality_status = 'error',
    defect_type = 'dimensional',
    oee = oee * 0.65,
    availability = availability * 0.75
WHERE
    machine_id = 'MACHINE-B-04'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '50 days') AND (CURRENT_DATE - INTERVAL '49 days');

-- Line 1 had excellent bamboo production week 10
UPDATE bodies_production
SET
    oee = LEAST(oee * 1.12, 0.99),
    quality_rate = LEAST(quality_rate * 1.06, 0.99),
    durability_score = LEAST(durability_score * 1.05, 99.0)
WHERE
    line_id = 'LINE-BODIES-001'
    AND material = 'bamboo'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '20 days') AND (CURRENT_DATE - INTERVAL '13 days');

-- Holiday reduced production (day 60-62)
UPDATE bodies_production
SET
    oee = oee * 0.55,
    availability = availability * 0.65,
    performance = performance * 0.82
WHERE
    timestamp BETWEEN (CURRENT_DATE - INTERVAL '62 days') AND (CURRENT_DATE - INTERVAL '59 days');

-- Summary statistics view
CREATE OR REPLACE VIEW bodies_summary AS
SELECT
    line_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    COUNT(*) FILTER (WHERE quality_status = 'error') as failed_units,
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability,
    ROUND(AVG(color_match_rating)::numeric, 3) as avg_color_match,
    ROUND(AVG(length_mm)::numeric, 2) as avg_length,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_total_cost
FROM bodies_production
GROUP BY line_id;

-- Material performance view - CRUCIAL for "bamboo performs better" insights
CREATE OR REPLACE VIEW bodies_material_performance AS
SELECT
    material,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability,
    ROUND(AVG(color_match_rating)::numeric, 3) as avg_color_match,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit)::numeric, 4) as avg_material_cost,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_total_cost,
    -- Cost per passed unit (economic efficiency)
    ROUND((AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit) /
           (COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*)))::numeric, 4) as cost_per_passed_unit
FROM bodies_production
GROUP BY material
ORDER BY avg_durability DESC;

-- Hourly trends view
CREATE OR REPLACE VIEW bodies_hourly_trends AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    line_id,
    COUNT(*) as units_produced,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability
FROM bodies_production
GROUP BY DATE_TRUNC('hour', timestamp), line_id
ORDER BY hour DESC;

-- Shift performance view
CREATE OR REPLACE VIEW bodies_shift_performance AS
SELECT
    shift_id,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(oee)::numeric, 3) as avg_oee,
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time,
    ROUND(AVG(material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit)::numeric, 4) as avg_cost_per_unit
FROM bodies_production
GROUP BY shift_id
ORDER BY pass_rate DESC;

-- Machine performance view
CREATE OR REPLACE VIEW bodies_machine_performance AS
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
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time
FROM bodies_production
GROUP BY machine_id, line_id
ORDER BY avg_oee DESC;

-- Defect analysis view
CREATE OR REPLACE VIEW bodies_defect_analysis AS
SELECT
    defect_type,
    COUNT(*) as defect_count,
    ROUND((COUNT(*)::numeric / (SELECT COUNT(*) FROM bodies_production WHERE defect_type IS NOT NULL) * 100), 2) as pct_of_defects,
    ROUND(AVG(cycle_time_seconds)::numeric, 2) as avg_cycle_time_when_defect,
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability_when_defect
FROM bodies_production
WHERE defect_type IS NOT NULL
GROUP BY defect_type
ORDER BY defect_count DESC;

-- Environmental impact view - for bamboo humidity analysis
CREATE OR REPLACE VIEW bodies_environmental_impact AS
SELECT
    material,
    CASE
        WHEN humidity_percent < 35 THEN 'low (<35%)'
        WHEN humidity_percent BETWEEN 35 AND 50 THEN 'optimal (35-50%)'
        WHEN humidity_percent BETWEEN 50 AND 65 THEN 'good (50-65%)'
        ELSE 'high (>65%)'
    END as humidity_range,
    COUNT(*) as total_units,
    COUNT(*) FILTER (WHERE quality_status = 'ok') as passed_units,
    ROUND((COUNT(*) FILTER (WHERE quality_status = 'ok')::numeric / COUNT(*) * 100), 2) as pass_rate,
    ROUND(AVG(durability_score)::numeric, 1) as avg_durability
FROM bodies_production
GROUP BY material, humidity_range
ORDER BY material, humidity_range;

COMMENT ON TABLE bodies_production IS 'Pen bodies manufacturing line production data - 90 days historical with rich dimensions';
COMMENT ON VIEW bodies_summary IS 'Summary statistics for bodies production by line';
COMMENT ON VIEW bodies_material_performance IS 'Material comparison showing bamboo superiority';
COMMENT ON VIEW bodies_hourly_trends IS 'Hourly production trends with quality metrics';
COMMENT ON VIEW bodies_shift_performance IS 'Performance comparison across shifts';
COMMENT ON VIEW bodies_machine_performance IS 'Machine-level performance and OEE metrics';
COMMENT ON VIEW bodies_defect_analysis IS 'Defect type distribution and impact analysis';
COMMENT ON VIEW bodies_environmental_impact IS 'Environmental factors impact on quality by material';
