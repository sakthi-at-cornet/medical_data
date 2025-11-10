{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- Quality trends by component type over time

with production_quality as (
    select * from {{ ref('int_production_quality') }}
),

hourly_aggregates as (
    select
        component_type,
        date_trunc('day', production_timestamp) as production_date,
        date_trunc('hour', production_timestamp) as production_hour,

        count(*) as total_units,
        sum(quality_flag) as passed_units,
        count(*) - sum(quality_flag) as failed_units,
        round(100.0 * sum(quality_flag) / count(*), 2) as pass_rate

    from production_quality
    group by 1, 2, 3
),

quality_trends as (
    select
        *,
        -- Moving averages (window functions on aggregated data)
        round(avg(pass_rate) over (
            partition by component_type
            order by production_hour
            rows between 3 preceding and current row
        ), 2) as moving_avg_pass_rate_4h

    from hourly_aggregates
)

select * from quality_trends
order by component_type, production_hour
