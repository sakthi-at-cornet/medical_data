
CREATE SCHEMA IF NOT EXISTS medical;

-- Set search path
SET search_path TO medical, public;

-- ============================================
-- RADIOLOGY AUDIT DATA TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS medical.radiology_audits (
    id SERIAL PRIMARY KEY,
    sr_no INTEGER,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Patient Demographics
    age INTEGER,
    gender VARCHAR(10),
    age_cohort VARCHAR(50),
    
    -- Study Information
    modality VARCHAR(20),  -- CT, MRI
    study_description VARCHAR(500),
    sub_specialty VARCHAR(100),  -- Neuro, Body, MSK, Cardiovascular, Multipart
    scan_type VARCHAR(50),
    body_part VARCHAR(200),
    body_part_category VARCHAR(100),  -- NEURO, ABDOMEN/PELVIS, SPINE, MSK, OTHER, HEAD AND NECK, CHEST
    
    -- Timestamps
    scan_date_and_time TIMESTAMP,
    report_date_and_time TIMESTAMP,
    case_upload_date_and_time TIMESTAMP,
    case_assigned_dated_and_time TIMESTAMP,
    review_completed_date_and_time_1 TIMESTAMP,
    
    -- Personnel
    original_radiologist_name VARCHAR(100),
    review_radiologist_name_1 VARCHAR(100),
    time_of_the_day_report_generated VARCHAR(50),
    unit_identifier VARCHAR(50),
    institute_name VARCHAR(200),
    
    -- Turnaround Times
    assign_tat VARCHAR(50),
    review_tat VARCHAR(50),
    
    -- Quality Scores (Q1-Q17)
    q1 DECIMAL(5,2),
    q2 DECIMAL(5,2),
    q3 DECIMAL(5,2),
    q4 DECIMAL(5,2),
    q5 DECIMAL(5,2),
    q6 DECIMAL(5,2),
    q7 DECIMAL(5,2),
    q8 DECIMAL(5,2),
    q9 DECIMAL(5,2),
    q10 DECIMAL(5,2),
    q11 DECIMAL(5,2),
    q12_q DECIMAL(5,2),
    q12_s DECIMAL(5,2),
    q13 DECIMAL(5,2),
    q14 DECIMAL(5,2),
    q15 DECIMAL(5,2),
    q16 DECIMAL(5,2),
    q17 DECIMAL(5,2),
    
    -- Audit Flags
    unable_to_audit VARCHAR(10),
    second_review VARCHAR(10),
    required_reaudit VARCHAR(10),
    comments TEXT,
    
    -- Final Outputs
    final_output VARCHAR(20),  -- CAT1, CAT2, CAT3, CAT4, CAT5
    safety_score DECIMAL(10,6),
    quality_score DECIMAL(10,6),
    productivity_score DECIMAL(10,6),
    efficiency_score DECIMAL(10,6),
    star_score DECIMAL(10,6),
    star INTEGER,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- QUESTION WEIGHTAGE TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS medical.question_weightage (
    id SERIAL PRIMARY KEY,
    question_no VARCHAR(50),
    category VARCHAR(50),  -- SAFETY, QUALITY
    responsibility VARCHAR(50),  -- RADIOLOGIST, DEPARTMENT
    percentage_weightage DECIMAL(5,2)
);

-- ============================================
-- SCORING RUBRIC TABLE  
-- ============================================

CREATE TABLE IF NOT EXISTS medical.scoring_rubric (
    id SERIAL PRIMARY KEY,
    question_no INTEGER,
    actual_question TEXT,
    score_0 INTEGER,
    score_1 INTEGER,
    score_2 INTEGER,
    score_3 INTEGER,
    score_4 INTEGER,
    score_5 INTEGER
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_audits_case_id ON medical.radiology_audits(case_id);
CREATE INDEX IF NOT EXISTS idx_audits_modality ON medical.radiology_audits(modality);
CREATE INDEX IF NOT EXISTS idx_audits_sub_specialty ON medical.radiology_audits(sub_specialty);
CREATE INDEX IF NOT EXISTS idx_audits_final_output ON medical.radiology_audits(final_output);
CREATE INDEX IF NOT EXISTS idx_audits_radiologist ON medical.radiology_audits(original_radiologist_name);
CREATE INDEX IF NOT EXISTS idx_audits_reviewer ON medical.radiology_audits(review_radiologist_name_1);
CREATE INDEX IF NOT EXISTS idx_audits_body_part_category ON medical.radiology_audits(body_part_category);
CREATE INDEX IF NOT EXISTS idx_audits_scan_date ON medical.radiology_audits(scan_date_and_time);
CREATE INDEX IF NOT EXISTS idx_audits_star ON medical.radiology_audits(star);

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Quality by Modality
CREATE OR REPLACE VIEW medical.v_quality_by_modality AS
SELECT 
    modality,
    COUNT(*) as total_cases,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
    ROUND(AVG(safety_score)::numeric, 2) as avg_safety_score,
    ROUND(AVG(star_score)::numeric, 2) as avg_star_score,
    COUNT(CASE WHEN final_output = 'CAT5' THEN 1 END) as cat5_count,
    COUNT(CASE WHEN final_output = 'CAT4' THEN 1 END) as cat4_count,
    COUNT(CASE WHEN final_output = 'CAT3' THEN 1 END) as cat3_count,
    COUNT(CASE WHEN final_output = 'CAT2' THEN 1 END) as cat2_count,
    COUNT(CASE WHEN final_output = 'CAT1' THEN 1 END) as cat1_count
FROM medical.radiology_audits
GROUP BY modality;

-- Quality by Body Part Category
CREATE OR REPLACE VIEW medical.v_quality_by_body_part AS
SELECT 
    body_part_category,
    COUNT(*) as total_cases,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
    ROUND(AVG(safety_score)::numeric, 2) as avg_safety_score,
    ROUND(AVG(star)::numeric, 2) as avg_star_rating
FROM medical.radiology_audits
WHERE body_part_category IS NOT NULL
GROUP BY body_part_category
ORDER BY avg_quality_score DESC;

-- Radiologist Performance
CREATE OR REPLACE VIEW medical.v_radiologist_performance AS
SELECT 
    original_radiologist_name as radiologist,
    COUNT(*) as total_cases,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
    ROUND(AVG(safety_score)::numeric, 2) as avg_safety_score,
    ROUND(AVG(star)::numeric, 2) as avg_star_rating,
    COUNT(CASE WHEN final_output IN ('CAT4', 'CAT5') THEN 1 END) as high_quality_cases,
    ROUND(COUNT(CASE WHEN final_output IN ('CAT4', 'CAT5') THEN 1 END) * 100.0 / COUNT(*)::numeric, 2) as high_quality_pct
FROM medical.radiology_audits
WHERE original_radiologist_name IS NOT NULL
GROUP BY original_radiologist_name
ORDER BY avg_quality_score DESC;

-- Reviewer Performance
CREATE OR REPLACE VIEW medical.v_reviewer_performance AS
SELECT 
    review_radiologist_name_1 as reviewer,
    COUNT(*) as total_reviews,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
    COUNT(CASE WHEN required_reaudit = 'Yes' THEN 1 END) as reaudit_flagged
FROM medical.radiology_audits
WHERE review_radiologist_name_1 IS NOT NULL
GROUP BY review_radiologist_name_1
ORDER BY total_reviews DESC;

-- CAT Distribution
CREATE OR REPLACE VIEW medical.v_cat_distribution AS
SELECT 
    final_output as category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()::numeric, 2) as percentage
FROM medical.radiology_audits
WHERE final_output IS NOT NULL
GROUP BY final_output
ORDER BY final_output;

-- Sub-specialty Performance
CREATE OR REPLACE VIEW medical.v_subspecialty_performance AS
SELECT 
    sub_specialty,
    COUNT(*) as total_cases,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
    ROUND(AVG(safety_score)::numeric, 2) as avg_safety_score,
    ROUND(AVG(star)::numeric, 2) as avg_star_rating
FROM medical.radiology_audits
WHERE sub_specialty IS NOT NULL
GROUP BY sub_specialty
ORDER BY avg_quality_score DESC;

-- Star Rating Distribution
CREATE OR REPLACE VIEW medical.v_star_distribution AS
SELECT 
    star as star_rating,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()::numeric, 2) as percentage
FROM medical.radiology_audits
WHERE star IS NOT NULL
GROUP BY star
ORDER BY star DESC;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON SCHEMA medical IS 'Medical radiology audit data schema';
COMMENT ON TABLE medical.radiology_audits IS 'Main radiology audit records with quality scores and CAT ratings';
COMMENT ON VIEW medical.v_quality_by_modality IS 'Quality metrics grouped by imaging modality (CT/MRI)';
COMMENT ON VIEW medical.v_radiologist_performance IS 'Performance metrics for each radiologist';
COMMENT ON VIEW medical.v_cat_distribution IS 'Distribution of CAT categories';
