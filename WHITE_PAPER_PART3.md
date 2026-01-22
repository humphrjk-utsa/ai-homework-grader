## 4. Parallel LLM Orchestration

### 4.1 Motivation for Parallelization

Sequential execution of two LLM calls results in:
- **Qwen Analysis**: 20-30 seconds
- **Gemma Feedback**: 25-35 seconds
- **Total Sequential**: 45-65 seconds

Parallel execution achieves:
- **Both Models**: max(20-30, 25-35) = 25-35 seconds
- **Speedup**: ~2x faster
- **Throughput**: 2x more submissions per hour

### 4.2 Implementation

**Technology**: Python `concurrent.futures.ThreadPoolExecutor`

**Code**:
```python
class BusinessAnalyticsGraderV2:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def grade_submission(self, student_code, student_markdown, ...):
        # Submit both tasks simultaneously
        future_code = self.executor.submit(
            self._analyze_code, 
            student_code, template_code, solution_code
        )
        
        future_feedback = self.executor.submit(
            self._generate_feedback,
            student_code, student_markdown
        )
        
        # Wait for both to complete
        code_analysis = future_code.result()
        comprehensive_feedback = future_feedback.result()
        
        # Merge results
        return self._merge_results(code_analysis, comprehensive_feedback)
```

### 4.3 Prompt Engineering

#### Qwen Code Analysis Prompt Structure
```
ROLE: Expert code reviewer and technical analyst

CONTEXT:
- Assignment: {assignment_name}
- Template code: {template_code}
- Student code: {student_code}
- Solution code: {solution_code}
- Validation results: {validation_summary}

TASK:
Analyze the student's code for:
1. Technical correctness
2. Code quality and organization
3. Best practices adherence
4. Algorithm efficiency
5. Specific strengths and improvements

OUTPUT FORMAT: JSON
{
    "code_strengths": [list],
    "code_suggestions": [list],
    "technical_observations": [list]
}
```



#### Gemma Feedback Generation Prompt Structure
```
ROLE: Experienced business analytics instructor

CONTEXT:
- Assignment: {assignment_name}
- Student markdown: {student_markdown}
- Code summary: {student_code_summary}
- Rubric: {rubric_criteria}
- Validation results: {validation_summary}

TASK:
Generate comprehensive, pedagogically sound feedback:
1. Overall assessment (instructor comments)
2. Reflection & critical thinking evaluation
3. Analytical strengths identification
4. Business application assessment
5. Areas for development
6. Specific recommendations

OUTPUT FORMAT: JSON
{
    "instructor_comments": string,
    "detailed_feedback": {
        "reflection_assessment": [list],
        "analytical_strengths": [list],
        "business_application": [list],
        "areas_for_development": [list],
        "recommendations": [list]
    }
}
```

### 4.4 Result Merging Strategy

After both models complete, results are merged:

1. **Validation Score** (Layers 1-2): Base score from rule-based checks
2. **Technical Analysis** (Layer 3): Code quality insights from Qwen
3. **Comprehensive Feedback** (Layer 4): Pedagogical feedback from Gemma
4. **Final Score**: Validation score (primary) + AI adjustments (minor)

**Rationale**: Rule-based validation provides objective, consistent scoring. AI provides rich, contextual feedback without introducing scoring variability.

