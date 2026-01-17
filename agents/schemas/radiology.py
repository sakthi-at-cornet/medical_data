"""
Radiology Domain Data Schema definitions.
"""
from typing import Dict, Any

# Structured Schema Definition
RADIOLOGY_SCHEMA_DICT: Dict[str, Any] = {
    "cube": "RadiologyAudits",
    "description": "Comprehensive radiology audit records including patient demographics, operational timestamps, and quality metrics.",
    "dimensions": {
        "caseId": "Unique case identifier (e.g., CS000001) - use for looking up specific cases",
        "srNo": "Serial number of the record",
        "modality": '"CT" or "MRI" (imaging modality)',
        "subSpecialty": '"Neuro", "Body", "MSK", "Cardiovascular", "Multipart", etc.',
        "bodyPartCategory": '"NEURO", "ABDOMEN/PELVIS", "SPINE", "MSK", "HEAD AND NECK", "CHEST", etc.',
        "bodyPart": 'Specific body part (e.g., "Brain", "Lumbar Spine", "Knee Right")',
        "studyDescription": 'Full description of the study (e.g., "MRI BRAIN STROKE PROTOCOL")',
        "scanType": 'Type of scan (e.g., "Plain", "Contrast", "Angio")',
        "instituteName": 'Name of the institute (e.g., "PIXEL DIAGNOSTICS - UIC")',
        "unitIdentifier": 'Unit ID (e.g., "1", "2")',
        "originalRadiologist": "Name/ID of the original reporting radiologist (e.g., RAD 1)",
        "reviewer": "Name of the reviewing radiologist (e.g., Reviewer1, Reviewer2)",
        "secondReview": '"Yes" or "No" - indicates if a second review was performed',
        "finalOutput": 'CAT rating ("CAT1"=Good, "CAT5"=Major Discrepancy) - The Peer Review Category',
        "starRating": 'Star rating (1-5) - Visual rating score',
        "gender": '"M" or "F" (Patient Gender)',
        "ageCohort": 'Age group classification (e.g., "less than 10")',
        "age": "Patient Age (numeric)",
        "unableToAudit": '"Yes" or "No" - indicates if the case could not be audited',
        "requiredReaudit": '"Yes" or "No" - indicates if re-audit is required',
        "comments": "Audit comments and feedback text",
        "reportDate": "Date/Time when the report was generated (Time Dimension)",
        "scanDate": "Date/Time of the scan (Time Dimension)",
        "uploadDate": "Date/Time when case was uploaded",
        "assignDate": "Date/Time when case was assigned",
        "reviewDate": "Date/Time when review was completed"
    },
    "measures": {
        "count": "Total number of audits/cases",
        "avgQualityScore": "Average Quality Score (0-100)",
        "avgSafetyScore": "Average Safety Score (0-100)",
        "avgProductivityScore": "Average Productivity Score (0-100)",
        "avgEfficiencyScore": "Average Efficiency Score (0-100)",
        "avgStarScore": "Average Star Score (0-100 derived)",
        "avgStarRating": "Average Star Rating (1-5 scale)",
        "avgAge": "Average Patient Age",
        "avgAssignTat": "Average Assignment Turnaround Time",
        "avgReviewTat": "Average Review Turnaround Time",
        # CAT Rating Counts
        "cat1Count": "Count of CAT1 ratings (Good/Concurrence)",
        "cat2Count": "Count of CAT2 ratings (Minor Discrepancy)",
        "cat3Count": "Count of CAT3 ratings",
        "cat4Count": "Count of CAT4 ratings",
        "cat5Count": "Count of CAT5 ratings (Major Discrepancy)",
        # Conditional counts
        "highSafetyCount": "Count of cases with Safety Score > 80",
        "highQualityCount": "Count of cases with Quality Score > 70",
        "lowQualityCount": "Count of cases with Quality Score < 60",
        "highSafetyRate": "Percentage of cases with Safety Score > 80",
        # Quality Question Scores (Q1-Q17) - Averages
        "avgQ1": "Avg Score for Q1",
        "avgQ2": "Avg Score for Q2",
        "avgQ3": "Avg Score for Q3",
        "avgQ4": "Avg Score for Q4",
        "avgQ5": "Avg Score for Q5",
        "avgQ6": "Avg Score for Q6",
        "avgQ7": "Avg Score for Q7",
        "avgQ8": "Avg Score for Q8",
        "avgQ9": "Avg Score for Q9",
        "avgQ10": "Avg Score for Q10",
        "avgQ11": "Avg Score for Q11",
        "avgQ12Q": "Avg Score for Q12_Q",
        "avgQ12S": "Avg Score for Q12_S",
        "avgQ13": "Avg Score for Q13",
        "avgQ14": "Avg Score for Q14",
        "avgQ15": "Avg Score for Q15",
        "avgQ16": "Avg Score for Q16",
        "avgQ17": "Avg Score for Q17"
    }
}

