# Prompt Improvement Plan

## Current Issues
1. **Self-dialog in responses** - AI includes internal reasoning like "We need to evaluate...", "Let's check..."
2. **Shallow code analysis** - Not deeply examining code logic and outputs
3. **No output comparison** - Not comparing student results to solution notebook outputs
4. **Missing alternative suggestions** - Not suggesting feasible alternatives when code differs from solution
5. **Ignoring irrelevant warnings** - Not filtering out warnings that don't affect results

## Reference Prompts (from ~/Documents/x/)
The reference prompts are much more detailed and include:
- **Reflection question focus** - Explicitly looks for and evaluates reflection responses
- **Higher minimum scores** - Starts at 90+ for complete work vs current 70+
- **More detailed evaluation criteria** - Specific focus areas for business analytics
- **Professional tone** - More academic and constructive language
- **Learning demonstration** - Emphasis on evidence of learning and growth

## Proposed Improvements

### 1. Code Analysis Prompt Enhancement
**Add:**
- Deep code logic analysis
- Output comparison with solution notebook
- Alternative approach recognition
- Warning/error filtering (ignore non-critical warnings)
- Specific code examples in suggestions

**Remove:**
- Internal reasoning language
- Assumptions about missing code
- Generic feedback

### 2. Feedback Generation Prompt Enhancement
**Add:**
- Explicit reflection question evaluation
- Output accuracy comparison
- Alternative solution recognition
- Specific examples from student work
- Higher baseline scores (90+ for complete work)

**Remove:**
- Self-dialog patterns
- Generic assessments
- Internal evaluation process descriptions

### 3. JSON Response Format
**Enforce:**
- Pure JSON output only
- No markdown wrappers
- No explanatory text before/after JSON
- Structured feedback arrays

## Implementation Strategy

### Phase 1: Update Code Analysis Prompt
```python
def _prepare_code_analysis_prompt():
    # Add sections for:
    # 1. Output comparison
    # 2. Alternative approach recognition
    # 3. Deep logic analysis
    # 4. Warning filtering
```

### Phase 2: Update Feedback Prompt
```python
def _prepare_feedback_prompt():
    # Add sections for:
    # 1. Reflection question focus
    # 2. Output accuracy check
    # 3. Alternative solution recognition
    # 4. Specific examples requirement
```

### Phase 3: Strengthen JSON Extraction
```python
def _parse_feedback_response():
    # Improve:
    # 1. JSON extraction from mixed content
    # 2. Self-dialog filtering
    # 3. Fallback handling
```

## Key Differences: Reference vs Current

| Aspect | Reference (x folder) | Current | Improvement Needed |
|--------|---------------------|---------|-------------------|
| Minimum Scores | 90-92+ | 70-85 | Raise baseline |
| Reflection Focus | Explicit priority | Mentioned | Make primary focus |
| Code Analysis Depth | Deep with examples | Surface level | Add output comparison |
| Alternative Solutions | Recognized | Not mentioned | Add recognition logic |
| Self-Dialog | Minimal | Present | Remove completely |
| Output Comparison | Included | Missing | Add comparison |
| Warning Handling | Filtered | Not addressed | Add filtering |

## Next Steps
1. Update `_prepare_code_analysis_prompt()` with deep analysis requirements
2. Update `_prepare_feedback_prompt()` with reflection focus and output comparison
3. Add output comparison logic to extract and compare results
4. Strengthen JSON extraction to handle mixed responses
5. Test with real submissions to verify improvements
