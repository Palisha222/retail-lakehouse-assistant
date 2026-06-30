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


def query_snapshot(snapshot_id: int, sql: str):
    """
    Executes a read-only SQL query against a specific Iceberg snapshot.
    """

    sql = sql.strip()

    # Only allow SELECT queries
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

    # Replace table reference with VERSION AS OF
    sql = sql.replace(
        "local.db.fact_sales",
        f"local.db.fact_sales VERSION AS OF {snapshot_id}"
    )

    df = spark.sql(sql)
    records = df.toPandas().to_dict(orient="records")

    return sanitize_records(records)