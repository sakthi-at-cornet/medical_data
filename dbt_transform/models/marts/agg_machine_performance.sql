{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- Machine performance aggregation
-- Daily machine-level KPIs with OEE breakdown, trends, and performance benchmarks

with hourly_production as (
    select * from {{ ref('fact_hourly_production_detail') }}
),

daily_machine_metrics as (
    select
        DATE_TRUNC('day', production_timestamp)::date as production_date,
        to_char(production_timestamp::date, 'YYYYMMDD')::integer as date_key,
        component_type,
        line_id,
        machine_id,

        -- Production volume
        COUNT(*) as total_units_produced,
        COUNT(*) FILTER (WHERE quality_flag = true) as passed_units,
        COUNT(*) FILTER (WHERE quality_flag = false) as failed_units,
        COUNT(*) FILTER (WHERE first_pass_yield = true) as first_pass_yield_units,
        COUNT(*) FILTER (WHERE rework_required = true) as rework_units,

        -- Quality metrics
        ROUND(AVG(CASE WHEN quality_flag THEN 1.0 ELSE 0.0 END) * 100, 2) as pass_rate_pct,
        ROUND(AVG(CASE WHEN first_pass_yield THEN 1.0 ELSE 0.0 END) * 100, 2) as first_pass_yield_pct,
        ROUND(AVG(CASE WHEN rework_required THEN 1.0 ELSE 0.0 END) * 100, 2) as rework_rate_pct,

        -- OEE components (average across the day)
        ROUND(AVG(oee), 4) as avg_oee,
        ROUND(AVG(availability), 4) as avg_availability,
        ROUND(AVG(performance), 4) as avg_performance,
        ROUND(AVG(quality_rate), 4) as avg_quality_rate,

        -- Cycle time analysis
        ROUND(AVG(cycle_time_seconds), 2) as avg_cycle_time_seconds,
        ROUND(MIN(cycle_time_seconds), 2) as min_cycle_time_seconds,
        ROUND(MAX(cycle_time_seconds), 2) as max_cycle_time_seconds,
        ROUND(STDDEV(cycle_time_seconds), 2) as stddev_cycle_time,

        -- Cost analysis
        ROUND(AVG(total_cost_per_unit), 4) as avg_cost_per_unit,
        ROUND(SUM(total_cost_per_unit), 2) as total_production_cost,

        -- Environmental conditions
        ROUND(AVG(temperature_celsius), 1) as avg_temperature_celsius,
        ROUND(AVG(humidity_percent), 1) as avg_humidity_percent,

        -- Defect tracking
        COUNT(DISTINCT defect_type) FILTER (WHERE defect_type IS NOT NULL) as unique_defect_types,
        COUNT(*) FILTER (WHERE defect_type IS NOT NULL) as total_defects,

        MAX(loaded_at) as last_updated

    from hourly_production
    group by
        DATE_TRUNC('day', production_timestamp)::date,
        date_key,
        component_type,
        line_id,
        machine_id
),

machine_performance_with_trends as (
    select
        dml.*,

        -- 7-day moving averages for trend detection
        ROUND(AVG(avg_oee) OVER (
            PARTITION BY component_type, machine_id
            ORDER BY production_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 4) as oee_7day_ma,

        ROUND(AVG(pass_rate_pct) OVER (
            PARTITION BY component_type, machine_id
            ORDER BY production_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) as pass_rate_7day_ma,

        ROUND(AVG(avg_cycle_time_seconds) OVER (
            PARTITION BY component_type, machine_id
            ORDER BY production_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) as cycle_time_7day_ma,

        -- Compare to previous day
        LAG(avg_oee, 1) OVER (
            PARTITION BY component_type, machine_id
            ORDER BY production_date
        ) as prev_day_oee,

        LAG(pass_rate_pct, 1) OVER (
            PARTITION BY component_type, machine_id
            ORDER BY production_date
        ) as prev_day_pass_rate,

        -- Machine performance rank within component type
        RANK() OVER (
            PARTITION BY component_type, production_date
            ORDER BY avg_oee DESC
        ) as oee_rank_in_component,

        -- Overall performance rank
        RANK() OVER (
            PARTITION BY production_date
            ORDER BY avg_oee DESC
        ) as oee_rank_overall

    from daily_machine_metrics dml
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key([
            'production_date',
            'component_type',
            'machine_id'
        ]) }} as machine_performance_key,

        date_key,
        production_date,
        component_type,
        line_id,
        machine_id,

        -- Production volume
        total_units_produced,
        passed_units,
        failed_units,
        first_pass_yield_units,
        rework_units,

        -- Quality metrics
        pass_rate_pct,
        first_pass_yield_pct,
        rework_rate_pct,

        -- OEE components
        avg_oee,
        avg_availability,
        avg_performance,
        avg_quality_rate,

        -- Cycle time metrics
        avg_cycle_time_seconds,
        min_cycle_time_seconds,
        max_cycle_time_seconds,
        stddev_cycle_time,

        -- Cost metrics
        avg_cost_per_unit,
        total_production_cost,

        -- Cost per passed unit (economic efficiency)
        CASE
            WHEN passed_units > 0
            THEN ROUND(total_production_cost / passed_units, 4)
            ELSE NULL
        END as cost_per_passed_unit,

        -- Environmental conditions
        avg_temperature_celsius,
        avg_humidity_percent,

        -- Defect metrics
        unique_defect_types,
        total_defects,

        -- Trends (7-day moving averages)
        oee_7day_ma,
        pass_rate_7day_ma,
        cycle_time_7day_ma,

        -- Day-over-day changes
        ROUND(avg_oee - prev_day_oee, 4) as oee_change_from_prev_day,
        ROUND(pass_rate_pct - prev_day_pass_rate, 2) as pass_rate_change_from_prev_day,

        -- Performance flags
        CASE
            WHEN avg_oee < 0.70 THEN 'poor'
            WHEN avg_oee < 0.80 THEN 'below_target'
            WHEN avg_oee < 0.90 THEN 'good'
            ELSE 'excellent'
        END as oee_performance_tier,

        CASE
            WHEN (avg_oee - prev_day_oee) < -0.05 THEN true
            ELSE false
        END as performance_degradation_alert,

        CASE
            WHEN total_defects > 5 THEN true
            ELSE false
        END as high_defect_count_alert,

        -- Rankings
        oee_rank_in_component,
        oee_rank_overall,

        last_updated

    from machine_performance_with_trends
)

select * from final
