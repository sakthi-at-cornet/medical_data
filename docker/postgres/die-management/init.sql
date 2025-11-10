-- Die Management System
-- Tracks die inventory, changeover events, condition assessments, and maintenance

-- ====================================================================
-- 1. DIE MASTER TABLE
-- ====================================================================

CREATE TABLE IF NOT EXISTS die_master (
    die_id VARCHAR(50) PRIMARY KEY,
    part_family VARCHAR(50) NOT NULL,  -- Door_Outer_Left, Door_Outer_Right, Bonnet_Outer
    die_type VARCHAR(50) NOT NULL,  -- Progressive, Transfer, Line
    press_line_compatible VARCHAR(100),  -- LINE_A_800T, LINE_B_1200T
    tonnage_rating DECIMAL(8,2) NOT NULL,  -- Rated tonnage capacity

    -- Lifecycle tracking
    manufacture_date DATE,
    first_production_date DATE,
    total_strokes_count BIGINT DEFAULT 0,
    service_life_target_strokes BIGINT,  -- Design life

    -- Current status
    health_status VARCHAR(20) NOT NULL DEFAULT 'good',  -- good, fair, poor, maintenance_required
    current_location VARCHAR(100),  -- Line_A, Line_B, Die_Shop, Storage
    is_active BOOLEAN DEFAULT TRUE,

    -- Maintenance schedule
    last_maintenance_date DATE,
    next_maintenance_due_date DATE,
    maintenance_interval_strokes INT DEFAULT 50000,

    -- Technical details
    number_of_stations INT,  -- For progressive dies
    binder_force_required BOOLEAN DEFAULT FALSE,
    material_compatibility TEXT,  -- CRS_SPCC, HSLA_350, DP600

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert 4 dies as per checklist
INSERT INTO die_master (
    die_id, part_family, die_type, press_line_compatible, tonnage_rating,
    manufacture_date, first_production_date, total_strokes_count, service_life_target_strokes,
    health_status, current_location, is_active,
    last_maintenance_date, next_maintenance_due_date, maintenance_interval_strokes,
    number_of_stations, binder_force_required, material_compatibility
) VALUES
    -- Door Left Die (Line A)
    ('DIE_DOL_Rev3', 'Door_Outer_Left', 'Progressive', 'LINE_A_800T', 650.0,
     '2023-02-15', '2023-04-01', 980000, 2000000,
     'fair', 'LINE_A_800T', TRUE,
     '2024-08-01', '2025-01-15', 50000,
     6, FALSE, 'CRS_SPCC'),

    -- Door Right Die (Line A)
    ('DIE_DOR_Rev2', 'Door_Outer_Right', 'Progressive', 'LINE_A_800T', 650.0,
     '2022-11-10', '2023-01-20', 1120000, 2000000,
     'good', 'LINE_A_800T', TRUE,
     '2024-09-10', '2025-02-25', 50000,
     6, FALSE, 'CRS_SPCC'),

    -- Bonnet Die Rev5 (Primary - Line B)
    ('DIE_BO_Rev5', 'Bonnet_Outer', 'Transfer', 'LINE_B_1200T', 1100.0,
     '2023-06-01', '2023-08-15', 650000, 1500000,
     'poor', 'LINE_B_1200T', TRUE,
     '2024-07-20', '2024-12-15', 40000,
     4, TRUE, 'HSLA_350, DP600'),

    -- Bonnet Die Rev4 (Backup - Line B)
    ('DIE_BO_Rev4', 'Bonnet_Outer', 'Transfer', 'LINE_B_1200T', 1100.0,
     '2022-08-25', '2022-11-01', 890000, 1500000,
     'good', 'Die_Shop', TRUE,
     '2024-10-05', '2025-03-20', 40000,
     4, TRUE, 'HSLA_350, DP600');

CREATE INDEX idx_die_part_family ON die_master(part_family);
CREATE INDEX idx_die_health_status ON die_master(health_status);
CREATE INDEX idx_die_location ON die_master(current_location);

-- ====================================================================
-- 2. DIE CHANGEOVER EVENTS TABLE
-- ====================================================================

CREATE TABLE IF NOT EXISTS die_changeover_events (
    changeover_id SERIAL PRIMARY KEY,
    press_line_id VARCHAR(50) NOT NULL,

    -- Timing
    timestamp_start TIMESTAMP WITH TIME ZONE NOT NULL,
    timestamp_end TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes DECIMAL(8,2) GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (timestamp_end - timestamp_start)) / 60
    ) STORED,

    -- Die information
    die_removed_id VARCHAR(50),
    die_installed_id VARCHAR(50),

    -- Changeover type
    changeover_type VARCHAR(50),  -- Scheduled, Emergency, Maintenance, Trial
    reason VARCHAR(200),  -- Part_family_switch, Die_wear, Preventive_maintenance

    -- SMED metrics (Single-Minute Exchange of Die)
    smed_target_minutes DECIMAL(6,2),  -- Target changeover time
    smed_variance_minutes DECIMAL(6,2) GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (timestamp_end - timestamp_start)) / 60 - smed_target_minutes
    ) STORED,

    -- Personnel
    setup_person_id VARCHAR(20),
    operator_id VARCHAR(20),
    team_size INT DEFAULT 2,

    -- Quality
    first_piece_inspection_passed BOOLEAN,
    adjustments_required INT DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    FOREIGN KEY (die_removed_id) REFERENCES die_master(die_id),
    FOREIGN KEY (die_installed_id) REFERENCES die_master(die_id)
);

