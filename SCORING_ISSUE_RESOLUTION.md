# Assignment 7 Scoring Issue - RESOLUTION

## THE PROBLEM

**Student Score:** 0.9 / 100  
**Actual Performance:** ~95 / 100  
**Issue:** Student used WRONG DATA FILES

## ROOT CAUSE DISCOVERED

### Correct Data Files (in ./data/):
```
customer_feedback.csv:
- Columns: feedback_id, customer_name, feedback_text, rating
- Rows: 20
- Format: Simple, clean data

transaction_log.csv:
- Columns: transaction_id, customer_name, transaction_date, amount  
- Rows: 30
- Format: Simple dates (2024-01-15)

product_catalog.csv:
- Columns: product_id, product_name, category, price
- Rows: 30
- Format: Messy text (extra spaces, mixed case)
```

### Student's Data Files (WRONG - from different source):
```
customer_feedback.csv:
- Columns: FeedbackID, CustomerID, Customer_Name, Feedback_Text, Contact_Info, Feedback_Date
- Rows: 100
- Format: Complex, different structure

transaction_log.csv:
- Columns: LogID, CustomerID, Transaction_DateTime, Amount, Status
- Rows: 150
- Format: Mixed date formats, NO customer names (only IDs)

product_catalog.csv:
- Columns: ProductID, Product_Description, Category, Price, In_Stock
- Rows: 75
- Format: Different column names
```

## WHY THE VALIDATOR FAILED

The validator checks for:
1. ✗ Column name `product_name` → Student has `Product_Description`
2. ✗ Column name `transaction_date` → Student has `Transaction_DateTime`
3. ✗ Column name `customer_name` in transactions → Student has `CustomerID`
4. ✗ Variable name `transactions_clean` → Student created `transactions_joined` (because they had to join tables to get customer names)

**Result:** Validator found only 3/25 expected variables → Score: 0.9/100

## WHAT THE STUDENT DID

The student actually did EXCELLENT work:
- ✓ Correctly adapted to their complex dataset
- ✓ Properly joined tables to get customer names
- ✓ Handled mixed date formats with parse_date_time()
- ✓ All string functions used correctly
- ✓ All date functions used correctly
- ✓ Excellent business analysis
- ✓ Thoughtful reflection answers

**The student solved a HARDER problem than the assignment required!**

## THE FIX

### Option 1: Student Redoes with Correct Data (RECOMMENDED)

**Steps:**
1. Student loads data from `./data/` directory (not from wherever they got it)
2. Student follows template exactly as written
3. Much simpler assignment - no joins needed, simple date parsing
4. Should take 30-60 minutes to redo

**New code structure:**
```r
# Task 1.2: Import from correct location
feedback <- read_csv("customer_feedback.csv")  # From ./data/
transactions <- read_csv("transaction_log.csv")  # From ./data/
products <- read_csv("product_catalog.csv")  # From ./data/

# Task 4.1: Simple date parsing (no parse_date_time needed)
transactions_clean <- transactions %>%
  mutate(date_parsed = ymd(transaction_date))  # Simple!

# Task 5.1: No joining needed - customer_name already in transactions
transactions_clean <- transactions_clean %>%
  mutate(days_since = as.numeric(today() - date_parsed))

# Task 6.1: Direct access to customer names
customer_outreach <- transactions_clean %>%
  mutate(first_name = str_extract(customer_name, "^\\w+"))
```

### Option 2: Update Validator to Accept Student's Approach (NOT RECOMMENDED)

This would require:
- Accepting multiple column name formats
- Accepting `transactions_joined` as equivalent to `transactions_clean`
- Accepting `parse_date_time()` as equivalent to `ymd()`
- Much more complex validation logic

## SPECIFIC ERRORS IN STUDENT'S CURRENT CODE

Even with wrong data, student made 2 small errors:

### Error 1: Premium Product Search (Task 7.1)
```r
# WRONG:
str_detect(Category, regex("premium", ignore_case = TRUE))

# RIGHT:
str_detect(Product_Description, regex("premium|pro|deluxe", ignore_case = TRUE))
```

### Error 2: Variable Naming
```r
# Used: transactions_joined
# Should be: transactions_clean
```

Everything else is actually correct!

## INSTRUCTIONS FOR STUDENT

### Quick Fix (Redo with Correct Data):

1. **Start fresh with correct data:**
   ```r
   setwd("/workspaces/Fall2025-MS3083-Base_Template")  # Or wherever the project root is
   
   feedback <- read_csv("data/customer_feedback.csv")
   transactions <- read_csv("data/transaction_log.csv")
   products <- read_csv("data/product_catalog.csv")
   ```

2. **Verify you have correct data:**
   ```r
   # Should see:
   colnames(feedback)  # feedback_id, customer_name, feedback_text, rating
   colnames(transactions)  # transaction_id, customer_name, transaction_date, amount
   colnames(products)  # product_id, product_name, category, price
   
   nrow(feedback)  # Should be 20
   nrow(transactions)  # Should be 30
   nrow(products)  # Should be 30
   ```

3. **Follow template exactly:**
   - Use `product_name` not `Product_Description`
   - Use `transaction_date` not `Transaction_DateTime`
   - Use `transactions_clean` not `transactions_joined`
   - Use `ymd()` not `parse_date_time()`
   - No joining needed - customer names already in transactions

4. **Key simplifications:**
   - No need to join tables
   - No need for parse_date_time()
   - No need to handle NA customer names
   - Much simpler overall!

5. **Run all cells and resubmit**

## EXPECTED OUTCOME

With correct data:
- Assignment is much simpler
- All validator checks will pass
- Expected score: 95-100/100

## LESSONS LEARNED

### For Students:
- Always verify you're using the correct data files
- Check column names match the template
- If something seems overly complex, you might have wrong data

### For Instructors:
- Add data validation at start of assignment
- Check that all students have identical data files
- Provide clear path to data files in instructions
- Consider adding a "data verification" cell that checks structure

## RECOMMENDATION

**Have student redo with correct data.** This is the cleanest solution and will take less time than trying to fix the current submission. The student clearly has the skills - they just need to use the right dataset.

Current submission shows the student can:
- ✓ Handle complex data structures
- ✓ Perform table joins
- ✓ Handle mixed date formats
- ✓ Use all required functions correctly
- ✓ Provide business insights

With correct data, they'll easily score 95-100/100.
