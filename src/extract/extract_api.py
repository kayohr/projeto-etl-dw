import requests
import json
import pandas as pd
import math
import time
from config import config

import sys
import os

# Ajuste de sys.path (normalmente não é necessário no Airflow, mas útil em execução local)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'src'))

# Define o diretório onde os dados serão armazenados
DATA_DIR = '/opt/airflow/data'

# Cria o diretório se ele ainda não existir (garante que o caminho existe)
os.makedirs(DATA_DIR, exist_ok=True)

# Função principal de extração de dados
def extract_data():
    pagina = 1
    todos_dados = []
    max_retries = 5  # número máximo de tentativas

    while True:
        params = {
            'token': config.token,
            'page': pagina
        }
        # Controle de tentativas (retries) com tratamento de falhas
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(config.base_url, params=params, timeout=30)
                response.raise_for_status()
                break  # se deu certo, sai do for
            except requests.exceptions.HTTPError as http_err:
                status_code = response.status_code
                if 400 <= status_code < 500:
                    # Erros definitivos, não adianta tentar de novo
                    print(f"Erro HTTP {status_code}: {http_err}. Não será feito retry.")
                    return
                else:
                    print(f"Erro HTTP {status_code}: {http_err}. Tentando novamente...")
            except requests.exceptions.RequestException as req_err:
                print(f"Erro de conexão: {req_err}. Tentativa {attempt}/{max_retries}")

            # Backoff exponencial com pequeno jitter (para evitar congestionamento)
            sleep_time = (2 ** attempt) + (0.1 * attempt)
            time.sleep(sleep_time)
        else:
            # Se chegou aqui, falhou em todas as tentativas
            print("Falha após várias tentativas. Abortando.")
            return

        try:
            texto_corrigido = response.text.replace('NaN', 'null')
            json_response = json.loads(texto_corrigido)
        except json.JSONDecodeError as json_err:
            print(f"Erro ao decodificar JSON corrigido: {json_err}")
            print("Conteúdo da resposta:", response.text)
            return
        except Exception as e:
            print("Erro inesperado ao processar a resposta JSON:", e)
            return
        # Extrai os dados da resposta
        dados = json_response.get('dados', [])
        todos_dados.extend(dados)

         # Captura informações de paginação
        total_linhas = json_response.get('total_linhas')
        linhas_por_pagina = json_response.get('linhas_por_pagina')

        # Validação se a resposta contém os campos esperados de paginação
        if total_linhas is None or linhas_por_pagina is None:
            print("Resposta JSON não contém as chaves esperadas de paginação.")
            return
        # Calcula o total de páginas
        total_paginas = math.ceil(total_linhas / linhas_por_pagina)
        if pagina >= total_paginas:
            break

        pagina += 1
    # Após coleta de todas as páginas, salva os dados em CSV
    if todos_dados:
        df = pd.DataFrame(todos_dados)
        file_path = os.path.join(DATA_DIR, 'dados_api.csv')
        df.to_csv(file_path, index=False, encoding='utf-8')
        print("Arquivo salvo em", file_path)
    else:
        print("Nenhum dado foi extraído da API.")

