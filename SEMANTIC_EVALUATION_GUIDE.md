# Semantic Evaluation Guide - November 1, 2025

## Overview

The grading system now uses **semantic evaluation** instead of exact matching. This means:
- ✅ Order doesn't matter
- ✅ Equivalent expressions accepted
- ✅ Numerical similarity allowed
- ✅ Concept alignment over exact wording
- ❌ Wrong values still penalized
- ❌ Contradictory statements rejected

---

## Part 1: Output Comparison (Code Results)

### Principle: Elements Matter, Not Order

#### ✅ EQUIVALENT OUTPUTS (Should Match)

**Example 1: Different Order**
```
Student:  "Customers: 94, Orders: 250, Products: 50"
Solution: "Orders: 250, Products: 50, Customers: 94"
→ MATCH (same elements, different order)
```

**Example 2: Rounding Differences**
```
Student:  "Top customer spent $8471.51"
Solution: "Top customer spent $8471.5"
→ MATCH (acceptable rounding difference)
```

**Example 3: Data Frame Row Order**
```
Student:  Tibble with 94 rows (sorted by Name)
Solution: Tibble with 94 rows (sorted by CustomerID)
→ MATCH (same data, different sort order)
```

**Example 4: Numerical Precision**
```
Student:  "Average: 94.67"
Solution: "Average: 94.7"
→ MATCH (acceptable precision difference)
```

#### ❌ NON-EQUIVALENT OUTPUTS (Should NOT Match)

**Example 1: Wrong Count**
```
Student:  "50 customers analyzed"
Solution: "94 customers analyzed"
→ NO MATCH (wrong value)
```

**Example 2: Wrong Calculation**
```
Student:  "Total revenue: $5,000"
Solution: "Total revenue: $8,471"
→ NO MATCH (significantly different value)
```

**Example 3: Missing Data**
```
Student:  "Customers: 94"
Solution: "Customers: 94, Orders: 250"
→ PARTIAL MATCH (missing information)
```

**Example 4: Error vs Valid Output**
```
Student:  "Error: object 'product_metrics' not found"
Solution: "# A tibble: 50 × 4"
→ NO MATCH (error vs valid output)
```

---

## Part 2: Written Answers (Reflections & Insights)

### Principle: Meaning Matters, Not Exact Wording

#### ✅ EQUIVALENT EXPRESSIONS (Should Accept)

**Concept: Join Types**
```
Student:  "Inner joins keep only matching records from both tables"
Solution: "Inner joins return rows that exist in both datasets"
→ EQUIVALENT (same concept, different wording)
```

**Concept: Data Quality**
```
Student:  "50 orphaned orders indicate data quality issues"
Solution: "Orders without customers suggest data integrity problems"
→ EQUIVALENT (same finding, different terminology)
```

**Concept: Business Insight**
```
Student:  "Houston is an expansion opportunity with 18 customers"
Solution: "Houston shows growth potential with high customer count"
→ EQUIVALENT (same insight, different phrasing)
```

**Concept: Recommendations**
```
Student:  "Focus marketing on high-value customers to increase retention"
Solution: "Target top customers with retention campaigns"
→ EQUIVALENT (same recommendation, different wording)
```

#### ❌ NON-EQUIVALENT EXPRESSIONS (Should Reject)

**Wrong Concept**
```
Student:  "Inner join keeps all records from both tables"
Solution: "Inner join keeps only matching records"
→ NOT EQUIVALENT (wrong concept)
```

**Contradicts Data**
```
Student:  "All customers have placed orders"
Solution: "0 customers have no orders" (but data shows 50 orphaned orders)
→ NOT ALIGNED (contradicts actual data)
```

**Wrong Values**
```
Student:  "Top customer is John Doe with $15,000 spent"
Solution: "Top customer is Customer 53 with $8,471 spent"
→ NOT ALIGNED (wrong customer and wrong value)
```

