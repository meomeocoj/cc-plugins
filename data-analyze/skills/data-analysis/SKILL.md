---
name: Data Analysis
description: This skill should be used when the user asks to "analyze data", "check data quality", "find patterns in data", "get statistics", "summarize CSV", "analyze JSON", "detect outliers", "find correlations", "suggest visualizations", or needs guidance on statistical analysis, data profiling, or pattern detection using DuckDB SQL.
version: 0.1.0
---

# Data Analysis with DuckDB

Comprehensive data analysis toolkit using DuckDB SQL for CSV, JSON, and database results.

## Overview

DuckDB provides powerful analytical capabilities directly on files without importing to a database. Execute SQL queries on CSV, JSON, and Parquet files for statistical analysis, data quality checks, and pattern detection.

## Core Analysis Workflow

### 1. Data Profiling

Start every analysis by understanding the data structure:

```sql
-- Profile a CSV file
DESCRIBE SELECT * FROM 'data.csv';

-- Get row count and sample
SELECT COUNT(*) as total_rows FROM 'data.csv';
SELECT * FROM 'data.csv' LIMIT 5;

-- Column-level profiling
SELECT
    column_name,
    COUNT(*) as non_null_count,
    COUNT(DISTINCT column_name) as unique_values
FROM 'data.csv'
GROUP BY ALL;
```

### 2. Statistical Summaries

Generate comprehensive statistics for numeric columns:

```sql
-- Basic statistics
SELECT
    AVG(column) as mean,
    MEDIAN(column) as median,
    STDDEV(column) as std_dev,
    MIN(column) as min_val,
    MAX(column) as max_val,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY column) as p25,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY column) as p75
FROM 'data.csv';

-- Correlation between columns
SELECT CORR(column_a, column_b) as correlation
FROM 'data.csv';
```

### 3. Data Quality Checks

Identify data quality issues:

```sql
-- Missing values per column
SELECT
    COUNT(*) - COUNT(column_name) as missing_count,
    ROUND(100.0 * (COUNT(*) - COUNT(column_name)) / COUNT(*), 2) as missing_pct
FROM 'data.csv';

-- Duplicate detection
SELECT *, COUNT(*) as dup_count
FROM 'data.csv'
GROUP BY ALL
HAVING COUNT(*) > 1;

-- Outlier detection (IQR method)
WITH stats AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as q3
    FROM 'data.csv'
)
SELECT * FROM 'data.csv', stats
WHERE value < q1 - 1.5 * (q3 - q1)
   OR value > q3 + 1.5 * (q3 - q1);
```

### 4. Pattern Detection

Identify trends and patterns:

```sql
-- Time-based trends (if date column exists)
SELECT
    DATE_TRUNC('month', date_column) as period,
    AVG(value) as avg_value,
    COUNT(*) as count
FROM 'data.csv'
GROUP BY 1
ORDER BY 1;

-- Distribution analysis
SELECT
    FLOOR(value / 10) * 10 as bucket,
    COUNT(*) as frequency
FROM 'data.csv'
GROUP BY 1
ORDER BY 1;

-- Top categories
SELECT category, COUNT(*) as count
FROM 'data.csv'
GROUP BY category
ORDER BY count DESC
LIMIT 10;
```

## File Format Support

### CSV Files
```sql
-- Read CSV with options
SELECT * FROM read_csv('file.csv',
    header=true,
    delim=',',
    nullstr='NA'
);
```

### JSON Files
```sql
-- Read JSON array
SELECT * FROM read_json('file.json');

-- Read JSON lines
SELECT * FROM read_json('file.jsonl', format='newline_delimited');

-- Extract nested fields
SELECT json_extract(data, '$.field.nested') as value
FROM read_json('file.json');
```

### Multiple Files
```sql
-- Glob pattern for multiple files
SELECT * FROM 'data/*.csv';

-- With filename column
SELECT *, filename FROM read_csv('data/*.csv', filename=true);
```

## Visualization Recommendations

Based on analysis results, suggest appropriate chart types:

| Data Pattern | Recommended Chart |
|-------------|-------------------|
| Distribution of single variable | Histogram, Box plot |
| Comparison across categories | Bar chart |
| Time series trends | Line chart |
| Correlation between 2 variables | Scatter plot |
| Part-to-whole relationship | Pie chart (if <7 categories) |
| Multiple metrics comparison | Grouped bar, Radar chart |

## Output Format

Present analysis results as a structured Markdown report:

```markdown
# Data Analysis Report

## Overview
- **File**: data.csv
- **Rows**: 10,000
- **Columns**: 15

## Statistical Summary
[Table of statistics per numeric column]

## Data Quality
- Missing values: [summary]
- Duplicates: [count]
- Outliers: [count and description]

## Key Findings
1. [Pattern or insight]
2. [Pattern or insight]

## Visualization Suggestions
- [Chart recommendation with rationale]
```

## DuckDB CLI Usage

Execute analysis from command line:

```bash
# Direct query
duckdb -c "SELECT * FROM 'data.csv' LIMIT 10"

# Run SQL file
duckdb -c ".read analysis.sql"

# Output to file
duckdb -c "SELECT * FROM 'data.csv'" -csv > output.csv
```

## Additional Resources

### Reference Files

For detailed DuckDB functions and patterns:
- **`references/duckdb-functions.md`** - Statistical and aggregate functions
- **`references/visualization-guide.md`** - Chart selection guide

### Scripts

Utility scripts for common analysis tasks:
- **`${CLAUDE_PLUGIN_ROOT}/scripts/profile.sql`** - Data profiling template
- **`${CLAUDE_PLUGIN_ROOT}/scripts/quality-check.sql`** - Quality check queries
