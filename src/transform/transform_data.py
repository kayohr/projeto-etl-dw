import pandas as pd

def transform_data():
    try:
        # Tenta ler o arquivo CSV extraído anteriormente
        df = pd.read_csv('data/dados_api.csv')
    except FileNotFoundError:
        print("Arquivo 'dados_api.csv' não encontrado. Verifique o caminho e o nome do arquivo.")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return

    try:
        # Tratamento inicial de nulos em texto
        df['review_comment_title'] = df['review_comment_title'].fillna('')
        df['review_comment_message'] = df['review_comment_message'].fillna('')

        # Conversão de datas
        colunas_datas = [
            'order_purchase_timestamp', 'order_approved_at', 
            'order_delivered_carrier_date', 'order_delivered_customer_date', 
            'order_estimated_delivery_date', 'review_creation_date', 
            'review_answer_timestamp'
        ]
        df[colunas_datas] = df[colunas_datas].apply(pd.to_datetime, errors='coerce')

        # Limpeza: remove registros com datas inválidas
        df = df.dropna(subset=colunas_datas)

        # Validação de campos obrigatórios
        campos_obrigatorios = ['product_id', 'price']
        nulos_obrigatorios = df[campos_obrigatorios].isnull().sum()
        for campo, qtd in nulos_obrigatorios.items():
            if qtd > 0:
                print(f"Atenção: {qtd} registros com {campo} nulo serão removidos.")
        df = df.dropna(subset=campos_obrigatorios)

        # Tratamento de numéricos
        colunas_numericas = ['freight_value', 'product_weight_g', 
                              'product_length_cm', 'product_height_cm', 'product_width_cm']
        df[colunas_numericas] = df[colunas_numericas].fillna(0)

        # Verificação de tipos
        for col in colunas_numericas:
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"Atenção: Coluna {col} contém valores não numéricos.")

        # Validação de duplicatas (exemplo: order_id + product_id como chave)
        if 'order_id' in df.columns:
            duplicatas = df.duplicated(subset=['order_id', 'product_id']).sum()
            if duplicatas > 0:
                print(f"Atenção: {duplicatas} registros duplicados encontrados e removidos.")
                df = df.drop_duplicates(subset=['order_id', 'product_id'])

        # Salva arquivo tratado
        df.to_csv('data/dados_api_tratado.csv', index=False, encoding='utf-8')
        print("Arquivo tratado salvo em data/dados_api_tratado.csv")

    except Exception as e:
        print(f"Erro durante o processamento dos dados: {e}")
        return
