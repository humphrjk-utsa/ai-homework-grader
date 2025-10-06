# Automatic Notebook Execution Feature

## Overview
The system now automatically detects if students have run their notebook cells and executes them if needed. This ensures accurate grading based on actual code execution results.

## How It Works

### 1. Detection
- Checks if cells have `execution_count` and `outputs`
- If less than 50% of cells have been executed → triggers automatic execution
- Logs: `{executed_cells}/{total_cells} cells executed`

### 2. Path Injection
Before execution, the system:
- Injects a setup cell that sets the working directory
- Comments out student's `setwd()` calls
- Replaces absolute paths with relative paths:
  - `~/Documents/data/file.csv` → `file.csv`
  - `C:/Users/Student/data/file.csv` → `file.csv`
  - `/Users/Student/Documents/file.csv` → `file.csv`

### 3. Data Folder Setup
- Copies all files from `data/` folder to temporary directory
- Sets working directory to temp folder
- Notebook runs in isolated environment

### 4. Execution
- Uses `jupyter nbconvert --execute`
- 30-second timeout (configurable)
- Captures all outputs
- Falls back to original notebook if execution fails

### 5. Grading
- Uses executed notebook (with outputs) for grading
- AI sees both code AND actual results
- More accurate assessment

## Configuration

```python
executor = NotebookExecutor(
    data_folder='data',  # Folder with assignment data files
    timeout=30           # Maximum execution time in seconds
)
```

## Usage

### Automatic (in grading workflow)
```python
# Already integrated in connect_web_interface.py
# Happens automatically during grading
```

### Manual
```python
from notebook_executor import NotebookExecutor

executor = NotebookExecutor(data_folder='data', timeout=30)
notebook_to_use, exec_info = executor.execute_if_needed('student_notebook.ipynb')

print(f"Needed execution: {exec_info['needed_execution']}")
print(f"Success: {exec_info['execution_success']}")
print(f"Use this notebook: {notebook_to_use}")
```

## Execution Info

The `exec_info` dictionary contains:
```python
{
    'needed_execution': bool,        # Did notebook need execution?
    'total_cells': int,              # Total code cells
    'executed_cells': int,           # Cells already executed by student
    'execution_attempted': bool,     # Did we try to execute?
    'execution_success': bool,       # Did execution succeed?
    'executed_notebook_path': str,   # Path to executed notebook
    'error_message': str             # Error if execution failed
}
```

## Benefits

1. **Accurate Grading**: AI sees actual outputs, not just code
2. **Catches Errors**: Detects runtime errors students missed
3. **Fair Assessment**: Students who didn't run cells aren't penalized
4. **Path Handling**: Automatically fixes path issues
5. **Safe Execution**: Timeout prevents infinite loops

## Safety Features

- **Timeout**: 30-second limit prevents long-running code
- **Isolation**: Runs in temporary directory
- **Fallback**: Uses original notebook if execution fails
- **Cleanup**: Automatically removes temporary files
- **Error Handling**: Graceful failure with error messages

## Data Folder Structure

```
data/
├── sales_data.csv
├── customer_feedback.xlsx
└── other_data_files...
```

All files in `data/` are copied to the execution environment.

## Example Output

```
Notebook analysis: 5/15 cells executed
Notebook needs execution (5/15 cells run)
Created temp directory: /tmp/notebook_exec_xyz
Copied data file: sales_data.csv
Copied data file: customer_feedback.xlsx
Created modified notebook with injected paths
Executing notebook with 30s timeout...
✅ Notebook executed successfully
Using executed notebook: student_notebook_executed.ipynb
```

## Troubleshooting

### Execution Fails
- Check if R kernel is installed: `jupyter kernelspec list`
- Verify data files exist in `data/` folder
- Check timeout (increase if needed)
- Review error message in `exec_info['error_message']`

### Path Issues
- Ensure data files are in `data/` folder
- Check that paths in notebook are relative or will be caught by regex
- Add custom path patterns to `inject_paths()` if needed

### Timeout
- Increase timeout for complex notebooks:
  ```python
  executor = NotebookExecutor(timeout=60)  # 60 seconds
  ```

## Future Enhancements

- [ ] Support for Python notebooks (currently R-focused)
- [ ] Configurable path replacement patterns
- [ ] Parallel execution for batch grading
- [ ] Caching of executed notebooks
- [ ] Resource usage monitoring
