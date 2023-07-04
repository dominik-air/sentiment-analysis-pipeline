from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import numpy as np
import pandas as pd
from scipy.special import softmax
from sqlalchemy import create_engine, desc, func, MetaData, Table, select
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig


class Model:
    def __init__(self):
        model_name = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.config = AutoConfig.from_pretrained(model_name)
        
        db_hook = PostgresHook(postgres_conn_id="postgres_sbx")
        db_string = db_hook.get_uri()
        self.engine = create_engine(db_string)
        self.tweets = Table('tweets', MetaData(), autoload=True, autoload_with=self.engine)
        self.sentiments = Table('sentiments', MetaData(), autoload=True, autoload_with=self.engine)
        
        self.dataframe = self.read_data()
        
    def read_data(self):
        stmt = (
            select([
                self.tweets.columns.id,
                self.tweets.columns.body            
            ])
            .order_by(desc('id'))
            .limit(10)
        )
        
        return pd.DataFrame(self.engine.execute(stmt).fetchall())
        
    @staticmethod
    def preprocess(text):
            new_text = []
            for t in text.split(" "):
                t = '@user' if t.startswith('@') and len(t) > 1 else t
                t = 'http' if t.startswith('http') else t
                new_text.append(t)
            return " ".join(new_text) 
    
    def get_model_output(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        
        return list(scores)
    
    def split_model_output(self):
        model_output = np.array(list(self.dataframe['scores'].values))
        
        self.dataframe['positive'] = model_output[:, 2]
        self.dataframe['negative'] = model_output[:, 0]
        self.dataframe['neutral'] = model_output[:, 1]
        
        self.dataframe.drop(columns=['scores'], inplace=True)
        
    def update_id(self):
        stmt = (
            select(func.max(self.sentiments.columns.id))
        )
        new_id = self.engine.execute(stmt).fetchall()[0][0]
        
        if new_id is not None:
            self.dataframe.index += new_id + 1
            
    def postprocessing(self):
        self.dataframe.drop(columns=['body'], inplace=True)
        
        self.dataframe.rename(columns={'id': 'tweet_id'}, inplace=True)
        
        
    def insert_result_into_database(self):
        self.update_id()
        
        self.dataframe.to_sql('sentiments', self.engine, if_exists='append', index=True, index_label='id')
        
    def predict(self):
        self.dataframe.body = self.dataframe.body.apply(Model.preprocess)
        self.dataframe['scores'] = self.dataframe.body.apply(self.get_model_output)
        
        self.split_model_output()
        
        self.postprocessing()
        
        self.insert_result_into_database()


with DAG(
    "calculate_sentiment_ratios",
    default_args={
        "owner": "airflow",
    },
    description="Read data from database, calculate sentiment ratios and insert results into database",
    schedule_interval="*/20 * * * *",
    start_date=days_ago(1),
    tags=["example"],
    catchup=False
) as dag:
    calculate_sentiment_ratios = PythonOperator(
        task_id="model", python_callable=Model().predict()
    )