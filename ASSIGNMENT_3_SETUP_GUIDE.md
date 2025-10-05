# Assignment 3 Setup Guide
## Data Transformation with dplyr - Part 1

### Assignment Overview
**Topic:** Data Transformation using `select()`, `filter()`, and `arrange()`
**Dataset:** retail_transactions.csv (500 rows, 8 columns)
**Difficulty:** Beginner (First-time R students)

### Required Sections (12 total):

#### Part 1: Data Import (2 sections)
1. **Import data** - `read_csv("retail_transactions.csv")`
2. **Initial exploration** - `head()`, `str()`, `names()`

#### Part 2: Column Selection with `select()` (4 sections)
3. **Basic selection** - Select specific columns by name
4. **Range selection** - Select columns using `:` operator
5. **Pattern selection** - Use `starts_with()`, `contains()`
6. **Exclusion selection** - Remove columns with `-`

#### Part 3: Row Filtering with `filter()` (5 sections)
7. **Single condition** - Filter by amount or category
8. **Multiple AND conditions** - Combine with `&`
9. **Multiple OR conditions** - Use `|` or `%in%`
10. **Date filtering** - Filter by date range
11. **Advanced challenge** - Find customers in multiple categories

#### Part 4: Data Sorting with `arrange()` (3 sections)
12. **Single column sort** - Sort ascending/descending
13. **Multiple column sort** - Sort by city then amount
14. **Date-based sort** - Chronological ordering

#### Part 5: Chaining Operations (3 sections)
15. **Simple chain** - Filter + select + arrange
16. **Complex chain** - Multiple operations
17. **Business intelligence** - Real-world analysis

#### Part 6: Analysis Questions (4 sections)
18. **Transaction counts** - Count filtered datasets
19. **Top customers** - Find frequent buyers
20. **Product analysis** - Most expensive items
21. **Geographic analysis** - City with highest transaction

#### Part 7: Reflection Questions (4 questions)
22. **Pipe operator benefits** - Why use `%>%`?
23. **Filtering strategy** - Trade-offs of specificity
24. **Sorting importance** - Business scenarios
25. **Real-world application** - Combined operations

### Solution Key Points:

**Part 1 Solutions:**
```r
# 1.1 Import
transactions <- read_csv("retail_transactions.csv")

# 1.2 Exploration
head(transactions, 10)
str(transactions)
names(transactions)
```

**Part 2 Solutions:**
```r
# 2.1 Basic selection
basic_info <- transactions %>%
  select(TransactionID, CustomerID, ProductName, TotalAmount)

# 2.2 Range selection
customer_details <- transactions %>%
  select(CustomerID:CustomerCity)

# 2.3 Pattern selection
date_columns <- transactions %>%
  select(starts_with("Date") | starts_with("Time"))

amount_columns <- transactions %>%
  select(contains("Amount"))

# 2.4 Exclusion
no_ids <- transactions %>%
  select(-TransactionID, -CustomerID)
```

**Part 3 Solutions:**
```r
# 3.1 Single condition
high_value_transactions <- transactions %>%
  filter(TotalAmount > 100)

electronics_transactions <- transactions %>%
  filter(ProductCategory == "Electronics")

# 3.2 Multiple AND
ny_bulk_purchases <- transactions %>%
  filter(TotalAmount > 50 & Quantity > 1 & CustomerCity == "New York")

# 3.3 Multiple OR
entertainment_transactions <- transactions %>%
  filter(ProductCategory %in% c("Books", "Music", "Movies"))

# 3.4 Date filtering
march_transactions <- transactions %>%
  filter(month(TransactionDate) == 3 & year(TransactionDate) == 2024)

# 3.5 Advanced challenge
electronics_customers <- transactions %>%
  filter(ProductCategory == "Electronics") %>%
  pull(CustomerID) %>%
  unique()

clothing_customers <- transactions %>%
  filter(ProductCategory == "Clothing") %>%
  pull(CustomerID) %>%
  unique()

both_categories_customers <- intersect(electronics_customers, clothing_customers)
```

**Part 4 Solutions:**
```r
# 4.1 Single column sort
transactions_by_amount_asc <- transactions %>%
  arrange(TotalAmount)

transactions_by_amount_desc <- transactions %>%
  arrange(desc(TotalAmount))

# 4.2 Multiple columns
transactions_by_city_amount <- transactions %>%
  arrange(CustomerCity, desc(TotalAmount))

# 4.3 Date-based
transactions_chronological <- transactions %>%
  arrange(TransactionDate)
```

**Part 5 Solutions:**
```r
# 5.1 Simple chain
premium_purchases <- transactions %>%
  filter(TotalAmount > 75) %>%
  select(CustomerName, ProductName, TotalAmount, CustomerCity) %>%
  arrange(desc(TotalAmount))

# 5.2 Complex chain
recent_tech_purchases <- transactions %>%
  filter(ProductCategory %in% c("Electronics", "Computers")) %>%
  select(TransactionDate, CustomerName, ProductName, TotalAmount) %>%
  arrange(desc(TransactionDate), desc(TotalAmount)) %>%
  head(20)

# 5.3 Business intelligence
high_value_customers <- transactions %>%
  filter(TotalAmount > 200) %>%
  select(CustomerName, CustomerCity, ProductName, TotalAmount) %>%
  arrange(CustomerName, desc(TotalAmount))
```

### Grading Criteria:

**Code Completion (60%):**
- Each of 21 code sections = ~2.9% each
- Must have working code with outputs
- Template code doesn't count

**Reflection Questions (40%):**
- 4 questions × 10% each
- Must provide substantive answers (50+ words)
- Generic answers get 50% credit

**Common Student Mistakes:**
1. Forgetting to use `%>%` pipe operator
2. Not running cells (no outputs)
3. Using `=` instead of `==` in filter
4. Forgetting `desc()` for descending sort
5. Not loading tidyverse library
6. Shallow reflection answers

### Expected Outputs:

Students should see:
- Data dimensions: "500 rows x 8 columns"
- High value transactions: ~150 rows
- Electronics transactions: ~80 rows
- Premium purchases: ~200 rows
- Reflection answers: 2-3 sentences each

### Assignment-Specific Prompt Instructions:

**For Code Analysis:**
- Check for `library(tidyverse)` at start
- Verify `%>%` pipe operator usage
- Look for actual outputs (not just code)
- Count completed sections out of 21
- Template code = 0 credit

**For Feedback:**
- Evaluate reflection depth (not just length)
- Check for business context understanding
- Assess pipe operator comprehension
- Verify sorting logic understanding

