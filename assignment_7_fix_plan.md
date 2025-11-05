# Assignment 7 - Fix Plan for Scoring Issue

## Problem Summary
Student received 0.9/100 despite completing all work correctly. The validator couldn't find expected variables due to dataset and naming mismatches.

## Root Causes

### 1. Dataset Mismatch (CRITICAL)
**Problem:** Student used different data files than the solution expects

**Evidence:**
- Student's data: 100 feedback rows, 150 transaction rows, 75 products
- Solution's data: 20 feedback rows, 30 transaction rows, 30 products
- Different column names (PascalCase vs snake_case)
- Different structures (CustomerID vs customer_name in transactions)

**Impact:** Validator looks for specific column names that don't exist

### 2. Variable Naming
**Problem:** Student created `transactions_joined` instead of `transactions_clean`

**Why:** Student's transaction data only had CustomerID, not customer names, so they correctly joined with feedback table

**Impact:** Validator expects `transactions_clean` variable

### 3. Date Format Complexity
**Problem:** Student's data has mixed date formats requiring `parse_date_time()`

**Why:** Data contains both "4/5/24 14:30" and "25-03-2024 16:45:30" formats

**Impact:** Validator expects simple `ymd()` usage

## Fixes Required

### Fix 1: Verify Dataset Source
**Action:** Determine which dataset is correct

**Option A:** Student has wrong data
- Need to provide correct data files
- Student must redo with correct data

**Option B:** Solution/rubric has wrong expectations
- Update rubric to match actual data
- Update validator to check correct column names

**To Check:**
```bash
# Check what data files exist in the data directory
ls -la data/
ls -la data/raw/

# Check if there are multiple versions
find data/ -name "customer_feedback.csv"
find data/ -name "transaction_log.csv"
find data/ -name "product_catalog.csv"
```

### Fix 2: Update Student Code (if using wrong data)
**Changes needed:**

1. **Use correct data files** (if different files exist)
2. **Rename variable:**
   ```r
   # Find all instances of transactions_joined
   # Replace with transactions_clean
   ```

3. **Fix premium product search:**
   ```r
   # In Task 7.1, change:
   str_detect(Category, regex("premium", ignore_case = TRUE))
   # To:
   str_detect(Product_Description, regex("premium|pro|deluxe", ignore_case = TRUE))
   ```

### Fix 3: Update Rubric/Validator (if data is correct)
**Changes needed in rubric:**

1. **Update expected column names:**
   ```json
   {
     "products": {
       "expected_columns": ["ProductID", "Product_Description", "Category", "Price", "In_Stock"]
     },
     "transactions": {
       "expected_columns": ["LogID", "CustomerID", "Transaction_DateTime", "Amount", "Status"]
     },
     "feedback": {
       "expected_columns": ["FeedbackID", "CustomerID", "Customer_Name", "Feedback_Text", "Contact_Info", "Feedback_Date"]
     }
   }
   ```

2. **Accept alternative variable names:**
   - `transactions_clean` OR `transactions_joined`
   - Check for functionality, not exact names

3. **Update date parsing expectations:**
   - Accept `parse_date_time()` as valid alternative to `ymd()`
   - Check that dates are parsed, not which function was used

## Validation Checklist

### Before Resubmission:
- [ ] Correct data files loaded
- [ ] All expected variables exist:
  - [ ] `feedback`
  - [ ] `transactions`
  - [ ] `products`
  - [ ] `products_clean`
  - [ ] `feedback_clean`
  - [ ] `transactions_clean` (not transactions_joined)
  - [ ] `customer_outreach`
  - [ ] `weekday_patterns`
  - [ ] `monthly_patterns`
  - [ ] `top_categories`

### Expected Columns in Each Variable:
- [ ] `products_clean` has: `product_name_clean`, `category_clean`, `is_wireless`, `is_premium`, `is_gaming`, `size_number`
- [ ] `feedback_clean` has: `feedback_clean`, `positive_words`, `negative_words`, `sentiment_score`
- [ ] `transactions_clean` has: `date_parsed`, `trans_year`, `trans_month`, `trans_month_name`, `trans_day`, `trans_weekday`, `trans_quarter`, `is_weekend`, `days_since`, `recency_category`
- [ ] `customer_outreach` has: `first_name`, `personalized_message`

### All Cells Executed:
- [ ] Every code cell shows output
- [ ] No cells show "not executed" or blank output
- [ ] All reflection questions answered

## Testing the Fix

### Step 1: Identify Correct Dataset
```r
# Run this to check current data structure
str(feedback)
str(transactions)
str(products)

# Compare with solution expectations
# Solution expects:
# - feedback: feedback_id, customer_name, feedback_text, rating
# - transactions: transaction_id, customer_name, transaction_date, amount
# - products: product_id, product_name, category, price
```

### Step 2: Test Variable Existence
```r
# Check if all required variables exist
exists("feedback")
exists("transactions")
exists("products")
exists("products_clean")
exists("feedback_clean")
exists("transactions_clean")  # This should be TRUE
exists("customer_outreach")
exists("weekday_patterns")
exists("monthly_patterns")
exists("top_categories")
```

### Step 3: Test Column Existence
```r
# Check if required columns exist
"product_name_clean" %in% colnames(products_clean)
"category_clean" %in% colnames(products_clean)
"is_wireless" %in% colnames(products_clean)
"is_premium" %in% colnames(products_clean)
"is_gaming" %in% colnames(products_clean)
"size_number" %in% colnames(products_clean)

"feedback_clean" %in% colnames(feedback_clean)
"positive_words" %in% colnames(feedback_clean)
"negative_words" %in% colnames(feedback_clean)
"sentiment_score" %in% colnames(feedback_clean)

"date_parsed" %in% colnames(transactions_clean)
"trans_year" %in% colnames(transactions_clean)
"trans_month" %in% colnames(transactions_clean)
"trans_weekday" %in% colnames(transactions_clean)
"is_weekend" %in% colnames(transactions_clean)
"days_since" %in% colnames(transactions_clean)
"recency_category" %in% colnames(transactions_clean)
```

## Expected Outcome After Fix

### Validator Should Find:
- **Variables:** 10/10 (currently 3/25)
- **Columns:** All required columns present
- **Outputs:** All cells executed with visible output

### Expected Score:
- **Technical Execution:** 23-25/25
- **String Manipulation:** 28-30/30
- **Date/Time Operations:** 28-30/30
- **Business Analysis:** 14-15/15

**Total Expected:** 93-100/100 (currently 0.9/100)

## Next Steps

1. **Immediate:** Determine which dataset is correct
   - Check data/ directory for multiple versions
   - Compare with solution file's expected structure
   - Verify with instructor which data students should use

2. **Short-term:** Fix student submission
   - If wrong data: provide correct files and ask for resubmission
   - If correct data: update code to use `transactions_clean` variable name

3. **Long-term:** Prevent future issues
   - Ensure all students receive identical datasets
   - Update validator to be more flexible with variable names
   - Add dataset validation at start of assignment
   - Improve error messages to tell students what's missing
