# Lesson 8: Advanced Data Wrangling Techniques & Best Practices

# Load necessary packages
library(tidyverse) # includes dplyr, tidyr, ggplot2

# 1. Chaining operations for complex workflows

# Example: Calculate average sales per product category per region
# Create a more complex dummy sales dataset
set.seed(123)
complex_sales_data <- data.frame(
  OrderID = 1:100,
  Product = sample(c("Laptop", "Mouse", "Keyboard", "Monitor", "Webcam", "Headphones"), 100, replace = TRUE),
  Category = sample(c("Electronics", "Peripherals"), 100, replace = TRUE, prob = c(0.6, 0.4)),
  Region = sample(c("North", "South", "East", "West"), 100, replace = TRUE),
  Sales = round(runif(100, 50, 1500), 2),
  Quantity = sample(1:5, 100, replace = TRUE),
  OrderDate = sample(seq(as.Date("2023-01-01"), as.Date("2023-12-31"), by = "day"), 100, replace = TRUE)
)

print("Complex Sales Data (first 10 rows):")
print(head(complex_sales_data))

# Chained operations: Filter, mutate, group, summarize, arrange
summary_sales_by_category_region <- complex_sales_data %>%
  filter(Sales > 100) %>%
  mutate(Revenue = Sales * Quantity) %>%
  group_by(Category, Region) %>%
  summarize(
    TotalRevenue = sum(Revenue),
    AverageSalesPerOrder = mean(Sales),
    NumberOfOrders = n(),
    .groups = "drop"
  ) %>%
  arrange(desc(TotalRevenue))

print("Summary Sales by Category and Region:")
print(summary_sales_by_category_region)

# 2. Conditional transformations (case_when())

# Categorize sales into tiers: Low, Medium, High
classified_sales <- complex_sales_data %>%
  mutate(
    SalesTier = case_when(
      Sales < 200 ~ "Low",
      Sales >= 200 & Sales < 800 ~ "Medium",
      Sales >= 800 ~ "High",
      TRUE ~ "Unknown" # Default case for any other condition
    )
  )

print("Sales Data with Sales Tier (first 10 rows):")
print(head(classified_sales))

# 3. Data validation and assertion

# Check if there are any missing values in key columns
complex_sales_data %>%
  summarise(
    MissingSales = sum(is.na(Sales)),
    MissingQuantity = sum(is.na(Quantity))
  )

# Assert that all Sales values are positive
# stopifnot(all(complex_sales_data$Sales > 0))
# If the above line throws an error, it means there are non-positive sales.

# Using assertr package for more robust assertions (install.packages("assertr"))
# library(assertr)
# complex_sales_data %>%
#   verify(Sales > 0) %>%
#   assert(is.numeric, Sales, Quantity) # Assert columns are numeric

# 4. Reproducible workflows (R Markdown)
# R Markdown allows you to create dynamic reports with R code, output, and narrative text.
# It combines R code, its output, and your comments in a single .Rmd file.
# This is crucial for reproducible research and analysis.

# To demonstrate, we can create a simple R Markdown file structure.
# (This part is conceptual, as creating and knitting .Rmd files is typically done in RStudio or VS Code with R extension)

# Example content for an R Markdown file (save as e.g., `report.Rmd`)
# ---
# title: "Sales Analysis Report"
# author: "Your Name"
# date: "`r Sys.Date()`"
# output: html_document
# ---
#
# ```{r setup, include=FALSE}
# knitr::opts_chunk$set(echo = TRUE)
# library(tidyverse)
# ```
#
# ## Introduction
# This report analyzes sales data to identify key trends.
#
# ## Data Loading and Wrangling
# ```{r data_load}
# sales_data <- read_csv("path/to/your/sales_data.csv")
# cleaned_sales <- sales_data %>%
#   drop_na() %>%
#   mutate(Revenue = Sales * Quantity)
# ```
#
# ## Summary Statistics
# ```{r summary_stats}
# cleaned_sales %>%
#   group_by(Category) %>%
#   summarize(TotalRevenue = sum(Revenue))
# ```
#
# ## Visualization
# ```{r sales_plot, echo=FALSE}
# cleaned_sales %>%
#   ggplot(aes(x = Category, y = Revenue, fill = Category)) +
#   geom_boxplot() +
#   labs(title = "Revenue Distribution by Category")
# ```

