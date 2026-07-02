from query_engine import spark


def query_snapshot(snapshot_id: str, sql: str):
    """
    Executes a read-only SQL query against a specific historical Iceberg
    snapshot of fact_sales.

    IMPORTANT: the caller's `sql` should reference the temp view name
    `historical_data`, e.g. "SELECT COUNT(*) FROM historical_data".
    (The previous version of this function created a temp view but then
    ran the raw SQL directly, so a query like "SELECT * FROM fact_sales"
    silently hit the *current* table instead of the snapshot. This
    version guards against that by rewriting bare references to the
    live table name to `historical_data` as a safety net, but the agent
    should always be told to use `historical_data` directly.)
    """
    try:
        df = (
            spark.read.option("snapshot-id", snapshot_id)
            .format("iceberg")
            .load("local.db.fact_sales")
        )
        df.createOrReplaceTempView("historical_data")

        # Safety net: if the model forgot and wrote the live table name,
        # redirect it to the snapshot view instead of silently querying
        # current data.
        safe_sql = sql.replace("local.db.fact_sales", "historical_data")
        safe_sql = safe_sql.replace("fact_sales", "historical_data")

        result_df = spark.sql(safe_sql)
        return result_df.toPandas().to_dict(orient="records")
    except Exception as e:
        return {"error": f"Failed to query snapshot {snapshot_id}: {str(e)}"}