# AI Homework Grading System - Architecture & Process Documentation

## System Overview

This is a distributed AI-powered homework grading system designed for business analytics courses. It uses two Mac Studios running specialized AI models in parallel to grade student R/Python notebooks with human-like feedback.

---

## Hardware Stack

### Mac Studio 1 (GPT-OSS Server)
- **Model**: M3 Ultra with 512GB RAM
- **IP**: 10.55.0.1:5001
- **AI Model**: GPT-OSS-120B (8-bit quantized)
- **Purpose**: Feedback generation and narrative assessment
- **Specialization**: Natural language, pedagogical feedback, student communication

### Mac Studio 2 (Qwen Server)
- **Model**: M4 Max with 128GB RAM
- **IP**: 10.55.0.2:5002
- **AI Model**: Qwen3-Coder-30B (bf16)
- **Purpose**: Code analysis and technical evaluation
- **Specialization**: Code quality, syntax, logic, R/Python analysis

### Connection
- **Network**: Thunderbolt bridge (10Gbps)
- **Protocol**: HTTP REST API
- **Communication**: Parallel execution via ThreadPoolExecutor

---

## Software Stack

### Core Technologies
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.9+
- **Database**: SQLite (submissions, students, assignments, feedback)
- **AI Framework**: MLX (Apple Silicon optimized)
- **Notebook Processing**: nbformat, nbconvert
- **PDF Generation**: ReportLab
- **Monitoring**: Custom real-time dashboard

### Key Components

```
ai-homework-grader-clean/
├── app.py                          # Main Streamlit application
├── business_analytics_grader.py    # Core grading engine
├── models/
│   └── distributed_mlx_client.py   # Distributed AI client
├── connect_web_interface.py        # Grading UI and batch processing
├── prompt_manager.py               # Prompt templates and management
├── server_manager.py               # Auto-restart and health monitoring
├── notebook_validation.py          # Submission validation
├── output_verifier.py              # Output verification (anti-hallucination)
├── report_generator.py             # PDF report generation
└── monitor_app.py                  # Real-time performance monitoring
```

---

## Grading Process Flow

### 1. Submission Upload
```
Student submits .ipynb → Extract Canvas ID from filename → Store in database
```

### 2. Pre-Processing
```
Notebook Validation:
├── Check file format
├── Verify cell structure
├── Count code vs markdown cells
├── Detect execution status
└── Calculate completion percentage

Size Check:
├── < 200KB: Normal processing
├── 200-400KB: Warning, skip output comparison
└── > 400KB: Skip, mark for manual review
```

### 3. Notebook Execution (if needed)
```
NotebookExecutor:
├── Detect unexecuted cells
├── Execute in isolated environment
├── Capture outputs
├── Handle errors gracefully
└── Return executed notebook
```

### 4. Content Extraction
```
Parse Notebook:
├── Extract all code cells → student_code
├── Extract all markdown cells → student_markdown
├── Extract cell outputs → for verification
├── Load template notebook → template_code
└── Load solution notebook → solution_code
```

### 5. Parallel AI Grading

#### Thread 1: Code Analysis (Qwen)
```
Qwen Coder receives:
├── Student code
├── Template code (what they started with)
├── Solution code (correct implementation)
└── Assignment context

Analyzes:
├── Syntax correctness
├── Logic implementation
├── Code efficiency
├── R/Python best practices
├── Use of required functions (dplyr, tidyverse)
└── Technical execution

Returns:
├── Technical score (0-37.5)
├── Code quality assessment
├── Specific technical issues
└── Improvement suggestions
```

#### Thread 2: Feedback Generation (GPT-OSS)
```
GPT-OSS receives:
├── Student markdown (answers, explanations)
├── Code summary
├── Assignment context
└── Rubric elements

Analyzes:
├── Business thinking
├── Data analysis approach
├── Communication clarity
├── Conceptual understanding
└── Professional presentation

Returns:
├── Overall score (0-37.5)
├── Narrative feedback
├── Strengths identification
├── Areas for improvement
└── Pedagogical guidance
```

