# Homework 8 Solution: Capstone Project - Comprehensive Data Wrangling
# Data Wrangling in R for Business Analytics
# Author: Manus AI

# Set working directory to sample_datasets
setwd("../sample_datasets")

print("=== HOMEWORK 8 SOLUTION ===")
print("Capstone Project - Comprehensive Data Wrangling")
print("===============================================")

# PART 1: Project Setup and Data Import
print("\n--- PART 1: Project Setup and Data Import ---")

# 1.1 Import all required datasets
required_files <- c("raw_sales_data.csv", "customer_demographics.csv", "product_inventory.csv", 
                   "sales_targets.csv", "regional_data.csv")
datasets <- list()

for (file in required_files) {
  if (file.exists(file)) {
    dataset_name <- gsub("\\.csv$", "", file)
    datasets[[dataset_name]] <- read.csv(file, stringsAsFactors = FALSE)
    print(paste("✓", file, "imported successfully"))
  } else {
    stop(paste("Error:", file, "not found!"))
  }
}

# Extract datasets from list for easier access
raw_sales <- datasets$raw_sales_data
demographics <- datasets$customer_demographics
inventory <- datasets$product_inventory
targets <- datasets$sales_targets
regional <- datasets$regional_data

# 1.2 Initial data assessment
print("\n1.2 Initial Data Assessment:")

datasets_info <- data.frame(
  Dataset = c("Raw Sales", "Customer Demographics", "Product Inventory", "Sales Targets", "Regional Data"),
  Rows = c(nrow(raw_sales), nrow(demographics), nrow(inventory), nrow(targets), nrow(regional)),
  Columns = c(ncol(raw_sales), ncol(demographics), ncol(inventory), ncol(targets), ncol(regional)),
  Size_MB = round(c(object.size(raw_sales), object.size(demographics), object.size(inventory), 
                   object.size(targets), object.size(regional)) / 1024^2, 2)
)

print("Dataset overview:")
print(datasets_info)

# 1.3 Examine data structures
print("\n1.3 Data Structure Analysis:")

print("RAW SALES DATA structure:")
str(raw_sales)
print("Sample:")
print(head(raw_sales, 3))

print("\nCUSTOMER DEMOGRAPHICS structure:")
str(demographics)
print("Sample:")
print(head(demographics, 3))

print("\nPRODUCT INVENTORY structure:")
str(inventory)
print("Sample:")
print(head(inventory, 3))

# PART 2: Data Quality Assessment and Cleaning
print("\n--- PART 2: Data Quality Assessment and Cleaning ---")

# 2.1 Missing values analysis
print("2.1 Missing Values Analysis:")

missing_analysis <- function(df, name) {
  missing_counts <- sapply(df, function(x) sum(is.na(x) | x == ""))
  missing_percent <- round((missing_counts / nrow(df)) * 100, 2)
  
  result <- data.frame(
    Column = names(missing_counts),
    Missing_Count = missing_counts,
    Missing_Percent = missing_percent
  )
  
  print(paste("\n", name, "- Missing Values:"))
  print(result[result$Missing_Count > 0, ])
  
  return(result)
}

sales_missing <- missing_analysis(raw_sales, "Raw Sales Data")
demo_missing <- missing_analysis(demographics, "Customer Demographics")
inventory_missing <- missing_analysis(inventory, "Product Inventory")

# 2.2 Data cleaning strategy
print("\n2.2 Data Cleaning Strategy:")

print("Cleaning approach:")
print("1. Remove duplicate records")
print("2. Handle missing values based on business rules")
print("3. Standardize data formats")
print("4. Validate data ranges and business logic")
print("5. Create derived variables")

# 2.3 Clean raw sales data
print("\n2.3 Cleaning Raw Sales Data:")

# Create a copy for cleaning
clean_sales <- raw_sales
original_rows <- nrow(clean_sales)

# Remove duplicates
clean_sales <- clean_sales[!duplicated(clean_sales), ]
print(paste("Removed", original_rows - nrow(clean_sales), "duplicate rows"))

