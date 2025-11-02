# Complete Grading System Documentation

## Overview

The complete grading system has **4 layers** of validation:

```
┌────────────────────────────────────────────────────────────────┐
│ LAYER 1: SYSTEMATIC VALIDATOR (Deterministic)                 │
│ ✅ Check variables exist                                      │
│ ✅ Verify functions used                                      │
│ ✅ Count cell execution                                       │
│ → Score: 91/100                                               │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ LAYER 2: OUTPUT VALIDATOR (Deterministic)                     │
│ ✅ Compare row counts with solution                           │
│ ✅ Verify numerical results (with tolerance)                  │
│ ✅ Check key metrics match                                    │
│ → Adjustment: -2 points (95% match)                           │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ LAYER 3: QWEN CODER (AI)                                      │
│ ✅ Analyze code quality                                       │
│ ✅ Identify issues                                            │
│ ✅ Generate fix recommendations                               │
│ → Technical feedback with code examples                       │
└────────────────────────────────────────────────────────────────┐
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ LAYER 4: GPT-OSS-120B (AI)                                    │
│ ✅ Generate personalized feedback                             │
│ ✅ Celebrate strengths                                        │
│ ✅ Explain improvements                                       │
│ → Warm, educational narrative                                 │
└────────────────────────────────────────────────────────────────┘

FINAL SCORE: 89/100 (A-)
```

## Layer 1: Systematic Validator

**Purpose:** Objective, consistent scoring based on code presence

**What it checks:**
- All 25 required variables exist
- Required functions are used (inner_join, left_join, etc.)
- Cells have been executed (outputs present)
- All 21 sections attempted

**Example output:**
```
✅ ALL 25 REQUIRED VARIABLES FOUND
✅ Part 1: Data Import: 5.0/5
✅ Part 2.1: Inner Join: 3.0/3
✅ Part 2.2: Left Join: 3.0/3
... (all 21 sections)

Score: 91/100
```

## Layer 2: Output Validator

**Purpose:** Verify results are correct (not just code exists)

**What it checks:**
- Row counts match expected values (with tolerance)
- Numerical results are close to solution
- Key metrics are calculated correctly

**Tolerance settings:**
```python
numerical_tolerance = 5%      # Allow 5% variation in numbers
row_count_tolerance = 5       # Allow ±5 rows difference
```

**Example checks:**

### Data Import
```
✅ customers: 100 rows (expected 100 ±0)
✅ orders: 250 rows (expected 250 ±0)
✅ order_items: 400 rows (expected 400 ±0)
```

### Join Results
```
✅ customer_orders: 200 rows (expected 200 ±5)
✅ orders_customers_items: 310 rows (expected 310 ±10)
✅ complete_data: 310 rows (expected 310 ±10)
```

### Business Metrics
```
✅ top customer total spent: 8471.51 (expected 8471.51 ±5%)
✅ top product revenue: 11763.16 (expected 11763.16 ±5%)
✅ highest city sales: 72277.52 (expected 72277.52 ±5%)
```

### Data Quality
```
✅ customers without orders: 0 (expected 0 ±2)
✅ orphaned orders: 50 (expected 50 ±5)
✅ products never ordered: 0 (expected 0 ±2)
```

**Score adjustment:**
- 95-100% match: 0 points deduction
- 90-95% match: -2 points
- 80-90% match: -5 points
- 70-80% match: -10 points
- <70% match: -15 points

## Layer 3: Qwen Coder Evaluation

**Purpose:** Technical code analysis and fix recommendations

**What it provides:**
- Code quality assessment
- Specific issues identified
- Fix recommendations with code examples
- Alternative approaches

