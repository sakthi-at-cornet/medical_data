ngeover management, material lot tracking across multiple part families, and aggregated KPIs across a heterogeneous manufacturing environment. This plan enables sophisticated analytics for production scheduling optimization, die utilization strategies, changeover reduction (SMED), and multi-part yield improvement.

---

## 1. Plant Architecture & Multi-Part Context

### Plant Configuration & Press Infrastructure[1][2]

**Press Line Portfolio** (complementary capacity and capability)

| Press Line | Equipment Type | Tonnage | Bed Size (mm) | Stroke SPM | Primary Part Types | Secondary Part Types | Coil Width Limit (mm) |
|------------|----------------|---------|---------------|-----------|-------------------|---------------------|----------------------|
| LiPerfect. Now I have comprehensive research on multi-part stamping operations, press shop planning with multiple dies and presses, setup times, tonnage requirements, and real-world press configurations. Let me create a deeply thought-out, multi-system dataset plan.

# Comprehensive Multi-Part Stamping Plant Dataset Plan: Doors, Roofs, Bonnets

## Executive Summary

This advanced plan extends the single-part door panel dataset into a **multi-part body panel stamping ecosystem** encompassing doors, roof panels, and bonnets across multiple press lines with varying capacities, different die configurations, setup management, and complex production scheduling. The dataset captures realistic operational complexity including press selection by part type, die chne A | JW36 H-Frame Double Crank | 800 T | 2200 × 1800 | 20-30 | Door outer panels (left/right) | — | 1800 |
| Line B | JW36 H-Frame Double Crank | 1000 T | 2200 × 1800 | 15-25 | Roof panel, Bonnet outer | Door reinforcements | 1800 |
| Line C | JS36 Close-Type Gear Press | 1200 T | 2500 × 2200 | 10-20 | Bonnet outer (complex draw), Roof reinforcement | Large door panels | 2000 |
| Line D | JW36 H-Frame | 600 T | 1800 × 1500 | 25-40 | Door inner panels, fastening clips | Bonnet trim elements | 1500 |
| Line E (Flex) | JH21 C-Frame | 250 T | 1200 × 800 | 40-60 | Trim pieces, piercing-only operations | Prototype tooling validation | 800 |

**Rationale**: Each press line is sized and configured for specific part families. Roof panels and complex bonnets require higher tonnage (drawing operations need more force per AHSS guidelines). Inner panels and trim can run on smaller, faster presses. This mix optimizes throughput, utilization, and changeover flexibility.[2][1]

### Body Panel Family Taxonomy

```
Stamped Body Panels
├── Doors (Closures)
│   ├── Outer Panel (Left/Right)
│   │   ├── 2-door configuration
│   │   └── 4-door configuration
│   ├── Inner Panel (Left/Right)
│   ├── Reinforcement Panel
│   └── Trim/Flange components
├── Roof (Closures & Structural)
│   ├── Roof Panel (main outer)
│   ├── Roof Reinforcement (structure, Class A surface)
│   ├── Roof Rail Mounting Pad
│   └── Sun-roof Opening Ring (if applicable)
└── Bonnets (Closures)
    ├── Outer Panel (Class A surface finish)
    ├── Inner Panel (reinforcement structure)
    ├── Hinge Bracket (attachment points)
    └── Latch Mounting Bracket
```

### Production Volume & Takt Context

- **Vehicle production target**: 400 vehicles/day (typical mid-size automotive OEM)
- **Parts per vehicle**: 
  - Doors: 4 (2 outer, 2 inner) + 2 reinforcements = 6 per vehicle
  - Roof: 1 outer + 1 reinforcement + 2 pads = 4 per vehicle
  - Bonnet: 1 outer + 1 inner + 2 brackets = 4 per vehicle
- **Daily stamping requirement**: 400 × (6 + 4 + 4) = 5,600 parts/day
- **Shift production target**: 5,600 ÷ 2 shifts = 2,800 parts/shift
- **Takt time per part**: Highly variable by type and process stage
  - Door outer: 1.2–1.5 sec/part (45–50 SPM on 800T press)
  - Roof outer: 4–6 sec/part (10–15 SPM on 1200T press, deep draw)
  - Bonnet outer: 3–5 sec/part (12–20 SPM on 1200T press)

***

## 2. Multi-System Data Architecture

### System 1: Press Line Data System
Monitors real-time press operations, one record per stroke/part, tagged by press_line_id.

### System 2: Die Tooling Management System
Tracks die inventory, maintenance history, changeover events, wear progression.

### System 3: Material Supply System
Coil sourcing, material lot tracking, supplier linkage across multiple part families.

### System 4: Quality Inspection System
Segregated by part type with type-specific dimensional specs and defect taxonomies.

### System 5: Production Planning & Scheduling System
Work orders, part sequencing, changeover planning, demand forecast linkage.

### System 6: Logistics & Traceability System
Part binning, shipping, genealogy tracking (coil → blank → part).

---

## 3. Hierarchical Data Structure for Multi-Part Context

### Top-Level Production Plan Entity

```yaml
production_plan_id: "PLAN_2025_03_15_SHIFT_2"
production_date: "2025-03-15"
shift_id: "Shift_2_Day"
production_targets:
  - part_family: "Door_Outer_Left"
    target_quantity: 280
    lines_assigned: ["Line_A"]
  - part_family: "Door_Outer_Right"
    target_quantity: 280
    lines_assigned: ["Line_A"]
  - part_family: "Roof_Outer"
    target_quantity: 200
    lines_assigned: ["Line_B", "Line_C"]
  - part_family: "Bonnet_Outer"
    target_quantity: 220
    lines_assigned: ["Line_C"]
  - part_family: "Door_Inner_Left"
    target_quantity: 280
    lines_assigned: ["Line_D"]
  - part_family: "Bonnet_Inner"
    target_quantity: 220
    lines_assigned: ["Line_D"]
```

