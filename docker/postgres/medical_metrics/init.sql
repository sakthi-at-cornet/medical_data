-- Medical Metrics Database Initialization
-- Primary source for Radiology Audit data

CREATE SCHEMA IF NOT EXISTS medical;

CREATE TABLE IF NOT EXISTS medical.radiology_audits (
    id SERIAL PRIMARY KEY,
    
    -- Case Identification
    case_id VARCHAR(50) UNIQUE NOT NULL,
    sr_no INTEGER,
    
    -- Patient Demographics
    age INTEGER,
    gender VARCHAR(20),
    
    -- Study Details
    modality VARCHAR(50), -- CT, MRI
    study_description TEXT,
    sub_specialty VARCHAR(50), -- Neuroradiology, MSK, Body
    scan_type VARCHAR(100),
    body_part VARCHAR(100),
    body_part_category VARCHAR(50),
    
    -- Timestamps
    scan_date_and_time TIMESTAMP,
    report_date_and_time TIMESTAMP,
    case_upload_date_and_time TIMESTAMP,
    case_assigned_dated_and_time TIMESTAMP,
    review_completed_date_and_time_1 TIMESTAMP,
    time_of_the_day_report_generated TIME,
    
    -- Radiologist Info
    original_radiologist_name VARCHAR(100),
    review_radiologist_name_1 VARCHAR(100),
    
    -- Location & Unit
    unit_identifier VARCHAR(100),
    institute_name VARCHAR(100),
    
    -- Turnaround Times
    assign_tat VARCHAR(50),
    review_tat VARCHAR(50),
    
    -- Quality Audit Questions (Q1-Q17)
    q1 INTEGER,
    q2 INTEGER,
    q3 INTEGER,
    q4 INTEGER,
    q5 INTEGER,
    q6 INTEGER,
    q7 INTEGER,
    q8 INTEGER,
    q9 INTEGER,
    q10 INTEGER,
    q11 INTEGER,
    q12_q INTEGER,
    q12_s INTEGER,
    q13 INTEGER,
    q14 INTEGER,
    q15 INTEGER,
    q16 INTEGER,
    q17 INTEGER,
    
    -- Audit Outcome
    unable_to_audit VARCHAR(10),
    second_review VARCHAR(10),
    required_reaudit VARCHAR(10),
    comments TEXT,
    
    -- Key Scores
    final_output VARCHAR(20), -- CAT1 to CAT5
    safety_score INTEGER,
    quality_score INTEGER,
    productivity_score INTEGER,
    efficiency_score INTEGER,
    star_score INTEGER,
    star INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_audit_case_id ON medical.radiology_audits(case_id);
CREATE INDEX idx_audit_modality ON medical.radiology_audits(modality);
CREATE INDEX idx_audit_final_output ON medical.radiology_audits(final_output);
CREATE INDEX idx_audit_radiologist ON medical.radiology_audits(original_radiologist_name);
CREATE INDEX idx_audit_report_date ON medical.radiology_audits(report_date_and_time);
