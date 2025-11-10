-- Data Warehouse Schema
-- Central repository for manufacturing data from all source systems

-- Create schemas for different layers
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Set search path
SET search_path TO raw, staging, marts, public;

-- ============================================
-- RAW LAYER: Direct copies from source systems
-- ============================================

-- Raw refills data (will be populated by Airbyte)
CREATE TABLE IF NOT EXISTS raw.refills_production (
    id INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE,
    line_id VARCHAR(50),
    batch_id VARCHAR(100),
    ink_viscosity_pas DECIMAL(5,2),
    write_distance_km DECIMAL(5,2),
    tip_diameter_mm DECIMAL(4,2),
    ink_color VARCHAR(20),
    flow_consistency DECIMAL(5,3),
    quality_status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE,
    _airbyte_ab_id VARCHAR(256),
    _airbyte_emitted_at TIMESTAMP WITH TIME ZONE,
    _airbyte_normalized_at TIMESTAMP WITH TIME ZONE
);

-- Raw bodies data (will be populated by Airbyte)
CREATE TABLE IF NOT EXISTS raw.bodies_production (
    id INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE,
    line_id VARCHAR(50),
    batch_id VARCHAR(100),
    durability_score DECIMAL(5,1),
    color_match_rating DECIMAL(5,3),
    length_mm DECIMAL(6,2),
    wall_thickness_mm DECIMAL(4,2),
    material VARCHAR(50),
    quality_status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE,
    _airbyte_ab_id VARCHAR(256),
    _airbyte_emitted_at TIMESTAMP WITH TIME ZONE,
    _airbyte_normalized_at TIMESTAMP WITH TIME ZONE
);

-- Raw springs data (will be populated by Airbyte)
CREATE TABLE IF NOT EXISTS raw.springs_production (
    id INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE,
    line_id VARCHAR(50),
    batch_id VARCHAR(100),
    diameter_mm DECIMAL(4,2),
    tensile_strength_mpa DECIMAL(6,1),
    material VARCHAR(50),
    compression_ratio DECIMAL(5,3),
    quality_status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE,
    _airbyte_ab_id VARCHAR(256),
    _airbyte_emitted_at TIMESTAMP WITH TIME ZONE,
    _airbyte_normalized_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- STAGING LAYER: Cleaned and standardized
-- (Will be populated by dbt)
-- ============================================

-- Staging tables will be created by dbt
-- Placeholder comments for expected tables:
-- staging.stg_refills_production
-- staging.stg_bodies_production
-- staging.stg_springs_production

-- ============================================
-- MARTS LAYER: Business-ready dimensional models
-- (Will be populated by dbt)
-- ============================================

-- Dimension: Date/Time
CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL
);

-- Dimension: Production Line
CREATE TABLE IF NOT EXISTS marts.dim_production_line (
    line_key SERIAL PRIMARY KEY,
    line_id VARCHAR(50) NOT NULL UNIQUE,
    line_type VARCHAR(50) NOT NULL, -- refills, bodies, springs
    line_number INTEGER NOT NULL,
    capacity_per_hour INTEGER,
    installation_date DATE,
    status VARCHAR(20) DEFAULT 'active'
);

-- Dimension: Material
CREATE TABLE IF NOT EXISTS marts.dim_material (
    material_key SERIAL PRIMARY KEY,
    material_name VARCHAR(50) NOT NULL UNIQUE,
    material_category VARCHAR(50) NOT NULL,
    cost_per_unit DECIMAL(10,2),
    supplier VARCHAR(100)
);

-- Dimension: Batch
CREATE TABLE IF NOT EXISTS marts.dim_batch (
    batch_key SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL UNIQUE,
    component_type VARCHAR(50) NOT NULL, -- refills, bodies, springs
    planned_quantity INTEGER,
    start_date DATE,
    end_date DATE
);

