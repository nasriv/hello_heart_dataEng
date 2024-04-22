import io
import requests
import pandas as pd
import boto3
import psycopg2

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.helpers import chain

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_data(api_url, limit, offset):
    #### department of health has a 1000 row limit on fetches
    all_data = []
    while True:
        try:
            response = requests.get(api_url, params={"$limit": limit, "$offset": offset})
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

            data = response.json()  # Convert response to JSON format
            if not data:
                break  # No more data available
            all_data.extend(data)
            offset += limit

        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            return None
    
    df = pd.DataFrame(all_data) # dump into dataframe and return
    return df.head(2)

def save_to_parquet_and_s3(data, s3_bucket, s3_key):
    df = pd.read_csv(io.BytesIO(data))
    df.to_parquet(f'/tmp/data.parquet')
    s3_client = boto3.client('s3')
    s3_client.upload_file(Filename='/tmp/data.parquet', Bucket=s3_bucket, Key=s3_key)

def load_to_postgres(s3_bucket, s3_key, table_name):
    s3_client = boto3.client('s3')
    s3_client.download_file(Bucket=s3_bucket, Key=s3_key, Filename='/tmp/data.parquet')
    df = pd.read_parquet('/tmp/data.parquet')
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    pg_hook.insert_rows(table=table_name, rows=df.values.tolist())

with DAG(dag_id="hello_heart_dag", start_date=datetime(2024,4,19), schedule_interval="@daily", catchup=False) as dag:
    t0 = PythonOperator(
        task_id="fetch_and_s3_data",
        python_callable=fetch_data,
        op_args=["https://healthdata.gov/resource/g62h-syeh.json", 1000, 0]
                    )
    
    t1 = PythonOperator(
        task_id="save_s3_parquet",
        python_callable=save_to_parquet_and_s3
    )

    t2 = PythonOperator(
        task_id="load_to_db",
        python_callable=load_to_postgres
    )

    chain(t0, [t1, t2])