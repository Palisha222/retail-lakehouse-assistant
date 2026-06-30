# retail-lakehouse-assistant

# Retail Lakehouse Migration & Conversational Query Assistant

## Project Overview

Modern retail organizations generate massive volumes of transactional data every day. Business teams frequently need answers to questions such as *"Which products generated the highest revenue last month?"* or *"How many orders were placed during the last weekend?"* Traditionally, these requests are handled by data engineers who write SQL queries against a data warehouse. While this approach works, it creates a dependency on technical teams, increases turnaround time, and limits the ability of business users to perform self-service analytics.

This project addresses that problem by migrating a traditional retail data warehouse to an **Apache Iceberg Lakehouse** and developing a conversational AI assistant that enables users to retrieve information using natural language instead of SQL. Rather than asking an engineer to write a query, users can simply ask questions through a chat interface, and the assistant retrieves answers directly from the Iceberg tables using dedicated query tools.

The project demonstrates several core capabilities of Apache Iceberg, including hidden partitioning, schema evolution, snapshot management, and time travel. These features improve data reliability, simplify maintenance, and provide historical access to data without requiring duplicate datasets or manual backups. On top of the lakehouse, a FastAPI backend and AI agent are used to translate natural language requests into safe, read-only queries against the data.

The overall objective is to build a modern analytics platform that combines the reliability of a data lakehouse with the accessibility of conversational AI.

---

# Project Objectives

The primary objectives of this project are:

- Migrate a retail star-schema warehouse into Apache Iceberg tables.
- Load retail data using Apache Spark.
- Demonstrate Iceberg hidden partitioning and metadata-based partition pruning.
- Demonstrate schema evolution without rewriting historical data.
- Demonstrate Iceberg time travel by querying historical snapshots.
- Develop an AI-powered conversational assistant capable of answering business questions using real data rather than generating estimated responses.
- Build a user-friendly React application that enables business users to interact with the data using natural language.

---

# Why Apache Iceberg?

Apache Iceberg is an open table format designed for large-scale analytical datasets. Unlike traditional Hive tables, Iceberg maintains rich metadata that allows queries to efficiently locate only the files required to answer a query. This significantly improves query performance while also providing advanced capabilities such as schema evolution, hidden partitioning, snapshot isolation, and time travel.

For a retail analytics platform where historical reporting and frequent data updates are common, these capabilities make Iceberg an ideal choice.

Some of the key advantages demonstrated throughout this project include:

- Hidden partitioning without changing SQL queries.
- Metadata-driven partition pruning.
- Safe schema evolution using field IDs.
- Snapshot-based version control.
- Historical querying using time travel.
- Atomic commits that prevent inconsistent writes.

---

# Project Architecture

The overall architecture consists of four primary layers.

1. Data ingestion using Apache Spark.
2. Apache Iceberg Lakehouse for storage.
3. FastAPI backend with AI query tools.
4. React-based conversational user interface.

The following diagram illustrates the complete architecture.

```

                        CSV Files / PostgreSQL
                                  │
                                  │
                          Apache Spark ETL
                                  │
                                  │
                     Apache Iceberg Lakehouse
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
 Lakehouse Query Tool                           Time Travel Tool
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  │
                           FastAPI Backend
                                  │
                          Claude Agent SDK
                                  │
                           React Chat Frontend

```

The Spark ETL process is responsible for ingesting retail source data and storing it inside Apache Iceberg tables. Iceberg maintains snapshots, metadata, and partition information that allow efficient querying and historical access.

The FastAPI application exposes endpoints that communicate with the AI agent. Instead of directly generating answers, the AI agent calls specialized tools capable of executing safe, read-only SQL queries against the Iceberg tables. This ensures that every response returned to the user is grounded in actual data stored in the lakehouse.

Finally, the React frontend provides a conversational interface where users can ask analytical questions in plain English and receive accurate responses without writing SQL.

---

# Technologies Used

This project combines several modern data engineering and application development technologies.

| Technology | Purpose |
|------------|---------|
| Apache Spark | Data ingestion and ETL processing |
| Apache Iceberg | Lakehouse table format |
| Hive Catalog | Metadata management |
| Python | Backend development |
| FastAPI | REST API |
| Claude Agent SDK | Conversational AI |
| MCP | AI tool integration |
| React | Frontend |
| Jotai | Local UI state management |
| TanStack Query | Server state management |

Each technology was selected because it addresses a specific requirement of the project. Spark provides scalable distributed data processing, while Iceberg adds modern table management features such as snapshots and schema evolution. FastAPI serves as the communication layer between the frontend and the AI agent, and React provides an intuitive interface for business users.

---

# Retail Data Warehouse Design

The retail warehouse follows a traditional star schema consisting of four dimension tables and one fact table.

### Dimension Tables

The dimension tables store descriptive information used for reporting and analysis.

- Date Dimension
- Product Dimension
- Customer Dimension
- Store Dimension

### Fact Table

The central fact table is **fact_sales**, which records every retail transaction.

The table contains the following columns:

| Column | Description |
|---------|-------------|
| order_id | Unique order identifier |
| order_date | Date of purchase |
| customer_id | Customer identifier |
| product_id | Product identifier |
| store_id | Store identifier |
| quantity | Number of units sold |
| total_amount | Total transaction value |
| discount_applied | Discount applied to the transaction |