**Illogical Conclusion**
```
Student:  "Houston has highest spending per customer"
Solution: "Houston has below-average spending ($2,119 vs $2,500 avg)"
→ NOT ALIGNED (contradicts data)
```

---

## Implementation

### 1. Output Comparator Enhancement

**Semantic Comparison Function:**
```python
def semantic_compare(self, student_out: str, solution_out: str):
    # Extract key metrics
    student_metrics = extract_key_metrics(student_out)
    solution_metrics = extract_key_metrics(solution_out)
    
    # Check for errors
    if student has error and solution doesn't:
        return NO MATCH
    
    # Compare row counts (order-independent)
    if row_counts_match:
        return MATCH
    
    # Compare numbers (order-independent)
    if 80%+ numbers match:
        return MATCH
    
    # Fall back to text similarity
    return text_similarity_score
```

**Key Features:**
- Extracts numbers from outputs
- Compares sets (order-independent)
- Checks row/column counts
- Detects errors vs valid outputs
- Uses Jaccard similarity for numbers

### 2. Prompt Enhancements

**Code Analysis Prompt:**
```
🔍 SEMANTIC OUTPUT COMPARISON RULES 🔍
1. Order doesn't matter - Data frames sorted differently are still correct
2. Elements matter - Check if same values/rows exist, not exact order
3. Numerical similarity - 94.7 vs 94.67 is acceptable
4. Column names - Must match
5. Row counts - Must match
6. Key metrics - Must be similar
```

**Feedback Prompt:**
```
🎯 EVALUATING WRITTEN ANSWER ALIGNMENT:
- Meaning matters, not exact wording
- Concepts matter, not exact terminology
- Alignment with solution's reasoning
- Rationality based on their data

Accept Equivalent Expressions:
- "Data quality issues" = "Data integrity problems"
- "Expansion opportunity" = "Growth potential"

Reject Contradictory Statements:
- If data shows X, student can't say Y
```

---

## Evaluation Rules

### Rule 1: Numerical Comparison
```
If outputs contain numbers:
  Extract all numbers from both outputs
  Compare as sets (order-independent)
  If 80%+ numbers match → MATCH
  If <50% numbers match → NO MATCH
```

### Rule 2: Row Count Comparison
```
If outputs show row counts:
  Extract row counts from both
  If counts match exactly → MATCH
  If counts differ → NO MATCH (critical difference)
```

### Rule 3: Text Similarity
```
If no numbers or row counts:
  Normalize whitespace and case
  Calculate text similarity
  If similarity > 75% → MATCH
  If similarity < 50% → NO MATCH
```

### Rule 4: Error Detection
```
If student output contains error:
  If solution also has error → MATCH
  If solution has valid output → NO MATCH
```

### Rule 5: Concept Alignment
```
For written answers:
  Extract key concepts from both
  Check if concepts align
  Accept equivalent terminology
  Reject contradictory statements
```

---

## Examples by Category

### Category 1: Data Frame Outputs

**Scenario:** Student and solution both show customer_metrics

**Student Output:**
```
# A tibble: 94 × 5
   CustomerID Name        Total_Spent Order_Count Avg_Order_Value
1          53 Customer 53       8472.           2           4236.
2           3 Customer 3        6107.           2           3053.
3          61 Customer 61       5768.           2           2884.
```

**Solution Output:**
```
# A tibble: 94 × 5
   CustomerID Name        Total_Spent Order_Count Avg_Order_Value
1           3 Customer 3        6107.           2           3053.
2          53 Customer 53       8472.           2           4236.
3          61 Customer 61       5768.           2           2884.
```

**Evaluation:**
- Row count: 94 = 94 ✅
- Columns: Same 5 columns ✅
- Values: Same customers, same metrics ✅
- Order: Different (sorted differently) ✅ OK
- **Result: MATCH**

### Category 2: Summary Statistics

**Scenario:** Student and solution show dataset dimensions