-- Generate ~270 changeover events over 90 days
-- Line A: Every 8 hours (alternating between DOL and DOR) = ~270 events
-- Line B: Occasional (week 7 maintenance) = ~1 event

INSERT INTO die_changeover_events (
    press_line_id, timestamp_start, timestamp_end,
    die_removed_id, die_installed_id, changeover_type, reason,
    smed_target_minutes, setup_person_id, operator_id, team_size,
    first_piece_inspection_passed, adjustments_required
)
-- Line A changeovers (alternating dies every 8 hours)
SELECT
    'LINE_A_800T' as press_line_id,
    (CURRENT_DATE - INTERVAL '90 days') + (changeover_num * 8 * INTERVAL '1 hour') as timestamp_start,
    (CURRENT_DATE - INTERVAL '90 days') + (changeover_num * 8 * INTERVAL '1 hour') +
        ((25 + random() * 15) * INTERVAL '1 minute') as timestamp_end,

    -- Alternating dies
    CASE WHEN changeover_num % 2 = 0 THEN 'DIE_DOR_Rev2' ELSE 'DIE_DOL_Rev3' END as die_removed_id,
    CASE WHEN changeover_num % 2 = 0 THEN 'DIE_DOL_Rev3' ELSE 'DIE_DOR_Rev2' END as die_installed_id,

    CASE
        WHEN changeover_num % 20 = 0 THEN 'Maintenance'
        WHEN random() < 0.05 THEN 'Emergency'
        ELSE 'Scheduled'
    END as changeover_type,

    'Part_family_switch' as reason,

    30.0 as smed_target_minutes,  -- Target 30 minutes

    'SETUP_' || LPAD((floor(random() * 10 + 1)::int)::text, 2, '0') as setup_person_id,
    'OP_' || LPAD((floor(random() * 20 + 1)::int)::text, 3, '0') as operator_id,
    2 as team_size,

    random() < 0.92 as first_piece_inspection_passed,
    floor(random() * 3)::int as adjustments_required

FROM generate_series(1, 270) as changeover_num;

-- Add a few Line B changeovers
INSERT INTO die_changeover_events (
    press_line_id, timestamp_start, timestamp_end,
    die_removed_id, die_installed_id, changeover_type, reason,
    smed_target_minutes, setup_person_id, operator_id, team_size,
    first_piece_inspection_passed, adjustments_required
)
VALUES
    -- Week 7 maintenance changeover
    ('LINE_B_1200T',
     CURRENT_DATE - INTERVAL '41 days' + INTERVAL '6 hours',
     CURRENT_DATE - INTERVAL '41 days' + INTERVAL '7 hours 45 minutes',
     'DIE_BO_Rev5', 'DIE_BO_Rev4', 'Maintenance', 'Preventive_maintenance_Rev5',
     90.0, 'SETUP_03', 'OP_025', 3, TRUE, 2),

    -- Return to primary die
    ('LINE_B_1200T',
     CURRENT_DATE - INTERVAL '40 days' + INTERVAL '18 hours',
     CURRENT_DATE - INTERVAL '40 days' + INTERVAL '20 hours 15 minutes',
     'DIE_BO_Rev4', 'DIE_BO_Rev5', 'Scheduled', 'Return_to_primary_die',
     90.0, 'SETUP_03', 'OP_028', 3, TRUE, 1);

CREATE INDEX idx_changeover_press_line ON die_changeover_events(press_line_id);
CREATE INDEX idx_changeover_timestamp ON die_changeover_events(timestamp_start);
CREATE INDEX idx_changeover_type ON die_changeover_events(changeover_type);
CREATE INDEX idx_changeover_removed_die ON die_changeover_events(die_removed_id);
CREATE INDEX idx_changeover_installed_die ON die_changeover_events(die_installed_id);

