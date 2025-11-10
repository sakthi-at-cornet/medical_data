cube(`PartFamilyPerformance`, {
  sql: `SELECT * FROM staging_marts.agg_part_family_performance`,

  joins: {

  },

  dimensions: {
    partFamily: {
      sql: `part_family`,
      type: `string`,
      primaryKey: true,
      title: `Part Family`
    },

    partType: {
      sql: `part_type`,
      type: `string`,
      title: `Part Type`
    },

    materialGrade: {
      sql: `material_grade`,
      type: `string`,
      title: `Material Grade`
    },

    firstProductionDate: {
      sql: `first_production_date`,
      type: `time`,
      title: `First Production Date`
    },

    lastProductionDate: {
      sql: `last_production_date`,
      type: `time`,
      title: `Last Production Date`
    }
  },

  measures: {
    totalPartsProduced: {
      sql: `total_parts_produced`,
      type: `sum`,
      title: `Total Parts Produced`
    },

    partsPassed: {
      sql: `parts_passed`,
      type: `sum`,
      title: `Parts Passed`
    },

    partsFailed: {
      sql: `parts_failed`,
      type: `sum`,
      title: `Parts Failed`
    },

    firstPassYield: {
      sql: `first_pass_yield_pct`,
      type: `avg`,
      title: `First Pass Yield %`,
      format: `percent`
    },

    reworkRate: {
      sql: `rework_rate_pct`,
      type: `avg`,
      title: `Rework Rate %`,
      format: `percent`
    },

    uniqueDefectTypes: {
      sql: `unique_defect_types`,
      type: `sum`,
      title: `Unique Defect Types`
    },

    avgOee: {
      sql: `avg_oee`,
      type: `avg`,
      title: `Average OEE`,
      format: `percent`
    },

    avgAvailability: {
      sql: `avg_availability`,
      type: `avg`,
      title: `Average Availability`,
      format: `percent`
    },

    avgPerformance: {
      sql: `avg_performance`,
      type: `avg`,
      title: `Average Performance`,
      format: `percent`
    },

    avgQualityRate: {
      sql: `avg_quality_rate`,
      type: `avg`,
      title: `Average Quality Rate`,
      format: `percent`
    },

    avgTonnage: {
      sql: `avg_tonnage`,
      type: `avg`,
      title: `Average Tonnage (T)`,
      format: `number`
    },

    avgCycleTime: {
      sql: `avg_cycle_time`,
      type: `avg`,
      title: `Average Cycle Time (s)`,
      format: `number`
    },

    avgCostPerPart: {
      sql: `avg_cost_per_part`,
      type: `avg`,
      title: `Average Cost Per Part`,
      format: `currency`
    },

    totalProductionCost: {
      sql: `total_production_cost`,
      type: `sum`,
      title: `Total Production Cost`,
      format: `currency`
    },

    avgMaterialCost: {
      sql: `avg_material_cost`,
      type: `avg`,
      title: `Average Material Cost`,
      format: `currency`
    },

    avgLaborCost: {
      sql: `avg_labor_cost`,
      type: `avg`,
      title: `Average Labor Cost`,
      format: `currency`
    },

    avgCoilDefectRate: {
      sql: `avg_coil_defect_rate`,
      type: `avg`,
      title: `Average Coil Defect Rate`,
      format: `percent`
    },

    avgMaterialYieldStrength: {
      sql: `avg_material_yield_strength`,
      type: `avg`,
      title: `Average Material Yield Strength (MPa)`,
      format: `number`
    },

    avgMaterialTensileStrength: {
      sql: `avg_material_tensile_strength`,
      type: `avg`,
      title: `Average Material Tensile Strength (MPa)`,
      format: `number`
    },

    productionDays: {
      sql: `production_days`,
      type: `sum`,
      title: `Total Production Days`
    }
  }
});