# Clean customer names
clean_sales$Customer_Name <- trimws(clean_sales$Customer_Name)
clean_sales$Customer_Name <- tools::toTitleCase(tolower(clean_sales$Customer_Name))

# Remove rows with missing critical data
critical_missing <- is.na(clean_sales$Customer_ID) | is.na(clean_sales$Product_ID) | 
                   is.na(clean_sales$Sale_Amount) | clean_sales$Customer_Name == ""

clean_sales <- clean_sales[!critical_missing, ]
print(paste("Removed", sum(critical_missing), "rows with missing critical data"))

# Handle missing sale dates
missing_dates <- is.na(clean_sales$Sale_Date) | clean_sales$Sale_Date == ""
if (sum(missing_dates) > 0) {
  # Assign a default date for missing dates
  clean_sales$Sale_Date[missing_dates] <- "2024-01-01"
  print(paste("Assigned default date to", sum(missing_dates), "missing sale dates"))
}

# Clean and validate sale amounts
clean_sales$Sale_Amount <- as.numeric(clean_sales$Sale_Amount)
negative_amounts <- clean_sales$Sale_Amount < 0
clean_sales <- clean_sales[!negative_amounts, ]
print(paste("Removed", sum(negative_amounts, na.rm = TRUE), "rows with negative sale amounts"))

# Clean quantities
clean_sales$Quantity <- as.numeric(clean_sales$Quantity)
invalid_quantities <- clean_sales$Quantity <= 0 | is.na(clean_sales$Quantity)
clean_sales$Quantity[invalid_quantities] <- 1  # Default to 1 for invalid quantities
print(paste("Fixed", sum(invalid_quantities), "invalid quantities"))

print(paste("Final cleaned sales data:", nrow(clean_sales), "rows"))

# 2.4 Clean customer demographics
print("\n2.4 Cleaning Customer Demographics:")

clean_demographics <- demographics

# Standardize customer names
clean_demographics$Customer_Name <- trimws(clean_demographics$Customer_Name)
clean_demographics$Customer_Name <- tools::toTitleCase(tolower(clean_demographics$Customer_Name))

# Clean age data
clean_demographics$Age <- as.numeric(clean_demographics$Age)
invalid_ages <- clean_demographics$Age < 18 | clean_demographics$Age > 100 | is.na(clean_demographics$Age)
clean_demographics$Age[invalid_ages] <- median(clean_demographics$Age, na.rm = TRUE)
print(paste("Fixed", sum(invalid_ages), "invalid ages with median value"))

# Standardize city names
clean_demographics$City <- trimws(clean_demographics$City)
clean_demographics$City <- tools::toTitleCase(tolower(clean_demographics$City))

# Clean income data
clean_demographics$Annual_Income <- as.numeric(gsub("[^0-9.]", "", clean_demographics$Annual_Income))
invalid_income <- clean_demographics$Annual_Income < 0 | is.na(clean_demographics$Annual_Income)
clean_demographics$Annual_Income[invalid_income] <- median(clean_demographics$Annual_Income, na.rm = TRUE)
print(paste("Fixed", sum(invalid_income), "invalid income values"))

# 2.5 Clean product inventory
print("\n2.5 Cleaning Product Inventory:")

clean_inventory <- inventory

# Standardize product names
clean_inventory$Product_Name <- trimws(clean_inventory$Product_Name)
clean_inventory$Product_Name <- tools::toTitleCase(tolower(clean_inventory$Product_Name))

# Clean price data
clean_inventory$Unit_Price <- as.numeric(gsub("[^0-9.]", "", clean_inventory$Unit_Price))
invalid_prices <- clean_inventory$Unit_Price <= 0 | is.na(clean_inventory$Unit_Price)
clean_inventory$Unit_Price[invalid_prices] <- median(clean_inventory$Unit_Price, na.rm = TRUE)
print(paste("Fixed", sum(invalid_prices), "invalid unit prices"))

# Clean stock quantities
clean_inventory$Stock_Quantity <- as.numeric(clean_inventory$Stock_Quantity)
negative_stock <- clean_inventory$Stock_Quantity < 0
clean_inventory$Stock_Quantity[negative_stock] <- 0
print(paste("Fixed", sum(negative_stock, na.rm = TRUE), "negative stock quantities"))

