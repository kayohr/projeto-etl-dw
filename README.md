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
### Primeira Estrutura do Projeto (sem Airflow)
````
etl_projeto/
│
├── README.md                 --> Documentação do projeto
├── requirements.txt          --> Dependências Python
│
├── sql/                      --> Scripts de criação de tabelas DW
│   └── create_dw.sql         --> Contém o DDL para criar as tabelas (dimensões e fato)
│
├── src/                      --> Código dividido por etapas do ETL
│   ├── config/
│   │   └── config.py         --> Arquivo de configuração (API URL, token, banco)
│   │
│   ├── extract/
│   │   └── extract_api.py    --> Código de extração da API e geração do CSV bruto
│   │
│   ├── transform/
│   │   └── transform_data.py --> Código de transformação e limpeza de dados
│   │
│   └── load/
│       └── load_dw.py        --> Código de carga no DW Postgres (usa create_dw.sql)
│
└── main.py                   --> Orquestrador manual do ETL (chama extract → transform → load)

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
</br>
As tabelas seguem um esquema estrela clássico, com:</br>
1 create_dw.sql	Responsável por criar as tabelas no Data Warehouse (modelo físico)</br>
2 load_dw.py	Responsável por realizar a carga dos dados transformados (CSVs) para dentro do DW
</br></br>
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

### Fluxo de carga de dados</br>
As tabelas são alimentadas com base nos arquivos CSV gerados na etapa de transformação (dados_api_tratado.csv).

O arquivo load_dw.py realiza:
- Truncamento das tabelas (para evitar duplicatas)
- Inserção dos dados transformados nas tabelas de dimensão e fato.
</br></br>
### Orquestrador ETL: main.py</br>
Extração:
- Executa o extract_api.py
- Coleta os dados via API paginada.
- Salva os dados brutos em arquivos CSV no diretório data/.

Transformação:
- Executa o transform_data.py
- Realiza a limpeza, normalização e padronização dos dados.
- Gera os arquivos CSV transformados prontos para carga (dados_api_tratado.csv).

Carga:
- Executa o load_dw.py
- Realiza a carga dos dados transformados no banco de dados PostgreSQL.
- Insere os registros nas tabelas de fato e dimensões previamente criadas.

 Execução simplificada:
- Permite executar o pipeline completo com um único comando localmente:


## Como Rodar o PostgreSQL
Após subir o Docker:
````
docker-compose -f docker-compose-postgres.yml up -d
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
├── airflow/
│   ├── dags/
│   │   ├── etl_pipeline.py    --> DAG principal (Extract → Transform → Load)
│   │   └── provision_dw.py    --> DAG de criação de schema (executa o SQL ou equivalente via Python)
│   │
│   ├── logs/                  --> Logs gerados pelo Airflow (não versionados)
│   └── data/                  --> Onde o extract salva os CSVs (data/dados_api.csv, etc)
│
├── sql/
│   └── create_dw.sql          --> DDL usado na DAG provision_dw ou executado manualmente
│
├── src/
│   ├── config/
│   ├── extract/
│   ├── transform/
│   └── load/
│
├── docker-compose.yml         --> Infraestrutura completa Airflow + Postgres
├── requirements.txt
├── README.md
└── .gitignore

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
Airflow (DAG etl_pipeline.py)
   │
   ├── Task 1: Extract --> src/extract/extract_api.py --> Gera data/dados_api.csv
   │
   ├── Task 2: Transform --> src/transform/transform_data.py --> Gera data/dados_api_tratado.csv
   │
   └── Task 3: Load --> src/load/load_dw.py --> Carga final no Postgres DW


  ````

## Visão Geral do Projeto Airflow ETL
````
[API Externa]  -->  [Extract (src/extract)]  -->  [Transform (src/transform)]  -->  [Load (src/load)]  -->  [Postgres DW]

                        |
                        |
                    [Airflow]
                        |
       ----------------|----------------
      |                |               |
  [DAGs]         [Logs / Runtime]   [Plugins]

  ````