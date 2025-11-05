# 4-Phase Grading System

## Overview
The grading system uses a 4-phase approach to ensure accurate, fair, and comprehensive evaluation of student submissions.

---

## Phase 1: Validation 🔍
**Purpose:** Structural integrity check  
**Time:** ~1-2 seconds  
**Module:** `notebook_validation.py`

### What it checks:
- ✅ Notebook format is valid JSON
- ✅ All required cells are present
- ✅ No corrupted or malformed cells
- ✅ Proper cell structure (code vs markdown)
- ✅ No excessive file size (>600KB rejected)

### Penalties applied:
- Missing cells: -10% per missing section
- Corrupted format: -20%
- Excessive size: Rejected (manual review required)

### Output:
```python
{
    'valid': True/False,
    'issues': ['list of problems'],
    'total_penalty_percent': 0-100,
    'validation_feedback': 'Human-readable summary'
}
```

---

## Phase 2: Execution ⚡
**Purpose:** Ensure code has been run and outputs exist  
**Time:** ~5-60 seconds (if execution needed)  
**Module:** `notebook_executor.py`

### What it does:
1. **Check execution status**
   - Count cells with outputs
   - Identify unexecuted cells
   
2. **Auto-execute if needed**
   - Run all code cells in order
   - Capture outputs and errors
   - Timeout after 60 seconds per cell
   
3. **Reduce penalties**
   - If auto-execution succeeds, reduce validation penalty from 50% → 10%
   - Ensures students aren't penalized for forgetting to run cells

### Output:
```python
{
    'execution_success': True/False,
    'executed_cells': 15,
    'total_cells': 15,
    'error_message': 'If failed',
    'notebook_path': 'path/to/executed/notebook.ipynb'
}
```

---

## Phase 3: Output Comparison 📊
**Purpose:** Quantitative verification of correctness  
**Time:** ~5-30 seconds  
**Module:** `output_comparator.py`

### What it compares:
- **Numerical outputs:** Check if values match (with tolerance for rounding)
- **Data frames:** Compare structure, column names, row counts
- **Text outputs:** Semantic similarity of printed results
- **Plots:** Verify plot generation (not visual comparison)

### Comparison logic:
```python
# Example comparisons:
Student: "Total customers: 94"
Solution: "Customers: 94"
→ MATCH (same value, different wording)

Student: "Average: $2,119.50"
Solution: "Average: $2,119.5"
→ MATCH (rounding difference acceptable)

Student: "50 customers"
Solution: "94 customers"
→ NO MATCH (wrong value)
```

### Output:
```python
{
    'total_cells': 15,
    'matching_cells': 12,
    'match_rate': 80.0,  # percentage
    'accuracy_score': 85.0,  # weighted by importance
    'cell_comparisons': [
        {
            'cell_id': 'task_1_1',
            'match': True,
            'student_output': '...',
            'solution_output': '...',
            'similarity': 0.95
        },
        ...
    ]
}
```

### Skipped when:
- Notebook > 200KB (prevents hangs)
- No solution notebook available
- Timeout after 30 seconds

---

## Phase 4: AI Analysis 🤖
**Purpose:** Deep semantic evaluation and feedback generation  
**Time:** ~10-30 seconds (parallel execution)  
**Modules:** `business_analytics_grader.py`, `prompt_manager.py`

### 4A: Code Analysis (Qwen 30B)
**Focus:** Technical execution and correctness

**Inputs:**
- Template code (what student received)
- Student code (what they submitted)
- Solution code (correct implementation)
- Rubric criteria
- Output comparison results (from Phase 3)
- Assignment-specific requirements

**Evaluates:**
- ✅ Code correctness and syntax
- ✅ Logic and approach
- ✅ Completion percentage
- ✅ Use of required functions
- ✅ Variable naming and structure
- ✅ Output accuracy

**Output:**
```json
{
    "technical_score": 75,
    "syntax_correctness": 85,
    "logic_correctness": 70,
    "business_relevance": 80,
    "effort_and_completion": 75,
    "code_strengths": [
        "You completed Task 1.1 correctly using str_trim()...",
        "Your date parsing in Task 4.1 works correctly..."
    ],
    "code_suggestions": [
        "Task 3.1 uses wrong pattern 'wifi' instead of 'wireless'...",
        "Task 5.1 hardcodes days_since=30 instead of calculating..."
    ],
    "technical_observations": [
        "Completion: 17 out of 25 sections (68%). Calculated score: 68%.",
        "Completed: Task 1.1, Task 1.2, Task 2.1, ...",
        "Incomplete: Task 4.3, Task 6.1, Task 7.1, ..."
    ]
}
```

### 4B: Feedback Generation (Gemma 27B)
**Focus:** Reflection questions and business understanding

**Inputs:**
- Student markdown (reflection answers)
- Code summary
- Rubric criteria
- Assignment-specific requirements

**Evaluates:**
- ✅ Reflection question depth
- ✅ Critical thinking
- ✅ Business application understanding
- ✅ Communication clarity
- ✅ Conceptual understanding

