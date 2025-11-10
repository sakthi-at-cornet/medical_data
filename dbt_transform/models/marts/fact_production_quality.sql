{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- Production quality fact table with dimensional references

with daily_summary as (
    select * from {{ ref('int_daily_production_summary') }}
),

final as (
    select
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key(['component_type', 'line_id', 'production_date']) }} as quality_key,

        -- Date dimension key
        to_char(production_date, 'YYYYMMDD')::integer as date_key,

        -- Production line dimension (join to dim_production_line)
        line_id,

        -- Facts
        production_date::timestamp with time zone as timestamp,
        component_type,
        total_units,
        passed_units,
        failed_units,
        pass_rate,

        -- Calculate average quality score (simple metric)
        round((passed_units::numeric / total_units * 100), 2) as avg_quality_score,

        -- Time tracking
        first_production_time,
        last_production_time

    from daily_summary
)

select * from final
