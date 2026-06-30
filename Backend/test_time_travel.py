from tools.time_travel_tool import query_snapshot

snapshot_id = 8745330447939967342

result = query_snapshot(
    snapshot_id,
    """
    SELECT COUNT(*) AS total_orders
    FROM local.db.fact_sales
    """
)

print(result)