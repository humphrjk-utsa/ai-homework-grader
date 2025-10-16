# ============================================================================
# CELL 1: SETUP
# ============================================================================
# Load necessary packages
library(tidyverse)
library(lubridate)

# Set seed for reproducibility
set.seed(123)
setwd("/Users/humphrjk/GitHub/ai-homework-grader-clean/data/")

cat("Packages loaded successfully!\n")
cat("Ready for advanced data wrangling!\n")


# ============================================================================
# CELL 2: LOAD DATA
# ============================================================================
# Load the sales data from CSV
# This dataset contains 25 transactions from Q1 2024
sales_data <- read_csv("raw/lesson8_sales_data.csv")

cat("✅ Sales data loaded successfully!\n")
cat("   Rows:", nrow(sales_data), "\n")
cat("   Date range:", min(sales_data$OrderDate), "to", max(sales_data$OrderDate), "\n\n")

cat("📊 Dataset Structure:\n")
cat("   • OrderID: Unique transaction identifier\n")
cat("   • OrderDate: Transaction date (Q1 2024)\n")
cat("   • Product: Laptop, Mouse, Keyboard, Monitor, Webcam, Headphones\n")
cat("   • Sales: Transaction amount ($)\n")
cat("   • Quantity: Number of items\n")
cat("   • Region: North, South, East, West\n")
cat("   • Category: Electronics, Peripherals\n")
cat("   • CustomerType: New, Returning, VIP\n\n")

print(head(sales_data, 10))


# ============================================================================
# CELL 3: COMPLEX CHAINED OPERATIONS - REGIONAL ANALYSIS
# ============================================================================
# BUSINESS USE CASE: Regional performance analysis for strategic planning
#
# Problem: Need to understand which region-category combinations perform best
# Impact: Can't allocate resources effectively or identify growth opportunities
# Solution: Build a complex pipeline that filters, calculates, groups, and analyzes

regional_analysis <- sales_data %>%
  # Step 1: FILTER - Remove low-value transactions
  # Why: Focus on significant sales, reduce noise
  # Business rule: Only analyze sales > $100
  filter(Sales > 100) %>%
  
  # Step 2: MUTATE - Calculate revenue and add time dimensions
  # Revenue = Sales * Quantity (total transaction value)
  # Time dimensions enable temporal analysis
  mutate(
    Revenue = Sales * Quantity,
    Month = month(OrderDate, label = TRUE),  # "Jan", "Feb", "Mar"
    Quarter = quarter(OrderDate)              # 1 for Q1
  ) %>%
  
  # Step 3: GROUP - Define analysis dimensions
  # Why: We want metrics BY region AND category
  # This creates groups for each unique combination
  group_by(Region, Category) %>%
  
  # Step 4: SUMMARIZE - Calculate key metrics for each group
  # These are the KPIs that matter to the business
  summarize(
    Total_Revenue = sum(Revenue),        # Total $ generated
    Avg_Sale = mean(Sales),              # Average transaction size
    Order_Count = n(),                   # Number of transactions
    Total_Units = sum(Quantity),         # Total items sold
    .groups = 'drop'                     # Remove grouping after summarize
  ) %>%
  
  # Step 5: MUTATE - Calculate revenue share (% of total)
  # Why: Executives want to see percentages, not just absolute numbers
  # sum(Total_Revenue) calculates across all rows
  mutate(
    Revenue_Share = (Total_Revenue / sum(Total_Revenue)) * 100
  ) %>%
  
  # Step 6: ARRANGE - Sort by revenue (highest first)
  # Why: Put most important results at the top
  # desc() means descending order
  arrange(desc(Total_Revenue))

cat("📊 REGIONAL PERFORMANCE ANALYSIS\n")
cat("(Complex Pipeline: Filter → Mutate → Group → Summarize → Mutate → Arrange)\n\n")

print(regional_analysis)

cat("\n💡 Business Insights:\n")
cat("  • Top region-category combinations drive", 
    round(sum(head(regional_analysis$Revenue_Share, 3)), 1), "% of revenue\n")
cat("  • Use this to allocate marketing budget\n")
cat("  • Identify underperforming combinations for improvement\n")


