# AI Homework Grader - Architecture & LLM Orchestration Analysis

## Executive Summary

Your AI homework grader uses a sophisticated **4-layer validation system** with **parallel two-model LLM orchestration** to grade student assignments. The system combines rule-based validation with AI analysis for comprehensive, accurate grading.

---

## Active Files & Components

### Core Application Files (ACTIVE)

1. **`app.py`** - Main Streamlit application entry point
   - Handles UI navigation and page routing
   - Initializes database and directory structure
   - Manages session state

2. **`connect_web_interface.py`** - Grading interface orchestrator
   - Connects UI to grading engine
   - Handles batch and individual grading workflows
   - Manages submission preprocessing and execution

3. **`business_analytics_grader_v2.py`** - Enhanced grading engine (PRIMARY)
   - Implements 4-layer validation system
   - Orchestrates parallel LLM calls
   - Merges validation + AI feedback

4. **`ai_grader.py`** - Legacy AI grader (FALLBACK)
   - Provides backward compatibility
   - Contains LocalAIClient for Ollama
   - Handles basic AI grading when V2 unavailable

5. **`unified_model_interface.py`** - Model abstraction layer
   - Unified interface for MLX and Ollama backends
   - Auto-detects available AI backends
   - Handles model selection and warm-up

---

## LLM Orchestration Architecture

### Two-Model System

Your system uses **TWO specialized LLMs working in parallel**:

```
┌─────────────────────────────────────────────────────────┐
│                  GRADING ORCHESTRATOR                   │
│           (business_analytics_grader_v2.py)             │
└─────────────────────────────────────────────────────────┘
                          │
                          ├─────────────────┬─────────────────┐
                          ▼                 ▼                 ▼
                   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                   │   LAYER 1    │  │   LAYER 2    │  │  LAYER 3+4   │
                   │  Systematic  │  │    Smart     │  │  AI Analysis │
                   │  Validation  │  │   Output     │  │  (Parallel)  │
                   │              │  │  Validation  │  │              │
                   └──────────────┘  └──────────────┘  └──────────────┘
                                                              │
                                          ┌───────────────────┴───────────────────┐
                                          ▼                                       ▼
                                   ┌─────────────┐                        ┌─────────────┐
                                   │   MODEL 1   │                        │   MODEL 2   │
                                   │    QWEN     │                        │   GEMMA     │
                                   │  3.0 Coder  │                        │    3.0      │
                                   │             │                        │             │
                                   │ Technical   │                        │  Feedback   │
                                   │  Analysis   │                        │ Generation  │
                                   └─────────────┘                        └─────────────┘
                                          │                                       │
                                          └───────────────────┬───────────────────┘
                                                              ▼
                                                    ┌──────────────────┐
                                                    │  MERGE RESULTS   │
                                                    │  & STRUCTURE     │
                                                    │    FEEDBACK      │
                                                    └──────────────────┘
```

### Model Roles

**Model 1: Qwen 3.0 Coder (30B)**
- **Purpose**: Technical code analysis
- **Model**: `hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest`
- **Tasks**:
  - Analyze code quality and structure
  - Identify technical strengths
  - Suggest code improvements
  - Evaluate methodology

**Model 2: Gemma 3.0 (27B) / GPT-OSS (120B)**
- **Purpose**: Feedback generation and synthesis
- **Model**: `gemma3:27b-it-q8_0` or `gpt-oss:120b`
- **Tasks**:
  - Generate comprehensive feedback
  - Create instructor comments
  - Assess business understanding
  - Provide learning recommendations

---

## 4-Layer Validation System

### Layer 1: Systematic Validation
**File**: `validators/rubric_driven_validator.py` or `validators/assignment_6_systematic_validator.py`

**What it does**:
- Checks for required variables in student code
- Validates section completion
- Tracks code execution rate
- Calculates base score from rubric

**Output**: Base score (0-100) + completion metrics

### Layer 2: Smart Output Validation
**File**: `validators/smart_output_validator.py`

**What it does**:
- Compares student outputs with solution outputs
- Validates numerical accuracy
- Checks data structure correctness
- Applies score adjustments based on discrepancies

**Output**: Match percentage + score adjustment

### Layer 3: AI Code Analysis (Qwen)
**Executed in parallel with Layer 4**

**What it does**:
- Deep code quality analysis
- Identifies student changes vs template
- Evaluates technical approach
- Generates specific code feedback

**Output**: Technical analysis + code suggestions

### Layer 4: AI Feedback Synthesis (Gemma/GPT-OSS)
**Executed in parallel with Layer 3**

**What it does**:
- Generates comprehensive feedback
- Creates instructor comments
- Assesses conceptual understanding
- Provides learning recommendations

**Output**: Structured feedback + instructor comments

---

## Parallel Execution Flow

### Code Location
**File**: `business_analytics_grader_v2.py`
**Method**: `grade_submission()`

### Execution Pattern

```python
# 1. Run validation layers (sequential)
validation_results = self._run_4layer_validation(notebook_path)

# 2. Submit AI tasks in parallel
future_code = executor.submit(code_analysis_task)
future_feedback = executor.submit(feedback_generation_task)

# 3. Wait for both to complete
code_analysis = future_code.result()
comprehensive_feedback = future_feedback.result()

# 4. Merge all results
final_feedback = self._merge_ai_and_validation_feedback(
    validation_results, 
    code_analysis, 
    comprehensive_feedback
)
```

### Performance Benefits
- **Sequential time**: ~60-90 seconds (if run one after another)
- **Parallel time**: ~30-45 seconds (both run simultaneously)
- **Speedup**: ~2x faster

---

## Backend Options

### Option 1: Ollama (Default)
**File**: `ai_grader.py` - `LocalAIClient`

