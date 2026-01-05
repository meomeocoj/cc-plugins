---
name: duckdb-federated-query
description: Query databases and explore data. Use when the user mentions database, query, SQL, table, schema, data exploration, "check the data", "look at the database", "what's in the table", "show me records", "find in database", PostgreSQL, MySQL, SQLite, cross-database joins, data validation, or export query results. Also triggers on: exploring schemas, sampling data, running analytics queries, checking data quality, or any task involving database operations.
---

# DuckDB Federated Query

Query and analyze data across PostgreSQL, MySQL, and SQLite databases using DuckDB as a unified query engine.

## FIRST STEP: Verify Database Credentials

**IMPORTANT**: Before using any query or exploration capabilities, verify which databases are configured.

### Check Available Databases

```bash
# List all configured database names
jq -r '.databases[].name' database-credentials.json

# Show database names and types (safe - no passwords)
jq -r '.databases[] | "\(.name): \(.type)"' database-credentials.json

# Check if specific database exists
jq -e '.databases[] | select(.name=="kolverse")' database-credentials.json >/dev/null && echo "Found" || echo "Not found"

# View database configuration WITHOUT exposing password
jq '.databases[] | select(.name=="your_db_name") | {name, type, host, database}' database-credentials.json
```

**Only proceed with queries after confirming your target database is listed above.**

---

## Quick Start

### Schema Exploration

```bash
# List all tables
python scripts/schema_explorer.py --name prod_db --list-tables

# Describe a specific table
python scripts/schema_explorer.py --name prod_db --describe users

# Sample data from a table
python scripts/schema_explorer.py --name prod_db --sample orders --limit 10
```

### Simple Queries

```bash
python scripts/federated_query.py \
  --name prod_db \
  --query "SELECT * FROM prod_db.users WHERE created_at >= '2024-01-01' LIMIT 10"
```

### Cross-Database Queries

```bash
python scripts/federated_query.py \
  --names prod_db,sales_db \
  --query "SELECT u.email, o.order_id FROM prod_db.users u JOIN sales_db.orders o ON u.id = o.user_id"
```

## Core Capabilities

### 1. Database Schema Exploration

Examine table structures, columns, and data types without writing SQL.

**Available operations:**
- `--list-tables`: Show all tables in database
- `--describe TABLE`: Show column names, types, nullability
- `--sample TABLE`: Preview rows from table
- `--stats TABLE`: Show row counts and column statistics

**Example workflow:**
```bash
# Step 1: List tables
python scripts/schema_explorer.py --name prod_db --list-tables

# Step 2: Examine specific table
python scripts/schema_explorer.py --name prod_db --describe users

# Step 3: Sample data
python scripts/schema_explorer.py --name prod_db --sample users --limit 5
```

### 2. Cross-Database Joins

Join tables across different database systems in a single query.

**Pattern:**
```sql
-- Databases are referenced by their credential names
-- For example, if you have "users_db" and "orders_db" in database-credentials.json

SELECT
    u.column,
    o.column
FROM users_db.table1 u
JOIN orders_db.table2 o ON u.id = o.foreign_id
```

**Example:**
```bash
python scripts/federated_query.py \
  --names users_db,orders_db \
  --query "
    SELECT
      u.email,
      COUNT(o.order_id) as total_orders
    FROM users_db.users u
    LEFT JOIN orders_db.orders o ON u.id = o.user_id
    GROUP BY u.email
    ORDER BY total_orders DESC
  "
```

### 3. Query Analysis

Analyze query performance and execution plans.

**Using EXPLAIN:**
```bash
python scripts/federated_query.py \
  --name prod_db \
  --query "EXPLAIN SELECT * FROM prod_db.large_table WHERE created_at >= '2024-01-01'"
```

### 4. Data Export

Export query results in multiple formats.

**Supported formats:** `table`, `json`, `csv`, `markdown`

```bash
# Export to JSON
python scripts/federated_query.py \
  --name prod_db \
  --query "SELECT * FROM prod_db.users" \
  --format json > output.json

# Export to CSV
python scripts/federated_query.py \
  --name prod_db \
  --query "SELECT * FROM prod_db.analytics" \
  --format csv > output.csv
```

## Credential Management

### Credential File Structure

The skill uses `database-credentials.json` to store database connections securely. See `database-credentials.example.json` for the full template.

**Key points:**
- Each database needs a unique `name` (this is what you reference in queries)
- Supported types: `postgres`, `mysql`, `sqlite`
- PostgreSQL/MySQL: requires `host`, `port`, `database`, `user`, `password`
- SQLite: requires `path` to database file

**Show available databases:**
```bash
# List all database names
jq -r '.databases[].name' database-credentials.json

# Show database types
jq -r '.databases[] | "\(.name): \(.type)"' database-credentials.json

# Check specific database exists
jq -e '.databases[] | select(.name=="kolverse")' database-credentials.json
```

### Security Best Practices

