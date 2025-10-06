# Homework 4 Solution: Data Transformation - Mutate, Summarize, Group_by
# Data Wrangling in R for Business Analytics
# Author: Manus AI

# Set working directory to sample_datasets
setwd("../sample_datasets")

print("=== HOMEWORK 4 SOLUTION ===")
print("Data Transformation - Mutate, Summarize, Group_by")
print("=================================================")

# PART 1: Data Import and Initial Setup
print("\n--- PART 1: Data Import and Initial Setup ---")

# 1.1 Import the company sales data
if (file.exists("company_sales_data.csv")) {
  company_data <- read.csv("company_sales_data.csv", stringsAsFactors = FALSE)
  print("1.1 Company sales data imported successfully!")
  
  print(paste("Dataset dimensions:", nrow(company_data), "rows x", ncol(company_data), "columns"))
  
  # 1.2 Examine the structure
  print("\n1.2 Dataset Structure:")
  str(company_data)
  
  print("\nFirst 5 rows:")
  print(head(company_data, 5))
  
  print("\nColumn summary:")
  print(summary(company_data))
  
} else {
  stop("Error: company_sales_data.csv not found!")
}

# PART 2: MUTATE Operations (Creating New Variables)
print("\n--- PART 2: MUTATE Operations (Creating New Variables) ---")

# 2.1 Calculate basic financial metrics
print("2.1 Creating Basic Financial Metrics:")

# Calculate profit
company_data$Profit <- company_data$Revenue - company_data$Cost
print("✓ Created Profit column")

# Calculate profit margin as percentage
company_data$Profit_Margin <- (company_data$Profit / company_data$Revenue) * 100
print("✓ Created Profit_Margin column")

# Calculate cost ratio
company_data$Cost_Ratio <- (company_data$Cost / company_data$Revenue) * 100
print("✓ Created Cost_Ratio column")

# Calculate revenue per unit
company_data$Revenue_Per_Unit <- company_data$Revenue / company_data$Units_Sold
print("✓ Created Revenue_Per_Unit column")

# Calculate cost per unit
company_data$Cost_Per_Unit <- company_data$Cost / company_data$Units_Sold
print("✓ Created Cost_Per_Unit column")

print("\nSample of new financial metrics:")
print(head(company_data[, c("Revenue", "Cost", "Profit", "Profit_Margin", "Revenue_Per_Unit")], 5))

# 2.2 Create categorical variables
print("\n2.2 Creating Categorical Variables:")

# Performance category based on profit margin
company_data$Performance_Category <- ifelse(company_data$Profit_Margin > 50, "High",
                                           ifelse(company_data$Profit_Margin > 30, "Medium", "Low"))
print("✓ Created Performance_Category")

# Revenue size category
company_data$Revenue_Size <- ifelse(company_data$Revenue > 30000, "Large",
                                   ifelse(company_data$Revenue > 15000, "Medium", "Small"))
print("✓ Created Revenue_Size category")

# Deal size category based on units sold
company_data$Deal_Size <- ifelse(company_data$Units_Sold > 50, "Bulk",
                                ifelse(company_data$Units_Sold > 20, "Standard", "Small"))
print("✓ Created Deal_Size category")

print("\nCategorical variable distributions:")
print("Performance Category:")
print(table(company_data$Performance_Category))
print("\nRevenue Size:")
print(table(company_data$Revenue_Size))
print("\nDeal Size:")
print(table(company_data$Deal_Size))

# 2.3 Create date-based variables
print("\n2.3 Creating Date-Based Variables:")

# Convert sale date to Date format
company_data$Sale_Date_Parsed <- as.Date(company_data$Sale_Date)

# Extract date components
company_data$Year <- format(company_data$Sale_Date_Parsed, "%Y")
company_data$Month <- format(company_data$Sale_Date_Parsed, "%m")
company_data$Quarter <- paste0("Q", ceiling(as.numeric(company_data$Month) / 3))
company_data$Weekday <- weekdays(company_data$Sale_Date_Parsed)

print("✓ Created date-based variables: Year, Month, Quarter, Weekday")

