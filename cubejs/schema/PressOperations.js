cube(`PressOperations`, {
  sql: `SELECT * FROM staging_marts.fact_press_operations`,

  joins: {

  },

  dimensions: {
    productionKey: {
      sql: `production_key`,
      type: `number`,
      primaryKey: true
    },

    partId: {
      sql: `part_id`,
      type: `string`,
      title: `Part ID`
    },

    pressLineId: {
      sql: `press_line_id`,
      type: `string`,
      title: `Press Line`
    },

    lineName: {
      sql: `line_name`,
      type: `string`,
      title: `Line Name`
    },

    dieId: {
      sql: `die_id`,
      type: `string`,
      title: `Die ID`
    },

    partFamily: {
      sql: `part_family`,
      type: `string`,
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

    coilId: {
      sql: `coil_id`,
      type: `string`,
      title: `Coil ID`
    },

    shiftId: {
      sql: `shift_id`,
      type: `string`,
      title: `Shift`
    },

    operatorId: {
      sql: `operator_id`,
      type: `string`,
      title: `Operator`
    },

    qualityStatus: {
      sql: `quality_status`,
      type: `string`,
      title: `Quality Status`
    },

    defectType: {
      sql: `defect_type`,
      type: `string`,
      title: `Defect Type`
    },

    defectSeverity: {
      sql: `defect_severity`,
      type: `string`,
      title: `Defect Severity`
    },

    tonnageCategory: {
      sql: `tonnage_category`,
      type: `string`,
      title: `Tonnage Category`
    },

    oeeCategory: {
      sql: `oee_category`,
      type: `string`,
      title: `OEE Category`
    },

    productionTimestamp: {
      sql: `production_timestamp`,
      type: `time`,
      title: `Production Timestamp`
    },

    productionDate: {
      sql: `production_date`,
      type: `time`,
      title: `Production Date`
    },

    isWeekend: {
      sql: `is_weekend`,
      type: `boolean`,
      title: `Is Weekend`
    }
  },

  measures: {
    count: {
      type: `count`,
      title: `Total Parts Produced`
    },

    passedCount: {
      sql: `quality_flag`,
      type: `count`,
      filters: [{
        sql: `${CUBE}.quality_flag = true`
      }],
      title: `Parts Passed`
    },

    failedCount: {
      sql: `quality_flag`,
      type: `count`,
      filters: [{
        sql: `${CUBE}.quality_flag = false`
      }],
      title: `Parts Failed`
    },

    passRate: {
      sql: `CAST(${passedCount} AS DOUBLE PRECISION) * 100.0 / NULLIF(CAST(${count} AS DOUBLE PRECISION), 0)`,
      type: `number`,
      format: `percent`,
      title: `Pass Rate %`
    },

    avgTonnage: {
      sql: `tonnage_peak`,
      type: `avg`,
      title: `Average Tonnage (T)`,
      format: `number`
    },

    avgCycleTime: {
      sql: `cycle_time_seconds`,
      type: `avg`,
      title: `Average Cycle Time (s)`,
      format: `number`
    },

    avgStrokeRate: {
      sql: `stroke_rate_spm`,
      type: `avg`,
      title: `Average Stroke Rate (SPM)`,
      format: `number`
    },

    avgOee: {
      sql: `oee`,
      type: `avg`,
      title: `Average OEE`,
      format: `percent`
    },

    avgAvailability: {
      sql: `availability`,
      type: `avg`,
      title: `Average Availability`,
      format: `percent`
    },

    avgPerformance: {
      sql: `performance`,
      type: `avg`,
      title: `Average Performance`,
      format: `percent`
    },

    avgQualityRate: {
      sql: `quality_rate`,
      type: `avg`,
      title: `Average Quality Rate`,
      format: `percent`
    },

    totalCost: {
      sql: `total_cost_per_unit`,
      type: `sum`,
      title: `Total Production Cost`,
      format: `currency`
    },

    avgCostPerPart: {
      sql: `total_cost_per_unit`,
      type: `avg`,
      title: `Average Cost Per Part`,
      format: `currency`
    },

    avgMaterialCost: {
      sql: `material_cost_per_unit`,
      type: `avg`,
      title: `Average Material Cost`,
      format: `currency`
    },

    avgLaborCost: {
      sql: `labor_cost_per_unit`,
      type: `avg`,
      title: `Average Labor Cost`,
      format: `currency`
    },

    avgEnergyCost: {
      sql: `energy_cost_per_unit`,
      type: `avg`,
      title: `Average Energy Cost`,
      format: `currency`
    },

    avgSurfaceDeviation: {
      sql: `surface_profile_deviation_mm`,
      type: `avg`,
      title: `Average Surface Deviation (mm)`,
      format: `number`
    },

    defectCount: {
      sql: `defect_type`,
      type: `count`,
      filters: [{
        sql: `${CUBE}.defect_type IS NOT NULL`
      }],
      title: `Defect Count`
    },

    reworkCount: {
      sql: `rework_required`,
      type: `count`,
      filters: [{
        sql: `${CUBE}.rework_required = true`
      }],
      title: `Rework Count`
    }
  },

  preAggregations: {
    main: {
      measures: [count, passedCount, failedCount, avgOee, totalCost],
      dimensions: [partFamily, pressLineId, partType],
      timeDimension: productionDate,
      granularity: `day`,
      refreshKey: {
        every: `1 hour`
      }
    },

    byShift: {
      measures: [count, avgOee, avgCostPerPart],
      dimensions: [partFamily, shiftId],
      timeDimension: productionDate,
      granularity: `day`,
      refreshKey: {
        every: `1 hour`
      }
    }
  }
});