def get_radiology_schema_prompt() -> str:
    """Generate the schema prompt string from the structured definition."""
    schema = RADIOLOGY_SCHEMA_DICT
    prompt = f"Available Data Schema:\n\nCube: {schema['cube']} ({schema['description']})\n\nDimensions (group by / filter):\n"
    for key, desc in schema['dimensions'].items():
        prompt += f"- {key}: {desc}\n"
    
    prompt += "\nMeasures (metrics to calculate):\n"
    for key, desc in schema['measures'].items():
        prompt += f"- {key}: {desc}\n"
        
    return prompt

# Legacy support for direct import (generated validation)
RADIOLOGY_DATA_SCHEMA = get_radiology_schema_prompt()

# Metric to Cube.js measure mapping by cube
METRIC_MAPPING = {
    # Medical Radiology Audits Cube
    "RadiologyAudits": {
        "count": "RadiologyAudits.count",
        "total": "RadiologyAudits.count",
        "cases": "RadiologyAudits.count",
        
        # Scores
        "avgQualityScore": "RadiologyAudits.avgQualityScore",
        "quality_score": "RadiologyAudits.avgQualityScore",
        "quality": "RadiologyAudits.avgQualityScore",
        "avgSafetyScore": "RadiologyAudits.avgSafetyScore",
        "safety_score": "RadiologyAudits.avgSafetyScore",
        "safety": "RadiologyAudits.avgSafetyScore",
        "avgProductivityScore": "RadiologyAudits.avgProductivityScore",
        "productivity_score": "RadiologyAudits.avgProductivityScore",
        "productivity": "RadiologyAudits.avgProductivityScore",
        "avgEfficiencyScore": "RadiologyAudits.avgEfficiencyScore",
        "efficiency_score": "RadiologyAudits.avgEfficiencyScore",
        "efficiency": "RadiologyAudits.avgEfficiencyScore",
        "avgStarScore": "RadiologyAudits.avgStarScore",
        "star_score": "RadiologyAudits.avgStarScore",
        "avgStarRating": "RadiologyAudits.avgStarRating",
        "star_rating": "RadiologyAudits.avgStarRating",
        "stars": "RadiologyAudits.avgStarRating",
        
        # CAT Counts
        "cat5Count": "RadiologyAudits.cat5Count",
        "cat5": "RadiologyAudits.cat5Count",
        "cat4Count": "RadiologyAudits.cat4Count",
        "cat4": "RadiologyAudits.cat4Count",
        "cat3Count": "RadiologyAudits.cat3Count",
        "cat3": "RadiologyAudits.cat3Count",
        "cat2Count": "RadiologyAudits.cat2Count",
        "cat2": "RadiologyAudits.cat2Count",
        "cat1Count": "RadiologyAudits.cat1Count",
        "cat1": "RadiologyAudits.cat1Count",
        "highQualityRate": "RadiologyAudits.highQualityRate",
        "high_quality_rate": "RadiologyAudits.highQualityRate",
        "reauditCount": "RadiologyAudits.reauditCount",
        "reaudit_count": "RadiologyAudits.reauditCount",
        
        # Demographics & TAT
        "avgAge": "RadiologyAudits.avgAge",
        "avg_age": "RadiologyAudits.avgAge",
        "avgAssignTat": "RadiologyAudits.avgAssignTat",
        "assign_tat": "RadiologyAudits.avgAssignTat",
        "avgReviewTat": "RadiologyAudits.avgReviewTat",
        "review_tat": "RadiologyAudits.avgReviewTat",
        
        # Individual Questions (assuming these measures exist in Cube or will be added)
        "avgQ1": "RadiologyAudits.avgQ1",
        "avgQ2": "RadiologyAudits.avgQ2",
        "avgQ3": "RadiologyAudits.avgQ3",
        "avgQ4": "RadiologyAudits.avgQ4",
        "avgQ5": "RadiologyAudits.avgQ5",
        "avgQ6": "RadiologyAudits.avgQ6",
        "avgQ7": "RadiologyAudits.avgQ7",
        "avgQ8": "RadiologyAudits.avgQ8",
        "avgQ9": "RadiologyAudits.avgQ9",
        "avgQ10": "RadiologyAudits.avgQ10",
        "avgQ11": "RadiologyAudits.avgQ11",
        "avgQ12Q": "RadiologyAudits.avgQ12Q",
        "avgQ12S": "RadiologyAudits.avgQ12S",
        "avgQ13": "RadiologyAudits.avgQ13",
        "avgQ14": "RadiologyAudits.avgQ14",
        "avgQ15": "RadiologyAudits.avgQ15",
        "avgQ16": "RadiologyAudits.avgQ16",
        "avgQ17": "RadiologyAudits.avgQ17",
    },
}