print("\nDate variable distributions:")
print("Year distribution:")
print(table(company_data$Year))
print("\nQuarter distribution:")
print(table(company_data$Quarter))

# 2.4 Create conditional variables
print("\n2.4 Creating Conditional Variables:")

# High-value customer flag
company_data$High_Value_Customer <- ifelse(company_data$Revenue > 25000, "Yes", "No")

# Profitable deal flag
company_data$Profitable_Deal <- ifelse(company_data$Profit_Margin > 40, "Yes", "No")

# Efficiency score (revenue per unit relative to cost per unit)
company_data$Efficiency_Score <- company_data$Revenue_Per_Unit / company_data$Cost_Per_Unit

print("✓ Created conditional variables")

print("\nConditional variable summary:")
print("High Value Customers:")
print(table(company_data$High_Value_Customer))
print("\nProfitable Deals:")
print(table(company_data$Profitable_Deal))
print(paste("Average Efficiency Score:", round(mean(company_data$Efficiency_Score, na.rm = TRUE), 2)))

# PART 3: SUMMARIZE Operations (Aggregate Statistics)
print("\n--- PART 3: SUMMARIZE Operations (Aggregate Statistics) ---")

# 3.1 Overall business summary
print("3.1 Overall Business Summary:")

total_revenue <- sum(company_data$Revenue, na.rm = TRUE)
total_cost <- sum(company_data$Cost, na.rm = TRUE)
total_profit <- sum(company_data$Profit, na.rm = TRUE)
avg_profit_margin <- mean(company_data$Profit_Margin, na.rm = TRUE)
total_units <- sum(company_data$Units_Sold, na.rm = TRUE)
total_transactions <- nrow(company_data)
avg_revenue_per_transaction <- mean(company_data$Revenue, na.rm = TRUE)

print(paste("Total Revenue: $", format(total_revenue, big.mark = ",")))
print(paste("Total Cost: $", format(total_cost, big.mark = ",")))
print(paste("Total Profit: $", format(total_profit, big.mark = ",")))
print(paste("Overall Profit Margin:", round(avg_profit_margin, 2), "%"))
print(paste("Total Units Sold:", format(total_units, big.mark = ",")))
print(paste("Total Transactions:", total_transactions))
print(paste("Average Revenue per Transaction: $", format(avg_revenue_per_transaction, big.mark = ",")))

# 3.2 Statistical summaries
print("\n3.2 Statistical Summaries:")

# Revenue statistics
revenue_stats <- c(
  Min = min(company_data$Revenue, na.rm = TRUE),
  Q1 = quantile(company_data$Revenue, 0.25, na.rm = TRUE),
  Median = median(company_data$Revenue, na.rm = TRUE),
  Mean = mean(company_data$Revenue, na.rm = TRUE),
  Q3 = quantile(company_data$Revenue, 0.75, na.rm = TRUE),
  Max = max(company_data$Revenue, na.rm = TRUE),
  SD = sd(company_data$Revenue, na.rm = TRUE)
)

print("Revenue Statistics:")
print(round(revenue_stats, 2))

# Profit margin statistics
margin_stats <- c(
  Min = min(company_data$Profit_Margin, na.rm = TRUE),
  Q1 = quantile(company_data$Profit_Margin, 0.25, na.rm = TRUE),
  Median = median(company_data$Profit_Margin, na.rm = TRUE),
  Mean = mean(company_data$Profit_Margin, na.rm = TRUE),
  Q3 = quantile(company_data$Profit_Margin, 0.75, na.rm = TRUE),
  Max = max(company_data$Profit_Margin, na.rm = TRUE),
  SD = sd(company_data$Profit_Margin, na.rm = TRUE)
)

print("\nProfit Margin Statistics:")
print(round(margin_stats, 2))

# PART 4: GROUP_BY Operations (Grouped Analysis)
print("\n--- PART 4: GROUP_BY Operations (Grouped Analysis) ---")

# 4.1 Analysis by Region
print("4.1 Analysis by Region:")

