# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Launch the Application

```bash
cd homework_grader
python run_grader.py
```

### Step 2: Create Your First Assignment

1. Click "Create Assignment" in the sidebar
2. Fill in the form:
   - **Name**: "Homework 1 - Intro to R"
   - **Description**: "Introduction to R programming"
   - **Total Points**: 100
   - **Rubric**: Copy from `sample_rubric.json`
   - **Template**: Upload `sample_assignment_template.ipynb`
   - **Solution**: Upload `sample_solution.ipynb`
3. Click "Create Assignment"

### Step 3: Upload Student Submissions

1. Go to "Upload Submissions"
2. Select your assignment
3. Upload individual `.ipynb` files or a ZIP containing multiple notebooks
4. Student files should be named with student IDs (e.g., `student123.ipynb`)

### Step 4: Grade with AI

1. Navigate to "Grade Submissions"
2. Select your assignment
3. Click "Grade All Submissions"
4. Wait for AI to process all notebooks

### Step 5: Review and Adjust

1. Go to "View Results"
2. Click "Grade" next to any submission
3. Review AI suggestions and adjust scores
4. Add personalized feedback
5. Save your grades

### Step 6: Train the AI (After 10+ Manual Grades)

1. Visit "AI Training"
2. Select your assignment
3. Click "Train AI Model"
4. The AI will learn from your grading patterns

## 📁 File Organization Tips

### Student Submission Naming

- Individual files: `studentID.ipynb` (e.g., `john_doe_123.ipynb`)
- ZIP files: Contains notebooks named with student IDs

### Assignment Templates

- Include clear instructions and point values
- Use markdown cells for explanations
- Leave empty code cells for student work
- Include reflection questions

### Solution Notebooks

- Complete all exercises with expected outputs
- Add detailed comments explaining the approach
- Include multiple solution methods where applicable

## 🎯 Best Practices

### For Better AI Grading

1. **Consistent Rubrics**: Use the same criteria across assignments
2. **Clear Instructions**: Specific requirements help AI understand expectations
3. **Manual Training**: Grade 10-15 submissions manually before relying on AI
4. **Regular Retraining**: Update AI models as you grade more submissions

### For Efficient Workflow

1. **Batch Processing**: Upload all submissions at once using ZIP files
2. **Review AI Suggestions**: Don't blindly accept AI grades - always review
3. **Detailed Feedback**: Rich feedback improves student learning and AI training
4. **Export Regularly**: Download results as CSV for backup and LMS integration

## 🔧 Troubleshooting

### Common Issues

- **Notebook won't execute**: Check for missing libraries or infinite loops
- **AI scores seem off**: Need more training data or inconsistent manual grading
- **Upload fails**: Verify file format (.ipynb) and naming conventions

### Getting Help

- Check the full README.md for detailed documentation
- Review error messages in the Streamlit interface
- Examine the database using any SQLite browser for debugging

## 📊 Understanding the Interface

### Dashboard

- Overview of all assignments and submissions
- Quick statistics and recent activity

### Create Assignment

- Set up new homework with rubrics and reference materials

### Upload Submissions

- Single file or batch upload of student work

### Grade Submissions

- AI-powered automatic grading with execution testing

### View Results

- Comprehensive results table with manual grading interface

### AI Training

- Model training and performance monitoring

## 🎓 Sample Workflow

1. **Semester Start**: Create assignment templates and rubrics
2. **Assignment Due**: Students submit notebooks via your preferred method
3. **Initial Grading**: Upload submissions and run AI grading
4. **Quality Review**: Manually review 10-20% of submissions
5. **Feedback**: Provide detailed feedback on reviewed submissions
6. **Model Training**: Train AI on your grading patterns
7. **Future Assignments**: AI becomes more accurate with each assignment

This system is designed to save you time while maintaining grading quality. Start with manual review and gradually rely more on AI as it learns your preferences!
