import math
from query_engine import spark

def sanitize_value(value):
    """
    Recursively replace NaN/Infinity with None so the result
    can always be safely JSON-serialized.
    """
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_value(v) for v in value]
    return value

def sanitize_records(records):
    return [sanitize_value(row) for row in records]

def execute_query(sql: str):
    """
    Executes a read-only SQL query against the Iceberg warehouse.
    Supports SELECT, SHOW, and DESCRIBE.
    """
    sql = sql.strip()
    sql_lower = sql.lower()

    # FIX: Allow SHOW and DESCRIBE for metadata discovery
    allowed_starts = ("select", "show", "describe")
    if not sql_lower.startswith(allowed_starts):
        raise ValueError("Only SELECT, SHOW, and DESCRIBE statements are allowed.")

    forbidden = [
        "insert", "update", "delete", "drop", "alter", 
        "truncate", "merge", "create", "call"
    ]

    # Check for forbidden keywords
    for word in forbidden:
        # Check if the word exists as a standalone token to avoid false positives
        if f" {word} " in f" {sql_lower} ":
            raise ValueError(f"{word.upper()} statements are not allowed.")

    try:
        df = spark.sql(sql)
        records = df.toPandas().to_dict(orient="records")
        return sanitize_records(records)
    except Exception as e:
        return f"Error executing query: {str(e)}"

def get_schema_info():
    """
    Returns column names and types for all retail lakehouse tables.
    """
    tables = ["dim_customer", "dim_product", "dim_store", "dim_date", "fact_sales"]
    schemas = {}
    for t in tables:
        try:
            # Assumes your catalog is 'local.db'
            df = spark.sql(f"DESCRIBE local.db.{t}")
            rows = df.collect()
            schemas[t] = [f"{row['col_name']}: {row['data_type']}" for row in rows]
        except Exception as e:
            schemas[t] = f"Error: {str(e)}"
    return schemas