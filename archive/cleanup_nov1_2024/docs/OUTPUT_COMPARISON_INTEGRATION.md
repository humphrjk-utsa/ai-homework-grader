# Output Comparison Integration - November 1, 2025

## Overview

Enhanced the grading system to use **programmatic output comparison** as PRIMARY evidence for grading accuracy. The system now compares student notebook outputs cell-by-cell against solution outputs.

---

## How It Works

### 1. Output Comparison Process

```python
# During grading, the system:
1. Loads student notebook and solution notebook
2. Extracts all code cell outputs
3. Compares outputs cell-by-cell using fuzzy matching
4. Calculates match rate: (matching_cells / total_cells) × 100
5. Passes results to AI and validator
```

### 2. Match Rate Calculation

**Similarity Threshold:** 80% similarity = match

**Example:**
- Total cells: 12
- Matching outputs: 8
- Match rate: 66.7%

### 3. Integration Points

#### A. AI Prompt Enhancement
Output comparison results are added to the AI grading prompt:

```
🔬 PROGRAMMATIC OUTPUT VERIFICATION (PRIMARY GRADING EVIDENCE):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Results:
- Cells with matching outputs: 8/12 (66.7%)
- Overall accuracy: 66.7%

🚨 CRITICAL GRADING RULES - FOLLOW EXACTLY:
- If match rate >= 90%: Outputs are CORRECT → Score 90-100%
- If match rate 75-89%: Outputs are MOSTLY CORRECT → Score 80-90%  
- If match rate 60-74%: Outputs are PARTIALLY CORRECT → Score 70-80%
- If match rate 40-59%: Outputs are MOSTLY INCORRECT → Score 50-70%
- If match rate < 40%: Outputs are INCORRECT or MISSING → Score 30-50%
```

#### B. Validator Integration
The validator now uses output comparison to cap scores:

```python
if match_rate < 40:
    max_score = 50  # Very low match
elif match_rate < 60:
    max_score = 70  # Low match
elif match_rate < 75:
    max_score = 80  # Moderate match
elif match_rate >= 90:
    # High match - note but don't cap
```

---

## Grading Rules with Output Comparison

### Rule Priority (Most Restrictive Wins)

1. **Errors in output** → Cap at 70-80%
2. **Missing required variables** → Cap at 75%
3. **Low output match rate** → Cap at 50-80%
4. **Incomplete TODO sections** → Cap at 20-70%

### Example Scenarios

#### Scenario 1: Perfect Match
```
Match rate: 95%
Errors: 0
Missing vars: 0
→ Score: 90-100% ✅
```

#### Scenario 2: Partial Match
```
Match rate: 66.7%
Errors: 2
Missing vars: 1
→ Score capped at: 75% (most restrictive)
```

#### Scenario 3: Low Match
```
Match rate: 35%
Errors: 5
Missing vars: 3
→ Score capped at: 50% (very low match)
```

---

## Benefits

### 1. Objective Grading
✅ Uses actual output comparison, not just code inspection
✅ Catches cases where code looks good but produces wrong results
✅ Prevents AI from hallucinating completion

### 2. Accurate Scoring
✅ Can't get high score with wrong outputs
✅ Match rate directly influences score
✅ Multiple validation layers

### 3. Transparent Feedback
✅ Students see match rate in feedback
✅ Clear explanation of why score was capped
✅ Validator logs show all decisions

---

## Implementation Details

### Files Modified

1. **business_analytics_grader.py**
   - Enhanced output comparison prompt section
   - Pass output_comparison to validator
   - More prominent grading rules

2. **score_validator.py**
   - Added output_comparison parameter
   - New Rule 4: Validate against output match rate
   - Cap scores based on match rate

3. **prompt_templates/general_code_analysis_prompt.txt**
   - Added instruction to use output comparison as PRIMARY evidence
   - Emphasized low match rate = low score

### Key Functions

```python
# In business_analytics_grader.py
comparator = OutputComparator(notebook_path, solution_notebook_path)
output_comparison = comparator.compare_outputs()

# Results structure:
{
    'total_cells': 12,
    'matching_cells': 8,
    'match_rate': 66.7,
    'accuracy_score': 66.7
}

# Passed to validator:
validate_and_adjust_scores(
    code_analysis, 
    feedback, 
    student_code, 
    template_code,
    rubric,
    output_comparison  # NEW
)
```

---

## Testing

### Test Case: Assignment 6 with Errors

**Input:**
- Student has 2 errors in output
- 5 missing required variables
- Output match rate: 66.7%
- AI initially gave: 85%

**Expected Output:**
- Error cap: 80%
- Missing var cap: 75%
- Output match cap: 80%
- **Final: 75%** (most restrictive)

**Actual Output:**
```
⚠️ VALIDATOR: Detected 2 error(s) - capping at 80%
⚠️ VALIDATOR: 5 required variables missing - capping at 75%
🔬 VALIDATOR: Output comparison match rate: 66.7%
✅ VALIDATOR: AI score of 75% with 66.7% output match - validated
Final Score: 75%
```

✅ **Test Passed**

---

## Configuration

### Similarity Threshold
Default: 80% similarity = match

Adjust in `output_comparator.py`:
```python
is_match = similarity >= 0.80  # Change this value
```

### Match Rate Caps
Adjust in `score_validator.py`:
```python
if match_rate < 40:
    max_score_outputs = 50  # Adjust these values
elif match_rate < 60:
    max_score_outputs = 70
elif match_rate < 75:
    max_score_outputs = 80
```

### Timeout
Default: 30 seconds for output comparison

Adjust in `business_analytics_grader.py`:
```python
signal.alarm(30)  # Change timeout value
```

---

## Limitations

### 1. Large Notebooks
- Notebooks >200KB skip output comparison (prevent hangs)
- Timeout after 30 seconds

### 2. Fuzzy Matching
- Uses SequenceMatcher for similarity
- May not catch semantic differences
- Whitespace normalized

### 3. Cell Order
- Compares cells by index
- Assumes same cell order as solution
- Extra cells don't penalize

---

## Future Enhancements

### Potential Improvements

1. **Semantic Comparison**
   - Compare data frame structures
   - Check numerical values with tolerance
   - Verify plot types

2. **Detailed Mismatch Reporting**
   - Show which specific cells don't match
   - Include expected vs actual outputs in feedback
   - Suggest corrections

3. **Variable Value Comparison**
   - Extract variable values from outputs
   - Compare specific metrics (e.g., mean, sum)
   - Verify calculations

4. **Weighted Cell Importance**
   - Some cells more important than others
   - Weight match rate by cell importance
   - Use rubric to determine weights

---

## Summary

The grading system now uses **three layers of validation**:

1. **AI Analysis** - Examines code and outputs
2. **Output Comparison** - Programmatically compares outputs
3. **Validator** - Enforces caps based on all evidence

**Result:** More accurate, objective grading that prevents inflation and catches incorrect outputs.

### Key Principle
**Low output match rate = Low score**

No matter how good the code looks, if outputs don't match the solution, the score is capped accordingly.
