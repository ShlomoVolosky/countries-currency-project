from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
import sys
import os

sys.path.append('/opt/airflow/dags')

from src.processors.currencies import CurrencyProcessor
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("currencies_dag")

default_args = {
    'owner': 'countries-currency-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'currencies_processing',
    default_args=default_args,
    description='Process currency exchange rates',
    schedule='0 */6 * * *',  # Every 6 hours
    catchup=False,
    tags=['currencies', 'exchange', 'frequent'],
)


def setup_database():
    """Initialize database connection"""
    import asyncio
    asyncio.run(db_connection.create_pool())
    logger.info("Database connection established")


def process_currencies():
    """Process currency rates"""
    import asyncio
    
    async def run_processor():
        processor = CurrencyProcessor()
        success = await processor.process()
        if success:
            logger.info("Currency processing completed successfully")
        else:
            raise Exception("Currency processing failed")
    
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

process_currencies_task = PythonOperator(
    task_id='process_currencies',
    python_callable=process_currencies,
    dag=dag,
)

cleanup_db_task = PythonOperator(
    task_id='cleanup_database',
    python_callable=cleanup_database,
    dag=dag,
    trigger_rule='all_done',
)

setup_db_task >> process_currencies_task >> cleanup_db_task
