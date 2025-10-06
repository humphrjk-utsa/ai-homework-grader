# Tableau Grading System Architecture

## Overview

Extension to the existing AI homework grading system to support Tableau workbook (.twbx) assignments. Integrates seamlessly with the current distributed AI architecture while adding specialized Tableau analysis capabilities.

---

## System Components

### 1. Tableau Parser (`homework_grader/tableau_parser.py`)

**Purpose**: Extract and analyze Tableau workbook structure

**Capabilities**:
- Extract TWBX files (ZIP archives)
- Parse TWB XML files
- Extract worksheets, dashboards, calculated fields
- Identify data sources and connections
- Analyze filters and parameters
- Generate structured JSON analysis

**Key Methods**:
```python
parser = TableauWorkbookParser(twbx_path)
analysis = parser.analyze_workbook()
# Returns: worksheets, dashboards, calculations, data sources, filters
```

**Output Example**:
```json
{
  "worksheets": [{"name": "Sales by Region", "marks_count": 5}],
  "dashboards": [{"name": "Executive Dashboard", "zones_count": 12}],
  "calculated_fields": [{"name": "Profit Margin", "formula": "[Profit]/[Sales]"}],
  "data_sources": [{"name": "Orders", "type": "excel"}]
}
```

---

### 2. Tableau Grader (`homework_grader/tableau_grader.py`)

**Purpose**: Automated technical validation and scoring

**Validation Checks**:
1. **Required Components**
   - Specific worksheet names
   - Specific dashboard names
   - Required calculated fields
   
2. **Minimum Requirements**
   - Minimum number of worksheets
   - Minimum number of dashboards
   - Minimum calculated fields

3. **Calculated Field Validation**
   - Formula syntax
   - Division by zero protection
   - Proper aggregation usage
   - Logic correctness

4. **Technical Scoring**
   - Component completeness (15 points)
   - Minimum requirements (10 points)
   - Calculated fields (12.5 points)
   - **Total: 37.5 points** (matches existing system)

**Key Methods**:
```python
grader = TableauGrader(assignment_config)
result = grader.grade_workbook(twbx_path)
# Returns: technical_score, details, AI prompt
```

---

### 3. Vision Analyzer (`homework_grader/vision_analyzer.py`) - TO BE BUILT

**Purpose**: AI-powered visual analysis of dashboards

**Capabilities**:
- Extract dashboard screenshots from TWBX
- Analyze chart types and appropriateness
- Evaluate color schemes and accessibility
- Assess layout and design principles
- Check for visual best practices

**Integration**:
- Use GPT-4 Vision or similar multimodal AI
- Generate visual design feedback
- Score aesthetic and UX elements

**Planned Features**:
```python
vision = VisionAnalyzer()
visual_score = vision.analyze_dashboard(dashboard_image)
# Returns: design_score, layout_feedback, accessibility_notes
```

---

### 4. Document Parser (`homework_grader/document_parser.py`) - TO BE BUILT

**Purpose**: Extract and analyze written answers from PDFs/DOCX

**Capabilities**:
- Parse PDF submissions
- Extract DOCX content
- Identify question-answer pairs
- Extract embedded images
- Structure text for AI analysis

**Use Cases**:
- Written analysis questions
- Business insights documentation
- Dashboard explanation essays
- Reflection questions

**Planned Features**:
```python
doc_parser = DocumentParser(pdf_path)
answers = doc_parser.extract_answers()
# Returns: structured Q&A for AI grading
```

---

## Integration with Existing System

### Current Architecture (R/Python Notebooks)

```
Student Submission → Notebook Validation → Code Extraction
                                              ↓
                    ┌─────────────────────────┴─────────────────────────┐
                    ↓                                                     ↓
            Qwen (Code Analysis)                              GPT-OSS (Feedback)
            Mac Studio 2                                      Mac Studio 1
                    ↓                                                     ↓
                    └─────────────────────────┬─────────────────────────┘
                                              ↓
                            Score Validation & Report Generation
```

### Extended Architecture (Tableau Assignments)