### Production Batch Entity (ordered work)

```yaml
batch_id: "BATCH_DOL_20250315_01"
batch_sequence_number: 1
part_family: "Door_Outer_Left"
planned_start_time: "2025-03-15 06:00"
planned_end_time: "2025-03-15 07:15"
planned_quantity: 140
assigned_press_line: "Line_A"
assigned_press_machine: "Press_A1_800T"
die_set_id: "DIE_DOL_Rev3"
die_changeover_from_previous: "DIE_DOR_Rev2"
changeover_start_time: "2025-03-15 05:35"
changeover_end_time: "2025-03-15 06:00"
changeover_duration_minutes: 25
changeover_type: "die_exchange"  # vs "material_coil_change", "program_update", "tool_resharpen"
smed_target_minutes: 10
material_lot_ids: ["JSW_CRS_2025_14728", "JSW_CRS_2025_14729"]
material_grade: "CRS_SPCC"
operator_id: "OP_1247"
setup_person_id: "SETUP_0445"
quality_hold_flag: false
actual_start_time: "2025-03-15 06:02"
actual_end_time: "2025-03-15 07:22"
actual_quantity_produced: 138
actual_quantity_good: 135
notes: "Minor delay in die clamping alignment"
```

### Individual Part Record (Extended Multi-Part Schema)

Each stamped part now includes **part_family** linkage and **cross-system identifiers**:

```yaml
part_id: "DOL_20250315_A_085473"
part_family: "Door_Outer_Left"
part_variant: "4-door_sedan_LHS"
batch_id: "BATCH_DOL_20250315_01"
batch_sequence_in_lot: 47
---
# Press Line Context
press_line_id: "Line_A"
press_machine_id: "Press_A1_800T"
die_set_id: "DIE_DOL_Rev3"
die_generation: 3  # Engineering revision level
die_lifecycle_stage: "production"  # vs "debug", "prototype", "end_of_life"
die_stroke_number_cumulative: 128450
die_estimated_remaining_strokes: 21550  # Based on tool wear model
die_planned_maintenance_stroke: 150000  # When sharping/overhaul scheduled
die_maintenance_last_performed: "2025-02-28"
die_maintenance_type: "full_overhaul"  # vs "edge_sharpening", "component_replacement"
---
# Coil & Material Linkage
coil_id: "JSW_CRS_2025_14728"
coil_supplier_id: "JSW_Steel_Bengaluru"
supplier_lot_number: "JCR-27189-A"
material_grade: "CRS_SPCC"
material_thickness_nominal: 0.8
material_thickness_measured_pre_stamping: 0.80
material_yield_strength_supplier_cert: 170
material_tensile_strength_supplier_cert: 340
material_elongation_supplier_cert: 38
material_chemistry_carbon_percent: 0.067
material_chemistry_manganese_percent: 0.35
coil_production_date: "2025-02-18"
coil_heat_treatment_applied: "annealed"
coil_lot_qa_passed: true
coil_qa_notes: "Passed all tensile and hardness tests"
---
# Production Timestamp & Lifecycle
production_timestamp: "2025-03-15 14:32:18.345"
shift_id: "Shift_2_Day"
operator_id: "OP_1247"
---
# Process Data (Sensor/Tonnage)
tonnage_peak: 625.3
tonnage_signature_crank_angles: [360 values]
stroke_rate_actual_spm: 45
cycle_time_actual_seconds: 1.33
forming_energy_ton_inches: 1847.2
die_temperature_zone1_celsius: 48.2
die_temperature_zone2_celsius: 52.7
---
# Quality Inspection (Part-Family-Specific)
# For Door Outer, critical dimensions differ from Roof or Bonnet
inspection_type: "CMM_sampling"  # Every 10th part
inspection_datetime: "2025-03-15 14:33:00"
inspected_by_operator_id: "INSP_0823"

# Door Outer Panel Specific Dimensions
length_overall_mm: 1087.4
width_overall_mm: 645.2
draw_depth_mm: 152.8
hole_hinge_upper_diameter_mm: 10.02
hole_hinge_lower_diameter_mm: 10.01
hole_lock_diameter_mm: 8.48
flange_width_bottom_mm: 24.5
flange_width_side_mm: 18.3
surface_profile_deviation_top_edge_mm: 0.18
surface_profile_deviation_left_edge_mm: -0.31
surface_profile_deviation_bottom_edge_mm: 0.22
surface_profile_deviation_right_edge_mm: -0.19

# Post-Forming Thickness (thinning measurement)
thickness_zone_1_draw_apex_mm: 0.62
thickness_zone_2_flange_mm: 0.78
thickness_zone_3_transition_mm: 0.71
thinning_percentage_max: 22.5
thinning_location: "draw_apex"
---
# Surface Quality
surface_defect_detected: false
defect_classification: null
defect_severity: null
defect_location_x_mm: null
defect_location_y_mm: null
inspection_image_id: null
---
# Final Disposition
qc_pass_fail: "pass"
scrap_reason_code: null
rework_type: null
rework_destination_line: null
---
# Traceability
part_serial_number: "DOL_20250315_000047"
part_genealogy_coil_to_part: ["JSW_CRS_2025_14728", "BLANK_20250315_001847", "DOL_20250315_A_085473"]
downstream_vehicle_vin_assigned: null  # Assigned during body assembly
```

***

## 4. Die Tooling Management System

### Die Master Record