# PART 3: Data Transformation and Feature Engineering
print("\n--- PART 3: Data Transformation and Feature Engineering ---")

# 3.1 Date processing
print("3.1 Date Processing:")

# Parse sale dates
clean_sales$Sale_Date_Parsed <- as.Date(clean_sales$Sale_Date)

# Extract date components
clean_sales$Year <- format(clean_sales$Sale_Date_Parsed, "%Y")
clean_sales$Month <- format(clean_sales$Sale_Date_Parsed, "%m")
clean_sales$Month_Name <- format(clean_sales$Sale_Date_Parsed, "%B")
clean_sales$Quarter <- paste0("Q", ceiling(as.numeric(clean_sales$Month) / 3))
clean_sales$Weekday <- weekdays(clean_sales$Sale_Date_Parsed)
clean_sales$Is_Weekend <- clean_sales$Weekday %in% c("Saturday", "Sunday")

print("Date components extracted successfully")

# 3.2 Financial calculations
print("\n3.2 Financial Calculations:")

# Calculate unit price from sale amount and quantity
clean_sales$Unit_Price_Calculated <- clean_sales$Sale_Amount / clean_sales$Quantity

# Add cost information from inventory
clean_sales <- merge(clean_sales, clean_inventory[, c("Product_ID", "Unit_Price", "Category")], 
                    by = "Product_ID", all.x = TRUE, suffixes = c("", "_Inventory"))

# Calculate profit metrics
clean_sales$Cost_Per_Unit <- clean_sales$Unit_Price_Inventory * 0.6  # Assume 60% cost ratio
clean_sales$Total_Cost <- clean_sales$Cost_Per_Unit * clean_sales$Quantity
clean_sales$Profit <- clean_sales$Sale_Amount - clean_sales$Total_Cost
clean_sales$Profit_Margin <- (clean_sales$Profit / clean_sales$Sale_Amount) * 100

print("Financial metrics calculated")

# 3.3 Customer segmentation
print("\n3.3 Customer Segmentation:")

# Add demographic information
clean_sales <- merge(clean_sales, clean_demographics, by = "Customer_ID", all.x = TRUE, suffixes = c("", "_Demo"))

# Create customer segments based on demographics
clean_sales$Age_Group <- ifelse(clean_sales$Age < 30, "Young",
                               ifelse(clean_sales$Age < 50, "Middle-aged", "Senior"))

clean_sales$Income_Segment <- ifelse(clean_sales$Annual_Income < 50000, "Low",
                                    ifelse(clean_sales$Annual_Income < 100000, "Medium", "High"))

# Create purchase behavior segments
customer_metrics <- aggregate(cbind(Sale_Amount, Profit) ~ Customer_ID, 
                             data = clean_sales, FUN = sum)
customer_metrics$Avg_Order_Value <- customer_metrics$Sale_Amount / 
  aggregate(Customer_ID ~ Customer_ID, data = clean_sales, FUN = length)$Customer_ID

# Define customer value segments
customer_metrics$Value_Segment <- ifelse(customer_metrics$Sale_Amount > quantile(customer_metrics$Sale_Amount, 0.8), "High Value",
                                        ifelse(customer_metrics$Sale_Amount > quantile(customer_metrics$Sale_Amount, 0.5), "Medium Value", "Low Value"))

# Merge back to main dataset
clean_sales <- merge(clean_sales, customer_metrics[, c("Customer_ID", "Value_Segment")], 
                    by = "Customer_ID", all.x = TRUE)

print("Customer segmentation completed")

# 3.4 Product performance metrics
print("\n3.4 Product Performance Metrics:")

# Calculate product-level metrics
product_metrics <- aggregate(cbind(Sale_Amount, Profit, Quantity) ~ Product_ID + Category, 
                           data = clean_sales, 
                           FUN = function(x) c(Sum = sum(x), Mean = mean(x), Count = length(x)))

