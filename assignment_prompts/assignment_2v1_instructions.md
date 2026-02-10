# Assignment 2v1 - Grading Instructions

## For Code Analysis Prompt:

```
ASSIGNMENT 2V1 - DATA CLEANING ASSIGNMENT

OPTIONAL SECTIONS (students choose ONE):
- Part 2.2 (Option A: Remove missing values) OR Part 2.3 (Option B: Impute missing values)
- Part 3.3 (Option A: Remove outliers) OR Part 3.4 (Option B: Cap outliers)

REQUIRED SECTIONS (12 total):
1. Data import and setup
2. Initial data assessment
3. Missing value identification (calculate total, per column, incomplete rows)
4. Missing value treatment (complete Option A OR Option B, not both)
5. Compare missing value strategies
6. Outlier detection using IQR method
7. Outlier visualization (boxplot)
8. Outlier treatment (complete Option A OR Option B, not both)
9. Final dataset selection with justification
10. Comparison summary table
11. Reflection question 1 (missing value strategy)
12. Reflection question 2 (outlier interpretation)

SCORING CALCULATION:
- Base score = (completed sections / 12) × 100
- Completing Option A OR Option B counts as completing that section
- Do NOT penalize for choosing one option over another
- Do NOT penalize if "# YOUR CODE HERE" comments remain but working code exists

IMPORTANT:
- Check OUTPUTS to verify completion, not just code presence
- If code produces correct results, section is complete
- Accept different valid approaches (mean vs median, different IQR thresholds, etc.)
```

## For Feedback Prompt:

```
ASSIGNMENT 2V1 - DATA CLEANING ASSIGNMENT

REFLECTION QUESTIONS (2 required):
1. Missing Value Strategy - When to remove vs impute? Provide business examples.
2. Outlier Interpretation - What could outliers represent? Should they be removed?

METHODOLOGY CHOICES (both valid):
- Option A (Removal): Valid if student explains trade-offs (sample size vs data quality)
- Option B (Imputation/Capping): Valid if student explains impact on analysis

EVALUATION FOCUS:
- Did student complete at least ONE missing value treatment option?
- Did student complete at least ONE outlier treatment option?
- Did student justify their final dataset choice?
- Did student answer BOTH reflection questions with business context?

SCORING:
- Reflection quality based on depth, business examples, critical thinking
- Methodology appropriateness based on justification, not which option chosen
- Accept different valid approaches (mean/median/mode imputation all valid)
```

---

## How to Add These in Prompt Manager:

1. Go to **Prompt Manager** in the UI
2. Select **"Assignment Prompts"** tab
3. Choose **"assignment 2v1"** from dropdown
4. For **Code Analysis**: Paste the "For Code Analysis Prompt" section above
5. For **Feedback**: Paste the "For Feedback Prompt" section above
6. Click **Save** for each

The system will automatically combine these with the general prompts when grading assignment 2v1.
