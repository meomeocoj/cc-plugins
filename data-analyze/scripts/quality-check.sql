-- Data Quality Check Script for DuckDB
-- Usage: duckdb -c ".read quality-check.sql" (after setting FILE variable)
-- Or: Replace '${FILE}' with actual file path

-- ===========================================
-- 1. DUPLICATE DETECTION
-- ===========================================
SELECT 'DUPLICATES' as check_type;

-- Full row duplicates
SELECT 'Full row duplicates:' as description;
SELECT *, COUNT(*) as dup_count
FROM '${FILE}'
GROUP BY ALL
HAVING COUNT(*) > 1
LIMIT 10;

-- Count of duplicate rows
SELECT COUNT(*) as duplicate_row_count
FROM (
    SELECT *, COUNT(*) as cnt
    FROM '${FILE}'
    GROUP BY ALL
    HAVING COUNT(*) > 1
);

-- ===========================================
-- 2. MISSING VALUES
-- ===========================================
SELECT 'MISSING_VALUES' as check_type;

-- Total rows for reference
SELECT COUNT(*) as total_rows FROM '${FILE}';

-- Per-column null counts (adjust columns for your data)
-- SELECT
--     COUNT(*) - COUNT(col1) as col1_missing,
--     COUNT(*) - COUNT(col2) as col2_missing,
--     ROUND(100.0 * (COUNT(*) - COUNT(col1)) / COUNT(*), 2) as col1_missing_pct,
--     ROUND(100.0 * (COUNT(*) - COUNT(col2)) / COUNT(*), 2) as col2_missing_pct
-- FROM '${FILE}';

-- ===========================================
-- 3. OUTLIER DETECTION (IQR Method)
-- ===========================================
SELECT 'OUTLIERS' as check_type;

-- Template for numeric columns (adjust column name)
-- WITH stats AS (
--     SELECT
--         PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY numeric_col) as q1,
--         PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY numeric_col) as q3
--     FROM '${FILE}'
-- ),
-- bounds AS (
--     SELECT
--         q1,
--         q3,
--         q1 - 1.5 * (q3 - q1) as lower_bound,
--         q3 + 1.5 * (q3 - q1) as upper_bound
--     FROM stats
-- )
-- SELECT
--     COUNT(*) as outlier_count,
--     MIN(numeric_col) as min_outlier,
--     MAX(numeric_col) as max_outlier
-- FROM '${FILE}', bounds
-- WHERE numeric_col < lower_bound OR numeric_col > upper_bound;

-- ===========================================
-- 4. VALUE RANGE VALIDATION
-- ===========================================
SELECT 'VALUE_RANGES' as check_type;

-- Check for negative values in columns that should be positive
-- SELECT COUNT(*) as negative_count
-- FROM '${FILE}'
-- WHERE amount < 0;

-- Check for future dates
-- SELECT COUNT(*) as future_dates
-- FROM '${FILE}'
-- WHERE date_col > CURRENT_DATE;

-- Check for invalid percentages
-- SELECT COUNT(*) as invalid_pct
-- FROM '${FILE}'
-- WHERE pct_col < 0 OR pct_col > 100;

-- ===========================================
-- 5. CONSISTENCY CHECKS
-- ===========================================
SELECT 'CONSISTENCY' as check_type;

-- Check for inconsistent casing in text columns
-- SELECT DISTINCT category, COUNT(*) as cnt
-- FROM '${FILE}'
-- GROUP BY category
-- ORDER BY LOWER(category), cnt DESC;

-- Check for whitespace issues
-- SELECT COUNT(*) as whitespace_issues
-- FROM '${FILE}'
-- WHERE col != TRIM(col);

-- ===========================================
-- 6. UNIQUENESS VALIDATION
-- ===========================================
SELECT 'UNIQUENESS' as check_type;

-- Check if ID column is unique
-- SELECT
--     COUNT(*) as total,
--     COUNT(DISTINCT id_col) as unique_ids,
--     COUNT(*) - COUNT(DISTINCT id_col) as duplicate_ids
-- FROM '${FILE}';

-- ===========================================
-- 7. REFERENTIAL INTEGRITY (if multiple files)
-- ===========================================
SELECT 'REFERENTIAL_INTEGRITY' as check_type;

-- Check for orphaned records
-- SELECT COUNT(*) as orphaned_records
-- FROM '${FILE}' a
-- LEFT JOIN 'reference.csv' b ON a.foreign_key = b.id
-- WHERE b.id IS NULL;

-- ===========================================
-- SUMMARY
-- ===========================================
SELECT 'QUALITY_SUMMARY' as check_type;
SELECT
    (SELECT COUNT(*) FROM '${FILE}') as total_rows,
    (SELECT COUNT(*) FROM (SELECT *, COUNT(*) FROM '${FILE}' GROUP BY ALL HAVING COUNT(*) > 1)) as duplicate_rows;
