from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from query_engine import (
    total_orders,
    top_products,
    sales_by_store,
    current_snapshot,
)
from tools.lakehouse_tool import execute_query
from tools.time_travel_tool import query_snapshot
from agent import run_agent

app = FastAPI(
    title="Retail Lakehouse API",
    description="API for querying Apache Iceberg retail data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Vite dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Retail Lakehouse API is running!"}


@app.get("/orders")
def get_total_orders():
    df = total_orders()
    return {"total_orders": df.collect()[0]["total_orders"]}


@app.get("/top-products")
def get_top_products(limit: int = 5):
    df = top_products(limit)
    results = [
        {
            "product_id": row["product_id"],
            "revenue": float(row["revenue"]) if row["revenue"] is not None else None,
        }
        for row in df.collect()
    ]
    return results


@app.get("/sales-by-store")
def get_sales_by_store():
    df = sales_by_store()
    results = [
        {
            "store_id": row["store_id"],
            "revenue": float(row["revenue"]) if row["revenue"] is not None else None,
        }
        for row in df.collect()
    ]
    return results


@app.get("/snapshots")
def get_snapshots():
    df = current_snapshot()
    return df.toPandas().to_dict(orient="records")


@app.post("/query")
def run_query(payload: dict = Body(...)):
    sql = payload.get("sql")
    if not sql:
        return {"error": "SQL query is required."}
    try:
        return execute_query(sql)
    except ValueError as e:
        return {"error": str(e)}


@app.post("/time-travel")
def run_time_travel(payload: dict = Body(...)):
    snapshot_id = payload.get("snapshot_id")
    sql = payload.get("sql")
    if not snapshot_id or not sql:
        return {"error": "snapshot_id and sql are required."}
    try:
        return query_snapshot(snapshot_id, sql)
    except ValueError as e:
        return {"error": str(e)}


@app.post("/chat")
def chat_endpoint(payload: dict = Body(...)):
    """
    Natural-language endpoint. Gemini's automatic function calling (in
    agent.py) decides on its own which lakehouse tools to call
    (get_schema, run_sql_query, query_time_travel) to answer the
    question, e.g.:
      - "what's the total record count in fact_sales?"
      - "top 5 products by revenue last month"
      - "what did total orders look like 3 days ago?"
    """
    message = payload.get("message")
    if not message:
        return {"error": "Message is required."}

    try:
        response_text = run_agent(message)
    except Exception as e:
        return {"error": f"Agent failed to respond: {str(e)}"}

    return {"response": response_text}