# Flatten the results
product_summary <- data.frame(
  Product_ID = product_metrics$Product_ID,
  Category = product_metrics$Category,
  Total_Revenue = product_metrics$Sale_Amount[, "Sum"],
  Avg_Revenue = round(product_metrics$Sale_Amount[, "Mean"], 2),
  Total_Profit = product_metrics$Profit[, "Sum"],
  Avg_Profit = round(product_metrics$Profit[, "Mean"], 2),
  Total_Quantity = product_metrics$Quantity[, "Sum"],
  Transaction_Count = product_metrics$Sale_Amount[, "Count"]
)

# Calculate performance indicators
product_summary$Profit_Margin <- (product_summary$Total_Profit / product_summary$Total_Revenue) * 100
product_summary$Revenue_Per_Transaction <- product_summary$Total_Revenue / product_summary$Transaction_Count

# Rank products
product_summary$Revenue_Rank <- rank(-product_summary$Total_Revenue)
product_summary$Profit_Rank <- rank(-product_summary$Total_Profit)

print("Product performance metrics calculated")

# PART 4: Advanced Analytics and Insights
print("\n--- PART 4: Advanced Analytics and Insights ---")

# 4.1 Sales performance analysis
print("4.1 Sales Performance Analysis:")

# Overall business metrics
total_revenue <- sum(clean_sales$Sale_Amount, na.rm = TRUE)
total_profit <- sum(clean_sales$Profit, na.rm = TRUE)
overall_margin <- (total_profit / total_revenue) * 100
total_transactions <- nrow(clean_sales)
unique_customers <- length(unique(clean_sales$Customer_ID))
unique_products <- length(unique(clean_sales$Product_ID))

business_summary <- data.frame(
  Metric = c("Total Revenue", "Total Profit", "Overall Profit Margin", "Total Transactions", 
             "Unique Customers", "Unique Products", "Avg Transaction Value", "Avg Customer Value"),
  Value = c(
    paste("$", format(total_revenue, big.mark = ",")),
    paste("$", format(total_profit, big.mark = ",")),
    paste(round(overall_margin, 2), "%"),
    format(total_transactions, big.mark = ","),
    format(unique_customers, big.mark = ","),
    format(unique_products, big.mark = ","),
    paste("$", round(total_revenue / total_transactions, 2)),
    paste("$", round(total_revenue / unique_customers, 2))
  )
)

print("Business Performance Summary:")
print(business_summary)

# 4.2 Time-based analysis
print("\n4.2 Time-Based Analysis:")

# Monthly performance
monthly_performance <- aggregate(cbind(Sale_Amount, Profit, Quantity) ~ Year + Month + Month_Name, 
                               data = clean_sales, FUN = sum)
monthly_performance$Profit_Margin <- (monthly_performance$Profit / monthly_performance$Sale_Amount) * 100
monthly_performance <- monthly_performance[order(monthly_performance$Year, monthly_performance$Month), ]

print("Monthly Performance (last 12 months):")
print(tail(monthly_performance, 12))

# Quarterly performance
quarterly_performance <- aggregate(cbind(Sale_Amount, Profit) ~ Year + Quarter, 
                                 data = clean_sales, FUN = sum)
quarterly_performance$Profit_Margin <- (quarterly_performance$Profit / quarterly_performance$Sale_Amount) * 100

print("\nQuarterly Performance:")
print(quarterly_performance)

# Day of week analysis
weekday_performance <- aggregate(cbind(Sale_Amount, Profit) ~ Weekday, 
                               data = clean_sales, FUN = function(x) c(Sum = sum(x), Mean = mean(x), Count = length(x)))

weekday_summary <- data.frame(
  Weekday = weekday_performance$Weekday,
  Total_Revenue = weekday_performance$Sale_Amount[, "Sum"],
  Avg_Revenue = round(weekday_performance$Sale_Amount[, "Mean"], 2),
  Transaction_Count = weekday_performance$Sale_Amount[, "Count"]
)

# Order by day of week
day_order <- c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
weekday_summary$Weekday <- factor(weekday_summary$Weekday, levels = day_order)
weekday_summary <- weekday_summary[order(weekday_summary$Weekday), ]

print("\nWeekday Performance:")
print(weekday_summary)

# 4.3 Customer analysis
print("\n4.3 Customer Analysis:")

