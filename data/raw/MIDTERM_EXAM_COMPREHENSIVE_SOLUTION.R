# ============================================================================
# MIDTERM EXAM: Comprehensive R Data Wrangling Assessment - SOLUTION
# ============================================================================
# This solution demonstrates all concepts from Lessons 1-8
# Students should use this as a reference for correct approaches
# ============================================================================

# ============================================================================
# Part 1: R Basics and Data Import (Lesson 1)
# ============================================================================

# Task 1.1: Set Working Directory
# IMPORTANT: Students must set their own path!
# Example for Mac:
setwd("/Users/yourname/GitHub/ai-homework-grader-clean/data")
# Example for Windows:
# setwd("C:/Users/yourname/GitHub/ai-homework-grader-clean/data")

# Verify working directory
cat("Current working directory:", getwd(), "\n")

# Task 1.2: Load Required Packages
library(tidyverse)  # Includes dplyr, tidyr, stringr, ggplot2
library(lubridate)  # For date operations

cat("✅ Packages loaded successfully!\n")

# Task 1.3: Import Datasets
# Note: File paths are relative to working directory
sales_data <- read_csv("processed/company_sales_data.csv")
customers <- read_csv("processed/customers.csv")
products <- read_csv("processed/products.csv")
orders <- read_csv("processed/orders.csv")
order_items <- read_csv("processed/order_items.csv")

# Display import summary
cat("✅ Data imported successfully!\n")
cat("Sales data:", nrow(sales_data), "rows\n")
cat("Customers:", nrow(customers), "rows\n")
cat("Products:", nrow(products), "rows\n")
cat("Orders:", nrow(orders), "rows\n")
cat("Order items:", nrow(order_items), "rows\n")

# ============================================================================
# Part 2: Data Cleaning - Missing Values & Outliers (Lesson 2)
# ============================================================================

# Task 2.1: Check for Missing Values
# Use colSums() with is.na() to count NAs in each column
missing_summary <- colSums(is.na(sales_data))

cat("========== MISSING VALUES SUMMARY ==========\n")
print(missing_summary)
cat("\nTotal missing values:", sum(missing_summary), "\n")

# Task 2.2: Handle Missing Values
# Use na.omit() or complete.cases() to remove rows with ANY missing values
sales_clean <- sales_data %>%
  na.omit()  # Alternative: filter(complete.cases(.))

cat("========== DATA CLEANING RESULTS ==========\n")
cat("Original rows:", nrow(sales_data), "\n")
cat("Cleaned rows:", nrow(sales_clean), "\n")
cat("Rows removed:", nrow(sales_data) - nrow(sales_clean), "\n")

# Task 2.3: Detect Outliers in Revenue
# IQR method: outliers are values < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
Q1 <- quantile(sales_clean$Revenue, 0.25)
Q3 <- quantile(sales_clean$Revenue, 0.75)
IQR_value <- Q3 - Q1
lower_bound <- Q1 - 1.5 * IQR_value
upper_bound <- Q3 + 1.5 * IQR_value

outlier_analysis <- data.frame(
  Metric = c("Q1", "Q3", "IQR", "Lower Bound", "Upper Bound"),
  Value = c(Q1, Q3, IQR_value, lower_bound, upper_bound)
)

cat("========== OUTLIER ANALYSIS ==========\n")
print(outlier_analysis)

# Count outliers
outlier_count <- sum(sales_clean$Revenue < lower_bound | sales_clean$Revenue > upper_bound)
cat("\nNumber of outliers detected:", outlier_count, "\n")

# ============================================================================
# Part 3: Data Transformation Part 1 (Lesson 3)
# ============================================================================

# Task 3.1: Select Specific Columns
sales_summary <- sales_clean %>%
  select(Region, Product_Category, Revenue, Units_Sold, Sale_Date)

cat("========== SELECTED COLUMNS ==========\n")
cat("Columns:", names(sales_summary), "\n")
cat("Rows:", nrow(sales_summary), "\n")
head(sales_summary, 5)

# Task 3.2: Filter High Revenue Sales
high_revenue_sales <- sales_clean %>%
  filter(Revenue > 20000)

cat("========== HIGH REVENUE SALES ==========\n")
cat("Total high revenue transactions:", nrow(high_revenue_sales), "\n")
cat("Total revenue from these sales: $", sum(high_revenue_sales$Revenue), "\n")

