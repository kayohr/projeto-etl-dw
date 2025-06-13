# Projeto ETL com Data Warehouse + Airflow + Docker

##  Visão Geral do Projeto
- Este projeto visa demonstrar um pipeline completo de Engenharia de Dados com:
- Extração de dados via API (paginação inclusa).
- Transformação e tratamento dos dados.
- Modelagem de um Data Warehouse dimensional.
- Persistência dos dados em PostgreSQL.
- Automação completa via Airflow, tudo containerizado com Docker.
- Objetivo: desenvolver um pipeline modular, escalável, organizado e automatizado, seguindo boas práticas reais de Engenharia de Dados.


## Tecnologias Utilizadas
Python 3.11;</BR>
Pandas / Requests (Extração e transformação);</BR>
PostgreSQL 15 (Data Warehouse);</BR>
Docker e Docker Compose (Infraestrutura);</BR>
Apache Airflow 2.6 (Orquestração);</BR>
SQL (DDL e DML via COPY);</BR>
WSL2 (ambiente local de desenvolvimento;)</BR>
Visual Studio Code com extensão PostgreSQL (Chris Kolkman) para visualização do banco.</BR>

## Configuração do Ambiente
### Instalação de Dependências.</BR>
Instale as dependências Python:
```
pip install -r requirements.txt
````

## Organização do Projeto
### Primeira Estrutura do Projeto (sem Airflow ainda)
````
etl_projeto/
│
├── README.md
├── requirements.txt
│
├── data/                        # Área de armazenamento temporário
│   ├── dados_api.csv            # Dados extraídos brutos diretamente da API 
│   ├── dados_api_tratado.csv    # Dados tratados (limpeza, conversão de tipos) 
│   ├── dim_cliente.csv          # Dados da dimensão cliente (normalizados) 
│   ├── dim_produto.csv          # Dados da dimensão produto (normalizados)
│   └── fato_pedido.csv          # Dados da tabela fato (modelo  dimensional)
├── src/
│   ├── config/
│   │   └── config.py
│   ├── extract/
│   │   └── extract_api.py
│   ├── transform/
│   │   └── transform_data.py
│   └── load/
│       └── load_dw.py
│
└── main.py
````
</BR>

## Explicação de Cada Etapa
### Extração (extract_api.py)
- Utiliza requests para consumir uma API REST com paginação.
- Faz várias requisições iterativas, respeitando o número total de páginas.
- Salva o arquivo bruto dados_api.csv.

### Transformação (transform_data.py)
- Faz limpeza e preenchimento de dados nulos.
- Normaliza colunas com problemas de tipo.
- Realiza o particionamento lógico em:

- `dim_cliente.csv`
- `dim_produto.csv`
- `fato_pedido.csv`

### Carregamento (load_dw.py)
- Carrega os CSVs já tratados e estruturados para o banco PostgreSQL.
- Utiliza o comando COPY para alta performance na carga.

## Modelagem e Armazenamento
### Modelo dimensional: Esquema Estrela
- create_dw.sql: responsável por modelar o DW com as tabelas fato e dimensões.
- load_dw.sql: responsável por carregar os arquivos CSV transformados gerados no ETL para dentro do DW.</br></br>
Tabelas criadas:
````
Tabela dim_cliente
Campo	Tipo
customer_id	VARCHAR(255) PK
customer_city	VARCHAR(255)
customer_state	VARCHAR(255)
customer_zip_code_prefix	VARCHAR(10)

Tabela dim_produto
Campo	Tipo
product_id	VARCHAR(255) PK
product_category_name	VARCHAR(255)
product_photos_qty	INTEGER
product_weight_g	NUMERIC(10,2)
product_length_cm	NUMERIC(10,2)
product_height_cm	NUMERIC(10,2)
product_width_cm	NUMERIC(10,2)

Tabela fato_pedido
Campo	Tipo	                        Observação
order_id	VARCHAR(255)	            PK (chave primária)
customer_id	VARCHAR(255)	            FK → dim_cliente(customer_id)
product_id	VARCHAR(255)	            FK → dim_produto(product_id)
order_status	VARCHAR(50)	
order_purchase_timestamp	TIMESTAMP	
order_approved_at	TIMESTAMP	
order_delivered_carrier_date	TIMESTAMP	
order_delivered_customer_date	TIMESTAMP	
order_estimated_delivery_date	TIMESTAMP	
price	NUMERIC(10,2)	
freight_value	NUMERIC(10,2)	
review_score	INTEGER	
review_comment_title	TEXT	
review_comment_message	TEXT	
review_creation_date	DATE	
review_answer_timestamp	TIMESTAMP	


````
Todas as tabelas são carregadas com base nos CSVs gerados no processo de transformação.
</br></br>
### Orquestrador ETL: main.py</br>
O arquivo main.py é responsável por orquestrar todo o pipeline ETL de forma sequencial, em ambiente local, sem a necessidade do Airflow (modo manual de execução).
</br> Responsabilidade do main.py:
- Executa o extract_api.py → coleta os dados via API paginada.

- Executa o transform_data.py → realiza a limpeza e a geração dos CSVs já modelados.

* Executa o load_dw.py → carrega os arquivos CSV diretamente no PostgreSQL via SQL COPY.

* Permite executar o pipeline inteiro com um único comando:

## Como Rodar o PostgreSQL
Após subir o Docker:
````
docker-compose up -d
````
Acessar o PostgreSQL via terminal:
````
docker exec -it postgres-db psql -U postgres -d etl_projeto
````
Rodar os scripts de criação de schema e carga. Dentro do PostgreSQL via psql rodando dentro do container Docker psql:
````
\i /sql/create_dw.sql
\i /sql/load_dw.sql
````

## Nova Estrutura Final com Airflow (Automatizado)
Agora com a inclusão do Airflow para automação do ETL:
````
etl_projeto/
│
├── data/
├── sql/
├── src/
├── postgres_data/
│
├── airflow/
│   ├── dags/
│   │   └── etl_pipeline.py
│   ├── logs/
│   ├── plugins/
│   └── docker-compose.yml
│
└── docker-compose.yml
````
Orquestração via Airflow
DAG etl_pipeline.py
O Airflow orquestra:

1- Extract: Vai buscar os dados na API.</br>
Faz requisições paginadas, trata os dados NaN → null, e salva o CSV bruto no diretório data/.</br>
2- Ler o CSV bruto, fazer limpeza, tratar tipos, remover inconsistências, normalizar, gerar o dados_api_tratado.csv.
</BR>
3- Carrega o dados_api_tratado.csv para o banco de dados.</br>
Faz o TRUNCATE nas tabelas fato e dimensões.</br>
Insere os dados limpos e formatados nas tabelas do DW.</br>
Tudo containerizado e escalável.</br>
</br>
Todo dia ele vai executar o fluxo completo automaticamente.</br>
Não precisa mais rodar scripts manuais.</br>
O Airflow cuida de todo o ciclo de vida do seu pipeline de dados.</br></br>
RESUMINDO:
</BR>
- Pipeline completa de ETL orquestrada com Airflow:</BR>
- Automação de extração de dados via API paginada.</br>
- Tratamento incremental com limpeza de dados.</br>
- Carga automatizada para Data Warehouse Postgres.</br>
- Infraestrutura dockerizada.</br>
- Código versionado e escalável.</br>

### Ponto importante! </br>
Foi criado dois compose docker-compose-postgres.yml e docker-compose-airflow.yml tem que dar um ````docker network create airflow-network```` e adicionar em cada compose:
````
networks:
  - airflow-network
````
Após isso fazer novamente o ````docker-compose -f docker-compose-postgres.yml up -d```` e ````docker-compose -f docker-compose-airflow.yml up -d````.
## Diagrama Resumido da Arquitetura
````
API -> extract_api.py -> dados_api.csv
         ↓
   transform_data.py -> dim_cliente.csv / dim_produto.csv / fato_pedido.csv
         ↓
   load_dw.py + SQL COPY -> PostgreSQL (DW)
         ↓
  Airflow controla tudo via DAG
  ````