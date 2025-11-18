# Midterm Exam - Complete Grading Setup

## Files Created

### 1. Exam Template
- **File:** `data/raw/MIDTERM_EXAM_COMPREHENSIVE.ipynb`
- **Purpose:** Student template with TODO sections
- **Sections:** 9 parts covering Lessons 1-8 + reflections

### 2. Solution Notebook
- **File:** `data/raw/MIDTERM_EXAM_COMPREHENSIVE_SOLUTION.ipynb`
- **Purpose:** Complete solution for grader reference
- **Content:** All code cells filled in, all reflections answered

### 3. Rubric
- **File:** `rubrics/midterm_exam_rubric.json`
- **Purpose:** Grading criteria for RubricDrivenValidator
- **Points:** 100 total
  - Technical Execution: 40 points
  - Code Quality: 20 points
  - Business Understanding: 20 points
  - Analysis & Insights: 15 points
  - Reflection Questions: 5 points

### 4. Assignment-Specific Prompts
- **Code Analysis:** `assignment_prompts/midterm_exam_code_analysis_prompt.txt`
- **Feedback:** `assignment_prompts/midterm_exam_feedback_prompt.txt`
- **Purpose:** Guide AI to provide exam-specific feedback

### 5. Data Requirements
- **File:** `data/raw/MIDTERM_EXAM_DATA_REQUIREMENTS.md`
- **Purpose:** Documents required CSV files and structure

## How to Set Up Grading

### Step 1: Create Assignment in Database

```python
import sqlite3
import json

conn = sqlite3.connect('grading_system.db')
cursor = conn.cursor()

# Load rubric
with open('rubrics/midterm_exam_rubric.json', 'r') as f:
    rubric = json.load(f)

# Insert assignment
cursor.execute("""
    INSERT INTO assignments (name, description, rubric, template_notebook, solution_notebook, total_points)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    'midterm_exam',
    'Midterm Exam - Comprehensive R Data Wrangling Assessment (Lessons 1-8)',
    json.dumps(rubric),
    'data/raw/MIDTERM_EXAM_COMPREHENSIVE.ipynb',
    'data/raw/MIDTERM_EXAM_COMPREHENSIVE_SOLUTION.ipynb',
    100.0
))

conn.commit()
conn.close()
```

### Step 2: Generate Sample Data (if needed)

Run the R script from `MIDTERM_EXAM_DATA_REQUIREMENTS.md` to create:
- `data/processed/company_sales_data.csv`
- `data/processed/customers.csv`
- `data/processed/products.csv`
- `data/processed/orders.csv`
- `data/processed/order_items.csv`

### Step 3: Test Grading System

```python
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

# Initialize grader with midterm rubric and solution
grader = BusinessAnalyticsGraderV2(
    rubric_path='rubrics/midterm_exam_rubric.json',
    solution_path='data/raw/MIDTERM_EXAM_COMPREHENSIVE_SOLUTION.ipynb'
)

# Grade a test submission
result = grader.grade_submission(
    student_code=student_code,
    student_markdown=student_markdown,
    template_code=template_code,
    solution_code=solution_code,
    assignment_info={
        'name': 'midterm_exam',
        'title': 'Midterm Exam - Comprehensive R Data Wrangling Assessment'
    },
    notebook_path='path/to/student/submission.ipynb'
)
```

## Grading Flow

```
Student Submission
       ↓
RubricDrivenValidator
  - Checks all required variables
  - Validates function usage
  - Scores each section (Parts 1-9)
       ↓
SmartOutputValidator
  - Compares outputs with solution
  - Checks data structures
  - Validates calculations
       ↓
AI Analysis (Qwen + GPT-OSS)
  - Uses midterm_exam_code_analysis_prompt.txt
  - Uses midterm_exam_feedback_prompt.txt
  - Generates specific feedback
       ↓
Score Validation
  - Ensures scores don't exceed maximums
  - Validates component breakdowns
       ↓
PDF Report Generation
  - Comprehensive feedback
  - Section-by-section breakdown
  - Reflection question assessment
```

## Required Variables (Autograder Checks)

The validator will check for these exact variable names:

**Part 1 (Setup):**
- sales_data, customers, products, orders, order_items

**Part 2 (Cleaning):**
- missing_summary, sales_clean, outlier_analysis

**Part 3 (Transformation 1):**
- sales_summary, high_revenue_sales, top_sales, regional_top_sales

**Part 4 (Transformation 2):**
- sales_enhanced, overall_summary, regional_summary, category_summary

**Part 5 (Reshaping):**
- region_category_revenue, revenue_wide, revenue_long

**Part 6 (Joins):**
- customer_orders, orders_with_items

**Part 7 (Strings & Dates):**
- sales_enhanced (with new columns: region_clean, category_clean, date_parsed, sale_month, sale_weekday)

**Part 8 (Advanced):**
- sales_enhanced (with performance_tier), business_kpis

## Scoring Breakdown

| Part | Lesson | Points | Focus |
|------|--------|--------|-------|
| 1 | R Basics & Import | 10 | Working directory, packages, data import |
| 2 | Data Cleaning | 15 | Missing values, outliers (IQR method) |
| 3 | Transformation 1 | 10 | select, filter, arrange, pipes |
| 4 | Transformation 2 | 15 | mutate, summarize, group_by |
| 5 | Reshaping | 10 | pivot_wider, pivot_longer |
| 6 | Joins | 10 | left_join, inner_join |
| 7 | Strings & Dates | 15 | str_*, mdy, month, wday |
| 8 | Advanced | 10 | case_when, KPIs |
| 9 | Reflections | 5 | 5 questions × 1 point each |
| **Total** | | **100** | |

## Common Issues to Watch For

1. **Variable Names:** Students must use exact names (sales_clean, not sales_cleaned)
2. **Outlier Formula:** Must use IQR method: Q1 - 1.5*IQR and Q3 + 1.5*IQR
3. **Join Types:** left_join for customers/orders, inner_join for orders/items
4. **Date Parsing:** mdy() for MM/DD/YYYY format
5. **case_when:** Must include TRUE ~ "Low" as default
6. **Pipe Operator:** Should be used consistently throughout
7. **Reflection Questions:** Minimum 30 words each

## Testing Checklist

Before grading real submissions:

- [ ] Rubric loads correctly
- [ ] Solution notebook has all cells executed
- [ ] Validator recognizes all required variables
- [ ] AI prompts load from assignment_prompts/
- [ ] Sample data files exist in data/processed/
- [ ] PDF report generates successfully
- [ ] Scores don't exceed maximums
- [ ] Feedback is specific to midterm exam

## Notes

- This is a comprehensive exam covering ALL course material
- Students have 4 hours to complete
- All code must be executed (outputs visible)
- Template-only submissions receive 0 points
- Partial credit available for correct logic with minor errors
- Reflection questions worth 5% of total grade
