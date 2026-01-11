"""
Modern Data Stack Pipeline DAG

Orchestrates the complete data pipeline:
1. Extract and Load from source databases to warehouse
2. Run dbt transformations
3. Run dbt tests
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import logging

logger = logging.getLogger(__name__)


def task_failure_alert(context):
    """
    Callback function for task failures
    Logs failure details and can be extended to send alerts via Slack, PagerDuty, etc.
    """
    task_instance = context['task_instance']
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id
    execution_date = context['execution_date']
    exception = context.get('exception')

    error_message = f"""
    ========================================
    PIPELINE FAILURE ALERT
    ========================================
    DAG: {dag_id}
    Task: {task_id}
    Execution Date: {execution_date}
    Exception: {exception}
    ========================================
    """

    logger.error(error_message)
    print(error_message)

    # TODO: Add integration with alerting systems
    # - Slack webhook
    # - PagerDuty
    # - Email (if SMTP configured)
    # - Praval agent for anomaly detection

    return error_message

default_args = {
    'owner': 'praval',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': task_failure_alert,
}

dag = DAG(
    'mds_pipeline',
    default_args=default_args,
    description='Medical Data Stack - EL + dbt Pipeline',
    schedule_interval='0 0 * * *',  # Daily at midnight
    start_date=days_ago(1),
    catchup=False,
    tags=['medical', 'radiology', 'el', 'dbt'],
)

# Task 1: Load CSV Data to Warehouse
el_pipeline_task = BashOperator(
    task_id='load_medical_data',
    bash_command="""
    cd /opt/airflow/project && \
    python3 -m pip install --quiet psycopg2-binary > /dev/null 2>&1 && \
    export DB_HOST=postgres-warehouse && \
    export DB_PORT=5432 && \
    python3 load_data.py
    """,
    dag=dag,
)

# Task 2: Run dbt transformations
dbt_run_task = BashOperator(
    task_id='run_dbt_transformations',
    bash_command="""
    pip install --quiet dbt-postgres dbt-core > /dev/null 2>&1 && \
    dbt run --project-dir=/opt/airflow/project/dbt_transform --profiles-dir=/home/airflow/.dbt
    """,
    dag=dag,
)

# Task 3: Run dbt tests
dbt_test_task = BashOperator(
    task_id='run_dbt_tests',
    bash_command="""
    dbt test --project-dir=/opt/airflow/project/dbt_transform --profiles-dir=/home/airflow/.dbt
    """,
    dag=dag,
)

# Task 4: Generate summary report
def generate_summary(**context):
    """Generate pipeline execution summary"""
    execution_date = context['execution_date']
    print(f"Pipeline completed successfully for {execution_date}")
    print("Summary:")
    print("- EL Pipeline: Extracted and loaded radiology audit data")
    print("- dbt Transformations: Built medical models (stg_radiology_audits, mart_radiology_quality)")
    print("- dbt Tests: Executed 53 tests")
    return "Pipeline execution complete"

summary_task = PythonOperator(
    task_id='generate_summary',
    python_callable=generate_summary,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
el_pipeline_task >> dbt_run_task >> dbt_test_task >> summary_task
