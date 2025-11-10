{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- Material performance analysis for bodies

with bodies_staging as (
    select * from {{ ref('stg_bodies_production') }}
),

material_performance as (
    select
        material,
        count(*) as total_units,
        sum(quality_flag) as passed_units,
        count(*) - sum(quality_flag) as failed_units,

        round(100.0 * sum(quality_flag) / count(*), 2) as pass_rate,

        -- Metrics by material
        round(avg(durability_score), 2) as avg_durability,
        round(avg(color_match_rating), 3) as avg_color_match,
        round(avg(length_mm), 2) as avg_length,
        round(avg(wall_thickness_mm), 2) as avg_thickness,

        -- Distribution of quality categories
        count(*) filter (where durability_category = 'high') as high_durability_count,
        count(*) filter (where durability_category = 'medium') as medium_durability_count,
        count(*) filter (where durability_category = 'low') as low_durability_count

    from bodies_staging
    group by material
)

select * from material_performance
order by pass_rate desc
