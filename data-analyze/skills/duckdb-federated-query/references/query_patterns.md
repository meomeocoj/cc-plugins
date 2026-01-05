# Federated Query Patterns

Common patterns for querying across multiple databases using DuckDB.

## Basic Queries

### List Tables
```sql
SHOW TABLES FROM postgres_db;
```

### Describe Schema
```sql
DESCRIBE postgres_db.users;
```

### Sample Data
```sql
SELECT * FROM postgres_db.users LIMIT 10;
```

### Count Rows
```sql
SELECT COUNT(*) FROM postgres_db.orders;
```

## Cross-Database Joins

### Join PostgreSQL and MySQL
```sql
-- Attach databases
ATTACH 'host=localhost dbname=analytics' AS pg (TYPE POSTGRES);
ATTACH 'host=localhost database=sales' AS mysql (TYPE MYSQL);

-- Join across databases
SELECT
    u.id,
    u.email,
    o.order_id,
    o.total_amount
FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id
WHERE o.created_at >= '2024-01-01';
```

### Three-Way Join
```sql
-- PostgreSQL users, MySQL orders, SQLite products
SELECT
    u.email,
    o.order_id,
    p.product_name,
    o.quantity
FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id
JOIN sqlite.products p ON o.product_id = p.id
WHERE u.country = 'US';
```

## Aggregation Patterns

### Aggregate Across Databases
```sql
-- Total sales by country from multiple sources
SELECT
    u.country,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.amount) as total_revenue
FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id
GROUP BY u.country
ORDER BY total_revenue DESC;
```

### Window Functions
```sql
-- Rank users by order count
SELECT
    u.email,
    COUNT(o.order_id) as order_count,
    RANK() OVER (ORDER BY COUNT(o.order_id) DESC) as user_rank
FROM pg.users u
LEFT JOIN mysql.orders o ON u.id = o.user_id
GROUP BY u.email
ORDER BY order_count DESC;
```

## Data Export Patterns

### Export to Parquet
```sql
COPY (
    SELECT * FROM pg.users u
    JOIN mysql.orders o ON u.id = o.user_id
) TO 'joined_data.parquet' (FORMAT PARQUET);
```

### Export to CSV
```sql
COPY (
    SELECT * FROM pg.analytics_summary
) TO 'summary.csv' (HEADER, DELIMITER ',');
```

### Create Local DuckDB Table
```sql
-- Materialize cross-database query
CREATE TABLE local_summary AS
SELECT
    u.country,
    DATE_TRUNC('month', o.created_at) as month,
    SUM(o.amount) as revenue
FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id
GROUP BY u.country, month;
```

## Analysis Patterns

### Query Execution Plan
```sql
EXPLAIN ANALYZE
SELECT * FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id
WHERE u.created_at >= '2024-01-01';
```

### Data Quality Checks
```sql
-- Find mismatched IDs between databases
SELECT 'orphaned_orders' as issue, COUNT(*) as count
FROM mysql.orders o
LEFT JOIN pg.users u ON o.user_id = u.id
WHERE u.id IS NULL

UNION ALL

SELECT 'orphaned_users' as issue, COUNT(*) as count
FROM pg.users u
LEFT JOIN mysql.orders o ON u.id = o.user_id
WHERE o.user_id IS NULL;
```

### Duplicate Detection
```sql
-- Find duplicate users across databases
SELECT email, COUNT(*) as occurrences
FROM (
    SELECT email FROM pg.users
    UNION ALL
    SELECT email FROM mysql.customers
) combined
GROUP BY email
HAVING COUNT(*) > 1;
```

## Performance Optimization

### Use Query Pushdown
```sql
-- Filter is pushed to PostgreSQL
SELECT * FROM pg.large_table
WHERE created_at >= '2024-01-01'  -- Executed in PostgreSQL
  AND status = 'active'            -- Executed in PostgreSQL
LIMIT 1000;                        -- Executed in DuckDB
```

### Materialize Large Joins
```sql
-- For repeated queries, materialize intermediate results
CREATE TEMP TABLE user_orders AS
SELECT u.*, o.order_id, o.amount
FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id;

-- Now query the temp table
SELECT country, AVG(amount) FROM user_orders GROUP BY country;
```

### Selective Column Projection
```sql
-- Only select needed columns
SELECT u.id, u.email, o.amount  -- Not SELECT *
FROM pg.users u
JOIN mysql.orders o ON u.id = o.user_id;
```

## Project-Specific Patterns

### Query Bronze Tables via DuckDB
```python
# From the twitter-data-pipeline project
import duckdb

con = duckdb.connect(':memory:')
con.execute("INSTALL postgres")
con.execute("LOAD postgres")

# Attach project database
pg_conn = "host=localhost port=5432 dbname=kolverse user=postgres password=postgres"
con.execute(f"ATTACH '{pg_conn}' AS kolverse (TYPE POSTGRES)")

# Query bronze tables
result = con.execute("""
    SELECT
        account_id,
        username,
        COUNT(*) as tweet_count
    FROM kolverse.bronze.tweets
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY account_id, username
    ORDER BY tweet_count DESC
    LIMIT 10
""").df()

print(result)
con.close()
```

### Cross-Reference with External Data
```python
# Join project data with external MySQL analytics
con.execute(f"ATTACH '{pg_conn}' AS kolverse (TYPE POSTGRES)")
con.execute(f"ATTACH '{mysql_conn}' AS analytics (TYPE MYSQL)")

result = con.execute("""
    SELECT
        t.username,
        t.tweet_count,
        a.engagement_score
    FROM kolverse.bronze.tweets t
    LEFT JOIN analytics.twitter_metrics a ON t.account_id = a.account_id
    WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days'
""").df()
```
