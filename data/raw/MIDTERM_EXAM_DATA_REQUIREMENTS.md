# Midterm Exam - Data Requirements

## Required Data Files

The midterm exam requires the following CSV files in the `data/processed/` folder:

### 1. company_sales_data.csv
**Columns:**
- `Region` (text): North, South, East, West
- `Product_Category` (text): Electronics, Clothing, Home, Sports
- `Revenue` (numeric): Sales revenue in dollars
- `Units_Sold` (numeric): Number of units sold
- `Sale_Date` (text): Date in MM/DD/YYYY format

**Purpose:** Main sales transaction data for analysis

### 2. customers.csv
**Columns:**
- `CustomerID` (numeric): Unique customer identifier
- `CustomerName` (text): Customer full name
- `Email` (text): Customer email address
- `JoinDate` (text): Date customer joined

**Purpose:** Customer master data for joins

### 3. products.csv
**Columns:**
- `ProductID` (numeric): Unique product identifier
- `ProductName` (text): Product name
- `Category` (text): Product category
- `Price` (numeric): Product price

**Purpose:** Product master data

### 4. orders.csv
**Columns:**
- `OrderID` (numeric): Unique order identifier
- `CustomerID` (numeric): Foreign key to customers
- `OrderDate` (text): Date of order
- `TotalAmount` (numeric): Total order amount

**Purpose:** Order header data for joins

### 5. order_items.csv
**Columns:**
- `OrderItemID` (numeric): Unique order item identifier
- `OrderID` (numeric): Foreign key to orders
- `ProductID` (numeric): Foreign key to products
- `Quantity` (numeric): Quantity ordered
- `LineTotal` (numeric): Line item total

**Purpose:** Order detail data for joins

## Data Generation

If these files don't exist, you can generate sample data using this R script:

```r
library(tidyverse)
library(lubridate)

# Set seed for reproducibility
set.seed(123)

# Generate company_sales_data.csv
sales_data <- tibble(
  Region = sample(c("North", "South", "East", "West"), 500, replace = TRUE),
  Product_Category = sample(c("Electronics", "Clothing", "Home", "Sports"), 500, replace = TRUE),
  Revenue = round(runif(500, 5000, 50000), 2),
  Units_Sold = sample(10:200, 500, replace = TRUE),
  Sale_Date = format(sample(seq(as.Date("2023-01-01"), as.Date("2023-12-31"), by = "day"), 500, replace = TRUE), "%m/%d/%Y")
)

# Add some missing values (10%)
sales_data$Revenue[sample(1:500, 50)] <- NA
sales_data$Units_Sold[sample(1:500, 50)] <- NA

write_csv(sales_data, "data/processed/company_sales_data.csv")

# Generate customers.csv
customers <- tibble(
  CustomerID = 1:100,
  CustomerName = paste("Customer", 1:100),
  Email = paste0("customer", 1:100, "@email.com"),
  JoinDate = format(sample(seq(as.Date("2020-01-01"), as.Date("2023-12-31"), by = "day"), 100, replace = TRUE), "%m/%d/%Y")
)

write_csv(customers, "data/processed/customers.csv")

# Generate products.csv
products <- tibble(
  ProductID = 1:50,
  ProductName = paste("Product", 1:50),
  Category = sample(c("Electronics", "Clothing", "Home", "Sports"), 50, replace = TRUE),
  Price = round(runif(50, 10, 500), 2)
)

write_csv(products, "data/processed/products.csv")

# Generate orders.csv
orders <- tibble(
  OrderID = 1:200,
  CustomerID = sample(1:100, 200, replace = TRUE),
  OrderDate = format(sample(seq(as.Date("2023-01-01"), as.Date("2023-12-31"), by = "day"), 200, replace = TRUE), "%m/%d/%Y"),
  TotalAmount = round(runif(200, 50, 1000), 2)
)

write_csv(orders, "data/processed/orders.csv")

# Generate order_items.csv
order_items <- tibble(
  OrderItemID = 1:500,
  OrderID = sample(1:200, 500, replace = TRUE),
  ProductID = sample(1:50, 500, replace = TRUE),
  Quantity = sample(1:10, 500, replace = TRUE),
  LineTotal = round(runif(500, 10, 500), 2)
)

write_csv(order_items, "data/processed/order_items.csv")

cat("✅ All data files generated successfully!\n")
```

## Lesson Coverage

The midterm exam covers material from:

- **Lesson 1:** R Basics and Data Import (Lecture-1.ipynb)
- **Lesson 2:** Data Cleaning (Lecture-2-Data-Cleaning.ipynb)
- **Lesson 3:** Data Transformation Part 1 (homework_lesson_3)
- **Lesson 4:** Data Transformation Part 2 (Lesson-4-Data-Transformation-Part-2.ipynb)
- **Lesson 5:** Data Reshaping (Lesson-5-Data-Reshaping-with-tidyr.ipynb)
- **Lesson 6:** Combining Datasets (Lesson-6-Combining-Datasets-Joins-Final.ipynb)
- **Lesson 7:** String & DateTime (Lesson-7-String-DateTime.ipynb)
- **Lesson 8:** Advanced Wrangling (Lesson-8-Advanced-Wrangling.ipynb)

All concepts in the exam are covered in these lesson notebooks.
