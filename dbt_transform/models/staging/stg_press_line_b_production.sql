{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('press_line_b', 'press_line_b_production') }}
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

        -- Process data (bonnet-specific with cushion pressure)
        tonnage_peak,
        stroke_rate_spm,
        cycle_time_seconds,
        die_temperature_zone1_celsius,
        die_temperature_zone2_celsius,
        forming_energy_ton_inches,
        cushion_pressure_bar,

        -- Quality
        quality_status,
        quality_flag,
        defect_type,
        defect_severity,
        rework_required,

        -- Quality metrics (bonnet-specific dimensions)
        length_overall_mm,
        width_overall_mm,
        draw_depth_apex_mm,
        surface_profile_deviation_mm,
        hinge_bracket_position_x_mm,
        hinge_bracket_position_y_mm,
        thinning_percentage_max,
        thinning_location,

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
            when material_grade = 'HSLA_350' then 'HSLA'
            when material_grade = 'DP600' then 'DP'
            else 'OTHER'
        end as material_type,

        case
            when tonnage_peak < 950 then 'low'
            when tonnage_peak between 950 and 1050 then 'normal'
            else 'high'
        end as tonnage_category,

        case
            when cycle_time_seconds < 3.5 then 'fast'
            when cycle_time_seconds between 3.5 and 4.5 then 'normal'
            else 'slow'
        end as cycle_time_category,

        case
            when oee >= 0.80 then 'excellent'
            when oee >= 0.70 then 'good'
            when oee >= 0.60 then 'fair'
            else 'poor'
        end as oee_category,

        case
            when thinning_percentage_max < 20 then 'acceptable'
            when thinning_percentage_max between 20 and 25 then 'monitor'
            else 'critical'
        end as thinning_severity,

        -- Extract date/time components
        date(timestamp) as production_date,
        extract(hour from timestamp) as production_hour,
        extract(dow from timestamp) as day_of_week,
        case when extract(dow from timestamp) in (0, 6) then true else false end as is_weekend,

        -- Die generation (from die_id)
        case
            when die_id like '%Rev5' then 5
            when die_id like '%Rev4' then 4
            else null
        end as die_revision

    from source
)

select * from cleaned
