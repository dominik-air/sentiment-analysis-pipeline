from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago


def read_and_display_data():
    db_hook = PostgresHook(postgres_conn_id="postgres_sbx")
    conn = db_hook.get_conn()
    cursor = conn.cursor()

    select_data_query = """
    SELECT * FROM persons;
    """

    cursor.execute(select_data_query)
    data = cursor.fetchall()

    print("Data from sandbox table:")
    for row in data:
        print(row)


with DAG(
    "read_and_display_data_dag",
    default_args={
        "owner": "airflow",
    },
    description="An example DAG that reads from PostgreSQL",
    schedule_interval=None,
    start_date=days_ago(2),
    tags=["example"],
    catchup=False,
) as dag:
    read_and_display_data_task = PythonOperator(
        task_id="read_and_display_data", python_callable=read_and_display_data
    )
