/**
 * Radiology Audits Cube
 * Main analytics cube for radiology quality audit data
 */
cube(`RadiologyAudits`, {
    sql: `SELECT * FROM medical.radiology_audits`,

    title: 'Radiology Audits',
    description: 'Quality audit data for radiology imaging reports',

    joins: {},

    measures: {
        count: {
            type: `count`,
            title: 'Total Cases',
            drillMembers: [caseId, modality, subSpecialty, finalOutput]
        },

        avgQualityScore: {
            type: `avg`,
            sql: `quality_score`,
            title: 'Average Quality Score',
            format: 'percent'
        },

        avgSafetyScore: {
            type: `avg`,
            sql: `safety_score`,
            title: 'Average Safety Score',
            format: 'percent'
        },

        avgProductivityScore: {
            type: `avg`,
            sql: `productivity_score`,
            title: 'Average Productivity Score',
            format: 'percent'
        },

        avgEfficiencyScore: {
            type: `avg`,
            sql: `efficiency_score`,
            title: 'Average Efficiency Score',
            format: 'percent'
        },

        avgStarScore: {
            type: `avg`,
            sql: `star_score`,
            title: 'Average Star Score',
            format: 'percent'
        },

        avgStarRating: {
            type: `avg`,
            sql: `star`,
            title: 'Average Star Rating'
        },

        cat5Count: {
            type: `count`,
            sql: `case_id`,
            title: 'CAT 5 Cases (Excellent)',
            filters: [{ sql: `${CUBE}.final_output = 'CAT5'` }]
        },

        cat4Count: {
            type: `count`,
            sql: `case_id`,
            title: 'CAT 4 Cases (Good)',
            filters: [{ sql: `${CUBE}.final_output = 'CAT4'` }]
        },

        cat3Count: {
            type: `count`,
            sql: `case_id`,
            title: 'CAT 3 Cases (Acceptable)',
            filters: [{ sql: `${CUBE}.final_output = 'CAT3'` }]
        },

        cat2Count: {
            type: `count`,
            sql: `case_id`,
            title: 'CAT 2 Cases (Needs Improvement)',
            filters: [{ sql: `${CUBE}.final_output = 'CAT2'` }]
        },

        cat1Count: {
            type: `count`,
            sql: `case_id`,
            title: 'CAT 1 Cases (Poor)',
            filters: [{ sql: `${CUBE}.final_output = 'CAT1'` }]
        },

        highQualityRate: {
            type: `number`,
            sql: `ROUND(COUNT(CASE WHEN ${CUBE}.final_output IN ('CAT4', 'CAT5') THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2)`,
            title: 'High Quality Rate (%)',
            description: 'Percentage of cases rated CAT4 or CAT5'
        },

        reauditCount: {
            type: `count`,
            sql: `case_id`,
            title: 'Reaudit Required',
            filters: [{ sql: `${CUBE}.required_reaudit = 'Yes'` }]
        },

        avgAge: {
            type: `avg`,
            sql: `age`,
            title: 'Average Patient Age'
        },

        // Quality sub-scores
        avgQ1: { type: `avg`, sql: `q1`, title: 'Avg Q1 - Referral Interpretable' },
        avgQ2: { type: `avg`, sql: `q2`, title: 'Avg Q2 - Clinical History' },
        avgQ3: { type: `avg`, sql: `q3`, title: 'Avg Q3 - Clinical Question' },
        avgQ4: { type: `avg`, sql: `q4`, title: 'Avg Q4 - Diagnostic Quality' },
        avgQ5: { type: `avg`, sql: `q5`, title: 'Avg Q5 - Extra Images' },
        avgQ11: { type: `avg`, sql: `q11`, title: 'Avg Q11 - Differential Diagnosis' },
        avgQ16: { type: `avg`, sql: `q16`, title: 'Avg Q16 - Language Errors' },
        avgQ17: { type: `avg`, sql: `q17`, title: 'Avg Q17 - Final CAT Score' }
    },

    dimensions: {
        id: {
            sql: `id`,
            type: `number`,
            primaryKey: true
        },

        caseId: {
            sql: `case_id`,
            type: `string`,
            title: 'Case ID'
        },

        age: {
            sql: `age`,
            type: `number`,
            title: 'Patient Age'
        },

        gender: {
            sql: `gender`,
            type: `string`,
            title: 'Gender'
        },

        ageCohort: {
            sql: `age_cohort`,
            type: `string`,
            title: 'Age Cohort'
        },

        modality: {
            sql: `modality`,
            type: `string`,
            title: 'Modality'
        },

        studyDescription: {
            sql: `study_description`,
            type: `string`,
            title: 'Study Description'
        },

        subSpecialty: {
            sql: `sub_specialty`,
            type: `string`,
            title: 'Sub-Specialty'
        },

        scanType: {
            sql: `scan_type`,
            type: `string`,
            title: 'Scan Type'
        },

        bodyPart: {
            sql: `body_part`,
            type: `string`,
            title: 'Body Part'
        },

        bodyPartCategory: {
            sql: `body_part_category`,
            type: `string`,
            title: 'Body Part Category'
        },

        originalRadiologist: {
            sql: `original_radiologist_name`,
            type: `string`,
            title: 'Radiologist'
        },

        reviewer: {
            sql: `review_radiologist_name_1`,
            type: `string`,
            title: 'Reviewer'
        },

        instituteName: {
            sql: `institute_name`,
            type: `string`,
            title: 'Institute'
        },

        unitIdentifier: {
            sql: `unit_identifier`,
            type: `string`,
            title: 'Unit'
        },

        finalOutput: {
            sql: `final_output`,
            type: `string`,
            title: 'CAT Rating'
        },

        starRating: {
            sql: `star`,
            type: `number`,
            title: 'Star Rating'
        },

        secondReview: {
            sql: `second_review`,
            type: `string`,
            title: 'Second Review Required'
        },

        requiredReaudit: {
            sql: `required_reaudit`,
            type: `string`,
            title: 'Reaudit Required'
        },

        comments: {
            sql: `comments`,
            type: `string`,
            title: 'Comments'
        },

        assignTat: {
            sql: `assign_tat`,
            type: `string`,
            title: 'Assignment TAT'
        },

        reviewTat: {
            sql: `review_tat`,
            type: `string`,
            title: 'Review TAT'
        },

        scanDateTime: {
            sql: `scan_date_and_time`,
            type: `time`,
            title: 'Scan Date/Time'
        },

        reportDateTime: {
            sql: `report_date_and_time`,
            type: `time`,
            title: 'Report Date/Time'
        },

        reviewCompletedDateTime: {
            sql: `review_completed_date_and_time_1`,
            type: `time`,
            title: 'Review Completed Date/Time'
        },

        createdAt: {
            sql: `created_at`,
            type: `time`,
            title: 'Created At'
        }
    },

    segments: {
        ctScans: {
            sql: `${CUBE}.modality = 'CT'`
        },
        mriScans: {
            sql: `${CUBE}.modality = 'MRI'`
        },
        highQuality: {
            sql: `${CUBE}.final_output IN ('CAT4', 'CAT5')`
        },
        lowQuality: {
            sql: `${CUBE}.final_output IN ('CAT1', 'CAT2')`
        },
        neuroStudies: {
            sql: `${CUBE}.sub_specialty = 'Neuro'`
        },
        bodyStudies: {
            sql: `${CUBE}.sub_specialty = 'Body'`
        }
    },

    
});
