{{
    config(
        materialized='table'
    )
}}

with production as (
    select * from {{ ref('fact_press_operations') }}
),

material_coils as (
    select * from {{ ref('stg_material_coils') }}
),

part_family_metrics as (
    select
        p.part_family,
        p.part_type,
        p.material_grade,

        -- Volume metrics
        count(*) as total_parts_produced,
        count(*) filter (where p.quality_flag = true) as parts_passed,
        count(*) filter (where p.quality_flag = false) as parts_failed,
        round((count(*) filter (where p.quality_flag = true)::numeric / count(*) * 100), 2) as first_pass_yield_pct,

        -- Quality metrics
        count(distinct p.defect_type) as unique_defect_types,
        count(*) filter (where p.rework_required) as rework_count,
        round((count(*) filter (where p.rework_required)::numeric / count(*) * 100), 2) as rework_rate_pct,

        -- OEE metrics
        round(avg(p.oee), 3) as avg_oee,
        round(avg(p.availability), 3) as avg_availability,
        round(avg(p.performance), 3) as avg_performance,
        round(avg(p.quality_rate), 3) as avg_quality_rate,

        -- Process metrics
        round(avg(p.tonnage_peak), 2) as avg_tonnage,
        round(avg(p.cycle_time_seconds), 2) as avg_cycle_time,
        round(avg(p.stroke_rate_spm), 1) as avg_stroke_rate,

        -- Cost metrics
        round(avg(p.total_cost_per_unit), 4) as avg_cost_per_part,
        round(sum(p.total_cost_per_unit), 2) as total_production_cost,

        -- Cost breakdown
        round(avg(p.material_cost_per_unit), 4) as avg_material_cost,
        round(avg(p.labor_cost_per_unit), 4) as avg_labor_cost,
        round(avg(p.energy_cost_per_unit), 4) as avg_energy_cost,

        -- Material metrics
        count(distinct p.coil_id) as unique_coils_used,
        round(avg(p.surface_profile_deviation_mm), 3) as avg_surface_deviation,

        -- Time range
        min(p.production_date) as first_production_date,
        max(p.production_date) as last_production_date,
        count(distinct p.production_date) as production_days

    from production p
    group by p.part_family, p.part_type, p.material_grade
),

with_material_correlation as (
    select
        pf.*,

        -- Material quality correlation
        round(avg(mc.avg_defect_rate), 4) as avg_coil_defect_rate,
        round(avg(mc.springback_issues), 2) as avg_springback_issues_per_coil,
        round(avg(mc.yield_strength_mpa), 1) as avg_material_yield_strength,
        round(avg(mc.tensile_strength_mpa), 1) as avg_material_tensile_strength

    from part_family_metrics pf
    left join material_coils mc on pf.material_grade = mc.material_grade
    group by
        pf.part_family, pf.part_type, pf.material_grade,
        pf.total_parts_produced, pf.parts_passed, pf.parts_failed, pf.first_pass_yield_pct,
        pf.unique_defect_types, pf.rework_count, pf.rework_rate_pct,
        pf.avg_oee, pf.avg_availability, pf.avg_performance, pf.avg_quality_rate,
        pf.avg_tonnage, pf.avg_cycle_time, pf.avg_stroke_rate,
        pf.avg_cost_per_part, pf.total_production_cost,
        pf.avg_material_cost, pf.avg_labor_cost, pf.avg_energy_cost,
        pf.unique_coils_used, pf.avg_surface_deviation,
        pf.first_production_date, pf.last_production_date, pf.production_days
)

select * from with_material_correlation
order by part_family, material_grade
