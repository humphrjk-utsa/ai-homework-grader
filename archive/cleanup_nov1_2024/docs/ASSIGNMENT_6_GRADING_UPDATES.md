# Assignment 6 Grading Updates

## 🎯 Key Changes to Rubric

### **1. Unexecuted Cells Penalty**

**Problem:** Students submit notebooks with code but no outputs (cells not run)

**Solution:**
```json
"execution_requirements": {
  "cells_must_be_run": true,
  "penalty": "Each unexecuted cell = 2 points deduction",
  "note": "Students must run ALL cells before submission"
}
```

**Impact:**
- Clear penalty for not running code
- Encourages students to test their work
- Easy to verify (count cells without outputs)

---

### **2. Creative Coding Allowed**

**Problem:** Students use their own approaches instead of cookie-cutter code

**Solution:**
```json
"creative_coding": {
  "allowed": true,
  "grading_focus": "Grade on RESULTS and OUTPUTS, not exact code matching",
  "key_principle": "If output is correct, code approach is acceptable"
}
```

**Examples of Acceptable Creativity:**
- ✅ Different variable names (as long as final required variables exist)
- ✅ Additional intermediate steps
- ✅ Alternative pipe chains
- ✅ Extra analysis beyond requirements
- ✅ Helper functions

**Grading Rule:**
> **If the output is correct, the approach is acceptable**

---

### **3. Output Validation Focus**

**New Section: `output_validation`**

**Key Principles:**
1. **Results matter more than code style**
2. **Check output correctness, not code matching**
3. **Accept alternative solutions if outputs are correct**

**Validation Rules:**
```
Step 1: Does output exist? (No output = 0 points)
Step 2: Is output correct? (Compare to expected results)
Step 3: Are required variables created? (Check final variables)
Step 4: Award points based on correctness
```

---

### **4. AI Grading Instructions**

**New Section: `ai_grading_instructions`**

**Primary Focus:** OUTPUT VALIDATION
- Check if results are correct
- Verify row counts, column names, values

**Secondary Focus:** CODE EXECUTION
- Count cells with/without outputs
- Apply execution penalty

**Tertiary Focus:** CODE QUALITY
- Assess approach only if outputs are wrong
- Don't penalize creative solutions

**Step-by-Step Process:**
```
1. Count total code cells and cells with outputs
2. Calculate execution penalty: (unexecuted_cells × 2 points)
3. For each section, check if REQUIRED VARIABLES exist
4. For each variable, validate OUTPUT shows correct results
5. Award points based on OUTPUT correctness, not code style
6. Accept creative solutions if outputs are correct
7. Deduct only for wrong outputs or missing execution
```

---

### **5. Common Scenarios**

**Scenario 1: Different Variable Names**
```
Student code:
  my_customer_data <- inner_join(customers, orders)
  customer_orders <- my_customer_data  # Creates required variable

Grading: ✅ Full credit (required variable exists with correct output)
```

**Scenario 2: Extra Analysis**
```
Student adds:
  customer_orders %>%
    summarize(avg_amount = mean(Amount))  # Beyond requirements

Grading: ✅ Full credit + bonus for initiative
```

**Scenario 3: Alternative Approach**
```
Student uses:
  customer_orders <- merge(customers, orders, by="CustomerID")
  # Instead of inner_join()

Grading: ✅ Full credit if output is correct (accepts base R merge)
```

**Scenario 4: Unexecuted Cells**
```
Student has code but no output (cell not run)

Grading: ❌ Deduct 2 points per cell, 0 points for that section
```

**Scenario 5: Wrong Output**
```
Output shows 50 rows when should be 100

Grading: ⚠️ 50% credit for attempt, explain what's wrong
```

---

### **6. Assignment Prompt Additions**

**Add to homework instructions:**