The fact table is partitioned using Iceberg's hidden partitioning mechanism based on the order date, enabling efficient filtering without exposing partition columns to end users.



# Data Ingestion and Iceberg Table Creation

After designing the retail warehouse schema, the next step was to migrate the existing warehouse into an Apache Iceberg lakehouse. Rather than storing the data as ordinary Parquet files, each table was created using the Iceberg table format. Iceberg manages metadata separately from the data files, allowing it to provide advanced features such as snapshot management, hidden partitioning, schema evolution, and time travel.

Apache Spark was used as the processing engine for this migration because it provides native support for Apache Iceberg through the Spark SQL catalog. A Spark session was configured with the Iceberg extensions enabled, allowing SQL statements to create, modify, and query Iceberg tables directly.

The retail warehouse consists of four dimension tables—Date, Product, Customer, and Store—and a central fact table named **fact_sales**. Each table was created within the Iceberg catalog and stored inside the configured warehouse directory. Once the tables were created, the retail dataset was loaded into the Iceberg tables using Spark DataFrames.

The loading process preserved the warehouse structure while taking advantage of Iceberg's metadata management capabilities. Unlike traditional Hive tables, Iceberg stores metadata about snapshots, manifests, schemas, and partitions, making future maintenance operations significantly more efficient.

The following query was used to verify that the data had been successfully loaded into the fact table.

```sql
SELECT *
FROM local.db.fact_sales
LIMIT 5;
```

The output confirmed that the records had been successfully written into the Iceberg table.

**Insert Screenshot Here**

```
images/load_data.png
```

---

# Hidden Partitioning

One of Apache Iceberg's most valuable features is **hidden partitioning**. Traditional Hive partitioning requires users to understand how a table is partitioned and include partition columns explicitly in their SQL queries. This often leads to complicated SQL statements and poor query performance if users forget to include partition filters.

Iceberg removes this complexity by separating the logical schema from the physical storage layout. Instead of exposing partition columns, Iceberg records partition information inside its metadata and automatically determines which partitions should be scanned during query execution.

For this project, the **fact_sales** table was partitioned using the following partition transform:

```
days(order_date)
```

This transform groups all records belonging to the same calendar day into the same partition while allowing users to continue querying the original **order_date** column without any knowledge of the underlying partition structure.

The important advantage of hidden partitioning is that the SQL query remains clean and intuitive. Business users simply filter by the order date, while Iceberg transparently converts that filter into partition pruning using its metadata.

For example, the following query was executed without referencing any partition column.

```sql
SELECT *
FROM local.db.fact_sales
WHERE order_date = '2026-09-16';
```

Although the query appears identical to a normal SQL query, Iceberg internally identifies the matching partition and scans only the files belonging to that partition instead of scanning the entire table.

This greatly reduces disk I/O and improves query performance, especially when working with large datasets.

---

# Demonstrating Metadata-Based Partition Pruning

Simply claiming that hidden partitioning works is not sufficient. The project requirements specifically require demonstrating that Iceberg actually skips unnecessary files during query execution.

To verify this behavior, Spark's execution plan was inspected using the **explain()** function.

Two execution plans were generated:

1. A query without any filter.
2. A query filtering on a single order date.

The first query scans the complete Iceberg table.

```python
df = spark.sql("""
SELECT *
FROM local.db.fact_sales
""")

df.explain(True)
```

Because no filter is provided, Spark cannot eliminate any partitions. The execution plan therefore scans every partition contained within the Iceberg table.

**Insert Screenshot Here**

```
images/before_pruning.png
```

The second query filters the table by a specific order date.

```python
df = spark.sql("""
SELECT *
FROM local.db.fact_sales
WHERE order_date = '2026-09-16'
""")

df.explain(True)
```

Although the SQL statement never references a partition column, Iceberg recognizes that the table is partitioned using **days(order_date)**. During query planning, Iceberg consults its metadata and determines exactly which partition contains the requested date.

As a result, Spark scans only the required partition while skipping all unrelated partitions. This optimization is known as **partition pruning**, and it significantly reduces the amount of data that must be read from storage.

**Insert Screenshot Here**

```
images/after_pruning.png
```

Comparing the two execution plans clearly demonstrates the effect of metadata-driven pruning. The first execution plan scans the entire dataset, whereas the second execution plan scans only the relevant partition. Importantly, this optimization occurs automatically without requiring any changes to the SQL query.

This demonstrates one of the major advantages of Apache Iceberg over traditional partitioned tables: business users write simple SQL while Iceberg transparently optimizes the query using its metadata.

---

# Benefits Observed

Implementing hidden partitioning provided several important benefits during the project.

First, the SQL queries remained simple and readable because users continued filtering directly on the **order_date** column. There was no need to expose partition columns or educate users about the physical storage layout.

Second, Iceberg's metadata enabled Spark to avoid scanning unnecessary files, reducing the amount of data read during query execution. Even though this project used a relatively small dataset, the same optimization becomes increasingly valuable as datasets grow to millions or billions of records.

Finally, hidden partitioning allows the physical partition strategy to evolve over time without forcing application developers or analysts to modify their existing SQL queries. This separation between logical and physical design makes Iceberg considerably easier to maintain in production environments.

At this stage of the project, the retail warehouse had been successfully migrated into Apache Iceberg, the data had been loaded using Apache Spark, and hidden partitioning had been verified through execution plan analysis.













