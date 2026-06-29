-- Dimension: Customers
CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    signup_date DATE
);

-- Dimension: Products
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2)
);

-- Dimension: Stores
CREATE TABLE dim_store (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(255),
    location VARCHAR(255),
    manager_name VARCHAR(255)
);

-- Dimension: Dates
CREATE TABLE dim_date (
    date_key DATE PRIMARY KEY,
    day INT,
    month INT,
    year INT,
    day_of_week VARCHAR(20)
);

-- Fact Table: Sales
CREATE TABLE fact_sales (
    order_id INT PRIMARY KEY,
    order_date DATE REFERENCES dim_date(date_key),
    customer_id INT REFERENCES dim_customer(customer_id),
    product_id INT REFERENCES dim_product(product_id),
    store_id INT REFERENCES dim_store(store_id),
    quantity INT,
    total_amount DECIMAL(12, 2)
);