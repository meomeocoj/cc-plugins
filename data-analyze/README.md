# data-analyze

Federated data analysis plugin using DuckDB to query across PostgreSQL, MySQL, and SQLite databases.

## Features

- **Cross-database queries**: Join tables across different database systems
- **Schema exploration**: List tables, describe columns, sample data
- **Flexible credentials**: Project or user-scoped credential files
- **Credential protection**: Hook prevents credential files from being read by LLM
- **Multiple output formats**: Table, JSON, CSV, Markdown

## Prerequisites

- Python 3.8+
- DuckDB (`pip install duckdb`)

## Quick Start

Run the setup command to check requirements:

```
/data-analyze:setup
```

## Setup

### 1. Create Credentials File

Credentials are stored in `.claude/data-analyze/credentials.json` at either:
- **Project scope**: `./.claude/data-analyze/credentials.json`
- **User scope**: `~/.claude/data-analyze/credentials.json`

```bash
# Create user-scoped credentials
mkdir -p ~/.claude/data-analyze
cp skills/unified-sql/credentials.example.json \
   ~/.claude/data-analyze/credentials.json
```

### 2. Edit Credentials

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

### 3. Secure the File

```bash
chmod 600 ~/.claude/data-analyze/credentials.json
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
├── commands/
│   └── setup.md              # /setup command
├── hooks/
│   ├── hooks.json            # Hook configuration
│   └── block-credentials.sh  # Blocks credential file reads
└── skills/unified-sql/
    ├── SKILL.md
    ├── credentials.example.json
    ├── .gitignore
    ├── scripts/
    │   ├── federated_query.py
    │   ├── schema_explorer.py
    │   └── credential_manager.py
    └── references/
        ├── extensions.md
        └── query_patterns.md
```

## Credential Search Order

The plugin searches for credentials in this order:
1. `./.claude/data-analyze/credentials.json` (project)
2. `~/.claude/data-analyze/credentials.json` (user)

Project credentials take priority, allowing project-specific database configurations.

## Security

- **Credential protection**: PreToolUse hook blocks LLM from reading credential files
- **Gitignored**: Credentials stored in `.claude/` which is typically gitignored
- **Read-only**: Use read-only database accounts for analytics
- **Name-based**: Credentials referenced by name, passwords never in queries

## License

MIT
