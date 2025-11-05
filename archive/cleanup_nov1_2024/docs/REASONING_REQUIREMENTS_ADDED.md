# Reasoning Requirements for Feedback - November 1, 2025

## Problem

The AI was giving feedback like:
- "Your output is incorrect" ❌
- "You need to improve this section" ❌
- "Consider adding more analysis" ❌

**Issue:** No explanation of WHAT, WHY, or HOW to fix

---

## Solution: Required Reasoning Framework

### For Code Analysis (general_code_analysis_prompt.txt)

Added requirement that ALL feedback about incorrect outputs must include:

#### 1. WHAT is wrong
- Specific values, structure, or format that's incorrect
- Concrete details, not vague statements

#### 2. WHY it's wrong
- What caused the error
- Wrong function, missing step, incorrect logic

#### 3. WHAT was expected
- Show the correct output or approach from solution
- Reference specific values or structure

#### 4. HOW to fix it
- Specific code changes needed
- Exact function calls or syntax

---

## Examples

### ❌ BAD Feedback (Before)
```
"Your output is incorrect."
"You need to complete this section."
"The calculation is wrong."
```

**Problems:**
- No specifics
- No explanation
- No guidance
- Student can't learn from it

### ✅ GOOD Feedback (After)
```
"Your customer_metrics output shows 50 customers, but the solution shows 94. 
This happened because you used inner_join() instead of left_join(), which 
excluded customers without orders. The correct approach is: 
customer_metrics <- complete_data %>% group_by(CustomerID, Name) %>% 
summarise(...). This ensures all customers are included in the analysis."
```

**Why it's good:**
- ✅ WHAT: Shows 50 vs expected 94
- ✅ WHY: Used inner_join instead of left_join
- ✅ EXPECTED: Should include all customers
- ✅ HOW: Specific code to fix it

---

## Implementation

### 1. Code Analysis Prompt

Added section:
```
🎯 REASONING REQUIREMENTS FOR INCORRECT OUTPUTS:
When outputs are wrong, you MUST explain:
1. WHAT is wrong: Specific values, structure, or format that's incorrect
2. WHY it's wrong: What caused the error (wrong function, missing step, incorrect logic)
3. WHAT was expected: Show the correct output or approach from the solution
4. HOW to fix it: Specific code changes needed
```

### 2. Code Suggestions Format

Enhanced to require:
```
"FORMAT WITH DETAILED REASONING - Each suggestion must include:",
"  1. WHAT is wrong: 'You did not complete [section]' OR 'Your [section] output is incorrect'",
"  2. WHY it's wrong: 'This happened because [specific reason]'",
"  3. WHAT was expected: 'The solution shows [expected output/approach]'",
"  4. HOW to fix: 'To fix this, [specific code change needed]'",
```

### 3. Feedback Prompt

Added requirement:
```
🎯 REASONING REQUIREMENTS FOR FEEDBACK:
When discussing incorrect work or areas for improvement, you MUST provide:
1. WHAT needs improvement: Specific aspect that's lacking
2. WHY it matters: Business or analytical impact
3. HOW to improve: Concrete, actionable steps with examples
4. WHAT good looks like: Reference to solution or best practice
```

### 4. Areas for Development Format

Enhanced to require:
```
"REQUIRED FORMAT - Each item must include WHAT, WHY, HOW, and EXAMPLE:",
"WHAT: 'To strengthen your work, you need to [specific improvement]'",
"WHY: 'This is important because [business/analytical reason]'",
"HOW: 'To improve, [specific actionable steps]'",
"EXAMPLE: 'For instance, [concrete example from solution or best practice]'",
```

---

## Real-World Examples

### Example 1: Missing Variable

**Before:**
```
"You did not create product_metrics."
```

**After:**
```
"You did not create the required variable product_metrics. This section requires 
you to calculate Total_Revenue, Total_Quantity, and Order_Frequency for each 
product using group_by(ProductID, Product_Name) %>% summarise(...). The solution 
shows this should produce a data frame with 50 products. Add this code after the 
supplier_metrics section."
```

### Example 2: Wrong Output

**Before:**
```
"Your regional analysis is incomplete."
```

**After:**
```
"Your regional analysis is missing the Avg_Customer_Value calculation. This 
metric is crucial for identifying markets with high customer counts but low 
spending, which are prime targets for marketing campaigns. To add this, use: 
Avg_Customer_Value = Total_Sales / Customer_Count in your summarise() function. 
The solution shows this reveals that Houston has high customer count (18) but 
below-average spending ($2,119 per customer), making it an expansion opportunity."
```

### Example 3: Logic Error

**Before:**
```
"Your join is wrong."
```

**After:**
```
"Your customer_orders_left join shows 200 rows, but it should show all 100 
customers even if they have no orders. This happened because you used 
inner_join() which only keeps matching records. The correct approach is 
left_join(customers, orders, by = 'CustomerID'), which keeps all customers 
and adds NA for those without orders. This is essential for identifying 
customers who haven't made purchases yet."
```

---

## Benefits

### 1. Educational Value
✅ Students learn WHY their code is wrong
✅ Students understand the business impact
✅ Students get specific guidance to improve
✅ Students can apply learning to future work

### 2. Actionable Feedback
✅ Clear steps to fix issues
✅ Specific code examples
✅ Reference to solution
✅ No vague suggestions

### 3. Quality Assurance
✅ AI can't give lazy feedback
✅ Forces detailed analysis
✅ Ensures personalized responses
✅ Maintains high feedback standards

---

## Validation

The prompts now explicitly reject:
- ❌ "Your output is incorrect" (no details)
- ❌ "You need to improve" (no specifics)
- ❌ "Consider adding more" (no guidance)
- ❌ "This could be better" (no actionable steps)

And require:
- ✅ Specific values/structures that are wrong
- ✅ Explanation of root cause
- ✅ Reference to expected output
- ✅ Concrete code to fix it
- ✅ Business/analytical context

---

## Testing

### Test Prompt
When grading a submission with errors, check that feedback includes:

1. **Specific details:** Numbers, variable names, function names
2. **Root cause:** Why the error occurred
3. **Expected result:** What should have happened
4. **Fix instructions:** Exact code changes needed
5. **Context:** Why it matters for analysis

### Quality Checklist
- [ ] Does feedback explain WHAT is wrong specifically?
- [ ] Does feedback explain WHY it's wrong?
- [ ] Does feedback show WHAT was expected?
- [ ] Does feedback provide HOW to fix it?
- [ ] Does feedback include concrete examples?
- [ ] Is feedback actionable and specific?

---

## Summary

### Before
```
"Your output is incorrect."
"You need to complete this section."
"Consider improving your analysis."
```
**Problem:** Vague, not actionable, not educational

### After
```
"Your customer_metrics shows 50 customers but should show 94. This happened 
because you used inner_join() instead of left_join(), excluding customers 
without orders. Use: left_join(customers, orders, by = 'CustomerID') to 
include all customers. This is essential for complete customer analysis."
```
**Solution:** Specific, actionable, educational, with context

---

## Key Principle

**Every piece of feedback must answer:**
1. What's wrong?
2. Why is it wrong?
3. What should it be?
4. How do I fix it?

**No exceptions. No vague feedback.**
