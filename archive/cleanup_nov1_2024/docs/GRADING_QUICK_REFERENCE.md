# Grading System Quick Reference

## 🎯 Core Principles

1. **Evidence-Based** - Use output comparison, error detection, variable checking
2. **Semantic** - Order doesn't matter, equivalent expressions accepted
3. **Detailed Reasoning** - Explain WHAT, WHY, EXPECTED, HOW
4. **Fair** - Most restrictive rule wins, no blind boosting

---

## 📊 Validation Rules

| Rule | Condition | Cap |
|------|-----------|-----|
| Errors | 3+ errors | 70% |
| Errors | 1-2 errors | 80% |
| Missing Vars | 3+ missing | 75% |
| Output Match | < 40% | 50% |
| Output Match | 40-59% | 70% |
| Output Match | 60-74% | 80% |
| Incomplete | 10+ sections | 20% |
| Incomplete | 5+ sections | 50% |
| Incomplete | 3+ sections | 70% |

**Most restrictive wins!**

---

## ✅ Semantic Matching

### Outputs Match If:
- ✅ Same numbers (any order)
- ✅ Same row counts
- ✅ Rounding differences (94.7 vs 94.67)
- ✅ Different sort order

### Outputs Don't Match If:
- ❌ Different values (50 vs 94)
- ❌ Errors vs valid output
- ❌ Missing data
- ❌ Wrong calculations

### Written Answers Match If:
- ✅ Same concepts, different words
- ✅ Equivalent terminology
- ✅ Aligned with data
- ✅ Logical and rational

### Written Answers Don't Match If:
- ❌ Wrong concepts
- ❌ Contradicts data
- ❌ Illogical conclusions
- ❌ Wrong values cited

---

## 📝 Feedback Requirements

Every piece of feedback must include:

1. **WHAT** - Specific issue
2. **WHY** - Root cause
3. **EXPECTED** - What should be
4. **HOW** - How to fix

**Example:**
"Your customer_metrics shows 50 customers (WHAT), but should show 94. This happened because you used inner_join() instead of left_join() (WHY), which excluded customers without orders. The correct approach is left_join(customers, orders, by = 'CustomerID') (HOW) to include all customers (EXPECTED)."

---

## 🔍 Quick Checks

### Before Grading
- [ ] Output comparison completed?
- [ ] Errors detected?
- [ ] Required variables checked?
- [ ] Semantic rules applied?

### During Grading
- [ ] Feedback includes WHAT, WHY, EXPECTED, HOW?
- [ ] Order-independent comparison used?
- [ ] Equivalent expressions accepted?
- [ ] Evidence-based scoring?

### After Grading
- [ ] Validator applied caps?
- [ ] Most restrictive rule won?
- [ ] Score matches evidence?
- [ ] Feedback is actionable?

---

## 🚫 Common Mistakes to Avoid

1. ❌ Penalizing different order
2. ❌ Requiring exact wording
3. ❌ Vague feedback
4. ❌ Blind boosting
5. ❌ Ignoring errors
6. ❌ Not checking required variables

---

## 📚 Documentation

- **FINAL_GRADING_IMPROVEMENTS_SUMMARY.md** - Complete overview
- **SEMANTIC_EVALUATION_GUIDE.md** - Semantic matching details
- **REASONING_REQUIREMENTS_ADDED.md** - Feedback requirements
- **OUTPUT_COMPARISON_INTEGRATION.md** - Output comparison details
- **VALIDATOR_FIX_SUMMARY.md** - Validator changes
