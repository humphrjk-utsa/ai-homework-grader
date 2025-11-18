# What the AI Receives for Grading

## Complete Context Provided to AI Models

When grading a submission, the AI receives comprehensive context to make nuanced assessments:

### 1. Quantitative Validation Results (Already Calculated)

```
Variables Found: 22/22 required variables present
Output Accuracy: 100% (23/23 checks passed)
Base Score: 95.2%
Adjusted Score: 97.6%

This means the student HAS completed work. Focus on quality and approach, not completion.
```

### 2. Section Completion Details

```
VALIDATION RESULTS:
- Variables Found: 22/22
- Sections Complete: 8/9 (89%)
- Execution Rate: 100.0%
- Base Score: 95.2/100
- Output Match Rate: 100.0%
- Output Checks Passed: 23/23

COMPLETED SECTIONS:
  ✅ Part 1: R Basics and Data Import
  ✅ Part 2: Data Cleaning
  ✅ Part 3: Basic Data Transformation
  ✅ Part 4: Advanced Transformation
  ✅ Part 5: Data Reshaping
  ✅ Part 6: Combining Datasets
  ✅ Part 7: String Manipulation & Date/Time
  ✅ Part 8: Advanced Wrangling
  ✅ Part 9: Reflection Questions

INCOMPLETE SECTIONS:
  (None - all sections complete)
```

### 3. Code Comparison

The AI receives:
- **Template Code**: What the student started with
- **Student Code**: What they submitted
- **Solution Code**: Reference implementation

This allows the AI to:
- Identify what the student actually wrote (vs template)
- Compare their approach to the solution
- Recognize valid alternative implementations
- Provide specific, actionable feedback

### 4. Reflection Question Comparison (NEW!)

```
REFLECTION QUESTIONS ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Student answered 5 reflection questions.

QUESTION 9.1: How did handling missing values and outliers affect your analysis?...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STUDENT ANSWER (58 words):
Handling missing values and outliers ensured that the data used for analysis was
more accurate and reliable. Data cleaning is important because it prevents skewed
results and ensures that business decisions are based on complete, trustworthy data.

SOLUTION ANSWER (70 words):
Handling missing values and outliers ensured our analysis was based on complete
and accurate data. Missing values can lead to biased results, while outliers can
skew summary statistics. Data cleaning is crucial before business analysis because
decisions based on flawed data can be costly. Clean data leads to reliable insights.

QUESTION 9.2: What insights did you gain from the regional and category summaries...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STUDENT ANSWER (54 words):
Grouped analysis revealed patterns and trends that were not apparent in the raw data.
Businesses can use this type of analysis to identify top-performing regions, understand
product category performance, and allocate resources more effectively.

SOLUTION ANSWER (76 words):
Grouped analysis revealed that different regions and product categories perform
differently. For example, we could see which regions generate the most revenue
and which product categories are most profitable. Businesses use this to identify
growth opportunities, optimize inventory, target marketing, and allocate resources
to high-performing areas.

[... continues for all 5 questions ...]

GRADING INSTRUCTIONS FOR REFLECTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Compare student answers to solution answers for DEPTH and QUALITY
2. Look for:
   - Understanding of concepts (not just memorization)
   - Business application and real-world connections
   - Critical thinking and analysis
   - Specific examples and details
3. DO NOT require exact wording - accept equivalent understanding
4. DO NOT penalize for different examples if they demonstrate understanding
5. Provide specific feedback on what was good and what could be improved
6. Be nuanced - recognize partial understanding vs complete misunderstanding

SCORING GUIDANCE:
- Excellent (90-100%): Demonstrates deep understanding, provides specific examples, makes business connections
- Good (80-89%): Shows solid understanding, provides some examples, makes some connections
- Adequate (70-79%): Shows basic understanding, limited examples, minimal connections
- Needs Improvement (<70%): Superficial understanding, no examples, missing key concepts
```

### 5. Output Discrepancies (If Any)

If outputs don't match, the AI receives:
```
ISSUES DETECTED:
- Cell 5 output mismatch: Row count differs (expected 100, got 95)
- Cell 12 output mismatch: Missing column 'profit_margin'
```

## What the AI Does With This Information

### Code Analysis (Qwen Model)
1. **Identifies what the student actually wrote** (not template code)
2. **Compares approach to solution** - recognizes valid alternatives
3. **Focuses on cells with wrong outputs** - provides specific fixes
4. **Gives actionable suggestions** with actual code examples using student's variable names

### Feedback Generation (GPT-OSS Model)
1. **Assesses reflection quality** by comparing to solution answers
2. **Evaluates depth of understanding** - not just word count
3. **Recognizes equivalent understanding** even with different wording
4. **Provides nuanced feedback** on what was good and what could be deeper
5. **Makes business connections** and suggests real-world applications

## Key Principles

### The AI Does NOT:
- ❌ Change the score (already calculated by validation layers)
- ❌ Re-check variables or outputs (already done)
- ❌ Penalize for different variable names if outputs match
- ❌ Require exact wording in reflections
- ❌ Give generic feedback

### The AI DOES:
- ✅ Provide qualitative assessment of code quality
- ✅ Compare reflection depth and understanding
- ✅ Give specific, actionable suggestions
- ✅ Recognize valid alternative approaches
- ✅ Focus on learning and improvement
- ✅ Make feedback personal to this student's work

## Example AI Output

### For Code:
```
"code_strengths": [
  "Excellent use of pipe operator (%>%) throughout - your code in Part 3 
   chains select(), filter(), and arrange() cleanly",
  "Strong data cleaning approach in Part 2 - you correctly identified 
   outliers using IQR method with quantile() function",
  "Good business logic in Part 8 - your case_when() for performance_tier 
   uses appropriate revenue thresholds"
]

"code_suggestions": [
  "WHAT: Part 2 could use drop_na() instead of na.omit(). 
   WHY: drop_na() is more explicit and works better with pipes. 
   HOW: Replace na.omit(sales_data) with sales_data %>% drop_na(). 
   EXAMPLE: sales_clean <- sales_data %>% drop_na() %>% filter(Revenue > 0)"
]
```

### For Reflections:
```
"reflection_assessment": [
  "Question 9.1: Good understanding of data cleaning importance. You correctly 
   identified that missing values lead to inaccurate analysis. Consider adding 
   a specific example of how an outlier could skew business decisions.",
  
  "Question 9.2: Solid grasp of grouped analysis value. You mentioned resource 
   allocation which shows business thinking. The solution also discusses inventory 
   optimization - this could strengthen your answer.",
  
  "Question 9.4: Excellent explanation of join differences! Your answer is actually 
   more detailed than the solution, with clear examples of when to use each type."
]
```

## Result

The student receives:
- **Accurate quantitative score** (97.6% / 122/125)
- **Specific qualitative feedback** on code and reflections
- **Actionable suggestions** for improvement
- **Recognition** of what they did well
- **Nuanced assessment** that goes beyond just checking boxes
