
{{ config(materialized='table') }}

WITH audits AS (
    SELECT * FROM {{ ref('stg_radiology_audits') }}
)

SELECT
    final_output AS cat_rating,
    modality,
    body_part_category,
    COUNT(*) AS total_cases,
    ROUND(AVG(quality_score)::numeric, 2) AS avg_quality_score,
    ROUND(AVG(safety_score)::numeric, 2) AS avg_safety_score
FROM audits
GROUP BY final_output, modality, body_part_category
ORDER BY total_cases DESC
