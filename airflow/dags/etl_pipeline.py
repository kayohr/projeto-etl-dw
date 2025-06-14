from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
from datetime import datetime, timedelta
import sys
import os

# Ajuste de path para importar os módulos internos (extract, transform, load)
# Esse bloco permite que o Airflow encontre as pastas 'src/extract', 'src/transform', 'src/load'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'src'))

# Importação dos scripts de ETL
from extract.extract_api import extract_data
from transform.transform_data import transform_data
from load.load_dw import load_dw

# Configuração dos argumentos padrão da DAG
default_args = {
    'owner': 'kayo',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 1),
    'retries': 3, 
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': True,
    'email': ['dados@maxinutri.com.br'],  
    'email_on_retry': False,
}

# Função de callback para capturar falhas e gerar logs adicionais
def on_failure_callback(context):
    dag_run = context.get('dag_run')
    task_instance = context.get('task_instance')
    print(f"[ALERTA] Falha na DAG: {dag_run.dag_id}, Task: {task_instance.task_id}")

# Definição principal da DAG
with DAG(
    dag_id='etl_projeto',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    on_failure_callback=on_failure_callback
) as dag:
     # Task de extração de dados
    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )
    # Task de transformação dos dados
    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )
    # Task de carga dos dados transformados no Data Warehouse
    load = PythonOperator(
        task_id='load_dw',
        python_callable=load_dw
    )
    # Definição da ordem de execução das tasks
    extract >> transform >> load
