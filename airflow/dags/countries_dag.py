from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

sys.path.append('/opt/airflow/dags')

from src.processors.countries import CountriesProcessor
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("countries_dag")

default_args = {
    'owner': 'countries-currency-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'countries_processing',
    default_args=default_args,
    description='Process countries data from REST Countries API',
    schedule='0 2 * * 0',  # Weekly on Sunday at 2 AM
    catchup=False,
    tags=['countries', 'weekly'],
)


def setup_database():
    """Initialize database connection"""
    import asyncio
    asyncio.run(db_connection.create_pool())
    logger.info("Database connection established")


def process_countries():
    """Process countries data"""
    import asyncio
    
    async def run_processor():
        processor = CountriesProcessor()
        success = await processor.process()
        if success:
            logger.info("Countries processing completed successfully")
        else:
            raise Exception("Countries processing failed")
    
    asyncio.run(run_processor())


def cleanup_database():
    """Cleanup database connections"""
    import asyncio
    asyncio.run(db_connection.close_pool())
    logger.info("Database connections closed")


setup_db_task = PythonOperator(
    task_id='setup_database',
    python_callable=setup_database,
    dag=dag,
)

process_countries_task = PythonOperator(
    task_id='process_countries',
    python_callable=process_countries,
    dag=dag,
)

cleanup_db_task = PythonOperator(
    task_id='cleanup_database',
    python_callable=cleanup_database,
    dag=dag,
    trigger_rule='all_done',
)

setup_db_task >> process_countries_task >> cleanup_db_task