# ============================================================================
# CELL 4: ADVANCED CONDITIONAL LOGIC - CUSTOMER SEGMENTATION
# ============================================================================
# BUSINESS USE CASE: Multi-dimensional customer value scoring
#
# Problem: Need to segment customers for targeted marketing and service levels
# Impact: Can't personalize experience, missing revenue from high-value customers
# Solution: Use case_when() to create sophisticated segmentation logic

sales_classified <- sales_data %>%
  mutate(
    # Calculate total revenue (will use for classification)
    Revenue = Sales * Quantity,
    
    # CLASSIFICATION 1: Sales Tier (simple, single condition)
    # Purpose: Quick categorization of transaction size
    Sales_Tier = case_when(
      Sales < 200 ~ "Low",           # Small transactions
      Sales >= 200 & Sales < 800 ~ "Medium",  # Mid-size transactions
      Sales >= 800 ~ "High",         # Large transactions
      TRUE ~ "Unknown"               # Safety net (should never happen)
    ),
    
    # CLASSIFICATION 2: Customer Value Score (complex, multiple factors)
    # Purpose: Identify most valuable customers for VIP treatment
    # Logic: Combines customer type AND revenue
    Value_Score = case_when(
      # Platinum: VIP customers with high revenue
      # & means AND (both conditions must be true)
      CustomerType == "VIP" & Revenue > 1000 ~ "Platinum",
      
      # Gold: Either VIP OR high revenue (but not both)
      # | means OR (at least one condition must be true)
      CustomerType == "VIP" | Revenue > 1000 ~ "Gold",
      
      # Silver: Returning customers with decent revenue
      CustomerType == "Returning" & Revenue > 500 ~ "Silver",
      
      # Bronze: Everyone else (new customers, low revenue)
      TRUE ~ "Bronze"
    ),
    
    # CLASSIFICATION 3: Follow-up Priority (derived from Value_Score)
    # Purpose: Prioritize sales team outreach
    # %in% checks if value is in a vector
    Follow_Up_Priority = case_when(
      Value_Score %in% c("Platinum", "Gold") ~ "High",    # Top customers
      Value_Score == "Silver" ~ "Medium",                  # Good customers
      TRUE ~ "Low"                                         # Standard customers
    )
  )

cat("🎯 CUSTOMER SEGMENTATION WITH case_when()\n\n")

# Show sample of classifications
sales_classified %>%
  select(OrderID, Sales, Revenue, Sales_Tier, CustomerType, Value_Score, Follow_Up_Priority) %>%
  head(10) %>%
  print()

cat("\n💡 Business Logic Explained:\n")
cat("  Platinum: VIP + Revenue > $1000 (top 5-10% of customers)\n")
cat("  Gold: VIP OR Revenue > $1000 (high-value segment)\n")
cat("  Silver: Returning + Revenue > $500 (loyal customers)\n")
cat("  Bronze: All others (growth potential)\n")


# ============================================================================
# CELL 5: DATA VALIDATION - MISSING VALUES CHECK
# ============================================================================
# BUSINESS USE CASE: Automated data quality checks
#
# Problem: Need to ensure data quality before analysis
# Impact: Bad data leads to wrong decisions and wasted time
# Solution: Implement systematic validation checks

# CHECK 1: Missing Values
# Why: Missing data can skew calculations and cause errors
missing_check <- sales_data %>%
  summarize(
    Missing_Sales = sum(is.na(Sales)),
    Missing_Quantity = sum(is.na(Quantity)),
    Missing_OrderDate = sum(is.na(OrderDate)),
    Total_Rows = n(),
    # Calculate percentage missing
    Pct_Missing_Sales = (Missing_Sales / Total_Rows) * 100
  )

cat("✅ MISSING VALUE CHECK:\n\n")
print(missing_check)

if (sum(missing_check[1:3]) == 0) {
  cat("\n✅ No missing values detected!\n")
} else {
  cat("\n⚠️  Missing values found - investigate before analysis!\n")
}

cat("\n💡 What to do if missing values found:\n")
cat("  • < 5% missing: Consider imputation or removal\n")
cat("  • 5-20% missing: Investigate pattern, may indicate systematic issue\n")
cat("  • > 20% missing: Serious data quality problem, contact data source\n")


# ============================================================================
# CELL 6: DATA VALIDATION - BUSINESS RULES CHECK
# ============================================================================
# CHECK 2: Business Rule Validation
# Why: Ensure data follows business logic (no negative sales, valid dates, etc.)

