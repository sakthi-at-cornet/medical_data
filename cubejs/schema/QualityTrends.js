cube(`QualityTrends`, {
  sql: `SELECT * FROM staging_marts.agg_component_quality_trends`,

  joins: {

  },

  dimensions: {
    componentType: {
      sql: `component_type`,
      type: `string`,
      title: `Component Type`
    },

    productionDate: {
      sql: `production_date`,
      type: `time`,
      title: `Production Date`
    },

    productionHour: {
      sql: `production_hour`,
      type: `time`,
      title: `Production Hour`
    }
  },

  measures: {
    totalUnits: {
      sql: `total_units`,
      type: `sum`,
      title: `Total Units`,
      drillMembers: [componentType, productionHour]
    },

    passedUnits: {
      sql: `passed_units`,
      type: `sum`,
      title: `Passed Units`
    },

    failedUnits: {
      sql: `failed_units`,
      type: `sum`,
      title: `Failed Units`
    },

    passRate: {
      sql: `pass_rate`,
      type: `avg`,
      format: `percent`,
      title: `Pass Rate %`
    },

    movingAvgPassRate: {
      sql: `moving_avg_pass_rate_4h`,
      type: `avg`,
      format: `percent`,
      title: `4-Hour Moving Average Pass Rate`,
      description: `Rolling 4-hour average of pass rate for trend analysis`
    },

    count: {
      type: `count`,
      title: `Number of Hourly Records`
    }
  },

  preAggregations: {
    hourlyTrends: {
      measures: [totalUnits, passedUnits, failedUnits, passRate],
      dimensions: [componentType],
      timeDimension: productionHour,
      granularity: `hour`
    }
  }
});