```
Student Submission (.twbx + optional PDF)
            ↓
    Tableau Parser
            ↓
    ┌───────┴───────┐
    ↓               ↓
Technical      Vision Analysis
Validation     (screenshots)
    ↓               ↓
    └───────┬───────┘
            ↓
    Document Parser (if PDF included)
            ↓
    ┌─────────────────────────┴─────────────────────────┐
    ↓                                                     ↓
Qwen (Technical + Calculation Review)        GPT-OSS (Design + Business Feedback)
Mac Studio 2                                 Mac Studio 1
    ↓                                                     ↓
    └─────────────────────────┬─────────────────────────┘
                              ↓
                Score Validation & Report Generation
```

---

## Assignment Configuration

### Tableau Assignment Config Structure

```python
{
    'assignment_name': 'Executive Sales Dashboard',
    'assignment_type': 'tableau',  # NEW: identifies assignment type
    
    # Tableau-specific requirements
    'required_worksheets': ['Sales by Region', 'Profit Trend', 'Top Products'],
    'required_dashboards': ['Executive Dashboard'],
    'required_calculations': ['Profit Margin', 'YoY Growth', 'Sales Growth %'],
    
    # Minimum requirements
    'min_worksheets': 3,
    'min_dashboards': 1,
    'min_calculated_fields': 2,
    
    # Scoring breakdown
    'technical_points': 37.5,
    'points_breakdown': {
        'required_components': 15,      # Worksheets, dashboards, calculations
        'minimum_requirements': 10,     # Count thresholds
        'calculated_fields': 12.5,      # Formula validation
        'visual_design': 0,             # Optional: vision analysis
        'written_answers': 0            # Optional: document analysis
    },
    
    # Optional: Written component
    'has_written_component': True,
    'written_questions': [
        'Explain your dashboard design choices',
        'What insights did you discover?',
        'How would you improve this analysis?'
    ],
    
    # Prompts
    'code_analysis_prompt': 'prompts/tableau/calculation_review.txt',
    'feedback_prompt': 'prompts/tableau/dashboard_feedback.txt',
    'vision_prompt': 'prompts/tableau/visual_design.txt'
}
```

---

## Grading Workflow

### Phase 1: Technical Validation (Automated)

```python
# 1. Parse workbook
parser = TableauWorkbookParser(twbx_path)
analysis = parser.analyze_workbook()

# 2. Technical grading
grader = TableauGrader(assignment_config)
technical_result = grader.grade_workbook(twbx_path)

# Output:
# - Technical score (0-37.5)
# - Component checklist
# - Calculation validations
# - Missing requirements
```

### Phase 2: AI Analysis (Parallel)

```python
# Thread 1: Qwen - Technical Review
qwen_prompt = f"""
Analyze these Tableau calculated fields:
{json.dumps(calculated_fields)}

Check for:
- Correct formula syntax
- Appropriate aggregations
- Business logic accuracy
- Performance considerations
"""

# Thread 2: GPT-OSS - Design & Business Feedback
gemma_prompt = f"""
Review this Tableau dashboard:
Worksheets: {worksheets}
Dashboards: {dashboards}
Calculations: {calculations}

Provide feedback on:
- Dashboard design effectiveness
- Appropriate visualization choices
- Data storytelling quality
- Professional presentation
"""

# Execute in parallel (existing infrastructure)
with ThreadPoolExecutor(max_workers=2) as executor:
    qwen_future = executor.submit(qwen_analyze, qwen_prompt)
    gemma_future = executor.submit(gemma_feedback, gemma_prompt)
```

### Phase 3: Vision Analysis (Optional)

```python
# Extract dashboard screenshots
vision = VisionAnalyzer()
screenshots = vision.extract_dashboard_images(twbx_path)

# Analyze with GPT-4 Vision
for screenshot in screenshots:
    visual_feedback = vision.analyze_image(screenshot)
    # Returns: layout quality, color usage, accessibility
```

### Phase 4: Document Analysis (Optional)

```python
# If PDF submission included
if pdf_path:
    doc_parser = DocumentParser(pdf_path)
    answers = doc_parser.extract_answers()
    
    # Grade written responses with GPT-OSS
    written_feedback = gemma_grade_written(answers, questions)
```

### Phase 5: Score Aggregation

```python
final_score = {
    'technical': technical_score,        # From automated validation
    'ai_technical': qwen_score,          # From Qwen analysis
    'ai_feedback': gemma_score,          # From GPT-OSS feedback
    'visual_design': vision_score,       # Optional
    'written': written_score,            # Optional
    'final': calculate_weighted_average()
}
```

