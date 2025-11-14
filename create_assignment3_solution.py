#!/usr/bin/env python3
"""
Create Assignment 3 Solution Notebook
Fills in all the solution code for homework_lesson_3
"""

import json
import nbformat

# Read the template notebook
with open('data/raw/homework_lesson_3_data_transformation.ipynb', 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Update student name in first cell
nb.cells[0]['source'] = nb.cells[0]['source'].replace('[Enter Your Name Here]', 'SOLUTION KEY')

# Define all solutions - matching the cell order in the template
solutions = [
    # Cell 2: Part 1.1 - Data Import
    '''# Load required libraries
library(tidyverse)

# Task 1.1: Import the retail_transactions.csv file
transactions <- read_csv("retail_transactions.csv")

# Display success message
cat("Data imported successfully!\\n")
cat("Dataset dimensions:", nrow(transactions), "rows x", ncol(transactions), "columns\\n")''',
    
    # Cell 4: Part 1.2 - Initial Exploration
    '''# Task 1.2: Initial Exploration

# Display the first 10 rows
cat("First 10 rows of the dataset:\\n")
head(transactions, 10)

# Check the structure of the dataset
cat("\\nDataset structure:\\n")
str(transactions)

# Display column names and their data types
cat("\\nColumn names:\\n")
names(transactions)''',
    
    # Cell 6: Part 2.1 - Basic Selection
    '''# Task 2.1: Basic Selection
basic_info <- transactions %>%
  select(TransactionID, CustomerID, ProductName, TotalAmount)

# Display the result
cat("Basic info dataset (first 5 rows):\\n")
head(basic_info, 5)''',
    
    # Cell 8: Part 2.2 - Range Selection
    '''# Task 2.2: Range Selection
customer_details <- transactions %>%
  select(CustomerID:CustomerCity)

# Display the result
cat("Customer details (first 5 rows):\\n")
head(customer_details, 5)''',
    
    # Cell 10: Part 2.3 - Pattern Selection
    '''# Task 2.3: Pattern-Based Selection

# Create 'date_columns' with columns starting with "Date" or "Time"
date_columns <- transactions %>%
  select(starts_with("Date") | starts_with("Time"))

# Create 'amount_columns' with columns containing the word "Amount"
amount_columns <- transactions %>%
  select(contains("Amount"))

# Display column names for verification
cat("Date/Time columns:", names(date_columns), "\\n")
cat("Amount columns:", names(amount_columns), "\\n")''',
    
    # Cell 12: Part 2.4 - Exclusion
    '''# Task 2.4: Exclusion Selection
no_ids <- transactions %>%
  select(-TransactionID, -CustomerID)

# Display column names for verification
cat("Columns after removing IDs:", names(no_ids), "\\n")
cat("Number of columns:", ncol(no_ids), "\\n")''',
    
    # Cell 14: Part 3.1 - Single Condition
    '''# Task 3.1: Single Condition Filtering

# Filter transactions with TotalAmount > $100
high_value_transactions <- transactions %>%
  filter(TotalAmount > 100)

# Filter transactions from "Electronics" category
electronics_transactions <- transactions %>%
  filter(ProductCategory == "Electronics")

# Display results
cat("High value transactions (>$100):", nrow(high_value_transactions), "rows\\n")
cat("Electronics transactions:", nrow(electronics_transactions), "rows\\n")''',
    
    # Cell 16: Part 3.2 - Multiple AND
    '''# Task 3.2: Multiple Condition Filtering (AND)
ny_bulk_purchases <- transactions %>%
  filter(TotalAmount > 50 & Quantity > 1 & CustomerCity == "New York")

# Display results
cat("NY bulk purchases:", nrow(ny_bulk_purchases), "rows\\n")
if(nrow(ny_bulk_purchases) > 0) {
  head(ny_bulk_purchases)
}''',
    
    # Cell 18: Part 3.3 - Multiple OR
    '''# Task 3.3: Multiple Condition Filtering (OR)
entertainment_transactions <- transactions %>%
  filter(ProductCategory %in% c("Books", "Music", "Movies"))

# Display results
cat("Entertainment transactions:", nrow(entertainment_transactions), "rows\\n")
if(nrow(entertainment_transactions) > 0) {
  head(entertainment_transactions)
}''',
    
    # Cell 20: Part 3.4 - Date Filtering
    '''# Task 3.4: Date-Based Filtering
# Filter transactions from March 2024
march_transactions <- transactions %>%
  filter(month(TransactionDate) == 3 & year(TransactionDate) == 2024)

# Display results
cat("March 2024 transactions:", nrow(march_transactions), "rows\\n")''',
    
    # Cell 22: Part 3.5 - Advanced Challenge
    '''# Task 3.5: Advanced Filtering Challenge

# Step 1: Find customers who bought Electronics
electronics_customers <- transactions %>%
  filter(ProductCategory == "Electronics") %>%
  pull(CustomerID) %>%
  unique()

# Step 2: Find customers who bought Clothing
clothing_customers <- transactions %>%
  filter(ProductCategory == "Clothing") %>%
  pull(CustomerID) %>%
  unique()

# Step 3: Find customers who bought both
both_categories_customers <- intersect(electronics_customers, clothing_customers)

# Display results
cat("Customers who bought both Electronics and Clothing:", length(both_categories_customers), "customers\\n")''',
    
    # Cell 24: Part 4.1 - Single Column Sort
    '''# Task 4.1: Single Column Sorting

# Sort by TotalAmount ascending
transactions_by_amount_asc <- transactions %>%
  arrange(TotalAmount)

# Sort by TotalAmount descending
transactions_by_amount_desc <- transactions %>%
  arrange(desc(TotalAmount))

# Display top 5 of each
cat("Lowest amounts:\\n")
head(transactions_by_amount_asc %>% select(CustomerName, ProductName, TotalAmount), 5)

cat("\\nHighest amounts:\\n")
head(transactions_by_amount_desc %>% select(CustomerName, ProductName, TotalAmount), 5)''',
    
    # Cell 26: Part 4.2 - Multiple Column Sort
    '''# Task 4.2: Multiple Column Sorting
transactions_by_city_amount <- transactions %>%
  arrange(CustomerCity, desc(TotalAmount))

# Display first 10 rows
cat("Transactions sorted by city, then amount:\\n")
head(transactions_by_city_amount %>% select(CustomerCity, CustomerName, ProductName, TotalAmount), 10)''',
    
    # Cell 28: Part 4.3 - Date Sort
    '''# Task 4.3: Date-Based Sorting
transactions_chronological <- transactions %>%
  arrange(TransactionDate)

# Display first 5 transactions chronologically
cat("Earliest transactions:\\n")
head(transactions_chronological %>% select(TransactionDate, CustomerName, ProductName, TotalAmount), 5)''',
    
    # Cell 30: Part 5.1 - Simple Chain
    '''# Task 5.1: Simple Chain
premium_purchases <- transactions %>%
  filter(TotalAmount > 75) %>%
  select(CustomerName, ProductName, TotalAmount, CustomerCity) %>%
  arrange(desc(TotalAmount))

# Display results
cat("Premium purchases (>$75):\\n")
head(premium_purchases, 10)''',
    
    # Cell 32: Part 5.2 - Complex Chain
    '''# Task 5.2: Complex Chain
recent_tech_purchases <- transactions %>%
  filter(ProductCategory %in% c("Electronics", "Computers")) %>%
  select(TransactionDate, CustomerName, ProductName, TotalAmount) %>%
  arrange(desc(TransactionDate), desc(TotalAmount)) %>%
  head(20)

# Display results
cat("Recent tech purchases (top 20):\\n")
print(recent_tech_purchases)''',
    
    # Cell 34: Part 5.3 - Business Intelligence
    '''# Task 5.3: Business Intelligence Chain
high_value_customers <- transactions %>%
  filter(TotalAmount > 200) %>%
  select(CustomerName, CustomerCity, ProductName, TotalAmount) %>%
  arrange(CustomerName, desc(TotalAmount))

# Display results
cat("High-value customers:\\n")
head(high_value_customers, 15)''',
]

# Update code cells with solutions
code_cell_index = 0
for i, cell in enumerate(nb.cells):
    if cell['cell_type'] == 'code' and code_cell_index < len(solutions):
        cell['source'] = solutions[code_cell_index]
        cell['execution_count'] = code_cell_index + 1
        code_cell_index += 1

# Save the solution notebook
with open('data/raw/homework_lesson_3_solution.ipynb', 'w') as f:
    nbformat.write(nb, f)

print("✅ Solution notebook created successfully!")
print(f"Total cells: {len(nb.cells)}")
print(f"Code cells filled: {code_cell_index}")
print(f"Solutions provided: {len(solutions)}")
