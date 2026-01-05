---
name: unified-sql
description: Query databases and explore data. Use when the user mentions database, query, SQL, table, schema, data exploration, "check the data", "look at the database", "what's in the table", "show me records", "find in database", PostgreSQL, MySQL, SQLite, cross-database joins, data validation, or export query results. Also triggers on: exploring schemas, sampling data, running analytics queries, checking data quality, or any task involving database operations.
---

# Unified SQL

Query and analyze data across PostgreSQL, MySQL, and SQLite databases using DuckDB as a unified query engine.

---

## ⚠️ MANDATORY FIRST STEP: List Available Databases

**YOU MUST ALWAYS RUN THIS FIRST** before attempting ANY database operation.

**DO NOT** skip this step. **DO NOT** assume database names. **DO NOT** run queries until you see the list of available databases.

```bash
# ALWAYS run this first - find and list configured databases
CREDS=".claude/data-analyze/credentials.json"
if [ -f "./$CREDS" ]; then
  CREDS_FILE="./$CREDS"
  echo "Using project credentials: $CREDS_FILE"
elif [ -f "$HOME/$CREDS" ]; then
  CREDS_FILE="$HOME/$CREDS"
  echo "Using user credentials: $CREDS_FILE"
else
  echo "❌ No credentials file found!"
  echo "Create credentials at: ./.claude/data-analyze/credentials.json (project) or ~/.claude/data-analyze/credentials.json (user)"
  exit 1
fi

echo "Available databases:"
jq -r '.databases[] | "  - \(.name) (\(.type))"' "$CREDS_FILE"
```

**ONLY PROCEED** with queries after seeing the list of available databases above.

---

## Quick Start

### Schema Exploration

```bash
# List all tables
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name prod_db --list-tables

# Describe a specific table
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name prod_db --describe users

# Sample data from a table
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name prod_db --sample orders --limit 10
```

### Simple Queries

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
  --name prod_db \
  --query "SELECT * FROM prod_db.users WHERE created_at >= '2024-01-01' LIMIT 10"
```

### Cross-Database Queries

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
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
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name prod_db --list-tables

# Step 2: Examine specific table
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name prod_db --describe users

# Step 3: Sample data
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name prod_db --sample users --limit 5
```

### 2. Cross-Database Joins

Join tables across different database systems in a single query.

**Pattern:**
```sql
-- Databases are referenced by their credential names
-- For example, if you have "users_db" and "orders_db" in credentials.json

SELECT
    u.column,
    o.column
FROM users_db.table1 u
JOIN orders_db.table2 o ON u.id = o.foreign_id
```

**Example:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
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
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
  --name prod_db \
  --query "EXPLAIN SELECT * FROM prod_db.large_table WHERE created_at >= '2024-01-01'"
```

### 4. Data Export

Export query results in multiple formats.

**Supported formats:** `table`, `json`, `csv`, `markdown`

```bash
# Export to JSON
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
  --name prod_db \
  --query "SELECT * FROM prod_db.users" \
  --format json > output.json

# Export to CSV
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
  --name prod_db \
  --query "SELECT * FROM prod_db.analytics" \
  --format csv > output.csv
```

## Credential Management

### Credential File Structure

Credentials are stored in `.claude/data-analyze/credentials.json` and searched in order:
1. **Project**: `./.claude/data-analyze/credentials.json`
2. **User**: `~/.claude/data-analyze/credentials.json`

See `${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/credentials.example.json` for the template.

**Key points:**
- Each database needs a unique `name` (this is what you reference in queries)
- Supported types: `postgres`, `mysql`, `sqlite`
- PostgreSQL/MySQL: requires `host`, `port`, `database`, `user`, `password`
- SQLite: requires `path` to database file

**Show available databases:**
```bash
# Find and use credentials file
CREDS_FILE="${CREDS_FILE:-.claude/data-analyze/credentials.json}"
[ -f "./$CREDS_FILE" ] && CREDS_FILE="./$CREDS_FILE" || CREDS_FILE="$HOME/$CREDS_FILE"

jq -r '.databases[].name' "$CREDS_FILE"
jq -r '.databases[] | "\(.name): \(.type)"' "$CREDS_FILE"
```

### Security Best Practices

1. **Never commit credentials** - `.claude/` is typically gitignored
2. **Use read-only accounts** - Grant minimal permissions for analytics queries
3. **Credential file locations**:
   - Project: `./.claude/data-analyze/credentials.json`
   - User: `~/.claude/data-analyze/credentials.json`
4. **File permissions** - Restrict access: `chmod 600 ~/.claude/data-analyze/credentials.json`
5. **Reference by name only** - Scripts read credentials automatically, just use `--name`

### Usage Patterns

**Single database:**
```bash
# Scripts find credentials automatically (Project → User)
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/schema_explorer.py --name kolverse --list-tables
```

**Multiple databases (federated query):**
```bash
# Reference multiple databases by name (comma-separated)
python ${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts/federated_query.py \
  --names kolverse,analytics_db \
  --query "SELECT * FROM kolverse.users u JOIN analytics_db.metrics m ON u.id = m.user_id"
```

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

## Troubleshooting

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
- **`.claude/data-analyze/credentials.json`** - Your database credentials (Project or User scope)
- **`${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/credentials.example.json`** - Template for credentials file

### References
- **references/extensions.md** - DuckDB extension documentation
- **references/connection_examples.md** - Connection string examples and patterns
- **references/query_patterns.md** - Common query patterns and optimizations