# Task 3.3: Sort by Revenue
top_sales <- sales_clean %>%
  arrange(desc(Revenue)) %>%
  head(10)

cat("========== TOP 10 SALES ==========\n")
print(top_sales %>% select(Region, Product_Category, Revenue, Units_Sold))

# Task 3.4: Chain Multiple Operations
regional_top_sales <- sales_clean %>%
  filter(Revenue > 15000) %>%
  select(Region, Product_Category, Revenue) %>%
  arrange(Region, desc(Revenue)) %>%
  head(15)

cat("========== REGIONAL TOP SALES ==========\n")
print(regional_top_sales)

# ============================================================================
# Part 4: Data Transformation Part 2 (Lesson 4)
# ============================================================================

# Task 4.1: Create Calculated Columns
sales_enhanced <- sales_clean %>%
  mutate(
    revenue_per_unit = Revenue / Units_Sold,
    high_value = ifelse(Revenue > 20000, "Yes", "No")
  )

cat("========== ENHANCED SALES DATA ==========\n")
cat("New columns added: revenue_per_unit, high_value\n")
head(sales_enhanced %>% select(Revenue, Units_Sold, revenue_per_unit, high_value), 5)

# Task 4.2: Calculate Overall Summary Statistics
overall_summary <- sales_enhanced %>%
  summarize(
    total_revenue = sum(Revenue),
    avg_revenue = mean(Revenue),
    total_units = sum(Units_Sold),
    transaction_count = n()
  )

cat("========== OVERALL SUMMARY ==========\n")
print(overall_summary)

# Task 4.3: Regional Performance Analysis
regional_summary <- sales_enhanced %>%
  group_by(Region) %>%
  summarize(
    total_revenue = sum(Revenue),
    avg_revenue = mean(Revenue),
    transaction_count = n()
  ) %>%
  arrange(desc(total_revenue))

cat("========== REGIONAL SUMMARY ==========\n")
print(regional_summary)

# Task 4.4: Product Category Analysis
category_summary <- sales_enhanced %>%
  group_by(Product_Category) %>%
  summarize(
    total_revenue = sum(Revenue),
    avg_revenue = mean(Revenue),
    transaction_count = n()
  ) %>%
  arrange(desc(total_revenue))

cat("========== CATEGORY SUMMARY ==========\n")
print(category_summary)

# ============================================================================
# Part 5: Data Reshaping with tidyr (Lesson 5)
# ============================================================================

# Task 5.1: Create Wide Format Data (already done)
region_category_revenue <- sales_enhanced %>%
  group_by(Region, Product_Category) %>%
  summarize(total_revenue = sum(Revenue), .groups = 'drop')

cat("========== REGION-CATEGORY DATA (LONG FORMAT) ==========\n")
print(head(region_category_revenue, 10))

# Task 5.2: Reshape to Wide Format
revenue_wide <- region_category_revenue %>%
  pivot_wider(
    names_from = Product_Category,
    values_from = total_revenue
  )

cat("========== REVENUE DATA (WIDE FORMAT) ==========\n")
print(revenue_wide)

# Task 5.3: Reshape Back to Long Format
revenue_long <- revenue_wide %>%
  pivot_longer(
    cols = -Region,  # All columns except Region
    names_to = "Product_Category",
    values_to = "revenue"
  )

cat("========== REVENUE DATA (BACK TO LONG FORMAT) ==========\n")
print(head(revenue_long, 10))

# ============================================================================
# Part 6: Combining Datasets with Joins (Lesson 6)
# ============================================================================

# Task 6.1: Join Customers and Orders
customer_orders <- customers %>%
  left_join(orders, by = "CustomerID")

cat("========== CUSTOMER ORDERS ==========\n")
cat("Total rows:", nrow(customer_orders), "\n")
cat("Columns:", ncol(customer_orders), "\n")

# Task 6.2: Join Orders and Order Items
orders_with_items <- orders %>%
  inner_join(order_items, by = "OrderID")

cat("========== ORDERS WITH ITEMS ==========\n")
cat("Total rows:", nrow(orders_with_items), "\n")
head(orders_with_items, 5)

# ============================================================================
# Part 7: String Manipulation & Date/Time Operations (Lesson 7)
# ============================================================================

