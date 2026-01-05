# Data Visualization Selection Guide

## Chart Selection by Data Type

### Single Variable (Univariate)

| Data Type | Chart Options | When to Use |
|-----------|---------------|-------------|
| Continuous numeric | Histogram | Show distribution shape |
| Continuous numeric | Box plot | Show quartiles, outliers |
| Continuous numeric | Density plot | Smooth distribution curve |
| Categorical | Bar chart | Compare category counts |
| Categorical | Pie chart | Show part-to-whole (max 7 categories) |

### Two Variables (Bivariate)

| Data Types | Chart Options | When to Use |
|------------|---------------|-------------|
| Numeric vs Numeric | Scatter plot | Show correlation, clusters |
| Numeric vs Numeric | Line chart | Time series, trends |
| Categorical vs Numeric | Box plot (grouped) | Compare distributions |
| Categorical vs Numeric | Bar chart | Compare means/totals |
| Categorical vs Categorical | Heatmap | Show relationships |
| Categorical vs Categorical | Stacked bar | Compare proportions |

### Multiple Variables (Multivariate)

| Scenario | Chart Options | When to Use |
|----------|---------------|-------------|
| 3+ numeric variables | Pair plot/scatter matrix | Overview of relationships |
| Numeric with categories | Faceted charts | Compare across groups |
| Many categories | Treemap | Hierarchical proportions |
| Multiple metrics | Radar/spider chart | Compare profiles |
| Geographic data | Choropleth map | Regional patterns |

## Decision Tree for Chart Selection

```
Q: How many variables?
├── 1 variable
│   └── Q: Data type?
│       ├── Numeric → Histogram or Box plot
│       └── Categorical → Bar chart
├── 2 variables
│   └── Q: Data types?
│       ├── Both Numeric → Scatter or Line chart
│       ├── Both Categorical → Heatmap
│       └── Mixed → Grouped Bar or Box plot
└── 3+ variables
    └── Q: Primary relationship?
        ├── Time-based → Multi-line chart
        ├── Hierarchical → Treemap
        └── Comparative → Faceted charts
```

## Chart Recommendations by Analysis Goal

### Distribution Analysis
- **Histogram**: Best for understanding the shape of numeric data
- **Box plot**: Best for seeing quartiles, median, and outliers
- **Violin plot**: Combines box plot with density estimate
- **Density plot**: Smooth continuous distribution

### Comparison
- **Bar chart**: Compare values across categories
- **Grouped bar**: Compare multiple metrics across categories
- **Lollipop chart**: Alternative to bar for many categories
- **Dot plot**: Precise value comparison

### Trend Analysis
- **Line chart**: Show change over time
- **Area chart**: Emphasize cumulative change
- **Sparklines**: Compact trend indicators
- **Moving average overlay**: Smooth noisy trends

### Correlation/Relationship
- **Scatter plot**: Two numeric variables
- **Bubble chart**: Add third variable as size
- **Correlation heatmap**: Matrix of correlations
- **Pair plot**: All pairwise relationships

### Composition
- **Pie chart**: Part-to-whole (use sparingly, max 7 slices)
- **Donut chart**: Modern pie alternative
- **Stacked bar**: Composition over categories
- **100% stacked bar**: Proportional composition
- **Treemap**: Hierarchical composition

### Ranking
- **Horizontal bar chart**: Ranked categories
- **Bump chart**: Rank changes over time
- **Waterfall chart**: Sequential contributions

## Anti-Patterns to Avoid

### Pie Chart Misuse
- More than 7 categories
- Categories with similar values
- Comparing multiple pies
- 3D effects

### Line Chart Misuse
- Non-continuous x-axis
- Too many series (>5)
- Inconsistent time intervals
- Missing data without indication

### Bar Chart Misuse
- Non-zero baseline
- Too many categories
- 3D effects
- Poor color choices

### General Mistakes
- Truncated axes hiding context
- Rainbow color palettes
- Chart junk (unnecessary decorations)
- Missing labels, titles, legends

## Color Guidelines

### Sequential Data (low to high)
- Single hue gradient (light to dark)
- Examples: light blue → dark blue

### Diverging Data (negative ↔ positive)
- Two-hue gradient with neutral middle
- Examples: red ↔ white ↔ blue

### Categorical Data
- Distinct, contrasting colors
- Maximum 7-10 colors
- Consider colorblind accessibility

### Emphasis
- Use gray for context, accent color for focus
- Highlight specific data points
- De-emphasize less important elements

## SQL Queries for Chart Data

### Histogram Data
```sql
SELECT
    FLOOR(value / bin_width) * bin_width as bin_start,
    COUNT(*) as frequency
FROM table
GROUP BY 1
ORDER BY 1;
```

### Time Series
```sql
SELECT
    DATE_TRUNC('day', timestamp) as date,
    SUM(value) as total,
    AVG(value) as average
FROM table
GROUP BY 1
ORDER BY 1;
```

### Category Comparison
```sql
SELECT
    category,
    SUM(value) as total,
    AVG(value) as average,
    COUNT(*) as count
FROM table
GROUP BY category
ORDER BY total DESC;
```

### Correlation Matrix Data
```sql
SELECT
    CORR(col1, col2) as corr_1_2,
    CORR(col1, col3) as corr_1_3,
    CORR(col2, col3) as corr_2_3
FROM table;
```

### Percentile Distribution
```sql
SELECT
    category,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY value) as median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as p75
FROM table
GROUP BY category;
```
