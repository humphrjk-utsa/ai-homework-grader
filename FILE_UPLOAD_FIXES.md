# File Upload & Naming Fixes - Nov 2, 2024

## Issues Fixed

### 1. Student Name Extraction
**Problem**: Names not correctly parsed from filename before first `_`
**Fix**: The `parse_github_classroom_filename()` function already correctly extracts the first part as Canvas ID. The function works as designed.

### 2. File Upload Caching
**Problem**: Single file grading uses cached filename from previous uploads
**Solution**: 
- Added session state tracking with `last_uploaded_file`
- Detects new files by comparing `filename + filesize`
- Clears cached override values when new file is uploaded
- Shows clear "Extracted from filename" section

### 3. Duplicate Filename Handling
**Problem**: Can't grade same filename twice without clearing results
**Solution**:
- Added optional "Submission Label" field
- Label gets appended to filename: `Name_ID_label.ipynb`
- Examples: `John_Doe_12345_revised.ipynb`, `Jane_Smith_67890_v2.ipynb`

### 4. Manual Override
**Problem**: Manual override fields not working properly
**Solution**:
- Moved override fields out of expander for better visibility
- Used proper session state keys: `manual_override_id`, `manual_override_name`
- Fields now properly editable and persist correctly

## How It Works Now

### Single File Upload Flow:
1. Upload file → Auto-extracts Canvas ID and Name
2. Shows extracted info clearly
3. Edit fields if needed (Canvas ID, Student Name)
4. Add optional label for duplicates
5. Upload → Saves with proper naming

### Filename Format:
- **Without label**: `StudentName_CanvasID.ipynb`
- **With label**: `StudentName_CanvasID_label.ipynb`

### Examples:
```
Original: guadarramafrancisco_178108_11544892_homework.ipynb
Extracted: Canvas ID = guadarramafrancisco, Name = Guadarrama Francisco
Saved as: Guadarrama_Francisco_guadarramafrancisco.ipynb

With label "revised":
Saved as: Guadarrama_Francisco_guadarramafrancisco_revised.ipynb
```

## Files Modified
- `assignment_manager.py` - Single file upload function
  - Added session state tracking
  - Added submission label field
  - Improved UI layout
  - Fixed manual override handling