-- ====================================================================
-- 3. DIE CONDITION ASSESSMENTS TABLE
-- ====================================================================

CREATE TABLE IF NOT EXISTS die_condition_assessments (
    assessment_id SERIAL PRIMARY KEY,
    die_id VARCHAR(50) NOT NULL,
    assessment_date DATE NOT NULL,

    -- Inspector info
    inspector_id VARCHAR(20),
    assessment_type VARCHAR(50) DEFAULT 'Daily',  -- Daily, Weekly, Post_Maintenance

    -- Condition metrics
    overall_health_score DECIMAL(4,2),  -- 0-100 scale
    wear_level_percentage DECIMAL(5,2),  -- 0-100%

    -- Specific observations
    tonnage_drift_percentage DECIMAL(5,2),  -- Deviation from nominal
    dimensional_drift_mm DECIMAL(6,3),  -- Part dimension drift
    defect_rate_trend VARCHAR(20),  -- Improving, Stable, Degrading

    -- Mechanical condition
    punch_condition VARCHAR(20),  -- Excellent, Good, Fair, Poor
    die_surface_condition VARCHAR(20),
    alignment_status VARCHAR(20),
    lubrication_status VARCHAR(20),

    -- Predictive signals
    remaining_useful_life_strokes BIGINT,
    days_until_maintenance_recommended INT,
    recommended_action VARCHAR(100),  -- Continue, Monitor_closely, Schedule_maintenance, Immediate_maintenance

    -- Notes
    observations TEXT,
    issues_found TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    FOREIGN KEY (die_id) REFERENCES die_master(die_id)
);

-- Generate daily assessments for active dies over 90 days = ~360 records
INSERT INTO die_condition_assessments (
    die_id, assessment_date, inspector_id, assessment_type,
    overall_health_score, wear_level_percentage, tonnage_drift_percentage,
    dimensional_drift_mm, defect_rate_trend,
    punch_condition, die_surface_condition, alignment_status, lubrication_status,
    remaining_useful_life_strokes, days_until_maintenance_recommended,
    recommended_action, observations
)
-- DIE_DOL_Rev3 assessments (90 days)
SELECT
    'DIE_DOL_Rev3' as die_id,
    (CURRENT_DATE - INTERVAL '90 days')::date + day_num as assessment_date,
    'INSP_' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as inspector_id,
    CASE WHEN day_num % 7 = 0 THEN 'Weekly' ELSE 'Daily' END as assessment_type,

    -- Degrading health over time, with calibration issue on day 45
    CASE
        WHEN day_num = 45 THEN 65.0  -- Calibration issue
        ELSE ROUND((85.0 - (day_num * 0.08) + random() * 5)::numeric, 2)
    END as overall_health_score,

    ROUND((45.0 + (day_num * 0.15) + random() * 3)::numeric, 2) as wear_level_percentage,

    CASE
        WHEN day_num = 45 THEN 8.5  -- Calibration issue
        ELSE ROUND((1.5 + (day_num * 0.02) + random() * 1.5)::numeric, 2)
    END as tonnage_drift_percentage,

    ROUND((0.05 + (day_num * 0.003) + random() * 0.02)::numeric, 3) as dimensional_drift_mm,

    CASE
        WHEN day_num < 45 THEN 'Stable'
        WHEN day_num = 45 THEN 'Degrading'
        WHEN day_num BETWEEN 46 AND 60 THEN 'Degrading'
        ELSE 'Improving'
    END as defect_rate_trend,

    (ARRAY['Good', 'Fair', 'Fair', 'Fair'])[floor(random() * 4 + 1)] as punch_condition,
    (ARRAY['Good', 'Fair', 'Fair'])[floor(random() * 3 + 1)] as die_surface_condition,
    (ARRAY['Good', 'Good', 'Fair'])[floor(random() * 3 + 1)] as alignment_status,
    (ARRAY['Good', 'Good', 'Good', 'Fair'])[floor(random() * 4 + 1)] as lubrication_status,

    (1020000 - (day_num * 1100))::bigint as remaining_useful_life_strokes,
    CASE
        WHEN day_num < 45 THEN (90 - day_num)::int
        WHEN day_num = 45 THEN 0
        ELSE (120 - day_num)::int
    END as days_until_maintenance_recommended,

    CASE
        WHEN day_num < 45 THEN 'Continue'
        WHEN day_num = 45 THEN 'Immediate_maintenance'
        WHEN day_num BETWEEN 46 AND 60 THEN 'Monitor_closely'
        ELSE 'Continue'
    END as recommended_action,

    CASE
        WHEN day_num = 45 THEN 'Significant tonnage drift observed. Springback defects increasing. Recommend immediate calibration.'
        WHEN day_num BETWEEN 46 AND 60 THEN 'Post-calibration monitoring. Defect rate improving.'
        ELSE NULL
    END as observations

