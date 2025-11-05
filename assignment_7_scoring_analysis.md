# Assignment 7 Scoring Analysis - Marcelo Coronel

## Executive Summary
**Actual Score:** 0.9 / 100  
**Expected Score:** ~80-85 / 100  
**Primary Issue:** Validator cannot find expected variable names due to dataset mismatch

## Critical Discovery

The student used **DIFFERENT DATA FILES** than the solution/template expects:

### Student's Data Files:
- `customer_feedback.csv` - 100 rows, columns: FeedbackID, CustomerID, Customer_Name, Feedback_Text, Contact_Info, Feedback_Date
- `transaction_log.csv` - 150 rows, columns: LogID, CustomerID, Transaction_DateTime, Amount, Status
- `product_catalog.csv` - 75 rows, columns: ProductID, Product_Description, Category, Price, In_Stock

### Expected Data Files (from solution):
- `customer_feedback.csv` - 20 rows, columns: feedback_id, customer_name, feedback_text, rating
- `transaction_log.csv` - 30 rows, columns: transaction_id, customer_name, transaction_date, amount
- `product_catalog.csv` - 30 rows, columns: product_id, product_name, category, price

## Why the Validator Failed

### 1. **Column Name Mismatches**
The rubric expects specific column names that don't exist in the student's dataset:

**Products:**
- Expected: `product_name` → Student has: `Product_Description`
- Expected: `category` → Student has: `Category`

**Transactions:**
- Expected: `transaction_date` → Student has: `Transaction_DateTime`
- Expected: `customer_name` → Student has: `CustomerID` (no names!)

**Feedback:**
- Expected: `feedback_text` → Student has: `Feedback_Text`
- Expected: `customer_name` → Student has: `Customer_Name`

### 2. **Variable Name Issues**
The student created `transactions_joined` instead of `transactions_clean` because they had to join customer names from the feedback table (since transactions only had CustomerID).

This is actually **EXTRA WORK** the student did correctly, but the validator doesn't recognize it.

### 3. **Date Format Complexity**
The student's data has mixed date formats:
- Most: `"4/5/24 14:30"` (mdy with time)
- Some: `"25-03-2024 16:45:30"` (dmy with time)

The solution expects simple dates: `"2024-01-15"` (ymd)

The student correctly used `parse_date_time()` to handle multiple formats, but the rubric expects simple `ymd()`.

## Specific Code Issues vs Rubric Expectations

### Issue 1: Task 3.1 - Premium Detection Pattern
**Feedback Says:** "Missing 'deluxe' in premium detection"
**Reality:** Student used `"pro|premium|deluxe"` but the feedback says they only used `"pro|premium"`
**Verdict:** FALSE POSITIVE - Student's code is correct

### Issue 2: Task 4.1 - Date Parsing
**Feedback Says:** "Uses parse_date_time() which is more complex than required"
**Reality:** Student's data HAS mixed formats requiring parse_date_time()
**Verdict:** Student adapted correctly to their dataset

### Issue 3: Task 5.2 - Recency Categorization
**Feedback Says:** "Logic error in case_when()"
**Student's Code:**
```r
recency_category = case_when(
  days_since <= 30 ~ "Recent",
  days_since <= 90 ~ "Moderate",
  days_since > 90  ~ "At Risk",
  TRUE ~ NA_character_
)
```
**Verdict:** CORRECT - No logic error exists

### Issue 4: Task 6.1 - Personalized Messages
**Feedback Says:** "Same message for all customers"
**Reality:** Student's code has correct case_when() with different messages per category
**Verdict:** FALSE POSITIVE - Code is correct

### Issue 5: Task 7.1 - Premium Products Calculation
**Feedback Says:** "Searched in Category instead of Product_Description"
**Student's Code:** `str_detect(Category, regex("premium", ignore_case = TRUE))`
**Issue:** Student's dataset has `Product_Description` not `product_name`, and searching in Category is actually wrong
**Verdict:** TRUE ERROR - Should search in Product_Description