**Output:**
```json
{
    "overall_score": 70,
    "business_understanding": 75,
    "communication_clarity": 80,
    "data_interpretation": 70,
    "methodology_appropriateness": 75,
    "reflection_quality": 65,
    "detailed_feedback": {
        "reflection_assessment": [
            "Your response to Question 8.1 demonstrates...",
            "In Question 8.3, you provided only 2 applications..."
        ],
        "analytical_strengths": [...],
        "business_application": [...],
        "learning_demonstration": [...],
        "areas_for_development": [...],
        "recommendations": [...]
    },
    "instructor_comments": "Your work demonstrates..."
}
```

### Parallel Execution:
- Both models run simultaneously
- Code analysis: ~15 seconds
- Feedback generation: ~20 seconds
- Total: ~20 seconds (not 35!)
- Efficiency gain: ~1.75x

---

## Final Score Calculation

### Score Validation & Adjustment
**Module:** `score_validator.py`

1. **Apply validation penalty** (from Phase 1)
   ```python
   adjusted_score = raw_score * (1 - validation_penalty/100)
   ```

2. **Check output match rate** (from Phase 3)
   ```python
   if match_rate < 50%:
       max_score = 60  # Cap score if outputs are mostly wrong
   ```

3. **Verify completion alignment**
   ```python
   if completion_pct < 50% and score > 50:
       score = completion_pct  # Score can't exceed completion
   ```

4. **Apply rubric weights**
   ```python
   final_score = (
       technical_score * 0.40 +
       reflection_score * 0.20 +
       business_score * 0.20 +
       communication_score * 0.20
   )
   ```

5. **Bounds checking**
   ```python
   final_score = max(0, min(100, final_score))
   ```

---

## Assignment-Specific Prompts

### General Prompts (All Assignments)
- `prompt_templates/general_code_analysis_prompt.txt`
- `prompt_templates/general_feedback_prompt.txt`

### Assignment-Specific Prompts
- `assignment_prompts/a7_code_analysis_prompt.txt`
- `assignment_prompts/a7_feedback_prompt.txt`

### How they combine:
```python
final_prompt = f"""
{general_prompt}

{assignment_specific_prompt}

{correction_learning}  # From previous grading corrections

{rubric_criteria}

{student_code}
{solution_code}
"""
```

---

## Performance Metrics

### Typical Timing:
- Phase 1 (Validation): 1-2s
- Phase 2 (Execution): 5-60s (if needed)
- Phase 3 (Comparison): 5-30s
- Phase 4 (AI Analysis): 15-25s (parallel)
- **Total: 26-117 seconds per submission**

### Optimization:
- ✅ Parallel AI execution (1.75x faster)
- ✅ Skip comparison for large notebooks
- ✅ Timeout protection (prevents hangs)
- ✅ Caching of executed notebooks
- ✅ Distributed MLX for faster inference

---

## Error Handling

### Phase 1 Failures:
- Invalid JSON → Reject with error message
- Too large → Reject, require manual review
- Missing cells → Continue with penalty

### Phase 2 Failures:
- Execution timeout → Use original notebook
- Execution error → Use original notebook
- Kernel crash → Use original notebook

### Phase 3 Failures:
- Comparison timeout → Skip, continue to Phase 4
- No solution → Skip comparison
- Parse error → Skip comparison

### Phase 4 Failures:
- Model timeout → Retry once
- Invalid JSON response → Parse with fallback
- Model unavailable → Fail gracefully with error

---

## Quality Assurance

### Checks performed:
1. ✅ Score matches completion percentage
2. ✅ Feedback references actual student code
3. ✅ No contradictions between code_strengths and code_suggestions
4. ✅ Reflection scores align with answer count
5. ✅ Output comparison results inform AI scoring
6. ✅ Validation penalties are applied correctly

### Red flags:
- ⚠️ Score > 80 but completion < 50%
- ⚠️ Match rate < 30% but score > 70%
- ⚠️ 0 reflections answered but score > 20%
- ⚠️ Code has errors but score > 60%

---

## For Assignment 7 Specifically

### Phase 1: Validates structure
- 25 required sections present
- Proper cell IDs
- No corruption

### Phase 2: Executes if needed
- Runs all string manipulation code
- Runs all date parsing code
- Captures outputs

### Phase 3: Compares outputs
- Checks if 17 wireless products found
- Verifies date parsing success rate
- Compares sentiment scores
- Validates recency categories

### Phase 4: AI Analysis
- **Code Analysis:** Checks for ymd() vs as.Date(), str_trim() vs str_replace_all(), correct patterns
- **Feedback:** Evaluates 6 reflection questions, checks for 3+ applications in Q8.3

### Final Score:
```python
technical_score = (completed_sections / 25) * 100  # From Phase 4A
reflection_score = (answered_questions / 6) * 100  # From Phase 4B
match_rate_bonus = output_comparison['match_rate'] * 0.1  # From Phase 3
validation_penalty = validation_results['total_penalty_percent']  # From Phase 1

final_score = (
    (technical_score * 0.40 + 
     reflection_score * 0.20 + 
     business_score * 0.20 + 
     communication_score * 0.20) *
    (1 - validation_penalty/100)
)
```
