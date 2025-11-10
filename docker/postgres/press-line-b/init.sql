-- Press Line B - Bonnet Outer Panel Stamping (1200T Press)
-- Complex deep-draw geometry with high-strength materials (HSLA_350, DP600)

CREATE TABLE IF NOT EXISTS press_line_b_production (
    id SERIAL PRIMARY KEY,

    -- Core identifiers
    part_id VARCHAR(100) UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Production context
    press_line_id VARCHAR(50) NOT NULL DEFAULT 'LINE_B_1200T',
    die_id VARCHAR(50) NOT NULL,
    batch_id VARCHAR(100) NOT NULL,
    shift_id VARCHAR(20) NOT NULL,
    operator_id VARCHAR(20) NOT NULL,

    -- Part classification
    part_family VARCHAR(50) NOT NULL DEFAULT 'Bonnet_Outer',
    part_variant VARCHAR(50),  -- 4-door_sedan, SUV, etc.

    -- Material traceability
    coil_id VARCHAR(100) NOT NULL,
    material_grade VARCHAR(50) NOT NULL,  -- HSLA_350 or DP600
    material_thickness_nominal DECIMAL(5,3) NOT NULL,  -- 0.8mm
    material_thickness_measured DECIMAL(5,3),

    -- Process data (press operation)
    tonnage_peak DECIMAL(8,2) NOT NULL,  -- 900-1100T for bonnet deep draw on 1200T press
    stroke_rate_spm INTEGER NOT NULL,  -- Strokes per minute: 12-20 for bonnets (slower, complex draw)
    cycle_time_seconds DECIMAL(6,2) NOT NULL,  -- 3-5 seconds
    die_temperature_zone1_celsius DECIMAL(5,1),
    die_temperature_zone2_celsius DECIMAL(5,1),
    forming_energy_ton_inches DECIMAL(10,2),
    cushion_pressure_bar DECIMAL(6,2),  -- Blank holder pressure for deep draw

    -- Quality
    quality_status VARCHAR(20) NOT NULL,  -- 'ok' or 'error'
    quality_flag BOOLEAN NOT NULL,
    defect_type VARCHAR(50),  -- splitting_rupture, necking, mouse_ears, springback
    defect_severity VARCHAR(20),  -- minor, moderate, major, critical
    rework_required BOOLEAN DEFAULT FALSE,

    -- Quality metrics (Bonnet-specific dimensions)
    length_overall_mm DECIMAL(7,2),  -- ~1200mm
    width_overall_mm DECIMAL(7,2),   -- ~1100mm
    draw_depth_apex_mm DECIMAL(6,2),  -- ~185mm (deeper than doors)
    surface_profile_deviation_mm DECIMAL(5,3),
    hinge_bracket_position_x_mm DECIMAL(7,2),
    hinge_bracket_position_y_mm DECIMAL(7,2),
    thinning_percentage_max DECIMAL(5,2),  -- Material thinning at draw apex
    thinning_location VARCHAR(50),

    -- OEE components
    oee DECIMAL(5,3) NOT NULL,
    availability DECIMAL(5,3) NOT NULL,
    performance DECIMAL(5,3) NOT NULL,
    quality_rate DECIMAL(5,3) NOT NULL,

    -- Cost tracking (higher for bonnets due to complexity)
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
CREATE INDEX idx_press_b_timestamp ON press_line_b_production(timestamp);
CREATE INDEX idx_press_b_part_family ON press_line_b_production(part_family);
CREATE INDEX idx_press_b_die_id ON press_line_b_production(die_id);
CREATE INDEX idx_press_b_batch_id ON press_line_b_production(batch_id);
CREATE INDEX idx_press_b_coil_id ON press_line_b_production(coil_id);
CREATE INDEX idx_press_b_shift ON press_line_b_production(shift_id);
CREATE INDEX idx_press_b_quality ON press_line_b_production(quality_status);
CREATE INDEX idx_press_b_defect_type ON press_line_b_production(defect_type);
CREATE INDEX idx_press_b_material ON press_line_b_production(material_grade);

-- Generate 90 days of realistic bonnet panel production data
-- 2160 hourly records (24 hours × 90 days)
-- 100% Bonnet_Outer (complex deep-draw parts)

INSERT INTO press_line_b_production (
    part_id, timestamp, die_id, batch_id, shift_id, operator_id,
    part_family, part_variant, coil_id, material_grade,
    material_thickness_nominal, material_thickness_measured,
    tonnage_peak, stroke_rate_spm, cycle_time_seconds,
    die_temperature_zone1_celsius, die_temperature_zone2_celsius,
    forming_energy_ton_inches, cushion_pressure_bar,
    quality_status, quality_flag, defect_type, defect_severity, rework_required,
    length_overall_mm, width_overall_mm, draw_depth_apex_mm,
    surface_profile_deviation_mm, hinge_bracket_position_x_mm,
    hinge_bracket_position_y_mm, thinning_percentage_max, thinning_location,
    oee, availability, performance, quality_rate,
    material_cost_per_unit, labor_cost_per_unit, energy_cost_per_unit,
    temperature_celsius, humidity_percent
)
SELECT
    -- Part ID with press line prefix
    'BON_B_' || LPAD(hour_num::text, 6, '0') as part_id,

    -- Timestamp: 90 days ago, hourly
    (CURRENT_DATE - INTERVAL '90 days') + (hour_num * INTERVAL '1 hour') as timestamp,

    -- Die: Primary DIE_BO_Rev5, occasionally Rev4 for maintenance rotation
    CASE
        WHEN hour_num BETWEEN 1200 AND 1224 THEN 'DIE_BO_Rev4'  -- Week 7 maintenance
        ELSE 'DIE_BO_Rev5'
    END as die_id,

    -- Batch: Changes every 6 hours (bonnets take longer, smaller batches)
    'BATCH_B_' || LPAD((hour_num / 6)::int::text, 4, '0') as batch_id,

    -- Shift: Morning (6-14), Afternoon (14-22), Night (22-6)
    CASE
        WHEN (hour_num % 24) BETWEEN 6 AND 13 THEN 'SHIFT_MORNING'
        WHEN (hour_num % 24) BETWEEN 14 AND 21 THEN 'SHIFT_AFTERNOON'
        ELSE 'SHIFT_NIGHT'
    END as shift_id,

    -- Operator: 20 operators rotating (different from Line A)
    'OP_' || LPAD((floor(random() * 20 + 21)::int)::text, 3, '0') as operator_id,  -- OP_021 to OP_040

    'Bonnet_Outer' as part_family,
    '4_door_sedan' as part_variant,

    -- Coil: Changes every ~30 parts (30 hours) - bonnets use more material per part
    'COIL_' || CASE WHEN random() < 0.7 THEN 'SAIL_HSLA' ELSE 'NIPPON_DP600' END ||
        '_' || LPAD((hour_num / 30)::int::text, 4, '0') as coil_id,

    -- Material: 70% HSLA_350, 30% DP600 (high-strength steels)
    CASE WHEN random() < 0.7 THEN 'HSLA_350' ELSE 'DP600' END as material_grade,

    0.800 as material_thickness_nominal,
    ROUND((0.793 + random() * 0.014)::numeric, 3) as material_thickness_measured,

    -- Tonnage: 900-1100T for bonnet deep draw (1200T press capacity)
    -- Higher for HSLA/DP600 materials, varies by draw depth
    ROUND((980 + random() * 120 +
           CASE WHEN random() < 0.3 THEN 50 ELSE 0 END)::numeric, 2) as tonnage_peak,

    -- Stroke rate: 12-20 SPM (much slower than doors due to complex geometry)
    (12 + floor(random() * 9))::int as stroke_rate_spm,

    -- Cycle time: 3-5 seconds (slower forming)
    ROUND((3.0 + random() * 2.0)::numeric, 2) as cycle_time_seconds,

    -- Die temperatures (higher for deep draw)
    ROUND((52 + random() * 12)::numeric, 1) as die_temperature_zone1_celsius,
    ROUND((55 + random() * 15)::numeric, 1) as die_temperature_zone2_celsius,

    -- Forming energy (higher for deep draw)
    ROUND((3200 + random() * 600)::numeric, 2) as forming_energy_ton_inches,

    -- Cushion pressure for blank holder (critical for preventing splits)
    ROUND((85 + random() * 10)::numeric, 2) as cushion_pressure_bar,

    -- Quality: 4-5% defect rate (higher than doors due to complexity)
    -- Higher on weekends and night shift
    CASE
        WHEN random() < (0.045 +
                        CASE WHEN ((hour_num / 24)::int % 7) IN (0, 6) THEN 0.015 ELSE 0 END +
                        CASE WHEN (hour_num % 24) >= 22 OR (hour_num % 24) <= 5 THEN 0.012 ELSE 0 END)
            THEN 'error'
        ELSE 'ok'
    END as quality_status,

    CASE
        WHEN random() < 0.045 THEN FALSE
        ELSE TRUE
    END as quality_flag,

    -- Defect type: bonnet-specific failure modes
    CASE
        WHEN random() < 0.055 THEN
            (ARRAY['splitting_rupture', 'necking', 'mouse_ears', 'springback', 'wrinkling'])[floor(random() * 5 + 1)]
        ELSE NULL
    END as defect_type,

    CASE
        WHEN random() < 0.055 THEN
            (ARRAY['minor', 'moderate', 'major', 'critical'])[floor(random() * 4 + 1)]
        ELSE NULL
    END as defect_severity,

    random() < 0.035 as rework_required,

    -- Bonnet dimensions (larger than doors, complex geometry)
    ROUND((1198 + random() * 5)::numeric, 2) as length_overall_mm,
    ROUND((1098 + random() * 5)::numeric, 2) as width_overall_mm,
    ROUND((183 + random() * 5)::numeric, 2) as draw_depth_apex_mm,

    -- Surface profile deviation
    ROUND((random() * 1.2 - 0.6)::numeric, 3) as surface_profile_deviation_mm,

    -- Hinge bracket positions
    ROUND((150 + random() * 3)::numeric, 2) as hinge_bracket_position_x_mm,
    ROUND((200 + random() * 3)::numeric, 2) as hinge_bracket_position_y_mm,

    -- Thinning at draw apex (critical quality metric for deep draw)
    ROUND((18 + random() * 15)::numeric, 2) as thinning_percentage_max,
    (ARRAY['draw_apex', 'transition_zone', 'flange'])[floor(random() * 3 + 1)] as thinning_location,

    -- OEE components (lower than doors due to complexity and slower cycle time)
    ROUND((0.70 + random() * 0.20 -
           CASE WHEN ((hour_num / 24)::int % 7) IN (0, 6) THEN 0.06 ELSE 0 END)::numeric, 3) as oee,
    ROUND((0.82 + random() * 0.14)::numeric, 3) as availability,
    ROUND((0.78 + random() * 0.16)::numeric, 3) as performance,
    ROUND((0.95 + random() * 0.04)::numeric, 3) as quality_rate,

    -- Costs (higher due to HSLA/DP600 materials and complex forming)
    ROUND((1.20 + random() * 0.30)::numeric, 4) as material_cost_per_unit,
    ROUND((0.38 +
           CASE WHEN (hour_num % 24) >= 22 OR (hour_num % 24) <= 5 THEN 0.06 ELSE 0 END)::numeric, 4) as labor_cost_per_unit,
    ROUND((0.055 + random() * 0.025)::numeric, 4) as energy_cost_per_unit,

    -- Environmental
    ROUND((20 + 6 * sin(((hour_num % 24) + random() * 2) * 3.14159 / 12))::numeric, 1) as temperature_celsius,
    ROUND((45 + 15 * sin((hour_num / 24.0) * 2 * 3.14159 / 365) + random() * 8)::numeric, 1) as humidity_percent

FROM generate_series(0, 2159) as hour_num;

-- Add realistic anomalies

-- 1. HSLA material lot with insufficient forming pressure (day 60) - splitting/necking
UPDATE press_line_b_production
SET
    quality_status = 'error',
    quality_flag = FALSE,
    defect_type = CASE WHEN random() < 0.6 THEN 'splitting_rupture' ELSE 'necking' END,
    defect_severity = CASE WHEN defect_type = 'splitting_rupture' THEN 'critical' ELSE 'major' END,
    thinning_percentage_max = thinning_percentage_max * 1.6,
    oee = oee * 0.65
WHERE
    material_grade = 'HSLA_350'
    AND timestamp BETWEEN (CURRENT_DATE - INTERVAL '60 days') AND (CURRENT_DATE - INTERVAL '59 days')
    AND random() < 0.45;  -- 45% of HSLA parts affected

-- 2. Die DIE_BO_Rev5 wear progression causing increasing defects
UPDATE press_line_b_production
SET
    defect_type = CASE
        WHEN defect_type IS NULL AND random() < 0.15 THEN 'springback'
        ELSE defect_type
    END,
    quality_status = CASE
        WHEN defect_type IS NOT NULL THEN 'error'
        ELSE quality_status
    END,
    quality_flag = CASE
        WHEN defect_type IS NOT NULL THEN FALSE
        ELSE quality_flag
    END,
    surface_profile_deviation_mm = surface_profile_deviation_mm * 1.4
WHERE
    die_id = 'DIE_BO_Rev5'
    AND timestamp >= (CURRENT_DATE - INTERVAL '20 days')  -- Last 20 days
    AND random() < 0.20;

-- 3. Performance improvement week 7 (die maintenance, operator training)
UPDATE press_line_b_production
SET
    oee = LEAST(oee * 1.15, 0.95),
    cycle_time_seconds = cycle_time_seconds * 0.92,
    quality_rate = LEAST(quality_rate * 1.06, 0.99),
    quality_status = CASE WHEN quality_status = 'error' AND defect_severity != 'critical' THEN 'ok' ELSE quality_status END,
    quality_flag = CASE WHEN quality_status = 'ok' THEN TRUE ELSE quality_flag END
WHERE
    timestamp BETWEEN (CURRENT_DATE - INTERVAL '41 days') AND (CURRENT_DATE - INTERVAL '34 days');

-- Summary views

CREATE OR REPLACE VIEW press_line_b_summary AS
SELECT
    material_grade,
    COUNT(*) as total_parts,
    COUNT(*) FILTER (WHERE quality_flag = TRUE) as passed_parts,
    COUNT(*) FILTER (WHERE quality_flag = FALSE) as failed_parts,
    ROUND((COUNT(*) FILTER (WHERE quality_flag = TRUE)::numeric / COUNT(*) * 100), 2) as pass_rate_pct,
    ROUND(AVG(tonnage_peak), 2) as avg_tonnage_peak,
    ROUND(AVG(cycle_time_seconds), 2) as avg_cycle_time_seconds,
    ROUND(AVG(thinning_percentage_max), 2) as avg_thinning_pct,
    ROUND(AVG(oee), 3) as avg_oee,
    ROUND(AVG(total_cost_per_unit), 4) as avg_cost_per_unit
FROM press_line_b_production
GROUP BY material_grade;

CREATE OR REPLACE VIEW press_line_b_defects AS
SELECT
    defect_type,
    COUNT(*) as defect_count,
    ROUND((COUNT(*)::numeric / (SELECT COUNT(*) FROM press_line_b_production WHERE defect_type IS NOT NULL) * 100), 2) as pct_of_defects,
    ROUND(AVG(thinning_percentage_max), 2) as avg_thinning_when_defect,
    ARRAY_AGG(DISTINCT defect_severity) as severity_levels
FROM press_line_b_production
WHERE defect_type IS NOT NULL
GROUP BY defect_type
ORDER BY defect_count DESC;

CREATE OR REPLACE VIEW press_line_b_daily_summary AS
SELECT
    DATE_TRUNC('day', timestamp)::date as production_date,
    material_grade,
    COUNT(*) as parts_produced,
    COUNT(*) FILTER (WHERE quality_flag = TRUE) as parts_passed,
    ROUND(AVG(oee), 3) as avg_oee,
    ROUND(AVG(tonnage_peak), 1) as avg_tonnage,
    ROUND(AVG(thinning_percentage_max), 2) as avg_thinning_pct
FROM press_line_b_production
GROUP BY DATE_TRUNC('day', timestamp)::date, material_grade
ORDER BY production_date DESC;

COMMENT ON TABLE press_line_b_production IS 'Press Line B (1200T) - Bonnet outer panel deep-draw stamping with 90 days historical data';
COMMENT ON VIEW press_line_b_summary IS 'Summary statistics by material grade (HSLA_350 vs DP600)';
COMMENT ON VIEW press_line_b_defects IS 'Defect analysis showing complex failure modes';
COMMENT ON VIEW press_line_b_daily_summary IS 'Daily production rollup by material grade';