```yaml
die_set_id: "DIE_DOL_Rev3"
die_part_family: "Door_Outer_Left"
die_revision_level: 3
die_engineering_part_number: "ENG-DOL-P-2023-001-R3"
die_manufacturer: "TIPCO_Pune"
die_manufacturer_part_code: "TIPCO-45821-03"
die_commissioned_date: "2024-11-15"
---
# Physical Specifications
die_tonnage_rating: 800
die_estimated_service_life_strokes: 150000
die_bed_mounting_orientation: "horizontal"
die_components:
  - component_name: "Upper Die Plate"
    material: "Tool Steel H13"
    hardness_hrc: 42
    last_ground_date: "2025-02-28"
  - component_name: "Lower Die Plate"
    material: "Tool Steel H13"
    hardness_hrc: 42
    last_ground_date: "2025-02-28"
  - component_name: "Punch Assembly (hinge holes)"
    qty: 2
    material: "Tool Steel H11"
    wear_criticality: "high"
    replacement_schedule_every_strokes: 100000
  - component_name: "Punch Assembly (lock hole)"
    qty: 1
    material: "Tool Steel H11"
    wear_criticality: "high"
---
# Maintenance Schedule
preventive_maintenance_schedule:
  - action: "Edge sharpening"
    frequency_strokes: 50000
    duration_hours: 4
    last_performed_stroke: 128450
    next_scheduled_stroke: 178450
  - action: "Component inspection (punches)"
    frequency_strokes: 75000
    duration_hours: 6
    last_performed: "2025-02-28"
    next_scheduled: "2025-03-31"
  - action: "Full overhaul (bearing, guides, springs)"
    frequency_strokes: 150000
    duration_hours: 16
    last_performed: "2024-11-15"
    next_scheduled: "2025-06-15"
---
# Current Status
die_current_stroke_count: 128450
die_estimated_remaining_service_life_strokes: 21550
die_health_status: "healthy"  # vs "degraded", "critical", "retired"
die_current_location: "Press_A1_800T"
die_currently_installed: true
die_installation_date: "2025-03-10"
die_planned_removal_date: "2025-03-22"
die_unplanned_failures_ytd: 0
die_quality_complaints_ytd: 1  # Linked to specific part incidents
```

### Die Changeover Event Log

```yaml
changeover_event_id: "CHO_20250315_001"
timestamp_changeover_start: "2025-03-15 05:35:00"
timestamp_changeover_end: "2025-03-15 06:00:00"
changeover_duration_minutes: 25
press_line_id: "Line_A"
press_machine_id: "Press_A1_800T"
---
# Die Exchange
die_removed_id: "DIE_DOR_Rev2"
die_removed_stroke_count_at_removal: 148250
die_removed_reason: "end_of_batch"
die_removed_destination: "storage_bay_C4"
die_installed_id: "DIE_DOL_Rev3"
die_installed_stroke_count_at_installation: 128450
---
# Changeover Breakdown (SMED Analysis)
internal_setup_minutes: 15  # Machine downtime (die clamp, alignment, proving strokes)
external_setup_minutes: 10  # Off-line work (cleaning, inspection, next die prep)
proving_strokes_required: 5
proving_strokes_actual: 6
scrap_parts_during_proving: 1
---
# Personnel
setup_person_id: "SETUP_0445"
setup_person_shift: "Shift_2_Day"
supervision_approval_id: "SUPER_0078"
---
# SMED Target Tracking
smed_target_minutes: 10
smed_actual_minutes: 25
smed_variance_minutes: +15
smed_variance_reason: "alignment_adjustment_required"
smed_improvement_opportunity: "pre_align_die_off_press"
```

### Die Wear & Predictive Maintenance Signals

```yaml
die_condition_assessment_timestamp: "2025-03-15 12:00"
die_set_id: "DIE_DOL_Rev3"
---
# Tonnage Drift Analysis
tonnage_peak_historical_baseline: 615.0
tonnage_peak_current_average_last_100_strokes: 628.5
tonnage_drift_percent: +2.2  # Indicates punch wear or die degradation
tonnage_trend_slope: 0.045  # Tons per 1000 strokes
estimated_strokes_to_critical_tonnage_limit: 16800
---
# Surface Quality Trend
defect_rate_last_week: 1.2
defect_rate_this_week: 2.1
defect_rate_increase_percent: +75
defect_increase_types: ["springback_deviation", "surface_scratches"]
---
# Dimensional Drift
dimension_cpk_trend_last_30_days: 1.85 → 1.62 → 1.41
process_capability_degrading: true
---
# Predictive Signal
tool_remaining_useful_life_estimated_days: 6
tool_remaining_useful_life_estimated_strokes: 21550
recommended_action: "schedule_sharping_within_2_days"
recommended_action_priority: "high"
```

***

## 5. Production Planning & Scheduling System (Multi-Part Context)

### Work Order Entity

```yaml
work_order_id: "WO_2025_03_15_001"
work_order_date: "2025-03-10"
demand_source: "Tata_Auto_Pune_Plant_VIN_123456"
vehicle_model: "Nexon_EV_2025_5_Door"
---
# Line Item: Door Outer Left
line_item_1:
  part_family: "Door_Outer_Left"
  ordered_quantity: 280
  delivery_required_date: "2025-03-16"
  plant_section: "BIW_Door_Station"
  material_spec: "CRS_SPCC_0.8mm"
  ---
# Line Item: Roof Outer
line_item_2:
  part_family: "Roof_Outer"
  ordered_quantity: 200
  delivery_required_date: "2025-03-16"
  plant_section: "BIW_Roof_Station"
  material_spec: "CRS_SPCC_0.6mm"
  ---
# Line Item: Bonnet Outer
line_item_3:
  part_family: "Bonnet_Outer"
  ordered_quantity: 220
  delivery_required_date: "2025-03-16"
  plant_section: "BIW_Bonnet_Station"
  material_spec: "HSLA_350_0.8mm"
```

