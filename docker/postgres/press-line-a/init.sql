-- Press Line A - Door Outer Panel Stamping (800T Press)
-- Automotive body panel production with die management and material traceability

CREATE TABLE IF NOT EXISTS press_line_a_production (
    id SERIAL PRIMARY KEY,

    -- Core identifiers
    part_id VARCHAR(100) UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Production context
    press_line_id VARCHAR(50) NOT NULL DEFAULT 'LINE_A_800T',
    die_id VARCHAR(50) NOT NULL,
    batch_id VARCHAR(100) NOT NULL,
    shift_id VARCHAR(20) NOT NULL,
    operator_id VARCHAR(20) NOT NULL,

    -- Part classification
    part_family VARCHAR(50) NOT NULL,  -- Door_Outer_Left or Door_Outer_Right
    part_variant VARCHAR(50),  -- 4-door_sedan, 2-door_coupe, etc.

    -- Material traceability
    coil_id VARCHAR(100) NOT NULL,
    material_grade VARCHAR(50) NOT NULL,  -- CRS_SPCC
    material_thickness_nominal DECIMAL(5,3) NOT NULL,  -- 0.8mm
    material_thickness_measured DECIMAL(5,3),

    -- Process data (press operation)
    tonnage_peak DECIMAL(8,2) NOT NULL,  -- 600-650T for doors on 800T press
    stroke_rate_spm INTEGER NOT NULL,  -- Strokes per minute: 45-50 for doors
    cycle_time_seconds DECIMAL(6,2) NOT NULL,  -- 1.2-1.5 seconds
    die_temperature_zone1_celsius DECIMAL(5,1),
    die_temperature_zone2_celsius DECIMAL(5,1),
    forming_energy_ton_inches DECIMAL(10,2),

    -- Quality
    quality_status VARCHAR(20) NOT NULL,  -- 'ok' or 'error'
    quality_flag BOOLEAN NOT NULL,
    defect_type VARCHAR(50),  -- springback, surface_scratch, burr, piercing_burst
    defect_severity VARCHAR(20),  -- minor, moderate, major, critical
    rework_required BOOLEAN DEFAULT FALSE,

    -- Quality metrics (Door-specific dimensions)
    length_overall_mm DECIMAL(7,2),  -- ~1090mm
    width_overall_mm DECIMAL(7,2),   -- ~645mm
    draw_depth_mm DECIMAL(6,2),      -- ~152mm
    flange_width_bottom_mm DECIMAL(5,2),
    hole_hinge_upper_diameter_mm DECIMAL(5,3),
    hole_hinge_lower_diameter_mm DECIMAL(5,3),
    surface_profile_deviation_mm DECIMAL(5,3),  -- Springback measurement

    -- OEE components
    oee DECIMAL(5,3) NOT NULL,
    availability DECIMAL(5,3) NOT NULL,
    performance DECIMAL(5,3) NOT NULL,
    quality_rate DECIMAL(5,3) NOT NULL,

    -- Cost tracking
    material_cost_per_unit DECIMAL(8,4) NOT NULL,
    labor_cost_per_unit DECIMAL(8,4) NOT NULL,
    energy_cost_per_unit DECIMAL(8,4) NOT NULL,
    total_cost_per_unit DECIMAL(8,4) GENERATED ALWAYS AS (
        material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit
    ) STORED,

    -- Environmental factors
    temperature_celsius DECIMAL(4,1),
    humidity_percent DECIMAL(4,1),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_press_a_timestamp ON press_line_a_production(timestamp);
CREATE INDEX idx_press_a_part_family ON press_line_a_production(part_family);
CREATE INDEX idx_press_a_die_id ON press_line_a_production(die_id);
CREATE INDEX idx_press_a_batch_id ON press_line_a_production(batch_id);
CREATE INDEX idx_press_a_coil_id ON press_line_a_production(coil_id);
CREATE INDEX idx_press_a_shift ON press_line_a_production(shift_id);
CREATE INDEX idx_press_a_quality ON press_line_a_production(quality_status);
CREATE INDEX idx_press_a_defect_type ON press_line_a_production(defect_type);

-- Generate 90 days of realistic door panel production data
-- 2160 hourly records (24 hours × 90 days)
-- 50% Door_Outer_Left, 50% Door_Outer_Right

INSERT INTO press_line_a_production (
    part_id, timestamp, die_id, batch_id, shift_id, operator_id,
    part_family, part_variant, coil_id, material_grade,
    material_thickness_nominal, material_thickness_measured,
    tonnage_peak, stroke_rate_spm, cycle_time_seconds,
    die_temperature_zone1_celsius, die_temperature_zone2_celsius,
    forming_energy_ton_inches,
    quality_status, quality_flag, defect_type, defect_severity, rework_required,
    length_overall_mm, width_overall_mm, draw_depth_mm,
    flange_width_bottom_mm, hole_hinge_upper_diameter_mm,
    hole_hinge_lower_diameter_mm, surface_profile_deviation_mm,
    oee, availability, performance, quality_rate,
    material_cost_per_unit, labor_cost_per_unit, energy_cost_per_unit,
    temperature_celsius, humidity_percent
)
SELECT
    -- Part ID with press line prefix
    'DOL_A_' || LPAD(hour_num::text, 6, '0') || '_' ||
        CASE WHEN random() < 0.5 THEN 'L' ELSE 'R' END as part_id,

    -- Timestamp: 90 days ago, hourly
    (CURRENT_DATE - INTERVAL '90 days') + (hour_num * INTERVAL '1 hour') as timestamp,

    -- Die: Alternates between left and right every ~8 hours (batch change)
    CASE
        WHEN (hour_num / 8)::int % 2 = 0 THEN 'DIE_DOL_Rev3'
        ELSE 'DIE_DOR_Rev2'
    END as die_id,

    -- Batch: Changes every 8 hours
    'BATCH_A_' || LPAD((hour_num / 8)::int::text, 4, '0') as batch_id,

    -- Shift: Morning (6-14), Afternoon (14-22), Night (22-6)
    CASE
        WHEN (hour_num % 24) BETWEEN 6 AND 13 THEN 'SHIFT_MORNING'
        WHEN (hour_num % 24) BETWEEN 14 AND 21 THEN 'SHIFT_AFTERNOON'
        ELSE 'SHIFT_NIGHT'
    END as shift_id,

    -- Operator: 20 operators rotating
    'OP_' || LPAD((floor(random() * 20 + 1)::int)::text, 3, '0') as operator_id,

    -- Part family: Alternates with die
    CASE
        WHEN (hour_num / 8)::int % 2 = 0 THEN 'Door_Outer_Left'
        ELSE 'Door_Outer_Right'
    END as part_family,

    '4_door_sedan' as part_variant,

    -- Coil: Changes every ~40 parts (40 hours)
    'COIL_JSW_' || LPAD((hour_num / 40)::int::text, 4, '0') as coil_id,

    'CRS_SPCC' as material_grade,
    0.800 as material_thickness_nominal,
    ROUND((0.795 + random() * 0.010)::numeric, 3) as material_thickness_measured,

    -- Tonnage: 600-650T for doors (800T press capacity)
    -- Higher on night shift (operator fatigue → over-forming)
    ROUND((620 + random() * 30 +
           CASE WHEN (hour_num % 24) >= 22 OR (hour_num % 24) <= 5 THEN 15 ELSE 0 END)::numeric, 2) as tonnage_peak,

    -- Stroke rate: 45-50 SPM for doors
    (45 + floor(random() * 6))::int as stroke_rate_spm,

    -- Cycle time: 1.2-1.5 seconds
    ROUND((1.2 + random() * 0.3)::numeric, 2) as cycle_time_seconds,

    -- Die temperatures
    ROUND((45 + random() * 10)::numeric, 1) as die_temperature_zone1_celsius,
    ROUND((48 + random() * 12)::numeric, 1) as die_temperature_zone2_celsius,

    -- Forming energy
    ROUND((1800 + random() * 200)::numeric, 2) as forming_energy_ton_inches,

    -- Quality: 2-3% defect rate, higher on weekends and night shift
    CASE
        WHEN random() < (0.025 +
                        CASE WHEN ((hour_num / 24)::int % 7) IN (0, 6) THEN 0.01 ELSE 0 END +
                        CASE WHEN (hour_num % 24) >= 22 OR (hour_num % 24) <= 5 THEN 0.008 ELSE 0 END)
            THEN 'error'
        ELSE 'ok'
    END as quality_status,

    CASE
        WHEN random() < 0.025 THEN FALSE
        ELSE TRUE
    END as quality_flag,

    -- Defect type: only if error
    CASE
        WHEN random() < 0.03 THEN
            (ARRAY['springback', 'surface_scratch', 'burr', 'piercing_burst', 'dimensional'])[floor(random() * 5 + 1)]
        ELSE NULL
    END as defect_type,

    CASE
        WHEN random() < 0.03 THEN
            (ARRAY['minor', 'moderate', 'major'])[floor(random() * 3 + 1)]
        ELSE NULL
    END as defect_severity,

    random() < 0.02 as rework_required,

    -- Door dimensions (Class A surface)
    ROUND((1088 + random() * 4)::numeric, 2) as length_overall_mm,
    ROUND((643 + random() * 4)::numeric, 2) as width_overall_mm,
    ROUND((151 + random() * 3)::numeric, 2) as draw_depth_mm,
    ROUND((23.5 + random() * 1.5)::numeric, 2) as flange_width_bottom_mm,
    ROUND((10.00 + random() * 0.05)::numeric, 3) as hole_hinge_upper_diameter_mm,
    ROUND((10.00 + random() * 0.05)::numeric, 3) as hole_hinge_lower_diameter_mm,

    -- Surface profile deviation (springback indicator)
    ROUND((random() * 0.8 - 0.4)::numeric, 3) as surface_profile_deviation_mm,

    -- OEE components
    ROUND((0.78 + random() * 0.18 -
           CASE WHEN ((hour_num / 24)::int % 7) IN (0, 6) THEN 0.05 ELSE 0 END)::numeric, 3) as oee,
    ROUND((0.88 + random() * 0.10)::numeric, 3) as availability,
    ROUND((0.85 + random() * 0.12)::numeric, 3) as performance,
    ROUND((0.97 + random() * 0.025)::numeric, 3) as quality_rate,

    -- Costs
    ROUND((0.85 + random() * 0.15)::numeric, 4) as material_cost_per_unit,
    ROUND((0.22 +
           CASE WHEN (hour_num % 24) >= 22 OR (hour_num % 24) <= 5 THEN 0.04 ELSE 0 END)::numeric, 4) as labor_cost_per_unit,
    ROUND((0.035 + random() * 0.015)::numeric, 4) as energy_cost_per_unit,

    -- Environmental
    ROUND((20 + 6 * sin(((hour_num % 24) + random() * 2) * 3.14159 / 12))::numeric, 1) as temperature_celsius,
    ROUND((45 + 15 * sin((hour_num / 24.0) * 2 * 3.14159 / 365) + random() * 8)::numeric, 1) as humidity_percent

FROM generate_series(0, 2159) as hour_num;

-- Add realistic anomalies

-- 1. Die DIE_DOL_Rev3 calibration issue on day 45 (24 hours of poor quality)
UPDATE press_line_a_production
SET
    quality_status = 'error',
    quality_flag = FALSE,
    defect_type = 'springback',
    defect_severity = 'major',
    surface_profile_deviation_mm = surface_profile_deviation_mm * 2.5,
    oee = oee * 0.75,
    quality_rate = quality_rate * 0.80
WHERE
    die_id = 'DIE_DOL_Rev3'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '45 days') AND (CURRENT_DATE - INTERVAL '44 days')
    AND random() < 0.40;  -- 40% of parts affected

