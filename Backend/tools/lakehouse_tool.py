import math
from query_engine import spark


def sanitize_value(value):
    """
    Recursively replace NaN/Infinity with None so the result
    can always be safely JSON-serialized (Starlette's default
    JSONResponse uses allow_nan=False).
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
    """

    sql = sql.strip()

    # Allow only SELECT queries
    if not sql.lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")

    forbidden = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "merge",
        "create",
        "call"
    ]

    for word in forbidden:
        if word in sql.lower():
            raise ValueError(f"{word.upper()} statements are not allowed.")

    df = spark.sql(sql)
    records = df.toPandas().to_dict(orient="records")

    return sanitize_records(records)


def get_schema_info():
    """
    Returns column names and types for all retail lakehouse tables.
    Useful for guiding the agent on table schemas.
    """
    tables = ["dim_customer", "dim_product", "dim_store", "dim_date", "fact_sales"]
    schemas = {}
    for t in tables:
        try:
            df = spark.sql(f"DESCRIBE local.db.{t}")
            rows = df.collect()
            schemas[t] = [f"{row['col_name']}: {row['data_type']}" for row in rows]
        except Exception as e:
            schemas[t] = f"Error: {str(e)}"
    return schemas