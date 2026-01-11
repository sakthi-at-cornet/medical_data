"""Script to load all CSV data into PostgreSQL radiology database."""
import csv
import psycopg2
from datetime import datetime
import os

# Database connection settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5435"))
DB_NAME = "warehouse"
DB_USER = "warehouse_user"
DB_PASS = "warehouse_pass"

# CSV file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_SHEET1 = os.path.join(DATA_DIR, "Data_Example - Sheet1.csv")
CSV_SHEET2 = os.path.join(DATA_DIR, "Data_Example - Sheet2.csv")
CSV_SHEET3 = os.path.join(DATA_DIR, "Data_Example - Sheet3.csv")

def parse_datetime(value):
    """Parse datetime from various formats."""
    if not value or value.strip() == "":
        return None
    # Try different formats
    for fmt in ["%d-%m-%Y %I:%M %p", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %I:%M %p", "%d-%m-%Y", "%m/%d/%Y %I:%M %p"]:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None

def parse_float(value):
    """Parse float, return None if empty."""
    if not value or value.strip() == "":
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None

def parse_int(value):
    """Parse int, return None if empty."""
    if not value or value.strip() == "":
        return None
    try:
        return int(float(value.strip()))
    except ValueError:
        return None

def get_value(row, *keys):
    """Get value from row using multiple possible key names (case-insensitive)."""
    for key in keys:
        # Try exact match first
        if key in row:
            return row[key]
        # Try case-insensitive match
        for k in row.keys():
            if k.lower() == key.lower():
                return row[k]
    return ""

def load_radiology_audits(conn):
    """Load radiology audit data from Sheet1."""
    cur = conn.cursor()
    
    # Clear existing data
    print("Clearing existing radiology_audits data...")
    cur.execute("TRUNCATE medical.radiology_audits RESTART IDENTITY;")
    
    print(f"Loading radiology audits from {CSV_SHEET1}...")
    
    with open(CSV_SHEET1, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        insert_sql = """
        INSERT INTO medical.radiology_audits (
            sr_no, case_id, age, gender, modality, study_description,
            sub_specialty, scan_type, body_part, body_part_category,
            scan_date_and_time, report_date_and_time, case_upload_date_and_time,
            case_assigned_dated_and_time, review_completed_date_and_time_1,
            original_radiologist_name, review_radiologist_name_1,
            time_of_the_day_report_generated, unit_identifier, institute_name,
            assign_tat, review_tat,
            q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12_q, q12_s, q13, q14, q15, q16, q17,
            unable_to_audit, second_review, required_reaudit, comments,
            final_output, safety_score, quality_score, productivity_score, efficiency_score, star_score, star
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        count = 0
        for row in reader:
            try:
                values = (
                    parse_int(get_value(row, 'sr._no', 'sr_no', 'srno')),
                    get_value(row, 'caseid', 'case_id').strip() or f'CASE_{count}',
                    parse_int(get_value(row, 'Age', 'age')),
                    get_value(row, 'Gender', 'gender').strip() or None,
                    get_value(row, 'modality', 'Modality').strip() or None,
                    get_value(row, 'study_description', 'Study_Description').strip() or None,
                    get_value(row, 'sub_specialty', 'Sub_Specialty').strip() or None,
                    get_value(row, 'scan_type', 'Scan_Type').strip() or None,
                    get_value(row, 'body_part', 'Body_Part').strip() or None,
                    get_value(row, 'body_part_category', 'Body_Part_Category').strip() or None,
                    parse_datetime(get_value(row, 'scan_date_and_time', 'Scan_Date_And_Time')),
                    parse_datetime(get_value(row, 'report_date_and_time', 'Report_Date_And_Time')),
                    parse_datetime(get_value(row, 'case_upload_date_and_time', 'Case_Upload_Date_And_Time')),
                    parse_datetime(get_value(row, 'case_assigned_dated_and_time', 'Case_Assigned_Dated_And_Time')),
                    parse_datetime(get_value(row, 'review_completed_date_and_time_1', 'Review_Completed_Date_And_Time_1')),
                    get_value(row, 'original_radiologist_name', 'Original_Radiologist_Name').strip() or None,
                    get_value(row, 'review_radiologist_name_1', 'Review_Radiologist_Name_1').strip() or None,
                    get_value(row, 'time_of_the_day_report_generated', 'Time_Of_The_Day_Report_Generated').strip() or None,
                    get_value(row, 'unit_identifier', 'Unit_Identifier').strip() or None,
                    get_value(row, 'institute_name', 'Institute_Name').strip() or None,
                    get_value(row, 'assign_tat', 'Assign_TAT').strip() or None,
                    get_value(row, 'review_tat', 'Review_TAT').strip() or None,
                    parse_float(get_value(row, 'Q1', 'q1')),
                    parse_float(get_value(row, 'Q2', 'q2')),
                    parse_float(get_value(row, 'Q3', 'q3')),
                    parse_float(get_value(row, 'Q4', 'q4')),
                    parse_float(get_value(row, 'Q5', 'q5')),
                    parse_float(get_value(row, 'Q6', 'q6')),
                    parse_float(get_value(row, 'Q7', 'q7')),
                    parse_float(get_value(row, 'Q8', 'q8')),
                    parse_float(get_value(row, 'Q9', 'q9')),
                    parse_float(get_value(row, 'Q10', 'q10')),
                    parse_float(get_value(row, 'Q11', 'q11')),
                    parse_float(get_value(row, 'Q12_Q', 'q12_q')),
                    parse_float(get_value(row, 'Q12_S', 'q12_s')),
                    parse_float(get_value(row, 'Q13', 'q13')),
                    parse_float(get_value(row, 'Q14', 'q14')),
                    parse_float(get_value(row, 'Q15', 'q15')),
                    parse_float(get_value(row, 'Q16', 'q16')),
                    parse_float(get_value(row, 'Q17', 'q17')),
                    get_value(row, 'unable_to_audit', 'Unable_To_Audit').strip() or None,
                    get_value(row, 'second_review', 'Second_Review').strip() or None,
                    get_value(row, 'required_reaudit', 'Required_Reaudit').strip() or None,
                    get_value(row, 'comments', 'Comments').strip() or None,
                    get_value(row, 'Final_Output', 'final_output', 'FinalOutput').strip() or None,
                    parse_float(get_value(row, 'Safety_score', 'safety_score', 'SafetyScore')),
                    parse_float(get_value(row, 'Quality_score', 'quality_score', 'QualityScore')),
                    parse_float(get_value(row, 'Productivity_score', 'productivity_score', 'ProductivityScore')),
                    parse_float(get_value(row, 'Efficiency_score', 'efficiency_score', 'EfficiencyScore')),
                    parse_float(get_value(row, 'star_score', 'Star_Score', 'StarScore')),
                    parse_int(get_value(row, 'star', 'Star')),
                )
                
                cur.execute(insert_sql, values)
                count += 1
                
                if count % 100 == 0:
                    print(f"  Loaded {count} audit records...")
                    
            except Exception as e:
                print(f"Error on row {count}: {e}")
                print(f"Row data: {row}")
                raise
        
        conn.commit()
        print(f"Successfully loaded {count} audit records!")
    
    return count

def load_question_weightage(conn):
    """Load question weightage data from Sheet2."""
    cur = conn.cursor()
    
    # Clear existing data
    print("\nClearing existing question_weightage data...")
    cur.execute("TRUNCATE medical.question_weightage RESTART IDENTITY;")
    
    print(f"Loading question weightage from {CSV_SHEET2}...")
    
    with open(CSV_SHEET2, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        insert_sql = """
        INSERT INTO medical.question_weightage (
            question_no, category, responsibility, percentage_weightage
        ) VALUES (%s, %s, %s, %s)
        """
        
        count = 0
        for row in reader:
            try:
                question_no = get_value(row, 'QUESTION NO', 'question_no', 'QuestionNo').strip()
                category = get_value(row, 'CATEGORY', 'category', 'Category').strip()
                responsibility = get_value(row, 'RAD VS ORG', 'responsibility', 'Responsibility').strip()
                weightage = parse_float(get_value(row, 'PERCENTAGE_WEIGHTAGE', 'percentage_weightage', 'Weightage'))
                
                if question_no:
                    cur.execute(insert_sql, (question_no, category or None, responsibility or None, weightage))
                    count += 1
                    
            except Exception as e:
                print(f"Error on weightage row {count}: {e}")
                continue
        
        conn.commit()
        print(f"Successfully loaded {count} question weightage records!")
    
    return count

def load_scoring_rubric(conn):
    """Load scoring rubric data from Sheet3."""
    cur = conn.cursor()
    
    # Clear existing data
    print("\nClearing existing scoring_rubric data...")
    cur.execute("TRUNCATE medical.scoring_rubric RESTART IDENTITY;")
    
    print(f"Loading scoring rubric from {CSV_SHEET3}...")
    
    with open(CSV_SHEET3, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        insert_sql = """
        INSERT INTO medical.scoring_rubric (
            question_no, actual_question, score_0, score_1, score_2, score_3, score_4, score_5
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        count = 0
        for row in reader:
            try:
                question_no = parse_int(get_value(row, 'QUESTION NO', 'question_no', 'QuestionNo'))
                actual_question = get_value(row, 'ACTUAL QUESTION', 'actual_question', 'ActualQuestion').strip()
                
                if question_no:
                    values = (
                        question_no,
                        actual_question or None,
                        parse_int(get_value(row, '0', 'score_0')),
                        parse_int(get_value(row, '1', 'score_1')),
                        parse_int(get_value(row, '2', 'score_2')),
                        parse_int(get_value(row, '3', 'score_3')),
                        parse_int(get_value(row, '4', 'score_4')),
                        parse_int(get_value(row, '5', 'score_5')),
                    )
                    cur.execute(insert_sql, values)
                    count += 1
                    
            except Exception as e:
                print(f"Error on rubric row {count}: {e}")
                continue
        
        conn.commit()
        print(f"Successfully loaded {count} scoring rubric records!")
    
    return count

def verify_data(conn):
    """Verify loaded data."""
    cur = conn.cursor()
    
    print("\n=== DATA VERIFICATION ===")
    
    # Radiology audits
    cur.execute("SELECT COUNT(*) FROM medical.radiology_audits;")
    count = cur.fetchone()[0]
    print(f"Radiology Audits: {count} records")
    
    # Quality score stats
    cur.execute("""
        SELECT modality, 
               COUNT(*) as total, 
               COUNT(quality_score) as with_quality_score,
               ROUND(AVG(quality_score)::numeric, 2) as avg_quality,
               ROUND(AVG(safety_score)::numeric, 2) as avg_safety
        FROM medical.radiology_audits 
        GROUP BY modality 
        ORDER BY modality;
    """)
    print("\nQuality by Modality:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} total, {row[2]} with scores, Avg Quality: {row[3]}, Avg Safety: {row[4]}")
    
    # CAT distribution
    cur.execute("""
        SELECT final_output, COUNT(*) 
        FROM medical.radiology_audits 
        WHERE final_output IS NOT NULL
        GROUP BY final_output 
        ORDER BY final_output;
    """)
    print("\nCAT Distribution:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} cases")
    
    # Question weightage
    cur.execute("SELECT COUNT(*) FROM medical.question_weightage;")
    count = cur.fetchone()[0]
    print(f"\nQuestion Weightage: {count} records")
    
    # Scoring rubric
    cur.execute("SELECT COUNT(*) FROM medical.scoring_rubric;")
    count = cur.fetchone()[0]
    print(f"Scoring Rubric: {count} records")

def main():
    """Main function to load all data."""
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    
    try:
        # Load all CSV files
        load_radiology_audits(conn)
        load_question_weightage(conn)
        load_scoring_rubric(conn)
        
        # Verify
        verify_data(conn)
        
    finally:
        conn.close()
    
    print("\n=== ALL DATA LOADED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