### Production Schedule (Master Plan)

```yaml
schedule_id: "SCHED_2025_03_15_SHIFT_2"
schedule_date: "2025-03-15"
shift_id: "Shift_2_Day"
planned_start_time: "06:00"
planned_end_time: "14:00"
shift_duration_minutes: 480
---
batch_sequence:
  - sequence: 1
    part_family: "Door_Outer_Left"
    batch_id: "BATCH_DOL_20250315_01"
    planned_start: "06:00"
    planned_duration_minutes: 75
    planned_quantity: 140
    assigned_line: "Line_A"
    assigned_die: "DIE_DOL_Rev3"
    material_coil: "JSW_CRS_2025_14728"
  
  - sequence: 2
    part_family: "Door_Outer_Right"
    batch_id: "BATCH_DOR_20250315_01"
    planned_start: "07:15"
    planned_duration_minutes: 70
    planned_quantity: 140
    assigned_line: "Line_A"
    assigned_die: "DIE_DOR_Rev2"
    material_coil: "JSW_CRS_2025_14729"
    changeover_from_sequence_1: true
    estimated_changeover_time_minutes: 20
  
  - sequence: 3
    part_family: "Roof_Outer"
    batch_id: "BATCH_RO_20250315_01"
    planned_start: "08:00"  # Can run parallel on Line_B while Line_A finishes Door_Outer_Right
    planned_duration_minutes: 120
    planned_quantity: 200
    assigned_line: "Line_B"
    assigned_die: "DIE_RO_Rev4"
    material_coil: "NIPPON_SPCC_2025_08812"
  
  - sequence: 4
    part_family: "Bonnet_Outer"
    batch_id: "BATCH_BO_20250315_01"
    planned_start: "08:30"  # Parallel on Line_C
    planned_duration_minutes: 150
    planned_quantity: 220
    assigned_line: "Line_C"
    assigned_die: "DIE_BO_Rev5"
    material_coil: "SAIL_HSLA350_2025_19441"
---
# Line Utilization Plan
line_a_utilization_percent: 89.6
line_b_utilization_percent: 75.0
line_c_utilization_percent: 62.5
line_d_utilization_percent: 92.0  # Inner panels + brackets
overall_plant_utilization_target: 78.0
---
# Constraint Analysis
critical_bottleneck: "Line_C_Bonnet_Deep_Draw"
constraint_reason: "High tonnage requirement for HSLA material limits SPM"
recommended_mitigation: "Split bonnet order across Line_B on secondary shift"
```

***

## 6. Enhanced Quality Inspection System (Multi-Part Taxonomies)

### Part-Family-Specific Dimensional Specs

#### Door Outer Panel Quality Schema

```yaml
part_family: "Door_Outer"
quality_level: "Class_A"  # Customer-visible, high cosmetic standard
---
critical_dimensions:
  - dimension: "Overall_Length"
    nominal_mm: 1090
    tolerance_minus_mm: 1.5
    tolerance_plus_mm: 1.5
    cpk_target: 1.33
    measurement_frequency: "every_10_parts"
    measurement_method: "CMM_arm"
  
  - dimension: "Draw_Depth"
    nominal_mm: 152.5
    tolerance_minus_mm: 0.8
    tolerance_plus_mm: 0.8
    cpk_target: 1.67
    measurement_frequency: "every_5_parts"
    measurement_method: "depth_gauge"
    notes: "Critical for BIW fit; tight tolerance due to assembly interface"
  
  - dimension: "Flange_Width_Bottom"
    nominal_mm: 24.0
    tolerance_minus_mm: 0.5
    tolerance_plus_mm: 0.5
    measurement_frequency: "every_10_parts"
    notes: "Related to door frame engagement and gap control"
---
defect_taxonomy:
  - defect_class: "Springback"
    severity: "major"
    description: "Elastic recovery after forming; exceeds ±1.0mm deviation"
    root_causes: ["material_yield_strength_high", "die_temperature_low", "tool_wear"]
    corrective_actions: ["increase_die_temperature", "adjust_cushion_pressure", "schedule_die_sharpening"]
    frequency_baseline: 0.8
    frequency_target: 0.3
  
  - defect_class: "Surface_Scratch"
    severity: "major"
    description: "Visible surface marring from die contact or material handling"
    root_causes: ["die_surface_contamination", "blank_sliding_during_draw", "handling_damage"]
    defect_threshold_length_mm: 10
  
  - defect_class: "Burr"
    severity: "minor"
    description: "Sharp edge from trimming or piercing operations"
    root_causes: ["punch_wear", "die_clearance_excessive", "material_hardness_variation"]
    typical_location: "hole_edges"
    deburr_method: "vibratory_deburr"
---
acceptance_criteria:
  - metric: "First_Pass_Yield"
    target_percent: 97.0
  - metric: "Cpk_All_Critical_Dims"
    target: 1.33
  - metric: "Surface_Defect_Count_Per_1000"
    target: 5
```

#### Roof Panel Quality Schema

