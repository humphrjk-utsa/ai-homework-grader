# Assignment Management System

## Overview

The enhanced assignment management system now supports JSON file upload for rubrics and intelligent assignment-to-rubric matching. This eliminates the need for manual copy-paste of JSON rubrics and ensures the correct rubric is used for each assignment.

## Key Features

### 🚀 **New Assignment Management Page**
- **Location**: Main navigation → "Assignment Management"
- **Tabs**: Create, Edit, Overview, Migration Helper

### 📁 **JSON File Upload**
- Upload rubric JSON files directly
- Automatic validation of rubric structure
- Preview rubric before saving
- Support for predefined rubrics

### 🎯 **Intelligent Matching**
- Automatic suggestion of appropriate rubrics based on assignment names
- Assignment type detection (Data Cleaning, Introduction, etc.)
- Compatibility scoring between assignments and rubrics

### 🔄 **Migration Helper**
- Automatically detect assignments that need rubric updates
- Suggest appropriate rubrics for existing assignments
- Bulk update capabilities

## How to Use

### Creating a New Assignment

1. **Navigate** to "Assignment Management" → "Create Assignment" tab
2. **Enter** assignment details:
   - Assignment Name (e.g., "2.3", "Homework 2 - Data Cleaning")
   - Description
   - Total Points
3. **Choose Rubric Method**:
   - **Upload JSON File**: Browse and select a `.json` rubric file
   - **Predefined Rubrics**: Choose from available rubrics (auto-suggested based on name)
   - **Manual Entry**: Type JSON directly
4. **Upload Files** (optional):
   - Template notebook
   - Solution notebook
5. **Create Assignment**

### Editing Existing Assignments

1. **Navigate** to "Assignment Management" → "Edit Assignments" tab
2. **Select** assignment to edit
3. **Update** details as needed
4. **Update Rubric**:
   - Upload new JSON file
   - Edit current JSON
5. **Save Changes**

### Using the Migration Helper

1. **Navigate** to "Assignment Management" → "Migration Helper" tab
2. **Review** assignments that need rubric updates
3. **Apply** suggested rubrics or choose manually
4. **Verify** compatibility scores

## Rubric File Structure

### Required Structure
```json
{
  "assignment_info": {
    "title": "Assignment Title",
    "total_points": 37.5,
    "learning_objectives": [...]
  },
  "grading_strategy": {
    "automated_testing": 22.5,
    "manual_review": 15
  },
  "rubric_elements": {
    "element_name": {
      "max_points": 10,
      "weight": 10,
      "category": "automated",
      "description": "Element description",
      "criteria": {...}
    }
  }
}
```

### Predefined Rubrics
- **Assignment 1**: Introduction to R - Environment Setup
- **Assignment 2**: Data Cleaning - Missing Values and Outliers

Located in: `homework_grader/rubrics/`

## Assignment Name Matching

The system automatically matches assignment names to appropriate rubrics:

### Assignment 2 Patterns
- "2.3", "Assignment 2.3", "Homework 2"
- "Data Cleaning", "Missing Values", "Outliers"

### Assignment 1 Patterns  
- "1.1", "Assignment 1", "Homework 1"
- "Introduction to R", "Environment Setup", "Import"

## Troubleshooting

### Common Issues

1. **"Invalid JSON format"**
   - Check JSON syntax using a validator
   - Ensure all quotes are properly closed
   - Verify comma placement

2. **"Rubric validation errors"**
   - Ensure required sections exist: `assignment_info`, `rubric_elements`
   - Check that `max_points` are numeric
   - Verify total points match sum of elements

3. **"No rubric suggestion"**
   - Assignment name doesn't match known patterns
   - Use Migration Helper to manually assign rubric
   - Create custom rubric if needed

### Getting Help

1. **Validation Errors**: The system shows specific validation errors
2. **Compatibility Check**: Shows compatibility score and suggestions
3. **Migration Helper**: Guides you through fixing rubric assignments

## Technical Details

### Files Added/Modified
- `assignment_editor.py` - New assignment management interface
- `rubric_manager.py` - Rubric validation and management utilities
- `assignment_matcher.py` - Intelligent assignment-to-rubric matching
- `migration_helper.py` - Migration and compatibility checking
- `app.py` - Updated navigation to include new page

### Database Changes
- No schema changes required
- Uses existing `assignments.rubric` column
- Stores JSON rubrics as text

### File Structure
```
homework_grader/
├── rubrics/                    # Predefined rubric files
│   ├── assignment_1_rubric.json
│   └── assignment_2_rubric.json
├── assignment_editor.py        # Main assignment management
├── rubric_manager.py           # Rubric utilities
├── assignment_matcher.py       # Intelligent matching
└── migration_helper.py         # Migration tools
```

## Benefits

1. **No More Copy-Paste**: Upload JSON files directly
2. **Automatic Matching**: System suggests appropriate rubrics
3. **Validation**: Catch rubric errors before saving
4. **Migration**: Easy updates for existing assignments
5. **Consistency**: Standardized rubric structure
6. **Flexibility**: Support for custom rubrics

## Next Steps

1. **Test** the new system with existing assignments
2. **Use Migration Helper** to update assignments that need rubrics
3. **Create** new assignments using the enhanced interface
4. **Verify** that grading uses the correct rubrics

The system is now ready to properly match assignments to their appropriate rubrics, ensuring Francisco's Assignment 2.3 submission gets graded with the Assignment 2 rubric instead of Assignment 1!