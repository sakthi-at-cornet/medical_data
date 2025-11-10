{{
    config(
        materialized='view'
    )
}}

-- Combine all production quality metrics across components

with refills as (
    select
        'refills' as component_type,
        production_timestamp,
        line_id,
        batch_id,
        quality_status,
        quality_flag,
        loaded_at
    from {{ ref('stg_refills_production') }}
),

bodies as (
    select
        'bodies' as component_type,
        production_timestamp,
        line_id,
        batch_id,
        quality_status,
        quality_flag,
        loaded_at
    from {{ ref('stg_bodies_production') }}
),

springs as (
    select
        'springs' as component_type,
        production_timestamp,
        line_id,
        batch_id,
        quality_status,
        quality_flag,
        loaded_at
    from {{ ref('stg_springs_production') }}
),

combined as (
    select * from refills
    union all
    select * from bodies
    union all
    select * from springs
)

select * from combined