# 5. Common data wrangling pitfalls and how to avoid them
# - Not understanding your data: Always inspect data with `head()`, `str()`, `summary()`, `View()`.
# - Ignoring missing values: Decide on a strategy (remove, impute) and document it.
# - Inconsistent data entry: Use `str_to_lower()`, `str_trim()`, `factor()` to standardize.
# - Not handling dates/times correctly: Use `lubridate` for robust parsing and manipulation.
# - Not backing up original data: Always work on copies or use version control.
# - Not documenting your steps: Use R Markdown or add comments to your scripts.

# 6. Introduction to data visualization with ggplot2 (brief overview of wrangled data visualization)

# Basic Scatter Plot: Sales vs. Quantity
ggplot(complex_sales_data, aes(x = Quantity, y = Sales)) +
  geom_point() +
  labs(title = "Sales vs. Quantity", x = "Quantity", y = "Sales Amount")

# Bar Chart: Total Sales by Region
complex_sales_data %>%
  group_by(Region) %>%
  summarize(TotalSales = sum(Sales), .groups = "drop") %>%
  ggplot(aes(x = Region, y = TotalSales, fill = Region)) +
  geom_col() +
  labs(title = "Total Sales by Region", x = "Region", y = "Total Sales")

# Histogram: Distribution of Sales
ggplot(complex_sales_data, aes(x = Sales)) +
  geom_histogram(binwidth = 100, fill = "skyblue", color = "black") +
  labs(title = "Distribution of Sales", x = "Sales Amount", y = "Frequency")

# Boxplot: Sales Distribution by Category
ggplot(complex_sales_data, aes(x = Category, y = Sales, fill = Category)) +
  geom_boxplot() +
  labs(title = "Sales Distribution by Product Category", x = "Product Category", y = "Sales Amount")

# Hands-on Exercise: End-to-end data wrangling project using a new, slightly more complex dataset, culminating in a simple visualization.
# Assume a dataset `customer_feedback.csv` with columns: `FeedbackID`, `CustomerID`, `Rating` (1-5), `Comment`, `SubmissionDate`.
# Task: Load data, clean comments (remove punctuation, convert to lowercase), calculate average rating per customer, and visualize rating distribution.

# Dummy data for exercise (in real scenario, this would be loaded from a CSV)
exercise_feedback_data <- data.frame(
  FeedbackID = 1:10,
  CustomerID = c(1, 2, 1, 3, 2, 4, 1, 3, 5, 2),
  Rating = c(4, 5, 3, 4, 5, 2, 4, 3, 5, 4),
  Comment = c("Great product!", "Very satisfied.", "Could be better.", "Good value for money.", "Excellent service!",
              "Not happy with delivery.", "Love it!", "Average experience.", "Highly recommend.", "Works well."),
  SubmissionDate = as.Date(c("2024-06-01", "2024-06-01", "2024-06-02", "2024-06-02", "2024-06-03",
                              "2024-06-03", "2024-06-04", "2024-06-04", "2024-06-05", "2024-06-05"))
)

print("Exercise Feedback Data:")
print(exercise_feedback_data)

# Solution (for instructor/self-check):
cleaned_feedback <- exercise_feedback_data %>%
  mutate(
    CleanedComment = str_to_lower(str_replace_all(Comment, "[[:punct:]]", "")) # Remove punctuation and convert to lowercase
  )

summary_ratings <- cleaned_feedback %>%
  group_by(CustomerID) %>%
  summarize(AverageRating = mean(Rating), .groups = "drop")

print("Summary Ratings per Customer:")
print(summary_ratings)

# Visualization of Rating Distribution
ggplot(cleaned_feedback, aes(x = factor(Rating))) +
  geom_bar(fill = "lightgreen", color = "black") +
  labs(title = "Distribution of Customer Ratings", x = "Rating (1-5)", y = "Count") +
  theme_minimal()