business_rules_check <- sales_data %>%
  summarize(
    Negative_Sales = sum(Sales < 0),           # Sales should be positive
    Zero_Quantity = sum(Quantity <= 0),        # Quantity should be > 0
    Future_Dates = sum(OrderDate > today()),   # Dates shouldn't be in future
    Invalid_Records = Negative_Sales + Zero_Quantity + Future_Dates
  )

cat("✅ BUSINESS RULES CHECK:\n\n")
print(business_rules_check)

if (business_rules_check$Invalid_Records == 0) {
  cat("\n✅ All business rules passed!\n")
} else {
  cat("\n⚠️  Business rule violations found!\n")
}

cat("\n💡 Business Rules:\n")
cat("  • Sales must be positive (no negative amounts)\n")
cat("  • Quantity must be > 0 (can't sell 0 items)\n")
cat("  • Dates must be in the past (no future transactions)\n")


# ============================================================================
# CELL 7: SUMMARY STATISTICS AND KPIs
# ============================================================================
# BUSINESS USE CASE: Executive dashboard KPIs
#
# Problem: Executives need high-level metrics at a glance
# Impact: Can't track performance or make quick decisions
# Solution: Calculate key performance indicators (KPIs)

kpi_summary <- sales_data %>%
  mutate(Revenue = Sales * Quantity) %>%
  summarize(
    # Volume Metrics
    Total_Transactions = n(),
    Total_Units_Sold = sum(Quantity),
    
    # Revenue Metrics
    Total_Revenue = sum(Revenue),
    Avg_Transaction_Value = mean(Revenue),
    
    # Customer Metrics
    Unique_Customers = n_distinct(CustomerType),
    VIP_Transactions = sum(CustomerType == "VIP"),
    VIP_Percentage = (VIP_Transactions / Total_Transactions) * 100,
    
    # Product Metrics
    Unique_Products = n_distinct(Product),
    Avg_Units_Per_Transaction = mean(Quantity)
  )

cat("📊 EXECUTIVE KPI DASHBOARD\n")
cat("="*60, "\n\n")

cat("💰 REVENUE METRICS:\n")
cat("   Total Revenue: $", format(kpi_summary$Total_Revenue, big.mark=","), "\n")
cat("   Avg Transaction: $", round(kpi_summary$Avg_Transaction_Value, 2), "\n\n")

cat("📦 VOLUME METRICS:\n")
cat("   Total Transactions:", kpi_summary$Total_Transactions, "\n")
cat("   Total Units Sold:", kpi_summary$Total_Units_Sold, "\n")
cat("   Avg Units/Transaction:", round(kpi_summary$Avg_Units_Per_Transaction, 1), "\n\n")

cat("👥 CUSTOMER METRICS:\n")
cat("   VIP Transactions:", kpi_summary$VIP_Transactions, 
    "(", round(kpi_summary$VIP_Percentage, 1), "%)\n\n")

cat("🎯 KEY INSIGHTS:\n")
cat("   • Focus on VIP customers - they drive premium transactions\n")
cat("   • Average transaction value indicates pricing strategy effectiveness\n")
cat("   • Units per transaction shows cross-selling success\n")


# ============================================================================
# CELL 8: FINAL SUMMARY - WHAT WE LEARNED
# ============================================================================
cat("\n🎓 LESSON 8 SUMMARY: ADVANCED DATA WRANGLING\n")
cat("="*60, "\n\n")

cat("✅ Skills Mastered:\n")
cat("   1. Complex chained operations (6+ steps in one pipeline)\n")
cat("   2. Advanced conditional logic with case_when()\n")
cat("   3. Data validation and quality checks\n")
cat("   4. KPI calculation and business metrics\n")
cat("   5. Professional code documentation\n\n")

cat("💼 Business Applications:\n")
cat("   • Regional performance analysis for resource allocation\n")
cat("   • Customer segmentation for targeted marketing\n")
cat("   • Data quality assurance for reliable insights\n")
cat("   • Executive reporting and KPI tracking\n\n")

cat("🚀 Next Steps:\n")
cat("   • Apply these techniques to your own datasets\n")
cat("   • Combine with visualization (ggplot2) for reports\n")
cat("   • Build automated analysis pipelines\n")
cat("   • Create reusable functions for common tasks\n\n")

cat("🎯 You're now ready for professional data analysis!\n")
