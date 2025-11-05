# Kathryn Emerick - Assignment 7 Analysis

## Score Issue
**Actual Score:** 60% (based on "Completion: 19 out of 25 sections (76%). Calculated score: 60%")
**Technical Observations:** "Variables found: 1/25"
**Same fundamental issue as Marcelo**

## Key Differences from Marcelo

### 1. Data Source - SAME WRONG DATA
Kathryn also used the WRONG dataset:
- 100 feedback rows (should be 20)
- 150 transaction rows (should be 30)  
- 75 product rows (should be 30)
- Wrong column names (CustomerID, Product_Description, etc.)

### 2. Critical Errors in Kathryn's Code

#### Error 1: Task 4.1 - Date Parsing with Data Loss
```r
transactions_clean <- transactions %>%
  mutate(
    date_parsed = mdy_hm(Transaction_DateTime)   
  ) %>%
  filter(!is.na(date_parsed))  # ⚠️ REMOVES 61 ROWS!
```

**Problem:** Warning says "61 failed to parse" and she FILTERED THEM OUT
**Impact:** Lost 61/150 = 40% of transaction data!
**Why it happened:** Mixed date formats in her dataset

#### Error 2: Task 6.1 - Extracting CustomerID Instead of Name
```r
first_name = str_extract(CustomerID, "^\\w+")
```

**Problem:** Extracting from CustomerID (a number) instead of customer_name
**Result:** First names are "26", "21", "12" instead of actual names
**Output shows:** "Hi 26 , it's been a while!"

#### Error 3: Task 7.1 - Date Display as Timestamps
```r
cat("Date range:", min(transactions_clean$date_parsed), "to", max(transactions_clean$date_parsed), "\n")
```

**Problem:** Displays as Unix timestamps: "1710513000 to 1712327400"
**Should be:** "2024-03-15 to 2024-04-05"

#### Error 4: Task 2.2 - Category Capitalization
```r
category_clean = str_to_title(str_trim(Category))
```

**Problem:** "TV" becomes "Tv" (should stay "TV")
**Minor issue but affects consistency**

## Validator Failure Analysis

### Why "Variables found: 1/25"?

The validator is looking for:
1. ✓ `feedback` - EXISTS
2. ✓ `transactions` - EXISTS  
3. ✓ `products` - EXISTS
4. ✓ `products_clean` - EXISTS
5. ✓ `feedback_clean` - EXISTS
6. ✓ `transactions_clean` - EXISTS
7. ✓ `customer_outreach` - EXISTS
8. ✓ `weekday_patterns` - EXISTS
9. ✓ `monthly_patterns` - EXISTS
10. ✓ `top_categories` - EXISTS

**All variables exist!** So why only 1/25?

### The Real Issue: Column Names

The validator checks for specific column names WITHIN the dataframes:

**Expected in transactions_clean:**
- `transaction_date` → She has `Transaction_DateTime`
- `customer_name` → She has `CustomerID` (no names!)
- `date_parsed` → She has this ✓
- `trans_year` → She has this ✓
- etc.

**Expected in products_clean:**
- `product_name` → She has `Product_Description`
- `category` → She has `Category`
- `product_name_clean` → She has this ✓
- etc.

**Expected in feedback_clean:**
- `feedback_text` → She has `Feedback_Text`
- `customer_name` → She has `CustomerID`
- `feedback_clean` → She has this ✓
- etc.

## Comparison: Kathryn vs Marcelo

| Aspect | Marcelo | Kathryn |
|--------|---------|---------|
| **Dataset** | Wrong (same as Kathryn) | Wrong |
| **Data Loss** | None - handled mixed formats | Lost 61/150 rows (40%!) |
| **Customer Names** | Joined tables to get names | Used CustomerID as "names" |
| **Date Parsing** | parse_date_time() - correct | mdy_hm() + filter - wrong |
| **Adaptability** | Excellent - solved harder problem | Struggled with complexity |
| **Score** | 0.9/100 | 60/100 |
| **Actual Performance** | ~95/100 | ~70/100 |

## Specific Code Issues

### Issue 1: Data Loss (CRITICAL)
```r
# WRONG - Kathryn's approach:
transactions_clean <- transactions %>%
  mutate(date_parsed = mdy_hm(Transaction_DateTime)) %>%
  filter(!is.na(date_parsed))  # Loses 61 rows!

# RIGHT - Marcelo's approach:
transactions_clean <- transactions %>%
  mutate(
    date_parsed = parse_date_time(
      Transaction_DateTime,
      orders = c("mdy HM", "dmy HMS", "dmy HM", "ymd_HMS"),
      quiet = TRUE
    )
  )
# No data loss!
```