**Example output:**
```
## Code Quality Assessment
Your code demonstrates strong understanding of dplyr joins. The structure
is logical and follows best practices. However, there are a few areas
where the code could be improved.

## Issues and Fixes

### Issue 1: Unexecuted Cells
**Problem:** 4 code cells were not executed before submission
**Impact:** Cannot verify these sections work correctly
**Fix:**
```r
# Before submitting, run all cells:
# In RStudio: Ctrl+Alt+R or Run > Run All
# In Jupyter: Kernel > Restart & Run All
```

### Issue 2: Row Count Mismatch
**Problem:** customer_orders has 195 rows but expected 200
**Impact:** May indicate incorrect join logic or data filtering
**Fix:**
```r
# Check your join logic:
customer_orders <- customers %>%
  inner_join(orders, by = "CustomerID")

# Verify the result:
cat("Rows:", nrow(customer_orders))
```

## Recommendations
1. Add comments explaining complex join logic
2. Use consistent variable naming
3. Consider chaining joins with pipes for cleaner code

## Alternative Approaches
Instead of separate joins, you could chain them:
```r
complete_data <- orders %>%
  inner_join(order_items, by = "OrderID") %>%
  inner_join(customers, by = "CustomerID") %>%
  inner_join(products, by = "ProductID") %>%
  inner_join(suppliers, by = "Supplier_ID")
```
```

## Layer 4: GPT-OSS Narrative Feedback

**Purpose:** Personalized, encouraging educational feedback

**What it provides:**
- Overall assessment
- Celebration of strengths
- Constructive areas for growth
- Actionable recommendations
- Encouraging closing

**Example output:**
```
## Overall Assessment
Excellent work on this assignment! You've demonstrated strong mastery of
join operations and created comprehensive business analyses. Your adjusted
score of 89% reflects high-quality work with minor areas for improvement.

## Strengths
- All 25 required variables created correctly
- Perfect execution of all 6 join types
- Comprehensive business analysis with specific metrics
- Clear, well-organized code structure
- Thoughtful insights in your summary section
- 95% output accuracy - your results closely match the solution

## Areas for Growth
- Remember to execute all code cells before submission (4 cells unexecuted)
- One join result had slightly different row count (195 vs 200 expected)
- Consider adding more comments to explain analytical choices

## Recommendations
1. Before submitting, use "Run All" to ensure every cell executes
2. Double-check join results match expected row counts
3. Add comments explaining why you chose specific join types
4. In future assignments, include more data visualizations

## Encouragement
You're doing excellent work! Your understanding of joins is solid, and
your business analysis shows real analytical thinking. The minor output
discrepancy is easily fixable - just verify your join logic. Keep up the
great work!
```

## Complete Example

### Student: Kathryn Emerick

**Layer 1 (Systematic):**
- Variables: 25/25 ✅
- Sections: 21/21 ✅
- Execution: 27/31 cells (87%)
- **Score: 91/100**

**Layer 2 (Output):**
- Row counts: 18/20 match ✅
- Numerical values: 10/10 match ✅
- Overall match: 95%
- **Adjustment: -2 points**

**Layer 3 (Qwen):**
- Code quality: Good
- Issues: 4 unexecuted cells, 2 row count mismatches
- Recommendations: Run all cells, verify join logic

**Layer 4 (GPT-OSS):**
- Strengths: Excellent join mastery, comprehensive analysis
- Growth areas: Execute all cells, verify outputs
- Encouragement: Solid work, minor fixes needed

**FINAL SCORE: 89/100 (B+)**

## Setup Requirements

### 1. Solution Notebook

Create a solution notebook at:
```
data/solutions/assignment_6_solution.ipynb
```

This should contain:
- All required variables with correct values
- Expected row counts in outputs
- Expected numerical results

### 2. Ollama Models

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull qwen2.5-coder:latest
ollama pull gpt-oss-120b:latest

# Start Ollama
ollama serve
```

### 3. Python Dependencies

```bash
pip install requests
```

## Usage

### Grade One Student

```bash
python3 validators/hybrid_grading_pipeline.py \
  --file submissions/12/student.ipynb \
  --output grading_results
```

### Grade All Students

```python
from pathlib import Path
from validators.hybrid_grading_pipeline import HybridGradingPipeline

pipeline = HybridGradingPipeline(
    solution_notebook_path="data/solutions/assignment_6_solution.ipynb"
)