-- Fact: Production Quality Metrics
CREATE TABLE IF NOT EXISTS marts.fact_production_quality (
    quality_key SERIAL PRIMARY KEY,
    date_key INTEGER REFERENCES marts.dim_date(date_key),
    line_key INTEGER REFERENCES marts.dim_production_line(line_key),
    batch_key INTEGER REFERENCES marts.dim_batch(batch_key),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    total_units INTEGER NOT NULL,
    passed_units INTEGER NOT NULL,
    failed_units INTEGER NOT NULL,
    pass_rate DECIMAL(5,2) NOT NULL,
    avg_quality_score DECIMAL(8,2)
);

-- ============================================
-- INDEXES for performance
-- ============================================

-- Raw layer indexes
CREATE INDEX IF NOT EXISTS idx_raw_refills_timestamp ON raw.refills_production(timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_bodies_timestamp ON raw.bodies_production(timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_springs_timestamp ON raw.springs_production(timestamp);

-- Marts layer indexes
CREATE INDEX IF NOT EXISTS idx_fact_quality_date ON marts.fact_production_quality(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_quality_line ON marts.fact_production_quality(line_key);
CREATE INDEX IF NOT EXISTS idx_fact_quality_batch ON marts.fact_production_quality(batch_key);
CREATE INDEX IF NOT EXISTS idx_fact_quality_timestamp ON marts.fact_production_quality(timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_quality_component ON marts.fact_production_quality(component_type);

-- ============================================
-- SEED DATA for dimensions
-- ============================================

-- Seed production lines
INSERT INTO marts.dim_production_line (line_id, line_type, line_number, capacity_per_hour, installation_date, status)
VALUES
    ('LINE-REFILLS-001', 'refills', 1, 1200, '2023-01-15', 'active'),
    ('LINE-REFILLS-002', 'refills', 2, 1200, '2023-01-15', 'active'),
    ('LINE-BODIES-001', 'bodies', 1, 800, '2023-02-01', 'active'),
    ('LINE-BODIES-002', 'bodies', 2, 800, '2023-02-01', 'active'),
    ('LINE-SPRINGS-001', 'springs', 1, 1500, '2023-01-10', 'active'),
    ('LINE-SPRINGS-002', 'springs', 2, 1500, '2023-01-10', 'active'),
    ('LINE-SPRINGS-003', 'springs', 3, 1500, '2023-01-10', 'active')
ON CONFLICT (line_id) DO NOTHING;

-- Seed materials
INSERT INTO marts.dim_material (material_name, material_category, cost_per_unit, supplier)
VALUES
    ('plastic', 'body_material', 0.15, 'PlasticCorp Inc'),
    ('bamboo', 'body_material', 0.25, 'EcoMaterials Ltd'),
    ('metal', 'body_material', 0.45, 'MetalWorks Co'),
    ('stainless_steel', 'spring_material', 0.08, 'SteelSupply Inc'),
    ('music_wire', 'spring_material', 0.12, 'WirePro LLC'),
    ('chrome_vanadium', 'spring_material', 0.10, 'ChromeTech Ltd'),
    ('black_ink', 'refill_material', 0.05, 'InkMasters'),
    ('blue_ink', 'refill_material', 0.05, 'InkMasters'),
    ('red_ink', 'refill_material', 0.06, 'InkMasters'),
    ('green_ink', 'refill_material', 0.06, 'ColorInk Co'),
    ('purple_ink', 'refill_material', 0.07, 'ColorInk Co')
ON CONFLICT (material_name) DO NOTHING;

-- Seed date dimension (basic - will be expanded by dbt)
INSERT INTO marts.dim_date (date_key, date, year, quarter, month, month_name, week, day_of_month, day_of_week, day_name, is_weekend, is_holiday)
SELECT
    TO_CHAR(date, 'YYYYMMDD')::INTEGER as date_key,
    date::DATE,
    EXTRACT(YEAR FROM date)::INTEGER as year,
    EXTRACT(QUARTER FROM date)::INTEGER as quarter,
    EXTRACT(MONTH FROM date)::INTEGER as month,
    TO_CHAR(date, 'Month') as month_name,
    EXTRACT(WEEK FROM date)::INTEGER as week,
    EXTRACT(DAY FROM date)::INTEGER as day_of_month,
    EXTRACT(DOW FROM date)::INTEGER as day_of_week,
    TO_CHAR(date, 'Day') as day_name,
    EXTRACT(DOW FROM date) IN (0, 6) as is_weekend,
    FALSE as is_holiday
FROM generate_series(
    '2024-01-01'::DATE,
    '2025-12-31'::DATE,
    '1 day'::INTERVAL
) as date
ON CONFLICT (date_key) DO NOTHING;

-- ============================================
-- UTILITY VIEWS
-- ============================================

-- Cross-component quality overview
CREATE OR REPLACE VIEW marts.v_overall_quality AS
SELECT
    pl.line_type as component_type,
    COUNT(*) as total_records,
    SUM(fq.passed_units) as total_passed,
    SUM(fq.failed_units) as total_failed,
    ROUND(AVG(fq.pass_rate)::numeric, 2) as avg_pass_rate
FROM marts.fact_production_quality fq
JOIN marts.dim_production_line pl ON fq.line_key = pl.line_key
GROUP BY pl.line_type;

-- Recent production summary
CREATE OR REPLACE VIEW marts.v_recent_production AS
SELECT
    dd.date,
    pl.line_id,
    pl.line_type,
    SUM(fq.total_units) as total_units,
    SUM(fq.passed_units) as passed_units,
    SUM(fq.failed_units) as failed_units,
    ROUND(AVG(fq.pass_rate)::numeric, 2) as avg_pass_rate
FROM marts.fact_production_quality fq
JOIN marts.dim_date dd ON fq.date_key = dd.date_key
JOIN marts.dim_production_line pl ON fq.line_key = pl.line_key
WHERE dd.date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY dd.date, pl.line_id, pl.line_type
ORDER BY dd.date DESC, pl.line_id;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON SCHEMA raw IS 'Raw data layer - direct copies from source systems via Airbyte';
COMMENT ON SCHEMA staging IS 'Staging layer - cleaned and standardized data via dbt';
COMMENT ON SCHEMA marts IS 'Business marts layer - dimensional models for analytics';

COMMENT ON TABLE marts.dim_date IS 'Date dimension for time-based analysis';
COMMENT ON TABLE marts.dim_production_line IS 'Production line master data';
COMMENT ON TABLE marts.dim_material IS 'Material master data with costs';
COMMENT ON TABLE marts.dim_batch IS 'Production batch tracking';
COMMENT ON TABLE marts.fact_production_quality IS 'Production quality metrics fact table';

COMMENT ON VIEW marts.v_overall_quality IS 'Cross-component quality summary';
COMMENT ON VIEW marts.v_recent_production IS 'Last 7 days production summary by line';

-- ============================================
-- AUTOMOTIVE MATERIAL COIL TRACKING (Phase 1.4)
-- ============================================

-- Supplier Master Table
CREATE TABLE IF NOT EXISTS marts.supplier_master (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL,
    country VARCHAR(100),
    material_specialization TEXT,
    quality_certification VARCHAR(100),  -- ISO9001, TS16949, etc.

    -- Quality scorecards
    quality_score_overall DECIMAL(4,2),  -- 0-100 scale
    on_time_delivery_rate DECIMAL(5,2),  -- Percentage
    defect_rate_ppm DECIMAL(8,2),  -- Parts per million

    -- Contact
    contact_person VARCHAR(100),
    contact_email VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- active, suspended, inactive
    last_audit_date DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert 3 suppliers
INSERT INTO marts.supplier_master (
    supplier_id, supplier_name, country, material_specialization, quality_certification,
    quality_score_overall, on_time_delivery_rate, defect_rate_ppm,
    contact_person, contact_email, status, last_audit_date
) VALUES
    ('JSW_Steel', 'JSW Steel Limited', 'India', 'Cold Rolled Steel (CRS_SPCC)',
     'ISO9001:2015, TS16949', 92.5, 95.8, 245.0,
     'Rajesh Kumar', 'rajesh.k@jswsteel.in', 'active', '2024-09-15'),

    ('NIPPON_Steel', 'Nippon Steel Corporation', 'Japan', 'High Strength Steel (DP600)',
     'ISO9001:2015, TS16949, ISO14001', 96.2, 98.5, 120.0,
     'Takeshi Yamamoto', 'takeshi.y@nipponsteel.com', 'active', '2024-08-20'),

    ('SAIL_Steel', 'Steel Authority of India Limited', 'India', 'High Strength Low Alloy (HSLA_350)',
     'ISO9001:2015, TS16949', 88.3, 92.0, 380.0,
     'Amit Sharma', 'amit.s@sail.in', 'active', '2024-10-05')
ON CONFLICT (supplier_id) DO NOTHING;

-- Material Coils Table
CREATE TABLE IF NOT EXISTS marts.material_coils (
    coil_id VARCHAR(100) PRIMARY KEY,
    supplier_id VARCHAR(50) NOT NULL,
    material_grade VARCHAR(50) NOT NULL,  -- CRS_SPCC, HSLA_350, DP600

    -- Physical properties
    thickness_nominal DECIMAL(5,3) NOT NULL,  -- 0.8mm
    width_mm DECIMAL(7,2),  -- Coil width
    weight_kg DECIMAL(10,2),  -- Coil weight

    -- Material certification data (from mill cert)
    yield_strength_mpa DECIMAL(6,1),  -- Yield strength
    tensile_strength_mpa DECIMAL(6,1),  -- Ultimate tensile strength
    elongation_percentage DECIMAL(5,2),  -- Ductility
    hardness_hv DECIMAL(5,1),  -- Vickers hardness
    carbon_content_percentage DECIMAL(4,3),

    -- Traceability
    heat_number VARCHAR(50),  -- Steel heat/batch number
    mill_test_certificate_number VARCHAR(100),

    -- Lifecycle dates
    manufactured_date DATE,
    received_date DATE,
    inspection_date DATE,
    inspection_status VARCHAR(20) DEFAULT 'pending',  -- pending, passed, failed
    mounted_date DATE,  -- When coil was mounted on press line
    exhausted_date DATE,  -- When coil was fully consumed

    -- Usage tracking
    parts_produced INT DEFAULT 0,
    scrap_count INT DEFAULT 0,
    remaining_weight_kg DECIMAL(10,2),

    -- Quality metrics (calculated from parts produced)
    avg_defect_rate DECIMAL(5,3),
    springback_issues INT DEFAULT 0,
    surface_defects INT DEFAULT 0,

    -- Notes
    quality_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    FOREIGN KEY (supplier_id) REFERENCES marts.supplier_master(supplier_id)
);

-- Generate ~126 coil records (54 for doors, 72 for bonnets)
-- 54 coils for doors (JSW Steel - CRS_SPCC) - consumed every ~40 parts
INSERT INTO marts.material_coils (
    coil_id, supplier_id, material_grade,
    thickness_nominal, width_mm, weight_kg,
    yield_strength_mpa, tensile_strength_mpa, elongation_percentage, hardness_hv, carbon_content_percentage,
    heat_number, mill_test_certificate_number,
    manufactured_date, received_date, inspection_date, inspection_status, mounted_date,
    parts_produced, scrap_count, remaining_weight_kg,
    avg_defect_rate, springback_issues, surface_defects,
    quality_notes
)
SELECT
    'COIL_JSW_' || LPAD(coil_num::text, 4, '0') as coil_id,
    'JSW_Steel' as supplier_id,
    'CRS_SPCC' as material_grade,

    0.800 as thickness_nominal,
    ROUND((1050 + random() * 20)::numeric, 2) as width_mm,
    ROUND((2200 + random() * 200)::numeric, 2) as weight_kg,

    -- Material properties (CRS_SPCC typical values)
    ROUND((180 + random() * 20)::numeric, 1) as yield_strength_mpa,
    ROUND((310 + random() * 30)::numeric, 1) as tensile_strength_mpa,
    ROUND((38 + random() * 4)::numeric, 2) as elongation_percentage,
    ROUND((140 + random() * 20)::numeric, 1) as hardness_hv,
    ROUND((0.06 + random() * 0.02)::numeric, 3) as carbon_content_percentage,

    'HEAT_JSW_' || TO_CHAR((CURRENT_DATE - INTERVAL '180 days') + (coil_num * 2 * INTERVAL '1 day'), 'YYYYMMDD') ||
        '_' || LPAD((floor(random() * 9999)::int)::text, 4, '0') as heat_number,
    'MTC_JSW_2024_' || LPAD((10000 + coil_num)::text, 6, '0') as mill_test_certificate_number,

    (CURRENT_DATE - INTERVAL '180 days') + (coil_num * 2 * INTERVAL '1 day') as manufactured_date,
    (CURRENT_DATE - INTERVAL '175 days') + (coil_num * 2 * INTERVAL '1 day') as received_date,
    (CURRENT_DATE - INTERVAL '174 days') + (coil_num * 2 * INTERVAL '1 day') as inspection_date,
    'passed' as inspection_status,
    (CURRENT_DATE - INTERVAL '173 days') + (coil_num * 2 * INTERVAL '1 day') as mounted_date,

    40 + floor(random() * 10)::int as parts_produced,
    floor(random() * 3)::int as scrap_count,
    ROUND((50 + random() * 100)::numeric, 2) as remaining_weight_kg,

    -- Quality metrics - coils 15-17 have higher defect rates (per anomaly plan)
    CASE
        WHEN coil_num BETWEEN 15 AND 17 THEN ROUND((0.065 + random() * 0.025)::numeric, 3)
        ELSE ROUND((0.022 + random() * 0.015)::numeric, 3)
    END as avg_defect_rate,

    CASE
        WHEN coil_num BETWEEN 15 AND 17 THEN floor(random() * 5 + 3)::int
        ELSE floor(random() * 2)::int
    END as springback_issues,

    floor(random() * 2)::int as surface_defects,

    CASE
        WHEN coil_num BETWEEN 15 AND 17 THEN 'Higher yield strength batch. Increased springback defects observed. Supplier notified.'
        ELSE NULL
    END as quality_notes

FROM generate_series(0, 53) as coil_num;

-- 72 coils for bonnets (70% SAIL HSLA, 30% NIPPON DP600) - consumed every ~30 parts
INSERT INTO marts.material_coils (
    coil_id, supplier_id, material_grade,
    thickness_nominal, width_mm, weight_kg,
    yield_strength_mpa, tensile_strength_mpa, elongation_percentage, hardness_hv, carbon_content_percentage,
    heat_number, mill_test_certificate_number,
    manufactured_date, received_date, inspection_date, inspection_status, mounted_date,
    parts_produced, scrap_count, remaining_weight_kg,
    avg_defect_rate, springback_issues, surface_defects,
    quality_notes
)
SELECT
    'COIL_' || CASE WHEN random() < 0.7 THEN 'SAIL_HSLA' ELSE 'NIPPON_DP600' END || '_' ||
        LPAD(coil_num::text, 4, '0') as coil_id,
    CASE WHEN random() < 0.7 THEN 'SAIL_Steel' ELSE 'NIPPON_Steel' END as supplier_id,
    CASE WHEN random() < 0.7 THEN 'HSLA_350' ELSE 'DP600' END as material_grade,

    0.800 as thickness_nominal,
    ROUND((1200 + random() * 30)::numeric, 2) as width_mm,
    ROUND((2800 + random() * 300)::numeric, 2) as weight_kg,

    -- Material properties vary by grade
    CASE
        WHEN random() < 0.7 THEN ROUND((350 + random() * 30)::numeric, 1)  -- HSLA_350
        ELSE ROUND((600 + random() * 40)::numeric, 1)  -- DP600
    END as yield_strength_mpa,

    CASE
        WHEN random() < 0.7 THEN ROUND((480 + random() * 40)::numeric, 1)  -- HSLA_350
        ELSE ROUND((950 + random() * 50)::numeric, 1)  -- DP600
    END as tensile_strength_mpa,

    CASE
        WHEN random() < 0.7 THEN ROUND((22 + random() * 4)::numeric, 2)  -- HSLA_350 (lower ductility)
        ELSE ROUND((18 + random() * 3)::numeric, 2)  -- DP600 (even lower)
    END as elongation_percentage,

    CASE
        WHEN random() < 0.7 THEN ROUND((180 + random() * 30)::numeric, 1)  -- HSLA_350
        ELSE ROUND((240 + random() * 40)::numeric, 1)  -- DP600
    END as hardness_hv,

    CASE
        WHEN random() < 0.7 THEN ROUND((0.08 + random() * 0.03)::numeric, 3)  -- HSLA_350
        ELSE ROUND((0.14 + random() * 0.03)::numeric, 3)  -- DP600
    END as carbon_content_percentage,

    'HEAT_' || CASE WHEN random() < 0.7 THEN 'SAIL' ELSE 'NIPPON' END || '_' ||
        TO_CHAR((CURRENT_DATE - INTERVAL '180 days') + (coil_num * 1.5 * INTERVAL '1 day'), 'YYYYMMDD') ||
        '_' || LPAD((floor(random() * 9999)::int)::text, 4, '0') as heat_number,

    'MTC_' || CASE WHEN random() < 0.7 THEN 'SAIL' ELSE 'NIPPON' END || '_2024_' ||
        LPAD((20000 + coil_num)::text, 6, '0') as mill_test_certificate_number,

    (CURRENT_DATE - INTERVAL '180 days') + (coil_num * 1.5 * INTERVAL '1 day') as manufactured_date,
    (CURRENT_DATE - INTERVAL '175 days') + (coil_num * 1.5 * INTERVAL '1 day') as received_date,
    (CURRENT_DATE - INTERVAL '174 days') + (coil_num * 1.5 * INTERVAL '1 day') as inspection_date,
    'passed' as inspection_status,
    (CURRENT_DATE - INTERVAL '173 days') + (coil_num * 1.5 * INTERVAL '1 day') as mounted_date,

    30 + floor(random() * 8)::int as parts_produced,
    floor(random() * 4)::int as scrap_count,  -- Higher scrap for deep draw
    ROUND((60 + random() * 120)::numeric, 2) as remaining_weight_kg,

    -- Bonnets have higher defect rate overall
    ROUND((0.045 + random() * 0.025)::numeric, 3) as avg_defect_rate,
    floor(random() * 3)::int as springback_issues,
    floor(random() * 4 + 1)::int as surface_defects,

    NULL as quality_notes

FROM generate_series(0, 71) as coil_num;

CREATE INDEX idx_coils_supplier ON marts.material_coils(supplier_id);
CREATE INDEX idx_coils_material_grade ON marts.material_coils(material_grade);
CREATE INDEX idx_coils_received_date ON marts.material_coils(received_date);
CREATE INDEX idx_coils_inspection_status ON marts.material_coils(inspection_status);

-- ============================================
-- VIEWS FOR MATERIAL TRACKING
-- ============================================

CREATE OR REPLACE VIEW marts.v_supplier_quality_scorecard AS
SELECT
    sm.supplier_id,
    sm.supplier_name,
    sm.material_specialization,
    sm.quality_score_overall as supplier_overall_score,
    sm.defect_rate_ppm as supplier_target_ppm,

    COUNT(mc.coil_id) as total_coils_supplied,
    SUM(mc.parts_produced) as total_parts_produced,
    SUM(mc.scrap_count) as total_scrap_parts,
    ROUND(AVG(mc.avg_defect_rate) * 100, 2) as actual_defect_rate_pct,
    SUM(mc.springback_issues) as total_springback_issues,
    SUM(mc.surface_defects) as total_surface_defects,

    ROUND(AVG(mc.yield_strength_mpa), 1) as avg_yield_strength_mpa,
    ROUND(AVG(mc.tensile_strength_mpa), 1) as avg_tensile_strength_mpa,
    ROUND(AVG(mc.elongation_percentage), 2) as avg_elongation_pct

FROM marts.supplier_master sm
LEFT JOIN marts.material_coils mc ON sm.supplier_id = mc.supplier_id
GROUP BY sm.supplier_id, sm.supplier_name, sm.material_specialization,
         sm.quality_score_overall, sm.defect_rate_ppm
ORDER BY sm.supplier_id;

CREATE OR REPLACE VIEW marts.v_coil_traceability AS
SELECT
    mc.coil_id,
    mc.supplier_id,
    sm.supplier_name,
    mc.material_grade,
    mc.heat_number,
    mc.mill_test_certificate_number,
    mc.manufactured_date,
    mc.received_date,
    mc.mounted_date,
    mc.parts_produced,
    mc.scrap_count,
    ROUND((mc.scrap_count::numeric / NULLIF(mc.parts_produced, 0) * 100), 2) as scrap_rate_pct,
    mc.avg_defect_rate,
    mc.springback_issues,
    mc.surface_defects,
    mc.yield_strength_mpa,
    mc.tensile_strength_mpa,
    mc.quality_notes
FROM marts.material_coils mc
JOIN marts.supplier_master sm ON mc.supplier_id = sm.supplier_id
ORDER BY mc.received_date DESC;

CREATE OR REPLACE VIEW marts.v_material_grade_comparison AS
SELECT
    material_grade,
    COUNT(*) as total_coils,
    SUM(parts_produced) as total_parts,
    ROUND(AVG(avg_defect_rate) * 100, 3) as avg_defect_rate_pct,
    ROUND(AVG(yield_strength_mpa), 1) as avg_yield_strength_mpa,
    ROUND(AVG(tensile_strength_mpa), 1) as avg_tensile_strength_mpa,
    ROUND(AVG(elongation_percentage), 2) as avg_elongation_pct,
    ROUND(AVG(hardness_hv), 1) as avg_hardness_hv
FROM marts.material_coils
GROUP BY material_grade
ORDER BY material_grade;

COMMENT ON TABLE marts.supplier_master IS 'Supplier master data with quality scorecards';
COMMENT ON TABLE marts.material_coils IS 'Material coil tracking with traceability and genealogy (~126 coils)';
COMMENT ON VIEW marts.v_supplier_quality_scorecard IS 'Supplier quality performance scorecard';
COMMENT ON VIEW marts.v_coil_traceability IS 'Full coil-to-part traceability with quality metrics';
COMMENT ON VIEW marts.v_material_grade_comparison IS 'Comparison of material grades performance';

-- ============================================
-- FOREIGN DATA WRAPPERS FOR CROSS-DATABASE ACCESS
-- ============================================

-- Enable postgres_fdw extension
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Create foreign servers for press line databases
CREATE SERVER IF NOT EXISTS press_line_a_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'postgres-press-line-a', port '5432', dbname 'press_line_a');

CREATE SERVER IF NOT EXISTS press_line_b_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'postgres-press-line-b', port '5432', dbname 'press_line_b');

CREATE SERVER IF NOT EXISTS die_management_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'postgres-die-management', port '5432', dbname 'die_management');

-- Create user mappings
CREATE USER MAPPING IF NOT EXISTS FOR warehouse_user
    SERVER press_line_a_server
    OPTIONS (user 'press_a_user', password 'press_a_pass');

CREATE USER MAPPING IF NOT EXISTS FOR warehouse_user
    SERVER press_line_b_server
    OPTIONS (user 'press_b_user', password 'press_b_pass');

CREATE USER MAPPING IF NOT EXISTS FOR warehouse_user
    SERVER die_management_server
    OPTIONS (user 'die_mgmt_user', password 'die_mgmt_pass');

-- Import foreign tables into raw schema
IMPORT FOREIGN SCHEMA public LIMIT TO (press_line_a_production)
    FROM SERVER press_line_a_server INTO raw;

IMPORT FOREIGN SCHEMA public LIMIT TO (press_line_b_production)
    FROM SERVER press_line_b_server INTO raw;

IMPORT FOREIGN SCHEMA public LIMIT TO (die_master, die_changeover_events, die_condition_assessments)
    FROM SERVER die_management_server INTO raw;

COMMENT ON FOREIGN TABLE raw.press_line_a_production IS 'Foreign table from Press Line A database';
COMMENT ON FOREIGN TABLE raw.press_line_b_production IS 'Foreign table from Press Line B database';
COMMENT ON FOREIGN TABLE raw.die_master IS 'Foreign table from Die Management database';
COMMENT ON FOREIGN TABLE raw.die_changeover_events IS 'Foreign table from Die Management database';
COMMENT ON FOREIGN TABLE raw.die_condition_assessments IS 'Foreign table from Die Management database';
