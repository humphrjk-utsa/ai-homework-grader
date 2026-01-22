# Active Files in Test-DGX Branch

## Core Application Files (ACTIVELY USED)

### Main Entry Point
- **`app.py`** - Main Streamlit application entry point
  - Imports all UI modules
  - Manages navigation and session state
  - Initializes database and directories

### Primary Grading Engine
- **`business_analytics_grader_v2.py`** - Enhanced 4-layer grading system
  - Layer 1: Systematic validation (variables, sections, execution)
  - Layer 2: Smart output validation (compare with solution)
  - Layer 3: AI code analysis (Qwen 3.0 Coder)
  - Layer 4: AI feedback generation (GPT-OSS 120B)
  - Supports disaggregated inference (DGX + Mac)
  - Parallel processing with ThreadPoolExecutor

### Web Interface Connectors
- **`connect_web_interface.py`** - Connects UI to grading engine
  - `grade_submissions_page()` - Main grading interface
  - `grade_single_submission()` - Individual grading
  - `grade_batch_submissions()` - Batch processing
  - Handles notebook execution and preprocessing

### UI Components
- **`assignment_manager.py`** - Assignment creation and upload
- **`assignment_editor.py`** - Assignment management interface
- **`grading_interface.py`** - Results viewing interface
- **`enhanced_training_page.py`** - Training data review
- **`training_interface.py`** - AI training interface
- **`prompt_manager.py`** - Prompt template management
- **`model_status_display.py`** - Two-model system status display

### Validation System (4-Layer)
- **`validators/rubric_driven_validator.py`** - Layer 1: Systematic validation
  - Checks variables, sections, execution
  - Rubric-driven scoring
- **`validators/smart_output_validator.py`** - Layer 2: Output comparison
  - Cell-by-cell output matching
  - Accuracy scoring
- **`grading_validator.py`** - Score validation and fixing
- **`output_comparator.py`** - Output comparison engine
- **`reflection_extractor.py`** - Extract reflection sections
- **`reflection_grader.py`** - AI-powered reflection grading

### Notebook Processing
- **`notebook_executor.py`** - Execute notebooks if needed
- **`submission_preprocessor.py`** - Preprocess submissions
- **`notebook_validation.py`** - Notebook structure validation

### Report Generation
- **`report_generator.py`** - PDF report generation

### Utilities
- **`anonymization_utils.py`** - Student name anonymization
- **`ai_grader.py`** - AI feedback filtering
- **`score_validator.py`** - Score validation utilities

## DGX-Specific Files (ACTIVELY USED)

### Disaggregated Inference System
- **`disaggregated_client.py`** - Client for DGX prefill + Mac decode
  - Manages KV cache passing
  - Coordinates DGX Spark 1/2 with Mac Studio 1/2
  - Performance metrics tracking

### Configuration
- **`disaggregated_inference/config_current.json`** - Active DGX configuration
  - DGX Spark 1 (169.254.150.103) - Qwen prefill
  - DGX Spark 2 (169.254.150.104) - GPT-OSS prefill
  - Mac Studio 1 (localhost) - GPT-OSS decode
  - Mac Studio 2 (169.254.150.102) - Qwen decode

### Ollama Configuration
- **`ollama_servers.json`** - Ollama server endpoints
  - Maps model names to server URLs
  - Used for disaggregated routing

## Model Interface
- **`unified_model_interface.py`** - Unified MLX/Ollama interface
  - Backend detection (MLX vs Ollama)
  - Model selection UI
  - Status monitoring

## Database
- **`grading_database.db`** - SQLite database
  - Assignments table
  - Students table
  - Submissions table
  - AI training data table

## Configuration Files
- **`requirements.txt`** - Python dependencies
- **`model_config.py`** - Model configuration
- **`server_config.json`** - Server configuration

## Data Directories (ACTIVELY USED)

### Assignments
- **`assignments/`** - Assignment templates and solutions
  - `*_template.ipynb` - Student templates
  - `*_solution.ipynb` - Solution notebooks

