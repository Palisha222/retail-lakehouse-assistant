import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse
import os

# --- CONFIGURATION ---
username = 'postgres'
password = 'v@mpire@bsessed17'
host = 'localhost'
port = '5432'
database = 'postgres'
DATA_FOLDER = 'Data'
# ---------------------

encoded_password = urllib.parse.quote_plus(password)
db_connection_str = f'postgresql://{username}:{encoded_password}@{host}:{port}/{database}'
db_connection = create_engine(db_connection_str)

files_to_load = [
    ('dim_customer.csv', 'dim_customer'),
    ('dim_product.csv', 'dim_product'),
    ('dim_store.csv', 'dim_store'),
    ('dim_date.csv', 'dim_date'),
    ('fact_sales.csv', 'fact_sales')
]

def load_data():
    # 1. Clear existing data (Child first, then Parents)
    with db_connection.begin() as conn:
        print("Clearing existing data...")
        conn.execute(text("TRUNCATE TABLE fact_sales, dim_customer, dim_product, dim_store, dim_date RESTART IDENTITY CASCADE;"))

    # 2. Load data
    for file_name, table_name in files_to_load:
        file_path = os.path.join(DATA_FOLDER, file_name)
        print(f"Loading {file_name} into {table_name}...")
        df = pd.read_csv(file_path)
        df.to_sql(table_name, db_connection, if_exists='append', index=False)
        print(f"Successfully loaded {table_name}!")

if __name__ == "__main__":
    load_data()
    print("All data loaded successfully.")