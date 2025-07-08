"""
ENEM Pipeline Summary DAG for Apache Airflow.
This DAG handles only the pipeline summary phase of the ENEM ETL process.
Can be manually triggered to generate pipeline execution summary.
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
from etl_operators import create_pipeline_summary_operator

# Default arguments for the DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=15),
}

# Create the DAG
dag = DAG(
    'enem_pipeline_summary_only',
    default_args=default_args,
    description='ENEM Pipeline Summary Phase - Manual Trigger Only',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['enem', 'summary', 'manual'],
    max_active_runs=1,
)

# Define the tasks
start_task = EmptyOperator(
    task_id='start',
    dag=dag,
)

# Pipeline summary task
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
start_task >> summary_task >> end_task 