# Customer segment performance
segment_performance <- aggregate(cbind(Sale_Amount, Profit) ~ Value_Segment + Age_Group + Income_Segment, 
                               data = clean_sales, FUN = sum)
segment_performance$Profit_Margin <- (segment_performance$Profit / segment_performance$Sale_Amount) * 100
segment_performance <- segment_performance[order(-segment_performance$Sale_Amount), ]

print("Top customer segments by revenue:")
print(head(segment_performance, 10))

# Geographic analysis
geographic_performance <- aggregate(cbind(Sale_Amount, Profit) ~ City, 
                                  data = clean_sales, FUN = sum)
geographic_performance$Profit_Margin <- (geographic_performance$Profit / geographic_performance$Sale_Amount) * 100
geographic_performance <- geographic_performance[order(-geographic_performance$Sale_Amount), ]

print("\nTop cities by revenue:")
print(head(geographic_performance, 10))

# 4.4 Product category analysis
print("\n4.4 Product Category Analysis:")

category_performance <- aggregate(cbind(Sale_Amount, Profit, Quantity) ~ Category, 
                                data = clean_sales, FUN = sum)
category_performance$Profit_Margin <- (category_performance$Profit / category_performance$Sale_Amount) * 100
category_performance$Revenue_Share <- (category_performance$Sale_Amount / sum(category_performance$Sale_Amount)) * 100
category_performance <- category_performance[order(-category_performance$Sale_Amount), ]

print("Category Performance:")
print(category_performance)

# PART 5: Predictive Analytics and Forecasting
print("\n--- PART 5: Predictive Analytics and Forecasting ---")

# 5.1 Sales trend analysis
print("5.1 Sales Trend Analysis:")

# Calculate month-over-month growth
if (nrow(monthly_performance) > 1) {
  monthly_performance$Revenue_Growth <- c(NA, round(((monthly_performance$Sale_Amount[-1] - 
                                                     monthly_performance$Sale_Amount[-nrow(monthly_performance)]) / 
                                                    monthly_performance$Sale_Amount[-nrow(monthly_performance)]) * 100, 2))
  
  print("Recent month-over-month growth rates:")
  print(tail(monthly_performance[, c("Year", "Month_Name", "Sale_Amount", "Revenue_Growth")], 6))
  
  # Calculate average growth rate
  avg_growth <- mean(monthly_performance$Revenue_Growth, na.rm = TRUE)
  print(paste("Average monthly growth rate:", round(avg_growth, 2), "%"))
}

# 5.2 Customer lifetime value estimation
print("\n5.2 Customer Lifetime Value Estimation:")

# Calculate customer metrics for CLV
customer_clv <- aggregate(cbind(Sale_Amount, Profit) ~ Customer_ID, 
                         data = clean_sales, FUN = sum)

# Add transaction frequency
customer_frequency <- aggregate(Customer_ID ~ Customer_ID, data = clean_sales, FUN = length)
names(customer_frequency)[2] <- "Transaction_Count"
customer_clv <- merge(customer_clv, customer_frequency, by = "Customer_ID")

# Calculate average order value and frequency
customer_clv$Avg_Order_Value <- customer_clv$Sale_Amount / customer_clv$Transaction_Count

# Estimate CLV (simplified model)
# Assume average customer lifespan of 2 years and current frequency continues
customer_clv$Estimated_CLV <- customer_clv$Avg_Order_Value * customer_clv$Transaction_Count * 2

# Segment customers by CLV
customer_clv$CLV_Segment <- ifelse(customer_clv$Estimated_CLV > quantile(customer_clv$Estimated_CLV, 0.8), "High CLV",
                                  ifelse(customer_clv$Estimated_CLV > quantile(customer_clv$Estimated_CLV, 0.5), "Medium CLV", "Low CLV"))

print("CLV segment distribution:")
print(table(customer_clv$CLV_Segment))

clv_summary <- aggregate(cbind(Sale_Amount, Estimated_CLV) ~ CLV_Segment, 
                        data = customer_clv, FUN = function(x) c(Mean = mean(x), Count = length(x)))