# Create region summary
regions <- unique(company_data$Region)
region_summary <- data.frame(
  Region = character(),
  Total_Revenue = numeric(),
  Total_Profit = numeric(),
  Avg_Profit_Margin = numeric(),
  Total_Units = numeric(),
  Transaction_Count = numeric(),
  Avg_Revenue_Per_Transaction = numeric(),
  stringsAsFactors = FALSE
)

for (region in regions) {
  region_data <- company_data[company_data$Region == region, ]
  region_summary <- rbind(region_summary, data.frame(
    Region = region,
    Total_Revenue = sum(region_data$Revenue, na.rm = TRUE),
    Total_Profit = sum(region_data$Profit, na.rm = TRUE),
    Avg_Profit_Margin = mean(region_data$Profit_Margin, na.rm = TRUE),
    Total_Units = sum(region_data$Units_Sold, na.rm = TRUE),
    Transaction_Count = nrow(region_data),
    Avg_Revenue_Per_Transaction = mean(region_data$Revenue, na.rm = TRUE),
    stringsAsFactors = FALSE
  ))
}

# Sort by total revenue
region_summary <- region_summary[order(-region_summary$Total_Revenue), ]
region_summary$Revenue_Share <- round((region_summary$Total_Revenue / sum(region_summary$Total_Revenue)) * 100, 2)

print("Regional Performance Summary:")
print(region_summary)

# 4.2 Analysis by Product Category
print("\n4.2 Analysis by Product Category:")

categories <- unique(company_data$Product_Category)
category_summary <- data.frame(
  Product_Category = character(),
  Total_Revenue = numeric(),
  Total_Profit = numeric(),
  Avg_Profit_Margin = numeric(),
  Total_Units = numeric(),
  Transaction_Count = numeric(),
  Avg_Revenue_Per_Unit = numeric(),
  stringsAsFactors = FALSE
)

for (category in categories) {
  cat_data <- company_data[company_data$Product_Category == category, ]
  category_summary <- rbind(category_summary, data.frame(
    Product_Category = category,
    Total_Revenue = sum(cat_data$Revenue, na.rm = TRUE),
    Total_Profit = sum(cat_data$Profit, na.rm = TRUE),
    Avg_Profit_Margin = mean(cat_data$Profit_Margin, na.rm = TRUE),
    Total_Units = sum(cat_data$Units_Sold, na.rm = TRUE),
    Transaction_Count = nrow(cat_data),
    Avg_Revenue_Per_Unit = mean(cat_data$Revenue_Per_Unit, na.rm = TRUE),
    stringsAsFactors = FALSE
  ))
}

# Sort by total revenue
category_summary <- category_summary[order(-category_summary$Total_Revenue), ]
category_summary$Revenue_Share <- round((category_summary$Total_Revenue / sum(category_summary$Total_Revenue)) * 100, 2)

print("Product Category Performance Summary:")
print(category_summary)

# 4.3 Analysis by Sales Representative
print("\n4.3 Analysis by Sales Representative:")

sales_reps <- unique(company_data$Sales_Rep_Name)
rep_summary <- data.frame(
  Sales_Rep = character(),
  Total_Revenue = numeric(),
  Total_Profit = numeric(),
  Avg_Profit_Margin = numeric(),
  Total_Units = numeric(),
  Deal_Count = numeric(),
  Avg_Deal_Size = numeric(),
  stringsAsFactors = FALSE
)

for (rep in sales_reps) {
  rep_data <- company_data[company_data$Sales_Rep_Name == rep, ]
  rep_summary <- rbind(rep_summary, data.frame(
    Sales_Rep = rep,
    Total_Revenue = sum(rep_data$Revenue, na.rm = TRUE),
    Total_Profit = sum(rep_data$Profit, na.rm = TRUE),
    Avg_Profit_Margin = mean(rep_data$Profit_Margin, na.rm = TRUE),
    Total_Units = sum(rep_data$Units_Sold, na.rm = TRUE),
    Deal_Count = nrow(rep_data),
    Avg_Deal_Size = mean(rep_data$Revenue, na.rm = TRUE),
    stringsAsFactors = FALSE
  ))
}

# Sort by total revenue
rep_summary <- rep_summary[order(-rep_summary$Total_Revenue), ]

print("Top 10 Sales Representatives by Revenue:")
print(head(rep_summary, 10))

