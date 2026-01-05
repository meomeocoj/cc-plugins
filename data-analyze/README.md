# data-analyze

Comprehensive data analysis toolkit for Claude Code using DuckDB SQL.

## Features

- **Statistical summaries**: Mean, median, std, percentiles, correlations
- **Data quality checks**: Missing values, outliers, duplicates, type validation
- **Visualization suggestions**: Chart type recommendations based on data
- **Pattern detection**: Trends, anomalies, clustering insights

## Supported Data Types

- CSV/Excel files
- JSON/API responses (including JSONL)
- Parquet files
- Database query results

## Prerequisites

[DuckDB CLI](https://duckdb.org/docs/installation/) must be installed:

```bash
# macOS
brew install duckdb

# Linux
curl -LO https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
sudo mv duckdb /usr/local/bin/
```

## Installation

```bash
# Use with --plugin-dir
claude --plugin-dir /path/to/data-analyze

# Or copy to your project
cp -r data-analyze /your/project/.claude-plugin/
```

## Usage

### Command: `/analyze`

```bash
/analyze path/to/data.csv              # Full analysis
/analyze path/to/data.json profile     # Profile only
/analyze path/to/data.csv quality      # Quality checks only
/analyze path/to/data.parquet stats    # Statistics only
```

### Agent: `data-analyzer`

The agent activates when you ask for data analysis help:

- "Analyze this sales.csv file and find patterns"
- "Check the data quality of user_metrics.json"
- "What correlations exist in this dataset?"
- "Detect outliers in my financial data"

### Skill: `data-analysis`

Provides guidance on:
- DuckDB SQL syntax for analysis
- Statistical methods and functions
- Data quality check patterns
- Visualization recommendations

## Components

```
data-analyze/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── analyze.md           # /analyze command
├── agents/
│   └── data-analyzer.md     # Data analysis agent
├── skills/
│   └── data-analysis/
│       ├── SKILL.md         # Analysis guidance
│       └── references/
│           ├── duckdb-functions.md
│           └── visualization-guide.md
└── scripts/
    ├── profile.sql          # Data profiling template
    └── quality-check.sql    # Quality check template
```

## Example Workflow

1. Run `/analyze sales.csv` on your data file
2. Claude profiles the data and identifies column types
3. Statistical summaries are generated for numeric columns
4. Data quality issues (missing values, duplicates, outliers) are identified
5. A Markdown report is generated with findings and visualization suggestions

## DuckDB Quick Reference

```sql
-- Read CSV
SELECT * FROM 'file.csv' LIMIT 10;

-- Read JSON
SELECT * FROM read_json('file.json');

-- Basic statistics
SELECT AVG(col), MEDIAN(col), STDDEV(col) FROM 'file.csv';

-- Missing values
SELECT COUNT(*) - COUNT(col) as missing FROM 'file.csv';

-- Correlation
SELECT CORR(col_a, col_b) FROM 'file.csv';
```

## License

MIT
