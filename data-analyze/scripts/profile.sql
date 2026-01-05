-- Data Profiling Script for DuckDB
-- Usage: duckdb -c ".read profile.sql" (after setting FILE variable)
-- Or: Replace '${FILE}' with actual file path

-- Overview
SELECT 'OVERVIEW' as section;
SELECT COUNT(*) as total_rows FROM '${FILE}';

-- Schema
SELECT 'SCHEMA' as section;
DESCRIBE SELECT * FROM '${FILE}';

-- Sample rows
SELECT 'SAMPLE' as section;
SELECT * FROM '${FILE}' LIMIT 5;

-- Numeric column statistics (template - adjust column names)
SELECT 'NUMERIC_STATS' as section;
-- Uncomment and adjust for your columns:
-- SELECT
--     'column_name' as column,
--     COUNT(column_name) as non_null,
--     COUNT(*) - COUNT(column_name) as null_count,
--     AVG(column_name) as mean,
--     MEDIAN(column_name) as median,
--     STDDEV(column_name) as std_dev,
--     MIN(column_name) as min_val,
--     MAX(column_name) as max_val,
--     PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY column_name) as p25,
--     PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY column_name) as p75
-- FROM '${FILE}';

-- Categorical column value counts (template)
SELECT 'CATEGORICAL_STATS' as section;
-- Uncomment and adjust for your columns:
-- SELECT column_name, COUNT(*) as count
-- FROM '${FILE}'
-- GROUP BY column_name
-- ORDER BY count DESC
-- LIMIT 20;

-- Missing value summary
SELECT 'MISSING_VALUES' as section;
-- Generate per-column missing counts dynamically
-- Adjust column list for your data:
-- SELECT
--     SUM(CASE WHEN col1 IS NULL THEN 1 ELSE 0 END) as col1_nulls,
--     SUM(CASE WHEN col2 IS NULL THEN 1 ELSE 0 END) as col2_nulls
-- FROM '${FILE}';