### 6. Score Validation & Adjustment
```
Validator checks:
├── Scores are within bounds (0-37.5)
├── Code vs template comparison (prevent over-crediting)
├── Output verification (anti-hallucination)
├── Consistency between technical and overall scores
└── Apply validation penalties if needed

Adjustments:
├── Penalize missing outputs
├── Penalize execution errors
├── Adjust for incomplete work
└── Ensure fairness
```

### 7. Results Merging
```
Combine:
├── Technical score (Qwen)
├── Overall score (GPT-OSS)
├── Validation penalties
├── Rubric breakdown
└── Comprehensive feedback

Calculate:
├── Final score = min(technical, overall) - penalties
├── Percentage = (final_score / 37.5) * 100
└── Letter grade equivalent
```

### 8. Report Generation
```
PDF Report includes:
├── Student name and ID
├── Assignment details
├── Final score and percentage
├── Instructor assessment (GPT-OSS feedback)
├── Technical evaluation (Qwen analysis)
├── Rubric breakdown by category
├── Specific strengths
├── Areas for improvement
└── Validation notes (if any)
```

---

## Prompt System Architecture

### Prompt Manager (`prompt_manager.py`)

The system uses a two-tier prompt system:

#### 1. General Prompts (Base Templates)
Located in `prompts/general/`

**code_analysis_prompt.txt**
```
Purpose: Base template for code evaluation
Contains:
- Role definition (expert R/Python instructor)
- Evaluation criteria
- Output format requirements
- Scoring guidelines
- Technical focus areas
```

**feedback_prompt.txt**
```
Purpose: Base template for narrative feedback
Contains:
- Role definition (supportive instructor)
- Pedagogical approach
- Communication style
- Feedback structure
- Student-centered language
```

#### 2. Assignment-Specific Prompts
Located in `prompts/assignments/`

**assignment_3_code_analysis.txt**
```
Purpose: Specific requirements for Assignment 3
Contains:
- Required functions (select, filter, arrange, pipe)
- Expected outputs
- Common mistakes to check
- Specific grading criteria
- dplyr/tidyverse requirements
```

**assignment_3_feedback.txt**
```
Purpose: Assignment 3 feedback guidelines
Contains:
- Key concepts to assess
- Business analytics context
- Data transformation focus
- Specific learning objectives
```

### Prompt Combination Process

```python
final_prompt = general_prompt + assignment_specific_prompt + {
    "student_code": actual_code,
    "template_code": starting_code,
    "solution_code": correct_code,
    "assignment_title": "Lesson 3: Data Transformation",
    "rubric": rubric_elements
}
```

### Prompt Variables

Dynamic variables injected at runtime:
- `{assignment_title}` - Assignment name
- `{template_code}` - What students started with
- `{student_code}` - What students submitted
- `{solution_code}` - Correct implementation
- `{student_markdown}` - Student explanations
- `{rubric_elements}` - Scoring criteria

---

## Distributed Processing

### Parallel Execution Model

```python
with ThreadPoolExecutor(max_workers=2) as executor:
    # Submit both tasks simultaneously
    qwen_future = executor.submit(generate_code_analysis, code_prompt)
    gemma_future = executor.submit(generate_feedback, feedback_prompt)
    
    # Wait for both (runs in parallel)
    qwen_result = qwen_future.result(timeout=180)
    gemma_result = gemma_future.result(timeout=200)
```

### Performance Metrics

**Sequential Processing**: ~90 seconds per submission
- Qwen: 45s
- GPT-OSS: 45s
- Total: 90s

**Parallel Processing**: ~50 seconds per submission
- Both run simultaneously
- Total: max(45s, 45s) + overhead
- **Efficiency**: 1.8x speedup

### Batch Processing

```
Batch Grading Flow:
├── Load ungraded submissions
├── For each submission:
│   ├── Grade (parallel AI)
│   ├── Wait 2 seconds (thermal management)
│   └── Every 10 submissions: 30s cooling break
├── Track performance metrics
├── Handle failures gracefully
└── Generate summary report
```

---

## Error Handling & Recovery

### Auto-Restart System

**Triggers**:
- Server returns None (connection failed)
- Server returns non-200 status
- Timeout after 180s (Qwen) or 200s (GPT-OSS)