# 4.4 Time-based analysis
print("\n4.4 Time-Based Analysis:")

# Monthly analysis
monthly_summary <- aggregate(cbind(Revenue, Profit, Units_Sold) ~ Year + Month, 
                           data = company_data, FUN = sum)
monthly_summary$Profit_Margin <- (monthly_summary$Profit / monthly_summary$Revenue) * 100
monthly_summary <- monthly_summary[order(monthly_summary$Year, monthly_summary$Month), ]

print("Monthly Performance (first 12 months):")
print(head(monthly_summary, 12))

# Quarterly analysis
quarterly_summary <- aggregate(cbind(Revenue, Profit, Units_Sold) ~ Year + Quarter, 
                             data = company_data, FUN = sum)
quarterly_summary$Profit_Margin <- (quarterly_summary$Profit / quarterly_summary$Revenue) * 100
quarterly_summary <- quarterly_summary[order(quarterly_summary$Year, quarterly_summary$Quarter), ]

print("\nQuarterly Performance:")
print(quarterly_summary)

# PART 5: Advanced Grouping and Analysis
print("\n--- PART 5: Advanced Grouping and Analysis ---")

# 5.1 Multi-dimensional analysis (Region + Product Category)
print("5.1 Multi-Dimensional Analysis (Region + Product Category):")

# Create cross-tabulation
region_category_revenue <- aggregate(Revenue ~ Region + Product_Category, 
                                   data = company_data, FUN = sum)
region_category_revenue <- region_category_revenue[order(-region_category_revenue$Revenue), ]

print("Top 10 Region-Category combinations by Revenue:")
print(head(region_category_revenue, 10))

# Create a pivot-like summary
region_category_matrix <- aggregate(Revenue ~ Region + Product_Category, 
                                  data = company_data, FUN = sum)

# Reshape to wide format for better visualization
library_available <- require(reshape2, quietly = TRUE)
if (!library_available) {
  # Manual pivot using base R
  regions_unique <- unique(region_category_matrix$Region)
  categories_unique <- unique(region_category_matrix$Product_Category)
  
  pivot_matrix <- matrix(0, nrow = length(regions_unique), ncol = length(categories_unique))
  rownames(pivot_matrix) <- regions_unique
  colnames(pivot_matrix) <- categories_unique
  
  for (i in 1:nrow(region_category_matrix)) {
    row_idx <- which(regions_unique == region_category_matrix$Region[i])
    col_idx <- which(categories_unique == region_category_matrix$Product_Category[i])
    pivot_matrix[row_idx, col_idx] <- region_category_matrix$Revenue[i]
  }
  
  print("\nRevenue Matrix (Region x Product Category):")
  print(pivot_matrix)
}

# 5.2 Performance category analysis
print("\n5.2 Performance Category Analysis:")

performance_analysis <- aggregate(cbind(Revenue, Profit, Units_Sold) ~ Performance_Category, 
                                data = company_data, FUN = function(x) c(Sum = sum(x), Mean = mean(x), Count = length(x)))

# Flatten the results
perf_summary <- data.frame(
  Performance_Category = performance_analysis$Performance_Category,
  Total_Revenue = performance_analysis$Revenue[, "Sum"],
  Avg_Revenue = round(performance_analysis$Revenue[, "Mean"], 2),
  Transaction_Count = performance_analysis$Revenue[, "Count"],
  Total_Profit = performance_analysis$Profit[, "Sum"],
  Avg_Profit = round(performance_analysis$Profit[, "Mean"], 2),
  Total_Units = performance_analysis$Units_Sold[, "Sum"]
)

perf_summary$Revenue_Share <- round((perf_summary$Total_Revenue / sum(perf_summary$Total_Revenue)) * 100, 2)

print("Performance Category Summary:")
print(perf_summary)

# PART 6: COUNT Operations and Frequency Analysis
print("\n--- PART 6: COUNT Operations and Frequency Analysis ---")

# 6.1 Count by categorical variables
print("6.1 Frequency Analysis:")

print("Count by Performance Category:")
perf_counts <- table(company_data$Performance_Category)
print(perf_counts)
print(paste("Percentage distribution:", round(prop.table(perf_counts) * 100, 2)))

