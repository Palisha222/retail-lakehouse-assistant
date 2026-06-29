import pandas as pd
import random
from faker import Faker
import os
import datetime

# --- CONFIGURATION ---
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 20
NUM_STORES = 5
NUM_SALES = 1000
DATA_DIR = 'Data'
# ---------------------

fake = Faker()
Faker.seed(42)
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Generate unique dates
start_date = datetime.date(2026, 1, 1)
date_list = [start_date + datetime.timedelta(days=i) for i in range(365)]
dates = pd.DataFrame([{
    'date_key': d,
    'day': d.day,
    'month': d.month,
    'year': d.year,
    'day_of_week': d.strftime('%A')
} for d in date_list])

# 2. Generate dimensions
customers = pd.DataFrame([{
    'customer_id': i,
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'email': fake.email(),
    'signup_date': fake.date_between(start_date='-2y', end_date='today')
} for i in range(NUM_CUSTOMERS)])

products = pd.DataFrame([{
    'product_id': i,
    'product_name': fake.word().capitalize() + " " + fake.job().split()[0],
    'category': fake.word().capitalize(),
    'price': round(random.uniform(10.0, 500.0), 2)
} for i in range(NUM_PRODUCTS)])

stores = pd.DataFrame([{
    'store_id': i,
    'store_name': fake.company(),
    'location': fake.city(),
    'manager_name': fake.name()
} for i in range(NUM_STORES)])

# 3. Generate Fact Table
sales_data = []
for i in range(NUM_SALES):
    price = round(random.uniform(10.0, 500.0), 2)
    qty = random.randint(1, 5)
    sales_data.append({
        'order_id': i,
        'order_date': random.choice(date_list),
        'customer_id': random.randint(0, NUM_CUSTOMERS - 1),
        'product_id': random.randint(0, NUM_PRODUCTS - 1),
        'store_id': random.randint(0, NUM_STORES - 1),
        'quantity': qty,
        'total_amount': round(price * qty, 2)
    })
sales = pd.DataFrame(sales_data)

# Save
customers.to_csv(f'{DATA_DIR}/dim_customer.csv', index=False)
products.to_csv(f'{DATA_DIR}/dim_product.csv', index=False)
stores.to_csv(f'{DATA_DIR}/dim_store.csv', index=False)
dates.to_csv(f'{DATA_DIR}/dim_date.csv', index=False)
sales.to_csv(f'{DATA_DIR}/fact_sales.csv', index=False)

print("Successfully generated star schema CSVs!")