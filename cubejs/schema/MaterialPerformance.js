cube(`MaterialPerformance`, {
  sql: `SELECT * FROM staging_marts.agg_material_performance`,

  joins: {

  },

  dimensions: {
    material: {
      sql: `material`,
      type: `string`,
      primaryKey: true,
      title: `Material Type`
    }
  },

  measures: {
    totalUnits: {
      sql: `total_units`,
      type: `sum`,
      title: `Total Units`
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

    avgDurability: {
      sql: `avg_durability`,
      type: `avg`,
      title: `Average Durability Score`
    },

    avgColorMatch: {
      sql: `avg_color_match`,
      type: `avg`,
      title: `Average Color Match Rating`
    },

    avgLength: {
      sql: `avg_length`,
      type: `avg`,
      title: `Average Length (mm)`
    },

    avgThickness: {
      sql: `avg_thickness`,
      type: `avg`,
      title: `Average Wall Thickness (mm)`
    },

    highDurabilityCount: {
      sql: `high_durability_count`,
      type: `sum`,
      title: `High Durability Count`
    },

    mediumDurabilityCount: {
      sql: `medium_durability_count`,
      type: `sum`,
      title: `Medium Durability Count`
    },

    lowDurabilityCount: {
      sql: `low_durability_count`,
      type: `sum`,
      title: `Low Durability Count`
    },

    count: {
      type: `count`,
      title: `Number of Materials`
    }
  }
});
