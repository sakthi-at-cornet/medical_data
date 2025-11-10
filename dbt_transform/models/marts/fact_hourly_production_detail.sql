{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- Hourly-level production detail with all dimensions and metrics
-- Enables deep analysis of production patterns, OEE, costs, and environmental factors

with refills_hourly as (
    select
        production_timestamp,
        DATE_TRUNC('hour', production_timestamp) as production_hour,
        line_id,
        machine_id,
        batch_id,
        shift_id,
        operator_id,
        'refills' as component_type,

        -- Quality metrics
        quality_status,
        quality_flag,
        defect_type,
        first_pass_yield,
        rework_required,

        -- Performance metrics
        cycle_time_seconds,
        oee,
        availability,
        performance,
        quality_rate,

        -- Cost metrics
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        (material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit) as total_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Component-specific metrics
        ink_viscosity_pas as metric_1,
        write_distance_km as metric_2,
        tip_diameter_mm as metric_3,
        NULL::decimal as metric_4,
        NULL::varchar as material_type,

        loaded_at

    from {{ source('raw', 'refills_production') }}
),

bodies_hourly as (
    select
        production_timestamp,
        DATE_TRUNC('hour', production_timestamp) as production_hour,
        line_id,
        machine_id,
        batch_id,
        shift_id,
        operator_id,
        'bodies' as component_type,

        -- Quality metrics
        quality_status,
        quality_flag,
        defect_type,
        first_pass_yield,
        rework_required,

        -- Performance metrics
        cycle_time_seconds,
        oee,
        availability,
        performance,
        quality_rate,

        -- Cost metrics
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        (material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit) as total_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Component-specific metrics
        durability_score as metric_1,
        CAST(color_match_rating AS DOUBLE PRECISION) as metric_2,
        length_mm as metric_3,
        wall_thickness_mm as metric_4,
        material as material_type,

        loaded_at

    from {{ source('raw', 'bodies_production') }}
),

springs_hourly as (
    select
        production_timestamp,
        DATE_TRUNC('hour', production_timestamp) as production_hour,
        line_id,
        machine_id,
        batch_id,
        shift_id,
        operator_id,
        'springs' as component_type,

        -- Quality metrics
        quality_status,
        quality_flag,
        defect_type,
        first_pass_yield,
        rework_required,

        -- Performance metrics
        cycle_time_seconds,
        oee,
        availability,
        performance,
        quality_rate,

        -- Cost metrics
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        (material_cost_per_unit + labor_cost_per_unit + energy_cost_per_unit) as total_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Component-specific metrics
        diameter_mm as metric_1,
        tensile_strength_mpa as metric_2,
        CAST(compression_ratio AS DOUBLE PRECISION) as metric_3,
        NULL::decimal as metric_4,
        material as material_type,

        loaded_at

    from {{ source('raw', 'springs_production') }}
),

combined as (
    select * from refills_hourly
    union all
    select * from bodies_hourly
    union all
    select * from springs_hourly
),

final as (
    select
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key([
            'component_type',
            'line_id',
            'machine_id',
            'batch_id',
            'production_timestamp'
        ]) }} as production_key,

        -- Date dimension key
        to_char(production_hour, 'YYYYMMDDHH24')::bigint as hour_key,
        to_char(production_timestamp::date, 'YYYYMMDD')::integer as date_key,

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

        -- Quality metrics
        quality_status,
        quality_flag,
        defect_type,
        first_pass_yield,
        rework_required,

        -- Performance metrics
        cycle_time_seconds,
        oee,
        availability,
        performance,
        quality_rate,

        -- Cost metrics
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        total_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Component-specific metrics (polymorphic)
        metric_1,
        metric_2,
        metric_3,
        metric_4,

        -- Metadata
        loaded_at

    from combined
)

select * from final
