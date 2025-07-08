"""
ENEM Create Indexes DAG for Apache Airflow.
This DAG handles only the create indexes phase of the ENEM ETL process.
Can be manually triggered to create database indexes for performance.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import ETL operators from the dedicated module
from etl_operators import create_indexes_operator

# Default arguments for the DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# Create the DAG
dag = DAG(
    'enem_create_indexes_only',
    default_args=default_args,
    description='ENEM Create Indexes Phase - Manual Trigger Only',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['enem', 'indexes', 'manual'],
    max_active_runs=1,
)

# Define the tasks
start_task = EmptyOperator(
    task_id='start',
    dag=dag,
)

# Create indexes task
create_indexes_task = create_indexes_operator(
    task_id='create_indexes',
    dag=dag,
)

end_task = EmptyOperator(
    task_id='end',
    dag=dag,
)

# Define the task dependencies
start_task >> create_indexes_task >> end_task 