{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- Defect analysis fact table
-- Comprehensive defect categorization, patterns, and root cause indicators

with all_production as (
    select * from {{ ref('fact_hourly_production_detail') }}
    where defect_type is not null  -- Only records with defects
),

defect_details as (
    select
        production_key,
        date_key,
        hour_key,
        production_timestamp,
        production_hour,
        component_type,
        line_id,
        machine_id,
        batch_id,
        shift_id,
        operator_id,
        material_type,

        -- Defect classification
        defect_type,
        quality_status,
        rework_required,

        -- Impact metrics
        cycle_time_seconds,
        total_cost_per_unit,

        -- Performance impact
        oee,
        availability,
        performance,
        quality_rate,

        -- Environmental conditions at time of defect
        temperature_celsius,
        humidity_percent,

        -- Categorize defect severity based on multiple factors
        CASE
            WHEN rework_required = false AND cycle_time_seconds < 60 THEN 'minor'
            WHEN rework_required = true AND cycle_time_seconds < 90 THEN 'moderate'
            ELSE 'major'
        END as defect_severity,

        -- Defect category grouping
        CASE
            WHEN defect_type IN ('dimension_out_of_spec', 'dimensional', 'dimensional_error')
                THEN 'dimensional'
            WHEN defect_type IN ('material_defect', 'tensile_failure')
                THEN 'material'
            WHEN defect_type IN ('crack', 'surface_defect')
                THEN 'surface'
            WHEN defect_type IN ('machine_calibration', 'compression_failure')
                THEN 'machine'
            ELSE 'other'
        END as defect_category,

        -- Time-based patterns
        EXTRACT(HOUR FROM production_timestamp) as hour_of_day,
        EXTRACT(DOW FROM production_timestamp) as day_of_week,
        CASE
            WHEN EXTRACT(DOW FROM production_timestamp) IN (0, 6) THEN true
            ELSE false
        END as is_weekend,

        loaded_at

    from all_production
),

defect_aggregates as (
    select
        defect_details.*,

        -- Count defects per machine/shift/operator (for pattern detection)
        COUNT(*) OVER (
            PARTITION BY machine_id, shift_id
            ORDER BY production_timestamp
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW  -- 24 hour window
        ) as defects_last_24h_machine_shift,

        COUNT(*) OVER (
            PARTITION BY operator_id
            ORDER BY production_timestamp
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) as defects_last_24h_operator,

        -- Average OEE before defect (indicator of degradation)
        AVG(oee) OVER (
            PARTITION BY machine_id
            ORDER BY production_timestamp
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) as avg_oee_before_defect

    from defect_details
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key([
            'production_key',
            'defect_type'
        ]) }} as defect_key,

        production_key,
        date_key,
        hour_key,

        -- Dimensions
        production_timestamp,
        production_hour,
        component_type,
        line_id,
        machine_id,
        batch_id,
        shift_id,
        operator_id,
        material_type,

        -- Defect classification
        defect_type,
        defect_category,
        defect_severity,
        quality_status,
        rework_required,

        -- Impact metrics
        cycle_time_seconds,
        total_cost_per_unit,
        oee,
        availability,
        performance,
        quality_rate,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Time patterns
        hour_of_day,
        day_of_week,
        is_weekend,
        shift_id as shift_pattern,

        -- Defect concentration indicators (for root cause analysis)
        defects_last_24h_machine_shift,
        defects_last_24h_operator,
        avg_oee_before_defect,

        -- Flags for potential root causes
        CASE
            WHEN defects_last_24h_machine_shift > 5 THEN true
            ELSE false
        END as machine_issue_suspected,

        CASE
            WHEN defects_last_24h_operator > 3 THEN true
            ELSE false
        END as operator_training_needed,

        CASE
            WHEN avg_oee_before_defect < 0.70 THEN true
            ELSE false
        END as degraded_performance_before_defect,

        -- Environmental flags
        CASE
            WHEN component_type = 'bodies'
                 AND material_type = 'bamboo'
                 AND (humidity_percent < 35 OR humidity_percent > 65)
            THEN true
            ELSE false
        END as environmental_factor_suspected,

        loaded_at

    from defect_aggregates
)

select * from final
