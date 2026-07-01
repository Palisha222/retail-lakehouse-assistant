import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# --- Environment Setup for PySpark ---
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = (
    os.path.join(os.environ["HADOOP_HOME"], "bin")
    + os.path.pathsep
    + os.environ["PATH"]
)

# --- Define Paths relative to script location ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAREHOUSE_DIR = os.path.join(BASE_DIR, "Iceberg", "output", "iceberg_warehouse")
DATA_DIR = os.path.join(BASE_DIR, "Data")

def create_spark_session():
    """Initializes Spark Session with Apache Iceberg extensions and Hadoop catalog."""
    return (
        SparkSession.builder
        .appName("LoadDimensionsToIceberg")
        .master("local[*]")
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", WAREHOUSE_DIR)
        .config("spark.sql.defaultCatalog", "local")
        .getOrCreate()
    )

def main():
    spark = create_spark_session()
    print("=" * 60)
    print("SUCCESS: Spark Session connected successfully!")
    print(f"Warehouse Location: {WAREHOUSE_DIR}")
    print("=" * 60)
    
    # 1. Load dim_customer
    print("\n[1/4] Loading dim_customer...")
    df_customer = spark.read.option("header", "true").csv(os.path.join(DATA_DIR, "dim_customer.csv"))
    df_customer_transformed = df_customer.select(
        col("customer_id").cast("bigint"),
        col("first_name").cast("string"),
        col("last_name").cast("string"),
        col("email").cast("string"),
        col("signup_date").cast("date")
    )
    spark.sql("DROP TABLE IF EXISTS local.db.dim_customer")
    df_customer_transformed.writeTo("local.db.dim_customer").create()
    print("Loaded local.db.dim_customer successfully!")

    # 2. Load dim_product
    print("\n[2/4] Loading dim_product...")
    df_product = spark.read.option("header", "true").csv(os.path.join(DATA_DIR, "dim_product.csv"))
    df_product_transformed = df_product.select(
        col("product_id").cast("bigint"),
        col("product_name").cast("string"),
        col("category").cast("string"),
        col("price").cast("double")
    )
    spark.sql("DROP TABLE IF EXISTS local.db.dim_product")
    df_product_transformed.writeTo("local.db.dim_product").create()
    print("Loaded local.db.dim_product successfully!")

    # 3. Load dim_store
    print("\n[3/4] Loading dim_store...")
    df_store = spark.read.option("header", "true").csv(os.path.join(DATA_DIR, "dim_store.csv"))
    df_store_transformed = df_store.select(
        col("store_id").cast("bigint"),
        col("store_name").cast("string"),
        col("location").cast("string"),
        col("manager_name").cast("string")
    )
    spark.sql("DROP TABLE IF EXISTS local.db.dim_store")
    df_store_transformed.writeTo("local.db.dim_store").create()
    print("Loaded local.db.dim_store successfully!")

    # 4. Load dim_date
    print("\n[4/4] Loading dim_date...")
    df_date = spark.read.option("header", "true").csv(os.path.join(DATA_DIR, "dim_date.csv"))
    df_date_transformed = df_date.select(
        col("date_key").cast("date"),
        col("day").cast("int"),
        col("month").cast("int"),
        col("year").cast("int"),
        col("day_of_week").cast("string")
    )
    spark.sql("DROP TABLE IF EXISTS local.db.dim_date")
    df_date_transformed.writeTo("local.db.dim_date").create()
    print("Loaded local.db.dim_date successfully!")

    print("\n" + "=" * 60)
    print("VERIFICATION: Listing Tables in local.db:")
    spark.sql("SHOW TABLES IN local.db").show()
    print("=" * 60)

if __name__ == "__main__":
    main()
