#!/usr/bin/env python3
"""
DuckDB Federated Query Tool

Execute SQL queries across multiple database systems using DuckDB as a query engine.
Supports PostgreSQL, MySQL, SQLite, and cross-database joins.

Usage (with credentials file):
    python federated_query.py --name prod_db --query "SELECT * FROM prod_db.users LIMIT 10"
    python federated_query.py --names prod_db,sales_db --query "SELECT u.email FROM prod_db.users u JOIN sales_db.orders o ON u.id = o.user_id"

Usage (direct connection):
    python federated_query.py --query "SELECT * FROM postgres_table LIMIT 10" --postgres "host=localhost dbname=mydb"
    python federated_query.py --query "SELECT * FROM mysql_db.users JOIN postgres_db.orders ON users.id = orders.user_id" --mysql "host=localhost database=mydb" --postgres "host=localhost dbname=pgdb"
"""

import argparse
import sys
import duckdb
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from credential_manager import CredentialManager, parse_credential_names


def setup_postgres_connection(con: duckdb.DuckDBPyConnection, connection_string: str, alias: str = "postgres_db"):
    """Attach PostgreSQL database to DuckDB connection."""
    con.execute("INSTALL postgres")
    con.execute("LOAD postgres")
    con.execute(f"ATTACH '{connection_string}' AS {alias} (TYPE POSTGRES)")
    print(f"✅ Connected to PostgreSQL as '{alias}'")


def setup_mysql_connection(con: duckdb.DuckDBPyConnection, connection_string: str, alias: str = "mysql_db"):
    """Attach MySQL database to DuckDB connection."""
    con.execute("INSTALL mysql")
    con.execute("LOAD mysql")
    con.execute(f"ATTACH '{connection_string}' AS {alias} (TYPE MYSQL)")
    print(f"✅ Connected to MySQL as '{alias}'")


def setup_sqlite_connection(con: duckdb.DuckDBPyConnection, db_path: str, alias: str = "sqlite_db"):
    """Attach SQLite database to DuckDB connection."""
    con.execute(f"ATTACH '{db_path}' AS {alias} (TYPE SQLITE)")
    print(f"✅ Connected to SQLite as '{alias}'")


def setup_credential_connection(con: duckdb.DuckDBPyConnection, cred_manager: CredentialManager, cred_name: str):
    """Setup connection using credential from credentials file."""
    cred = cred_manager.get(cred_name)
    connection_string = cred.get_connection_string()
    alias = cred_name  # Use credential name as alias

    if cred.type == "postgres":
        setup_postgres_connection(con, connection_string, alias)
    elif cred.type == "mysql":
        setup_mysql_connection(con, connection_string, alias)
    elif cred.type == "sqlite":
        setup_sqlite_connection(con, connection_string, alias)
    else:
        raise ValueError(f"Unsupported database type: {cred.type}")


def execute_query(
    query: str,
    credential_names: Optional[List[str]] = None,
    postgres_conn: Optional[str] = None,
    mysql_conn: Optional[str] = None,
    sqlite_path: Optional[str] = None,
    format: str = "table"
):
    """
    Execute a federated query across multiple databases.

    Args:
        query: SQL query to execute
        credential_names: List of credential names to load from credentials file
        postgres_conn: PostgreSQL connection string (direct connection)
        mysql_conn: MySQL connection string (direct connection)
        sqlite_path: Path to SQLite database file (direct connection)
        format: Output format ('table', 'json', 'csv', 'markdown')
    """
    con = duckdb.connect(database=':memory:')

    try:
        # Setup connections from credentials file
        if credential_names:
            cred_manager = CredentialManager()
            if not cred_manager.has_credentials():
                print("❌ No credentials file found. Create database-credentials.json", file=sys.stderr)
                print("   See database-credentials.example.json for template", file=sys.stderr)
                sys.exit(1)

            print(f"🔐 Loading {len(credential_names)} credential(s)...")
            for cred_name in credential_names:
                setup_credential_connection(con, cred_manager, cred_name)

        # Setup direct connections (fallback)
        if postgres_conn:
            setup_postgres_connection(con, postgres_conn)

        if mysql_conn:
            setup_mysql_connection(con, mysql_conn)

        if sqlite_path:
            setup_sqlite_connection(con, sqlite_path)

        # Execute query
        print(f"\n🔍 Executing query:\n{query}\n")
        result = con.execute(query)

        # Format output
        if format == "table":
            print(result.df())
        elif format == "json":
            print(result.df().to_json(orient="records", indent=2))
        elif format == "csv":
            print(result.df().to_csv(index=False))
        elif format == "markdown":
            print(result.df().to_markdown(index=False))
        else:
            print(result.fetchall())

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(
        description="Execute federated queries across multiple databases using DuckDB"
    )

    parser.add_argument("--query", "-q", required=True, help="SQL query to execute")

    # Credential-based connections (preferred)
    parser.add_argument("--name", help="Single database credential name from database-credentials.json")
    parser.add_argument("--names", help="Comma-separated database credential names (e.g., 'db1,db2,db3')")

    # Direct connection options (fallback)
    parser.add_argument("--postgres", "-p", help="PostgreSQL connection string")
    parser.add_argument("--mysql", "-m", help="MySQL connection string")
    parser.add_argument("--sqlite", "-s", help="SQLite database file path")

    parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "csv", "markdown"],
        default="table",
        help="Output format"
    )

    args = parser.parse_args()

    # Parse credential names
    credential_names = []
    if args.name:
        credential_names.append(args.name)
    if args.names:
        credential_names.extend(parse_credential_names(args.names))

    # Check that at least one connection method is specified
    has_credentials = len(credential_names) > 0
    has_direct = any([args.postgres, args.mysql, args.sqlite])

    if not has_credentials and not has_direct:
        print("❌ Error: At least one database connection must be specified", file=sys.stderr)
        print("   Use --name, --names, or direct connections (--postgres/--mysql/--sqlite)", file=sys.stderr)
        sys.exit(1)

    execute_query(
        query=args.query,
        credential_names=credential_names if credential_names else None,
        postgres_conn=args.postgres,
        mysql_conn=args.mysql,
        sqlite_path=args.sqlite,
        format=args.format
    )


if __name__ == "__main__":
    main()
