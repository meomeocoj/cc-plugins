#!/usr/bin/env python3
"""
DuckDB Schema Explorer

Explore database schemas, tables, columns, and data types across multiple database systems.

Usage (with credentials file):
    python schema_explorer.py --name prod_db --list-tables
    python schema_explorer.py --name prod_db --describe users
    python schema_explorer.py --name prod_db --sample users --limit 5

Usage (direct connection):
    python schema_explorer.py --postgres "host=localhost dbname=mydb" --list-tables
    python schema_explorer.py --postgres "host=localhost dbname=mydb" --describe users
    python schema_explorer.py --postgres "host=localhost dbname=mydb" --sample users --limit 5
"""

import argparse
import re
import sys
import duckdb
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from credential_manager import CredentialManager


# Valid identifier pattern (alphanumeric, underscore, dots for schema.table)
VALID_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$')


def validate_identifier(name: str, identifier_type: str = "identifier") -> str:
    """
    Validate SQL identifier to prevent SQL injection.

    Args:
        name: The identifier to validate
        identifier_type: Type of identifier for error messages (e.g., "table", "schema")

    Returns:
        The validated identifier

    Raises:
        ValueError: If the identifier contains invalid characters
    """
    if not name:
        raise ValueError(f"Empty {identifier_type} name")

    if not VALID_IDENTIFIER_PATTERN.match(name):
        raise ValueError(
            f"Invalid {identifier_type} name '{name}'. "
            f"Only alphanumeric characters and underscores are allowed."
        )

    # Check for SQL keywords that could be dangerous
    dangerous_keywords = {'DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE'}
    if name.upper() in dangerous_keywords:
        raise ValueError(f"Reserved keyword '{name}' cannot be used as {identifier_type} name")

    return name


def sanitize_error_message(error: Exception) -> str:
    """Sanitize error messages to prevent credential leakage."""
    error_msg = str(error)
    # Remove potential passwords from error messages
    error_msg = re.sub(r'password=[^\s&]+', 'password=***', error_msg, flags=re.IGNORECASE)
    error_msg = re.sub(r'pwd=[^\s&]+', 'pwd=***', error_msg, flags=re.IGNORECASE)
    # Remove potential connection strings
    error_msg = re.sub(r'host=[^\s]+\s+.*?password=[^\s]+', '[connection details redacted]', error_msg, flags=re.IGNORECASE)
    return error_msg


def setup_connection(con: duckdb.DuckDBPyConnection, db_type: str, connection_string: str, alias: str = "db"):
    """Setup database connection based on type."""
    alias = validate_identifier(alias, "alias")
    if db_type == "postgres":
        con.execute("INSTALL postgres")
        con.execute("LOAD postgres")
        con.execute(f"ATTACH '{connection_string}' AS {alias} (TYPE POSTGRES)")
    elif db_type == "mysql":
        con.execute("INSTALL mysql")
        con.execute("LOAD mysql")
        con.execute(f"ATTACH '{connection_string}' AS {alias} (TYPE MYSQL)")
    elif db_type == "sqlite":
        con.execute(f"ATTACH '{connection_string}' AS {alias} (TYPE SQLITE)")

    print(f"✅ Connected to {db_type.upper()} as '{alias}'\n")


def list_tables(con: duckdb.DuckDBPyConnection, schema: str = "db"):
    """List all tables in the attached database."""
    schema = validate_identifier(schema, "schema")
    print("📋 Available tables:\n")
    result = con.execute(f"SHOW TABLES FROM {schema}").fetchall()
    for table in result:
        print(f"  • {table[0]}")
    print()


def describe_table(con: duckdb.DuckDBPyConnection, table_name: str, schema: str = "db"):
    """Describe table schema (columns, types, nullability)."""
    schema = validate_identifier(schema, "schema")
    table_name = validate_identifier(table_name, "table")
    print(f"📊 Schema for table '{table_name}':\n")
    result = con.execute(f"DESCRIBE {schema}.{table_name}").df()
    print(result.to_markdown(index=False))
    print()


