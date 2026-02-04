# Homework 3 Solution: Data Transformation - Select, Filter, Arrange
# Data Wrangling in R for Business Analytics
# Author: Manus AI

# Set working directory to sample_datasets
setwd("../sample_datasets")

print("=== HOMEWORK 3 SOLUTION ===")
print("Data Transformation - Select, Filter, Arrange")
print("=============================================")

# PART 1: Data Import and Initial Exploration
print("\n--- PART 1: Data Import and Initial Exploration ---")

# 1.1 Import the retail transactions data
if (file.exists("retail_transactions.csv")) {
  retail_data <- read.csv("retail_transactions.csv", stringsAsFactors = FALSE)
  print("1.1 Retail transactions data imported successfully!")
  
  print(paste("Dataset dimensions:", nrow(retail_data), "rows x", ncol(retail_data), "columns"))
  
  # 1.2 Examine the structure
  print("\n1.2 Dataset Structure:")
  str(retail_data)
  
  print("\nColumn names:")
  print(names(retail_data))
  
  print("\nFirst 5 rows:")
  print(head(retail_data, 5))
  
} else {
  stop("Error: retail_transactions.csv not found!")
}

# PART 2: SELECT Operations (Column Selection)
print("\n--- PART 2: SELECT Operations (Column Selection) ---")

# 2.1 Select specific columns for customer analysis
print("2.1 Customer Analysis - Select customer and transaction info:")
customer_info <- retail_data[, c("TransactionID", "CustomerID", "CustomerName", "CustomerCity")]
print("Selected columns: TransactionID, CustomerID, CustomerName, CustomerCity")
print(head(customer_info, 5))

# 2.2 Select columns for product analysis
print("\n2.2 Product Analysis - Select product-related columns:")
product_info <- retail_data[, c("TransactionID", "ProductName", "ProductCategory", "TotalAmount", "Quantity")]
print("Selected columns: TransactionID, ProductName, ProductCategory, TotalAmount, Quantity")
print(head(product_info, 5))

# 2.3 Select columns for financial analysis
print("\n2.3 Financial Analysis - Select financial columns:")
financial_info <- retail_data[, c("TransactionID", "TotalAmount", "Quantity", "TransactionDate")]
print("Selected columns: TransactionID, TotalAmount, Quantity, TransactionDate")
print(head(financial_info, 5))

# 2.4 Select columns using column indices
print("\n2.4 Select using column indices (first 4 columns):")
first_four_cols <- retail_data[, 1:4]
print("First 4 columns:")
print(head(first_four_cols, 3))

# 2.5 Select all columns except specific ones
print("\n2.5 Select all columns except CustomerID:")
all_except_customerid <- retail_data[, !names(retail_data) %in% "CustomerID"]
print(paste("Original columns:", ncol(retail_data)))
print(paste("After removing CustomerID:", ncol(all_except_customerid)))
print("Remaining columns:")
print(names(all_except_customerid))

# PART 3: FILTER Operations (Row Selection)
print("\n--- PART 3: FILTER Operations (Row Selection) ---")

# 3.1 Filter by transaction amount
print("3.1 High-Value Transactions (Amount > $1000):")
high_value <- retail_data[retail_data$TotalAmount > 1000, ]
print(paste("Total transactions:", nrow(retail_data)))
print(paste("High-value transactions:", nrow(high_value)))
print(paste("Percentage of high-value transactions:", round((nrow(high_value)/nrow(retail_data))*100, 2), "%"))

print("\nSample of high-value transactions:")
print(head(high_value[, c("TransactionID", "CustomerName", "ProductName", "TotalAmount")], 5))

# 3.2 Filter by product category
print("\n3.2 Electronics Transactions:")
electronics <- retail_data[retail_data$ProductCategory == "Electronics", ]
print(paste("Electronics transactions:", nrow(electronics)))

print("\nElectronics product distribution:")
electronics_products <- table(electronics$ProductName)
print(sort(electronics_products, decreasing = TRUE))

# 3.3 Filter by customer city
print("\n3.3 Transactions from Major Cities (New York, Los Angeles, Chicago):")
major_cities <- c("New York", "Los Angeles", "Chicago")
major_city_transactions <- retail_data[retail_data$CustomerCity %in% major_cities, ]
print(paste("Transactions from major cities:", nrow(major_city_transactions)))