```yaml
part_family: "Roof_Outer"
quality_level: "Class_A"
notes: "Highest cosmetic standard; customer-visible; exposed to weathering"
---
critical_dimensions:
  - dimension: "Surface_Profile_Deviation"
    tolerance_mm: ±0.5
    cpk_target: 1.67
    notes: "Class A surface requires very tight profile control; critical for panel gap perception"
    measurement_method: "laser_profiling"  # More accurate than CMM for large panels
    sampling_frequency: "every_5_parts"
  
  - dimension: "Roof_Curvature_Radius"
    nominal_radius_mm: 1200
    tolerance_mm: ±20
    notes: "Structural and aesthetic requirement; affects water drainage"
  
  - dimension: "Attachment_Hole_Pattern"
    positional_tolerance_mm: ±0.3
    hole_qty: 4
    notes: "Roof rail mounting; tight tolerance for structural stiffness"
---
material_specific_concerns:
  - material: "AHSS_DP600"
    tensile_strength_range_mpa: [600, 700]
    springback_risk: "high"
    thinning_max_percent: 25
    forming_sequence_required: "hydromechanical_deep_draw"  # Staged forming
  - material: "CRS_SPCC"
    tensile_strength_mpa: 340
    springback_risk: "moderate"
    thinning_max_percent: 18
---
defect_taxonomy:
  - defect_class: "Oil_Canning"
    severity: "major"
    description: "Localized surface flexing/buckling due to low panel stiffness post-forming"
    root_causes: ["insufficient_material_strength", "underforming", "inadequate_reinforcement"]
    detection_method: "visual_inspection_under_light"
  
  - defect_class: "Springback_Curvature"
    severity: "major"
    description: "Roof panel develops unwanted curvature after unloading from die"
    root_causes: ["material_yield_strength_excessive", "hydro_draw_pressure_inadequate"]
    measurement: "laser_profiling_at_5_zones"
```

#### Bonnet Panel Quality Schema

```yaml
part_family: "Bonnet_Outer"
quality_level: "Class_A"
material_spec: "HSLA_350 / DP600"
notes: "Deep-draw complex geometry; high strength material; Class A surface"
---
critical_dimensions:
  - dimension: "Draw_Depth_at_Apex"
    nominal_mm: 185
    tolerance_mm: ±2.0
    cpk_target: 1.33
    notes: "Large draw; requires precise control to avoid splits or excessive thinning"
  
  - dimension: "Surface_Profile_Entire_Panel"
    tolerance_mm: ±0.8
    sampling: "50_point_laser_scan"
    notes: "Complex double-curved surface; laser profiling required for full geometry"
  
  - dimension: "Hinge_Bracket_Position"
    positional_tolerance_mm: ±0.5
    qty_brackets: 2
    notes: "Bonnet opening/closing mechanism; critical for alignment"
---
material_specific_quality_drivers:
  - material: "HSLA_350"
    yield_strength_mpa: 350
    tensile_strength_mpa: 450
    elongation_percent: 22
    strain_hardening: "present"  # Work-hardening during draw increases strength but reduces ductility
    thinning_risk: "high"
    thinning_max_allowable_percent: 30
    forming_stages: 3  # Multi-stage draw required for complex geometry
  - material: "DP600"
    dual_phase: true
    ferrite_matrix: true
    martensite_islands: true
    springback_tendency: "significant"  # Requires post-forming stress relief
---
defect_taxonomy:
  - defect_class: "Splitting_Rupture"
    severity: "critical"
    description: "Material failure/tearing at draw apex or transition zones"
    root_causes: ["material_yield_low", "draw_progression_inadequate", "lubricant_film_breakdown"]
    scrap_result: true
    typical_location: "draw_apex"
  
  - defect_class: "Necking"
    severity: "major"
    description: "Localized thinning preceding split; deformation instability"
    root_causes: ["material_property_variation_from_lot", "draw_speed_excessive"]
  
  - defect_class: "Mouse_Ears"
    severity: "minor"
    description: "Localized deflection/bulging near panel boundaries from uneven stretch"
    root_causes: ["blank_holder_pressure_non_uniform", "material_flow_imbalance"]
    cosmetic_only: true  # Trimmed off in secondary operation
```

***

## 7. Material Supply System Integration

### Coil Master Record (Multi-Part Linkage)

```yaml
coil_id: "JSW_CRS_2025_14728"
supplier_id: "JSW_Steel_Limited_Bengaluru"
coil_part_number: "CRS-SPCC-08-750"
supplier_coil_reference: "JCR-27189-A"
---
material_specification:
  grade: "CRS_SPCC"  # Commercial drawing steel
  thickness_nominal_mm: 0.8
  thickness_tolerance_mm: ±0.05
  coil_width_mm: 1200
  coil_outer_diameter_mm: 1400
  coil_inner_diameter_mm: 508
  coil_weight_kg: 3200
  rolling_date: "2025-02-18"
  heat_treatment: "annealed"
---
certification_data:
  tensile_strength_mpa: 340
  yield_strength_mpa: 170
  elongation_percent: 38
  hardness_hb: 94
  formability_index: "0.42"  # Based on work-hardening exponent
  deep_drawing_index: "good"
---
intended_parts_for_coil:
  - part_family: "Door_Outer_Left"
    qty_expected: 1400  # How many parts can be stamped from this coil
    batch_reference: ["BATCH_DOL_20250315_01", "BATCH_DOL_20250316_01"]
  - part_family: "Door_Outer_Right"
    qty_expected: 1400
    batch_reference: ["BATCH_DOR_20250315_01"]
  - part_family: "Door_Inner_Left"
    qty_expected: 1800  # Smaller parts, higher density
    batch_reference: ["BATCH_DIL_20250316_01"]
---
# Coil lifecycle tracking
coil_received_date: "2025-02-25"
coil_inspection_status: "passed"
coil_storage_location: "Coil_Rack_A_Level_3"
coil_mounted_on_press_date: "2025-03-15"
coil_mounted_press_line: "Line_A"
coil_remaining_weight_kg: 890  # After blanking
parts_stamped_from_coil: 1847
parts_stamped_good_quality: 1823
parts_stamped_scrap: 24
actual_yield_percent: 98.7
coil_depleted_date: "2025-03-18"
coil_remnant_weight_kg: 45
coil_remnant_disposition: "scrap"
---
# Traceability: Part genealogy links to coil
part_ids_from_coil: ["DOL_20250315_A_*", "DOL_20250315_B_*", ...]
```