print("\nCount by Revenue Size:")
revenue_size_counts <- table(company_data$Revenue_Size)
print(revenue_size_counts)

print("\nCount by Deal Size:")
deal_size_counts <- table(company_data$Deal_Size)
print(deal_size_counts)

# 6.2 Cross-tabulation analysis
print("\n6.2 Cross-Tabulation Analysis:")

print("Performance Category vs Revenue Size:")
cross_tab1 <- table(company_data$Performance_Category, company_data$Revenue_Size)
print(cross_tab1)

print("\nRegion vs Product Category:")
cross_tab2 <- table(company_data$Region, company_data$Product_Category)
print(cross_tab2)

# PART 7: Business Intelligence Metrics
print("\n--- PART 7: Business Intelligence Metrics ---")

# 7.1 Key Performance Indicators (KPIs)
print("7.1 Key Performance Indicators:")

# Calculate KPIs
total_customers <- length(unique(company_data$Sales_Rep_Name))  # Using sales rep as proxy for customers
avg_deal_value <- mean(company_data$Revenue, na.rm = TRUE)
conversion_rate <- (sum(company_data$Profitable_Deal == "Yes") / nrow(company_data)) * 100
high_value_rate <- (sum(company_data$High_Value_Customer == "Yes") / nrow(company_data)) * 100

print(paste("Total Sales Representatives:", total_customers))
print(paste("Average Deal Value: $", format(avg_deal_value, big.mark = ",")))
print(paste("Profitable Deal Rate:", round(conversion_rate, 2), "%"))
print(paste("High-Value Customer Rate:", round(high_value_rate, 2), "%"))

# 7.2 Efficiency metrics
print("\n7.2 Efficiency Metrics:")

avg_efficiency_score <- mean(company_data$Efficiency_Score, na.rm = TRUE)
avg_cost_ratio <- mean(company_data$Cost_Ratio, na.rm = TRUE)
avg_units_per_transaction <- mean(company_data$Units_Sold, na.rm = TRUE)

print(paste("Average Efficiency Score:", round(avg_efficiency_score, 2)))
print(paste("Average Cost Ratio:", round(avg_cost_ratio, 2), "%"))
print(paste("Average Units per Transaction:", round(avg_units_per_transaction, 2)))

# 7.3 Growth and trend analysis
print("\n7.3 Growth and Trend Analysis:")