**Characteristics**:
- Cross-platform compatibility
- Easy model management
- Runs on CPU or GPU
- Models stored on external drive

**Models Used**:
- `qwen3-coder:30b` - Code analysis
- `gemma3:27b` - Feedback generation
- `gpt-oss:120b` - Alternative feedback model

### Option 2: MLX (Apple Silicon)
**File**: `models/mlx_ai_client.py`

**Characteristics**:
- Optimized for M1/M2/M3 chips
- Faster inference on Apple Silicon
- Lower memory usage
- Better battery efficiency

### Option 3: Distributed MLX (Multi-Mac)
**File**: `models/distributed_mlx_client.py`

**Characteristics**:
- Runs models on separate Mac Studios
- True parallel processing
- Network-based communication
- Highest performance option

**Configuration**: `distributed_config.json`

---

## Prompt Management

### File: `prompt_manager.py`

**Purpose**: Centralized prompt templates for consistency

**Key Features**:
- Assignment-specific prompts
- Template-based generation
- Context injection
- Validation integration

**Prompt Types**:
1. **Code Analysis Prompts** - For Qwen model
2. **Feedback Generation Prompts** - For Gemma/GPT-OSS model
3. **Combined Prompts** - Merge validation context

---

## Data Flow

### Complete Grading Pipeline

```
1. SUBMISSION RECEIVED
   ↓
2. PREPROCESSING
   - Extract notebook content
   - Execute if needed (notebook_executor.py)
   - Identify student changes (vs template)
   ↓
3. LAYER 1: SYSTEMATIC VALIDATION
   - Check variables
   - Validate sections
   - Calculate base score
   ↓
4. LAYER 2: OUTPUT VALIDATION
   - Compare with solution
   - Validate outputs
   - Adjust score
   ↓
5. LAYER 3 & 4: PARALLEL AI ANALYSIS
   ┌─────────────────┬─────────────────┐
   │  Qwen Analysis  │ Gemma Feedback  │
   │  (Technical)    │ (Comprehensive) │
   └─────────────────┴─────────────────┘
   ↓
6. MERGE RESULTS
   - Combine validation + AI feedback
   - Structure final output
   - Calculate component scores
   ↓
7. SAVE TO DATABASE
   - Store scores
   - Save feedback
   - Update submission status
   ↓
8. GENERATE REPORT (Optional)
   - PDF generation
   - Detailed breakdown
   - Student-facing format
```

---

## Key Supporting Files

### Validation System
- `validators/rubric_driven_validator.py` - Generic rubric-based validation
- `validators/assignment_6_systematic_validator.py` - Assignment-specific validation
- `validators/smart_output_validator.py` - Output comparison
- `grading_validator.py` - Score validation and fixing

### Notebook Processing
- `notebook_executor.py` - Execute student notebooks
- `notebook_validation.py` - Legacy validation
- `submission_preprocessor.py` - Clean and prepare submissions

### Feedback & Reporting
- `report_generator.py` - PDF report generation
- `anonymization_utils.py` - Student name anonymization
- `output_comparator.py` - Compare outputs with solution

### UI Components
- `assignment_manager.py` - Assignment creation
- `assignment_editor.py` - Assignment editing
- `grading_interface.py` - Results viewing
- `training_interface.py` - AI training data management

---

## Database Schema

### Tables (SQLite)

1. **assignments**
   - id, name, description, total_points
   - rubric (JSON), template_notebook, solution_notebook

2. **students**
   - id, student_id, name, email

3. **submissions**
   - id, assignment_id, student_id, notebook_path
   - ai_score, ai_feedback, human_score, human_feedback
   - final_score, graded_date

4. **ai_training_data**
   - id, assignment_id, cell_content
   - expected_output, human_score, ai_score
   - ai_feedback, human_feedback, features

---

## Performance Optimization

### Model Loading Strategy
1. **First Request**: Model loads from disk (45-60 seconds)
2. **Subsequent Requests**: Model in memory (10-20 seconds)
3. **Keep-Alive**: Prevents model unloading between requests

### Batch Processing
- Processes multiple submissions sequentially
- 2-second delay between submissions (prevent overload)
- 30-second cooling break every 10 submissions (thermal management)
- Tracks performance metrics per submission

### Parallel Processing
- Uses `ThreadPoolExecutor` with 2 workers
- Submits code analysis and feedback generation simultaneously
- Waits for both to complete before merging

---

## Configuration Files

### Active Configuration
- `distributed_config.json` - Distributed MLX setup
- `server_config.json` - Server endpoints
- `model_config.py` - Model parameters
- `grading_database.db` - SQLite database

### Rubric Files
- `rubrics/assignment_6_rubric.json` - Assignment 6 rubric
- `rubrics/*.json` - Other assignment rubrics

---

## Inactive/Archive Files

These files exist but are NOT actively used:

- `Lessons/` folder - Old grading system
- `archive/` folder - Archived code
- `benchmarks/` folder - Performance testing
- `mac_studio_deployment/` - Deployment scripts
- `alternative_approaches.py` - Experimental code
- Various `*_v1.py` files - Old versions

---

## Summary

Your system is a **production-grade AI grading platform** with:

✅ **4-layer validation** (systematic + output + 2x AI)
✅ **Parallel LLM orchestration** (2x speedup)
✅ **Multiple backend support** (Ollama, MLX, Distributed)
✅ **Comprehensive feedback** (technical + pedagogical)
✅ **Batch processing** (with thermal management)
✅ **Database persistence** (SQLite)
✅ **PDF report generation**
✅ **Training data collection** (for model improvement)

The orchestration is handled primarily by `business_analytics_grader_v2.py`, which coordinates all layers and merges results into structured feedback.