-- 2. Coil supplier lot variation (high yield strength causing springback) - affects specific coils
UPDATE press_line_a_production
SET
    defect_type = 'springback',
    defect_severity = 'moderate',
    quality_status = CASE WHEN random() < 0.08 THEN 'error' ELSE quality_status END,
    quality_flag = CASE WHEN random() < 0.08 THEN FALSE ELSE quality_flag END,
    surface_profile_deviation_mm = surface_profile_deviation_mm * 1.8
WHERE
    coil_id IN ('COIL_JSW_0015', 'COIL_JSW_0016', 'COIL_JSW_0017')  -- Problem coils
    AND random() < 0.35;

-- 3. Performance improvement week 12 (better operator training, die maintenance)
UPDATE press_line_a_production
SET
    oee = LEAST(oee * 1.12, 0.99),
    quality_rate = LEAST(quality_rate * 1.05, 0.99),
    cycle_time_seconds = cycle_time_seconds * 0.95,
    quality_status = 'ok',
    quality_flag = TRUE
WHERE
    timestamp BETWEEN (CURRENT_DATE - INTERVAL '6 days') AND (CURRENT_DATE - INTERVAL '1 day');

-- Summary views

CREATE OR REPLACE VIEW press_line_a_summary AS
SELECT
    part_family,
    COUNT(*) as total_parts,
    COUNT(*) FILTER (WHERE quality_flag = TRUE) as passed_parts,
    COUNT(*) FILTER (WHERE quality_flag = FALSE) as failed_parts,
    ROUND((COUNT(*) FILTER (WHERE quality_flag = TRUE)::numeric / COUNT(*) * 100), 2) as pass_rate_pct,
    ROUND(AVG(tonnage_peak), 2) as avg_tonnage_peak,
    ROUND(AVG(cycle_time_seconds), 2) as avg_cycle_time_seconds,
    ROUND(AVG(oee), 3) as avg_oee,
    ROUND(AVG(total_cost_per_unit), 4) as avg_cost_per_unit
