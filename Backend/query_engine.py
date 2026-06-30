import os
import sys
from pyspark.sql import SparkSession

# ==========================================================
# Environment Configuration
# ==========================================================

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

os.environ["HADOOP_HOME"] = r"C:\hadoop"

os.environ["PATH"] = (
    os.path.join(os.environ["HADOOP_HOME"], "bin")
    + os.path.pathsep
    + os.environ["PATH"]
)

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WAREHOUSE_DIR = os.path.join(
    BASE_DIR,
    "Iceberg",
    "output",
    "iceberg_warehouse"
)

# ==========================================================
# Create Spark Session
# ==========================================================

def create_spark_session():

    spark = (
        SparkSession.builder
        .appName("RetailLakehouse")
        .master("local[*]")

        .config(
            "spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2"
        )

        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
        )

        .config(
            "spark.sql.catalog.local",
            "org.apache.iceberg.spark.SparkCatalog"
        )

        .config(
            "spark.sql.catalog.local.type",
            "hadoop"
        )

        .config(
            "spark.sql.catalog.local.warehouse",
            WAREHOUSE_DIR
        )

        .config(
            "spark.sql.defaultCatalog",
            "local"
        )

        .getOrCreate()
    )

    return spark


# ==========================================================
# Create Spark Session
# ==========================================================

spark = create_spark_session()

print("=" * 60)
print("Retail Lakehouse Connected Successfully")
print(f"Spark Version : {spark.version}")
print(f"Warehouse     : {WAREHOUSE_DIR}")
print("=" * 60)

# ==========================================================
# Query Functions
# ==========================================================

def total_orders():

    df = spark.sql("""
        SELECT COUNT(*) AS total_orders
        FROM local.db.fact_sales
    """)

    return df


def top_products(limit=5):

    df = spark.sql(f"""
        SELECT
            product_id,
            SUM(total_amount) AS revenue
        FROM local.db.fact_sales
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT {limit}
    """)

    return df


def sales_by_store():

    df = spark.sql("""
        SELECT
            store_id,
            SUM(total_amount) AS revenue
        FROM local.db.fact_sales
        GROUP BY store_id
        ORDER BY revenue DESC
    """)

    return df


def current_snapshot():

    df = spark.sql("""
        SELECT *
        FROM local.db.fact_sales.snapshots
    """)

    return df


def time_travel(snapshot_id):

    df = spark.sql(f"""
        SELECT *
        FROM local.db.fact_sales
        VERSION AS OF {snapshot_id}
    """)

    return df


# ==========================================================
# Run only when executed directly
# ==========================================================

if __name__ == "__main__":

    print("\nTesting Iceberg Connection...\n")

    print("Total Orders")
    total_orders().show()

    print("\nTop Products")
    top_products().show()

    print("\nSnapshots")
    current_snapshot().show(truncate=False)