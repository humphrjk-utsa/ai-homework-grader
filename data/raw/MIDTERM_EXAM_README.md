# Comprehensive Midterm Exam - All 8 Lessons

## Overview

**File:** `MIDTERM_EXAM_comprehensive.ipynb`  
**Format:** Jupyter Notebook (R kernel)  
**Total Cells:** 39  
**Time Limit:** 4 hours  
**Coverage:** ALL 8 Lessons (100% of course material)

## Complete Lesson Coverage

### ✅ Lesson 1: R Basics and Data Import
- Set working directory
- Load packages (tidyverse, lubridate)
- Import multiple CSV files
- Examine data structures

### ✅ Lesson 2: Data Cleaning
- Identify missing values (colSums, is.na())
- Handle NAs (na.omit())
- Detect outliers (IQR method)
- Create cleaned dataset

### ✅ Lesson 3: Data Transformation Part 1
- select() specific columns
- filter() by conditions
- arrange() to sort data
- Chain operations with %>%

### ✅ Lesson 4: Data Transformation Part 2
- mutate() to create calculated columns
- summarize() for aggregations
- group_by() for grouped analysis
- Calculate business metrics

### ✅ Lesson 5: Data Reshaping
- pivot_wider() for long to wide format
- pivot_longer() for wide to long format
- Understand tidy data principles

### ✅ Lesson 6: Combining Datasets
- left_join() customers and orders
- inner_join() orders and order_items
- Integrate multiple datasets

### ✅ Lesson 7: String & Date Operations
- str_trim(), str_to_title() for text cleaning
- ymd(), mdy(), dmy() for date parsing
- month(), wday() for date component extraction

### ✅ Lesson 8: Advanced Wrangling
- case_when() for complex conditional logic
- Calculate business KPIs
- Generate executive summaries

## Exam Structure

### Part 1: R Basics & Data Import (4 tasks)
- Set working directory
- Load packages
- Import 5 datasets
- Examine structures

### Part 2: Data Cleaning (3 tasks)
- Check missing values → `missing_summary`
- Handle NAs → `sales_clean`
- Detect outliers → `outlier_analysis`

### Part 3: Data Transformation Part 1 (4 tasks)
- Select columns → `sales_summary`
- Filter data → `high_revenue_sales`
- Sort data → `top_sales`
- Chain operations → `regional_top_sales`

### Part 4: Data Transformation Part 2 (4 tasks)
- Create calculated columns → `sales_enhanced`
- Calculate summaries → `overall_summary`
- Group by region → `regional_summary`
- Group by category → `category_summary`

### Part 5: Data Reshaping (3 tasks)
- Create summary data → `region_category_revenue`
- Pivot to wide → `revenue_wide`
- Pivot to long → `revenue_long`

### Part 6: Combining Datasets (2 tasks)
- Join customers & orders → `customer_orders`
- Join orders & items → `orders_with_items`

### Part 7: String & Date Operations (2 tasks)
- Clean text → `region_clean`, `category_clean`
- Parse dates → `date_parsed`, `sale_month`, `sale_weekday`

### Part 8: Advanced Wrangling (2 tasks)
- Create categories → `performance_tier`
- Calculate KPIs → `business_kpis`

### Part 9: Reflection Questions (5 questions)
- Data cleaning impact
- Grouped analysis value
- Data reshaping purpose
- Joining datasets
- Skills integration

## Required Data Files

Students must have these files in their data directory:
- `company_sales_data.csv`
- `customers.csv`
- `products.csv`
- `orders.csv`
- `order_items.csv`

**Note:** Students set their own working directory at the beginning.

## Key Variables for Grading

### Dataframes Students Must Create:
1. `missing_summary` - Missing value counts
2. `sales_clean` - Cleaned sales data
3. `outlier_analysis` - Outlier thresholds
4. `sales_summary` - Selected columns
5. `high_revenue_sales` - Filtered data
6. `top_sales` - Top 10 sales
7. `regional_top_sales` - Chained operations result
8. `sales_enhanced` - Enhanced with calculated columns
9. `overall_summary` - Overall metrics
10. `regional_summary` - Regional performance
11. `category_summary` - Category performance
12. `region_category_revenue` - Region-category data
13. `revenue_wide` - Wide format data
14. `revenue_long` - Long format data
15. `customer_orders` - Joined customers and orders
16. `orders_with_items` - Joined orders and items
17. `business_kpis` - Business KPIs

### Calculated Columns in sales_enhanced:
- `revenue_per_unit`
- `high_value`
- `region_clean`
- `category_clean`
- `date_parsed`
- `sale_month`
- `sale_weekday`
- `performance_tier`

## Output Markers for Grading

Each task includes clear output markers:
```
========== SECTION NAME ==========
[output here]
```

This makes it easy to identify and parse outputs programmatically.

## Difficulty Level

**Appropriate for first-time business analytics students:**
- Clear instructions for each task
- Hints provided where needed
- Progressive difficulty
- Builds on previous tasks
- Real-world business context
- Not overly complex

**Challenging enough to assess mastery:**
- Requires applying knowledge, not just copying
- Integrates multiple skills
- Requires business thinking
- Tests understanding, not memorization

## Grading Criteria

### Code Correctness (40%)
- All required dataframes created
- Correct variable names
- Accurate calculations
- Proper function usage

### Code Quality (20%)
- Clean, organized code
- Helpful comments
- Proper use of pipe operator
- Efficient approach

### Business Understanding (20%)
- Appropriate analysis choices
- Meaningful interpretations
- Context awareness

### Analysis & Insights (15%)
- Correct summaries
- Logical groupings
- Appropriate categorizations

### Reflection Questions (5%)
- Complete answers
- Demonstrates understanding
- Specific examples

## Time Management

Suggested time allocation:
- Part 1: 20 minutes (setup)
- Part 2: 30 minutes (cleaning)
- Part 3: 30 minutes (transformation 1)
- Part 4: 40 minutes (transformation 2)
- Part 5: 30 minutes (reshaping)
- Part 6: 20 minutes (joins)
- Part 7: 30 minutes (string/date)
- Part 8: 30 minutes (advanced)
- Part 9: 30 minutes (reflection)
- **Total: 4 hours**

## Academic Integrity

Students may use:
- Course notes and lessons
- R documentation
- Previous homework

Students may NOT:
- Collaborate with others
- Use external help
- Share solutions

---

**Created:** 2025-01-05  
**Purpose:** Comprehensive midterm exam  
**Coverage:** 100% of Lessons 1-8  
**Difficulty:** Appropriate for first-time students  
**Grading:** Structured for automated assessment
