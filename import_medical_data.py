"""
Import Medical Radiology Audit Data from CSV files into PostgreSQL.
Run this script to load the data after containers are up.
"""
import csv
import psycopg2
from datetime import datetime
import os
import re

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 5435,
    'database': 'warehouse',
    'user': 'warehouse_user',
    'password': 'warehouse_pass'
}

def parse_datetime(value):
    """Parse datetime from various formats."""
    if not value or value.strip() == '':
        return None
    
    # Clean the value
    value = value.strip()
    
    # Try different formats
    formats = [
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y 0:00:00',
        '%m/%d/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    
    return None

def parse_decimal(value):
    """Parse decimal value."""
    if not value or value.strip() == '':
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None

def parse_int(value):
    """Parse integer value."""
    if not value or value.strip() == '':
        return None
    try:
        return int(float(value.strip()))
    except ValueError:
        return None

def import_radiology_audits(cursor, csv_path):
    """Import main audit data from Sheet1."""
    print(f"Importing radiology audits from {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        insert_sql = """
        INSERT INTO medical.radiology_audits (
            sr_no, case_id, age, gender, modality, study_description, sub_specialty,
            scan_date_and_time, report_date_and_time, case_upload_date_and_time,
            case_assigned_dated_and_time, review_completed_date_and_time_1,
            original_radiologist_name, time_of_the_day_report_generated, unit_identifier,
            institute_name, assign_tat, review_radiologist_name_1, second_review, review_tat,
            q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12_q, q12_s, q13, q14, q15, q16, q17,
            unable_to_audit, comments, required_reaudit, age_cohort, scan_type, body_part,
            body_part_category, final_output, safety_score, quality_score, productivity_score,
            efficiency_score, star_score, star
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (case_id) DO UPDATE SET
            age = EXCLUDED.age,
            gender = EXCLUDED.gender,
            modality = EXCLUDED.modality,
            final_output = EXCLUDED.final_output,
            quality_score = EXCLUDED.quality_score,
            safety_score = EXCLUDED.safety_score,
            star = EXCLUDED.star;
        """
        
        count = 0
        for row in reader:
            try:
                values = (
                    parse_int(row.get('sr._no', row.get('sr_no'))),
                    row.get('caseid', '').strip(),
                    parse_int(row.get('Age')),
                    row.get('Gender', '').strip(),
                    row.get('modality', '').strip(),
                    row.get('study_description', '').strip(),
                    row.get('sub_specialty', '').strip(),
                    parse_datetime(row.get('scan_date_and_time')),
                    parse_datetime(row.get('report_date_and_time')),
                    parse_datetime(row.get('case_upload_date_and_time')),
                    parse_datetime(row.get('case_assigned_dated_and_time')),
                    parse_datetime(row.get('review_completed_date_and_time_1')),
                    row.get('original_radiologist_name/identifier', '').strip(),
                    row.get('time_of_the_day_report_generated', '').strip(),
                    row.get('unit_identifier', '').strip(),
                    row.get('institute_name', '').strip(),
                    row.get('assign_tat', '').strip(),
                    row.get('review_radiologist_name_1', '').strip(),
                    row.get('second_review', '').strip(),
                    row.get('review_tat', '').strip(),
                    parse_decimal(row.get('Q1')),
                    parse_decimal(row.get('Q2')),
                    parse_decimal(row.get('Q3')),
                    parse_decimal(row.get('Q4')),
                    parse_decimal(row.get('Q5')),
                    parse_decimal(row.get('Q6')),
                    parse_decimal(row.get('Q7')),
                    parse_decimal(row.get('Q8')),
                    parse_decimal(row.get('Q9')),
                    parse_decimal(row.get('Q10')),
                    parse_decimal(row.get('Q11')),
                    parse_decimal(row.get('Q12_Q')),
                    parse_decimal(row.get('Q12_S')),
                    parse_decimal(row.get('Q13')),
                    parse_decimal(row.get('Q14')),
                    parse_decimal(row.get('Q15')),
                    parse_decimal(row.get('Q16')),
                    parse_decimal(row.get('Q17')),
                    row.get('unable_to_audit', '').strip(),
                    row.get('comments', '').strip(),
                    row.get('required_reaudit', '').strip(),
                    row.get('age_cohort', '').strip(),
                    row.get('scan_type', '').strip(),
                    row.get('body_part', '').strip(),
                    row.get('body_part_category', '').strip(),
                    row.get('Final_Output', '').strip(),
                    parse_decimal(row.get('Safety_score')),
                    parse_decimal(row.get('Quality_score')),
                    parse_decimal(row.get('Productivity_score')),
                    parse_decimal(row.get('Efficiency_score')),
                    parse_decimal(row.get('star_score')),
                    parse_int(row.get('star'))
                )
                
                if values[1]:  # Only insert if case_id exists
                    cursor.execute(insert_sql, values)
                    count += 1
                    if count % 100 == 0:
                        print(f"  Imported {count} records...")
                        
            except Exception as e:
                print(f"  Error importing row: {e}")
                print(f"  Row data: {row.get('caseid')}")
                continue
        
        print(f"  Total imported: {count} records")
        return count

def main():
    """Main import function."""
    print("=" * 60)
    print("Medical Radiology Audit Data Import")
    print("=" * 60)
    
    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        print("Connected successfully!")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return
    
    try:
        # First, run the schema creation
        print("\nCreating medical schema...")
        schema_path = os.path.join(os.path.dirname(__file__), 'docker', 'postgres', 'warehouse', 'medical_init.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        print("Schema created!")
        
        # Import main audit data
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'Data_Example - Sheet1.csv')
        if os.path.exists(data_path):
            import_radiology_audits(cursor, data_path)
        else:
            print(f"Data file not found: {data_path}")
        
        # Commit all changes
        conn.commit()
        print("\nAll data imported successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM medical.radiology_audits")
        total = cursor.fetchone()[0]
        print(f"\nSummary: {total} total audit records in database")
        
        cursor.execute("SELECT modality, COUNT(*) FROM medical.radiology_audits GROUP BY modality")
        print("\nBy Modality:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} cases")
        
        cursor.execute("SELECT final_output, COUNT(*) FROM medical.radiology_audits GROUP BY final_output ORDER BY final_output")
        print("\nBy CAT Rating:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} cases")
            
    except Exception as e:
        print(f"\nError during import: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == '__main__':
    main()