FROM generate_series(0, 89) as day_num

UNION ALL

-- DIE_DOR_Rev2 assessments (90 days) - healthier die
SELECT
    'DIE_DOR_Rev2' as die_id,
    (CURRENT_DATE - INTERVAL '90 days')::date + day_num as assessment_date,
    'INSP_' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as inspector_id,
    CASE WHEN day_num % 7 = 0 THEN 'Weekly' ELSE 'Daily' END as assessment_type,

    ROUND((90.0 - (day_num * 0.04) + random() * 4)::numeric, 2) as overall_health_score,
    ROUND((35.0 + (day_num * 0.12) + random() * 3)::numeric, 2) as wear_level_percentage,
    ROUND((0.8 + (day_num * 0.015) + random() * 0.8)::numeric, 2) as tonnage_drift_percentage,
    ROUND((0.03 + (day_num * 0.002) + random() * 0.015)::numeric, 3) as dimensional_drift_mm,

    (ARRAY['Stable', 'Stable', 'Improving'])[floor(random() * 3 + 1)] as defect_rate_trend,

    (ARRAY['Excellent', 'Good', 'Good'])[floor(random() * 3 + 1)] as punch_condition,
    (ARRAY['Excellent', 'Good', 'Good'])[floor(random() * 3 + 1)] as die_surface_condition,
    (ARRAY['Good', 'Good', 'Good'])[floor(random() * 3 + 1)] as alignment_status,
    (ARRAY['Good', 'Good', 'Excellent'])[floor(random() * 3 + 1)] as lubrication_status,

    (880000 - (day_num * 980))::bigint as remaining_useful_life_strokes,
    (150 - day_num)::int as days_until_maintenance_recommended,

    CASE
        WHEN day_num < 75 THEN 'Continue'
        ELSE 'Monitor_closely'
    END as recommended_action,

    NULL as observations

FROM generate_series(0, 89) as day_num

UNION ALL

-- DIE_BO_Rev5 assessments (90 days) - poor condition, wear progression
SELECT
    'DIE_BO_Rev5' as die_id,
    (CURRENT_DATE - INTERVAL '90 days')::date + day_num as assessment_date,
    'INSP_' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as inspector_id,
    CASE WHEN day_num % 7 = 0 THEN 'Weekly' ELSE 'Daily' END as assessment_type,

    -- Degrading significantly in last 20 days
    CASE
        WHEN day_num < 70 THEN ROUND((75.0 - (day_num * 0.15) + random() * 4)::numeric, 2)
        ELSE ROUND((55.0 - ((day_num - 70) * 0.35) + random() * 3)::numeric, 2)
    END as overall_health_score,

    ROUND((50.0 + (day_num * 0.20) + random() * 4)::numeric, 2) as wear_level_percentage,
    ROUND((2.5 + (day_num * 0.04) + random() * 2.0)::numeric, 2) as tonnage_drift_percentage,
    ROUND((0.08 + (day_num * 0.005) + random() * 0.03)::numeric, 3) as dimensional_drift_mm,

    CASE
        WHEN day_num < 70 THEN 'Stable'
        ELSE 'Degrading'
    END as defect_rate_trend,

    CASE
        WHEN day_num < 70 THEN (ARRAY['Good', 'Fair'])[floor(random() * 2 + 1)]
        ELSE (ARRAY['Fair', 'Poor'])[floor(random() * 2 + 1)]
    END as punch_condition,

    CASE
        WHEN day_num < 70 THEN (ARRAY['Fair', 'Fair'])[floor(random() * 2 + 1)]
        ELSE 'Poor'
    END as die_surface_condition,

    (ARRAY['Good', 'Fair', 'Fair'])[floor(random() * 3 + 1)] as alignment_status,
    (ARRAY['Good', 'Fair'])[floor(random() * 2 + 1)] as lubrication_status,

    (850000 - (day_num * 1500))::bigint as remaining_useful_life_strokes,
    CASE
        WHEN day_num < 70 THEN (120 - day_num)::int
        ELSE (15)::int  -- Urgent in last 20 days
    END as days_until_maintenance_recommended,

    CASE
        WHEN day_num < 70 THEN 'Continue'
        WHEN day_num < 85 THEN 'Monitor_closely'
        ELSE 'Schedule_maintenance'
    END as recommended_action,

    CASE
        WHEN day_num >= 70 AND day_num < 80 THEN 'Die wear progression observed. Springback defects increasing. Monitor closely.'
        WHEN day_num >= 80 THEN 'Significant wear detected. Surface degradation evident. Recommend maintenance scheduling.'
        ELSE NULL
    END as observations

