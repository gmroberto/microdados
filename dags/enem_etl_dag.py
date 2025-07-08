"""
ENEM ETL Pipeline DAG for Apache Airflow.
This DAG orchestrates the complete ETL process for ENEM microdata.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import ETL operators from the dedicated module
from etl_operators import (
    create_download_operator,
    create_extract_operator,
    create_delete_zip_operator,
    create_load_operator,
    create_united_table_operator,
    create_populate_united_table_operator,
    create_indexes_operator,
    create_pipeline_summary_operator
)

# Default arguments for the DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=10),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=60),
}

# Create the DAG
dag = DAG(
    'enem_etl_pipeline_advanced',
    default_args=default_args,
    description='Advanced ENEM Microdata ETL Pipeline with Error Handling',
    schedule_interval='@monthly',
    catchup=False,
    tags=['enem', 'etl', 'microdata', 'advanced'],
    max_active_runs=1,
)

# Define the tasks
start_task = EmptyOperator(
    task_id='start',
    dag=dag,
)

# Download task with specific retry configuration
download_task = create_download_operator(
    task_id='download_phase',
    retries=2,
    retry_delay=timedelta(minutes=5),
    dag=dag,
)

# Extract task
extract_task = create_extract_operator(
    task_id='extract_phase',
    dag=dag,
)

# Delete ZIP task
delete_zip_task = create_delete_zip_operator(
    task_id='delete_zip_phase',
    dag=dag,
)

# Load task with higher retries due to potential database issues
load_task = create_load_operator(
    task_id='load_phase',
    retries=3,
    retry_delay=timedelta(minutes=15),
    dag=dag,
)

# United table creation task
create_united_table_task = create_united_table_operator(
    task_id='create_united_table',
    dag=dag,
)

# Populate united table task
populate_united_table_task = create_populate_united_table_operator(
    task_id='populate_united_table',
    retries=2,
    retry_delay=timedelta(minutes=10),
    dag=dag,
)

# Create indexes task
create_indexes_task = create_indexes_operator(
    task_id='create_indexes',
    dag=dag,
)

# Summary task
summary_task = create_pipeline_summary_operator(
    task_id='pipeline_summary',
    trigger_rule=TriggerRule.ALL_DONE,  # Run regardless of upstream task status
    dag=dag,
)

end_task = EmptyOperator(
    task_id='end',
    trigger_rule=TriggerRule.ALL_DONE,  # Run even if some tasks failed
    dag=dag,
)

# Define the task dependencies
start_task >> download_task >> extract_task >> delete_zip_task >> load_task >> create_united_table_task >> populate_united_table_task >> create_indexes_task >> summary_task >> end_task 