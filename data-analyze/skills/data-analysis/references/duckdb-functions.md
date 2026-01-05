# DuckDB Statistical Functions Reference

## Aggregate Functions

### Basic Statistics
| Function | Description | Example |
|----------|-------------|---------|
| `COUNT(*)` | Count all rows | `SELECT COUNT(*) FROM t` |
| `COUNT(col)` | Count non-null values | `SELECT COUNT(col) FROM t` |
| `COUNT(DISTINCT col)` | Count unique values | `SELECT COUNT(DISTINCT col) FROM t` |
| `SUM(col)` | Sum of values | `SELECT SUM(amount) FROM t` |
| `AVG(col)` | Arithmetic mean | `SELECT AVG(price) FROM t` |
| `MIN(col)` | Minimum value | `SELECT MIN(date) FROM t` |
| `MAX(col)` | Maximum value | `SELECT MAX(score) FROM t` |

### Advanced Statistics
| Function | Description | Example |
|----------|-------------|---------|
| `STDDEV(col)` | Standard deviation (sample) | `SELECT STDDEV(value) FROM t` |
| `STDDEV_POP(col)` | Standard deviation (population) | `SELECT STDDEV_POP(value) FROM t` |
| `VARIANCE(col)` | Variance (sample) | `SELECT VARIANCE(value) FROM t` |
| `VAR_POP(col)` | Variance (population) | `SELECT VAR_POP(value) FROM t` |
| `MEDIAN(col)` | Median value | `SELECT MEDIAN(price) FROM t` |
| `MODE(col)` | Most frequent value | `SELECT MODE(category) FROM t` |

### Percentiles
```sql
-- Continuous percentile (interpolated)
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) as median
FROM table;

-- Discrete percentile (actual value)
SELECT PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY value) as median
FROM table;

-- Multiple percentiles
SELECT
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY v) as p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY v) as p50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY v) as p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY v) as p90,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY v) as p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY v) as p99
FROM table;
```

### Correlation & Covariance
```sql
-- Pearson correlation coefficient (-1 to 1)
SELECT CORR(x, y) as correlation FROM table;

-- Covariance (sample)
SELECT COVAR_SAMP(x, y) as covariance FROM table;

-- Covariance (population)
SELECT COVAR_POP(x, y) as covariance FROM table;

-- Regression slope and intercept
SELECT
    REGR_SLOPE(y, x) as slope,
    REGR_INTERCEPT(y, x) as intercept,
    REGR_R2(y, x) as r_squared
FROM table;
```

### List Aggregates
```sql
-- Collect values into list
SELECT LIST(value) as all_values FROM table;

-- String aggregation
SELECT STRING_AGG(name, ', ') as names FROM table;

-- First/Last value
SELECT FIRST(value), LAST(value) FROM table;

-- Arbitrary value (any non-null)
SELECT ARBITRARY(category) FROM table;
```

## Window Functions

### Ranking
```sql
SELECT
    *,
    ROW_NUMBER() OVER (ORDER BY score DESC) as rank,
    RANK() OVER (ORDER BY score DESC) as rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank,
    NTILE(4) OVER (ORDER BY score) as quartile,
    PERCENT_RANK() OVER (ORDER BY score) as pct_rank
FROM table;
```

### Running Calculations
```sql
SELECT
    *,
    SUM(value) OVER (ORDER BY date) as running_total,
    AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d,
    LAG(value, 1) OVER (ORDER BY date) as prev_value,
    LEAD(value, 1) OVER (ORDER BY date) as next_value,
    value - LAG(value) OVER (ORDER BY date) as change
FROM table;
```

### Partitioned Windows
```sql
SELECT
    category,
    date,
    value,
    SUM(value) OVER (PARTITION BY category ORDER BY date) as category_running_total,
    AVG(value) OVER (PARTITION BY category) as category_avg,
    value / SUM(value) OVER (PARTITION BY category) as pct_of_category
FROM table;
```

## Date/Time Functions

### Extraction
```sql
SELECT
    YEAR(date_col) as year,
    MONTH(date_col) as month,
    DAY(date_col) as day,
    DAYOFWEEK(date_col) as dow,
    WEEK(date_col) as week,
    QUARTER(date_col) as quarter
FROM table;
```

### Truncation
```sql
SELECT
    DATE_TRUNC('year', ts) as year_start,
    DATE_TRUNC('month', ts) as month_start,
    DATE_TRUNC('week', ts) as week_start,
    DATE_TRUNC('day', ts) as day_start,
    DATE_TRUNC('hour', ts) as hour_start
FROM table;
```

### Date Arithmetic
```sql
SELECT
    date + INTERVAL 7 DAY as plus_week,
    date - INTERVAL 1 MONTH as minus_month,
    DATEDIFF('day', start_date, end_date) as days_between,
    AGE(end_date, start_date) as interval
FROM table;
```

## String Functions

### Analysis
```sql
SELECT
    LENGTH(text) as char_count,
    LENGTH(text) - LENGTH(REPLACE(text, ' ', '')) + 1 as word_count,
    REGEXP_MATCHES(text, pattern) as matches,
    CONTAINS(text, 'search') as has_search
FROM table;
```

### Cleaning
```sql
SELECT
    TRIM(text) as trimmed,
    LOWER(text) as lowercase,
    UPPER(text) as uppercase,
    REGEXP_REPLACE(text, '[^a-zA-Z0-9]', '') as alphanumeric_only
FROM table;
```

## Type Conversion

```sql
SELECT
    CAST(value AS INTEGER) as int_val,
    CAST(value AS DOUBLE) as float_val,
    CAST(value AS VARCHAR) as string_val,
    TRY_CAST(value AS INTEGER) as safe_int,  -- Returns NULL on failure
    STRPTIME(date_str, '%Y-%m-%d') as parsed_date
FROM table;
```

## NULL Handling

```sql
SELECT
    COALESCE(nullable_col, 'default') as with_default,
    NULLIF(value, 0) as zero_as_null,
    IFNULL(value, replacement) as replaced,
    value IS NULL as is_missing,
    value IS NOT NULL as has_value
FROM table;
```

## Conditional Logic

```sql
SELECT
    CASE
        WHEN value < 0 THEN 'negative'
        WHEN value = 0 THEN 'zero'
        ELSE 'positive'
    END as category,
    IF(condition, true_val, false_val) as ternary,
    GREATEST(a, b, c) as max_of_three,
    LEAST(a, b, c) as min_of_three
FROM table;
```
