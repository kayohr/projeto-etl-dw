-- Limpa as tabelas antes de carregar
TRUNCATE TABLE fato_pedido, dim_produto, dim_cliente;

-- Carregar dados da dimensão cliente
COPY dim_cliente(customer_id, customer_city, customer_state, customer_zip_code_prefix)
FROM '/data/dim_cliente.csv'
DELIMITER ',' CSV HEADER;

-- Carregar dados da dimensão produto
COPY dim_produto(product_id, product_category_name, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
FROM '/opt/airflow/data/dim_produto.csv'
DELIMITER ',' CSV HEADER;

-- Carregar dados da fato pedido
COPY fato_pedido(order_id, customer_id, product_id, order_status, order_purchase_timestamp, order_approved_at,
order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, price, freight_value,
review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp)
FROM '/data/fato_pedido.csv'
DELIMITER ',' CSV HEADER;
