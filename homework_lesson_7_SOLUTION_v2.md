# Assignment 7 Solution - Version 2 (Processed Data)

## Data Structure

This solution works with the ACTUAL data students have:
- `customer_feedback (1).csv` - 100 rows with FeedbackID, CustomerID, Feedback_Text, Contact_Info, Feedback_Date
- `transaction_log.csv` - 150 rows with LogID, CustomerID, Transaction_DateTime, Amount, Status
- `product_catalog.csv` - 75 rows with ProductID, Product_Description, Category, Price, In_Stock

## Key Differences from Version 1

1. **No customer names in transactions** - Must join with feedback to get names
2. **Mixed date formats** - Requires parse_date_time() not simple ymd()
3. **PascalCase columns** - Product_Description not product_name
4. **More complex data** - 100/150/75 rows vs 20/30/30

## Solution Code

```r
# Task 1.1: Load Required Packages
library(tidyverse)
library(lubridate)
cat("✅ Packages loaded successfully!\n")

# Task 1.2: Import Datasets
feedback <- read_csv("data/processed/customer_feedback (1).csv")
transactions <- read_csv("data/processed/transaction_log.csv")
products <- read_csv("data/processed/product_catalog.csv")

cat("✅ Data imported successfully!\n")
cat("Feedback rows:", nrow(feedback), "\n")
cat("Transaction rows:", nrow(transactions), "\n")
cat("Product rows:", nrow(products), "\n")

# Task 1.3: Initial Data Exploration
cat("=== CUSTOMER FEEDBACK DATA ===\n")
str(feedback)
head(feedback, 5)

cat("\n=== TRANSACTION DATA ===\n")
str(transactions)
head(transactions, 5)

cat("\n=== PRODUCT CATALOG DATA ===\n")
str(products)
head(products, 5)

# Task 2.1: Clean Product Names
# NOTE: Column is Product_Description not product_name
products_clean <- products %>%
  mutate(
    product_name_clean = str_to_title(str_trim(Product_Description))
  )

cat("Product Name Cleaning Results:\n")
products_clean %>%
  select(Product_Description, product_name_clean) %>%
  head(10) %>%
  print()

# Task 2.2: Standardize Product Categories
products_clean <- products_clean %>%
  mutate(
    category_clean = str_to_title(str_trim(Category))
  )

cat("Original categories:\n")
print(unique(products$Category))

cat("\nCleaned categories:\n")
print(unique(products_clean$category_clean))

# Task 2.3: Clean Customer Feedback Text
# NOTE: Column is Feedback_Text not feedback_text
feedback_clean <- feedback %>%
  mutate(
    feedback_clean = str_squish(str_to_lower(Feedback_Text))
  )

cat("Feedback Cleaning Sample:\n")
feedback_clean %>%
  select(Feedback_Text, feedback_clean) %>%
  head(5) %>%
  print()

# Task 3.1: Detect Product Features
products_clean <- products_clean %>%
  mutate(
    is_wireless = str_detect(str_to_lower(product_name_clean), "wireless"),
    is_premium = str_detect(str_to_lower(product_name_clean), "pro|premium|deluxe"),
    is_gaming = str_detect(str_to_lower(product_name_clean), "gaming|gamer")
  )

cat("Product Feature Detection:\n")
products_clean %>%
  select(product_name_clean, is_wireless, is_premium, is_gaming) %>%
  head(10) %>%
  print()

cat("\nFeature Summary:\n")
cat("Wireless products:", sum(products_clean$is_wireless), "\n")
cat("Premium products:", sum(products_clean$is_premium), "\n")
cat("Gaming products:", sum(products_clean$is_gaming), "\n")

# Task 3.2: Extract Product Specifications
products_clean <- products_clean %>%
  mutate(
    size_number = str_extract(product_name_clean, "\\d+")
  )

cat("Extracted Product Specifications:\n")
products_clean %>%
  filter(!is.na(size_number)) %>%
  select(product_name_clean, size_number) %>%
  head(10) %>%
  print()

# Task 3.3: Simple Sentiment Analysis
feedback_clean <- feedback_clean %>%
  mutate(
    positive_words = str_count(feedback_clean, "great|excellent|love|amazing"),
    negative_words = str_count(feedback_clean, "bad|terrible|hate|awful"),
    sentiment_score = positive_words - negative_words
  )

cat("Sentiment Analysis Results:\n")
feedback_clean %>%
  select(feedback_clean, positive_words, negative_words, sentiment_score) %>%
  head(10) %>%
  print()

cat("\nOverall Sentiment Summary:\n")
cat("Average sentiment score:", mean(feedback_clean$sentiment_score), "\n")
cat("Positive reviews:", sum(feedback_clean$sentiment_score > 0), "\n")
cat("Negative reviews:", sum(feedback_clean$sentiment_score < 0), "\n")

# Task 4.1: Parse Transaction Dates
# CRITICAL: Mixed formats require parse_date_time()
# Some dates: "4/5/24 14:30" (mdy HM)
# Some dates: "25-03-2024 16:45:30" (dmy HMS)
transactions_clean <- transactions %>%
  mutate(
    date_parsed = parse_date_time(
      Transaction_DateTime,
      orders = c("mdy HM", "dmy HMS", "dmy HM", "ymd HMS"),
      quiet = TRUE
    )
  )

# Verify parsing worked - should have NO NAs
cat("Date Parsing Results:\n")
cat("Total rows:", nrow(transactions_clean), "\n")
cat("Successfully parsed:", sum(!is.na(transactions_clean$date_parsed)), "\n")
cat("Failed to parse:", sum(is.na(transactions_clean$date_parsed)), "\n")

transactions_clean %>%
  select(Transaction_DateTime, date_parsed) %>%
  head(10) %>%
  print()

# Task 4.2: Extract Date Components
transactions_clean <- transactions_clean %>%
  mutate(
    trans_year = year(date_parsed),
    trans_month = month(date_parsed),
    trans_month_name = month(date_parsed, label = TRUE, abbr = FALSE),
    trans_day = day(date_parsed),
    trans_weekday = wday(date_parsed, label = TRUE, abbr = FALSE),
    trans_quarter = quarter(date_parsed)
  )

cat("Date Component Extraction:\n")
transactions_clean %>%
  select(date_parsed, trans_month_name, trans_weekday, trans_quarter) %>%
  head(10) %>%
  print()

# Task 4.3: Identify Weekend Transactions
transactions_clean <- transactions_clean %>%
  mutate(
    is_weekend = wday(date_parsed) %in% c(1, 7)
  )

cat("Weekend vs Weekday Transactions:\n")
table(transactions_clean$is_weekend) %>% print()

cat("\nPercentage of weekend transactions:",
    round(sum(transactions_clean$is_weekend) / nrow(transactions_clean) * 100, 1), "%\n")

# Task 5.1: Calculate Days Since Transaction
transactions_clean <- transactions_clean %>%
  mutate(
    days_since = as.numeric(today() - as_date(date_parsed))
  )

cat("Days Since Transaction:\n")
transactions_clean %>%
  select(CustomerID, date_parsed, days_since) %>%
  arrange(desc(days_since)) %>%
  head(10) %>%
  print()

# Task 5.2: Categorize by Recency
transactions_clean <- transactions_clean %>%
  mutate(
    recency_category = case_when(
      days_since <= 30 ~ "Recent",
      days_since <= 90 ~ "Moderate",
      days_since > 90 ~ "At Risk",
      TRUE ~ NA_character_
    )
  )

cat("Recency Category Distribution:\n")
table(transactions_clean$recency_category) %>% print()

cat("\nAt-Risk Customers (>90 days):\n")
transactions_clean %>%
  filter(recency_category == "At Risk") %>%
  select(CustomerID, date_parsed, days_since) %>%
  arrange(desc(days_since)) %>%
  head(10) %>%
  print()

# Task 6.1: Extract First Names and Create Personalized Messages
# CRITICAL CHALLENGE: Transactions only have CustomerID, not names!
# SOLUTION: Join with feedback to get customer names

# First, get unique customer names from feedback
customer_names <- feedback_clean %>%
  distinct(CustomerID) %>%
  mutate(
    # Create synthetic names for customers (in real scenario, would come from customer database)
    customer_name = paste("Customer", CustomerID)
  )

# Join names into transactions
customer_outreach <- transactions_clean %>%
  left_join(customer_names, by = "CustomerID") %>%
  mutate(
    first_name = str_extract(customer_name, "^\\w+"),
    personalized_message = case_when(
      recency_category == "Recent" ~ paste("Hi", first_name, "! Thanks for your recent purchase!"),
      recency_category == "Moderate" ~ paste("Hi", first_name, ", we miss you! Check out our new products."),
      recency_category == "At Risk" ~ paste("Hi", first_name, ", it's been a while! Here's a special offer for you."),
      TRUE ~ NA_character_
    )
  )

cat("Personalized Customer Messages:\n")
customer_outreach %>%
  select(CustomerID, first_name, days_since, personalized_message) %>%
  head(10) %>%
  print()

# Task 6.2: Analyze Transaction Patterns by Weekday
weekday_patterns <- transactions_clean %>%
  group_by(trans_weekday) %>%
  summarise(
    transaction_count = n(),
    total_amount = sum(Amount, na.rm = TRUE),
    avg_amount = mean(Amount, na.rm = TRUE),
    .groups = 'drop'
  ) %>%
  arrange(desc(transaction_count))

cat("Transaction Patterns by Weekday:\n")
print(weekday_patterns)

busiest_day <- weekday_patterns$trans_weekday[1]
cat("\n🔥 Busiest day:", as.character(busiest_day), "\n")

# Task 6.3: Monthly Transaction Analysis
monthly_patterns <- transactions_clean %>%
  group_by(trans_month, trans_month_name) %>%
  summarise(
    transaction_count = n(),
    unique_customers = n_distinct(CustomerID),
    .groups = 'drop'
  ) %>%
  arrange(trans_month)

cat("Monthly Transaction Patterns:\n")
print(monthly_patterns)

# Task 7.1: Create Business Intelligence Dashboard
cat("\n", rep("=", 60), "\n")
cat("         BUSINESS INTELLIGENCE SUMMARY\n")
cat(rep("=", 60), "\n\n")

# Product Analysis
cat("📦 PRODUCT ANALYSIS\n")
cat(rep("─", 30), "\n")
cat("Total products:", nrow(products_clean), "\n")
cat("Wireless products:", sum(products_clean$is_wireless), "\n")
cat("Premium products:", sum(products_clean$is_premium), "\n")
most_common_cat <- products_clean %>%
  count(category_clean) %>%
  arrange(desc(n)) %>%
  slice(1) %>%
  pull(category_clean)
cat("Most common category:", as.character(most_common_cat), "\n")

# Customer Sentiment
cat("\n💬 CUSTOMER SENTIMENT\n")
cat(rep("─", 30), "\n")
cat("Total feedback entries:", nrow(feedback_clean), "\n")
cat("Average sentiment score:", round(mean(feedback_clean$sentiment_score), 2), "\n")
positive_pct <- round(sum(feedback_clean$sentiment_score > 0) / nrow(feedback_clean) * 100, 1)
negative_pct <- round(sum(feedback_clean$sentiment_score < 0) / nrow(feedback_clean) * 100, 1)
cat("Positive reviews:", positive_pct, "%\n")
cat("Negative reviews:", negative_pct, "%\n")

# Transaction Patterns
cat("\n📊 TRANSACTION PATTERNS\n")
cat(rep("─", 30), "\n")
cat("Total transactions:", nrow(transactions_clean), "\n")
earliest <- min(transactions_clean$date_parsed, na.rm = TRUE)
latest <- max(transactions_clean$date_parsed, na.rm = TRUE)
cat("Date range:", format(earliest, "%Y-%m-%d"), "to", format(latest, "%Y-%m-%d"), "\n")
cat("Busiest weekday:", as.character(busiest_day), "\n")
weekend_pct <- round(sum(transactions_clean$is_weekend, na.rm = TRUE) / nrow(transactions_clean) * 100, 1)
cat("Weekend transactions:", weekend_pct, "%\n")

# Customer Recency
cat("\n👥 CUSTOMER RECENCY\n")
cat(rep("─", 30), "\n")
recent_count <- sum(transactions_clean$recency_category == "Recent", na.rm = TRUE)
at_risk_count <- sum(transactions_clean$recency_category == "At Risk", na.rm = TRUE)
cat("Recent customers (< 30 days):", recent_count, "\n")
cat("At-risk customers (> 90 days):", at_risk_count, "\n")
reengagement_pct <- round(at_risk_count / nrow(transactions_clean) * 100, 1)
cat("Needing re-engagement:", reengagement_pct, "%\n")

cat("\n", rep("=", 60), "\n")

# Task 7.2: Identify Top Products by Category
top_categories <- products_clean %>%
  group_by(category_clean) %>%
  summarise(
    product_count = n(),
    .groups = 'drop'
  ) %>%
  arrange(desc(product_count)) %>%
  head(5)

cat("Top Product Categories:\n")
print(top_categories)
```

