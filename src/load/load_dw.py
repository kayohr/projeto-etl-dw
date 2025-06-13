import pandas as pd
import psycopg2
import numpy as np

def load_dw():
    try:
        df = pd.read_csv('data/dados_api_tratado.csv')
    except FileNotFoundError:
        print("Arquivo CSV não encontrado. Verifique o caminho.")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return

    dim_cliente = df[['customer_id', 'customer_city', 'customer_state', 'customer_zip_code_prefix']].drop_duplicates()
    dim_produto = df[['product_id', 'product_category_name', 'product_photos_qty',
                      'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']].drop_duplicates()
    fato_pedido = df[['order_id', 'customer_id', 'product_id', 'order_status',
                      'order_purchase_timestamp', 'order_approved_at',
                      'order_delivered_carrier_date', 'order_delivered_customer_date',
                      'order_estimated_delivery_date', 'price', 'freight_value',
                      'review_score', 'review_comment_title', 'review_comment_message',
                      'review_creation_date', 'review_answer_timestamp']]

    try:
        conn = psycopg2.connect(
            host="postgres-db",
            database="etl_projeto",
            user="postgres",
            password="sua_senha"
        )
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar no banco de dados: {e}")
        return

    cur = conn.cursor()

    try:
        cur.execute("TRUNCATE TABLE fato_pedido, dim_produto, dim_cliente;")
        conn.commit()
    except Exception as e:
        print(f"Erro ao truncar as tabelas: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return

    # Carregar dim_cliente
    for index, row in dim_cliente.iterrows():
        try:
            cur.execute("""
                INSERT INTO dim_cliente (customer_id, customer_city, customer_state, customer_zip_code_prefix)
                VALUES (%s, %s, %s, %s)
            """, tuple(row))
        except Exception as e:
            print(f"Erro na dim_cliente linha {index}: {e}")
    conn.commit()

    # Carregar dim_produto (blindado)
    for index, row in dim_produto.iterrows():
        try:
            values = (
                row['product_id'],
                row['product_category_name'],
                int(row['product_photos_qty']) if not pd.isna(row['product_photos_qty']) else 0,
                int(row['product_weight_g']) if not pd.isna(row['product_weight_g']) else 0,
                int(row['product_length_cm']) if not pd.isna(row['product_length_cm']) else 0,
                int(row['product_height_cm']) if not pd.isna(row['product_height_cm']) else 0,
                int(row['product_width_cm']) if not pd.isna(row['product_width_cm']) else 0
            )

            cur.execute("""
                INSERT INTO dim_produto (product_id, product_category_name, product_photos_qty,
                                          product_weight_g, product_length_cm, product_height_cm, product_width_cm)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, values)
        except Exception as e:
            print(f"Erro na dim_produto linha {index}: {e}")
    conn.commit()

    # Carregar fato_pedido (já estava protegido)
    for index, row in fato_pedido.iterrows():
        try:
            cur.execute("""
                INSERT INTO fato_pedido (
                    order_id, customer_id, product_id, order_status,
                    order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, 
                    order_delivered_customer_date, order_estimated_delivery_date, price, freight_value,
                    review_score, review_comment_title, review_comment_message,
                    review_creation_date, review_answer_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        except Exception as e:
            print(f"Erro na fato_pedido linha {index}: {e}")
    conn.commit()

    cur.close()
    conn.close()

    print("Carga no DW finalizada!")