**Process**:
```
1. Detect failure
2. Kill existing server process (SSH)
3. Restart server (SSH)
4. Wait 5 seconds for initialization
5. Verify health endpoint
6. Retry generation once
7. If still fails, mark for manual review
```

### Timeout Protection

- **Qwen**: 180 second timeout
- **GPT-OSS**: 200 second timeout
- **Output comparison**: 30 second timeout
- **Large notebooks**: Skip if > 400KB

### Validation Penalties

Applied automatically:
- Missing outputs: -5%
- Execution errors: -10%
- Incomplete work: -15%
- No code execution: -20%

---

## Monitoring & Diagnostics

### Real-Time Monitor (`monitor_app.py`)

Tracks every 3 seconds:
- CPU usage (user/system/idle)
- Memory usage (GB and %)
- GPU activity (%)
- Power consumption (watts)
- Active users
- Server status
- Tokens per second
- Active requests

### Performance Logger (`performance_logger.py`)

Logs to CSV:
- All metrics from both Mac Studios
- Timestamps
- Event markers
- Grading session data

### Analysis Tools (`analyze_performance_logs.py`)

Generates reports:
- Average/max/min metrics
- Server uptime
- Performance degradation
- Issue detection
- Thermal throttling alerts

---

## Database Schema

### Tables

**students**
```sql
- id (primary key)
- student_id (Canvas ID)
- name
- email
- created_at
```

**assignments**
```sql
- id (primary key)
- name
- description
- total_points (37.5)
- rubric (JSON)
- template_notebook (path)
- solution_notebook (path)
- created_at
```

**submissions**
```sql
- id (primary key)
- student_id (foreign key)
- assignment_id (foreign key)
- notebook_path
- submission_date
- ai_score
- human_score (for corrections)
- final_score
- feedback (JSON)
- graded_at
```

**human_feedback**
```sql
- id (primary key)
- submission_id (foreign key)
- score
- feedback_text
- instructor_notes
- created_at
```

---

## Security & Privacy

### Data Protection
- Student names anonymized in UI
- Canvas IDs hashed for display
- No data leaves local network
- All processing on-premises

### Access Control
- SSH key authentication
- Passwordless sudo for powermetrics
- Local database only
- No external API calls

---

## Performance Optimization

### Techniques Used

1. **Parallel Processing**: 1.8x speedup
2. **Output Comparison Skipping**: Saves 10-30s for large notebooks
3. **Thermal Management**: Prevents throttling
4. **Caching**: Prompt templates cached
5. **Batch Processing**: Efficient database operations
6. **8-bit Quantization**: Faster inference, lower memory

### Bottlenecks

- Large notebooks (>400KB): Timeout risk
- GPU thermal limits: Requires cooling breaks
- Network latency: Minimal (Thunderbolt bridge)
- Database writes: Negligible

---

## Future Enhancements

### Planned Features
- Multi-language support (SQL, JavaScript)
- Plagiarism detection
- Automated test case generation
- Student progress tracking
- Comparative analytics
- Export to LMS integration

### Scalability
- Add more Mac Studios for higher throughput
- Implement load balancing
- Queue system for large batches
- Distributed database (PostgreSQL)

---

## Troubleshooting Guide

### Common Issues

**Qwen crashes frequently**
- Check thermal status
- Reduce batch size
- Increase cooling breaks
- Monitor GPU temperature

**Timeouts on large notebooks**
- Automatically skipped if > 400KB
- Manual review required
- Consider splitting assignments

**Scores seem too high/low**
- Check validation penalties
- Review prompt templates
- Adjust rubric weights
- Compare with human grading

**Server won't restart**
- Check SSH connectivity
- Verify server_config.json
- Check disk space
- Review server logs

---

## Maintenance

### Daily
- Monitor server health
- Check error logs
- Verify disk space

### Weekly
- Review grading accuracy
- Update prompt templates
- Backup database
- Clean old logs

### Monthly
- Analyze performance trends
- Update AI models if needed
- Review and adjust rubrics
- System performance audit

---

## Contact & Support

For issues or questions:
1. Check logs in `performance_logs/`
2. Review error messages in terminal
3. Check monitor dashboard
4. Restart servers if needed
5. Manual review for edge cases

---

*Last Updated: October 5, 2025*
*Version: 2.0*
*System Status: Production*
