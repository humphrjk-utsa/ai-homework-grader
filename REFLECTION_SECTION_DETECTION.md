# Reflection Section Detection

## How It Works

The system automatically detects which section contains reflection questions, regardless of the part number.

## Detection Logic

The system looks for sections that meet **either** criteria:

1. **Explicit marker**: `"check_type": "markdown"`
2. **Name-based**: Contains "reflection" in the section name (case-insensitive)

## Examples

### Example 1: Part 9 Reflections (Midterm)
```json
{
  "part9_reflections": {
    "name": "Part 9: Reflection Questions",
    "points": 5,
    "check_type": "markdown",
    "reflection_questions": 5,
    "min_words_per_question": 50
  }
}
```
✅ Detected by: `check_type == "markdown"` AND name contains "reflection"

### Example 2: Part 6 Reflections (Homework)
```json
{
  "part6_reflections": {
    "name": "Part 6: Reflection Questions",
    "points": 10,
    "check_type": "markdown",
    "reflection_questions": 3,
    "min_words_per_question": 50
  }
}
```
✅ Detected by: `check_type == "markdown"` AND name contains "reflection"

### Example 3: Part 3 Reflections (Short Assignment)
```json
{
  "part3_written_responses": {
    "name": "Part 3: Written Reflection",
    "points": 15,
    "check_type": "markdown",
    "reflection_questions": 2,
    "min_words_per_question": 100
  }
}
```
✅ Detected by: `check_type == "markdown"` AND name contains "reflection"

### Example 4: Final Thoughts (Alternative Name)
```json
{
  "part5_final_thoughts": {
    "name": "Part 5: Reflective Analysis",
    "points": 8,
    "check_type": "markdown",
    "reflection_questions": 4,
    "min_words_per_question": 75
  }
}
```
✅ Detected by: `check_type == "markdown"` AND name contains "reflect"

## What Happens After Detection

1. **Extract Reflections**: System finds all markdown cells with "Question X.Y" pattern
2. **Grade Quality**: AI compares student answers to solution answers
3. **Calculate Score**: Average quality score × max_points
4. **Replace Score**: Replaces simple completion score with AI quality score
5. **Recalculate Total**: Updates overall grade with new reflection score

## Rubric Requirements

For reflection sections to be AI-graded, the rubric must include:

```json
{
  "partX_reflections": {
    "name": "Part X: Reflection Questions",  // Must contain "reflection"
    "points": 10,                            // Max points for this section
    "check_type": "markdown",                // Marks as reflection section
    "reflection_questions": 3,               // Number of questions expected
    "min_words_per_question": 50             // Minimum words per answer
  }
}
```

## Fallback Behavior

If no reflection section is detected:
- System continues with normal grading
- No AI reflection grading is performed
- No error is thrown

If reflection section is detected but AI grading fails:
- Falls back to completion-based scoring
- Checks if questions are answered (word count)
- Logs warning about AI unavailability

## Benefits

✅ **Flexible**: Works with any part number (Part 1, Part 6, Part 9, etc.)
✅ **Automatic**: No hardcoding of section IDs
✅ **Robust**: Multiple detection methods (check_type + name)
✅ **Backward Compatible**: Existing rubrics continue to work
✅ **Clear**: Section name makes it obvious what's being graded

## Testing

To test with different part numbers:

```python
# Create test rubric with Part 6 reflections
rubric = {
  "autograder_checks": {
    "sections": {
      "part6_reflections": {
        "name": "Part 6: Reflection Questions",
        "check_type": "markdown",
        "points": 10
      }
    }
  }
}

# System will automatically detect and grade Part 6
```

## Output

When grading, you'll see:

```
[LAYER 2.5: REFLECTION GRADING]
--------------------------------------------------------------------------------
   Found reflection section: Part 6: Reflection Questions (10 points)
✅ Reflection Score: 8.5/10
✅ Reflection Quality: 85.0%

🎯 REFLECTION ADJUSTMENT:
  Section: Part 6: Reflection Questions
  Old score: 10.0 (completion-based)
  New score: 8.5 (AI-graded quality)
  Adjusted base score: 92.3%
```

The system works the same regardless of which part number contains reflections!
