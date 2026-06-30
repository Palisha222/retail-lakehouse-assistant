from tools.lakehouse_tool import execute_query

result = execute_query("""
SELECT *
FROM local.db.fact_sales
LIMIT 5
""")

print(result)


# from tools.lakehouse_tool import execute_query

# result = execute_query("""
# DROP TABLE local.db.fact_sales
# """)

# print(result)
# Tjis query returned ValueError:Only SELECT statements are allowed.