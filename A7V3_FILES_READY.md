# Assignment 7 V3 Files - Ready to Use

## ✅ Files Retrieved from Master Branch

All Assignment 7 V3 files have been successfully retrieved from the master branch and are ready to use.

### Files Available

#### Assignment Files
- ✅ `assignments/a7v3_template.ipynb` (25 KB)
  - Student template with TODO sections
  - String manipulation and date/time exercises
  - Uses data from `data/` directory

- ✅ `assignments/a7v3_solution.ipynb` (77 KB)
  - Complete solution with all answers
  - Reference for grading and validation

#### Prompt Files
- ✅ `assignment_prompts/a7v3_code_analysis_prompt.txt` (6.1 KB, 108 lines)
  - Custom prompt for code analysis phase
  - Tailored for Assignment 7 V3 requirements

- ✅ `assignment_prompts/a7v3_feedback_prompt.txt` (8.2 KB, 128 lines)
  - Custom prompt for feedback generation phase
  - Personalized feedback guidelines

### Rubric

The assignment uses the existing rubric:
- 📋 `rubrics/assignment_7_rubric_v2.json`
  - Comprehensive rubric for Assignment 7
  - Includes autograder checks
  - Works with RubricDrivenValidator

### Data Files

The assignment expects data in `data/processed/`:
- `customer_feedback.csv`
- `transaction_log.csv`
- `product_catalog.csv`

These files should already be present from previous setup.

## 🎯 Using A7V3 in the Grading System

### Option 1: Via Web Interface

1. Open http://localhost:8501
2. Go to "Assignment Management"
3. Create new assignment:
   - Name: `a7v3`
   - Template: Upload `assignments/a7v3_template.ipynb`
   - Solution: Upload `assignments/a7v3_solution.ipynb`
   - Rubric: Select `assignment_7_rubric_v2.json`

### Option 2: Via Database

The assignment can be added directly to the database with:
- Template path: `assignments/a7v3_template.ipynb`
- Solution path: `assignments/a7v3_solution.ipynb`
- Rubric path: `rubrics/assignment_7_rubric_v2.json`

### Option 3: Via Prompt Manager

The custom prompts will be automatically detected by the PromptManager when:
- Assignment name matches `a7v3`
- Prompt files exist in `assignment_prompts/`

## 🔧 Integration with Disaggregated System

The a7v3 assignment will automatically use:
- **Code Analysis**: DGX Spark 1 + Mac Studio 2 (Qwen)
- **Feedback Generation**: DGX Spark 2 + Mac Studio 1 (GPT-OSS)
- **4-Layer Validation**: Systematic + Output + AI Analysis + Feedback

## 📊 Assignment Structure

### Part 1: Data Import and Exploration
- Load packages (tidyverse, lubridate)
- Import CSV files
- Examine data structure

### Part 2: String Manipulation
- Clean messy text data
- Standardize formats
- Extract information

### Part 3: Date/Time Operations
- Parse dates
- Extract temporal components
- Calculate time differences

### Part 4: Combined Analysis
- Customer segmentation
- Temporal patterns
- Business insights

### Part 5: Reflection
- Learning outcomes
- Challenges faced
- Real-world applications

## ✅ Ready to Grade

All files are in place and the system is ready to grade Assignment 7 V3 submissions!

To test:
1. Upload a student submission for a7v3
2. The system will use the custom prompts
3. Grading will use all 4 machines in parallel
4. Results will include comprehensive feedback
