{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'bodies_production') }}
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
        durability_score,
        color_match_rating,
        length_mm,
        wall_thickness_mm,
        material,

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
            when durability_score < 70 then 'low'
            when durability_score between 70 and 85 then 'medium'
            else 'high'
        end as durability_category,

        case
            when length_mm < 148 then 'short'
            when length_mm between 148 and 152 then 'standard'
            else 'long'
        end as length_category,

        case
            when material = 'plastic' then 1
            when material = 'bamboo' then 2
            when material = 'metal' then 3
            else null
        end as material_grade

    from source
)

select * from cleaned
