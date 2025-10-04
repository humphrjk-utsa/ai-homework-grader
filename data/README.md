# Sample Datasets for Data Wrangling in R Course

This directory contains realistic business datasets designed for the 8-lesson Data Wrangling in R course. Each dataset corresponds to specific lessons and homework assignments.

## Dataset Overview

### Lesson 1: Introduction to R, RStudio, and Data Import
- **sales_data.csv** - Basic sales transactions for import practice
- **customer_ratings.csv** - Customer satisfaction ratings
- **customer_comments.csv** - Customer feedback comments

### Lesson 2: Data Cleaning - Handling Missing Values and Outliers
- **messy_sales_data.csv** - Sales data with intentional quality issues including:
  - Missing values in multiple columns
  - Outliers in sales amounts
  - Inconsistent categorical data
  - Invalid dates

### Lesson 3: Data Transformation with dplyr - Part 1
- **retail_transactions.csv** - Comprehensive retail transaction data for filtering, selecting, and arranging exercises

### Lesson 4: Data Transformation with dplyr - Part 2
- **company_sales_data.csv** - Company sales data for advanced transformations, grouping, and KPI calculations

### Lesson 5: Data Reshaping with tidyr
- **quarterly_sales_wide.csv** - Sales data in wide format for pivot_longer() practice
- **survey_responses_long.csv** - Survey data in long format for pivot_wider() practice
- **employee_skills_wide.csv** - Employee skills matrix for reshaping exercises

### Lesson 6: Combining Datasets - Joins
- **customers.csv** - Customer information
- **orders.csv** - Order records (some with invalid customer IDs for join practice)
- **order_items.csv** - Individual items within orders
- **products.csv** - Product catalog
- **suppliers.csv** - Supplier information

### Lesson 7: String Manipulation and Date/Time Data
- **customer_feedback.csv** - Customer feedback with messy text data
- **transaction_log.csv** - Transaction logs with various date/time formats
- **product_catalog.csv** - Product descriptions with inconsistent formatting

### Lesson 8: Advanced Data Wrangling Techniques & Best Practices
- **raw_sales_data.csv** - Complex, messy sales data for capstone project

## Data Characteristics

### Realistic Business Context
All datasets simulate real business scenarios that students might encounter in their careers:
- E-commerce transactions
- Customer feedback and surveys
- Product catalogs and inventory
- Sales performance data
- Marketing campaigns

### Intentional Data Quality Issues
Many datasets include common data quality problems:
- Missing values (various patterns)
- Outliers and anomalous values
- Inconsistent formatting
- Duplicate records
- Invalid data types
- Mixed case text
- Various date formats

### Progressive Complexity
Datasets increase in complexity throughout the course:
- **Lessons 1-2**: Simple, clean data for basic operations
- **Lessons 3-4**: Moderate complexity with realistic business scenarios
- **Lessons 5-6**: Multiple related tables requiring joins and reshaping
- **Lessons 7-8**: Complex, messy data requiring comprehensive cleaning

## Usage Instructions

### For Instructors
1. Distribute the entire `sample_datasets` folder to students
2. Each homework assignment references specific datasets
3. Students should place datasets in their R working directory
4. Datasets are designed to work with VS Code Codespaces

### For Students
1. Download the sample_datasets.zip file from the course website
2. Extract all files to your R working directory
3. Use `read_csv()` or `read.csv()` to import CSV files
4. Follow homework instructions for specific dataset usage

## Dataset Details

### File Formats
- **CSV files**: Most datasets for easy import with `read_csv()`
- **Excel files**: Some datasets for `read_excel()` practice (when available)

### Data Volume
- Small datasets (50-100 rows): For quick exercises and demonstrations
- Medium datasets (200-500 rows): For realistic analysis practice
- Larger datasets (500+ rows): For performance and scalability lessons

### Column Types
Each dataset includes a mix of:
- Numerical data (integers, decimals)
- Categorical data (factors, characters)
- Date/time data (various formats)
- Text data (for string manipulation)
- Boolean/logical data

## Data Dictionary

### Common Column Patterns
- **ID columns**: CustomerID, TransactionID, ProductID, etc.
- **Date columns**: Various formats to practice date parsing
- **Amount columns**: Sales amounts, costs, prices (with some outliers)
- **Category columns**: Product categories, regions, departments
- **Text columns**: Names, descriptions, feedback (with formatting issues)

### Missing Value Patterns
- **Random missing**: Scattered throughout datasets
- **Systematic missing**: Entire columns or specific patterns
- **Problematic values**: Empty strings, spaces, invalid entries

## Best Practices for Use

### Data Import
```r
# Basic import
sales_data <- read_csv("sample_datasets/sales_data.csv")

# Import with specific column types
sales_data <- read_csv("sample_datasets/sales_data.csv",
                      col_types = cols(
                        Date = col_date(),
                        Amount = col_double()
                      ))
```

### Working Directory
Ensure datasets are in your R working directory:
```r
# Check current directory
getwd()

# List files to verify datasets are present
list.files("sample_datasets")
```

### Data Exploration
Always start with basic exploration:
```r
# Basic inspection
head(sales_data)
str(sales_data)
summary(sales_data)

# Check for missing values
sum(is.na(sales_data))
```

## Support

If you encounter issues with any datasets:
1. Check that files are in the correct directory
2. Verify file names match exactly (case-sensitive)
3. Ensure you have the required R packages installed
4. Refer to the homework assignment instructions for specific guidance

## License

These datasets are created for educational purposes and are freely available for use in the Data Wrangling in R course.

