-- Criação da Dimensão Cliente
CREATE TABLE dim_cliente (
    customer_id VARCHAR(255) PRIMARY KEY,
    customer_city VARCHAR(255),
    customer_state VARCHAR(255),
    customer_zip_code_prefix VARCHAR(10)
);

-- Criação da Dimensão Produto
CREATE TABLE dim_produto (
    product_id VARCHAR(255) PRIMARY KEY,
    product_category_name VARCHAR(255),
    product_photos_qty BIGINT,
    product_weight_g BIGINT,
    product_length_cm BIGINT,
    product_height_cm BIGINT,
    product_width_cm BIGINT
);

-- Criação da Tabela Fato Pedido
CREATE TABLE fato_pedido (
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