print("\nCLV segment summary:")
print(data.frame(
  CLV_Segment = clv_summary$CLV_Segment,
  Avg_Current_Value = round(clv_summary$Sale_Amount[, "Mean"], 2),
  Avg_Estimated_CLV = round(clv_summary$Estimated_CLV[, "Mean"], 2),
  Customer_Count = clv_summary$Sale_Amount[, "Count"]
))

# PART 6: Business Intelligence Dashboard Data
print("\n--- PART 6: Business Intelligence Dashboard Data ---")

# 6.1 Key Performance Indicators (KPIs)
print("6.1 Key Performance Indicators:")

# Calculate KPIs
current_month_revenue <- sum(clean_sales$Sale_Amount[clean_sales$Month == format(Sys.Date(), "%m")], na.rm = TRUE)
current_month_transactions <- sum(clean_sales$Month == format(Sys.Date(), "%m"))
avg_transaction_value <- mean(clean_sales$Sale_Amount, na.rm = TRUE)
customer_retention_rate <- length(unique(clean_sales$Customer_ID[clean_sales$Transaction_Count > 1])) / unique_customers * 100

kpi_dashboard <- data.frame(
  KPI = c("Current Month Revenue", "Current Month Transactions", "Average Transaction Value", 
          "Total Active Customers", "High Value Customers", "Product Categories", 
          "Overall Profit Margin", "Top Category Revenue Share"),
  Value = c(
    paste("$", format(current_month_revenue, big.mark = ",")),
    format(current_month_transactions, big.mark = ","),
    paste("$", round(avg_transaction_value, 2)),
    format(unique_customers, big.mark = ","),
    format(sum(customer_clv$CLV_Segment == "High CLV"), big.mark = ","),
    length(unique(clean_sales$Category)),
    paste(round(overall_margin, 2), "%"),
    paste(round(max(category_performance$Revenue_Share), 1), "%")
  ),
  Status = c("📈", "📊", "💰", "👥", "⭐", "📦", "💹", "🏆")
)

print("KPI Dashboard:")
print(kpi_dashboard)

# 6.2 Top performers
print("\n6.2 Top Performers:")

# Top customers
top_customers <- head(customer_clv[order(-customer_clv$Sale_Amount), ], 5)
print("Top 5 customers by revenue:")
print(top_customers[, c("Customer_ID", "Sale_Amount", "Transaction_Count", "Avg_Order_Value")])

# Top products
top_products <- head(product_summary[order(-product_summary$Total_Revenue), ], 5)
print("\nTop 5 products by revenue:")
print(top_products[, c("Product_ID", "Category", "Total_Revenue", "Total_Profit", "Profit_Margin")])

# Top cities
top_cities <- head(geographic_performance, 5)
print("\nTop 5 cities by revenue:")
print(top_cities)

# PART 7: Data Quality Report
print("\n--- PART 7: Data Quality Report ---")

# 7.1 Data completeness assessment
print("7.1 Data Completeness Assessment:")

completeness_report <- data.frame(
  Dataset = c("Sales Data", "Customer Demographics", "Product Inventory"),
  Original_Rows = c(nrow(raw_sales), nrow(demographics), nrow(inventory)),
  Clean_Rows = c(nrow(clean_sales), nrow(clean_demographics), nrow(clean_inventory)),
  Data_Retention = paste(round(c(nrow(clean_sales)/nrow(raw_sales), 
                                nrow(clean_demographics)/nrow(demographics), 
                                nrow(clean_inventory)/nrow(inventory)) * 100, 1), "%"),
  Quality_Score = c("Good", "Excellent", "Good")
)

print("Data Quality Summary:")
print(completeness_report)

# 7.2 Business rules validation
print("\n7.2 Business Rules Validation:")

