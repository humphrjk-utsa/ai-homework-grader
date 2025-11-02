# Hybrid Grading Pipeline Guide

## Overview

The hybrid pipeline combines three approaches for comprehensive grading:

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: SYSTEMATIC VALIDATOR (Deterministic Python)       │
│  ✅ Check variables exist (regex)                          │
│  ✅ Verify functions used (string search)                  │
│  ✅ Count outputs (JSON parsing)                           │
│  ✅ Calculate objective scores (math)                      │
│  → Result: 91/100, Grade A, detailed breakdown             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: QWEN CODER (AI Code Evaluation)                   │
│  ✅ Analyze code quality and style                         │
│  ✅ Identify specific issues                               │
│  ✅ Generate fix recommendations with code examples        │
│  ✅ Suggest alternative approaches                         │
│  → Result: Detailed technical feedback                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: GPT-OSS-120B (AI Narrative Feedback)              │
│  ✅ Generate personalized, encouraging feedback            │
│  ✅ Celebrate strengths                                    │
│  ✅ Explain areas for improvement                          │
│  ✅ Provide actionable recommendations                     │
│  → Result: Warm, educational narrative                     │
└─────────────────────────────────────────────────────────────┘
```

## Why This Approach?

### Systematic Validator (Python)
- **Purpose:** Objective, consistent scoring
- **Strengths:** Fast, accurate, transparent, reproducible
- **Use for:** Pass/fail checks, variable existence, execution verification

### Qwen Coder
- **Purpose:** Technical code evaluation
- **Strengths:** Understands R/dplyr syntax, can suggest fixes
- **Use for:** Code quality, bug identification, fix recommendations

### GPT-OSS-120B
- **Purpose:** Educational feedback
- **Strengths:** Natural language, encouraging tone, pedagogical
- **Use for:** Narrative feedback, learning guidance, motivation

## Setup

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Start Your Ollama Models

```bash
# Terminal 1: Start Qwen Coder
ollama run qwen2.5-coder:latest

# Terminal 2: Start GPT-OSS-120B
ollama run gpt-oss-120b:latest
```

### 3. Verify Endpoints

```bash
# Test Qwen
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:latest",
  "prompt": "Hello",
  "stream": false
}'

# Test GPT-OSS
curl http://localhost:11434/api/generate -d '{
  "model": "gpt-oss-120b:latest",
  "prompt": "Hello",
  "stream": false
}'
```

## Usage

### Grade a Single Submission

```bash
python3 validators/hybrid_grading_pipeline.py \
  --file submissions/12/Emerickkathrynj_emerickkathrynj.ipynb \
  --output grading_results_hybrid
```

### Grade with Custom Endpoints

```bash
python3 validators/hybrid_grading_pipeline.py \
  --file submissions/12/student.ipynb \
  --qwen-endpoint http://localhost:11434/api/generate \
  --gpt-endpoint http://localhost:11434/api/generate
```

### Batch Grading Script

Create `batch_grade_hybrid.py`:

```python
from pathlib import Path
from validators.hybrid_grading_pipeline import grade_with_hybrid_pipeline

submissions_dir = Path("submissions/12")
output_dir = "grading_results_hybrid"

for notebook in submissions_dir.glob("*.ipynb"):
    print(f"\n{'='*80}")
    print(f"Grading: {notebook.name}")
    print(f"{'='*80}")
    
    try:
        result = grade_with_hybrid_pipeline(
            notebook_path=str(notebook),
            output_dir=output_dir
        )
        print(f"✅ {notebook.stem}: {result['grade']} ({result['objective_score']:.1f}%)")
    except Exception as e:
        print(f"❌ Error: {e}")
```

## Output Files

For each student, you get:

### 1. JSON Result (`student_result.json`)
```json
{
  "objective_score": 91.0,
  "grade": "A",
  "validation_details": {
    "components": {...},
    "variable_check": {...},
    "section_breakdown": {...}
  },
  "code_evaluation": {
    "raw_response": "...",
    "recommendations": [...]
  },
  "narrative_feedback": {
    "raw_response": "...",
    "sections": {...}
  }
}
```

### 2. Comprehensive Report (`student_comprehensive_report.txt`)
```
================================================================================
COMPREHENSIVE GRADING REPORT
================================================================================

FINAL GRADE: A (91.0/100)

================================================================================
OBJECTIVE SCORING (Systematic Validator)
================================================================================

TECHNICAL EXECUTION: 32.0/40
JOIN OPERATIONS: 40.0/40
DATA UNDERSTANDING: 9.0/10
ANALYSIS INSIGHTS: 10.0/10

Variables Found: 25/25
Sections Complete: 21/21
Execution Rate: 87.1%

================================================================================
CODE EVALUATION (Qwen Coder)
================================================================================

## Code Quality Assessment
Your code demonstrates strong understanding of dplyr joins...

## Issues and Fixes
### Issue 1: Unexecuted Cells
**Problem:** 4 cells were not executed before submission
**Impact:** Cannot verify these sections work correctly
**Fix:**
```r
# Run all cells before submission
# In RStudio: Ctrl+Alt+R or Run > Run All
```

## Recommendations
- Consider using more descriptive variable names
- Add comments explaining complex join logic
- Use consistent pipe operator style

## Alternative Approaches
Instead of multiple separate joins, you could chain them:
```r
complete_data <- orders %>%
  inner_join(order_items, by = "OrderID") %>%
  inner_join(customers, by = "CustomerID") %>%
  inner_join(products, by = "ProductID") %>%
  inner_join(suppliers, by = "Supplier_ID")
```

