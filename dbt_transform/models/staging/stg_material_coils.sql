{{
    config(
        materialized='view'
    )
}}

with supplier_master as (
    select * from {{ source('materials', 'supplier_master') }}
),

material_coils as (
    select * from {{ source('materials', 'material_coils') }}
),

supplier_cleaned as (
    select
        supplier_id,
        supplier_name,
        country,
        material_specialization,
        quality_certification,
        quality_score_overall,
        on_time_delivery_rate,
        defect_rate_ppm,
        contact_person,
        contact_email,
        status,
        last_audit_date,
        created_at,
        updated_at,

        -- Derived fields
        case
            when quality_score_overall >= 95 then 'excellent'
            when quality_score_overall >= 90 then 'good'
            when quality_score_overall >= 80 then 'acceptable'
            else 'needs_improvement'
        end as supplier_quality_category,

        case
            when on_time_delivery_rate >= 98 then 'excellent'
            when on_time_delivery_rate >= 95 then 'good'
            else 'needs_improvement'
        end as delivery_performance,

        current_date - last_audit_date as days_since_audit

    from supplier_master
),

coils_cleaned as (
    select
        mc.coil_id,
        mc.supplier_id,
        mc.material_grade,
        mc.thickness_nominal,
        mc.width_mm,
        mc.weight_kg,
        mc.yield_strength_mpa,
        mc.tensile_strength_mpa,
        mc.elongation_percentage,
        mc.hardness_hv,
        mc.carbon_content_percentage,
        mc.heat_number,
        mc.mill_test_certificate_number,
        mc.manufactured_date,
        mc.received_date,
        mc.inspection_date,
        mc.inspection_status,
        mc.mounted_date,
        mc.exhausted_date,
        mc.parts_produced,
        mc.scrap_count,
        mc.remaining_weight_kg,
        mc.avg_defect_rate,
        mc.springback_issues,
        mc.surface_defects,
        mc.quality_notes,
        mc.created_at,
        mc.updated_at,

        -- Derived fields
        case
            when mc.material_grade = 'CRS_SPCC' then 'Cold_Rolled_Steel'
            when mc.material_grade = 'HSLA_350' then 'High_Strength_Low_Alloy'
            when mc.material_grade = 'DP600' then 'Dual_Phase_Steel'
            else 'Other'
        end as material_category,

        round((mc.scrap_count::numeric / nullif(mc.parts_produced, 0) * 100), 2) as scrap_rate_percentage,

        mc.received_date - mc.manufactured_date as lead_time_days,
        mc.mounted_date - mc.received_date as storage_duration_days,

        case
            when mc.avg_defect_rate < 0.03 then 'excellent'
            when mc.avg_defect_rate < 0.05 then 'good'
            when mc.avg_defect_rate < 0.08 then 'acceptable'
            else 'poor'
        end as coil_quality_category,

        case
            when mc.yield_strength_mpa < mc.tensile_strength_mpa * 0.5 then 'low'
            when mc.yield_strength_mpa < mc.tensile_strength_mpa * 0.7 then 'medium'
            else 'high'
        end as yield_ratio_category,

        case
            when mc.springback_issues > 5 then 'high_springback_risk'
            when mc.springback_issues > 2 then 'moderate_springback_risk'
            else 'low_springback_risk'
        end as springback_risk_level,

        -- Calculate weight utilization
        round(((mc.weight_kg - mc.remaining_weight_kg) / nullif(mc.weight_kg, 0) * 100), 2) as weight_utilization_percentage,

        extract(month from mc.received_date) as received_month,
        extract(year from mc.received_date) as received_year

    from material_coils mc
),

joined as (
    select
        c.*,
        s.supplier_name,
        s.country,
        s.quality_score_overall as supplier_quality_score,
        s.supplier_quality_category,
        s.on_time_delivery_rate,
        s.delivery_performance,
        s.defect_rate_ppm as supplier_target_defect_ppm

    from coils_cleaned c
    left join supplier_cleaned s on c.supplier_id = s.supplier_id
)

select * from joined
