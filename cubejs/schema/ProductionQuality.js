cube(`ProductionQuality`, {
  sql: `SELECT * FROM staging_marts.fact_production_quality`,

  joins: {

  },

  dimensions: {
    qualityKey: {
      sql: `quality_key`,
      type: `string`,
      primaryKey: true
    },

    componentType: {
      sql: `component_type`,
      type: `string`,
      title: `Component Type`
    },

    lineId: {
      sql: `line_id`,
      type: `string`,
      title: `Production Line`
    },

    productionDate: {
      sql: `timestamp`,
      type: `time`,
      title: `Production Date`
    }
  },

  measures: {
    totalUnits: {
      sql: `total_units`,
      type: `sum`,
      title: `Total Units Produced`,
      drillMembers: [componentType, lineId, productionDate]
    },

    passedUnits: {
      sql: `passed_units`,
      type: `sum`,
      title: `Passed Units`,
      drillMembers: [componentType, lineId, productionDate]
    },

    failedUnits: {
      sql: `failed_units`,
      type: `sum`,
      title: `Failed Units`,
      drillMembers: [componentType, lineId, productionDate]
    },

    passRate: {
      sql: `CAST(${passedUnits} AS DOUBLE PRECISION) * 100.0 / NULLIF(CAST(${totalUnits} AS DOUBLE PRECISION), 0)`,
      type: `number`,
      format: `percent`,
      title: `Pass Rate %`,
      description: `Percentage of units that passed quality checks`
    },

    avgQualityScore: {
      sql: `avg_quality_score`,
      type: `avg`,
      title: `Average Quality Score`,
      format: `percent`
    },

    count: {
      type: `count`,
      title: `Number of Production Runs`
    }
  },

  preAggregations: {
    main: {
      measures: [totalUnits, passedUnits, failedUnits],
      dimensions: [componentType, lineId],
      timeDimension: productionDate,
      granularity: `day`
    }
  }
});
