#!/usr/bin/env python3
"""
Credential Manager for DuckDB Federated Query

Manages database credentials from database-credentials.json file.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def get_search_paths() -> List[Path]:
    """Get list of paths to search for credentials file."""
    return [
        Path.cwd() / ".claude" / "data-analyze" / "credentials.json",  # Project
        Path.home() / ".claude" / "data-analyze" / "credentials.json",  # User
    ]


def find_credentials_file() -> Optional[Path]:
    """
    Search for credentials file in priority order.

    Returns:
        Path to credentials file if found, None otherwise
    """
    for path in get_search_paths():
        if path.exists():
            return path
    return None


class DatabaseCredential:
    """Represents a single database credential."""

    def __init__(self, config: Dict):
        self.name = config["name"]
        self.type = config["type"].lower()
        self.config = config

        # Validate required fields based on database type
        if self.type == "sqlite":
            if "path" not in config:
                raise ValueError(f"SQLite credential '{self.name}' missing 'path' field")
        else:
            required = ["host", "database", "user", "password"]
            missing = [f for f in required if f not in config]
            if missing:
                raise ValueError(f"Credential '{self.name}' missing required fields: {missing}")

    def get_connection_string(self) -> str:
        """Generate connection string for this credential."""
        if self.type == "postgres":
            host = self.config["host"]
            port = self.config.get("port", 5432)
            database = self.config["database"]
            user = self.config["user"]
            password = self.config["password"]
            return f"host={host} port={port} dbname={database} user={user} password={password}"

        elif self.type == "mysql":
            host = self.config["host"]
            port = self.config.get("port", 3306)
            database = self.config["database"]
            user = self.config["user"]
            password = self.config["password"]
            return f"host={host} port={port} database={database} user={user} password={password}"

        elif self.type == "sqlite":
            return self.config["path"]

        else:
            raise ValueError(f"Unsupported database type: {self.type}")

    def __repr__(self):
        return f"<DatabaseCredential name='{self.name}' type='{self.type}'>"


class CredentialManager:
    """Manages database credentials from JSON file."""

    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize credential manager.

        Args:
            credentials_file: Path to credentials JSON file.
                            If None, searches in priority order:
                            1. ./.claude/data-analyze/credentials.json (project)
                            2. ~/.claude/data-analyze/credentials.json (user)
        """
        if credentials_file is None:
            credentials_file = find_credentials_file()

        self.credentials_file = Path(credentials_file) if credentials_file else None
        self.credentials: Dict[str, DatabaseCredential] = {}

        if self.credentials_file and self.credentials_file.exists():
            self._load_credentials()

    def _load_credentials(self):
        """Load credentials from JSON file."""
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)

            if "databases" not in data:
                raise ValueError("Credentials file must contain 'databases' array")

            for db_config in data["databases"]:
                cred = DatabaseCredential(db_config)
                self.credentials[cred.name] = cred

            print(f"✅ Loaded {len(self.credentials)} database credential(s)")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in credentials file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading credentials: {e}")

    def get(self, name: str) -> DatabaseCredential:
        """
        Get credential by name.

        Args:
            name: Credential name

        Returns:
            DatabaseCredential object

        Raises:
            KeyError: If credential not found
        """
        if name not in self.credentials:
            available = ", ".join(self.credentials.keys())
            raise KeyError(
                f"Credential '{name}' not found. "
                f"Available: {available or 'none'}"
            )
        return self.credentials[name]

    def get_multiple(self, names: List[str]) -> List[DatabaseCredential]:
        """
        Get multiple credentials by names.

        Args:
            names: List of credential names

        Returns:
            List of DatabaseCredential objects
        """
        return [self.get(name) for name in names]

    def list_credentials(self) -> List[str]:
        """Get list of available credential names."""
        return list(self.credentials.keys())

    def has_credentials(self) -> bool:
        """Check if any credentials are loaded."""
        return len(self.credentials) > 0


def parse_credential_names(names_arg: Optional[str]) -> List[str]:
    """
    Parse comma-separated credential names.

    Args:
        names_arg: Comma-separated credential names or None

    Returns:
        List of credential names
    """
    if not names_arg:
        return []
    return [name.strip() for name in names_arg.split(",") if name.strip()]


def validate_credential_config(config: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate a credential configuration without raising exceptions.

    Args:
        config: Database configuration dict

    Returns:
        Tuple of (is_valid, error_message)
    """
    if "name" not in config:
        return False, "missing 'name' field"
    if "type" not in config:
        return False, "missing 'type' field"

    db_type = config["type"].lower()

    if db_type == "sqlite":
        if "path" not in config:
            return False, "missing 'path' field"
    elif db_type in ("postgres", "mysql"):
        required = ["host", "database", "user", "password"]
        missing = [f for f in required if f not in config]
        if missing:
            return False, f"missing fields: {', '.join(missing)}"
    else:
        return False, f"unsupported type '{db_type}'"

    return True, None


def validate_credentials_file(file_path: Path) -> List[Dict]:
    """
    Validate credentials file and return validation results.

    Args:
        file_path: Path to credentials file

    Returns:
        List of dicts with 'name', 'type', 'valid', 'error' keys
    """
    results = []

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [{"name": "file", "type": "json", "valid": False, "error": f"Invalid JSON: {e}"}]
    except Exception as e:
        return [{"name": "file", "type": "file", "valid": False, "error": str(e)}]

    if "databases" not in data:
        return [{"name": "file", "type": "structure", "valid": False, "error": "missing 'databases' array"}]

    for config in data["databases"]:
        name = config.get("name", "unnamed")
        db_type = config.get("type", "unknown")
        valid, error = validate_credential_config(config)
        results.append({
            "name": name,
            "type": db_type,
            "valid": valid,
            "error": error
        })

    return results
