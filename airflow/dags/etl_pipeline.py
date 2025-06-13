from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

import sys
import os

# Subir uma pasta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adicionar o caminho correto do src
sys.path.append(os.path.join(BASE_DIR, '..', 'src'))

from extract.extract_api import extract_data
from transform.transform_data import transform_data
from load.load_dw import load_dw

default_args = {
    'owner': 'kayo',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='etl_projeto',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load = PythonOperator(
        task_id='load_dw',
        python_callable=load_dw
    )

    extract >> transform >> load
