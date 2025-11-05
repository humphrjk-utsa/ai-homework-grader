# Assignment 7 - Final Action Plan

## Executive Summary

**Root Cause:** Two different versions of the assignment exist. Students used Version 2 (processed data), but the validator expects Version 1 (simple data).

**Impact:** Both students scored far below their actual performance level.

**Solution:** Choose one version and update all materials to match.

## The Two Versions

### Version 1: Simple Teaching Data
- **Location:** `/data/`
- **Rows:** 20/30/30
- **Columns:** snake_case (`feedback_id`, `customer_name`, `transaction_date`, `product_name`)
- **Complexity:** Simple, clean data
- **Solution:** EXISTS (`homework_lesson_7_string_datetime_SOLUTION.ipynb`)
- **Template:** `homework_lesson_7_string_datetime.ipynb`
- **Validator:** Configured for this version

### Version 2: Realistic Business Data
- **Location:** `/data/processed/`
- **Rows:** 100/150/75
- **Columns:** PascalCase (`FeedbackID`, `CustomerID`, `Transaction_DateTime`, `Product_Description`)
- **Complexity:** Mixed date formats, no customer names in transactions
- **Solution:** DID NOT EXIST (I just created it)
- **Template:** `homework_lesson_7_string_datetime (1).ipynb`
- **Validator:** NOT configured for this version

## Student Performance Analysis

### Marcelo Coronel
**Score:** 0.9/100  
**Actual Performance:** 95/100

**What he did:**
- ✓ Used Version 2 data correctly
- ✓ Handled mixed date formats with parse_date_time()
- ✓ Joined tables to get customer names
- ✓ No data loss
- ✓ Excellent adaptation to complexity
- ✗ One minor error (searched Category instead of Product_Description)

**Why he failed:** Validator expected Version 1 column names

### Kathryn Emerick
**Score:** 60/100  
**Actual Performance:** 70/100

**What she did:**
- ✓ Used Version 2 data
- ✓ Basic functions correct
- ✗ Lost 40% of data (filtered NAs)
- ✗ Used CustomerID as names
- ✗ Displayed dates as timestamps
- ✗ Struggled with complexity

**Why she scored low:** Validator expected Version 1 + she made errors

## Recommended Solution

### Option A: Standardize on Version 1 (RECOMMENDED)

**Pros:**
- Solution already exists
- Validator already configured
- Rubric already correct
- Simpler for students
- Faster to implement

**Cons:**
- Less realistic data
- Doesn't teach adaptation

**Actions:**
1. Tell students to use data from `/data/` not `/data/processed/`
2. Students redo assignment (30-60 minutes)
3. No validator changes needed
4. Expected scores: Marcelo 95+, Kathryn 90+

### Option B: Standardize on Version 2

**Pros:**
- More realistic data
- Teaches adaptation skills
- Students already did this work

**Cons:**
- Need to update validator
- Need to update rubric
- More complex grading
- Takes more time

**Actions:**
1. Use my new solution as reference
2. Update rubric to accept:
   - PascalCase columns
   - parse_date_time() as valid
   - Workarounds for missing customer names
3. Update validator to check Version 2 structure
4. Regrade existing submissions
5. Expected scores: Marcelo 95, Kathryn 70

## Immediate Actions Required

### Step 1: Decide Which Version (TODAY)
- Review both versions
- Decide: Simple (V1) or Realistic (V2)?
- Communicate decision to team

### Step 2: Update Materials (THIS WEEK)
**If Version 1:**
- Email students: "Use data from `/data/` directory"
- Provide clear file paths
- Allow resubmission

**If Version 2:**
- Update rubric (use my solution as guide)
- Update validator to check PascalCase columns
- Accept parse_date_time() as valid
- Regrade existing submissions

### Step 3: Prevent Future Issues
- Delete or clearly label unused version
- Add data validation to assignment start
- Document which data to use in template
- Test validator with both student submissions

## Validator Updates Needed (If Version 2)

### Current Validator Checks:
```json
{
  "expected_columns": {
    "feedback": ["feedback_id", "customer_name", "feedback_text"],
    "transactions": ["transaction_id", "customer_name", "transaction_date"],
    "products": ["product_id", "product_name", "category"]
  }
}
```

### Updated for Version 2:
```json
{
  "expected_columns": {
    "feedback": ["FeedbackID", "CustomerID", "Feedback_Text"],
    "transactions": ["LogID", "CustomerID", "Transaction_DateTime"],
    "products": ["ProductID", "Product_Description", "Category"]
  },
  "flexible_checks": {
    "date_parsing": ["ymd", "mdy", "dmy", "parse_date_time"],
    "customer_names": "optional_if_joined"
  }
}
```

## Grading Adjustments

### Marcelo Coronel
**Current:** 0.9/100  
**Adjusted:** 95/100

**Justification:**
- Correctly used Version 2 data
- Excellent adaptation to complexity
- All functions used correctly
- One minor error in Task 7.1
- Should receive A grade

### Kathryn Emerick
**Current:** 60/100  
**Adjusted:** 70/100 (Version 2) OR 90/100 (if redone with Version 1)

**Justification:**
- Correctly attempted Version 2 data
- Made several errors (data loss, wrong extraction)
- Basic functions correct
- Would do much better with Version 1 data

## Communication Template

### Email to Students:

**Subject: Assignment 7 - Data File Clarification**

Hi [Student Name],

We've identified an issue with Assignment 7 data files. There are two versions of the data, and we need to ensure everyone uses the same version.

**[If Version 1]**
Please redo your assignment using the data files from the `/data/` directory (not `/data/processed/`). These files have:
- customer_feedback.csv (20 rows)
- transaction_log.csv (30 rows)
- product_catalog.csv (30 rows)

With these files, the assignment will be simpler and match the solution guide.

**[If Version 2]**
You used the correct data files from `/data/processed/`. We're updating our grading rubric to properly assess your work. Your regrade will be completed by [DATE].

We apologize for the confusion. If you have questions, please reach out.

Best regards,
[Instructor]

## Files Created

I've created the following reference documents:

1. **CRITICAL_FINDING.md** - Explains the two-version issue
2. **homework_lesson_7_SOLUTION_v2.md** - Complete solution for Version 2 data
3. **ACTION_PLAN_FINAL.md** - This document
4. **VALIDATOR_ISSUE_ANALYSIS.md** - Detailed validator bug analysis
5. **kathryn_emerick_analysis.md** - Kathryn's submission analysis
6. **assignment_7_scoring_analysis.md** - Marcelo's submission analysis

## Next Steps

1. **Decision:** Choose Version 1 or Version 2
2. **Communication:** Email students with clear instructions
3. **Implementation:** Update validator/rubric OR allow resubmissions
4. **Verification:** Test with both student submissions
5. **Documentation:** Update assignment instructions to prevent future issues

## Timeline

- **Today:** Make version decision
- **This week:** Implement changes
- **Next week:** Regrade or collect resubmissions
- **Before next assignment:** Verify all materials match

## Success Criteria

- ✓ All students using same data version
- ✓ Validator matches data structure
- ✓ Rubric matches data structure
- ✓ Students scored fairly
- ✓ Clear documentation for future semesters
