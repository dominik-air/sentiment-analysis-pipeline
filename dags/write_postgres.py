import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago


def insert_data():
    r = requests.get("http://34.90.170.212?n=10")

    if r.status_code != 200: raise ValueError("API issue.")
   
    df = pd.DataFrame(r.json())

    db_hook = PostgresHook(postgres_conn_id="postgres_sbx")
    conn = db_hook.get_conn()
    cursor = conn.cursor()

    user_ids = []
    for user_name in df.user:
        insert_user_query = f"""INSERT INTO Users (name) 
        SELECT '{user_name}'
        WHERE not exists (SELECT * FROM Users WHERE name = '{user_name}')"""
        cursor.execute(insert_user_query)
        conn.commit()
        select_user_id = f"""SELECT id FROM Users WHERE name = '{user_name}';"""
        cursor.execute(select_user_id)
        conn.commit()
        user_id = cursor.fetchall()[0][0]
        user_ids.append(user_id)
    
    df["user_id"] = user_ids
    df.drop(columns=["user", "id"], inplace=True)
    df.to_sql("tweets", con=db_hook.get_uri(), if_exists="append", index_label="id")

with DAG(
    "create_and_populate_table_dag",
    default_args={
        "owner": "airflow",
    },
    description="Downloads data from Twitter API and inserts it into the DB.",
    schedule_interval="*/15 * * * *",
    start_date=days_ago(1),
    tags=["example"],
    catchup=False
) as dag:
    create_and_populate_table_task = PythonOperator(
        task_id="insert_data", python_callable=insert_data
    )
