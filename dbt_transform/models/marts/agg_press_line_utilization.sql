{{
    config(
        materialized='table'
    )
}}

with daily_production as (
    select * from {{ ref('int_daily_production_by_press') }}
),

utilization_metrics as (
    select
        press_line_id,
        line_name,
        part_type,

        -- Production volume
        sum(total_parts) as total_parts_produced,
        sum(parts_passed) as total_parts_passed,
        sum(parts_failed) as total_parts_failed,
        round(avg(pass_rate_pct), 2) as avg_pass_rate_pct,

        -- OEE metrics
        round(avg(avg_oee), 3) as overall_avg_oee,
        round(avg(avg_availability), 3) as overall_avg_availability,
        round(avg(avg_performance), 3) as overall_avg_performance,
        round(avg(avg_quality_rate), 3) as overall_avg_quality_rate,

        -- Process metrics
        round(avg(avg_tonnage_peak), 2) as avg_tonnage,
        round(avg(avg_cycle_time_seconds), 2) as avg_cycle_time,
        round(avg(avg_stroke_rate_spm), 1) as avg_stroke_rate,

        -- Cost metrics
        round(sum(total_production_cost), 2) as total_cost,
        round(avg(avg_total_cost_per_unit), 4) as avg_cost_per_unit,

        -- Operational metrics
        count(distinct production_date) as total_production_days,
        sum(batch_count) as total_batches,
        sum(operator_count) as total_operator_shifts,
        sum(defect_count) as total_defects,
        sum(rework_count) as total_rework,

        -- Die usage
        avg(die_count) as avg_dies_per_day,

        -- Weekend analysis
        sum(total_parts) filter (where is_weekend) as weekend_parts,
        sum(total_parts) filter (where not is_weekend) as weekday_parts,
        round((sum(total_parts) filter (where is_weekend)::numeric / sum(total_parts) * 100), 2) as weekend_production_pct,

        -- Shift analysis
        sum(total_parts) filter (where shift_id = 'SHIFT_MORNING') as morning_shift_parts,
        sum(total_parts) filter (where shift_id = 'SHIFT_AFTERNOON') as afternoon_shift_parts,
        sum(total_parts) filter (where shift_id = 'SHIFT_NIGHT') as night_shift_parts,

        -- Time range
        min(production_date) as first_production_date,
        max(production_date) as last_production_date

    from daily_production
    group by press_line_id, line_name, part_type
)

select * from utilization_metrics
order by press_line_id
