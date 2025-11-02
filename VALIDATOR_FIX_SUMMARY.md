# Score Validator Fix - November 1, 2025

## Problem Identified

The score validator was **blindly boosting scores to 85%** when it detected:
- More than 100 lines of code
- Presence of outputs

This caused **grade inflation** because it didn't check:
- ❌ If outputs were errors
- ❌ If required variables were created
- ❌ If code actually worked correctly

### Example Case
**Student Submission:** Assignment 6 (R Joins)
- **AI gave:** 85.1% (31.9/37.5)
- **Should be:** ~81-82% (30.5/37.5)

**Issues missed:**
1. `product_metrics` variable never created (empty code cell)
2. `critical_suppliers` code failed with error: "object 'Total_Revenue' not found"
3. `supplier_metrics` missing required `Total_Revenue` column
4. Multiple cells with errors but validator boosted anyway

---

## Changes Made

### 1. Updated Prompts (`prompt_templates/general_code_analysis_prompt.txt`)

**Added strict validation rules:**
```
🚨 CRITICAL OUTPUT VERIFICATION RULES 🚨
1. IF YOU SEE OUTPUT TEXT AFTER CODE, CHECK IF IT'S AN ERROR OR VALID OUTPUT
2. Valid outputs: "# A tibble:", printed numbers, data frames, cat() output, plots
3. INVALID outputs (mark as INCOMPLETE): "Error:", "object not found", "undefined"
4. If code produces an error, the section is INCOMPLETE
5. If a REQUIRED VARIABLE is never created, the section is INCOMPLETE
6. Check the rubric for required variable names - if they don't exist, mark incomplete
```

**Added examples of incomplete work:**
- Code that produces errors
- Missing required variables
- Code referencing non-existent columns

### 2. Updated Score Validator (`score_validator.py`)

**New Smart Validation Logic:**

#### Rule 1: Cap scores if errors detected
- 3+ errors → cap at 70%
- 1-2 errors → cap at 80%

#### Rule 2: Cap scores if required variables missing
- 3+ missing required vars → cap at 75%

#### Rule 3: Only boost if ALL conditions met
- 150+ lines of code
- Has valid outputs
- **Zero errors**
- **At most 1 missing required variable**
- AI gave very low score (<50%)
- Boost to 70% (not 85%)

#### Rule 4: Trust AI if score is reasonable
- If AI gives 50-90%, don't adjust
- AI probably saw something we didn't

**New Error Detection:**
```python
error_indicators = [
    'Error:',
    'Error in',
    'object not found',
    'could not find function',
    'undefined columns',
    'argument is missing',
    'subscript out of bounds'
]
```

**New Required Variable Checking:**
```python
# Check if variable is created (look for "var_name <-" pattern)
if f"{var} <-" not in student_code:
    missing_required_vars.append(var)
```

---

## How It Works Now

### Before (Old Validator):
```
Student has >100 lines + outputs?
→ Boost to 85% automatically ✗
```

### After (New Validator):
```
1. Count errors in output
   → If 3+ errors: cap at 70%
   → If 1-2 errors: cap at 80%

2. Check required variables (from rubric)
   → If 3+ missing: cap at 75%

3. Only boost if:
   - 150+ lines of code
   - Valid outputs (not errors)
   - Zero errors
   - ≤1 missing required var
   - AI gave <50%
   → Boost to 70% (conservative)

4. Trust AI if score is 50-90%
   → No adjustment
```

---

## Testing the Fix

### Test Case: Assignment 6 Submission

**Expected behavior with new validator:**

1. **Detect errors:**
   - "Error: object 'product_metrics' not found"
   - "Error: object 'Total_Revenue' not found"
   - Count: 2 errors

2. **Check required variables:**
   - Missing: `product_metrics`
   - Missing columns in `supplier_metrics`

3. **Apply rules:**
   - Rule 1: 2 errors → cap at 80%
   - Rule 2: 1 missing var → no additional cap
   - Rule 3: Has errors → don't boost
   - **Final: Cap at 80%**

4. **Result:**
   - Old: 85.1% (inflated)
   - New: ~80-82% (accurate)

---

## Benefits

✅ **More accurate grading** - catches errors and missing work
✅ **Prevents inflation** - doesn't blindly boost
✅ **Still prevents false negatives** - boosts if AI is too harsh
✅ **Uses rubric data** - checks required variables
✅ **Transparent** - logs all decisions

---

## Configuration

The validator now accepts rubric parameter:
```python
validate_and_adjust_scores(
    code_analysis, 
    comprehensive_feedback, 
    student_code, 
    template_code,
    rubric  # NEW: passes rubric for required variable checking
)
```

---

## Next Steps

1. **Test with multiple submissions** to verify accuracy
2. **Monitor validator logs** to see adjustments
3. **Fine-tune thresholds** if needed:
   - Error count caps (currently 70-80%)
   - Missing variable caps (currently 75%)
   - Boost threshold (currently 70%)

---

## Summary

The validator now **validates quality**, not just quantity. It:
- Checks for errors before boosting
- Verifies required variables exist
- Caps scores appropriately
- Only boosts when genuinely undergraded
- Trusts AI analysis in reasonable ranges

**Result:** More accurate, fair grading that catches incomplete work while still preventing false negatives.
