import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="etl_projeto",
        user="postgres",
        password="sua_senha"
    )
    print("Conexão bem-sucedida!")
except Exception as e:
    print("Erro na conexão:", e)
finally:
    if conn:
        conn.close()
