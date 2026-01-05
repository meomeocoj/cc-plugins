---
name: data-analyze:help
description: Show data-analyze plugin help and available commands
allowed-tools: []
---

# Data Analyze Plugin Help

Display help information for the data-analyze plugin.

## Output

```
data-analyze - Federated SQL queries across PostgreSQL, MySQL, SQLite

COMMANDS
  /data-analyze:setup    Check requirements (DuckDB, credentials)
  /data-analyze:help     Show this help message

CREDENTIALS
  Credentials are stored in .claude/data-analyze/credentials.json

  Search order:
    1. ./.claude/data-analyze/credentials.json (project)
    2. ~/.claude/data-analyze/credentials.json (user)

SKILL
  The unified-sql skill activates when you mention:
  - database, query, SQL, table, schema
  - "check the data", "what's in the table"
  - PostgreSQL, MySQL, SQLite
  - cross-database joins

QUICK START
  1. Run /data-analyze:setup to check requirements
  2. Create credentials file in ~/.claude/data-analyze/credentials.json
  3. Ask: "Show me tables in prod_db" or "Query users from my database"

SECURITY
  - Credential files are protected from being read by LLM
  - Use read-only database accounts
  - Credentials referenced by name only
```
