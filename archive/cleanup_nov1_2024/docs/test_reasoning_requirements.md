# Test: Reasoning Requirements in Feedback

## Test Scenario

**Student Submission:** Assignment 6 with errors
- Missing `product_metrics` variable
- Wrong join type in `customer_orders_left`
- Missing `Avg_Customer_Value` in regional analysis

---

## Expected Feedback Format

### For Missing Variable (product_metrics)

**Required Elements:**
1. ✅ WHAT: "You did not create the required variable product_metrics"
2. ✅ WHY: "This section requires calculating Total_Revenue, Total_Quantity, and Order_Frequency"
3. ✅ EXPECTED: "The solution shows this should produce a data frame with 50 products"
4. ✅ HOW: "Use: product_metrics <- complete_data %>% group_by(ProductID, Product_Name) %>% summarise(...)"

**Full Example:**
```
"You did not create the required variable product_metrics. This section requires 
you to calculate Total_Revenue, Total_Quantity, and Order_Frequency for each 
product using group_by(ProductID, Product_Name) %>% summarise(Total_Revenue = 
sum(Unit_Price * Quantity), Total_Quantity = sum(Quantity), Order_Frequency = 
n_distinct(OrderID)). The solution shows this should produce a data frame with 
50 products showing which products generate the most revenue. Add this code in 
Part 5.2 after the customer_metrics section."
```

---

### For Wrong Join Type

**Required Elements:**
1. ✅ WHAT: "Your customer_orders_left shows 200 rows instead of all 100 customers"
2. ✅ WHY: "This happened because you used inner_join() instead of left_join()"
3. ✅ EXPECTED: "Should keep all customers even if they have no orders"
4. ✅ HOW: "Change to: customer_orders_left <- left_join(customers, orders, by = 'CustomerID')"

**Full Example:**
```
"Your customer_orders_left join shows 200 rows, but it should show all 100 
customers even if they have no orders. This happened because you used 
inner_join() which only keeps matching records, excluding customers without 
orders. The correct approach is left_join(customers, orders, by = 'CustomerID'), 
which keeps all customers and adds NA for those without orders. This is essential 
for identifying customers who haven't made purchases yet, which is valuable for 
marketing campaigns."
```

---

### For Missing Calculation

**Required Elements:**
1. ✅ WHAT: "Your regional_analysis is missing the Avg_Customer_Value metric"
2. ✅ WHY: "This metric identifies markets with high potential but low current spending"
3. ✅ EXPECTED: "Solution shows Houston has 18 customers but only $2,119 average value"
4. ✅ HOW: "Add: Avg_Customer_Value = Total_Sales / Customer_Count in your summarise()"

**Full Example:**
```
"Your regional_analysis is missing the Avg_Customer_Value calculation. This 
metric is crucial for identifying markets with high customer counts but low 
spending, which are prime targets for marketing campaigns. To add this, include 
Avg_Customer_Value = Total_Sales / Customer_Count in your summarise() function. 
The solution shows this reveals that Houston has high customer count (18) but 
below-average spending ($2,119 per customer), making it an expansion opportunity 
where targeted promotions could increase per-customer revenue."
```

---

## Validation Checklist

For each piece of feedback, verify:

- [ ] **Specific Details:** Includes actual values, variable names, function names
- [ ] **Root Cause:** Explains why the error occurred (wrong function, missing step, logic error)
- [ ] **Expected Result:** Shows what the correct output should be
- [ ] **Fix Instructions:** Provides exact code changes needed
- [ ] **Business Context:** Explains why it matters for analysis
- [ ] **No Vague Language:** Avoids "consider", "could", "might want to"
- [ ] **Actionable:** Student can immediately apply the fix

---

## Red Flags (Reject These)

### ❌ Too Vague
```
"Your output is incorrect."
"You need to complete this section."
"Consider improving your analysis."
```

### ❌ No Root Cause
```
"Your customer_metrics is wrong. Fix it by using the correct join."
```
(Doesn't explain WHY it's wrong or WHAT join to use)

### ❌ No Specifics
```
"Your regional analysis needs more metrics."
```
(Doesn't say WHICH metrics or HOW to add them)

### ❌ No Context
```
"Add Avg_Customer_Value to your code."
```
(Doesn't explain WHY it matters or WHERE to add it)

---

## Grading the Feedback

### Excellent Feedback (90-100%)
- ✅ All 4 elements present (WHAT, WHY, EXPECTED, HOW)
- ✅ Specific values and code examples
- ✅ Business context included
- ✅ Immediately actionable
- ✅ Educational value

### Good Feedback (75-89%)
- ✅ 3-4 elements present
- ✅ Mostly specific
- ⚠️ Some vague language
- ✅ Generally actionable

### Adequate Feedback (60-74%)
- ⚠️ 2-3 elements present
- ⚠️ Some specifics missing
- ⚠️ Limited context
- ⚠️ Partially actionable

### Poor Feedback (Below 60%)
- ❌ 0-1 elements present
- ❌ Vague and generic
- ❌ No context
- ❌ Not actionable

---

## Test Cases

### Test Case 1: Error in Output
**Input:** Code produces "Error: object 'product_metrics' not found"

**Expected Feedback:**
```
"Your code in Part 5.2 produces an error: 'object product_metrics not found'. 
This happened because you did not create the product_metrics variable before 
trying to use it in the output statement. You need to add code that creates 
this variable using: product_metrics <- complete_data %>% group_by(ProductID, 
Product_Name) %>% summarise(Total_Revenue = sum(Unit_Price * Quantity), 
Total_Quantity = sum(Quantity), Order_Frequency = n_distinct(OrderID)). 
The solution shows this should analyze all 50 products to identify top sellers."
```

### Test Case 2: Wrong Output Values
**Input:** customer_metrics shows 50 customers instead of 94

**Expected Feedback:**
```
"Your customer_metrics output shows only 50 customers, but the solution shows 
94 customers. This discrepancy occurred because you used inner_join() in your 
multi-table join chain, which excluded customers without complete order data. 
To fix this, use left_join() when joining customers to preserve all customer 
records: orders_customers_items <- inner_join(orders_items, customers, by = 
'CustomerID'). This ensures your customer analysis includes all customers in 
the database, not just those with complete transaction histories."
```

### Test Case 3: Missing Required Column
**Input:** supplier_metrics missing Total_Revenue column

**Expected Feedback:**
```
"Your supplier_metrics variable is missing the Total_Revenue column, which is 
required for the critical_suppliers analysis in Part 6.3. This happened because 
you only calculated Product_Count without including revenue metrics. To fix 
this, modify your summarise() to include: Total_Revenue = sum(Unit_Price * 
Quantity, na.rm = TRUE). The solution shows this is essential for identifying 
which suppliers contribute most to business revenue, not just product diversity. 
Add this calculation alongside Product_Count in your supplier_metrics code."
```

---

## Summary

**Every piece of feedback must be:**
1. **Specific** - Exact values, variables, functions
2. **Explanatory** - Root cause of the issue
3. **Comparative** - What was expected vs what happened
4. **Actionable** - Exact code to fix it
5. **Contextual** - Why it matters for analysis

**No vague, generic, or unhelpful feedback allowed.**