### Rubrics
- **`rubrics/`** - Grading rubrics (JSON format)
  - `*_rubric.json` - Assignment rubrics
  - Contains autograder_checks for validation

### Submissions
- **`submissions/`** - Student submissions
  - Organized by assignment ID
  - Contains uploaded notebooks

### Prompts
- **`prompt_templates/`** - AI prompt templates
  - `ollama/code_analysis_prompt.txt`
  - `ollama/feedback_prompt.txt`
- **`assignment_prompts/`** - Assignment-specific prompts

### Reports
- **`reports/`** - Generated PDF reports

## Test Files (ACTIVELY USED FOR DEBUGGING)
- **`test_dgx_connection.py`** - Test DGX connectivity
- **`test_dgx_grading.py`** - Test DGX grading pipeline
- **`test_disaggregated_client.py`** - Test disaggregated system
- **`test_disaggregated_setup.py`** - Test setup validation
- **`test_grader_disaggregated.py`** - Test grader with DGX
- **`test_batch_grading.py`** - Test batch processing

## Documentation Files (REFERENCE)
- **`DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md`** - System architecture
- **`DISAGGREGATED_STATUS.md`** - Current status
- **`DGX_QWEN_SETUP_PLAN.md`** - Setup instructions
- **`GRADER_V2_READY.md`** - V2 grader documentation
- **`FINAL_STATUS.md`** - Production readiness

## INACTIVE/ARCHIVED Files (NOT USED)

### Old Graders
- `business_analytics_grader.py` - Legacy grader (replaced by v2)
- `business_analytics_grader_old.py` - Archived
- `business_analytics_grader_v2_broken.py` - Broken version
- `business_analytics_grader_v2_master.py` - Backup

### Deprecated Systems
- `distributed_config.json.mlx_not_used` - MLX distributed (disabled)
- `servers/` - Old server scripts (replaced by disaggregated_client)
- `setup/` - Old setup scripts

### Old Documentation
- Various `*_COMPLETE.md` files - Historical records

## File Import Chain

```
app.py
├── assignment_manager.py
├── assignment_editor.py
├── training_interface.py
├── enhanced_training_page.py
├── connect_web_interface.py
│   ├── business_analytics_grader_v2.py
│   │   ├── prompt_manager.py
│   │   ├── notebook_validation.py
│   │   ├── score_validator.py
│   │   ├── output_comparator.py
│   │   ├── validators/rubric_driven_validator.py
│   │   ├── validators/smart_output_validator.py
│   │   ├── reflection_extractor.py
│   │   ├── reflection_grader.py
│   │   └── disaggregated_client.py (if DGX enabled)
│   ├── grading_validator.py
│   ├── report_generator.py
│   ├── ai_grader.py
│   ├── anonymization_utils.py
│   ├── notebook_executor.py
│   └── submission_preprocessor.py
├── grading_interface.py
├── prompt_manager.py
└── model_status_display.py
```

## Key Differences from Master Branch

### Test-DGX Branch Additions:
1. **Disaggregated inference system** - DGX prefill + Mac decode
2. **Enhanced 4-layer validation** - Systematic + Output + AI
3. **Reflection grading** - AI-powered reflection assessment
4. **Output comparison** - Cell-by-cell accuracy checking
5. **Midterm exam support** - Comprehensive exam grading
6. **Performance metrics** - Detailed throughput tracking

### Master Branch (Simpler):
- Basic 2-model system (Qwen + Gemma)
- Simple validation
- No DGX support
- No reflection grading
- No output comparison

## How to Verify Active Files

Run the app and check imports:
```bash
cd ai-homework-grader
python -c "import app; print('App loads successfully')"
```

Check for import errors:
```bash
python app.py 2>&1 | grep -i "import\|error"
```

List actually imported modules at runtime:
```python
import sys
import app
print("Loaded modules:", [m for m in sys.modules.keys() if 'grader' in m or 'validator' in m])
```