### Supplier Quality Scorecard (Multi-Part Impact)

```yaml
scorecard_period: "2025_Q1"
supplier_id: "JSW_Steel_Limited_Bengaluru"
---
quality_metrics:
  - metric: "On_Time_Delivery_Percent"
    target: 98.0
    actual: 96.5
    status: "miss"
  
  - metric: "Certificate_of_Conformance_Acceptance"
    target: 100
    actual: 100
    status: "pass"
  
  - metric: "Incoming_Inspection_Reject_Rate_Percent"
    target: 0.5
    actual: 1.2
    status: "miss"
    detail: "3 coils out of 250 rejected for hardness out of spec"
  
  - metric: "Defect_Rate_In_Finished_Parts_Percent"
    target: 2.0
    actual: 2.8
    status: "miss"
    detail:
      - part_family: "Door_Outer"
        defect_rate: 1.5
        primary_defect: "springback_deviation"
        root_cause_analysis: "High yield strength in this lot (180 MPa vs. 170 nominal)"
      - part_family: "Door_Inner"
        defect_rate: 3.2
        primary_defect: "surface_scratches"
        root_cause_analysis: "Surface oxidation on coil due to storage humidity"
      - part_family: "Roof_Outer"
        defect_rate: 5.1
        primary_defect: "necking_and_splits"
        root_cause_analysis: "Thickness variation (+0.08mm in zones) caused uneven draw"
---
corrective_actions_required:
  - action_id: "CA_JSW_2025_001"
    date_issued: "2025-03-20"
    issue: "Thickness variation exceeds tolerance"
    corrective_action: "Implement 100% thickness profiling before coil dispatch"
    target_completion: "2025-05-01"
    follow_up_date: "2025-04-15"
  
  - action_id: "CA_JSW_2025_002"
    date_issued: "2025-03-20"
    issue: "Yield strength lot variation causing springback issues in Door_Outer parts"
    corrective_action: "Narrow annealing window specification (target YS 170±5 MPa)"
    target_completion: "2025-04-15"
---
supplier_rating_score: 78  # Out of 100; below target 85
supplier_status: "on_probation"
supplier_future_allocation: "reduced_to_30_percent_of_volume"
```

***

## 8. Aggregate Statistics & KPIs (Multi-Part)

### Daily Shift Summary (Multi-Line, Multi-Part)

```yaml
shift_summary_id: "SHIFT_SUM_20250315_SHIFT2"
shift_date: "2025-03-15"
shift_id: "Shift_2_Day"
shift_start_time: "06:00"
shift_end_time: "14:00"
shift_duration_minutes: 480
---
# Line-by-Line Production
line_a_production:
  line_id: "Line_A"
  press_capacity_tons: 800
  parts_produced_total: 287
  parts_produced_good: 282
  scrap_count: 5
  first_pass_yield_percent: 98.3
  downtime_minutes: 42
  changeover_events: 2
  material_coils_used: 2
  estimated_oee_percent: 81.2
  
line_b_production:
  line_id: "Line_B"
  press_capacity_tons: 1000
  parts_produced_total: 195
  parts_produced_good: 188
  scrap_count: 7
  first_pass_yield_percent: 96.4
  downtime_minutes: 58
  changeover_events: 1
  estimated_oee_percent: 74.5

line_c_production:
  line_id: "Line_C"
  press_capacity_tons: 1200
  parts_produced_total: 218
  parts_produced_good: 209
  scrap_count: 9
  first_pass_yield_percent: 95.9
  downtime_minutes: 75  # Complex Bonnet deep draws require more setup
  changeover_events: 1
  estimated_oee_percent: 68.3

line_d_production:
  line_id: "Line_D"
  press_capacity_tons: 600
  parts_produced_total: 542
  parts_produced_good: 538
  scrap_count: 4
  first_pass_yield_percent: 99.3
  downtime_minutes: 20
  changeover_events: 2
  estimated_oee_percent: 88.9
---
# Aggregate Plant Metrics
total_parts_produced: 1242
total_parts_good: 1217
total_parts_scrap: 25
plant_first_pass_yield_percent: 98.0
plant_scrap_rate_percent: 2.0
plant_downtime_minutes: 195
planned_production_time_minutes: 1920  # 4 lines × 480 min
actual_production_time_minutes: 1725
availability_percent: 89.9
---
# Material Yield (Weight-Based)
total_material_input_kg: 4287
total_material_output_good_parts_kg: 2124
total_material_output_scrap_kg: 612
total_material_trimming_waste_kg: 1551
effective_material_yield_percent: 49.6  # (2124 / 4287) × 100
---
# OEE Breakdown
plant_oee_availability_percent: 89.9
plant_oee_performance_percent: 91.2
plant_oee_quality_percent: 98.0
plant_oee_combined_percent: 80.1
oee_target_percent: 85.0
oee_variance_percent: -4.9
---
# Defect Analysis by Part Family
scrap_by_part_family:
  - part_family: "Door_Outer"
    scrap_count: 2
    scrap_rate_percent: 0.7
    primary_defect: "springback_deviation"
    corrective_action: "increase_die_temperature"
  
  - part_family: "Door_Inner"
    scrap_count: 1
    scrap_rate_percent: 0.2
    primary_defect: "piercing_burst"
    root_cause: "punch_wear"
  
  - part_family: "Roof_Outer"
    scrap_count: 7
    scrap_rate_percent: 3.5
    primary_defect: "necking_splits"
    root_cause: "coil_thickness_variation_from_supplier"
    corrective_action_issued: "CA_JSW_2025_001"
  
  - part_family: "Bonnet_Outer"
    scrap_count: 9
    scrap_rate_percent: 4.1
    primary_defect: "drawing_failure_necking"
    root_cause: "forming_pressure_insufficient_for_HSLA_material_batch"
    corrective_action: "adjust_cushion_pressure_87→92_bar"
  
  - part_family: "Bonnet_Inner"
    scrap_count: 4
    scrap_rate_percent: 2.2
    primary_defect: "surface_scratches"
    root_cause: "material_handling_bin_condition_degraded"
---
# Die Wear Progression (Predictive)
die_condition_summary:
  - die_id: "DIE_DOL_Rev3"
    stroke_count: 128450
    remaining_service_life_strokes: 21550
    health_status: "healthy"
    next_maintenance: "edge_sharpening_in_3_days"
  
  - die_id: "DIE_DOR_Rev2"
    stroke_count: 148250
    remaining_service_life_strokes: 1750
    health_status: "critical"
    next_maintenance: "immediate_full_overhaul"
    production_hold_recommendation: true
    impact: "Door_Outer_Right production must pause until Die overhaul completed"
```

