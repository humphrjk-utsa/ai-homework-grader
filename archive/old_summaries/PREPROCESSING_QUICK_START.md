# Preprocessing System - Quick Start

## What It Does

Automatically fixes common coding issues in student submissions before AI grading.

## Common Fixes

| Issue | Before | After |
|-------|--------|-------|
| Commented libraries | `# library(tidyverse)` | `library(tidyverse)` |
| Pipe syntax errors | `data %>% count(data$col)` | `data %>% count(col)` |
| Excessive whitespace | Multiple blank lines | Normalized spacing |
| Smart quotes | `"text"` | `"text"` |

## How to Use

### Automatic (Default)

Preprocessing happens automatically when you grade submissions through the web interface. Nothing to do!

### Manual Testing

Test preprocessing on a specific notebook:

```bash
python submission_preprocessor.py path/to/notebook.ipynb
```

Example output:
```
📋 Preprocessing Summary:
Preprocessing applied:
  • Uncommented library(tidyverse)
  • Fixed pipe chain $ notation in count()

📊 Stats:
  Code length: 9719 chars
  Fixes applied: 2
```

## Where to See Results

### 1. Console Output (during grading)
```
🔧 Preprocessing submission...
✅ Applied 3 preprocessing fixes:
   • Uncommented library(tidyverse)
   • Fixed pipe chain $ notation in count()
   • Normalized whitespace and formatting
```

### 2. PDF Reports (for students)

A "Submission Preprocessing" section appears when fixes were applied:

```
Submission Preprocessing
Your submission was automatically normalized before grading 
to fix 3 common issue(s).

Fixes Applied:
• Uncommented library(tidyverse)
• Fixed pipe chain $ notation in count()
• Normalized whitespace and formatting
```

### 3. Grading Database

Preprocessing info is stored in the `ai_feedback` JSON:

```json
{
  "final_score": 32.5,
  "preprocessing": {
    "fixes_applied": ["Uncommented library(tidyverse)", ...],
    "needs_manual_review": false
  }
}
```

## Manual Review Flag

If **more than 5 fixes** are needed, the submission is flagged for manual review:

```
⚠️ Note: Multiple preprocessing fixes were needed. 
Your instructor may review this submission manually.
```

## Configuration

### Change Manual Review Threshold

Edit `connect_web_interface.py`:

```python
preprocessing_info = {
    'fixes_applied': fixes_applied,
    'needs_manual_review': len(fixes_applied) > 5  # Change this number
}
```

### Add Custom Fixes

Edit `submission_preprocessor.py` in the `_clean_code_cell()` method:

```python
# Your custom fix
if re.search(r'your_pattern', code):
    code = re.sub(r'your_pattern', r'replacement', code)
    self.fixes_applied.append("Description of your fix")
```

## Troubleshooting

### Preprocessing not showing in reports?

1. Check console output - are fixes being applied?
2. Verify `preprocessing_info` is passed to `grade_submission()`
3. Check PDF report has preprocessing section

### Too many false positives?

Adjust the regex patterns in `submission_preprocessor.py` to be more specific.

### Need to disable preprocessing?

Comment out the preprocessing section in `connect_web_interface.py`:

```python
# preprocessor = SubmissionPreprocessor()
# student_code, student_markdown, fixes_applied = preprocessor.preprocess_notebook(notebook_path)

# Use original extraction instead
with open(notebook_to_use, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)
    # ... original code extraction
```

## Benefits

✅ **Improved AI parsing** - Fewer "Unable to parse" errors
✅ **Consistent grading** - All submissions normalized
✅ **Transparency** - Students see what was fixed
✅ **Quality control** - Flags problematic submissions

## Files

- `submission_preprocessor.py` - Main preprocessing logic
- `connect_web_interface.py` - Integration point
- `business_analytics_grader.py` - Receives preprocessing info
- `report_generator.py` - Displays in reports

## Full Documentation

See `PREPROCESSING_SYSTEM.md` for complete documentation.

## Support

Questions? Check:
1. Console output during grading
2. `PREPROCESSING_SYSTEM.md` troubleshooting section
3. Test with: `python submission_preprocessor.py notebook.ipynb`
