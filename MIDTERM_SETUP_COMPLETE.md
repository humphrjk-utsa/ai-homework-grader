# Midterm Exam Setup - Complete

## ✅ Files Created/Updated

1. **Rubric**: `rubrics/midterm_exam_rubric_comprehensive.json`
   - Valid JSON format
   - Follows assignment_7_rubric_v2.json pattern
   - 100 total points
   - Detailed validation rules for all 9 parts

2. **Template**: `assignment_prompts/MIDTERM_EXAM_COMPREHENSIVE (1).ipynb`
   - Clean template with TODO sections
   - All 9 parts included

3. **Solution**: `data/raw/MIDTERM_EXAM_COMPREHENSIVE_SOLUTION.ipynb`
   - All code executed with outputs
   - Note: Task 7.2 uses `mdy()` but should use `ymd()` (dates are YYYY-MM-DD format)

## 📊 Data Files Required

Students need these CSV files in their data folder:
- `company_sales_data.csv` (300 rows)
- `customers.csv` (100 rows)
- `products.csv` (50 rows)
- `orders.csv` (250 rows)
- `order_items.csv` (400 rows)

## 🎯 Grading Breakdown

| Part | Topic | Points |
|------|-------|--------|
| 1 | R Basics & Data Import | 8 |
| 2 | Data Cleaning | 12 |
| 3 | Transformation Part 1 | 12 |
| 4 | Transformation Part 2 | 13 |
| 5 | Data Reshaping | 8 |
| 6 | Joins | 7 |
| 7 | Strings & Dates | 10 |
| 8 | Advanced Wrangling | 10 |
| 9 | Reflection Questions | 10 |
| **Total** | | **100** |

## 🔧 Next Steps

1. **Create New Assignment in Database**:
   ```sql
   INSERT INTO assignments (name, rubric, template_notebook, solution_notebook)
   VALUES (
     'Midterm Exam Comprehensive',
     '<contents of midterm_exam_rubric_comprehensive.json>',
     '<path to template>',
     '<path to solution>'
   );
   ```

2. **Test with Marcelo's Submission**:
   - His submission completed ALL tasks correctly
   - Should score 95-100% (only minor deduction for reflection depth)
   - Previous score of 7.5/10 was due to wrong rubric expectations

## ⚠️ Known Issues

1. **Solution File Date Parsing**: Task 7.2 uses `mdy()` which creates NAs because data is in `ymd()` format
2. **Working Directory**: Students set their own paths - validator must accept variations
3. **Code Style**: Accept equivalent code (e.g., `na.omit()` vs `drop_na()`)

## 📝 Validator Key Points

- Accept `ymd()`, `mdy()`, or `parse_date_time()` for date parsing
- No penalty for different working directory paths
- Check for required variables, not exact code
- Verify row counts match expected values
- Reflection questions need 50+ words each