1. **Never commit credentials** - `database-credentials.json` is in `.gitignore`
2. **Use read-only accounts** - Grant minimal permissions for analytics queries
3. **Credential file location** - Keep in skill directory: `.claude/skills/duckdb-federated-query/`
4. **File permissions** - Restrict access: `chmod 600 database-credentials.json`
5. **Reference by name only** - Scripts read credentials automatically, just use `--name`

### Usage Patterns

**Single database:**
```bash
# Scripts read credentials from database-credentials.json automatically
python scripts/schema_explorer.py --name kolverse --list-tables
```

**Multiple databases (federated query):**
```bash
# Reference multiple databases by name (comma-separated)
python scripts/federated_query.py \
  --names kolverse,analytics_db \
  --query "SELECT * FROM kolverse.users u JOIN analytics_db.metrics m ON u.id = m.user_id"
```

## Common Query Patterns

### Schema Inspection
```sql
-- Use your credential name instead of "prod_db"
SHOW TABLES FROM prod_db;
DESCRIBE prod_db.table_name;
```

### Data Sampling
```sql
SELECT * FROM prod_db.large_table LIMIT 100;
SELECT * FROM prod_db.table TABLESAMPLE BERNOULLI(1);  -- 1% sample
```

### Aggregation
```sql
SELECT
    category,
    COUNT(*) as count,
    AVG(price) as avg_price
FROM prod_db.products
GROUP BY category
ORDER BY count DESC;
```

### Data Quality Checks
```sql
-- Find orphaned foreign keys across databases
-- Requires --names users_db,orders_db
SELECT 'orphaned_orders' as issue, COUNT(*) as count
FROM orders_db.orders o
LEFT JOIN users_db.users u ON o.user_id = u.id
WHERE u.id IS NULL;
```

For more patterns including three-way joins, window functions, and performance optimization, see [references/query_patterns.md](references/query_patterns.md).

## Available Extensions

DuckDB supports many database extensions:

**Pre-configured in scripts:**
- `postgres` - PostgreSQL databases
- `mysql` - MySQL/MariaDB databases
- `sqlite` - SQLite file databases

**Other useful extensions:**
- `httpfs` - Query remote files (S3, HTTP)
- `parquet` - Parquet file support
- `json` - JSON/NDJSON support
- `icu` - Advanced string operations

See [references/extensions.md](references/extensions.md) for detailed extension documentation and usage examples.

## Integration with Project

### Query Bronze/Silver Tables

```bash
# List all schemas and tables
python scripts/schema_explorer.py --name kolverse --list-tables

# Query silver layer data
python scripts/federated_query.py \
  --name kolverse \
  --query "SELECT account_id, COUNT(*) FROM kolverse.bronze.tweets GROUP BY account_id LIMIT 10"
```

### Compare with External Analytics

```bash
# Show available databases
jq -r '.databases[].name' database-credentials.json

# Join project data with external database by name
python scripts/federated_query.py \
  --names kolverse,external_analytics \
  --query "
    SELECT
      t.username,
      COUNT(t.id) as tweet_count,
      a.engagement_score
    FROM kolverse.bronze.tweets t
    LEFT JOIN external_analytics.twitter_metrics a ON t.account_id = a.account_id
    WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY t.username, a.engagement_score
    ORDER BY tweet_count DESC
  "
```

## Troubleshooting

### Credential Issues
```bash
# Verify database-credentials.json exists
ls -la database-credentials.json

# Show available databases
jq -r '.databases[].name' database-credentials.json

# Validate JSON syntax
jq . database-credentials.json

# Show specific database configuration (without exposing password)
jq '.databases[] | select(.name=="kolverse") | {name, type, host, database}' database-credentials.json
```

### Connection Errors
- Verify database is accessible: `psql -h HOST -U USER -d DATABASE` (use credentials from your config)
- Check firewall rules and port accessibility
- Confirm credentials in `database-credentials.json` are correct
- Test connection manually first before using the skill

### Extension Not Found
```python
# Install missing extension
con.execute("INSTALL postgres")
con.execute("LOAD postgres")
```

### Query Timeout
- Add LIMIT clause to large queries
- Use WHERE filters to reduce data scanned
- Consider materializing intermediate results

### Memory Issues
- Process data in batches
- Use streaming results: `con.execute(query).fetch_df_chunk()`
- Increase DuckDB memory limit: `con.execute("SET memory_limit='4GB'")`

## Resources

### Scripts
- **scripts/federated_query.py** - Main federated query tool (supports `--name`, `--names`)
- **scripts/schema_explorer.py** - Database schema exploration tool (supports `--name`)
- **scripts/credential_manager.py** - Credential loading and validation

### Credentials
- **database-credentials.json** - Your database credentials (gitignored, create from example)
- **database-credentials.example.json** - Template for credentials file

### References
- **references/extensions.md** - DuckDB extension documentation
- **references/connection_examples.md** - Connection string examples and patterns
- **references/query_patterns.md** - Common query patterns and optimizations
