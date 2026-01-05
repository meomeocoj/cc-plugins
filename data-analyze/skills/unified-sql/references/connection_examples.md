# Connection Examples Reference

This document provides connection string examples for different database systems.

## PostgreSQL

### Basic Connection
```json
{
  "name": "my_postgres",
  "type": "postgres",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "postgres",
  "password": "secret"
}
```

### Remote Connection
```json
{
  "name": "prod_postgres",
  "type": "postgres",
  "host": "db.example.com",
  "port": 5432,
  "database": "production",
  "user": "readonly_user",
  "password": "secure_password"
}
```

### Connection String Format
```
host=<host> port=<port> dbname=<database> user=<user> password=<password>
```

## MySQL

### Basic Connection
```json
{
  "name": "my_mysql",
  "type": "mysql",
  "host": "localhost",
  "port": 3306,
  "database": "mydb",
  "user": "root",
  "password": "secret"
}
```

### Remote Connection
```json
{
  "name": "analytics_mysql",
  "type": "mysql",
  "host": "mysql.example.com",
  "port": 3306,
  "database": "analytics",
  "user": "analyst",
  "password": "secure_password"
}
```

### Connection String Format
```
host=<host> port=<port> database=<database> user=<user> password=<password>
```

## SQLite

### Local File
```json
{
  "name": "local_data",
  "type": "sqlite",
  "path": "/path/to/database.db"
}
```

### Relative Path
```json
{
  "name": "project_db",
  "type": "sqlite",
  "path": "./data/local.db"
}
```

## Multiple Databases

### Federated Setup Example
```json
{
  "databases": [
    {
      "name": "users_db",
      "type": "postgres",
      "host": "postgres.example.com",
      "port": 5432,
      "database": "users",
      "user": "readonly",
      "password": "secret1"
    },
    {
      "name": "orders_db",
      "type": "mysql",
      "host": "mysql.example.com",
      "port": 3306,
      "database": "orders",
      "user": "readonly",
      "password": "secret2"
    },
    {
      "name": "cache_db",
      "type": "sqlite",
      "path": "./cache/local.db"
    }
  ]
}
```

### Cross-Database Query
```sql
-- With above credentials, query across all three databases
SELECT
    u.email,
    o.order_id,
    c.cache_key
FROM users_db.users u
JOIN orders_db.orders o ON u.id = o.user_id
LEFT JOIN cache_db.user_cache c ON u.id = c.user_id
```

## Common Connection Issues

### PostgreSQL
- **Connection refused**: Check if PostgreSQL is running and accepting connections
- **Authentication failed**: Verify username/password and pg_hba.conf settings
- **Database not found**: Confirm database name exists

### MySQL
- **Access denied**: Check user privileges and host whitelist
- **Unknown database**: Verify database name
- **Connection timeout**: Check firewall and network settings

### SQLite
- **File not found**: Verify file path is correct and accessible
- **Permission denied**: Check file read permissions
- **Database locked**: Close other connections to the file

## Best Practices

1. **Use read-only accounts**: Create dedicated analytics users with SELECT-only privileges
2. **Use descriptive names**: Name credentials after their purpose (e.g., `analytics_prod`, `reporting_db`)
3. **Secure credentials**: Set file permissions to 600 on credentials.json
4. **Test connections**: Verify connectivity before running complex queries
5. **Document databases**: Keep notes on what each database contains