for notebook in Path("submissions/12").glob("*.ipynb"):
    result = pipeline.grade_submission(str(notebook))
    print(f"{notebook.stem}: {result['grade']} ({result['adjusted_score']:.1f}%)")
```

## Configuration

### Adjust Tolerances

```python
from validators.output_validator import OutputValidator

validator = OutputValidator(
    solution_notebook_path="data/solutions/assignment_6_solution.ipynb",
    numerical_tolerance=0.10,  # 10% tolerance for numbers
    row_count_tolerance=10,    # ±10 rows tolerance
    allow_extra_columns=True   # Allow students to add columns
)
```

### Customize Checks

Edit `validators/output_validator.py` in the `_define_expected_outputs()` method:

```python
'part5_customer_metrics': {
    'description': 'Customer metrics analysis',
    'checks': [
        {
            'type': 'row_count',
            'variable': 'customer_metrics',
            'expected': 94,
            'tolerance': 10
        },
        {
            'type': 'numerical_value',
            'description': 'top customer total spent',
            'expected': 8471.51,
            'tolerance_percent': 5  # 5% tolerance
        },
        # Add more checks here
    ]
}
```

## Output Files

For each student:

### 1. JSON Result
```json
{
  "objective_score": 91.0,
  "adjusted_score": 89.0,
  "grade": "B",
  "validation_details": {...},
  "output_validation": {
    "overall_match": 0.95,
    "passed_checks": 28,
    "total_checks": 30,
    "score_adjustment": -2
  },
  "code_evaluation": {...},
  "narrative_feedback": {...}
}
```

### 2. Comprehensive Report
```
================================================================================
COMPREHENSIVE GRADING REPORT
================================================================================

FINAL GRADE: B+ (89.0/100)
  (Base: 91.0, Output Adjustment: -2)

================================================================================
OBJECTIVE SCORING (Systematic Validator)
================================================================================
... (detailed breakdown)

================================================================================
OUTPUT VALIDATION (vs Solution)
================================================================================
Overall Match: 95.0%
Checks Passed: 28/30

✅ part1_data_import: Data import and dimensions
  ✅ customers: 100 rows (expected 100 ±0)
  ✅ orders: 250 rows (expected 250 ±0)
  ...

❌ part2_inner_join: Inner join results
  ❌ customer_orders: 195 rows (expected 200 ±5)

================================================================================
CODE EVALUATION (Qwen Coder)
================================================================================
... (technical feedback)

================================================================================
INSTRUCTOR FEEDBACK (GPT-OSS-120B)
================================================================================
... (narrative feedback)
```

## Benefits

### For Students
- ✅ Objective, transparent scoring
- ✅ Detailed feedback on what's wrong
- ✅ Code examples showing how to fix issues
- ✅ Encouraging, educational tone

### For Instructors
- ✅ Consistent, fair grading
- ✅ Automated output verification
- ✅ Detailed reports for each student
- ✅ Time saved on manual grading

### For Quality
- ✅ No false negatives (claiming work missing when it exists)
- ✅ Verifies results are correct, not just code exists
- ✅ Allows reasonable variation (tolerance)
- ✅ Combines deterministic + AI strengths

## Troubleshooting

### Issue: Output validation failing

Check if solution notebook exists:
```bash
ls -la data/solutions/assignment_6_solution.ipynb
```

### Issue: Tolerance too strict

Increase tolerances:
```python
pipeline = HybridGradingPipeline(
    solution_notebook_path="...",
    numerical_tolerance=0.10,  # 10% instead of 5%
    row_count_tolerance=10     # ±10 instead of ±5
)
```

### Issue: Can't find values in output

The validator uses regex patterns. If it can't find values, check the output format in the notebook and adjust patterns in `_check_row_count()` or `_check_numerical_value()`.

## Conclusion

This complete system provides:
1. **Objective scoring** (systematic validator)
2. **Result verification** (output validator)
3. **Technical feedback** (Qwen coder)
4. **Educational guidance** (GPT-OSS)

= **Comprehensive, fair, accurate grading** 🎉
