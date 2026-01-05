#!/usr/bin/env python3
"""
Credential Manager for DuckDB Federated Query

Manages database credentials from database-credentials.json file.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


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
                            If None, looks for database-credentials.json in skill directory.
        """
        if credentials_file is None:
            # Default to skill directory
            skill_dir = Path(__file__).parent.parent
            credentials_file = skill_dir / "database-credentials.json"

        self.credentials_file = Path(credentials_file)
        self.credentials: Dict[str, DatabaseCredential] = {}

        if self.credentials_file.exists():
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
