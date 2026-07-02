"""
Gemini-based agent for the retail lakehouse chat assistant.

IMPORTANT: this uses the CURRENT Google SDK (`google-genai`), not the old
`google.generativeai` package, which Google has deprecated and archived.
If you already have code using `google.generativeai`, swap it for this —
the old package is not guaranteed to keep working with newer models.

Install:
    pip install google-genai python-dotenv

Env (get a free-tier key at https://aistudio.google.com/apikey):
    GEMINI_API_KEY=...
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.lakehouse_tool import execute_query, get_schema_info as _get_schema_info
from tools.time_travel_tool import query_snapshot as _query_snapshot

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set. "
        "Get a free key at https://aistudio.google.com/apikey and add it "
        "to your .env file."
    )

client = genai.Client(api_key=api_key)

# gemini-2.5-flash: free tier is ~10-15 requests/minute depending on your
# account. gemini-3.5-flash is newer/smarter but capped at just 5 RPM on
# the free tier, which is easy to blow through while testing — that's the
# 429 RESOURCE_EXHAUSTED error you hit. Swap back to "gemini-3.5-flash" if
# you upgrade to a paid tier later. Check current limits at
# https://ai.google.dev/gemini-api/docs/rate-limits
MODEL_NAME = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# System instruction: this is what lets the model turn "what's the total
# record count?" into correct SQL instead of guessing table/column names.
# Update this if your Week 1 schema differs.
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """You are a data analyst assistant for a retail Apache Iceberg lakehouse.

Catalog: local.db
Tables:
  - dim_customer  (customer dimension)
  - dim_product   (product dimension)
  - dim_store     (store dimension)
  - dim_date      (date dimension)
  - fact_sales    (sales / orders fact table)

Rules:
1. If you are not certain of exact column names, call get_schema first.
   Never invent a column or table name.
2. Always answer using run_sql_query (for current data) or
   query_time_travel (for "as of <date/snapshot>" questions). Never state
   a number you did not get from a tool call.
3. Always use fully qualified table names: local.db.<table>.
4. When you report a number, briefly name the table/query it came from
   (and the snapshot/date, if it was a time-travel query).
5. If a query fails, explain the error in plain language rather than
   silently retrying with a guess.
"""


# ---------------------------------------------------------------------------
# Tool functions — google-genai's automatic function calling builds the
# schema from these type hints + docstrings, so both need to be accurate.
# ---------------------------------------------------------------------------
def get_schema() -> dict:
    """Get column names and types for every table in the retail lakehouse
    (dim_customer, dim_product, dim_store, dim_date, fact_sales). Call this
    before writing SQL if you are unsure of a column name."""
    return _get_schema_info()


def run_sql_query(sql: str) -> str:
    """Run a read-only SQL query (SELECT, SHOW, or DESCRIBE) against the
    CURRENT state of the Iceberg lakehouse and return the resulting rows.

    Args:
        sql: A fully qualified, read-only SQL query, e.g.
             "SELECT COUNT(*) AS total FROM local.db.fact_sales"
    """
    return str(execute_query(sql))


def query_time_travel(snapshot_id: str, sql: str) -> str:
    """Run a read-only SQL query against a specific historical Iceberg
    snapshot of fact_sales. Use this for "as of <date>" or "N days ago"
    questions. Write the SQL as if the historical table were named
    `historical_data`, e.g. "SELECT COUNT(*) FROM historical_data".

    Args:
        snapshot_id: The Iceberg snapshot ID to query against
        sql: SQL written against the table name `historical_data`
    """
    return str(_query_snapshot(snapshot_id, sql))


_config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    tools=[get_schema, run_sql_query, query_time_travel],
)


def run_agent(user_message: str) -> str:
    """
    Sends a user message to Gemini with the lakehouse tools attached.
    Automatic function calling handles the tool-call loop (including
    calling get_schema first if needed) and returns the final text answer.
    """
    try:
        chat = client.chats.create(model=MODEL_NAME, config=_config)
        response = chat.send_message(user_message)
        return response.text or "I couldn't generate an answer."
    except genai.errors.ClientError as e:
        if getattr(e, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e):
            return (
                "I'm being rate-limited by the free-tier Gemini API "
                "(too many requests this minute). Wait about a minute "
                "and try again."
            )
        return f"The model API returned an error: {e}"