### Issue 6: Task 7.1 - Most Common Category
**Feedback Says:** "Used count() and slice(1) instead of arrange()"
**Student's Code:**
```r
most_common_category <- products_clean %>%
  count(category_clean, sort = TRUE) %>%
  slice(1) %>%
  pull(category_clean)
```
**Verdict:** CORRECT APPROACH - This is actually better than arrange()

## Root Cause Analysis

### Primary Problem: Dataset Mismatch
The grading system expects:
1. Specific column names (lowercase with underscores)
2. Specific variable names (`transactions_clean` not `transactions_joined`)
3. Simple date formats
4. Customer names in transactions table

The student received:
1. Different column names (PascalCase)
2. More complex data requiring joins
3. Mixed date formats
4. No customer names in transactions (only IDs)

### Secondary Problem: Validator Logic
The validator checks for:
- Exact variable names: `transactions_clean`, `products_clean`, `feedback_clean`
- Exact column names in those variables
- Specific function usage patterns

The validator found: "Variables found: 3/25"

This means it only found 3 of the 25 expected variables, likely:
- `feedback` ✓
- `transactions` ✓  
- `products` ✓

But NOT:
- `transactions_clean` (student used `transactions_joined`)
- Correct column names within dataframes

## What the Student Did Right

1. **Adapted to dataset complexity** - Correctly joined tables to get customer names
2. **Handled mixed date formats** - Used parse_date_time() appropriately
3. **Extra data cleaning** - Replaced NA names with "Valued Customer"
4. **Correct string functions** - All str_* functions used properly
5. **Correct date functions** - All lubridate functions used properly
6. **Business analysis** - Excellent insights and interpretations
7. **Reflection questions** - Thoughtful, specific answers

## What Needs to be Fixed

### For the Student's Code:

1. **Use expected variable name:**
   ```r
   # Change from:
   transactions_joined <- ...
   # To:
   transactions_clean <- ...
   ```

2. **Fix premium product search:**
   ```r
   # Change from:
   str_detect(Category, regex("premium", ignore_case = TRUE))
   # To:
   str_detect(Product_Description, regex("premium", ignore_case = TRUE))
   ```

3. **Ensure all expected variables exist:**
   - `products_clean` ✓ (exists)
   - `feedback_clean` ✓ (exists)
   - `transactions_clean` ✗ (needs rename from transactions_joined)
   - `customer_outreach` ✓ (exists)
   - `weekday_patterns` ✓ (exists)
   - `monthly_patterns` ✓ (exists)
   - `top_categories` ✓ (exists)

### For the Grading System:

1. **Provide correct dataset** - Students should receive the same data as the solution
2. **Update rubric** - If using different data, update expected column names
3. **Flexible validation** - Check for functionality, not just exact variable names
4. **Better error messages** - Tell students which variables are missing

## Recommended Actions

### Immediate Fix (Student):
1. Rename `transactions_joined` to `transactions_clean` throughout
2. Fix premium product detection to search Product_Description
3. Re-run all cells to ensure outputs are visible
4. Resubmit

### Long-term Fix (Instructor):
1. Verify all students receive identical datasets
2. Update data generation scripts to match solution expectations
3. Add dataset validation at start of assignment
4. Improve validator to check functionality over exact naming

## Estimated Correct Score

If the validator could properly assess the student's work:

- **Technical Execution (25%):** 22/25 (minor premium search error)
- **String Manipulation (30%):** 28/30 (all functions correct)
- **Date/Time Operations (30%):** 30/30 (perfect, even handled complexity)
- **Business Analysis (15%):** 15/15 (excellent insights)
- **Reflection Questions (not in rubric but mentioned):** Full credit

**Estimated Total:** 95/100

The 0.9 score is due to validator failure, not student performance.
