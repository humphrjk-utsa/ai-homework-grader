# Auto-Execution Feature - November 1, 2025

## Overview

The grading system now **automatically executes notebooks** that haven't been run before grading them. This ensures students get fair grades even if they forgot to run their cells.

---

## How It Works

### Step 1: Detection
```
Check notebook execution status:
- Count total code cells
- Count cells with outputs
- If < 50% cells executed → needs execution
```

### Step 2: Execution
```
If notebook needs execution:
1. Create temporary directory
2. Copy data files to temp directory
3. Inject path fixes (remove absolute paths)
4. Execute notebook with 60s timeout
5. Save executed version
6. Use executed version for grading
```

### Step 3: Grading
```
If execution successful:
- Use executed notebook
- Reduce validation penalty (50% → 10%)
- Grade with full outputs

If execution failed:
- Use original notebook
- Keep validation penalty
- Grade with partial outputs
```

---

## Benefits

### 1. Fair Grading
✅ Students who forgot to run cells still get graded on their code
✅ No harsh penalty for technical oversight
✅ Actual code quality is evaluated

### 2. Better Feedback
✅ Outputs available for comparison
✅ Can verify calculations
✅ Can check for errors

### 3. Reduced Manual Work
✅ No need to manually execute notebooks
✅ Automatic path fixing
✅ Handles data file locations

---

## Configuration

### Timeout
Default: 60 seconds

Adjust in `business_analytics_grader.py`:
```python
executor = NotebookExecutor(data_folder='data', timeout=60)
```

### Execution Threshold
Default: < 50% cells executed

Adjust in `notebook_executor.py`:
```python
needs_exec = executed_cells < (total_cells * 0.5)
```

### Validation Penalty Reduction
Default: 50% → 10% if auto-executed

Adjust in `business_analytics_grader.py`:
```python
if validation_penalty >= 50:
    validation_penalty = 10  # Adjust this value
```

---

## Path Fixing

The executor automatically fixes common path issues:

### Windows Paths
```r
# Before
read_csv("C:/Users/Student/Documents/data/file.csv")

# After (auto-fixed)
read_csv("file.csv")
```

### Mac/Linux Paths
```r
# Before
read_csv("/Users/Student/Documents/data/file.csv")

# After (auto-fixed)
read_csv("file.csv")
```

### Relative Paths
```r
# Before
read_csv("../../data/file.csv")

# After (auto-fixed)
read_csv("file.csv")
```

### setwd() Calls
```r
# Before
setwd("/Users/Student/Documents/MSBA")

# After (auto-fixed)
# setwd() commented out for grading
```

---

## Execution Flow

```
┌─────────────────────────────────────┐
│ 1. Check Notebook Execution Status │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Executed?    │
        └──┬───────┬───┘
           │       │
       Yes │       │ No
           │       │
           ▼       ▼
    ┌──────────┐  ┌─────────────────┐
    │ Use      │  │ 2. Execute      │
    │ Original │  │    Notebook     │
    └────┬─────┘  └────────┬────────┘
         │                 │
         │                 ▼
         │          ┌──────────────┐
         │          │ Success?     │
         │          └──┬───────┬───┘
         │             │       │
         │         Yes │       │ No
         │             │       │
         │             ▼       ▼
         │      ┌──────────┐  ┌──────────┐
         │      │ Use      │  │ Use      │
         │      │ Executed │  │ Original │
         │      └────┬─────┘  └────┬─────┘
         │           │             │
         └───────────┴─────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ 3. Grade        │
            │    Notebook     │
            └─────────────────┘
```

---

## Logging

### Execution Detected
```
🔍 Checking if notebook has been executed...
⚡ Notebook not fully executed (5/20 cells)
🚀 Attempting to execute notebook before grading...
```

### Execution Success
```
✅ Notebook executed successfully!
📝 Using executed notebook for grading
📉 Reducing validation penalty from 50% to 10% (auto-executed)
```

### Execution Failure
```
⚠️ Execution failed: Timeout (60s exceeded)
📝 Using original notebook (may have incomplete outputs)
```

### Already Executed
```
✅ Notebook already executed (18/20 cells)
```

---

## Error Handling

### Timeout
```
If execution takes > 60 seconds:
- Stop execution
- Use original notebook
- Log timeout error
- Continue with grading
```

### Execution Error
```
If code has errors:
- Capture error message
- Use original notebook
- Include error in feedback
- Continue with grading
```

### Missing Data Files
```
If data files not found:
- Log warning
- Attempt execution anyway
- May fail if files needed
- Use original notebook
```

---

## Examples

### Example 1: Unexecuted Notebook

**Input:**
- Notebook: 20 code cells
- Executed: 0 cells
- Validation penalty: 50%

**Process:**
```
🔍 Checking if notebook has been executed...
⚡ Notebook not fully executed (0/20 cells)
🚀 Attempting to execute notebook before grading...
✅ Notebook executed successfully!
📝 Using executed notebook for grading
📉 Reducing validation penalty from 50% to 10%
```

**Result:**
- Uses executed notebook
- Penalty reduced to 10%
- Full outputs available

### Example 2: Partially Executed

**Input:**
- Notebook: 20 code cells
- Executed: 8 cells (40%)
- Validation penalty: 25%

**Process:**
```
🔍 Checking if notebook has been executed...
⚡ Notebook not fully executed (8/20 cells)
🚀 Attempting to execute notebook before grading...
✅ Notebook executed successfully!
📝 Using executed notebook for grading
```

**Result:**
- Uses executed notebook
- Penalty stays at 25% (not reduced, wasn't 50%)
- Full outputs available

### Example 3: Already Executed

**Input:**
- Notebook: 20 code cells
- Executed: 18 cells (90%)
- Validation penalty: 0%

**Process:**
```
🔍 Checking if notebook has been executed...
✅ Notebook already executed (18/20 cells)
```

**Result:**
- Uses original notebook
- No execution needed
- Proceeds to grading

### Example 4: Execution Fails

**Input:**
- Notebook: 20 code cells
- Executed: 0 cells
- Code has syntax errors

**Process:**
```
🔍 Checking if notebook has been executed...
⚡ Notebook not fully executed (0/20 cells)
🚀 Attempting to execute notebook before grading...
⚠️ Execution failed: SyntaxError in cell 5
📝 Using original notebook (may have incomplete outputs)
```

**Result:**
- Uses original notebook
- Penalty stays at 50%
- Grading proceeds with errors noted

---

## Testing

### Test Execution
```bash
# Test the executor directly
python notebook_executor.py

# Or test via grading
# Upload an unexecuted notebook and watch logs
```

### Check Logs
```bash
# Watch for execution messages
tail -f logs/training_interface_*.log | grep "Checking if notebook"
```

---

## Limitations

### 1. Timeout
- Maximum 60 seconds execution time
- Long-running code may timeout
- Adjust timeout if needed

### 2. Dependencies
- Requires jupyter nbconvert
- Requires R kernel (ir)
- May fail if packages missing

### 3. Data Files
- Assumes data files in 'data' folder
- May fail if files elsewhere
- Path fixing has limits

### 4. Complex Code
- May fail on complex setups
- May fail on external dependencies
- May fail on system-specific code

---

## Summary

### Before
```
Student forgets to run notebook
→ 50% validation penalty
→ No outputs to grade
→ Low score
```

### After
```
Student forgets to run notebook
→ System detects and executes
→ Penalty reduced to 10%
→ Full outputs available
→ Fair grade based on code quality
```

**Result:** More fair grading that focuses on code quality, not technical oversights.
