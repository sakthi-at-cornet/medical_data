{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['production_date']},
            {'columns': ['press_line_id']},
            {'columns': ['part_family']},
            {'columns': ['die_id']},
            {'columns': ['coil_id']},
            {'columns': ['quality_status']}
        ]
    )
}}

with production as (
    select * from {{ ref('int_automotive_production_combined') }}
),

final as (
    select
        -- Keys
        id as production_key,
        part_id,
        production_timestamp,
        production_date,
        production_hour,

        -- Dimensions
        press_line_id,
        line_name,
        die_id,
        die_revision,
        batch_id,
        shift_id,
        operator_id,
        part_family,
        part_type,
        part_variant,
        coil_id,
        material_grade,

        -- Process measurements
        tonnage_peak,
        stroke_rate_spm,
        cycle_time_seconds,
        forming_energy_ton_inches,
        die_temperature_zone1_celsius,
        die_temperature_zone2_celsius,
        cushion_pressure_bar,

        -- Material properties
        material_thickness_nominal,
        material_thickness_measured,

        -- Quality metrics
        quality_status,
        quality_flag,
        defect_type,
        defect_severity,
        rework_required,

        -- Dimensional measurements
        length_overall_mm,
        width_overall_mm,
        draw_depth,
        draw_depth_apex_mm,
        surface_profile_deviation_mm,
        thinning_percentage_max,

        -- OEE components
        oee,
        availability,
        performance,
        quality_rate,

        -- Cost breakdown
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        total_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Derived categories
        tonnage_category,
        cycle_time_category,
        oee_category,
        day_of_week,
        is_weekend,

        -- Metadata
        created_at

    from production
)

select * from final