FROM press_line_a_production
GROUP BY part_family;

CREATE OR REPLACE VIEW press_line_a_defects AS
SELECT
    defect_type,
    COUNT(*) as defect_count,
    ROUND((COUNT(*)::numeric / (SELECT COUNT(*) FROM press_line_a_production WHERE defect_type IS NOT NULL) * 100), 2) as pct_of_defects,
    ROUND(AVG(surface_profile_deviation_mm), 3) as avg_deviation_mm
FROM press_line_a_production
WHERE defect_type IS NOT NULL
GROUP BY defect_type
ORDER BY defect_count DESC;

CREATE OR REPLACE VIEW press_line_a_daily_summary AS
SELECT
    DATE_TRUNC('day', timestamp)::date as production_date,
    part_family,
    COUNT(*) as parts_produced,
    COUNT(*) FILTER (WHERE quality_flag = TRUE) as parts_passed,
    ROUND(AVG(oee), 3) as avg_oee,
    ROUND(AVG(tonnage_peak), 1) as avg_tonnage
FROM press_line_a_production
GROUP BY DATE_TRUNC('day', timestamp)::date, part_family
ORDER BY production_date DESC;

COMMENT ON TABLE press_line_a_production IS 'Press Line A (800T) - Door outer panel stamping with 90 days historical data';
COMMENT ON VIEW press_line_a_summary IS 'Summary statistics by part family';
COMMENT ON VIEW press_line_a_defects IS 'Defect analysis showing types and frequencies';
COMMENT ON VIEW press_line_a_daily_summary IS 'Daily production rollup by part family';