### Issue 2: Customer Names
```r
# WRONG - Kathryn:
first_name = str_extract(CustomerID, "^\\w+")
# Result: "26", "21", "12"

# RIGHT - Marcelo:
# First joined feedback to get customer names
transactions_joined <- transactions_clean %>%
  left_join(feedback_cleaned %>% select(CustomerID, Customer_Name), by = "CustomerID")
# Then extracted:
first_name = str_extract(Customer_Name, "^\\w+")
# Result: "Susan", "Mary", "Bob"
```

### Issue 3: Date Display
```r
# WRONG - Kathryn:
cat("Date range:", min(transactions_clean$date_parsed), "to", max(transactions_clean$date_parsed), "\n")
# Output: "Date range: 1710513000 to 1712327400"

# RIGHT:
earliest <- min(transactions_clean$date_parsed)
latest <- max(transactions_clean$date_parsed)
cat("Date range:", format(earliest, "%Y-%m-%d"), "to", format(latest, "%Y-%m-%d"), "\n")
# Output: "Date range: 2024-03-15 to 2024-04-05"
```

## Why Kathryn Scored Higher Than Marcelo

Despite having MORE errors, Kathryn scored 60% vs Marcelo's 0.9%. Why?

**Hypothesis:** The validator has a bug or inconsistency:
- Marcelo's score: "Completion: 0/0 sections (0%). Score: 2%"
- Kathryn's score: "Completion: 19 out of 25 sections (76%). Calculated score: 60%"

This suggests:
1. The validator ran differently for each student
2. Or there's a threshold issue where Marcelo fell below minimum
3. Or the validator version changed between submissions

## What Kathryn Did Right

1. ✓ Loaded packages correctly
2. ✓ Imported data correctly
3. ✓ Used str_trim(), str_to_title(), str_to_lower() correctly
4. ✓ Used str_detect(), str_extract(), str_count() correctly
5. ✓ Extracted date components correctly
6. ✓ Created recency categories correctly
7. ✓ Grouped and summarized data correctly
8. ✓ Answered reflection questions thoughtfully

## What Kathryn Did Wrong

1. ✗ Lost 40% of transaction data by filtering NAs
2. ✗ Used CustomerID instead of customer names
3. ✗ Displayed dates as timestamps
4. ✗ Used wrong dataset (same as Marcelo)
5. ✗ Didn't handle mixed date formats properly

## Recommendations for Kathryn

### Immediate Fixes:

1. **Use correct dataset from ./data/**
   ```r
   feedback <- read_csv("data/customer_feedback.csv")
   transactions <- read_csv("data/transaction_log.csv")
   products <- read_csv("data/product_catalog.csv")
   ```

2. **Fix date parsing (with correct data, this becomes simple):**
   ```r
   transactions_clean <- transactions %>%
     mutate(date_parsed = ymd(transaction_date))  # Simple!
   ```

3. **Fix customer name extraction:**
   ```r
   # With correct data, customer_name is already in transactions
   first_name = str_extract(customer_name, "^\\w+")
   ```

4. **Fix date display:**
   ```r
   earliest <- min(transactions_clean$date_parsed)
   latest <- max(transactions_clean$date_parsed)
   cat("Date range:", format(earliest, "%Y-%m-%d"), "to", format(latest, "%Y-%m-%d"), "\n")
   ```

## Expected Outcome with Correct Data

With the correct dataset:
- No data loss (all dates parse correctly)
- Customer names available directly
- Simple date parsing with ymd()
- All validator checks pass
- Expected score: 90-95/100

## Root Cause: Same as Marcelo

**Both students used the wrong dataset.**

The fundamental issue is NOT the students' coding ability - it's that they're working with data that doesn't match the assignment expectations.

### Evidence:
1. Both have 100/150/75 rows instead of 20/30/30
2. Both have wrong column names (PascalCase vs snake_case)
3. Both have CustomerID instead of customer_name in transactions
4. Both have mixed date formats requiring complex parsing

### Solution:
**Provide correct data files and have both students redo the assignment.**

With correct data:
- Marcelo would score ~95/100 (excellent adaptation skills)
- Kathryn would score ~90/100 (good execution, minor errors)

## Key Insight

Kathryn's higher score (60% vs 0.9%) despite having MORE actual errors suggests the validator has inconsistent behavior or scoring thresholds. This needs investigation.
