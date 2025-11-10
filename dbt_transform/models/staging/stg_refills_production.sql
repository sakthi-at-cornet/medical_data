{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'refills_production') }}
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
        ink_viscosity_pas,
        write_distance_km,
        tip_diameter_mm,
        ink_color,
        flow_consistency,

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
            when ink_viscosity_pas < 1.0 then 'low'
            when ink_viscosity_pas between 1.0 and 1.5 then 'medium'
            else 'high'
        end as viscosity_category,

        case
            when write_distance_km < 2.5 then 'below_spec'
            when write_distance_km between 2.5 and 4.5 then 'within_spec'
            else 'above_spec'
        end as write_distance_category

    from source
)

select * from cleaned