---

## Database Schema Extensions

### New Table: `tableau_submissions`

```sql
CREATE TABLE tableau_submissions (
    id INTEGER PRIMARY KEY,
    submission_id INTEGER,  -- FK to submissions
    twbx_path TEXT,
    pdf_path TEXT,          -- Optional written component
    
    -- Workbook analysis
    num_worksheets INTEGER,
    num_dashboards INTEGER,
    num_calculations INTEGER,
    worksheet_names TEXT,   -- JSON array
    dashboard_names TEXT,   -- JSON array
    calculation_names TEXT, -- JSON array
    
    -- Technical validation
    required_components_met BOOLEAN,
    minimum_requirements_met BOOLEAN,
    technical_score REAL,
    
    -- AI scores
    calculation_score REAL,
    design_score REAL,
    visual_score REAL,
    written_score REAL,
    
    -- Metadata
    analysis_json TEXT,     -- Full workbook analysis
    graded_at TIMESTAMP,
    
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);
```

---

## Prompt Templates

### Location: `prompts/tableau/`

**calculation_review.txt** (Qwen)
```
You are an expert Tableau instructor reviewing calculated fields.

STUDENT CALCULATIONS:
{calculated_fields}

ASSIGNMENT REQUIREMENTS:
{required_calculations}

Evaluate each calculation for:
1. Correct formula syntax
2. Appropriate aggregation level
3. Business logic accuracy
4. Edge case handling (division by zero, nulls)
5. Performance considerations

Provide specific feedback on improvements.
Score: 0-37.5 points
```

**dashboard_feedback.txt** (GPT-OSS)
```
You are a supportive Tableau instructor reviewing a student dashboard.

WORKBOOK STRUCTURE:
{workbook_analysis}

ASSIGNMENT CONTEXT:
{assignment_description}

Provide encouraging feedback on:
1. Dashboard design and layout
2. Visualization type appropriateness
3. Data storytelling effectiveness
4. Professional presentation quality
5. Areas for improvement

Be specific and pedagogical.
Score: 0-37.5 points
```

**visual_design.txt** (Vision AI)
```
Analyze this Tableau dashboard screenshot for:
1. Layout and composition
2. Color scheme effectiveness
3. Chart type appropriateness
4. Visual hierarchy
5. Accessibility considerations
6. Professional polish

Provide constructive design feedback.
```

---

## UI Integration

### Streamlit Interface Extensions

**New Assignment Type Selector**:
```python
assignment_type = st.selectbox(
    "Assignment Type",
    ["R Notebook", "Python Notebook", "Tableau Workbook", "Mixed (Tableau + PDF)"]
)

if assignment_type == "Tableau Workbook":
    twbx_file = st.file_uploader("Upload TWBX", type=['twbx'])
    
    if st.checkbox("Include written component"):
        pdf_file = st.file_uploader("Upload PDF answers", type=['pdf'])
```

**Grading Display**:
```python
# Show Tableau-specific results
st.subheader("📊 Workbook Analysis")
st.json(workbook_analysis)

st.subheader("✅ Component Checklist")
for component, status in component_check.items():
    st.write(f"{status['icon']} {component}: {status['message']}")

st.subheader("🧮 Calculated Fields")
for calc in calculated_fields:
    with st.expander(calc['name']):
        st.code(calc['formula'])
        st.write(calc['validation'])
```

---

## Report Generation

### PDF Report Extensions

**Tableau-Specific Sections**:
1. **Workbook Summary**
   - Number of worksheets/dashboards
   - Calculated fields used
   - Data sources

2. **Technical Validation**
   - Component checklist
   - Requirement compliance
   - Calculation review

3. **Design Feedback**
   - Dashboard layout assessment
   - Visualization choices
   - Professional presentation

4. **Visual Analysis** (if enabled)
   - Screenshot annotations
   - Design recommendations
   - Accessibility notes

5. **Written Responses** (if included)
   - Question-by-question feedback
   - Business insight evaluation

---

## Implementation Phases

### ✅ Phase 1: Core Parsing (COMPLETE)
- [x] TWBX extraction
- [x] TWB XML parsing
- [x] Workbook analysis
- [x] Technical validation
- [x] Basic grading logic

