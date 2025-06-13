import requests
import json
import pandas as pd
import math
from config import config

import sys
import os

# Ajuste de sys.path (só necessário se estiver executando diretamente, no Airflow não precisa mais)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'src'))

# Diretório onde será salvo o CSV (caminho absoluto dentro do container)
DATA_DIR = '/opt/airflow/data'

# Garante que o diretório existe
os.makedirs(DATA_DIR, exist_ok=True)

def extract_data():
    pagina = 1
    todos_dados = []

    while True:
        params = {
            'token': config.token,
            'page': pagina
        }

        try:
            response = requests.get(config.base_url, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"Erro HTTP na requisição: {http_err}")
            break
        except requests.exceptions.RequestException as req_err:
            print(f"Erro na requisição: {req_err}")
            break

        try:
            texto_corrigido = response.text.replace('NaN', 'null')
            json_response = json.loads(texto_corrigido)
        except json.JSONDecodeError as json_err:
            print(f"Erro ao decodificar JSON corrigido: {json_err}")
            print("Conteúdo da resposta:", response.text)
            break
        except Exception as e:
            print("Erro inesperado ao processar a resposta JSON:", e)
            break

        dados = json_response.get('dados', [])
        todos_dados.extend(dados)

        total_linhas = json_response.get('total_linhas')
        linhas_por_pagina = json_response.get('linhas_por_pagina')

        if total_linhas is None or linhas_por_pagina is None:
            print("Resposta JSON não contém as chaves esperadas de paginação.")
            break

        total_paginas = math.ceil(total_linhas / linhas_por_pagina)
        if pagina >= total_paginas:
            break

        pagina += 1

    if todos_dados:
        df = pd.DataFrame(todos_dados)
        file_path = os.path.join(DATA_DIR, 'dados_api.csv')
        df.to_csv(file_path, index=False, encoding='utf-8')
        print("Arquivo salvo em", file_path)
    else:
        print("Nenhum dado foi extraído da API.")

