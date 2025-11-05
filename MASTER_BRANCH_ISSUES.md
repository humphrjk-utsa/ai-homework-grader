# Master Branch Issues - Nov 2, 2024

## Issue 1: CSV Export Error
**Location**: Grade & Review page → Export to CSV button
**Status**: Need error message details
**Possible cause**: Same row_factory issue as bulk PDF (fixed in Test branch but not merged to master yet)

**Fix**: Apply the same row_factory fix from Test branch:
```python
conn = sqlite3.connect(self.grader.db_path)
conn.row_factory = sqlite3.Row  # Add this line
```

## Issue 2: Missing Performance Metrics
**Location**: Grading page - tokens/sec not showing
**Status**: Investigating
**Expected**: Should show:
- Qwen tokens/sec
- GPT-OSS tokens/sec  
- Combined throughput
- Parallel efficiency

**Possible causes**:
1. Distributed MLX client not returning performance_diagnostics
2. Performance metrics not being captured in grading result
3. UI not displaying the metrics even though they're captured

**Check**:
- Is `use_distributed_mlx` True?
- Is `distributed_client.get_performance_diagnostics()` being called?
- Are metrics in the grading result JSON?

## Files to Check
- `training_interface.py` - CSV export function
- `business_analytics_grader.py` - Performance metrics capture
- `connect_web_interface.py` - Performance metrics display
- `models/distributed_mlx_client.py` - get_performance_diagnostics()

## Next Steps
1. Get exact CSV error message
2. Check if performance_diagnostics is in grading results
3. Apply fixes from Test branch to master
4. Test both issues
