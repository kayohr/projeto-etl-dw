import pandas as pd

def transform_data():
    try:
        df = pd.read_csv('data/dados_api.csv')
    except FileNotFoundError:
        print("Arquivo 'dados_api.csv' não encontrado. Verifique o caminho e o nome do arquivo.")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return

    try:
        # Tratamento
        df['review_comment_title'] = df['review_comment_title'].fillna('')
        df['review_comment_message'] = df['review_comment_message'].fillna('')

        colunas_datas = [
            'order_purchase_timestamp', 'order_approved_at', 
            'order_delivered_carrier_date', 'order_delivered_customer_date', 
            'order_estimated_delivery_date', 'review_creation_date', 
            'review_answer_timestamp'
        ]
        df[colunas_datas] = df[colunas_datas].apply(pd.to_datetime, errors='coerce')

        # Limpeza: remove registros com datas inválidas
        df = df.dropna(subset=colunas_datas)

        df = df.dropna(subset=['product_id', 'price'])

        colunas_numericas = ['freight_value', 'product_weight_g', 
                            'product_length_cm', 'product_height_cm', 'product_width_cm']
        df[colunas_numericas] = df[colunas_numericas].fillna(0)

        df.to_csv('data/dados_api_tratado.csv', index=False, encoding='utf-8')
        print("Arquivo tratado salvo em data/dados_api_tratado.csv")
        
    except Exception as e:
        print(f"Erro durante o processamento dos dados: {e}")
        return
