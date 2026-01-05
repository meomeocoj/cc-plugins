# data-analyze

Federated data analysis plugin using DuckDB to query across PostgreSQL, MySQL, and SQLite databases.

## Features

- **Cross-database queries**: Join tables across different database systems
- **Schema exploration**: List tables, describe columns, sample data
- **Credential management**: Secure, gitignored credential storage
- **Multiple output formats**: Table, JSON, CSV, Markdown

## Prerequisites

- Python 3.8+
- DuckDB (`pip install duckdb`)

## Setup

1. Copy the credentials template:
   ```bash
   cp skills/duckdb-federated-query/database-credentials.example.json \
      skills/duckdb-federated-query/database-credentials.json
   ```

2. Edit `database-credentials.json` with your database connections:
   ```json
   {
     "databases": [
       {
         "name": "prod_db",
         "type": "postgres",
         "host": "localhost",
         "port": 5432,
         "database": "mydb",
         "user": "user",
         "password": "secret"
       }
     ]
   }
   ```

3. Secure the file:
   ```bash
   chmod 600 skills/duckdb-federated-query/database-credentials.json
   ```

## Usage

### Schema Exploration

```bash
# List tables
python scripts/schema_explorer.py --name prod_db --list-tables

# Describe table structure
python scripts/schema_explorer.py --name prod_db --describe users

# Sample data
python scripts/schema_explorer.py --name prod_db --sample orders --limit 10
```

### Query Execution

```bash
# Single database query
python scripts/federated_query.py --name prod_db \
  --query "SELECT * FROM prod_db.users LIMIT 10"

# Cross-database join
python scripts/federated_query.py --names prod_db,sales_db \
  --query "SELECT u.email, o.total
           FROM prod_db.users u
           JOIN sales_db.orders o ON u.id = o.user_id"

# Export to JSON
python scripts/federated_query.py --name prod_db \
  --query "SELECT * FROM prod_db.analytics" --format json
```

## Structure

```
data-analyze/
├── .claude-plugin/plugin.json
├── README.md
└── skills/duckdb-federated-query/
    ├── SKILL.md
    ├── database-credentials.example.json
    ├── .gitignore
    ├── scripts/
    │   ├── federated_query.py
    │   ├── schema_explorer.py
    │   └── credential_manager.py
    └── references/
        ├── extensions.md
        └── query_patterns.md
```

## Security

- `database-credentials.json` is gitignored
- Use read-only database accounts for analytics
- Credentials referenced by name, never exposed in queries

## License

MIT