**Student Output:**
```
Customers: 100 rows x 5 columns
Orders: 250 rows x 4 columns
```

**Solution Output:**
```
Orders: 250 rows x 4 columns
Customers: 100 rows x 5 columns
```

**Evaluation:**
- Numbers present: {100, 5, 250, 4} = {250, 4, 100, 5} ✅
- Order: Different ✅ OK
- **Result: MATCH**

### Category 3: Written Insights

**Scenario:** Student describes data quality findings

**Student Answer:**
```
"I discovered 50 orders that don't have corresponding customers in the 
database. This indicates data quality issues that need to be addressed."
```

**Solution Answer:**
```
"The analysis revealed 50 orphaned orders without valid customer IDs, 
suggesting data integrity problems in the order entry system."
```

**Evaluation:**
- Key concept: 50 orphaned orders ✅
- Interpretation: Data quality/integrity issues ✅
- Terminology: Different but equivalent ✅
- **Result: ALIGNED**

### Category 4: Business Recommendations

**Scenario:** Student provides strategic recommendations

**Student Answer:**
```
"Focus marketing efforts on high-value customers to increase retention 
and spending. Houston shows expansion potential with 18 customers but 
low average spending."
```

**Solution Answer:**
```
"Target top customers with retention campaigns. Houston represents a 
growth opportunity with high customer count but below-average revenue 
per customer."
```

**Evaluation:**
- Recommendation 1: Target high-value customers ✅
- Recommendation 2: Houston expansion opportunity ✅
- Supporting data: 18 customers, low spending ✅
- Wording: Different but equivalent ✅
- **Result: ALIGNED**

---

## Grading Impact

### Before (Exact Matching)
```
Student: "Orders: 250, Customers: 100"
Solution: "Customers: 100, Orders: 250"
→ NO MATCH (different order)
→ Score: 70% (penalized for "wrong" output)
```

### After (Semantic Matching)
```
Student: "Orders: 250, Customers: 100"
Solution: "Customers: 100, Orders: 250"
→ MATCH (same elements, different order)
→ Score: 95% (correct output recognized)
```

---

## Configuration

### Adjust Similarity Thresholds

**In output_comparator.py:**
```python
# Number matching threshold
if number_similarity > 0.8:  # Adjust this (0.0-1.0)
    return MATCH

# Text similarity threshold
if similarity >= 0.75:  # Adjust this (0.0-1.0)
    return MATCH
```

### Adjust Numerical Tolerance

```python
# For floating point comparison
def numbers_match(num1, num2, tolerance=0.01):
    return abs(num1 - num2) < tolerance
```

---

## Testing

### Test Case 1: Order Independence
```python
student = "A: 100, B: 200, C: 300"
solution = "C: 300, A: 100, B: 200"
assert semantic_compare(student, solution) == MATCH
```

### Test Case 2: Numerical Precision
```python
student = "Average: 94.67"
solution = "Average: 94.7"
assert semantic_compare(student, solution) == MATCH
```

### Test Case 3: Wrong Values
```python
student = "Total: 50"
solution = "Total: 94"
assert semantic_compare(student, solution) == NO_MATCH
```

### Test Case 4: Concept Alignment
```python
student = "Inner joins keep matching records"
solution = "Inner joins return rows in both tables"
assert concepts_align(student, solution) == TRUE
```

---

## Summary

### Key Principles

1. **Order Independence** - Same elements in different order = match
2. **Numerical Tolerance** - Small rounding differences = match
3. **Concept Alignment** - Same meaning, different words = match
4. **Value Accuracy** - Wrong numbers = no match
5. **Logical Consistency** - Contradicts data = no match

### What Changed

**Before:**
- Exact string matching
- Order mattered
- Wording had to match exactly
- Rounding differences penalized

**After:**
- Semantic comparison
- Order doesn't matter
- Equivalent expressions accepted
- Numerical similarity allowed

### Result

**More accurate, fair grading** that recognizes correct work even when expressed differently.
