# Prompt Fix for Score Clustering

## 🎯 **The Real Problem**

**It's the PROMPTS, not the rubric!**

The rubric is just metadata. The AI never sees most of it. What matters is the **grading prompts** in `business_analytics_grader.py`.

---

## 🔍 **Current Prompts (The Problem)**

### **Code Analysis Prompt (Line 720):**
```python
SCORING GUIDELINES:
- Complete working code with correct outputs: 95-100
- Working code with minor issues: 90-95
- Mostly working with some errors: 85-90  ← EVERYONE GETS THIS!
- Partial implementation: 75-85
```

**Problem:** Most students have "mostly working with some errors" → Everyone gets 85-90%

### **Feedback Prompt (Line 825):**
```python
SCORING GUIDELINES:
- Complete work with thoughtful reflections: 92-100
- Complete work with basic reflections: 88-92
- Mostly complete with good effort: 85-88  ← EVERYONE GETS THIS!
- Partial completion: 75-85
```

**Problem:** Most students show "good effort" → Everyone gets 85-88%

---

## 💡 **The Fix**

### **New Scoring Guidelines (Stricter):**

```python
SCORING GUIDELINES - STRICT DIFFERENTIATION REQUIRED:

EXCELLENT (90-100):
- ALL sections complete with outputs
- ALL outputs are CORRECT (match expected results)
- Code is clean, well-organized
- No significant errors
- Demonstrates mastery

GOOD (80-89):
- Most sections complete (7-8 of 8)
- Most outputs correct (80-90% accuracy)
- Minor errors that don't affect results
- Solid understanding shown

ADEQUATE (70-79):
- Some sections complete (5-6 of 8)
- Some outputs correct (60-80% accuracy)
- Several errors affecting some results
- Basic understanding shown

POOR (60-69):
- Few sections complete (3-4 of 8)
- Many outputs wrong or missing (40-60% accuracy)
- Major errors affecting results
- Minimal understanding

FAILING (0-59):
- Mostly incomplete (0-2 of 8)
- Template only or no outputs (<40% accuracy)
- Fundamental misunderstanding

CRITICAL RULES:
1. NO OUTPUT = 0 points for that section
2. WRONG OUTPUT = Deduct heavily (not just minor issue)
3. TEMPLATE ONLY = Maximum 10 points total
4. COUNT SECTIONS: Score cannot exceed (completed/total) × 100
5. DIFFERENTIATE: Not everyone should get 85%!

EXAMPLES:
- 8/8 complete, all correct → 95-100
- 8/8 complete, 2 wrong → 80-85
- 6/8 complete, all correct → 75-80
- 6/8 complete, 2 wrong → 65-70
- 4/8 complete → 50-60 maximum
- Template only → 5-10 maximum
```

---

## 🔧 **Implementation**

### **File to Update:**
`business_analytics_grader.py`

### **Lines to Change:**
1. **Line 780-785:** Code analysis scoring guidelines
2. **Line 870-875:** Feedback scoring guidelines

### **New Prompt Section:**

```python
STRICT SCORING REQUIREMENTS:

1. COUNT COMPLETED SECTIONS:
   - Section is "complete" ONLY if it has output AND output is correct
   - Count: X sections complete out of Y total
   - Maximum possible score = (X/Y) × 100

2. EVALUATE OUTPUT CORRECTNESS:
   - Compare student output to expected output
   - Wrong output = major deduction (not minor issue)
   - No output = 0 points for that section

3. APPLY PENALTIES:
   - Each wrong output: -10 to -15 points
   - Each missing section: -12.5 points (for 8 sections)
   - Syntax errors: -3 points each
   - Template only: Cap at 10 points total

4. DIFFERENTIATE SCORES:
   - Excellent work (all correct): 90-100
   - Good work (mostly correct): 80-89
   - Adequate work (some correct): 70-79
   - Poor work (few correct): 60-69
   - Failing (template/incomplete): 0-59

5. REALISTIC DISTRIBUTION:
   - Only 10-20% should score 90+
   - Only 25-35% should score 80-89
   - Most should score 70-79
   - Some should score 60-69
   - Template only should score <20

DO NOT give everyone 85%. Spread scores based on actual completion and correctness.
```

---

## 📊 **Expected Impact**

### **Before (Current Prompts):**
```
"Mostly working with some errors" → 85-90%
Everyone gets this → No differentiation
```

### **After (New Prompts):**
```
8/8 correct → 95%
8/8 with 2 wrong → 82%
6/8 correct → 75%
4/8 complete → 55%
Template → 10%
```

---

## 🎯 **Quick Fix (Add to Both Prompts)**

Add this section right before "OUTPUT ONLY THIS JSON":

```python
MANDATORY SCORING RULES (OVERRIDE ALL OTHER GUIDELINES):

1. Count sections with correct outputs: __/8
2. Maximum score = (correct_sections/8) × 100
3. Apply quality deductions within that maximum
4. Template only = 10 points maximum
5. No output = 0 points for that section

Example calculations:
- 8/8 correct, excellent quality = 95-100 points
- 8/8 correct, good quality = 90-95 points
- 7/8 correct = 87.5 maximum, actual 82-87
- 6/8 correct = 75 maximum, actual 70-75
- 4/8 correct = 50 maximum, actual 45-50
- 0/8 or template = 10 maximum

CRITICAL: Do NOT give 85% to everyone. Differentiate based on actual correctness.
```

---

## 🔍 **Testing**

After updating prompts, test with:

1. **Perfect submission** → Should get 95-100%
2. **Good submission (1-2 errors)** → Should get 80-89%
3. **Half complete** → Should get 50-60%
4. **Template only** → Should get 5-10%

If scores still cluster, prompts need to be even stricter.

---

## 💡 **Why Prompts Matter More Than Rubric**

**Rubric:**
- Metadata for humans
- AI sees small parts of it
- Mostly for documentation

**Prompts:**
- Direct instructions to AI
- AI follows these literally
- These control the actual scoring

**Fix the prompts = Fix the scoring!**

---

## 🎓 **Summary**

**Problem:** Prompts say "mostly working = 85-90%" → Everyone gets 85%

**Solution:** Update prompts to:
1. Count completed sections
2. Require correct outputs (not just any output)
3. Apply strict penalties
4. Force differentiation
5. Cap scores by completion percentage

**File to update:** `business_analytics_grader.py`
**Lines:** 780-785 and 870-875
**Impact:** Scores will spread from 40-95% instead of 80-90%

**Next:** Want me to update the prompts now?