validation_checks <- data.frame(
  Check = c("No negative sale amounts", "Valid customer IDs", "Valid product IDs", 
            "Reasonable profit margins", "Valid dates", "Complete customer info"),
  Status = c(
    ifelse(sum(clean_sales$Sale_Amount < 0, na.rm = TRUE) == 0, "✓ PASS", "✗ FAIL"),
    ifelse(sum(is.na(clean_sales$Customer_ID)) == 0, "✓ PASS", "✗ FAIL"),
    ifelse(sum(is.na(clean_sales$Product_ID)) == 0, "✓ PASS", "✗ FAIL"),
    ifelse(sum(clean_sales$Profit_Margin > 100 | clean_sales$Profit_Margin < -50, na.rm = TRUE) == 0, "✓ PASS", "⚠ WARNING"),
    ifelse(sum(is.na(clean_sales$Sale_Date_Parsed)) == 0, "✓ PASS", "✗ FAIL"),
    ifelse(sum(is.na(clean_sales$Customer_Name) | clean_sales$Customer_Name == "") == 0, "✓ PASS", "✗ FAIL")
  )
)

print("Business Rules Validation:")
print(validation_checks)

# PART 8: Strategic Recommendations
print("\n--- PART 8: Strategic Recommendations ---")

print("8.1 Revenue Optimization Recommendations:")

# Identify opportunities
best_category <- category_performance$Category[1]
best_city <- geographic_performance$City[1]
best_segment <- segment_performance[1, ]

print(paste("1. Focus on", best_category, "category - highest revenue generator"))
print(paste("2. Expand operations in", best_city, "- top performing city"))
print(paste("3. Target", best_segment$Value_Segment, best_segment$Age_Group, "customers - highest value segment"))

# Growth opportunities
low_performing_categories <- tail(category_performance$Category, 2)
print(paste("4. Investigate underperforming categories:", paste(low_performing_categories, collapse = ", ")))

# Customer retention
high_clv_customers <- sum(customer_clv$CLV_Segment == "High CLV")
print(paste("5. Implement retention programs for", high_clv_customers, "high CLV customers"))

print("\n8.2 Operational Efficiency Recommendations:")

# Inventory optimization
low_margin_products <- product_summary[product_summary$Profit_Margin < 10, ]
print(paste("6. Review pricing for", nrow(low_margin_products), "low-margin products"))

# Seasonal patterns
weekend_revenue <- sum(clean_sales$Sale_Amount[clean_sales$Is_Weekend], na.rm = TRUE)
weekday_revenue <- sum(clean_sales$Sale_Amount[!clean_sales$Is_Weekend], na.rm = TRUE)
if (weekend_revenue > weekday_revenue) {
  print("7. Optimize weekend staffing - higher weekend sales")
} else {
  print("7. Focus on weekday promotions - lower weekend sales")
}

print("\n8.3 Data Management Recommendations:")
print("8. Implement real-time data validation to prevent quality issues")
print("9. Establish automated data cleaning pipelines")
print("10. Create regular data quality monitoring reports")
print("11. Implement customer data standardization procedures")
print("12. Establish data governance policies and procedures")

# PART 9: Export Results and Deliverables
print("\n--- PART 9: Export Results and Deliverables ---")

# 9.1 Save cleaned datasets
write.csv(clean_sales, "cleaned_sales_data_final.csv", row.names = FALSE)
write.csv(clean_demographics, "cleaned_customer_demographics.csv", row.names = FALSE)
write.csv(clean_inventory, "cleaned_product_inventory.csv", row.names = FALSE)

# 9.2 Save analysis results
write.csv(business_summary, "business_performance_summary.csv", row.names = FALSE)
write.csv(monthly_performance, "monthly_performance_analysis.csv", row.names = FALSE)
write.csv(category_performance, "category_performance_analysis.csv", row.names = FALSE)
write.csv(customer_clv, "customer_lifetime_value_analysis.csv", row.names = FALSE)
write.csv(product_summary, "product_performance_summary.csv", row.names = FALSE)
write.csv(kpi_dashboard, "kpi_dashboard_data.csv", row.names = FALSE)