## Key Adaptations for Version 2 Data

### 1. Column Name Differences
- `Product_Description` instead of `product_name`
- `Feedback_Text` instead of `feedback_text`
- `Transaction_DateTime` instead of `transaction_date`
- `CustomerID` instead of `customer_name`

### 2. Missing Customer Names
Transactions only have CustomerID. Solutions:
- **Option A:** Create synthetic names (shown above)
- **Option B:** Join with feedback table (if it had names)
- **Option C:** Use CustomerID as identifier

### 3. Mixed Date Formats
Must use `parse_date_time()` with multiple format orders:
```r
date_parsed = parse_date_time(
  Transaction_DateTime,
  orders = c("mdy HM", "dmy HMS", "dmy HM", "ymd HMS"),
  quiet = TRUE
)
```

### 4. Data Validation
Always check for parsing failures:
```r
cat("Failed to parse:", sum(is.na(transactions_clean$date_parsed)), "\n")
```

## Grading Criteria for Version 2

Students should be graded on:
1. ✓ Correct use of stringr functions
2. ✓ Correct use of lubridate functions
3. ✓ Handling mixed date formats (parse_date_time or filter approach)
4. ✓ Adapting to missing customer names
5. ✓ Proper date display formatting
6. ✓ Business insights and reflections

Students should NOT be penalized for:
- Using PascalCase column names (that's what the data has)
- Not having customer names in transactions (data doesn't have them)
- Using parse_date_time() instead of ymd() (required for mixed formats)
- Creating workarounds for missing data

## Expected Outputs

With Version 2 data:
- 100 feedback rows
- 150 transaction rows (some may be filtered if dates don't parse)
- 75 product rows
- All customers likely "At Risk" (data from 2024, now 2025)
- No weekend transactions (data only has weekdays)
