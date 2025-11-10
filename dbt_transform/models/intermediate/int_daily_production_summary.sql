{{
    config(
        materialized='view'
    )
}}

-- Daily production summary by component and line

with production_quality as (
    select * from {{ ref('int_production_quality') }}
),

daily_summary as (
    select
        component_type,
        line_id,
        date_trunc('day', production_timestamp) as production_date,

        count(*) as total_units,
        sum(quality_flag) as passed_units,
        count(*) - sum(quality_flag) as failed_units,

        round(100.0 * sum(quality_flag) / count(*), 2) as pass_rate,

        min(production_timestamp) as first_production_time,
        max(production_timestamp) as last_production_time

    from production_quality
    group by 1, 2, 3
)

select * from daily_summary