def sample_data(con: duckdb.DuckDBPyConnection, table_name: str, schema: str = "db", limit: int = 5):
    """Show sample rows from a table."""
    schema = validate_identifier(schema, "schema")
    table_name = validate_identifier(table_name, "table")
    # Validate limit is a positive integer
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer")
    limit = min(limit, 10000)  # Cap at 10000 for safety
    print(f"🔍 Sample data from '{table_name}' (limit {limit}):\n")
    result = con.execute(f"SELECT * FROM {schema}.{table_name} LIMIT {limit}").df()
    print(result.to_markdown(index=False))
    print()


def table_stats(con: duckdb.DuckDBPyConnection, table_name: str, schema: str = "db"):
    """Show table statistics (row count, size)."""
    schema = validate_identifier(schema, "schema")
    table_name = validate_identifier(table_name, "table")
    print(f"📈 Statistics for table '{table_name}':\n")

    # Row count
    count = con.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}").fetchone()[0]
    print(f"  Total rows: {count:,}")

    # Column statistics
    result = con.execute(f"DESCRIBE {schema}.{table_name}").fetchall()
    print(f"  Total columns: {len(result)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Explore database schemas using DuckDB"
    )

    # Credential-based connection (preferred)
    parser.add_argument("--name", "-n", help="Database credential name from credentials.json")

    # Direct connection options (fallback)
    db_group = parser.add_mutually_exclusive_group()
    db_group.add_argument("--postgres", "-p", help="PostgreSQL connection string")
    db_group.add_argument("--mysql", "-m", help="MySQL connection string")
    db_group.add_argument("--sqlite", "-s", help="SQLite database file path")

    # Operation options
    parser.add_argument("--list-tables", "-l", action="store_true", help="List all tables")
    parser.add_argument("--describe", "-d", metavar="TABLE", help="Describe table schema")
    parser.add_argument("--sample", metavar="TABLE", help="Show sample data from table")
    parser.add_argument("--stats", metavar="TABLE", help="Show table statistics")
    parser.add_argument("--limit", type=int, default=5, help="Sample data limit (default: 5)")

    args = parser.parse_args()

    # Determine database connection method
    db_type = None
    connection_string = None
    alias = "db"

    if args.name:
        # Load from credentials file
        try:
            cred_manager = CredentialManager()
            if not cred_manager.has_credentials():
                print("❌ No credentials file found. Create .claude/data-analyze/credentials.json", file=sys.stderr)
                print("   See credentials.example.json for template", file=sys.stderr)
                sys.exit(1)

            cred = cred_manager.get(args.name)
            db_type = cred.type
            connection_string = cred.get_connection_string()
            alias = args.name  # Use credential name as alias
            print(f"🔐 Using credential: {args.name}")

        except Exception as e:
            print(f"❌ Error loading credential: {sanitize_error_message(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.postgres:
        db_type = "postgres"
        connection_string = args.postgres
    elif args.mysql:
        db_type = "mysql"
        connection_string = args.mysql
    elif args.sqlite:
        db_type = "sqlite"
        connection_string = args.sqlite
    else:
        print("❌ Error: Either --name or a direct connection (--postgres/--mysql/--sqlite) must be specified", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Create connection
    con = duckdb.connect(database=':memory:')

    try:
        setup_connection(con, db_type, connection_string, alias)

        # Execute requested operations
        if args.list_tables:
            list_tables(con, alias)

        if args.describe:
            describe_table(con, args.describe, alias)

        if args.sample:
            sample_data(con, args.sample, alias, args.limit)

        if args.stats:
            table_stats(con, args.stats, alias)

        if not any([args.list_tables, args.describe, args.sample, args.stats]):
            print("⚠️  No operation specified. Use --list-tables, --describe, --sample, or --stats")
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {sanitize_error_message(e)}", file=sys.stderr)
        sys.exit(1)

    finally:
        con.close()


if __name__ == "__main__":
    main()
