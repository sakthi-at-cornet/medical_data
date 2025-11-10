{{
    config(
        materialized='table'
    )
}}

with press_line_a as (
    select * from {{ ref('stg_press_line_a_production') }}
),

press_line_b as (
    select * from {{ ref('stg_press_line_b_production') }}
),

-- Unionize press line A and B data with standardized schema
combined as (
    -- Press Line A: Door panels
    select
        id,
        part_id,
        production_timestamp,
        press_line_id,
        die_id,
        batch_id,
        shift_id,
        operator_id,
        part_family,
        part_variant,
        coil_id,
        material_grade,
        material_thickness_nominal,
        material_thickness_measured,
        tonnage_peak,
        stroke_rate_spm,
        cycle_time_seconds,
        die_temperature_zone1_celsius,
        die_temperature_zone2_celsius,
        forming_energy_ton_inches,
        null::numeric as cushion_pressure_bar,  -- Only Line B has this
        quality_status,
        quality_flag,
        defect_type,
        defect_severity,
        rework_required,
        length_overall_mm,
        width_overall_mm,
        draw_depth_mm as draw_depth,
        null::numeric as draw_depth_apex_mm,  -- Bonnet-specific
        flange_width_bottom_mm,
        null::numeric as hinge_bracket_position_x_mm,  -- Bonnet-specific
        null::numeric as hinge_bracket_position_y_mm,  -- Bonnet-specific
        hole_hinge_upper_diameter_mm,
        hole_hinge_lower_diameter_mm,
        surface_profile_deviation_mm,
        null::numeric as thinning_percentage_max,  -- Bonnet-specific
        null::text as thinning_location,  -- Bonnet-specific
        oee,
        availability,
        performance,
        quality_rate,
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        total_cost_per_unit,
        temperature_celsius,
        humidity_percent,
        created_at,
        part_side,
        tonnage_category,
        cycle_time_category,
        oee_category,
        production_date,
        production_hour,
        day_of_week,
        is_weekend,
        die_revision,
        'Door' as part_type,
        'LINE_A' as line_name

    from press_line_a

    union all

    -- Press Line B: Bonnet panels
    select
        id,
        part_id,
        production_timestamp,
        press_line_id,
        die_id,
        batch_id,
        shift_id,
        operator_id,
        part_family,
        part_variant,
        coil_id,
        material_grade,
        material_thickness_nominal,
        material_thickness_measured,
        tonnage_peak,
        stroke_rate_spm,
        cycle_time_seconds,
        die_temperature_zone1_celsius,
        die_temperature_zone2_celsius,
        forming_energy_ton_inches,
        cushion_pressure_bar,
        quality_status,
        quality_flag,
        defect_type,
        defect_severity,
        rework_required,
        length_overall_mm,
        width_overall_mm,
        null::numeric as draw_depth,  -- Door-specific
        draw_depth_apex_mm,
        null::numeric as flange_width_bottom_mm,  -- Door-specific
        hinge_bracket_position_x_mm,
        hinge_bracket_position_y_mm,
        null::numeric as hole_hinge_upper_diameter_mm,  -- Door-specific
        null::numeric as hole_hinge_lower_diameter_mm,  -- Door-specific
        surface_profile_deviation_mm,
        thinning_percentage_max,
        thinning_location,
        oee,
        availability,
        performance,
        quality_rate,
        material_cost_per_unit,
        labor_cost_per_unit,
        energy_cost_per_unit,
        total_cost_per_unit,
        temperature_celsius,
        humidity_percent,
        created_at,
        null::text as part_side,  -- Door-specific
        tonnage_category,
        cycle_time_category,
        oee_category,
        production_date,
        production_hour,
        day_of_week,
        is_weekend,
        die_revision,
        'Bonnet' as part_type,
        'LINE_B' as line_name

    from press_line_b
)

select * from combined