print("\nTransactions by major city:")
city_counts <- table(major_city_transactions$CustomerCity)
print(sort(city_counts, decreasing = TRUE))

# 3.4 Filter by quantity
print("\n3.4 Bulk Purchases (Quantity >= 5):")
bulk_purchases <- retail_data[retail_data$Quantity >= 5, ]
print(paste("Bulk purchase transactions:", nrow(bulk_purchases)))
print(paste("Average amount for bulk purchases: $", round(mean(bulk_purchases$TotalAmount), 2)))

# 3.5 Multiple condition filtering
print("\n3.5 Complex Filter - High-Value Electronics in Major Cities:")
complex_filter <- retail_data[retail_data$TotalAmount > 1000 & 
                             retail_data$ProductCategory == "Electronics" & 
                             retail_data$CustomerCity %in% major_cities, ]
print(paste("Transactions matching all criteria:", nrow(complex_filter)))

if (nrow(complex_filter) > 0) {
  print("\nSample of complex filtered data:")
  print(head(complex_filter[, c("CustomerName", "CustomerCity", "ProductName", "TotalAmount")], 5))
}

# 3.6 Filter using logical operators
print("\n3.6 Medium-Value Transactions ($500 - $1500):")
medium_value <- retail_data[retail_data$TotalAmount >= 500 & retail_data$TotalAmount <= 1500, ]
print(paste("Medium-value transactions:", nrow(medium_value)))
print(paste("Average medium-value transaction: $", round(mean(medium_value$TotalAmount), 2)))

# PART 4: ARRANGE Operations (Sorting)
print("\n--- PART 4: ARRANGE Operations (Sorting) ---")

# 4.1 Sort by transaction amount (ascending)
print("4.1 Lowest Transaction Amounts:")
sorted_asc <- retail_data[order(retail_data$TotalAmount), ]
print("Top 5 lowest amounts:")
print(head(sorted_asc[, c("TransactionID", "CustomerName", "ProductName", "TotalAmount")], 5))

# 4.2 Sort by transaction amount (descending)
print("\n4.2 Highest Transaction Amounts:")
sorted_desc <- retail_data[order(-retail_data$TotalAmount), ]
print("Top 5 highest amounts:")
print(head(sorted_desc[, c("TransactionID", "CustomerName", "ProductName", "TotalAmount")], 5))

# 4.3 Sort by multiple columns
print("\n4.3 Sort by City, then by Amount (descending):")
sorted_multi <- retail_data[order(retail_data$CustomerCity, -retail_data$TotalAmount), ]
print("First 8 rows (sorted by city, then amount):")
print(head(sorted_multi[, c("CustomerCity", "CustomerName", "ProductName", "TotalAmount")], 8))

# 4.4 Sort by product category and quantity
print("\n4.4 Sort by Product Category, then Quantity (descending):")
sorted_product <- retail_data[order(retail_data$ProductCategory, -retail_data$Quantity), ]
print("Sample of sorted data:")
print(head(sorted_product[, c("ProductCategory", "ProductName", "Quantity", "TotalAmount")], 8))

# 4.5 Sort character columns alphabetically
print("\n4.5 Sort by Customer Name (alphabetical):")
sorted_names <- retail_data[order(retail_data$CustomerName), ]
print("First 5 customers alphabetically:")
print(head(sorted_names[, c("CustomerName", "CustomerCity", "ProductName", "TotalAmount")], 5))

# PART 5: Combined Operations
print("\n--- PART 5: Combined Operations ---")

# 5.1 Select, Filter, and Arrange combined
print("5.1 Combined Operation - Electronics over $800, sorted by amount:")

# Step 1: Filter for Electronics over $800
electronics_high <- retail_data[retail_data$ProductCategory == "Electronics" & 
                               retail_data$TotalAmount > 800, ]

# Step 2: Select relevant columns
electronics_selected <- electronics_high[, c("TransactionID", "CustomerName", "ProductName", 
                                             "TotalAmount", "CustomerCity")]

# Step 3: Sort by amount (descending)
electronics_final <- electronics_selected[order(-electronics_selected$TotalAmount), ]

print(paste("Transactions found:", nrow(electronics_final)))
print("Top 10 results:")
print(head(electronics_final, 10))

# 5.2 Customer analysis with combined operations
print("\n5.2 Customer Analysis - Top customers by total spending:")

# Calculate total spending per customer
customer_totals <- aggregate(TotalAmount ~ CustomerName + CustomerCity, 
                           data = retail_data, FUN = sum)

