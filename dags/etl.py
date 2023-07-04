from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import time


def extract_data():
    print("Extracting data...")
    time.sleep(5)
    print("Data extracted.")


def transform_data():
    print("Transforming data...")
    time.sleep(5)
    print("Data transformed.")


def load_data():
    print("Loading data to the database...")
    time.sleep(5)
    print("Data loaded to the database.")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 5, 14),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "etl_dag",
    default_args=default_args,
    description="A simple ETL DAG",
    schedule_interval=timedelta(days=1),
)

t1 = PythonOperator(
    task_id="extract",
    python_callable=extract_data,
    dag=dag,
)

t2 = PythonOperator(
    task_id="transform",
    python_callable=transform_data,
    dag=dag,
)

t3 = PythonOperator(
    task_id="load",
    python_callable=load_data,
    dag=dag,
)

t1 >> t2 >> t3
