---
name: analyze
description: Analyze data files (CSV, JSON) using DuckDB SQL for statistics, quality checks, and patterns
allowed-tools:
  - Read
  - Bash
  - Write
  - Glob
  - Grep
argument-hint: "<file_path> [analysis_type]"
---

# Data Analysis Command

Perform comprehensive data analysis on the specified file using DuckDB SQL.

## Arguments

- `file_path`: Path to the data file (CSV, JSON, or Parquet)
- `analysis_type` (optional): Type of analysis - `full` (default), `profile`, `quality`, `stats`

## Analysis Workflow

### 1. Validate Input

First, verify the file exists and determine its format:
- Check file extension (.csv, .json, .jsonl, .parquet)
- Verify DuckDB is available: `which duckdb`
- If DuckDB not found, inform user to install it

### 2. Data Profiling

Run initial profiling to understand the data:

```bash
duckdb -c "DESCRIBE SELECT * FROM 'FILE_PATH';"
duckdb -c "SELECT COUNT(*) as total_rows FROM 'FILE_PATH';"
duckdb -c "SELECT * FROM 'FILE_PATH' LIMIT 5;"
```

### 3. Statistical Analysis

For numeric columns identified in profiling:

```sql
SELECT
    AVG(column) as mean,
    MEDIAN(column) as median,
    STDDEV(column) as std_dev,
    MIN(column) as min_val,
    MAX(column) as max_val,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY column) as p25,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY column) as p75
FROM 'FILE_PATH';
```

### 4. Data Quality Checks

Check for common data quality issues:

```sql
-- Missing values per column
SELECT COUNT(*) - COUNT(column) as missing FROM 'FILE_PATH';

-- Duplicate rows
SELECT *, COUNT(*) FROM 'FILE_PATH' GROUP BY ALL HAVING COUNT(*) > 1;

-- Outliers using IQR
WITH stats AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY val) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY val) as q3
    FROM 'FILE_PATH'
)
SELECT COUNT(*) as outliers
FROM 'FILE_PATH', stats
WHERE val < q1 - 1.5*(q3-q1) OR val > q3 + 1.5*(q3-q1);
```

### 5. Pattern Detection

Look for patterns based on data types:

- **Time series**: Trends over date columns
- **Categories**: Distribution of categorical values
- **Correlations**: Between numeric columns

### 6. Generate Report

Create a Markdown report with:

```markdown
# Data Analysis Report: [filename]

## Overview
- **File**: [path]
- **Format**: [CSV/JSON/Parquet]
- **Rows**: [count]
- **Columns**: [count]

## Schema
[Table of column names, types]

## Statistical Summary
[Table of statistics per numeric column]

## Data Quality
### Missing Values
[Table of missing value counts]

### Duplicates
[Count and sample of duplicates]

### Outliers
[Outlier summary per numeric column]

## Key Findings
1. [Insight based on analysis]
2. [Pattern detected]

## Visualization Suggestions
- [Recommended charts based on data]
```

## Output

Display the analysis report directly in the conversation. For large datasets, summarize key findings and offer to write detailed results to a file.

## Error Handling

- If DuckDB is not installed, provide installation instructions
- If file format is unsupported, list supported formats
- If file is too large, suggest sampling strategies
- If queries fail, show the error and suggest fixes

## Examples

```
/analyze data/sales.csv
/analyze api_response.json profile
/analyze exports/report.csv quality
/analyze metrics.parquet stats
```