# Sort by total amount
customer_totals <- customer_totals[order(-customer_totals$TotalAmount), ]

# Add transaction count
customer_counts <- aggregate(TransactionID ~ CustomerName, 
                           data = retail_data, FUN = length)
names(customer_counts)[2] <- "TransactionCount"

# Merge totals and counts
customer_analysis <- merge(customer_totals, customer_counts, by = "CustomerName")

# Sort by total amount again
customer_analysis <- customer_analysis[order(-customer_analysis$TotalAmount), ]

print("Top 10 customers by total spending:")
print(head(customer_analysis, 10))

# 5.3 Product performance analysis
print("\n5.3 Product Performance Analysis:")

# Calculate metrics per product
product_metrics <- aggregate(cbind(TotalAmount, Quantity) ~ ProductName + ProductCategory, 
                           data = retail_data, FUN = function(x) c(Sum = sum(x), Count = length(x), Mean = mean(x)))

# Flatten the result
product_summary <- data.frame(
  ProductName = product_metrics$ProductName,
  ProductCategory = product_metrics$ProductCategory,
  TotalRevenue = product_metrics$TotalAmount[, "Sum"],
  TransactionCount = product_metrics$TotalAmount[, "Count"],
  AvgAmount = round(product_metrics$TotalAmount[, "Mean"], 2),
  TotalQuantity = product_metrics$Quantity[, "Sum"],
  AvgQuantity = round(product_metrics$Quantity[, "Mean"], 2)
)

# Sort by total revenue
product_summary <- product_summary[order(-product_summary$TotalRevenue), ]

print("Top 10 products by revenue:")
print(head(product_summary, 10))

# PART 6: Business Insights and Analysis
print("\n--- PART 6: Business Insights and Analysis ---")

# 6.1 Revenue analysis by category
print("6.1 Revenue Analysis by Product Category:")
category_revenue <- aggregate(TotalAmount ~ ProductCategory, data = retail_data, FUN = sum)
category_revenue <- category_revenue[order(-category_revenue$TotalAmount), ]
category_revenue$Percentage <- round((category_revenue$TotalAmount / sum(category_revenue$TotalAmount)) * 100, 2)

print(category_revenue)

# 6.2 Geographic analysis
print("\n6.2 Geographic Analysis - Top Cities by Revenue:")
city_revenue <- aggregate(TotalAmount ~ CustomerCity, data = retail_data, FUN = sum)
city_revenue <- city_revenue[order(-city_revenue$TotalAmount), ]
city_revenue$Percentage <- round((city_revenue$TotalAmount / sum(city_revenue$TotalAmount)) * 100, 2)

print("Top 10 cities by revenue:")
print(head(city_revenue, 10))

# 6.3 Transaction size analysis
print("\n6.3 Transaction Size Analysis:")

# Create transaction size categories
retail_data$TransactionSize <- ifelse(retail_data$TotalAmount < 500, "Small",
                                     ifelse(retail_data$TotalAmount < 1000, "Medium", "Large"))

size_analysis <- aggregate(cbind(TotalAmount, TransactionID) ~ TransactionSize, 
                          data = retail_data, 
                          FUN = function(x) c(Sum = sum(x), Count = length(x)))

size_summary <- data.frame(
  TransactionSize = size_analysis$TransactionSize,
  TotalRevenue = size_analysis$TotalAmount[, "Sum"],
  TransactionCount = size_analysis$TotalAmount[, "Count"],
  AvgAmount = round(size_analysis$TotalAmount[, "Sum"] / size_analysis$TotalAmount[, "Count"], 2)
)

size_summary$RevenuePercentage <- round((size_summary$TotalRevenue / sum(size_summary$TotalRevenue)) * 100, 2)
size_summary$CountPercentage <- round((size_summary$TransactionCount / sum(size_summary$TransactionCount)) * 100, 2)

print(size_summary)

# PART 7: Advanced Filtering Techniques
print("\n--- PART 7: Advanced Filtering Techniques ---")

# 7.1 Top N filtering
print("7.1 Top 5 Transactions by Amount:")
top_5_transactions <- head(retail_data[order(-retail_data$TotalAmount), ], 5)
print(top_5_transactions[, c("TransactionID", "CustomerName", "ProductName", "TotalAmount")])

