# Tableau Grading - Quick Start Guide

## ✅ What's Working Now

### 1. TWBX File Parsing
```python
from homework_grader.tableau_parser import TableauWorkbookParser

parser = TableauWorkbookParser("student_submission.twbx")
analysis = parser.analyze_workbook()

# Returns:
# - All worksheets
# - All dashboards  
# - All calculated fields with formulas
# - Data sources
# - Filters
```

### 2. Automated Technical Grading
```python
from homework_grader.tableau_grader import TableauGrader

config = {
    'assignment_name': 'Sales Dashboard',
    'min_worksheets': 3,
    'min_dashboards': 1,
    'technical_points': 37.5
}

grader = TableauGrader(config)
result = grader.grade_workbook("student_submission.twbx")

# Returns:
# - Technical score (0-37.5)
# - Component validation
# - Calculation validation
# - AI-ready prompt
```

---

## 🎯 What We Can Grade

### Automatically Validated:
✅ Required worksheets present  
✅ Required dashboards present  
✅ Required calculated fields present  
✅ Minimum component counts  
✅ Calculation formula syntax  
✅ Division by zero protection  
✅ Proper aggregation usage  

### Ready for AI Grading:
✅ Calculation logic correctness (Qwen)  
✅ Dashboard design quality (GPT-OSS)  
✅ Visualization appropriateness (GPT-OSS)  
✅ Business insight quality (GPT-OSS)  

### Coming Soon:
🚧 Visual design analysis (GPT-4 Vision)  
🚧 Written answer grading (PDF parsing)  
🚧 Screenshot analysis  
🚧 Accessibility checks  

---

## 📋 Example Assignment Config

```python
SALES_DASHBOARD_ASSIGNMENT = {
    'assignment_name': 'Executive Sales Dashboard',
    'assignment_type': 'tableau',
    
    # What must be present
    'required_worksheets': [
        'Sales by Region',
        'Profit Trend',
        'Top 10 Products'
    ],
    'required_dashboards': [
        'Executive Dashboard'
    ],
    'required_calculations': [
        'Profit Margin',
        'YoY Sales Growth',
        'Average Order Value'
    ],
    
    # Minimum counts
    'min_worksheets': 3,
    'min_dashboards': 1,
    'min_calculated_fields': 2,
    
    # Scoring (matches existing 37.5 point system)
    'technical_points': 37.5,
    'points_breakdown': {
        'required_components': 15,
        'minimum_requirements': 10,
        'calculated_fields': 12.5
    }
}
```

---

## 🚀 Quick Test

```bash
# Test the parser
python homework_grader/tableau_parser.py

# Test the grader
python homework_grader/tableau_grader.py

# Check the output
cat data/processed/tableau_grading_result.json
```

---

## 📊 Sample Output

```
============================================================
📊 TABLEAU GRADING RESULT
============================================================

File: Student_Dashboard.twbx
Technical Score: 25.0/37.5

📋 TECHNICAL DETAILS:
  ✅ All required components present (+15)
  ✅ Minimum requirements met (+10)
  ⚠️ 1 calculation issues (+0.0/12.5)

WORKBOOK ANALYSIS:
  • 5 worksheets
  • 1 dashboard
  • 1 calculated field (Profit Margin)
  • 1 data source

CALCULATED FIELDS:
  • Profit Margin: [Profit]/[Sales]
    Issue: Missing division by zero protection

✅ Ready for AI grading: True
============================================================
```

---

## 🔄 Integration with Existing System

### Current System:
```
Student .ipynb → Parse → Qwen + GPT-OSS → Score → Report
```

### Extended System:
```
Student .twbx → Parse → Technical Validation → Qwen + GPT-OSS → Score → Report
                                    ↓
                            (Same AI servers,
                             same workflow,
                             same 37.5 points)
```

**No changes needed to:**
- Mac Studio servers
- AI models
- Database structure (can extend later)
- Report generation (can extend later)
- Parallel processing logic

**Only additions:**
- New file type handler
- Tableau-specific prompts
- Technical validation logic

---

## 📁 File Structure

```
homework_grader/
├── tableau_parser.py          ✅ COMPLETE
├── tableau_grader.py          ✅ COMPLETE
├── vision_analyzer.py         🚧 TODO
└── document_parser.py         🚧 TODO

prompts/
└── tableau/
    ├── calculation_review.txt 🚧 TODO
    ├── dashboard_feedback.txt 🚧 TODO
    └── visual_design.txt      🚧 TODO

docs/
├── TABLEAU_GRADING_ARCHITECTURE.md  ✅ COMPLETE
└── TABLEAU_GRADING_QUICKSTART.md    ✅ COMPLETE
```

---

## 🎯 Next Steps

### Option 1: Full Integration (Recommended)
1. Create Tableau-specific prompts
2. Add Tableau mode to existing grading interface
3. Integrate with Qwen/GPT-OSS servers
4. Test end-to-end grading
5. Generate PDF reports

### Option 2: Standalone Testing
1. Create simple test script
2. Grade sample workbooks
3. Validate scoring logic
4. Refine before integration

### Option 3: Vision Analysis First
1. Build screenshot extractor
2. Integrate GPT-4 Vision
3. Add visual design scoring
4. Then integrate with main system

---

## 💡 Key Decisions Needed

1. **Should we integrate now or build standalone first?**
   - Integrate: Faster to production, uses existing infrastructure
   - Standalone: Easier testing, less risk to existing system

2. **Do we need vision analysis immediately?**
   - Yes: More comprehensive grading, better feedback
   - No: Start with technical + AI text analysis first

3. **Should we support PDF written components?**
   - Yes: More flexible assignments
   - No: Keep it simple initially

4. **Database changes now or later?**
   - Now: Proper tracking from start
   - Later: Use existing submissions table initially

---

## 🧪 Testing Checklist

- [x] Parse sample TWBX file
- [x] Extract worksheets and dashboards
- [x] Extract calculated fields
- [x] Validate technical requirements
- [x] Calculate technical score
- [ ] Generate AI prompts
- [ ] Test with Qwen server
- [ ] Test with GPT-OSS server
- [ ] Generate PDF report
- [ ] Test batch processing
- [ ] Validate scoring accuracy

---

## 📞 Questions to Answer

1. Do you have sample Tableau assignments to test with?
2. What's your typical Tableau assignment structure?
3. Do students submit just TWBX or also written analysis?
4. Should we prioritize integration or standalone tool?
5. Do you want vision analysis in v1 or later?

---

*Ready to proceed with Phase 2: AI Integration!*
