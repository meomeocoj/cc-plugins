---
name: setup
description: Check data-analyze plugin requirements (DuckDB, credentials)
allowed-tools:
  - Bash
  - Read
---

# Setup Check Command

Check if data-analyze plugin requirements are met.

## Steps

### 1. Check DuckDB Installation

```bash
# Check if duckdb is installed
if command -v duckdb &> /dev/null; then
    version=$(duckdb --version 2>&1 | head -1)
    echo "✅ DuckDB: installed ($version)"
else
    echo "❌ DuckDB: not installed"
    echo ""
    echo "Install DuckDB:"
    echo "  macOS: brew install duckdb"
    echo "  Linux: https://duckdb.org/docs/installation/"
fi
```

### 2. Check Credentials File

Search for credentials file in these locations (in order):
1. `./.claude/data-analyze/credentials.json` (project scope)
2. `~/.claude/data-analyze/credentials.json` (user scope)

```bash
# Check credential locations
project_creds="./.claude/data-analyze/credentials.json"
user_creds="$HOME/.claude/data-analyze/credentials.json"

if [ -f "$project_creds" ]; then
    echo "✅ Credentials: found at $project_creds (project)"
    creds_file="$project_creds"
elif [ -f "$user_creds" ]; then
    echo "✅ Credentials: found at $user_creds (user)"
    creds_file="$user_creds"
else
    echo "❌ Credentials: not found"
    echo ""
    echo "Searched locations:"
    echo "  1. $project_creds (project)"
    echo "  2. $user_creds (user)"
    echo ""
    echo "To create credentials:"
    echo "  mkdir -p ~/.claude/data-analyze"
    echo "  # Copy the example template from plugin and edit with your database details"
fi
```

### 3. Validate Credentials Structure (if found)

If credentials file is found, validate the JSON structure:

```bash
# Validate credentials using Python
python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/unified-sql/scripts')
from credential_manager import find_credentials_file, validate_credentials_file

creds_file = find_credentials_file()
if creds_file:
    print(f'\nValidating credentials structure...')
    results = validate_credentials_file(creds_file)
    valid_count = sum(1 for r in results if r['valid'])
    total_count = len(results)

    for r in results:
        if r['valid']:
            print(f\"  ✅ {r['name']} ({r['type']}) - valid\")
        else:
            print(f\"  ❌ {r['name']} ({r['type']}) - {r['error']}\")

    print(f'\n{valid_count}/{total_count} databases configured correctly')
"
```

## Output Format

Present results clearly:
- Use ✅ for passing checks
- Use ❌ for failing checks
- Provide actionable next steps for any failures
