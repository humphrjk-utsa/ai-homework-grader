# 🎯 How to Use the AI Training Interface

## 🚀 **Getting Started**

### **1. Launch the Web Interface**
```bash
cd homework_grader
streamlit run app.py
```

### **2. Navigate to AI Training**
- Open your browser to the Streamlit app
- Click **"AI Training"** in the sidebar
- You'll see the AI Training Dashboard

---

## 📝 **Review & Correct Tab - Main Workflow**

### **Step 1: Filter Submissions**
- **Assignment Filter**: Choose specific assignment or "All Assignments"
- **Status Filter**: 
  - "Needs Review" - Shows ungraded submissions
  - "Already Corrected" - Shows your previous corrections
  - "All" - Shows everything

### **Step 2: Review AI Grades**
For each submission, you'll see:

**Left Side - AI Assessment:**
- AI's score (0-100)
- AI's feedback text
- 💡 **Smart suggestions** based on code analysis

**Right Side - Your Assessment:**
- **Corrected Score**: Adjust the AI's score
- **Corrected Feedback**: Edit or write new feedback
- **Suggested feedback templates** appear automatically

### **Step 3: Make Corrections**
Two options for each submission:

1. **💾 Save Correction**: 
   - Modify score/feedback and save your changes
   - This trains the AI to grade more like you

2. **✅ Approve AI Grade**: 
   - Accept the AI's assessment as-is
   - Still counts as training data

### **Step 4: View Full Context**
- **📖 View Notebook**: See the complete student submission
- **Code analysis**: Review what the student actually wrote

---

## 📊 **Training Progress Tab**

### **Visual Analytics:**
- **Correction Rate Over Time**: Track your training progress
- **AI vs Human Scores**: Scatter plot showing agreement
- **Score Difference Distribution**: How far off the AI typically is

### **Key Metrics:**
- Total samples graded
- Correction rate percentage
- Average score difference between you and AI

---

## 🔄 **Retrain Model Tab**

### **When to Retrain:**
- After correcting 10+ submissions
- When you notice consistent AI errors
- Before grading a new batch of assignments

### **Training Options:**
1. **Global Model**: Trains on all assignments (recommended)
2. **Language-Specific**: Trains for R, SQL, Python separately
3. **Individual Assignment**: Trains for one specific assignment

### **Process:**
1. Select training scope
2. Choose options (feedback inclusion, cross-validation)
3. Click **🚀 Start Retraining**
4. Wait for completion (usually 1-2 minutes)

---

## 📈 **Performance Analytics Tab**

### **Error Analysis:**
- **Average Grading Error by Assignment**: Which assignments the AI struggles with
- **Types of Corrections**: Whether you typically increase/decrease AI scores
- **Common Feedback Themes**: Word frequency in your corrections

### **Use This To:**
- Identify problematic assignment types
- Understand your grading patterns
- Improve AI training focus

---

## 🧙‍♂️ **Setup Helper Tab**

### **Assignment Setup Wizard:**
- Guides you through creating new assignments
- Sets up proper rubrics and expectations
- Configures AI training parameters

### **Course Training Planner:**
- Plans training schedule for semester
- Estimates training data needs
- Suggests correction priorities

---

## 🔄 **Alternative Approaches Tab**

### **Flexibility Settings:**
- Configure how strict the AI should be
- Set acceptable alternative solutions
- Define equivalent approaches

### **Valid Examples:**
- Add examples of acceptable alternative solutions
- Train AI to recognize different valid approaches
- Handle creative student solutions

---

## 💡 **Best Practices**

### **Effective Training:**
1. **Start Small**: Correct 5-10 submissions initially
2. **Be Consistent**: Use similar scoring criteria
3. **Provide Context**: Write detailed feedback explaining your reasoning
4. **Regular Retraining**: Retrain after every 10-15 corrections

### **Efficient Workflow:**
1. **Filter by "Needs Review"** to focus on new submissions
2. **Use suggested feedback templates** as starting points
3. **Approve good AI grades** quickly with ✅ button
4. **Focus corrections** on submissions where AI is significantly off

### **Quality Control:**
1. **Review your corrections** in "Already Corrected" filter
2. **Check performance analytics** to see improvement trends
3. **Clear old training data** periodically to manage database size

---

## 🎯 **Example Training Session**

### **Typical 15-minute session:**
1. **Filter**: "Assignment 1" + "Needs Review"
2. **Review**: 5-8 submissions
3. **Correct**: 2-3 that need adjustment
4. **Approve**: 3-5 that are already good
5. **Retrain**: If you've accumulated 10+ corrections
6. **Check**: Performance analytics for improvement

### **Result:**
- AI learns your grading style
- Future grades become more accurate
- Less manual correction needed over time

---

## 🔧 **Troubleshooting**

### **Common Issues:**
- **"No submissions found"**: Check your filters, make sure assignments are uploaded
- **AI not improving**: Need more diverse training examples
- **Slow performance**: Clear old training data in Review tab

### **Getting Help:**
- Check the model status in the sidebar
- Review error messages in the interface
- Use the setup helper for guidance

---

## 🎉 **Success Metrics**

### **You'll know it's working when:**
- Correction rate decreases over time
- AI scores get closer to your scores
- Less time spent on manual grading
- More consistent grades across similar submissions

**The goal is to train the AI to grade like you, so you can focus on providing meaningful feedback rather than scoring!** 🌟