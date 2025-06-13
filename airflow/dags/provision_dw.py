from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2
from datetime import datetime

def create_dw_schema():
    conn = psycopg2.connect(
        host="postgres-db",
        database="etl_projeto",
        user="postgres",
        password="sua_senha"
    )
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_cliente (
        customer_id VARCHAR(255) PRIMARY KEY,
        customer_city VARCHAR(255),
        customer_state VARCHAR(255),
        customer_zip_code_prefix VARCHAR(10)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_produto (
        product_id VARCHAR(255) PRIMARY KEY,
        product_category_name VARCHAR(255),
        product_photos_qty BIGINT,
        product_weight_g BIGINT,
        product_length_cm BIGINT,
        product_height_cm BIGINT,
        product_width_cm BIGINT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fato_pedido (
        order_id VARCHAR(255) PRIMARY KEY,
        customer_id VARCHAR(255) REFERENCES dim_cliente(customer_id),
        product_id VARCHAR(255) REFERENCES dim_produto(product_id),
        order_status VARCHAR(50),
        order_purchase_timestamp TIMESTAMP,
        order_approved_at TIMESTAMP,
        order_delivered_carrier_date TIMESTAMP,
        order_delivered_customer_date TIMESTAMP,
        order_estimated_delivery_date TIMESTAMP,
        price NUMERIC(18,2),
        freight_value NUMERIC(18,2),
        review_score BIGINT,
        review_comment_title TEXT,
        review_comment_message TEXT,
        review_creation_date DATE,
        review_answer_timestamp TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

with DAG('provision_dw', start_date=datetime(2024,1,1), catchup=False, schedule_interval=None) as dag:
    create_dw = PythonOperator(
        task_id='create_dw_schema',
        python_callable=create_dw_schema
    )