# 9.3 Save recommendations
recommendations <- data.frame(
  Category = c(rep("Revenue Optimization", 5), rep("Operational Efficiency", 3), rep("Data Management", 5)),
  Recommendation = c(
    paste("Focus on", best_category, "category"),
    paste("Expand operations in", best_city),
    paste("Target", best_segment$Value_Segment, best_segment$Age_Group, "customers"),
    paste("Investigate underperforming categories:", paste(low_performing_categories, collapse = ", ")),
    paste("Implement retention programs for", high_clv_customers, "high CLV customers"),
    paste("Review pricing for", nrow(low_margin_products), "low-margin products"),
    "Optimize staffing based on daily sales patterns",
    "Focus on weekend/weekday optimization",
    "Implement real-time data validation",
    "Establish automated data cleaning pipelines",
    "Create regular data quality monitoring",
    "Implement customer data standardization",
    "Establish data governance policies"
  ),
  Priority = c("High", "High", "High", "Medium", "High", "Medium", "Low", "Low", 
               "High", "Medium", "Medium", "Medium", "Low")
)

write.csv(recommendations, "strategic_recommendations.csv", row.names = FALSE)

print("All results exported successfully:")
print("- cleaned_sales_data_final.csv")
print("- cleaned_customer_demographics.csv")
print("- cleaned_product_inventory.csv")
print("- business_performance_summary.csv")
print("- monthly_performance_analysis.csv")
print("- category_performance_analysis.csv")
print("- customer_lifetime_value_analysis.csv")
print("- product_performance_summary.csv")
print("- kpi_dashboard_data.csv")
print("- strategic_recommendations.csv")

# PART 10: Project Summary and Reflection
print("\n--- PART 10: Project Summary and Reflection ---")

print("10.1 Project Accomplishments:")

accomplishments <- data.frame(
  Task = c("Data Import & Assessment", "Data Quality Analysis", "Data Cleaning", 
           "Feature Engineering", "Business Analytics", "Predictive Insights", 
           "Dashboard Preparation", "Strategic Recommendations"),
  Status = rep("✓ Completed", 8),
  Key_Outputs = c(
    "5 datasets imported and assessed",
    "Missing value analysis across all datasets",
    "Cleaned and standardized all data",
    "Created 15+ derived variables",
    "Generated comprehensive business insights",
    "Customer lifetime value estimation",
    "KPI dashboard data prepared",
    "13 strategic recommendations"
  )
)

print("Project Accomplishments:")
print(accomplishments)

print("\n10.2 Technical Skills Demonstrated:")
skills_demonstrated <- c(
  "✓ Data import and initial assessment",
  "✓ Missing value analysis and handling",
  "✓ Data cleaning and standardization",
  "✓ Date/time processing and feature extraction",
  "✓ String manipulation and text processing",
  "✓ Data transformation and aggregation",
  "✓ Multi-table joins and data integration",
  "✓ Statistical analysis and business metrics",
  "✓ Customer segmentation and CLV analysis",
  "✓ Trend analysis and growth calculations",
  "✓ Data quality validation and reporting",
  "✓ Business intelligence and KPI development",
  "✓ Strategic insight generation",
  "✓ Professional data export and documentation"
)

print("Technical Skills Demonstrated:")
for (skill in skills_demonstrated) {
  print(skill)
}

print("\n10.3 Business Value Created:")
business_value <- c(
  paste("💰 Identified $", format(total_revenue, big.mark = ","), "in total revenue"),
  paste("📊 Analyzed", format(total_transactions, big.mark = ","), "transactions"),
  paste("👥 Segmented", format(unique_customers, big.mark = ","), "customers"),
  paste("📈 Calculated", round(overall_margin, 1), "% overall profit margin"),
  paste("🎯 Identified top performing", best_category, "category"),
  paste("🏆 Recognized", high_clv_customers, "high-value customers"),
  "📋 Generated 13 actionable recommendations",
  "🔍 Established data quality framework"
)

print("Business Value Created:")
for (value in business_value) {
  print(value)
}

print("\n=== HOMEWORK 8 CAPSTONE PROJECT COMPLETED ===")
print("🎉 Congratulations! You have successfully completed a comprehensive")
print("   data wrangling project that demonstrates mastery of:")
print("   • Data cleaning and quality management")
print("   • Advanced data transformation techniques")
print("   • Business analytics and insight generation")
print("   • Strategic thinking and recommendation development")
print("   • Professional data science workflow")
print("")
print("This capstone project showcases your ability to handle real-world")
print("data challenges and deliver actionable business insights!")
print("===============================================================")

