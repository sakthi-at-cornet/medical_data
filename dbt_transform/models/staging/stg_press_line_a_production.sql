{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('press_line_a', 'press_line_a_production') }}
),

cleaned as (
    select
        id,
        part_id,
        timestamp as production_timestamp,
        press_line_id,
        die_id,
        batch_id,
        shift_id,
        operator_id,

        -- Part classification
        part_family,
        part_variant,

        -- Material traceability
        coil_id,
        material_grade,
        material_thickness_nominal,
        material_thickness_measured,

        -- Process data
        tonnage_peak,
        stroke_rate_spm,
        cycle_time_seconds,
        die_temperature_zone1_celsius,
        die_temperature_zone2_celsius,
        forming_energy_ton_inches,

        -- Quality
        quality_status,
        quality_flag,
        defect_type,
        defect_severity,
        rework_required,

        -- Quality metrics (door-specific dimensions)
        length_overall_mm,
        width_overall_mm,
        draw_depth_mm,
        flange_width_bottom_mm,
        hole_hinge_upper_diameter_mm,
        hole_hinge_lower_diameter_mm,
        surface_profile_deviation_mm,

        -- OEE components
        oee,
        availability,
        performance,
        quality_rate,

        -- Cost tracking
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        total_cost_per_unit,

        -- Environmental factors
        temperature_celsius,
        humidity_percent,

        -- Metadata
        created_at,

        -- Derived fields
        case
            when part_family = 'Door_Outer_Left' then 'L'
            when part_family = 'Door_Outer_Right' then 'R'
            else null
        end as part_side,

        case
            when tonnage_peak < 610 then 'low'
            when tonnage_peak between 610 and 640 then 'normal'
            else 'high'
        end as tonnage_category,

        case
            when cycle_time_seconds < 1.3 then 'fast'
            when cycle_time_seconds between 1.3 and 1.4 then 'normal'
            else 'slow'
        end as cycle_time_category,

        case
            when oee >= 0.85 then 'excellent'
            when oee >= 0.75 then 'good'
            when oee >= 0.65 then 'fair'
            else 'poor'
        end as oee_category,

        -- Extract date/time components
        date(timestamp) as production_date,
        extract(hour from timestamp) as production_hour,
        extract(dow from timestamp) as day_of_week,
        case when extract(dow from timestamp) in (0, 6) then true else false end as is_weekend,

        -- Die generation (from die_id)
        case
            when die_id like '%Rev3' then 3
            when die_id like '%Rev2' then 2
            else null
        end as die_revision

    from source
)

select * from cleaned
