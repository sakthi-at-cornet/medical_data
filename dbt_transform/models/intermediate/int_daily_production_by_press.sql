{{
    config(
        materialized='table'
    )
}}

with production as (
    select * from {{ ref('int_automotive_production_combined') }}
),

daily_agg as (
    select
        production_date,
        press_line_id,
        line_name,
        part_type,
        part_family,
        shift_id,

        -- Volume metrics
        count(*) as total_parts,
        count(*) filter (where quality_flag = true) as parts_passed,
        count(*) filter (where quality_flag = false) as parts_failed,
        count(distinct batch_id) as batch_count,
        count(distinct operator_id) as operator_count,
        count(distinct die_id) as die_count,

        -- Quality metrics
        round(avg(case when quality_flag then 1 else 0 end) * 100, 2) as pass_rate_pct,
        count(*) filter (where defect_type is not null) as defect_count,
        count(*) filter (where rework_required) as rework_count,

        -- OEE metrics
        round(avg(oee), 3) as avg_oee,
        round(avg(availability), 3) as avg_availability,
        round(avg(performance), 3) as avg_performance,
        round(avg(quality_rate), 3) as avg_quality_rate,

        -- Process metrics
        round(avg(tonnage_peak), 2) as avg_tonnage_peak,
        round(min(tonnage_peak), 2) as min_tonnage_peak,
        round(max(tonnage_peak), 2) as max_tonnage_peak,
        round(avg(cycle_time_seconds), 2) as avg_cycle_time_seconds,
        round(avg(stroke_rate_spm), 1) as avg_stroke_rate_spm,

        -- Temperature metrics
        round(avg(die_temperature_zone1_celsius), 1) as avg_die_temp_zone1,
        round(avg(die_temperature_zone2_celsius), 1) as avg_die_temp_zone2,

        -- Cost metrics
        round(avg(total_cost_per_unit), 4) as avg_total_cost_per_unit,
        round(sum(total_cost_per_unit), 2) as total_production_cost,

        -- Material thickness
        round(avg(material_thickness_measured), 3) as avg_thickness_measured,

        -- Environmental
        round(avg(temperature_celsius), 1) as avg_ambient_temp,
        round(avg(humidity_percent), 1) as avg_humidity,

        -- Weekend flag
        max(is_weekend::int)::boolean as is_weekend

    from production
    group by
        production_date,
        press_line_id,
        line_name,
        part_type,
        part_family,
        shift_id
)

select * from daily_agg
order by production_date desc, press_line_id, shift_id
