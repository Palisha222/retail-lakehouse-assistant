import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# 1. Environment Configuration (Keep these)
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["HADOOP_HOME"] = r"C:\hadoop" 
os.environ["PATH"] = os.path.join(os.environ["HADOOP_HOME"], "bin") + os.path.pathsep + os.environ["PATH"]

def create_spark_session():
    WAREHOUSE_DIR = os.path.abspath("output/iceberg_warehouse")
    return SparkSession.builder \
        .appName("RetailLakehouse") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", WAREHOUSE_DIR) \
        .config("spark.sql.defaultCatalog", "local") \
        .getOrCreate()

spark = create_spark_session()

print("======================================================")
print("SUCCESS: Spark Session connected successfully!")
print(f"Spark Version: {spark.version}")
print(f"Warehouse Location: {os.path.abspath('output/iceberg_warehouse')}")
print("======================================================")

# 2. Create Table with Hidden Partitioning
spark.sql("CREATE DATABASE IF NOT EXISTS local.db")
spark.sql("""
    CREATE TABLE IF NOT EXISTS local.db.fact_sales (
        order_id bigint, 
        order_date date, 
        customer_id bigint, 
        product_id bigint, 
        store_id bigint, 
        quantity bigint, 
        total_amount double
    ) 
    USING iceberg 
    PARTITIONED BY (days(order_date))
""")

# 3. Load Data
df = spark.read.option("header", "true").csv("../Data/fact_sales.csv")
df.write.mode("overwrite").saveAsTable("local.db.fact_sales")

# 4. Prove Partition Pruning (Explain Plan)
print("--- Partition Pruning Explain Plan ---")
spark.sql("SELECT * FROM local.db.fact_sales WHERE order_date = '2026-01-01'").explain(True)

# --- VERIFICATION STEP ---
print("\n--- SCHEMA VERIFICATION ---")
print("CSV Source Schema:")
df.printSchema() # Should show the columns from your CSV
print("Iceberg Table Schema:")
spark.table("local.db.fact_sales").printSchema() # Should show the columns we just created

# 5. Schema Evolution (Add a column)
print("\n--- Applying Schema Evolution ---")
spark.sql("ALTER TABLE local.db.fact_sales ADD COLUMN discount double")
print("Added 'discount' column. Metadata updated successfully.")

# 6. Demonstrate Time Travel
# Capture snapshot ID after initial load
snapshot_id = spark.sql("SELECT snapshot_id FROM local.db.fact_sales.snapshots").collect()[-1][0]
print(f"\nInitial Snapshot ID: {snapshot_id}")

# Query as it was before the schema change (at the initial snapshot)
print("\n--- Querying 'yesterday' (Time Travel) ---")
df_time_travel = spark.read.option("snapshot-id", snapshot_id).table("local.db.fact_sales")
df_time_travel.show(5)