# Calculate month-over-month growth (simplified)
if (nrow(monthly_summary) > 1) {
  latest_month_revenue <- monthly_summary$Revenue[nrow(monthly_summary)]
  previous_month_revenue <- monthly_summary$Revenue[nrow(monthly_summary) - 1]
  mom_growth <- ((latest_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
  
  print(paste("Latest Month Revenue: $", format(latest_month_revenue, big.mark = ",")))
  print(paste("Previous Month Revenue: $", format(previous_month_revenue, big.mark = ",")))
  print(paste("Month-over-Month Growth:", round(mom_growth, 2), "%"))
}

# PART 8: Advanced Calculations and Ratios
print("\n--- PART 8: Advanced Calculations and Ratios ---")

# 8.1 Financial ratios
print("8.1 Financial Ratios:")

# Calculate additional financial metrics
company_data$ROI <- (company_data$Profit / company_data$Cost) * 100
company_data$Revenue_Growth_Potential <- ifelse(company_data$Profit_Margin > 40, "High",
                                               ifelse(company_data$Profit_Margin > 25, "Medium", "Low"))

print("ROI Statistics:")
roi_stats <- c(
  Min = min(company_data$ROI, na.rm = TRUE),
  Mean = mean(company_data$ROI, na.rm = TRUE),
  Median = median(company_data$ROI, na.rm = TRUE),
  Max = max(company_data$ROI, na.rm = TRUE)
)
print(round(roi_stats, 2))

print("\nRevenue Growth Potential Distribution:")
print(table(company_data$Revenue_Growth_Potential))

# 8.2 Comparative analysis
print("\n8.2 Comparative Analysis:")

# Compare performance across different dimensions
high_performers <- company_data[company_data$Performance_Category == "High", ]
low_performers <- company_data[company_data$Performance_Category == "Low", ]

print("High vs Low Performers Comparison:")
print(paste("High Performers - Avg Revenue: $", round(mean(high_performers$Revenue), 2)))
print(paste("Low Performers - Avg Revenue: $", round(mean(low_performers$Revenue), 2)))
print(paste("High Performers - Avg Profit Margin:", round(mean(high_performers$Profit_Margin), 2), "%"))
print(paste("Low Performers - Avg Profit Margin:", round(mean(low_performers$Profit_Margin), 2), "%"))

# PART 9: Data Validation and Quality Checks
print("\n--- PART 9: Data Validation and Quality Checks ---")

# 9.1 Validate calculated fields
print("9.1 Calculated Field Validation:")

# Check if profit calculation is correct
profit_check <- all.equal(company_data$Profit, company_data$Revenue - company_data$Cost)
print(paste("Profit calculation validation:", profit_check))

# Check if profit margin calculation is correct
margin_check <- all.equal(company_data$Profit_Margin, 
                         (company_data$Profit / company_data$Revenue) * 100)
print(paste("Profit margin calculation validation:", margin_check))

# 9.2 Check for outliers in calculated fields
print("\n9.2 Outlier Detection in Calculated Fields:")

# Check for extreme profit margins
extreme_margins <- sum(company_data$Profit_Margin > 100 | company_data$Profit_Margin < -50, na.rm = TRUE)
print(paste("Extreme profit margins (>100% or <-50%):", extreme_margins))

# Check for extreme efficiency scores
extreme_efficiency <- sum(company_data$Efficiency_Score > 10 | company_data$Efficiency_Score < 0.1, na.rm = TRUE)
print(paste("Extreme efficiency scores:", extreme_efficiency))

# PART 10: Business Insights and Recommendations
print("\n--- PART 10: Business Insights and Recommendations ---")

print("10.1 Key Business Insights:")

# Top performing region
top_region <- region_summary$Region[1]
top_region_revenue <- region_summary$Total_Revenue[1]
top_region_share <- region_summary$Revenue_Share[1]

print(paste("1. Top performing region:", top_region))
print(paste("   Revenue: $", format(top_region_revenue, big.mark = ","), "(", top_region_share, "% of total)"))

# Top performing product category
top_category <- category_summary$Product_Category[1]
top_category_revenue <- category_summary$Total_Revenue[1]
top_category_share <- category_summary$Revenue_Share[1]

print(paste("2. Top performing product category:", top_category))
print(paste("   Revenue: $", format(top_category_revenue, big.mark = ","), "(", top_category_share, "% of total)"))

# Top performing sales rep
top_rep <- rep_summary$Sales_Rep[1]
top_rep_revenue <- rep_summary$Total_Revenue[1]

print(paste("3. Top performing sales representative:", top_rep))
print(paste("   Revenue: $", format(top_rep_revenue, big.mark = ",")))

# Performance insights
high_perf_count <- sum(company_data$Performance_Category == "High")
high_perf_percent <- round((high_perf_count / nrow(company_data)) * 100, 2)

print(paste("4. High-performance transactions:", high_perf_count, "(", high_perf_percent, "%)"))

print("\n10.2 Strategic Recommendations:")
print("- Focus resources on top-performing regions and categories")
print("- Analyze and replicate success factors from high-performing sales reps")
print("- Investigate low-performing segments for improvement opportunities")
print("- Implement performance-based incentive programs")
print("- Monitor efficiency scores to optimize cost management")
print("- Develop targeted strategies for different customer segments")

print("\n=== HOMEWORK 4 SOLUTION COMPLETED ===")
print("All data transformation and analysis tasks completed successfully!")
print("Key learning objectives achieved:")
print("- Creating new variables using mutate operations")
print("- Calculating summary statistics and aggregations")
print("- Performing grouped analysis by multiple dimensions")
print("- Generating business intelligence metrics")
print("- Conducting comparative and trend analysis")
print("- Validating data quality and calculations")

# Display final dataset structure
print("\nFinal dataset structure with all new variables:")
str(company_data)

