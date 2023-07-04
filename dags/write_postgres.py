import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago


def insert_data():
    r = requests.get("http://34.90.170.212?n=10")

    if r.status_code != 200:
        raise ValueError("API issue.")

    df = pd.DataFrame(r.json())

    db_hook = PostgresHook(postgres_conn_id="postgres_sbx")
    conn = db_hook.get_conn()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        insert_user_query = f"""INSERT INTO Users (name) 
        SELECT '{row['user']}'
        WHERE not exists (SELECT * FROM Users WHERE name = '{row['user']}')"""
        cursor.execute(insert_user_query)
        conn.commit()
        select_user_id = f"""SELECT id FROM Users WHERE name = '{row['user']}';"""
        cursor.execute(select_user_id)
        conn.commit()
        user_id = cursor.fetchall()[0][0]
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> now it should work
=======
>>>>>>> 0170fcd24c25e0ad0863799a6fe39078fe2ef37f

        cursor.execute("SELECT MAX(id) FROM Tweets;")
        max_id = cursor.fetchone()[0]

        if max_id is None:
            max_id = 0

        new_id = max_id + 1

        insert_tweet_query = f"""
            INSERT INTO Tweets (id, body, user_id, created_at)
            VALUES ('{new_id}', '{row['body'].replace("'", "")}', '{user_id}', '{row['created_at']}');
            """
        cursor.execute(insert_tweet_query)
        conn.commit()
<<<<<<< HEAD
<<<<<<< HEAD
=======
        user_ids.append(user_id)
    
    df["user_id"] = user_ids
    df.drop(columns=["user", "id"], inplace=True)
<<<<<<< HEAD
    df.to_sql("tweets", con=db_hook.get_uri(), if_exists="append")
>>>>>>> use dbstring instead
=======
    df.to_sql("tweets", con=db_hook.get_uri(), if_exists="append", index_label="id")
>>>>>>> xd
=======
>>>>>>> now it should work
=======
>>>>>>> 0170fcd24c25e0ad0863799a6fe39078fe2ef37f


with DAG(
    "create_and_populate_table_dag",
    default_args={
        "owner": "airflow",
    },
    description="Downloads data from Twitter API and inserts it into the DB.",
    schedule_interval="*/15 * * * *",
    start_date=days_ago(1),
    tags=["example"],
    catchup=False,
) as dag:
    create_and_populate_table_task = PythonOperator(
        task_id="insert_data", python_callable=insert_data
    )
