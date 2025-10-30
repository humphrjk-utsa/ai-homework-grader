# Assignment 5 - Data Reshaping with tidyr - Grading Setup

## Files Created

### 1. Rubric
**File:** `rubrics/assignment_5_rubric.json`

**Structure:**
- **Total Points:** 100
- **Components:**
  - Technical Execution (25%) - Code quality and syntax
  - Data Reshaping (40%) - Core reshaping tasks (MOST IMPORTANT)
  - Data Validation (15%) - Validation checks
  - Reflection Questions (20%) - Critical thinking

**Key Sections:**
- Part 1: Data Import (3 points)
- Part 2: Wide to Long (12 points) - 3 tasks
- Part 3: Long to Wide (12 points) - 3 tasks
- Part 4: Complex Reshaping (5 points)
- Part 5: Business Applications (5 points)
- Part 6: Validation (3 points)
- Reflection Questions (20 points) - 5 questions

### 2. Assignment-Specific Prompt
**File:** `assignment_prompts/a5_data_reshaping_prompt.txt`

**Contents:**
- Assignment overview and learning objectives
- Critical grading points
- Required variables (9 total)
- Common student errors to check
- Specific function usage to verify
- Validation checks to look for
- Business context evaluation
- Grading workflow (4 steps)
- Red flags and excellence indicators
- Partial credit guidelines

## Required Variables to Check

Students must create these 9 variables:

**Imported:**
1. `quarterly_sales_wide`
2. `survey_responses_long`
3. `employee_skills_wide`

**Created in Part 2 (Wide to Long):**
4. `quarterly_sales_long` (Task 2.1)
5. `quarterly_sales_parsed` (Task 2.2)
6. `employee_skills_long` (Task 2.3)

**Created in Part 3 (Long to Wide):**
7. `survey_responses_wide` (Task 3.1)
8. `sales_by_region_wide` (Task 3.2)
9. `skills_matrix` (Task 3.3)

## Core Functions to Verify

**pivot_longer():**
- `cols` parameter
- `names_to` parameter
- `values_to` parameter
- `names_sep` (for parsing)

**pivot_wider():**
- `names_from` parameter
- `values_from` parameter
- `names_prefix` (optional)
- `values_fill` (optional)

## Grading Weights

```
Technical Execution:    25 points (25%)
Data Reshaping:         40 points (40%) ← MOST IMPORTANT
Data Validation:        15 points (15%)
Reflection Questions:   20 points (20%)
─────────────────────────────────────
Total:                 100 points
```

## Common Issues to Watch For

1. **File Path Errors** - Students may have incorrect paths to data files
2. **Hardcoded Column Names** - Using specific names that don't exist in data
3. **Missing Validation** - Skipping validation checks entirely
4. **Blank Reflections** - Not filling in reflection question answers
5. **Syntax Errors** - Code that doesn't run

## Reflection Questions

Five questions requiring 150-200 words each:

1. **Strategic Format Selection** (4 points)
   - Business scenario requiring wide-to-long conversion
   - Reasoning and stakeholder impact

2. **Validation Importance** (4 points)
   - Why validation is crucial
   - Business impact of skipping validation

3. **Efficiency and Learning** (4 points)
   - Evolution of thinking
   - Time savings estimates

4. **Stakeholder Communication** (4 points)
   - Different formats for different audiences
   - Executive vs. technical team needs

5. **Future Applications** (4 points)
   - Three specific scenarios
   - Data types, operations, and business outcomes

## Autograder Integration

The rubric includes an `autograder_checks` section with:
- List of required variables
- List of required functions
- Validation checks to verify

This can be used to automate initial scoring before human review.

## Grade Ranges

- **A (90-100):** Excellent mastery, complete validation, thoughtful reflection
- **B (80-89):** Good understanding, most tasks complete, adequate reflection
- **C (70-79):** Basic competency, some incomplete tasks, limited reflection
- **D (60-69):** Minimal understanding, many incomplete tasks
- **F (0-59):** Insufficient work or understanding

## Bonus Opportunities

- Exceptional validation beyond requirements: up to 5 points
- Advanced tidyr features not covered: up to 3 points
- Exceptional business insights: up to 2 points

## Notes for Graders

- This assignment tests both technical skills AND strategic thinking
- Weight technical execution heavily (65% combined for execution + reshaping)
- Don't ignore reflection component (20%) - it shows understanding
- Look for evidence of learning and growth, not just correct answers
- Partial credit available for good attempts with minor errors
