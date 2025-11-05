# Assignment 7 Grading Issue Analysis

## Problem
Student received 54/100 on Assignment 7, but actually completed 18/25 sections (72%) with good reflection answers. Expected score: 70-75/100.

## Root Causes

### 1. Assignment 6 Examples in General Prompts
The general prompts contain Assignment 6 (joins) examples that confuse the AI:

**In `general_code_analysis_prompt.txt`:**
```
Example of GOOD feedback:
"Your customer_metrics output shows 50 customers, but the solution shows 94. This happened because you used inner_join() instead of left_join()..."
```

**In `general_feedback_prompt.txt`:**
```
EXAMPLES OF EQUIVALENT ANSWERS:
✅ Student: "Inner joins keep only matching records" vs Solution: "Inner joins return rows that exist in both tables" → EQUIVALENT
```

**Result:** AI hallucinates Assignment 6 feedback like:
- "Complete Part 2.1: Inner Join"
- "Complete Part 2.2: Left Join"

### 2. Student's Actual Performance

**What the student did well:**
- ✅ Loaded packages correctly
- ✅ Imported all datasets
- ✅ Cleaned product names with str_trim() and str_to_title()
- ✅ Standardized categories
- ✅ Cleaned feedback text with str_to_lower() and str_squish()
- ✅ Detected features (wireless, premium, gaming) correctly
- ✅ Extracted specifications with str_extract()
- ✅ Performed sentiment analysis with str_count()
- ✅ Extracted date components (year, month, day, weekday, quarter)
- ✅ Calculated days_since with today()
- ✅ Categorized by recency with case_when()
- ✅ Analyzed weekday patterns
- ✅ Analyzed monthly patterns
- ✅ Answered all 6 reflection questions with good depth

**What needs improvement:**
- ⚠️ Task 4.1: Used parse_date_time() instead of ymd(), resulting in 33 NA values (22% failure)
- ⚠️ Task 4.3: Weekend detection shows 0% (but data has no weekends)
- ⚠️ Task 6.1: Used CustomerID instead of Customer_Name for first name extraction
- ⚠️ Task 7.1: Used wrong approach for "most common category"

**Fair score: 70-75/100**
- Technical: 18/25 sections = 72% → ~18/25 points
- Reflections: 6/6 answered well → ~18/20 points
- Date parsing penalty: -5 points for 22% NA rate
- Minor errors: -3 points
- **Total: ~73/100**

### 3. Why the Grader Gave 54/100

The feedback says:
- "Completion: 18 out of 25 sections (72%). Calculated score: 40%."
- But then gives 54/100

**The math doesn't add up.** The grader is:
1. Correctly counting 18/25 sections (72%)
2. Incorrectly calculating this as 40% score
3. Then adjusting to 54% final score
4. Adding hallucinated Assignment 6 feedback

## Solutions

### Solution 1: Update General Prompts (Remove Assignment 6 Examples)

Replace Assignment 6 examples with generic examples:

**OLD:**
```
"Your customer_metrics output shows 50 customers, but the solution shows 94. This happened because you used inner_join() instead of left_join()..."
```

**NEW:**
```
"Your analysis output shows 50 items, but the solution shows 94. This happened because you used an incorrect filtering approach. The correct method is: result <- data %>% filter(condition) %>% summarise(...). This ensures all required items are included."
```

### Solution 2: Fix Scoring Calculation

The grader should calculate:
- 18/25 sections complete = 72%
- Base technical score = 72% of 25 points = 18 points
- Reflection score = 18/20 points (good answers)
- Penalties: -5 for date parsing issues, -2 for minor errors
- **Final: 18 + 18 - 7 = 29/45 technical+reflection = 64%**
- **With business understanding: ~70-75/100**

### Solution 3: Improve Date Parsing Feedback

The student used `parse_date_time()` which is actually a valid lubridate function, just not the best choice. The feedback should be:

"You used parse_date_time() which resulted in 33 NA values (22% failure rate). While this is a lubridate function, it's not ideal for this dataset's mixed formats. The assignment specifically requires ymd() or mdy() which handle these formats better. Change to: date_parsed = ymd(Transaction_DateTime) for 100% parsing success."

## Recommended Actions

1. **Update general prompts** to remove Assignment 6 examples
2. **Test grading again** with updated prompts
3. **Verify scoring calculation** matches completion percentage
4. **Check that assignment-specific prompts** are being loaded correctly for a7v2
5. **Consider re-grading** this student's submission with corrected system

## Expected Outcome

With fixes applied:
- No more Assignment 6 hallucinations
- Score of 70-75/100 (fair for 72% completion + good reflections)
- Accurate feedback focused on actual Assignment 7 issues
- Proper recognition of what student did well
