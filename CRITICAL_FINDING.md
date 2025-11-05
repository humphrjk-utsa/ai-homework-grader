# CRITICAL FINDING - Assignment 7

## The Real Issue Discovered

After examining the actual template and data files, I found the root cause:

### There Are TWO Different Versions of This Assignment

#### Version 1 (Original - in `/data/`):
- **Data:** 20/30/30 rows
- **Columns:** `feedback_id`, `customer_name`, `feedback_text`, `transaction_date`, `product_name`, etc.
- **Solution:** `/data/raw/homework_lesson_7_string_datetime_SOLUTION.ipynb`
- **Template:** `/data/raw/homework_lesson_7_string_datetime.ipynb`
- **Format:** Simple, clean data with customer names in transactions

#### Version 2 (Actual - in `/data/processed/`):
- **Data:** 100/150/75 rows
- **Columns:** `FeedbackID`, `CustomerID`, `Feedback_Text`, `Transaction_DateTime`, `Product_Description`, etc.
- **Solution:** DOES NOT EXIST
- **Template:** `/data/raw/homework_lesson_7_string_datetime (1).ipynb`
- **Format:** Complex data with mixed date formats, NO customer names in transactions

### The Problem

**Students are using Version 2 data, but the rubric/validator expects Version 1 structure!**

This is why:
1. Both Marcelo and Kathryn "failed" - they used Version 2 data
2. Validator looks for Version 1 column names
3. No solution exists for Version 2
4. Students had to adapt on their own

### The Evidence

**Version 2 Data Structure (what students have):**
```
customer_feedback (1).csv: 101 rows
- FeedbackID, CustomerID, Feedback_Text, Contact_Info, Feedback_Date

transaction_log.csv: 150 rows  
- LogID, CustomerID, Transaction_DateTime, Amount, Status
- NO customer names! Only CustomerID

product_catalog.csv: 76 rows
- ProductID, Product_Description, Category, Price, In_Stock
```

**Version 1 Data Structure (what validator expects):**
```
customer_feedback.csv: 20 rows
- feedback_id, customer_name, feedback_text, rating

transaction_log.csv: 30 rows
- transaction_id, customer_name, transaction_date, amount
- HAS customer names!

product_catalog.csv: 30 rows
- product_id, product_name, category, price
```

### Why This Happened

Looking at the file paths:
- Version 1: `/data/` (simple teaching data)
- Version 2: `/data/processed/` (realistic business data)

**Hypothesis:** Someone created a more realistic version of the assignment with messier data, but:
1. Didn't update the rubric
2. Didn't create a new solution
3. Didn't update the validator
4. Students got the new data but old expectations

### What Students Actually Did

**Both Marcelo and Kathryn:**
- ✓ Used the correct data for their template
- ✓ Adapted to complex data structure
- ✗ Failed validator because it expects different structure

**Marcelo's Adaptation (Excellent):**
- Joined tables to get customer names
- Handled mixed date formats
- No data loss
- **This is ADVANCED work!**

**Kathryn's Adaptation (Struggled):**
- Tried to use CustomerID as names
- Lost 40% of data
- Didn't handle complexity well

### The Solution

We need to create THREE things:

1. **New Solution File** - For Version 2 data (processed/)
2. **Updated Rubric** - Matching Version 2 structure
3. **Updated Validator** - Checking Version 2 column names

OR

**Standardize on Version 1:**
- Move all students to simple data
- Use existing solution/rubric
- Much easier for teaching

### Recommendation

**Option A: Use Version 1 (Simple Data) - RECOMMENDED**
- Pros: Solution exists, rubric works, easier for students
- Cons: Less realistic data
- Action: Have students redo with data from `/data/` not `/data/processed/`

**Option B: Create Version 2 Solution**
- Pros: More realistic, teaches adaptation
- Cons: Need to create solution, update rubric, update validator
- Action: I can create this now

### Immediate Action Required

1. **Decide which version to use**
2. **Communicate to students** which data files to use
3. **Update validator** to match chosen version
4. **Allow resubmissions** with correct data

### Why Scores Were Wrong

**Marcelo (0.9/100):**
- Used Version 2 data correctly
- Validator expected Version 1
- Score should be 95/100 for Version 2 OR 95/100 if redone with Version 1

**Kathryn (60/100):**
- Used Version 2 data with errors
- Validator expected Version 1  
- Score should be 70/100 for Version 2 OR 90/100 if redone with Version 1

Both students were penalized for using the "wrong" data when they were actually using the data that matched their template!