***

## 9. Data Governance & Multi-System Integration Points

### Cross-System Data Synchronization

| Source System | Target System | Data Flow | Sync Frequency | Integration Method |
|--------------|--------------|-----------|----------------|-------------------|
| Press Line Data System | Quality Inspection System | Part ID, timestamp, tonnage signature | Real-time | MQTT topic subscription |
| Die Tooling Management | Production Planning | Die health status, remaining service life | Hourly | REST API |
| Material Supply System | Press Line Data System | Coil properties, batch info | At coil mount | Database trigger |
| Production Planning | Quality Inspection | Expected spec by part family | Batch start | SQL query |
| Quality Inspection | Material Supply | Defect root cause linkage to coil | Post-shift batch | ETL job |
| Logistics/Traceability | All Systems | Part genealogy, destination vehicle | Part completion | Event log |

### Master Data Management (MDM)

**Part Family Master**
- Part family code, description, print number, specification document
- Associated die sets, compatible press lines, material grades
- Quality dimension specifications (part-family-specific)
- BOM linkage (roof outer → roof reinforcement → vehicle assembly)

**Press Configuration Master**
- Press line ID, machine model, tonnage, specifications
- Compatible die interfaces, coil width limits, speed ranges
- Maintenance schedule, OEE baseline targets
- Operator certifications required

**Die Tooling Master**
- Die ID, part family mapping, revision level
- Service life, maintenance schedule, component inventory
- Supplier, cost, lead time for replacement
- Current location, installation date, expected removal

**Material Grade Master**
- Grade code (CRS_SPCC, HSLA_350, etc.)
- Properties (YS, TS, elongation, formability)
- Approved suppliers, cost per kg, lead time
- Suitable part families, forming constraints

**Defect Master**
- Defect class code, description, severity level
- Part families where applicable, scrap/rework decision rules
- Root cause codes, corrective action mappings
- SPC control limits

***

## 10. Advanced Multi-Part Analytics Use Cases

### 1. Multi-Part Scheduling Optimization
**Input**: Production demand (doors, roof, bonnet), press capacity, changeover times, material availability, die health
**Target variable**: Minimize total cycle time, changeovers, inventory
**Model**: Mixed-integer linear programming (MILP) or constraint programming
**Outcome**: Optimal batch sequencing across 5 press lines to meet demand with 15% fewer changeovers

### 2. Supply Chain Quality Correlation
**Input**: Supplier coil properties (YS, TS, thickness distribution), defect data by part family
**Target variable**: Defect rate per coil lot
**Model**: Logistic regression, decision tree
**Outcome**: Identify coil property ranges that predict defects in roof/bonnet deep-draw operations; feed back to supplier specs

### 3. Die Wear Prediction & Maintenance Scheduling
**Input**: Tonnage drift, defect rate trend, stroke count, material grade processed
**Target variable**: Strokes until die fails or quality unacceptable
**Model**: Exponential/Weibull survival model, Cox proportional hazards
**Outcome**: Predict die failure 5–10 days ahead; schedule maintenance to avoid unplanned downtime; reduce scrap from worn tooling

### 4. Process Resilience & Material Lot Impact
**Input**: Yield strength variation within supplier lot, forming pressure, draw depth, punch wear state
**Target variable**: Split/necking defect occurrence
**Model**: Logistic regression with interaction terms (YS × draw_depth × pressure)
**Outcome**: Identify critical parameter combinations for each material lot; auto-adjust cushion pressure by 5 MPa when lot property variance detected

### 5. Multi-Line Constraint Bottleneck Detection
**Input**: Hourly production, downtime events, die health, material availability across all 5 lines
**Target variable**: Plant-wide throughput vs. demand
**Model**: Discrete event simulation (DES), constraint theory (Theory of Constraints)
**Outcome**: Identify shifting bottleneck (e.g., Line_C Bonnet complex draws); recommend temporary production shift to parallel lines or external partner

### 6. OEE Variance Root Cause (Multi-Part Context)
**Input**: OEE components (availability, performance, quality) disaggregated by part family, press line, material lot, operator
**Target variable**: Why is overall plant OEE 80% vs. 85% target?
**Model**: ANOVA decomposition, variance partitioning
**Outcome**: E.g., "Roof panel OEE = 68% due to: 60% from HSLA material lot thickness variation (roots at supplier), 25% from Line_C high downtime (tool changeover SMED not optimized), 15% from operator skill variance"

***

## 11. Data Schema Summary Table