FROM generate_series(0, 89) as day_num

UNION ALL

-- DIE_BO_Rev4 assessments (fewer days, since it's backup)
SELECT
    'DIE_BO_Rev4' as die_id,
    (CURRENT_DATE - INTERVAL '90 days')::date + day_num as assessment_date,
    'INSP_' || LPAD((floor(random() * 5 + 1)::int)::text, 2, '0') as inspector_id,
    'Weekly' as assessment_type,

    ROUND((82.0 + random() * 8)::numeric, 2) as overall_health_score,
    ROUND((42.0 + random() * 5)::numeric, 2) as wear_level_percentage,
    ROUND((1.2 + random() * 1.0)::numeric, 2) as tonnage_drift_percentage,
    ROUND((0.04 + random() * 0.02)::numeric, 3) as dimensional_drift_mm,

    'Stable' as defect_rate_trend,

    'Good' as punch_condition,
    'Good' as die_surface_condition,
    'Good' as alignment_status,
    'Good' as lubrication_status,

    (610000)::bigint as remaining_useful_life_strokes,
    (180)::int as days_until_maintenance_recommended,

    'Continue' as recommended_action,

    'Die in storage. Good condition. Ready for production use.' as observations

FROM generate_series(0, 89, 7) as day_num;  -- Weekly assessments only

CREATE INDEX idx_assessment_die_id ON die_condition_assessments(die_id);
CREATE INDEX idx_assessment_date ON die_condition_assessments(assessment_date);
CREATE INDEX idx_assessment_health ON die_condition_assessments(overall_health_score);
CREATE INDEX idx_assessment_action ON die_condition_assessments(recommended_action);

-- ====================================================================
-- VIEWS
-- ====================================================================

CREATE OR REPLACE VIEW die_health_summary AS
SELECT
    dm.die_id,
    dm.part_family,
    dm.health_status,
    dm.current_location,
    dm.total_strokes_count,
    dm.service_life_target_strokes,
    ROUND((dm.total_strokes_count::numeric / dm.service_life_target_strokes * 100), 2) as lifecycle_percentage,
    dca.overall_health_score as latest_health_score,
    dca.wear_level_percentage as latest_wear_level,
    dca.recommended_action as latest_recommendation,
    dm.next_maintenance_due_date
FROM die_master dm
LEFT JOIN LATERAL (
    SELECT * FROM die_condition_assessments
    WHERE die_id = dm.die_id
    ORDER BY assessment_date DESC
    LIMIT 1
) dca ON TRUE
ORDER BY dm.die_id;

CREATE OR REPLACE VIEW changeover_performance_summary AS
SELECT
    press_line_id,
    COUNT(*) as total_changeovers,
    ROUND(AVG(duration_minutes), 2) as avg_duration_minutes,
    ROUND(AVG(smed_target_minutes), 2) as avg_target_minutes,
    ROUND(AVG(smed_variance_minutes), 2) as avg_variance_minutes,
    ROUND((COUNT(*) FILTER (WHERE first_piece_inspection_passed = TRUE)::numeric / COUNT(*) * 100), 2) as first_pass_rate_pct,
    ROUND(AVG(adjustments_required), 2) as avg_adjustments
FROM die_changeover_events
GROUP BY press_line_id;

CREATE OR REPLACE VIEW die_condition_trends AS
SELECT
    die_id,
    DATE_TRUNC('week', assessment_date) as week_start,
    ROUND(AVG(overall_health_score), 2) as avg_health_score,
    ROUND(AVG(wear_level_percentage), 2) as avg_wear_level,
    ROUND(AVG(tonnage_drift_percentage), 2) as avg_tonnage_drift
FROM die_condition_assessments
WHERE assessment_type = 'Daily'
GROUP BY die_id, DATE_TRUNC('week', assessment_date)
ORDER BY die_id, week_start;

COMMENT ON TABLE die_master IS 'Die inventory with lifecycle and maintenance tracking';
COMMENT ON TABLE die_changeover_events IS 'Die changeover events with SMED metrics (~270 events over 90 days)';
COMMENT ON TABLE die_condition_assessments IS 'Daily die condition assessments (~360 records over 90 days)';
COMMENT ON VIEW die_health_summary IS 'Current health status of all dies';
COMMENT ON VIEW changeover_performance_summary IS 'SMED performance by press line';
COMMENT ON VIEW die_condition_trends IS 'Weekly die health trends';