================================================================================
INSTRUCTOR FEEDBACK (GPT-OSS-120B)
================================================================================

## Overall Assessment
Excellent work on this assignment! You've demonstrated strong mastery of join
operations and created comprehensive business analyses. Your score of 91% 
reflects high-quality work with just minor areas for improvement.

## Strengths
- All 25 required variables created correctly
- Perfect execution of all 6 join types
- Comprehensive business analysis with specific metrics
- Clear, well-organized code structure
- Thoughtful insights in your summary section

## Areas for Growth
- Remember to execute all code cells before submission (4 cells were unexecuted)
- Consider adding more comments to explain your analytical choices
- Your summary could include more specific numeric examples

## Recommendations
1. Before submitting, use "Run All" to ensure every cell executes
2. Add comments explaining why you chose specific join types
3. In future assignments, include more data visualizations
4. Practice chaining multiple operations with pipes for cleaner code

## Encouragement
You're doing excellent work! Your understanding of joins is solid, and your
business analysis shows real analytical thinking. Keep up the great work, and
remember that small details like running all cells can make the difference
between an A and an A+. You're on the right track!
```

## Example Output

```bash
$ python3 validators/hybrid_grading_pipeline.py \
    --file submissions/12/Emerickkathrynj_emerickkathrynj.ipynb

================================================================================
HYBRID GRADING PIPELINE
================================================================================
Notebook: submissions/12/Emerickkathrynj_emerickkathrynj.ipynb

Step 1/3: Running systematic validation...
  ✅ Objective Score: 91.0/100
  ✅ Variables Found: 25/25
  ✅ Sections Complete: 21/21

Step 2/3: Running Qwen code evaluation...
  ✅ Code quality assessed
  ✅ Fix recommendations generated

Step 3/3: Generating narrative feedback with GPT-OSS...
  ✅ Personalized feedback generated

================================================================================
FINAL GRADE: A (91.0%)
================================================================================

✅ Comprehensive report saved to: grading_results_hybrid/Emerickkathrynj_comprehensive_report.txt
✅ JSON result saved to: grading_results_hybrid/Emerickkathrynj_result.json

================================================================================
GRADING COMPLETE
================================================================================
Final Grade: A (91.0%)
```

## Customization

### Adjust Temperature

```python
pipeline = HybridGradingPipeline()

# For more conservative code evaluation
code_eval = pipeline._qwen_evaluate_code(
    notebook_path,
    validation_result,
    temperature=0.1  # More deterministic
)

# For more creative feedback
feedback = pipeline._gpt_generate_feedback(
    notebook_path,
    validation_result,
    code_evaluation,
    temperature=0.9  # More creative
)
```

### Custom Prompts

Edit the `_build_qwen_prompt()` and `_build_gpt_prompt()` methods to customize what each model focuses on.

### Add More Models

```python
class ExtendedPipeline(HybridGradingPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_checker_endpoint = "http://localhost:11434/api/generate"
        self.style_checker_model = "codellama:latest"
    
    def check_code_style(self, code):
        # Add another model for style checking
        pass
```

## Performance

### Timing (Approximate)

- Systematic Validator: ~0.5 seconds
- Qwen Code Evaluation: ~10-30 seconds (depends on code length)
- GPT-OSS Feedback: ~10-30 seconds
- **Total: ~20-60 seconds per submission**

### Optimization Tips

1. **Batch Processing:** Grade multiple students in parallel
2. **Cache Results:** Save validation results to avoid re-running
3. **Limit Code Length:** Send only relevant code sections to LLMs
4. **Use Streaming:** Stream LLM responses for faster perceived performance

## Troubleshooting

### Issue: LLM Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Issue: Timeout Errors

Increase timeout in `_call_llm()`:

```python
response = requests.post(
    endpoint,
    json={...},
    timeout=300  # Increase from 120 to 300 seconds
)
```

### Issue: Poor Quality Feedback

Adjust prompts in `_build_qwen_prompt()` and `_build_gpt_prompt()` to be more specific about what you want.

## Best Practices

1. **Always run systematic validator first** - Get objective scores before AI evaluation
2. **Use Qwen for technical details** - Code fixes, syntax issues, best practices
3. **Use GPT-OSS for pedagogy** - Learning guidance, encouragement, big-picture feedback
4. **Review AI output** - LLMs can hallucinate; verify recommendations are accurate
5. **Iterate on prompts** - Refine prompts based on output quality

## Integration with Existing System

```python
# In your existing grading script
from validators.hybrid_grading_pipeline import HybridGradingPipeline

pipeline = HybridGradingPipeline()

for submission in submissions:
    # Get comprehensive results
    result = pipeline.grade_submission(submission)
    
    # Use objective score for gradebook
    gradebook.record_score(
        student=submission.student,
        score=result['objective_score'],
        grade=result['grade']
    )
    
    # Send feedback to student
    send_feedback(
        student=submission.student,
        feedback=result['narrative_feedback']['raw_response']
    )
    
    # Save detailed report for instructor
    save_report(
        student=submission.student,
        report=result
    )
```

## Conclusion

This hybrid approach gives you:
- ✅ **Objective, consistent scoring** (Systematic Validator)
- ✅ **Technical code evaluation** (Qwen Coder)
- ✅ **Personalized, educational feedback** (GPT-OSS-120B)

Best of all three worlds! 🎉
