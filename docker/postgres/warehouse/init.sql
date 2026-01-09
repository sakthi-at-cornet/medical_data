-- Legacy schema cleaned up.
-- Medical data is now the primary focus and is handled by medical_init.sql

CREATE SCHEMA IF NOT EXISTS marts;
SET search_path TO marts, public;

-- Dimension: Date/Time (Universal utility)
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

-- Seed date dimension
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

COMMENT ON TABLE marts.dim_date IS 'Date dimension for time-based analysis';
