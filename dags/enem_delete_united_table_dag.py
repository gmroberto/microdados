"""
ENEM Delete United Table DAG for Apache Airflow.
This DAG handles only the delete united table phase of the ENEM ETL process.
Can be manually triggered to clean up the united table.
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
from etl_operators import create_delete_united_table_operator

# Default arguments for the DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# Create the DAG
dag = DAG(
    'enem_unified_table_cleanup_manual',
    default_args=default_args,
    description='Manual cleanup and removal of unified ENEM table',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['enem', 'cleanup', 'unified_table', 'database', 'manual'],
    max_active_runs=1,
)

# Define the tasks
start_task = EmptyOperator(
    task_id='start',
    dag=dag,
)

# Delete United Table task
delete_united_table_task = create_delete_united_table_operator(
    task_id='delete_united_table_phase',
    dag=dag,
)

end_task = EmptyOperator(
    task_id='end',
    dag=dag,
)

# Define the task dependencies
start_task >> delete_united_table_task >> end_task 