| Entity | Record Frequency | Volume (per shift) | Key Fields | Relationships |
|--------|-----------------|------------------|-----------|----------------|
| Production Batch | Per work order (~5-8/shift) | 6-8 | batch_id, part_family, press_line, die, material_coil, qty | References: WO, press, die, material |
| Individual Part | Per stamped part | ~1,200 | part_id, batch_id, press_line, die_id, coil_id, tonnage, dimensions, defect_flag | References: batch, press, die, coil, quality_result |
| Die Changeover Event | Per setup (~6-10/shift) | 8-10 | changeover_id, die_from, die_to, timestamp, duration, smed_variance | References: press_line, die_removed, die_installed |
| Quality Inspection | Sampled (every 5-10 parts) | ~120-150/shift | inspection_id, part_id, dimensions (20-30 per part type), defect_class, pass_fail | References: part, defect_master |
| Coil Lifecycle | Per coil used (~2-3/shift per line) | 8-12 | coil_id, mounted_date, line, weight_used, parts_produced, scrap, yield | References: supplier, material_grade, parts |
| Die Condition Assessment | Per shift or on-demand | 5-10 | die_id, stroke_count, tonnage_drift, defect_rate_trend, health_status, maintenance_recommendation | References: die_master, production |
| Shift Summary | End of shift | 1 per shift | shift_summary_id, line_summaries, plant_oee, first_pass_yield, scrap_analysis, downtime_breakdown | Aggregates: all part, batch, inspection data |

***

## 12. Implementation Roadmap

### Phase 1: Foundation (Months 1–2)
- Deploy tonnage monitoring and coil traceability on Line A & B
- Implement part genealogy (coil → part) with QR codes
- Build basic shift summary dashboard (OEE, yield by line)
- Establish die maintenance event logging

### Phase 2: Integration (Months 3–4)
- Integrate Quality Inspection System (CMM data, defect classification)
- Connect Production Planning System (work order → press line assignment)
- Implement supplier coil property data ingestion
- Build multi-line production schedule view

### Phase 3: Analytics & Optimization (Months 5–6)
- Deploy predictive die maintenance model
- Develop multi-part scheduling optimization algorithm
- Implement supply chain quality correlation analysis
- Build constrained optimization dashboard for operator decision support

### Phase 4: Continuous Improvement (Ongoing)
- Expand analytics to all 5 press lines
- Implement real-time anomaly detection (tonnage, dimensions)
- Build supplier scorecard feedback loop
- Deploy SMED tracking and improvement workflow

***

## Summary

This comprehensive multi-part stamping plant dataset plan provides a realistic, interconnected view of automotive body panel manufacturing across doors, roofs, and bonnets. The architecture captures:

- **Multi-system integration** linking press operations, tooling, material supply, quality, planning, and logistics
- **Part-family-specific quality and process parameters** reflecting different forming pressures, material grades, dimensional tolerances, and defect modes
- **Complex production scheduling** with multi-line parallelization, changeover management, and bottleneck dynamics
- **Supplier traceability** correlating material lot properties to downstream defects in finished parts
- **Predictive maintenance** for dies with realistic service life, wear progression, and optimal maintenance timing
- **OEE analytics** decomposed across multiple lines, part families, and operational factors
- **Advanced optimization** spanning scheduling, process parameters, supply chain collaboration, and constraint management

The dataset enables manufacturers to transition from reactive problem-solving to predictive, data-driven continuous improvement across a complex, multi-part production environment typical of automotive Tier-1 supplier plantsants.

[1](https://www.worldgroupmachine.com/power-press-machine-tonnage-calculation-guide/)
[2](https://ahssinsights.org/forming/press-requirements/press-tonnage-predictions/)
[3](https://www.sciencedirect.com/topics/engineering/body-panel)
[4](https://alsettevs.com/what-is-stamping-in-automotive-manufacturing/)
[5](https://www.justdial.com/Bangalore/Automobile-Body-Panel-Manufacturers/nct-12075353)
[6](https://steelprogroup.com/automotive-steel/car-body-panel/)
[7](https://www.hidakausainc.com/case-studies/prototype-automotive-body-panel-assembly)
[8](https://www.violintec.com/sheet-metal-and-stamped-parts/an-overview-of-progressive-die-stamping/)
[9](https://www.6sigma.us/lean-tools/single-minute-exchange-of-die-smed/)
[10](https://european-aluminium.eu/wp-content/uploads/2022/11/5_6_aam_roof-and-trim.pdf)
[11](https://www.keatsmfg.com/blog/difference-multi-slide-progressive-die-stamping/)
[12](https://sixsigmastudyguide.com/single-minute-exchange-of-die/)
[13](https://www.guangduanpresses.com/mechanical-stamping-press-for-automotive-parts.html)
[14](https://www.nationalmaterial.com/metal-stamping-101-understanding-the-metal-stamping-process/)
[15](https://worldpressmachine.en.made-in-china.com/product/wFXtuWoUnrVT/China-Auto-Parts-Automatic-Stamping-Press-with-Coil-Feeding-Line.html)
[16](https://www.schulergroup.com/major/download_center/broschueren_stamping_cutting/download_stamping_cutting/stamping_cutting_broschuere_stanzsysteme_umformsysteme_e.pdf)
[17](https://www.metalformingmagazine.com/article/?%2Fcoil-and-sheet-handling%2Ffeeders%2Fproblem-solving-press-feeds)
[18](https://formingworld.com/handbook-biw-structure-design/)
[19](https://www.dreher.de/en-de/sheet-metal-forming/stamping-presses)
[20](https://www.reidsupply.com/en-us/industry-news/automotive-biw-welding-and-assembly-workholding)
