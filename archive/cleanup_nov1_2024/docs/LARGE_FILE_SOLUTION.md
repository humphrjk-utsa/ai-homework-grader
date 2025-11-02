# Solution for Large File Handling (500KB+)

## Problem
Files over 400KB are skipped for manual review, but output cells are critical for grading.

## Why Files Get Large

### Common Causes:
1. **Printing entire datasets** - `print(df)` on 1000+ row datasets
2. **Multiple head() calls** - Showing same data repeatedly
3. **Verbose outputs** - Long summary statistics
4. **Duplicate outputs** - Re-running cells multiple times
5. **Large plots** - Base64 encoded images in outputs

### What We Need to Keep:
- ✅ All code cells (shows student work)
- ✅ Key outputs (shows correct/incorrect answers)
- ✅ Error messages (shows what went wrong)
- ✅ Summary statistics (shows understanding)
- ✅ First/last few rows of data (shows results)

### What We Can Safely Reduce:
- ❌ Middle rows of large printouts (keep first 10, last 10)
- ❌ Duplicate outputs (keep only last execution)
- ❌ Excessive whitespace
- ❌ Base64 image data (keep plot descriptions only)

---

## Recommended Solution: Smart Output Compression

### Approach 1: Intelligent Output Limiting (Best)

**Keep grading accuracy while reducing size:**

```python
def compress_large_output(output_text: str, max_lines: int = 50) -> str:
    """
    Compress large outputs while keeping critical information
    
    Strategy:
    - Keep first 20 lines (shows column names, first rows)
    - Keep last 20 lines (shows final rows, totals)
    - Replace middle with summary
    """
    lines = output_text.split('\n')
    
    if len(lines) <= max_lines:
        return output_text
    
    # Keep beginning and end
    keep_start = 20
    keep_end = 20
    
    compressed = (
        '\n'.join(lines[:keep_start]) +
        f'\n\n... [{len(lines) - keep_start - keep_end} lines omitted for brevity] ...\n\n' +
        '\n'.join(lines[-keep_end:])
    )
    
    return compressed
```

**Benefits:**
- ✅ Keeps column names and structure
- ✅ Shows first results (correct/incorrect)
- ✅ Shows final results (totals, summaries)
- ✅ Reduces file size by 60-80%
- ✅ AI can still grade accurately

---

### Approach 2: Increase Limit + Smart Handling (Pragmatic)

**For files 400-800KB:**
- Process normally
- Use compression only if needed

**For files 800KB-1MB:**
- Apply smart output compression
- Process with extended timeout

**For files > 1MB:**
- Skip and mark for manual review
- These are likely corrupted or have embedded images

---

## Implementation Plan

### Phase 1: Quick Fix (Now)
**Increase limit to 600KB** - Handles most legitimate submissions

```python
# In business_analytics_grader.py line 193
if notebook_size_kb > 600:  # Was 400
    print(f"⚠️ SKIPPING: Notebook too large ({notebook_size_kb:.1f} KB)")
```

### Phase 2: Smart Compression (Next Week)
**Add output compression for 600KB-1MB files**

```python
def preprocess_large_notebook(notebook_path: str) -> str:
    """Preprocess large notebooks with smart output compression"""
    nb = nbformat.read(notebook_path, as_version=4)
    
    for cell in nb.cells:
        if cell.cell_type == 'code' and hasattr(cell, 'outputs'):
            for output in cell.outputs:
                if output.output_type == 'stream':
                    # Compress long outputs
                    output.text = compress_large_output(output.text)
                elif output.output_type == 'execute_result':
                    if 'text/plain' in output.data:
                        output.data['text/plain'] = compress_large_output(
                            output.data['text/plain']
                        )
    
    return nb
```

### Phase 3: Student Education (Ongoing)
**Add to assignment instructions:**

> **File Size Best Practices:**
> - Use `head()` instead of printing entire datasets
> - Avoid re-running cells multiple times
> - Use `summary()` instead of `print()` for large data
> - Clear outputs before submission if file > 500KB

---

## Testing Strategy

### Test with Real Large Files:
1. Find the 2 files that were skipped (500KB+)
2. Apply smart compression
3. Verify grading accuracy
4. Compare AI grades with/without compression

### Validation:
- ✅ AI can still identify correct answers
- ✅ AI can still provide specific feedback
- ✅ File size reduced to < 400KB
- ✅ Processing completes without timeout

---

## Expected Results

### Current State:
- Files > 400KB: Skipped (manual review)
- Success rate: ~95%
- Manual review: 2 files per batch

### After Phase 1 (600KB limit):
- Files > 600KB: Skipped
- Success rate: ~98%
- Manual review: 0-1 files per batch

### After Phase 2 (Smart compression):
- Files up to 1MB: Processed
- Success rate: ~99%
- Manual review: Rare

---

## Alternative: Pre-submission Tool

**Create a notebook cleaner for students:**

```python
# clean_notebook.py
def clean_for_submission(notebook_path: str):
    """Clean notebook before submission"""
    nb = nbformat.read(notebook_path, as_version=4)
    
    # Clear excessive outputs
    for cell in nb.cells:
        if cell.cell_type == 'code':
            # Keep only last execution
            if len(cell.outputs) > 1:
                cell.outputs = [cell.outputs[-1]]
            
            # Limit output size
            for output in cell.outputs:
                if output.output_type == 'stream':
                    lines = output.text.split('\n')
                    if len(lines) > 100:
                        output.text = compress_large_output(output.text)
    
    # Save cleaned version
    output_path = notebook_path.replace('.ipynb', '_cleaned.ipynb')
    nbformat.write(nb, output_path)
    print(f"✅ Cleaned notebook saved to: {output_path}")
```

**Benefits:**
- Students submit clean files
- No server-side processing needed
- Teaches good practices

---

## Recommendation

**Immediate:** Increase limit to 600KB (5 minute fix)

**This Week:** Implement smart output compression for 600KB-1MB files

**Long-term:** Provide pre-submission cleaning tool for students

This keeps grading accuracy while handling large files efficiently.
