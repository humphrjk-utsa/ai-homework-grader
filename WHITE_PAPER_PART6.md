## 7. Discussion

### 7.1 Advantages of Hybrid Approach

**Rule-based Validation (Layers 1-2)**:
- ✅ Objective and consistent
- ✅ Fast execution (<5 seconds)
- ✅ Transparent scoring
- ✅ No hallucination risk
- ❌ Limited to predefined checks
- ❌ Cannot assess conceptual understanding

**AI-based Analysis (Layers 3-4)**:
- ✅ Flexible and adaptive
- ✅ Assesses conceptual understanding
- ✅ Generates rich feedback
- ✅ Identifies novel approaches
- ❌ Slower execution (30-45 seconds)
- ❌ Potential for inconsistency
- ❌ Requires careful prompt engineering

**Hybrid System**:
- ✅ Combines strengths of both approaches
- ✅ Objective scoring + rich feedback
- ✅ Fast validation + deep analysis
- ✅ Consistent + adaptive

### 7.2 Why Two Models?

**Single Large Model Approach**:
- One 120B model for everything
- Pros: Simpler architecture
- Cons: Slower (60-90s), less specialized

**Dual Specialized Models**:
- 30B coding model + 27B general model
- Pros: Faster (30-45s), better specialization
- Cons: More complex orchestration

**Empirical Comparison**:
| Approach | Time | Code Analysis Quality | Feedback Quality |
|----------|------|----------------------|------------------|
| Single 120B | 65s | Good | Excellent |
| Dual (30B+27B) | 35s | Excellent | Excellent |
| Single 30B | 25s | Excellent | Good |

**Conclusion**: Dual specialized models provide best balance of speed and quality.

### 7.3 Limitations and Future Work

**Current Limitations**:
1. **Language-specific**: Currently optimized for R
2. **Notebook-only**: Requires Jupyter notebook format
3. **Rubric dependency**: Requires well-defined rubrics
4. **Computational cost**: Requires powerful hardware

**Future Directions**:
1. **Multi-language support**: Python, SQL, Julia
2. **Adaptive rubrics**: AI-generated rubrics from assignment descriptions
3. **Student interaction**: Chatbot for clarification questions
4. **Continuous learning**: Model fine-tuning from instructor corrections
5. **Plagiarism detection**: Code similarity analysis
6. **Real-time feedback**: Grade as students work



### 7.4 Ethical Considerations

**Transparency**:
- Students informed that AI assists grading
- Rubrics and criteria clearly communicated
- Human instructor reviews edge cases

**Fairness**:
- Consistent application of rubric to all students
- No bias based on student identity
- Multiple valid approaches accepted

**Privacy**:
- Student data stored locally
- No external API calls (models run locally)
- Anonymization option for demos/research

**Human Oversight**:
- Instructor reviews all grades before release
- Manual adjustment capability
- Training data collection for improvement

**Academic Integrity**:
- System detects template code vs student work
- Flags suspiciously similar submissions
- Encourages original thinking through detailed feedback

