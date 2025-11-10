{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'springs_production') }}
),

cleaned as (
    select
        id,
        timestamp as production_timestamp,
        line_id,
        machine_id,
        batch_id,
        shift_id,
        operator_id,

        -- Original metrics
        diameter_mm,
        tensile_strength_mpa,
        material,
        compression_ratio,

        -- Quality
        quality_status,
        case
            when quality_status = 'ok' then 1
            when quality_status = 'error' then 0
            else null
        end as quality_flag,

        -- New metrics
        cycle_time_seconds,
        first_pass_yield,
        defect_type,
        rework_required,
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Performance metrics (OEE)
        oee,
        availability,
        performance,
        quality_rate,

        -- Metadata
        created_at,
        _airbyte_emitted_at as loaded_at,

        -- Derived fields
        case
            when diameter_mm < 0.9 then 'small'
            when diameter_mm between 0.9 and 1.2 then 'standard'
            else 'large'
        end as diameter_category,

        case
            when tensile_strength_mpa < 900 then 'low'
            when tensile_strength_mpa between 900 and 1100 then 'medium'
            else 'high'
        end as strength_category,

        case
            when compression_ratio < 0.90 then 'poor'
            when compression_ratio between 0.90 and 0.95 then 'good'
            else 'excellent'
        end as compression_category

    from source
)

select * from cleaned
