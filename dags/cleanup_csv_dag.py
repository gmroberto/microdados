"""
CSV Cleanup DAG for Apache Airflow.
This DAG calls the cleanup function to delete CSV files from the downloads folder.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
import logging

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from etl_operators import create_cleanup_operator

# Configure logging
logger = logging.getLogger(__name__)

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
    'enem_csv_cleanup_maintenance',
    default_args=default_args,
    description='Weekly maintenance task to cleanup old CSV files from downloads folder',
    schedule_interval='@weekly',  # Run weekly to clean up old files
    catchup=False,
    tags=['enem', 'cleanup', 'csv', 'maintenance', 'weekly'],
    max_active_runs=1,
)


def cleanup_summary(**context):
    """Generate a summary of the cleanup operation."""
    task_instance = context['task_instance']
    
    # Get cleanup results from XCom
    cleanup_status = task_instance.xcom_pull(task_ids='cleanup_phase', key='cleanup_status')
    cleanup_error = task_instance.xcom_pull(task_ids='cleanup_phase', key='cleanup_error')
    cleanup_details = task_instance.xcom_pull(task_ids='cleanup_phase', key='cleanup_details')
    
    logger.info("=== CSV Cleanup Summary ===")
    logger.info(f"Cleanup Status: {cleanup_status}")
    
    if cleanup_error:
        logger.error(f"Cleanup Error: {cleanup_error}")
    
    if cleanup_details:
        logger.info(f"Files Deleted: {cleanup_details.get('files_deleted', 0)}")
        logger.info(f"Total Files Found: {cleanup_details.get('total_files', 0)}")
        logger.info(f"Space Freed: {cleanup_details.get('space_freed_bytes', 0)} bytes")
        
        failed_deletions = cleanup_details.get('failed_deletions', [])
        if failed_deletions:
            logger.warning(f"Failed to delete {len(failed_deletions)} files")
            for failure in failed_deletions:
                logger.warning(f"  - {failure['file']}: {failure['error']}")
    
    logger.info("=== CSV Cleanup Summary Completed ===")


# Define the tasks
start_task = EmptyOperator(
    task_id='start',
    dag=dag,
)

# CSV cleanup task - uses the ETL operator
cleanup_task = create_cleanup_operator(
    task_id='cleanup_phase',
    dag=dag,
)

# Summary task
summary_task = PythonOperator(
    task_id='cleanup_summary',
    python_callable=cleanup_summary,
    trigger_rule=TriggerRule.ALL_DONE,  # Run regardless of upstream task status
    dag=dag,
)

end_task = EmptyOperator(
    task_id='end',
    trigger_rule=TriggerRule.ALL_DONE,  # Run even if some tasks failed
    dag=dag,
)

# Define the task dependencies
start_task >> cleanup_task >> summary_task >> end_task 