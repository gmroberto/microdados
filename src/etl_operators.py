"""
ETL Operators for ENEM Pipeline.
This module contains Airflow operators that use the core ETL functions.
These operators handle Airflow-specific concerns like XCom, context, and task dependencies.
"""

import logging
from airflow.models import Variable
from airflow.operators.python import PythonOperator

from etl_functions import (
    download_enem_data,
    extract_zip_files,
    delete_zip_files,
    load_csv_files,
    create_united_table_structure,
    populate_united_table_data,
    create_database_indexes,
    cleanup_csv_files,
    generate_pipeline_summary
)

# Configure logging
logger = logging.getLogger(__name__)


def _execute_phase(phase_name: str, phase_func, **kwargs):
    """
    Generic phase execution wrapper that handles common Airflow concerns.
    
    Args:
        phase_name: Name of the phase for logging and XCom keys
        phase_func: Function to execute
        **kwargs: Arguments to pass to the phase function
    """
    def wrapper(**context):
        task_instance = context['task_instance']
        
        try:
            # Execute the phase function
            result = phase_func(**kwargs)
            
            # Store results in XCom
            task_instance.xcom_push(key=f'{phase_name}_status', value=result['status'])
            if result.get('error'):
                task_instance.xcom_push(key=f'{phase_name}_error', value=result['error'])
            if result.get('details'):
                task_instance.xcom_push(key=f'{phase_name}_details', value=result['details'])
            
            # Raise exception if failed
            if result['status'] == 'failed':
                raise Exception(result['error'])
                
        except Exception as e:
            logger.error(f"{phase_name.replace('_', ' ').title()} phase failed: {str(e)}")
            task_instance.xcom_push(key=f'{phase_name}_status', value='failed')
            task_instance.xcom_push(key=f'{phase_name}_error', value=str(e))
            raise
    
    return wrapper


def download_phase(**context):
    """Download Phase - Download ENEM microdata files."""
    years = Variable.get("enem_years", deserialize_json=True, default_var=None)
    skip_download = Variable.get("skip_download", default_var=False)
    
    return _execute_phase('download', download_enem_data, years=years, skip_download=skip_download)(**context)


def extract_phase(**context):
    """Extract Phase - Extract ZIP files to CSV without deleting them."""
    return _execute_phase('extract', extract_zip_files)(**context)


def delete_zip_phase(**context):
    """Delete ZIP Phase - Delete ZIP files after successful extraction."""
    return _execute_phase('delete_zip', delete_zip_files)(**context)


def load_phase(**context):
    """Load Phase - Load CSV files into database."""
    return _execute_phase('load', load_csv_files)(**context)


def create_united_table(**context):
    """Create United Table - Create the unified table structure."""
    return _execute_phase('create_table', create_united_table_structure)(**context)


def populate_united_table(**context):
    """Populate United Table - Fill the unified table with data."""
    return _execute_phase('populate', populate_united_table_data)(**context)


def create_indexes(**context):
    """Create Indexes - Create database indexes for performance."""
    return _execute_phase('indexes', create_database_indexes)(**context)


def cleanup_phase(**context):
    """Cleanup Phase - Clean up CSV files from downloads directory."""
    return _execute_phase('cleanup', cleanup_csv_files)(**context)


def pipeline_summary(**context):
    """Generate a summary of the pipeline execution."""
    task_instance = context['task_instance']
    
    # Collect status from all tasks
    statuses = {
        'download': task_instance.xcom_pull(task_ids='download_phase', key='download_status'),
        'extract': task_instance.xcom_pull(task_ids='extract_phase', key='extract_status'),
        'delete_zip': task_instance.xcom_pull(task_ids='delete_zip_phase', key='delete_zip_status'),
        'load': task_instance.xcom_pull(task_ids='load_phase', key='load_status'),
        'create_table': task_instance.xcom_pull(task_ids='create_united_table', key='create_table_status'),
        'populate': task_instance.xcom_pull(task_ids='populate_united_table', key='populate_status'),
        'indexes': task_instance.xcom_pull(task_ids='create_indexes', key='indexes_status'),
        'cleanup': task_instance.xcom_pull(task_ids='cleanup_phase', key='cleanup_status'),
    }
    
    # Call the core function
    summary = generate_pipeline_summary(statuses)
    
    # Store summary in XCom
    task_instance.xcom_push(key='pipeline_summary', value=summary)
    
    # Log the summary
    logger.info(f"Pipeline overall status: {summary['overall_status']}")
    if summary['failed_phases']:
        logger.warning(f"Failed phases: {', '.join(summary['failed_phases'])}")


# Factory functions to create operators
def create_operator(task_id: str, python_callable, **kwargs):
    """Generic operator factory to reduce code duplication."""
    return PythonOperator(
        task_id=task_id,
        python_callable=python_callable,
        **kwargs
    )


def create_download_operator(task_id='download_phase', **kwargs):
    """Create download phase operator."""
    return create_operator(task_id, download_phase, **kwargs)


def create_extract_operator(task_id='extract_phase', **kwargs):
    """Create extract phase operator."""
    return create_operator(task_id, extract_phase, **kwargs)


def create_delete_zip_operator(task_id='delete_zip_phase', **kwargs):
    """Create delete ZIP phase operator."""
    return create_operator(task_id, delete_zip_phase, **kwargs)


def create_load_operator(task_id='load_phase', **kwargs):
    """Create load phase operator."""
    return create_operator(task_id, load_phase, **kwargs)


def create_united_table_operator(task_id='create_united_table', **kwargs):
    """Create united table operator."""
    return create_operator(task_id, create_united_table, **kwargs)


def create_populate_united_table_operator(task_id='populate_united_table', **kwargs):
    """Create populate united table operator."""
    return create_operator(task_id, populate_united_table, **kwargs)


def create_indexes_operator(task_id='create_indexes', **kwargs):
    """Create indexes operator."""
    return create_operator(task_id, create_indexes, **kwargs)


def create_cleanup_operator(task_id='cleanup_phase', **kwargs):
    """Create cleanup phase operator."""
    return create_operator(task_id, cleanup_phase, **kwargs)


def create_pipeline_summary_operator(task_id='pipeline_summary', **kwargs):
    """Create pipeline summary operator."""
    return create_operator(task_id, pipeline_summary, **kwargs) 