# 7.2 Percentile-based filtering
print("\n7.2 Top 10% of Transactions by Amount:")
amount_90th_percentile <- quantile(retail_data$TotalAmount, 0.9)
top_10_percent <- retail_data[retail_data$TotalAmount >= amount_90th_percentile, ]

print(paste("90th percentile amount: $", round(amount_90th_percentile, 2)))
print(paste("Transactions in top 10%:", nrow(top_10_percent)))
print(paste("Average amount in top 10%: $", round(mean(top_10_percent$TotalAmount), 2)))

# 7.3 Pattern matching in text
print("\n7.3 Products with 'Pro' in the name:")
pro_products <- retail_data[grepl("Pro", retail_data$ProductName, ignore.case = TRUE), ]
print(paste("Transactions with 'Pro' products:", nrow(pro_products)))

if (nrow(pro_products) > 0) {
  print("Sample of 'Pro' products:")
  print(unique(pro_products$ProductName))
}

# PART 8: Data Quality Checks
print("\n--- PART 8: Data Quality Checks ---")

# 8.1 Check for missing values after operations
print("8.1 Missing Values Check:")
missing_check <- sapply(retail_data, function(x) sum(is.na(x)))
print("Missing values by column:")
print(missing_check)

# 8.2 Check for duplicates
print("\n8.2 Duplicate Check:")
duplicate_count <- sum(duplicated(retail_data))
print(paste("Duplicate rows:", duplicate_count))

# 8.3 Data range validation
print("\n8.3 Data Range Validation:")
print(paste("Amount range: $", min(retail_data$TotalAmount), " to $", max(retail_data$TotalAmount)))
print(paste("Quantity range:", min(retail_data$Quantity), " to", max(retail_data$Quantity)))

# Check for negative values
negative_amounts <- sum(retail_data$TotalAmount < 0)
negative_quantities <- sum(retail_data$Quantity < 0)
print(paste("Negative amounts:", negative_amounts))
print(paste("Negative quantities:", negative_quantities))

# PART 9: Summary Statistics
print("\n--- PART 9: Summary Statistics ---")

print("9.1 Overall Dataset Summary:")
print(paste("Total transactions:", nrow(retail_data)))
print(paste("Total revenue: $", format(sum(retail_data$TotalAmount), big.mark = ",")))
print(paste("Average transaction: $", round(mean(retail_data$TotalAmount), 2)))
print(paste("Median transaction: $", round(median(retail_data$TotalAmount), 2)))
print(paste("Total items sold:", sum(retail_data$Quantity)))
print(paste("Unique customers:", length(unique(retail_data$CustomerName))))
print(paste("Unique products:", length(unique(retail_data$ProductName))))
print(paste("Unique cities:", length(unique(retail_data$CustomerCity))))

# PART 10: Business Recommendations
print("\n--- PART 10: Business Recommendations ---")

print("10.1 Key Findings and Recommendations:")

# Top performing category
top_category <- category_revenue$ProductCategory[1]
top_category_revenue <- category_revenue$TotalAmount[1]

print(paste("1. Top performing category:", top_category, "with $", 
            format(top_category_revenue, big.mark = ","), "in revenue"))

# Top performing city
top_city <- city_revenue$CustomerCity[1]
top_city_revenue <- city_revenue$TotalAmount[1]

print(paste("2. Top performing city:", top_city, "with $", 
            format(top_city_revenue, big.mark = ","), "in revenue"))

# Transaction size insights
large_transactions_percent <- size_summary$CountPercentage[size_summary$TransactionSize == "Large"]
large_revenue_percent <- size_summary$RevenuePercentage[size_summary$TransactionSize == "Large"]

print(paste("3. Large transactions represent", large_transactions_percent, 
            "% of transactions but", large_revenue_percent, "% of revenue"))

print("\n10.2 Action Items:")
print("- Focus marketing efforts on top-performing categories and cities")
print("- Develop strategies to increase transaction sizes")
print("- Analyze customer behavior patterns for personalization")
print("- Monitor geographic expansion opportunities")
print("- Implement customer segmentation based on spending patterns")

print("\n=== HOMEWORK 3 SOLUTION COMPLETED ===")
print("All data transformation tasks completed successfully!")
print("Key learning objectives achieved:")
print("- Column selection using various methods")
print("- Row filtering with single and multiple conditions")
print("- Data sorting by single and multiple columns")
print("- Combined operations for complex analysis")
print("- Business insights generation from transformed data")
print("- Data quality validation techniques")

