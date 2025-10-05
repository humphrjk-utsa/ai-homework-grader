# Submission Preprocessing System

## Overview

The preprocessing system automatically normalizes and cleans student submissions before AI grading to improve parsing success and grading consistency.

## What It Does

The preprocessor fixes common issues that can cause AI parsing failures:

### 1. **Uncomments Essential Libraries**
```r
# Before:
# library(tidyverse)

# After:
library(tidyverse)
```

### 2. **Fixes Pipe Chain Syntax Errors**
```r
# Before:
data %>% count(data$column)

# After:
data %>% count(column)
```

### 3. **Normalizes Whitespace**
- Removes excessive blank lines
- Standardizes formatting

### 4. **Fixes Common R Syntax Issues**
- Normalizes operators spacing
- Converts smart quotes to regular quotes

## How It Works

### Architecture

```
Submission → Preprocessor → Cleaned Code → AI Grader → Results
                ↓
         Fixes Tracked
                ↓
         Added to Report
```

### Integration Points

1. **connect_web_interface.py** - Preprocessing happens in `grade_submission_internal()`
2. **business_analytics_grader.py** - Receives preprocessing info and includes in results
3. **report_generator.py** - Displays preprocessing info in PDF reports

## Usage

### Automatic (in grading flow)

Preprocessing happens automatically when grading submissions:

```python
# In connect_web_interface.py
preprocessor = SubmissionPreprocessor()
student_code, student_markdown, fixes_applied = preprocessor.preprocess_notebook(notebook_path)
```

### Manual Testing

Test preprocessing on a specific notebook:

```bash
python submission_preprocessor.py path/to/notebook.ipynb
```

### Programmatic Use

```python
from submission_preprocessor import preprocess_submission_for_grading

result = preprocess_submission_for_grading('notebook.ipynb')

print(result['preprocessing_summary'])
print(f"Fixes: {result['fixes_applied']}")
print(f"Needs review: {result['needs_manual_review']}")
```

## Output

### In Grading Results

Preprocessing info is included in the grading result:

```python
{
    'final_score': 26.1,
    'preprocessing': {
        'fixes_applied': [
            'Uncommented library(tidyverse)',
            'Fixed pipe chain $ notation in count()'
        ],
        'needs_manual_review': False
    },
    ...
}
```

### In PDF Reports

A "Submission Preprocessing" section appears in reports when fixes were applied:

```
Submission Preprocessing
------------------------
Your submission was automatically normalized before grading to fix 2 common issue(s).

Fixes Applied:
• Uncommented library(tidyverse)
• Fixed pipe chain $ notation in count()
```

### Manual Review Flag

If more than 5 fixes are needed, the submission is flagged for manual review:

```
Note: Multiple preprocessing fixes were needed. Your instructor may review 
this submission manually to ensure accuracy.
```

## Benefits

1. **Improved AI Parsing** - Fixes syntax issues that confuse the AI
2. **Consistent Grading** - All submissions normalized to same standard
3. **Transparency** - Students see what was fixed
4. **Quality Control** - Flags problematic submissions for manual review

## Configuration

### Adjusting Manual Review Threshold

In `connect_web_interface.py`:

```python
preprocessing_info = {
    'fixes_applied': fixes_applied,
    'needs_manual_review': len(fixes_applied) > 5  # Adjust threshold here
}
```

### Adding New Fixes

In `submission_preprocessor.py`, add to `_clean_code_cell()`:

```python
# Fix 6: Your new fix
if re.search(r'pattern', code):
    code = re.sub(r'pattern', r'replacement', code)
    self.fixes_applied.append("Description of fix")
```

## Testing

### Unit Tests

```bash
# Test basic preprocessing
python test_preprocessing.py

# Test integration
python test_preprocessing_integration.py
```

### Test Cases

The test suite includes:
- Commented libraries
- Pipe chain $ notation errors
- Multiple issues in one submission
- Clean submissions (no fixes needed)

## Troubleshooting

### Issue: Preprocessing not appearing in reports

**Check:**
1. Is preprocessing info being passed to `grade_submission()`?
2. Is it included in the result dict?
3. Is `_add_preprocessing_info()` being called in report generator?

### Issue: Too many false positives

**Solution:** Adjust the regex patterns in `_clean_code_cell()` to be more specific.

### Issue: Fixes not being applied

**Debug:**
```python
preprocessor = SubmissionPreprocessor()
code, markdown, fixes = preprocessor.preprocess_notebook('notebook.ipynb')
print(f"Fixes: {fixes}")
print(f"Code:\n{code}")
```

## Future Enhancements

Potential improvements:

1. **Language Detection** - Auto-detect R vs Python and apply appropriate fixes
2. **Custom Rules** - Allow instructors to define custom preprocessing rules
3. **Learning System** - Track which fixes are most common and suggest improvements
4. **Validation** - Verify fixes don't break working code

## Files Modified

- `submission_preprocessor.py` - New preprocessing module
- `connect_web_interface.py` - Integration into grading flow
- `business_analytics_grader.py` - Accept and track preprocessing info
- `report_generator.py` - Display preprocessing in reports

## Example Output

```
🔧 Preprocessing submission...
✅ Applied 3 preprocessing fixes:
   • Uncommented library(tidyverse)
   • Fixed pipe chain $ notation in count()
   • Normalized whitespace and formatting

🎓 Starting Business Analytics Grading...
📋 Preprocessing applied: 3 fixes
...
```

## Success Metrics

The preprocessing system is successful when:

1. ✅ AI parsing errors decrease
2. ✅ Grading consistency improves
3. ✅ Fewer submissions need manual review
4. ✅ Students understand what was fixed

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test cases in `test_preprocessing.py`
3. Examine preprocessing logs in grading output
