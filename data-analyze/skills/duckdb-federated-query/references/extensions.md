# DuckDB Extensions Reference

This document describes the core DuckDB extensions for federated database access.

## Core Extensions

### PostgreSQL Extension

```sql
INSTALL postgres;
LOAD postgres;
ATTACH 'host=localhost user=postgres password=secret dbname=mydb' AS pg (TYPE POSTGRES);
```

**Features:**
- Full read access to PostgreSQL tables
- Support for all PostgreSQL data types
- Direct query pushdown for optimal performance
- Transaction support

**Connection string format:**
```
host=<host> port=<port> dbname=<database> user=<user> password=<password>
```

### MySQL Extension

```sql
INSTALL mysql;
LOAD mysql;
ATTACH 'host=localhost user=root password=secret database=mydb' AS mysql (TYPE MYSQL);
```

**Features:**
- Read access to MySQL/MariaDB tables
- Support for common MySQL data types
- Query pushdown for filtering and aggregation

**Connection string format:**
```
host=<host> port=<port> database=<database> user=<user> password=<password>
```

### SQLite Extension

```sql
ATTACH 'path/to/database.db' AS sqlite (TYPE SQLITE);
```

**Features:**
- Direct file-based access
- Full read/write support
- No external dependencies
- Excellent for local data files

## Extension Management

### Install Extension
```sql
INSTALL extension_name;
```

### Load Extension
```sql
LOAD extension_name;
```

### List Installed Extensions
```sql
SELECT * FROM duckdb_extensions();
```

## Other Useful Extensions

### httpfs (HTTP/S3 Access)
```sql
INSTALL httpfs;
LOAD httpfs;
-- Query remote Parquet files
SELECT * FROM 'https://example.com/data.parquet';
```

### parquet (Parquet Files)
```sql
-- Read Parquet files
SELECT * FROM 'data.parquet';
-- Write Parquet files
COPY (SELECT * FROM table) TO 'output.parquet';
```

### json (JSON Files)
```sql
-- Read JSON files
SELECT * FROM 'data.json';
-- Read NDJSON
SELECT * FROM read_ndjson_auto('data.ndjson');
```

### icu (Internationalization)
```sql
INSTALL icu;
LOAD icu;
-- Advanced string collation and sorting
```

## Best Practices

1. **Load extensions once per connection** - Extensions persist for the connection lifetime
2. **Use ATTACH for database connections** - Attach gives you a named reference to query
3. **Alias databases descriptively** - Use meaningful names like `prod_db`, `analytics_db`
4. **Install extensions in-memory** - DuckDB handles extension management automatically
5. **Test connection strings first** - Verify connectivity before complex queries