# Dimension mapping by cube
DIMENSION_MAPPING = {
    # Medical Radiology Audits Cube
    "RadiologyAudits": {
        # Core Dimensions
        "caseId": "RadiologyAudits.caseId",
        "case_id": "RadiologyAudits.caseId",
        "srNo": "RadiologyAudits.srNo",
        "modality": "RadiologyAudits.modality",
        "sub_specialty": "RadiologyAudits.subSpecialty",
        "subSpecialty": "RadiologyAudits.subSpecialty",
        "subspecialty": "RadiologyAudits.subSpecialty",
        "body_part_category": "RadiologyAudits.bodyPartCategory",
        "bodyPartCategory": "RadiologyAudits.bodyPartCategory",
        "category": "RadiologyAudits.bodyPartCategory",
        "body_part": "RadiologyAudits.bodyPart",
        "bodyPart": "RadiologyAudits.bodyPart",
        "study_description": "RadiologyAudits.studyDescription",
        "studyDescription": "RadiologyAudits.studyDescription",
        "scan_type": "RadiologyAudits.scanType",
        "scanType": "RadiologyAudits.scanType",
        
        # People & Places
        "original_radiologist": "RadiologyAudits.originalRadiologist",
        "originalRadiologist": "RadiologyAudits.originalRadiologist",
        "radiologist": "RadiologyAudits.originalRadiologist",
        "reviewer": "RadiologyAudits.reviewer",
        "review_radiologist": "RadiologyAudits.reviewer",
        "institute_name": "RadiologyAudits.instituteName",
        "instituteName": "RadiologyAudits.instituteName",
        "unit_identifier": "RadiologyAudits.unitIdentifier",
        "unitIdentifier": "RadiologyAudits.unitIdentifier",
        "unit": "RadiologyAudits.unitIdentifier",
        
        # Outcomes & Quality
        "final_output": "RadiologyAudits.finalOutput",
        "finalOutput": "RadiologyAudits.finalOutput",
        "cat_rating": "RadiologyAudits.finalOutput",
        "cat": "RadiologyAudits.finalOutput",
        "star_rating": "RadiologyAudits.starRating",
        "starRating": "RadiologyAudits.starRating",
        "star": "RadiologyAudits.starRating",
        "unable_to_audit": "RadiologyAudits.unableToAudit",
        "unableToAudit": "RadiologyAudits.unableToAudit",
        "required_reaudit": "RadiologyAudits.requiredReaudit",
        "requiredReaudit": "RadiologyAudits.requiredReaudit",
        "second_review": "RadiologyAudits.secondReview",
        "secondReview": "RadiologyAudits.secondReview",
        "comments": "RadiologyAudits.comments",
        
        # Demographics
        "gender": "RadiologyAudits.gender",
        "sex": "RadiologyAudits.gender",
        "age": "RadiologyAudits.age",
        "age_cohort": "RadiologyAudits.ageCohort",
        "ageCohort": "RadiologyAudits.ageCohort",
        
        # Time Dimensions (Note: Cube.js typically uses specific time grains)
        "report_date": "RadiologyAudits.reportDate",
        "reportDate": "RadiologyAudits.reportDate",
        "scan_date": "RadiologyAudits.scanDate",
        "scanDate": "RadiologyAudits.scanDate",
        "upload_date": "RadiologyAudits.uploadDate",
        "uploadDate": "RadiologyAudits.uploadDate",
        "assign_date": "RadiologyAudits.assignDate",
        "assignDate": "RadiologyAudits.assignDate",
        "review_date": "RadiologyAudits.reviewDate",
        "reviewDate": "RadiologyAudits.reviewDate",
    },
}
