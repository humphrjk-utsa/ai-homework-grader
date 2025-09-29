# AI Training Guide

## How to Train the AI to Grade Like You

The homework grading system includes a sophisticated AI training mechanism that learns from your corrections and feedback. Here's how to use it effectively:

### 1. Initial Grading Phase

When you first start using the system:
- Grade assignments normally using the "Grade Submissions" page
- The AI will provide initial grades based on rule-based analysis
- All AI grades and extracted features are automatically stored as training data

### 2. Review and Correct AI Grades

Navigate to **AI Training** → **Review & Correct** tab:

- **Filter submissions** by assignment or correction status
- **Review AI assessments** alongside the original student work
- **Make corrections** by adjusting scores and feedback
- **Approve good grades** when the AI got it right

#### Correction Strategies:
- Focus on submissions where AI scores seem off by more than 5-10 points
- Pay attention to feedback tone - make it sound more like your teaching style
- Look for patterns in AI mistakes (too harsh/lenient on specific criteria)

### 3. Training Data Collection

The system automatically collects:
- **Student code and responses** (features extracted)
- **AI initial grades** and reasoning
- **Your corrections** and feedback
- **Approval/rejection** of AI assessments

### 4. Model Retraining

Once you have 10+ corrections:
- Go to **AI Training** → **Retrain Model** tab
- Choose between global or assignment-specific training
- Run retraining to update the AI model
- Review cross-validation results

### 5. Performance Monitoring

Track improvement in **Performance Analytics**:
- Monitor average grading error over time
- Identify assignments where AI struggles most
- Analyze common correction patterns
- Review feedback quality improvements

## Best Practices

### Effective Correction Workflow:
1. **Start with obvious errors** - large score discrepancies first
2. **Focus on feedback tone** - make it encouraging and constructive
3. **Be consistent** - use similar language for similar issues
4. **Correct in batches** - review 10-20 submissions, then retrain

### Training Tips:
- **Quality over quantity** - better to have 20 good corrections than 100 rushed ones
- **Document your reasoning** - detailed feedback helps the AI learn your style
- **Regular retraining** - retrain after every 10-15 new corrections
- **Assignment-specific models** - train separate models for different assignment types

## Understanding the AI Learning Process

### What the AI Learns From:
- **Code quality patterns** - syntax, structure, completeness
- **Response content** - thoroughness, accuracy, insight
- **Your scoring patterns** - how you weight different criteria
- **Feedback style** - your tone, common phrases, encouragement level

### Feature Extraction:
The system analyzes:
- Code execution success/failure
- Package usage and imports
- Data manipulation techniques
- Reflection question responses
- Code comments and documentation

### Continuous Improvement:
- Each correction improves future grading
- The AI adapts to your specific teaching style
- Performance metrics help identify areas needing attention
- Regular retraining keeps the model current

## Troubleshooting

### Common Issues:
- **"Need more training data"** - Continue correcting until you have 10+ samples
- **AI still making same mistakes** - Check if corrections are consistent
- **Scores too harsh/lenient** - Adjust your correction patterns and retrain

### Getting Better Results:
- Provide detailed feedback in corrections
- Be consistent in your grading standards
- Focus on the most important criteria for each assignment
- Regularly review and update your approach