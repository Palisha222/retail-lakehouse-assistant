# import re
# from tools.lakehouse_tool import execute_query, get_schema_info
# from tools.time_travel_tool import query_snapshot
# from query_engine import current_snapshot

# def run_agent(user_message: str) -> str:
#     """
#     Simulates the Conversational AI Agent.
#     If an API key is not configured, it runs in a rule-based hybrid mode:
#     1. It interprets common plain-English requests and translates them to SQL.
#     2. If the input is raw SQL starting with SELECT, it executes it directly.
#     3. Otherwise, it provides guidance on how to query the lakehouse.
#     """
#     msg = user_message.strip().lower()

#     # 1. Handle common plain English questions
#     # Question: Top products
#     if "top" in msg and "product" in msg:
#         limit = 5
#         match = re.search(r"top\s+(\d+)", msg)
#         if match:
#             limit = int(match.group(1))
        
#         sql = f"""
#             SELECT p.product_name, p.category, ROUND(SUM(s.total_amount), 2) AS revenue 
#             FROM local.db.fact_sales s
#             JOIN local.db.dim_product p ON s.product_id = p.product_id
#             GROUP BY p.product_name, p.category
#             ORDER BY revenue DESC
#             LIMIT {limit}
#         """
#         try:
#             records = execute_query(sql)
#             if not records:
#                 return "No product sales data found in the lakehouse."
            
#             response = f"### Top {limit} Products by Revenue\n\n"
#             response += "| Product Name | Category | Revenue ($) |\n"
#             response += "| :--- | :--- | :--- |\n"
#             for row in records:
#                 response += f"| {row.get('product_name')} | {row.get('category')} | ${row.get('revenue'):,.2f} |\n"
#             return response
#         except Exception as e:
#             return f"Error executing query: {str(e)}"

#     # Question: Total orders
#     elif "total" in msg and "order" in msg:
#         sql = "SELECT COUNT(*) AS total_orders FROM local.db.fact_sales"
#         try:
#             records = execute_query(sql)
#             total = records[0]["total_orders"] if records else 0
#             return f"### Total Orders\n\nThere have been a total of **{total:,}** orders placed in the retail lakehouse."
#         except Exception as e:
#             return f"Error executing query: {str(e)}"

#     # Question: Total revenue
#     elif "total" in msg and "revenue" in msg or "sales" in msg and "revenue" in msg:
#         sql = "SELECT ROUND(SUM(total_amount), 2) AS total_revenue FROM local.db.fact_sales"
#         try:
#             records = execute_query(sql)
#             revenue = records[0]["total_revenue"] if records else 0.0
#             return f"### Total Revenue\n\nThe total revenue recorded in the lakehouse is **${revenue:,.2f}**."
#         except Exception as e:
#             return f"Error executing query: {str(e)}"

#     # Question: Time travel / Look up orders X days ago / past snapshots
#     elif "orders" in msg and ("ago" in msg or "snapshot" in msg or "history" in msg):
#         try:
#             # Let's get the active snapshots list
#             df_snapshots = current_snapshot()
#             records_snapshots = df_snapshots.toPandas().to_dict(orient="records")
#             if not records_snapshots:
#                 return "No snapshots found for the sales fact table."
            
#             # Sort snapshots by committed_at ascending
#             records_snapshots = sorted(records_snapshots, key=lambda x: x["committed_at"])
            
#             # Default to the first (historical) snapshot for comparison
#             target_snapshot = records_snapshots[0]
#             snapshot_id = target_snapshot["snapshot_id"]
#             timestamp = target_snapshot["committed_at"]
            
#             # Execute count at that historical snapshot
#             sql_historical = "SELECT COUNT(*) AS total_orders FROM local.db.fact_sales"
#             historical_res = query_snapshot(snapshot_id, sql_historical)
#             historical_count = historical_res[0]["total_orders"] if historical_res else 0
            
#             # Current count
#             sql_current = "SELECT COUNT(*) AS total_orders FROM local.db.fact_sales"
#             current_res = execute_query(sql_current)
#             current_count = current_res[0]["total_orders"] if current_res else 0
            
#             response = f"### Iceberg Time Travel Summary\n\n"
#             response += f"* **Current Snapshot Orders:** {current_count:,} orders\n"
#             response += f"* **Historical Snapshot Orders:** {historical_count:,} orders (as of snapshot `{snapshot_id}` committed at `{timestamp}`)\n\n"
#             response += "This comparison demonstrates Apache Iceberg's time-travel capability, querying snapshot history without restoring data files."
#             return response
#         except Exception as e:
#             return f"Error retrieving historical snapshot: {str(e)}"

