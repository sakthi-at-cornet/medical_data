{{
    config(
        materialized='view'
    )
}}

with die_master as (
    select * from {{ source('die_management', 'die_master') }}
),

changeover_events as (
    select * from {{ source('die_management', 'die_changeover_events') }}
),

condition_assessments as (
    select * from {{ source('die_management', 'die_condition_assessments') }}
),

die_master_cleaned as (
    select
        die_id,
        part_family,
        die_type,
        press_line_compatible,
        tonnage_rating,
        manufacture_date,
        first_production_date,
        total_strokes_count,
        service_life_target_strokes,
        health_status,
        current_location,
        is_active,
        last_maintenance_date,
        next_maintenance_due_date,
        maintenance_interval_strokes,
        number_of_stations,
        binder_force_required,
        material_compatibility,
        created_at,
        updated_at,

        -- Derived fields
        round((total_strokes_count::numeric / nullif(service_life_target_strokes, 0) * 100), 2) as lifecycle_percentage,
        service_life_target_strokes - total_strokes_count as remaining_strokes,
        case
            when total_strokes_count::numeric / nullif(service_life_target_strokes, 0) >= 0.90 then 'critical'
            when total_strokes_count::numeric / nullif(service_life_target_strokes, 0) >= 0.75 then 'high'
            when total_strokes_count::numeric / nullif(service_life_target_strokes, 0) >= 0.50 then 'medium'
            else 'low'
        end as wear_urgency,

        next_maintenance_due_date - current_date as days_until_maintenance

    from die_master
),

changeover_events_cleaned as (
    select
        changeover_id,
        press_line_id,
        timestamp_start,
        timestamp_end,
        duration_minutes,
        die_removed_id,
        die_installed_id,
        changeover_type,
        reason,
        smed_target_minutes,
        smed_variance_minutes,
        setup_person_id,
        operator_id,
        team_size,
        first_piece_inspection_passed,
        adjustments_required,
        created_at,

        -- Derived fields
        date(timestamp_start) as changeover_date,
        extract(hour from timestamp_start) as changeover_hour,
        extract(dow from timestamp_start) as day_of_week,

        case
            when duration_minutes <= smed_target_minutes then 'on_target'
            when duration_minutes <= smed_target_minutes * 1.1 then 'acceptable'
            else 'needs_improvement'
        end as smed_performance,

        case
            when adjustments_required = 0 then 'excellent'
            when adjustments_required <= 2 then 'good'
            else 'poor'
        end as setup_quality

    from changeover_events
),

condition_assessments_cleaned as (
    select
        assessment_id,
        die_id,
        assessment_date,
        inspector_id,
        assessment_type,
        overall_health_score,
        wear_level_percentage,
        tonnage_drift_percentage,
        dimensional_drift_mm,
        defect_rate_trend,
        punch_condition,
        die_surface_condition,
        alignment_status,
        lubrication_status,
        remaining_useful_life_strokes,
        days_until_maintenance_recommended,
        recommended_action,
        observations,
        issues_found,
        created_at,

        -- Derived fields
        case
            when overall_health_score >= 85 then 'excellent'
            when overall_health_score >= 70 then 'good'
            when overall_health_score >= 55 then 'fair'
            else 'poor'
        end as health_category,

        case
            when wear_level_percentage >= 80 then 'critical'
            when wear_level_percentage >= 60 then 'high'
            when wear_level_percentage >= 40 then 'medium'
            else 'low'
        end as wear_category,

        extract(week from assessment_date) as assessment_week,
        extract(month from assessment_date) as assessment_month

    from condition_assessments
),

final as (
    select
        'die_master' as source_table,
        die_id as entity_id,
        null::timestamp as event_timestamp,
        to_jsonb(dm.*) as data
    from die_master_cleaned dm

    union all

    select
        'changeover_events' as source_table,
        changeover_id::text as entity_id,
        timestamp_start as event_timestamp,
        to_jsonb(ce.*) as data
    from changeover_events_cleaned ce

    union all

    select
        'condition_assessments' as source_table,
        assessment_id::text as entity_id,
        assessment_date::timestamp as event_timestamp,
        to_jsonb(ca.*) as data
    from condition_assessments_cleaned ca
)

select * from final