### 🚧 Phase 2: AI Integration (NEXT)
- [ ] Integrate with existing Qwen/GPT-OSS servers
- [ ] Create Tableau-specific prompts
- [ ] Parallel grading workflow
- [ ] Score aggregation

### 📋 Phase 3: Vision Analysis
- [ ] Screenshot extraction from TWBX
- [ ] GPT-4 Vision integration
- [ ] Visual design scoring
- [ ] Accessibility checks

### 📋 Phase 4: Document Parsing
- [ ] PDF text extraction
- [ ] DOCX parsing
- [ ] Question-answer matching
- [ ] Written response grading

### 📋 Phase 5: UI Integration
- [ ] Streamlit interface updates
- [ ] Assignment type selector
- [ ] Tableau-specific displays
- [ ] Report generation

### 📋 Phase 6: Database & Storage
- [ ] Schema extensions
- [ ] Submission handling
- [ ] Result storage
- [ ] Historical tracking

---

## Testing Strategy

### Unit Tests
```python
# test_tableau_parser.py
def test_extract_workbook()
def test_parse_worksheets()
def test_parse_calculations()
def test_parse_dashboards()

# test_tableau_grader.py
def test_component_validation()
def test_minimum_requirements()
def test_calculation_validation()
def test_scoring_logic()
```

### Integration Tests
```python
# test_tableau_integration.py
def test_end_to_end_grading()
def test_ai_prompt_generation()
def test_parallel_execution()
def test_report_generation()
```

### Sample Assignments
- Create 3-5 sample Tableau workbooks
- Include correct and incorrect examples
- Test edge cases (missing components, errors)
- Validate scoring accuracy

---

## Performance Considerations

### Optimization Strategies

1. **TWBX Extraction**
   - Cache extracted files
   - Reuse parsed XML
   - Clean up temp files

2. **AI Processing**
   - Parallel execution (existing)
   - Batch multiple submissions
   - Thermal management (existing)

3. **Vision Analysis**
   - Only when required
   - Batch image processing
   - Cache results

4. **Document Parsing**
   - Lazy loading
   - Incremental processing
   - Text extraction caching

### Expected Performance

- **TWBX Parsing**: ~2-5 seconds
- **Technical Validation**: ~1-2 seconds
- **AI Grading**: ~50 seconds (parallel, existing)
- **Vision Analysis**: ~10-15 seconds per image
- **Document Parsing**: ~5-10 seconds
- **Total**: ~70-90 seconds per submission

---

## Security & Privacy

### Data Protection
- TWBX files stored locally only
- No external API calls (except vision if needed)
- Student data anonymized
- Temp files cleaned up

### File Validation
- Verify TWBX format
- Scan for malicious content
- Size limits (< 50MB)
- Timeout protection

---

## Future Enhancements

### Advanced Features
- **Plagiarism Detection**: Compare workbook structures
- **Performance Analysis**: Query optimization suggestions
- **Interactivity Check**: Validate filters and parameters
- **Data Quality**: Check for data issues
- **Version Tracking**: Compare submission iterations
- **Peer Comparison**: Anonymous benchmarking

### AI Improvements
- **Custom Vision Models**: Train on Tableau dashboards
- **Formula Validation**: Advanced calculation checking
- **Design Patterns**: Recognize best practices
- **Automated Suggestions**: Generate improvement code

---

## Troubleshooting

### Common Issues

**TWBX won't extract**
- Check file corruption
- Verify ZIP format
- Check permissions

**Missing components not detected**
- Verify assignment config
- Check worksheet/dashboard names (case-sensitive)
- Review XML structure

**AI grading timeout**
- Reduce prompt size
- Skip vision analysis
- Process in smaller batches

**Vision analysis fails**
- Check image extraction
- Verify API credentials
- Fall back to text-only grading

---

## Documentation

### For Instructors
- Assignment configuration guide
- Rubric creation templates
- Sample assignments
- Grading workflow tutorial

### For Students
- Submission guidelines
- File naming conventions
- Required components checklist
- Common mistakes guide

---

*Last Updated: October 6, 2025*
*Status: Phase 1 Complete, Phase 2 In Progress*
*Version: 1.0*
