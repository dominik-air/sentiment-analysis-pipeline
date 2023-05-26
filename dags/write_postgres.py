from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago


def create_and_populate_table():
    db_hook = PostgresHook(postgres_conn_id="postgres_sbx")
    conn = db_hook.get_conn()
    cursor = conn.cursor()

    table_check_query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE  table_schema = 'public'
        AND    table_name   = 'persons'
    );
    """

    cursor.execute(table_check_query)
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        create_table_query = """
        CREATE TABLE persons (
            id serial PRIMARY KEY,
            name varchar(50),
            age int
        );
        """
        cursor.execute(create_table_query)

        insert_data_query = """
        INSERT INTO persons (name, age) VALUES
        ('name1', 1),
        ('name2', 2),
        ('name3', 3);
        """
        cursor.execute(insert_data_query)
        print("Data inserted successfully!")
    else:
        print("Table 'persons' is already present in the database!")

    conn.commit()


with DAG(
    "create_and_populate_table_dag",
    default_args={
        "owner": "airflow",
    },
    description="An example DAG that writes to PostgreSQL",
    schedule_interval=None,
    start_date=days_ago(2),
    tags=["example"],
    catchup=False
) as dag:
    create_and_populate_table_task = PythonOperator(
        task_id="create_and_populate_table", python_callable=create_and_populate_table
    )
