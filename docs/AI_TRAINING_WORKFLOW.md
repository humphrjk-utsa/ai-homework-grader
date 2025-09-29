# AI Training Workflow: How to Train the Model to Grade Like You

## Overview

The homework grading system uses a sophisticated machine learning approach that learns from your corrections and feedback. Here's exactly how it works and how to use it effectively:

## 1. Automatic Data Collection

**What happens automatically:**
- Every time you grade a submission, the system extracts features from the student's notebook
- Features include: code quality, execution success, response completeness, etc.
- The AI provides an initial grade and stores this as training data
- All interactions are saved to the `ai_training_data` table in the database

**No action needed** - this happens in the background during normal grading.

## 2. Review and Correction Process

**Navigate to: AI Training → Review & Correct**

### Step-by-step correction workflow:

1. **Filter submissions** to focus on:
   - Specific assignments where AI struggles
   - "Needs Review" status for uncorrected grades
   - Recent submissions for current patterns

2. **Review each AI assessment:**
   - Compare AI score vs your expected score
   - Read AI feedback vs your teaching style
   - Check smart suggestions (execution errors, incomplete work, etc.)

3. **Make corrections:**
   - Adjust the score if needed
   - Rewrite feedback in your voice and style
   - Use suggested feedback templates as starting points
   - Save corrections or approve good AI grades

### Pro Tips for Effective Corrections:
- **Focus on big discrepancies first** (>10 point differences)
- **Be consistent** in your correction patterns
- **Document your reasoning** in detailed feedback
- **Correct in batches** of 10-20, then retrain

## 3. Model Training Process

**Navigate to: AI Training → Retrain Model**

### When to retrain:
- After every 10-15 new corrections
- When you notice consistent AI mistakes
- Before grading a new batch of assignments

### Training options:
- **Global model**: Learns from all assignments (good for general grading style)
- **Assignment-specific**: Learns patterns for specific assignment types
- **Cross-validation**: Tests model accuracy before deployment

### What the AI learns:
- **Your scoring patterns**: How you weight different criteria
- **Feedback style**: Your tone, common phrases, encouragement level
- **Code quality assessment**: What you consider good/poor code
- **Content evaluation**: How you assess reflection questions

## 4. Continuous Improvement Cycle

```
Grade Submissions → AI Provides Initial Grades → Review & Correct → Retrain Model → Better AI Grades
```

### Monitoring improvement:
- **Training Progress**: Track correction rates over time
- **Performance Analytics**: Monitor average grading error
- **Score Accuracy**: Compare AI vs human scores
- **Feedback Quality**: Analyze correction patterns

## 5. Advanced Training Strategies

### For Different Assignment Types:
- **Code-heavy assignments**: Train separate model focusing on execution and syntax
- **Reflection-heavy assignments**: Train model emphasizing content depth and insight
- **Mixed assignments**: Use global model with assignment-specific fine-tuning

### Handling Edge Cases:
- **Exceptional students**: Create corrections for both high and low performers
- **Creative solutions**: Correct AI when it penalizes valid alternative approaches
- **Partial credit**: Train AI on nuanced scoring for incomplete but correct work

### Feedback Style Training:
- **Encouraging tone**: Consistently rewrite harsh AI feedback to be supportive
- **Specific guidance**: Replace vague AI comments with actionable advice
- **Positive reinforcement**: Always include what students did well

## 6. Technical Details

### Feature Extraction:
The system analyzes:
- **Code metrics**: Lines of code, function count, variable usage
- **Execution results**: Success/failure, error types, output quality
- **Content analysis**: Text length, keyword usage, concept coverage
- **Structure patterns**: Cell organization, comment usage, documentation

### Machine Learning Approach:
- **Random Forest Regressor**: Handles mixed data types and non-linear patterns
- **TF-IDF Vectorization**: Analyzes text content and feedback
- **Feature Engineering**: Combines code metrics with content analysis
- **Cross-validation**: Ensures model generalizes well to new data

### Training Data Storage:
```sql
ai_training_data table:
- assignment_id: Links to specific assignment
- cell_content: Path to student notebook
- features: JSON of extracted features
- ai_score: Initial AI assessment
- ai_feedback: Initial AI feedback
- human_score: Your corrected score
- human_feedback: Your corrected feedback
- created_at: When initially graded
- corrected_at: When you made corrections
```

## 7. Troubleshooting Common Issues

### "Model needs more training data"
- **Solution**: Continue making corrections until you have 10+ samples
- **Tip**: Focus on diverse examples (high, medium, low scores)

### "AI still making same mistakes"
- **Check**: Are your corrections consistent?
- **Solution**: Review your correction patterns for consistency
- **Tip**: Document your grading criteria clearly

### "Scores too harsh/lenient"
- **Analyze**: Review score difference distribution in analytics
- **Adjust**: Make more corrections in the problematic score range
- **Retrain**: Update model with new correction patterns

### "Feedback doesn't sound like me"
- **Strategy**: Rewrite AI feedback extensively in early corrections
- **Focus**: Use your common phrases and teaching style
- **Consistency**: Apply same feedback style across similar issues

## 8. Best Practices Summary

1. **Start with obvious corrections** - large score discrepancies
2. **Be consistent** in your grading standards
3. **Provide detailed feedback** in corrections
4. **Retrain regularly** after batches of corrections
5. **Monitor performance** using the analytics dashboard
6. **Focus on your teaching style** in feedback corrections
7. **Use assignment-specific models** for specialized content
8. **Document your criteria** for consistent training

This system gets better with use - the more corrections you make, the more it learns your specific grading style and standards!