#     # Question: Show schema / tables
#     elif "schema" in msg or "tables" in msg or "columns" in msg:
#         try:
#             schemas = get_schema_info()
#             response = "### Retail Lakehouse Schema & Tables\n\n"
#             for table, cols in schemas.items():
#                 response += f"#### Table: `local.db.{table}`\n"
#                 response += "```\n"
#                 for col_str in cols:
#                     response += f"  - {col_str}\n"
#                 response += "```\n"
#             return response
#         except Exception as e:
#             return f"Error listing schemas: {str(e)}"

#     # 2. Allow raw SELECT SQL queries directly
#     elif msg.startswith("select"):
#         try:
#             records = execute_query(user_message)
#             if not records:
#                 return "Query returned 0 results."
            
#             # Format JSON records as a markdown table
#             headers = list(records[0].keys())
#             response = "### SQL Execution Results\n\n"
#             response += "| " + " | ".join(headers) + " |\n"
#             response += "| " + " | ".join([":---" for _ in headers]) + " |\n"
#             for row in records:
#                 vals = [str(row.get(h)) for h in headers]
#                 response += "| " + " | ".join(vals) + " |\n"
#             return response
#         except Exception as e:
#             return f"### SQL Execution Error\n\n```\n{str(e)}\n```"

#     # 3. Default fallback guidance
#     else:
#         return (
#             "### Retail Lakehouse Assistant (Mock Agent Mode)\n\n"
#             "I am ready to help you analyze your Apache Iceberg retail data. Since no API key is configured, "
#             "I am running in rule-based mode. You can try asking:\n\n"
#             "* **\"Show schema\"** to list all catalog tables and columns.\n"
#             "* **\"Total orders\"** to get the count of all retail transactions.\n"
#             "* **\"Total revenue\"** to see total sales values.\n"
#             "* **\"Top 5 products\"** to fetch products generating highest sales.\n"
#             "* **\"Orders history\"** to perform an Iceberg time-travel snapshot comparison.\n\n"
#             "*Or, you can write any raw SQL query starting with **`SELECT`** directly (e.g. `SELECT * FROM local.db.dim_store LIMIT 3`).*"
#         )


import re
from tools.lakehouse_tool import execute_query, get_schema_info
from tools.time_travel_tool import query_snapshot
from query_engine import current_snapshot

def run_agent(user_message: str) -> str:
    msg = user_message.strip().lower()

    # --- 1. Raw SQL Path ---
    if msg.startswith("select "):
        try:
            records = execute_query(user_message)
            return format_to_markdown(records)
        except Exception as e:
            return f"### SQL Execution Error\n\n```\n{str(e)}\n```"

    # --- 2. Flexible NLP Path (Use regex for better matching) ---
    
    # Match questions about products (e.g., "best products", "top products", "which products sold most")
    if re.search(r"(top|best|most)\s+(product|item)", msg):
        limit = 5
        match = re.search(r"(\d+)", msg)
        if match: limit = int(match.group(1))
        
        sql = f"SELECT p.product_name, p.category, ROUND(SUM(s.total_amount), 2) AS revenue FROM local.db.fact_sales s JOIN local.db.dim_product p ON s.product_id = p.product_id GROUP BY p.product_name, p.category ORDER BY revenue DESC LIMIT {limit}"
        return format_to_markdown(execute_query(sql))

    # Match questions about volume (e.g., "count orders", "how many orders", "total orders")
    elif re.search(r"(count|how many|total)\s+(order|transaction)", msg):
        sql = "SELECT COUNT(*) AS total_orders FROM local.db.fact_sales"
        records = execute_query(sql)
        total = records[0]["total_orders"]
        return f"### Total Orders\n\nThere have been **{total:,}** orders in the lakehouse."

    # Match questions about revenue (e.g., "how much money", "total revenue", "total sales")
    elif re.search(r"(total|sum)\s+(revenue|sales|money)", msg):
        sql = "SELECT ROUND(SUM(total_amount), 2) AS total_revenue FROM local.db.fact_sales"
        records = execute_query(sql)
        revenue = records[0]["total_revenue"]
        return f"### Total Revenue\n\nThe total revenue is **${revenue:,.2f}**."

    # Match schema/table questions
    elif re.search(r"(schema|table|column|list)", msg):
        return format_schema_response(get_schema_info())

    # --- 3. Default Fallback ---
    return "I'm not sure how to answer that. Try asking about 'Total Revenue', 'Top products', or use a raw SQL `SELECT` statement."

# --- Helper functions to keep code clean ---
def format_to_markdown(records):
    if not records: return "No results found."
    headers = list(records[0].keys())
    response = "| " + " | ".join(headers) + " |\n"
    response += "| " + " | ".join([":---" for _ in headers]) + " |\n"
    for row in records:
        response += "| " + " | ".join([str(row.get(h, '')) for h in headers]) + " |\n"
    return response

def format_schema_response(schemas):
    response = "### Retail Lakehouse Schema\n\n"
    for table, cols in schemas.items():
        response += f"#### `{table}`\n- " + "\n- ".join(cols) + "\n"
    return response