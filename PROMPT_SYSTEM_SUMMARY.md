# Flexible Prompt & Rubric System

## Overview
Created a flexible, extensible system for managing prompts and rubrics that allows customization per assignment without hardcoding.

## System Components

### 1. **Prompt Templates** (`prompt_templates/`)
General prompt templates used for all assignments:
- `general_code_analysis_prompt.txt` - Template for code evaluation
- `general_feedback_prompt.txt` - Template for feedback generation

**Features:**
- Uses `{variable_name}` placeholders for dynamic content
- Can be edited through UI
- Applies to all assignments by default

### 2. **Assignment-Specific Prompts** (`assignment_prompts/`)
Optional additional instructions per assignment:
- `{assignment_name}_code_analysis_prompt.txt`
- `{assignment_name}_feedback_prompt.txt`

**Features:**
- Appended to general prompts
- Override or extend general instructions
- Created through UI per assignment

### 3. **Rubrics** (`rubrics/`)
JSON rubrics for each assignment:
- `{assignment_name}_rubric.json`

**Features:**
- AI-generated from assignment descriptions
- Structured format with components and criteria
- Includes suggested reflection questions

### 4. **Prompt Manager** (`prompt_manager.py`)
Core system for managing prompts and rubrics:

**Key Functions:**
- `load_general_prompt()` - Load template
- `save_general_prompt()` - Save template
- `load_assignment_prompt()` - Load assignment-specific instructions
- `save_assignment_prompt()` - Save assignment-specific instructions
- `get_combined_prompt()` - Combine general + assignment-specific
- `generate_rubric_with_ai()` - AI-powered rubric generation
- `save_rubric()` / `load_rubric()` - Rubric management

## UI Features

### Tab 1: General Prompts
- Edit general prompt templates
- Save changes
- Reset to defaults
- Applies to all assignments

### Tab 2: Assignment Prompts
- Select assignment
- Add assignment-specific instructions
- Preview combined prompt
- Clear instructions

### Tab 3: Rubric Generator
- Enter assignment description
- Set total points
- AI generates structured rubric
- Save rubric for assignment
- Load existing rubrics

## Integration

### Business Analytics Grader
Updated to use Prompt Manager:

```python
# Initialize
self.prompt_manager = PromptManager()

# Get combined prompts
code_prompt = self.prompt_manager.get_combined_prompt(
    assignment_name,
    "code_analysis",
    assignment_title=...,
    student_code=...,
    solution_code=...
)
```

### Main App
Added "Prompt Manager" page to navigation:
- Access from sidebar
- Manage all prompts and rubrics
- Generate new rubrics with AI

## Workflow

### Creating a New Assignment
1. **Create Assignment** - Use Assignment Management page
2. **Generate Rubric** - Use Prompt Manager → Rubric Generator tab
   - Enter assignment description
   - AI generates structured rubric
   - Save rubric
3. **Add Custom Instructions** (Optional) - Use Prompt Manager → Assignment Prompts tab
   - Select assignment
   - Add specific evaluation criteria
   - Preview combined prompt
4. **Grade Submissions** - System automatically uses:
   - General prompts
   - Assignment-specific instructions (if any)
   - Assignment rubric

### Editing Prompts
1. **Edit General Templates** - Affects all assignments
2. **Edit Assignment Instructions** - Affects only that assignment
3. **Preview Combined** - See final prompt before grading

## Benefits

### ✅ **Flexibility**
- No hardcoded prompts
- Easy to customize per assignment
- Can override general behavior

### ✅ **Extensibility**
- Add new assignments without code changes
- Create assignment-specific evaluation criteria
- Generate rubrics automatically

### ✅ **Maintainability**
- Prompts stored in files, not code
- Easy to version control
- Can share prompts across systems

### ✅ **AI-Powered**
- Rubric generation using LLM
- Consistent rubric structure
- Includes reflection questions

### ✅ **User-Friendly**
- UI for all operations
- No technical knowledge required
- Preview before applying

## File Structure

```
project/
├── prompt_templates/
│   ├── general_code_analysis_prompt.txt
│   └── general_feedback_prompt.txt
├── assignment_prompts/
│   ├── assignment_1_code_analysis_prompt.txt
│   ├── assignment_1_feedback_prompt.txt
│   ├── assignment_2_code_analysis_prompt.txt
│   └── assignment_2_feedback_prompt.txt
├── rubrics/
│   ├── assignment_1_rubric.json
│   └── assignment_2_rubric.json
├── prompt_manager.py
└── business_analytics_grader.py (updated)
```

## Example: Assignment-Specific Instructions

**General Prompt** (applies to all):
```
Analyze the code deeply...
Compare outputs...
Recognize alternatives...
```

**Assignment 2 Specific** (only for Assignment 2):
```
ASSIGNMENT-SPECIFIC INSTRUCTIONS:
For this assignment, pay special attention to:
- Use of dplyr for data manipulation
- Proper handling of missing values
- Visualization quality with ggplot2
- Reflection on data cleaning decisions
```

**Combined Prompt** (what AI sees):
```
Analyze the code deeply...
Compare outputs...
Recognize alternatives...

ASSIGNMENT-SPECIFIC INSTRUCTIONS:
For this assignment, pay special attention to:
- Use of dplyr for data manipulation
- Proper handling of missing values
- Visualization quality with ggplot2
- Reflection on data cleaning decisions
```

## AI Rubric Generation

### Input:
- Assignment description
- Total points

### Output:
```json
{
  "assignment_name": "Data Cleaning Assignment",
  "total_points": 37.5,
  "components": [
    {
      "name": "Technical Skills",
      "points": 9.375,
      "criteria": {
        "excellent": "Code executes flawlessly...",
        "good": "Code executes with minor issues...",
        "satisfactory": "Code mostly works...",
        "needs_improvement": "Code has significant issues..."
      }
    },
    ...
  ],
  "reflection_questions": [
    "How did you decide which missing value strategy to use?",
    "What challenges did you encounter?",
    "How would you improve your approach?"
  ]
}
```

## Future Enhancements

### Potential Additions:
1. **Prompt Versioning** - Track changes over time
2. **Prompt Templates Library** - Share templates across instructors
3. **A/B Testing** - Compare different prompts
4. **Prompt Analytics** - Track which prompts produce better results
5. **Multi-Language Support** - Prompts in different languages
6. **Rubric Templates** - Pre-built rubrics for common assignment types
7. **Collaborative Editing** - Multiple instructors editing prompts
8. **Prompt Validation** - Check for required placeholders

This system makes the grading platform truly extensible and customizable without requiring code changes!