```markdown
⚠️ IMPORTANT: You MUST run ALL code cells before submission. 
   Cells without outputs will lose points!

✅ You may use your own approach as long as you create the 
   required variables with correct results.

📊 Your outputs will be graded for correctness. Make sure 
   your results match the expected values.

🎯 Required variables that MUST exist:
   - customers, orders, order_items, products, suppliers
   - customer_orders, customer_orders_left, customer_orders_right, customer_orders_full
   - orders_items, orders_customers_items, complete_order_data, complete_data
   - customers_no_orders, orphaned_orders, products_never_ordered, active_customers
   - customer_metrics, product_metrics, supplier_metrics, regional_analysis
   - top_customers, product_combinations, critical_suppliers, market_expansion

✅ Test your work: After each section, check that your output 
   makes sense and matches the expected row counts.
```

---

## 📊 Grading Examples

### **Example 1: Perfect Submission**
```
✅ All cells executed (outputs visible)
✅ All required variables created
✅ Outputs show correct results
✅ Creative approach used (different intermediate steps)

Score: 95-100 points
Feedback: "Excellent work! Your creative approach shows 
           deep understanding. All outputs are correct."
```

### **Example 2: Good Work, Some Unexecuted**
```
⚠️ 3 cells not executed (no outputs)
✅ Most required variables created
✅ Executed cells show correct outputs

Score: 80-85 points (minus 6 points for unexecuted cells)
Feedback: "Good work on executed sections. Please run ALL 
           cells before submission. Lost 6 points for 3 
           unexecuted cells."
```

### **Example 3: Creative but Incomplete**
```
✅ All cells executed
✅ Creative approach with extra analysis
⚠️ Missing 2 required variables
⚠️ One output shows wrong row count

Score: 70-75 points
Feedback: "Creative approach appreciated! However, missing 
           customer_metrics and product_metrics variables. 
           Also, customer_orders should have 100 rows, not 50."
```

### **Example 4: Template Only**
```
❌ Most cells not executed
❌ Only template code, no student work
❌ No outputs visible

Score: 0-20 points (capped)
Feedback: "This appears to be template code only. Please 
           complete the assignment and run all cells."
```

---

## 🎯 Key Takeaways for Grading

### **DO:**
- ✅ Focus on output correctness
- ✅ Accept creative solutions
- ✅ Verify all cells are executed
- ✅ Check required variables exist
- ✅ Compare output values to expected results
- ✅ Give partial credit for attempts

### **DON'T:**
- ❌ Penalize for different code style
- ❌ Require exact code matching
- ❌ Deduct for extra analysis
- ❌ Penalize alternative approaches if correct
- ❌ Focus on code aesthetics over results

### **Critical Rules:**
1. **No output = 0 points** for that section
2. **Unexecuted cell = 2 points** deduction each
3. **Correct output = full credit** regardless of approach
4. **Wrong output = 50% credit** with explanation
5. **Creative solutions = bonus** if they show understanding

---

## 🔧 Implementation

### **For AI Grader:**

The AI will now:
1. Count cells without outputs (execution check)
2. Verify required variables exist (variable check)
3. Validate output correctness (result check)
4. Accept creative approaches (flexibility)
5. Provide specific feedback on what's wrong

### **For Students:**

Students now know:
1. Must run ALL cells before submission
2. Can use creative approaches
3. Outputs will be validated for correctness
4. Required variables must exist with exact names
5. Testing their work is important

---

## 📝 Summary

**Main Changes:**
1. ✅ Penalty for unexecuted cells (2 points each)
2. ✅ Creative coding explicitly allowed
3. ✅ Focus on output validation, not code matching
4. ✅ Clear grading scenarios documented
5. ✅ Assignment prompt additions for clarity

**Expected Impact:**
- Students will run all cells before submission
- More creative solutions will be accepted
- Grading will be more fair and consistent
- Focus shifts from code style to results
- Clear expectations for both students and AI

**Result:** Better grading that rewards understanding and correct results while penalizing incomplete work!
