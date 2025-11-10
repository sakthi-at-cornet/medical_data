cube(`PressLineUtilization`, {
  sql: `SELECT * FROM staging_marts.agg_press_line_utilization`,

  joins: {

  },

  dimensions: {
    pressLineId: {
      sql: `press_line_id`,
      type: `string`,
      primaryKey: true,
      title: `Press Line ID`
    },

    lineName: {
      sql: `line_name`,
      type: `string`,
      title: `Line Name`
    },

    partType: {
      sql: `part_type`,
      type: `string`,
      title: `Part Type`
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

    totalPartsPassed: {
      sql: `total_parts_passed`,
      type: `sum`,
      title: `Total Parts Passed`
    },

    totalPartsFailed: {
      sql: `total_parts_failed`,
      type: `sum`,
      title: `Total Parts Failed`
    },

    avgPassRate: {
      sql: `avg_pass_rate_pct`,
      type: `avg`,
      title: `Average Pass Rate %`,
      format: `percent`
    },

    overallAvgOee: {
      sql: `overall_avg_oee`,
      type: `avg`,
      title: `Overall Average OEE`,
      format: `percent`
    },

    overallAvgAvailability: {
      sql: `overall_avg_availability`,
      type: `avg`,
      title: `Overall Average Availability`,
      format: `percent`
    },

    overallAvgPerformance: {
      sql: `overall_avg_performance`,
      type: `avg`,
      title: `Overall Average Performance`,
      format: `percent`
    },

    overallAvgQualityRate: {
      sql: `overall_avg_quality_rate`,
      type: `avg`,
      title: `Overall Average Quality Rate`,
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

    totalCost: {
      sql: `total_cost`,
      type: `sum`,
      title: `Total Cost`,
      format: `currency`
    },

    avgCostPerUnit: {
      sql: `avg_cost_per_unit`,
      type: `avg`,
      title: `Average Cost Per Unit`,
      format: `currency`
    },

    totalProductionDays: {
      sql: `total_production_days`,
      type: `sum`,
      title: `Total Production Days`
    },

    totalBatches: {
      sql: `total_batches`,
      type: `sum`,
      title: `Total Batches`
    },

    totalOperatorShifts: {
      sql: `total_operator_shifts`,
      type: `sum`,
      title: `Total Operator Shifts`
    },

    totalDefects: {
      sql: `total_defects`,
      type: `sum`,
      title: `Total Defects`
    },

    totalRework: {
      sql: `total_rework`,
      type: `sum`,
      title: `Total Rework`
    },

    weekendParts: {
      sql: `weekend_parts`,
      type: `sum`,
      title: `Weekend Parts Produced`
    },

    weekdayParts: {
      sql: `weekday_parts`,
      type: `sum`,
      title: `Weekday Parts Produced`
    },

    weekendProductionPct: {
      sql: `weekend_production_pct`,
      type: `avg`,
      title: `Weekend Production %`,
      format: `percent`
    },

    morningShiftParts: {
      sql: `morning_shift_parts`,
      type: `sum`,
      title: `Morning Shift Parts`
    },

    afternoonShiftParts: {
      sql: `afternoon_shift_parts`,
      type: `sum`,
      title: `Afternoon Shift Parts`
    },

    nightShiftParts: {
      sql: `night_shift_parts`,
      type: `sum`,
      title: `Night Shift Parts`
    },

    utilizationRate: {
      sql: `CAST(${totalPartsProduced} AS DOUBLE PRECISION) / NULLIF(CAST(${totalProductionDays} AS DOUBLE PRECISION), 0)`,
      type: `number`,
      title: `Daily Utilization Rate (parts/day)`,
      format: `number`
    }
  }
});