# Task 7.1: Clean Text Data
sales_enhanced <- sales_enhanced %>%
  mutate(
    region_clean = str_trim(Region) %>% str_to_title(),
    category_clean = str_trim(Product_Category) %>% str_to_title()
  )

cat("========== CLEANED TEXT DATA ==========\n")
head(sales_enhanced %>% select(Region, region_clean, Product_Category, category_clean), 5)

# Task 7.2: Parse Dates and Extract Components
sales_enhanced <- sales_enhanced %>%
  mutate(
    date_parsed = mdy(Sale_Date),  # Use ymd(), mdy(), or dmy() based on format
    sale_month = month(date_parsed, label = TRUE, abbr = FALSE),
    sale_weekday = wday(date_parsed, label = TRUE, abbr = FALSE)
  )

cat("========== DATE COMPONENTS ==========\n")
head(sales_enhanced %>% select(Sale_Date, date_parsed, sale_month, sale_weekday), 5)

# ============================================================================
# Part 8: Advanced Wrangling & Business Intelligence (Lesson 8)
# ============================================================================

# Task 8.1: Create Performance Categories
sales_enhanced <- sales_enhanced %>%
  mutate(
    performance_tier = case_when(
      Revenue > 25000 ~ "High",
      Revenue > 15000 ~ "Medium",
      TRUE ~ "Low"  # Default case
    )
  )

cat("========== PERFORMANCE TIERS ==========\n")
table(sales_enhanced$performance_tier)

# Task 8.2: Calculate Business KPIs
business_kpis <- sales_enhanced %>%
  summarize(
    total_revenue = sum(Revenue),
    total_transactions = n(),
    avg_transaction_value = mean(Revenue),
    high_value_pct = sum(high_value == "Yes") / n() * 100
  )

cat("========== BUSINESS KPIs ==========\n")
print(business_kpis)

# ============================================================================
# REFLECTION QUESTIONS - SAMPLE ANSWERS
# ============================================================================

cat("\n========== REFLECTION QUESTIONS ==========\n\n")

cat("Question 9.1: Data Cleaning Impact\n")
cat("Answer: Handling missing values and outliers ensures our analysis is based on\n")
cat("complete and reliable data. Missing values can skew averages and totals, while\n")
cat("outliers can distort trends. Data cleaning is crucial because business decisions\n")
cat("based on flawed data can lead to poor outcomes. For example, if we didn't remove\n")
cat("missing revenue values, our total revenue calculation would be incorrect.\n\n")

cat("Question 9.2: Grouped Analysis Value\n")
cat("Answer: Grouped analysis revealed that different regions and product categories\n")
cat("perform very differently. The raw data showed individual transactions, but grouping\n")
cat("by region showed which markets are strongest. Businesses use this to allocate\n")
cat("resources, target marketing, and identify growth opportunities. For example, if\n")
cat("the West region has highest revenue, we might invest more in that market.\n\n")

cat("Question 9.3: Data Reshaping Purpose\n")
cat("Answer: Wide format is useful for comparison tables and reports (e.g., comparing\n")
cat("product categories side-by-side by region). Long format is better for analysis\n")
cat("and visualization (e.g., creating charts with ggplot2). Business scenario: A\n")
cat("dashboard might show wide format for executives to scan quickly, while analysts\n")
cat("use long format for statistical modeling.\n\n")

cat("Question 9.4: Joining Datasets\n")
cat("Answer: left_join() keeps all rows from the left table and matches from the right\n")
cat("(useful when you want to keep all customers even if they haven't ordered).\n")
cat("inner_join() only keeps rows that match in both tables (useful when you only want\n")
cat("customers who have actually made purchases). Use left_join() for customer analysis\n")
cat("(including inactive customers) and inner_join() for transaction analysis.\n\n")

cat("Question 9.5: Skills Integration\n")
cat("Answer: I think group_by() with summarize() is most valuable because it transforms\n")
cat("raw transactional data into actionable business metrics. Every business needs to\n")
cat("aggregate data by categories (products, regions, time periods) to understand\n")
cat("performance. This skill enables KPI dashboards, performance reports, and strategic\n")
cat("decision-making. All other skills support this core analytical capability.\n\n")

cat("========== SOLUTION COMPLETE ==========\n")
cat("This solution demonstrates all concepts from Lessons 1-8.\n")
cat("Students should understand the logic, not just copy the code.\n")
