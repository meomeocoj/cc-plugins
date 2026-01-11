# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugins repository containing custom plugins. Plugins are organized under `plugins/` with a root marketplace.json for distribution.

## Structure

```
.claude-plugin/marketplace.json   # Plugin registry (version, metadata)
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    # Plugin manifest
    commands/                     # Slash commands (markdown with YAML frontmatter)
    hooks/                        # Event hooks (hooks.json + scripts)
    skills/                       # AI-invoked skills (SKILL.md + scripts)
```

## Plugin Development Patterns

### Plugin Manifest (plugin.json)
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "...",
  "keywords": ["..."]
}
```

### Commands
- Markdown files with YAML frontmatter
- Define `allowed-tools` for security
- Located in `commands/` directory

### Skills
- SKILL.md with frontmatter containing `name` and `description`
- Description contains trigger keywords for AI invocation
- Use `${CLAUDE_PLUGIN_ROOT}` for script paths

### Hooks
- hooks.json maps events (PreToolUse, PostToolUse, etc.) to scripts
- Use `${CLAUDE_PLUGIN_ROOT}` in command paths
- Common pattern: block sensitive file reads

## Current Plugins

### data-analyze
Federated SQL queries across PostgreSQL, MySQL, and SQLite via DuckDB.

**Prerequisites:** Python 3.8+, DuckDB (`pip install duckdb`)

**Key scripts:**
```bash
# Schema exploration
python plugins/data-analyze/skills/unified-sql/scripts/schema_explorer.py --name DB_NAME --list-tables
python plugins/data-analyze/skills/unified-sql/scripts/schema_explorer.py --name DB_NAME --describe TABLE

# Query execution
python plugins/data-analyze/skills/unified-sql/scripts/federated_query.py --name DB_NAME --query "SELECT ..."
python plugins/data-analyze/skills/unified-sql/scripts/federated_query.py --names DB1,DB2 --query "SELECT ... JOIN ..."
```

**Credentials:** `.claude/data-analyze/credentials.json` (project or user scope)

## Security Patterns

- PreToolUse hooks block credential file reads from LLM
- SQL injection protection: identifier validation, dangerous keyword blocking
- Read-only mode by default (`--allow-writes` to override)
- Error messages sanitize passwords/connection details
