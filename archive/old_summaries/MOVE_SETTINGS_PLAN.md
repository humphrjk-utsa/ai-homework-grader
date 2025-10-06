# Move Assignment Helper & Settings Plan

## What Needs to Move

### From AI Training Page → To Assignment Management Page:
1. **Assignment Setup Helper** (tab 5)
2. **Model Settings** (temperature, max_tokens, model selection)

## Database Changes Needed

### Add columns to `assignments` table:
```sql
ALTER TABLE assignments ADD COLUMN temperature REAL DEFAULT 0.3;
ALTER TABLE assignments ADD COLUMN max_tokens INTEGER DEFAULT 1200;
ALTER TABLE assignments ADD COLUMN code_model TEXT DEFAULT 'hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest';
ALTER TABLE assignments ADD COLUMN feedback_model TEXT DEFAULT 'gemma3:27b-it-q8_0';
```

## Implementation Steps

### Step 1: Update Database Schema
- Create migration script
- Add new columns
- Set defaults

### Step 2: Update Assignment Editor UI
Add new tab: "🎛️ Grading Settings"
- Temperature slider
- Max tokens input
- Model selection dropdowns
- Assignment Setup Helper

### Step 3: Update Training Interface
- Remove "Setup Helper" tab
- Keep only training-related tabs:
  - Review & Correct
  - Training Progress
  - Retrain Model
  - Performance Analytics
  - Alternative Approaches

### Step 4: Update Grading Logic
- Load settings from assignment
- Pass to BusinessAnalyticsGrader
- Use assignment-specific temperature/models

### Step 5: Update Assignment Creation
- Save settings when creating assignment
- Load settings when editing assignment
- Display current settings

## Files to Modify

1. `migrations/add_grading_settings.py` (NEW)
2. `assignment_editor.py` - Add settings tab
3. `training_interface.py` - Remove setup helper tab
4. `connect_web_interface.py` - Load and use settings
5. `business_analytics_grader.py` - Accept settings parameters
6. `app.py` - Update schema

## User Flow

### Creating Assignment:
1. Go to Assignment Management
2. Fill in basic info
3. Go to "Grading Settings" tab
4. Set temperature, models, tokens
5. Use Setup Helper if needed
6. Save assignment (settings stored)

### Grading:
1. Upload submissions
2. Grade (loads assignment settings)
3. Uses assignment's temperature/models
4. Generates results

### Training:
1. Review AI grades
2. Correct mistakes
3. AI learns
(No setup/settings here)

## Benefits

✅ Logical organization
✅ Settings stored per assignment
✅ Different assignments can use different settings
✅ Clear separation of concerns
✅ Setup happens before grading, not during training
