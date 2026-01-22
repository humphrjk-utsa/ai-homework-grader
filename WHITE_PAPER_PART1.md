# A Hybrid Validation and Dual-LLM System for Automated Homework Grading in Business Analytics Education

**Authors**: [Your Name/Institution]  
**Date**: January 2025  
**Version**: 1.0

---

## Abstract

We present a novel automated grading system that combines rule-based validation with parallel dual-LLM orchestration to grade business analytics homework assignments. Our system employs a 4-layer validation architecture: (1) systematic validation of code structure and completeness, (2) smart output comparison against reference solutions, (3) technical code analysis using a specialized coding LLM, and (4) comprehensive feedback generation using a general-purpose LLM. By executing layers 3 and 4 in parallel, we achieve a 2x speedup while maintaining high accuracy and generating detailed, pedagogically sound feedback. The system has been deployed in production for business analytics courses, processing hundreds of student submissions with consistent, fair, and detailed grading.

**Keywords**: Automated grading, Large Language Models, Educational technology, Business analytics, Parallel processing, Hybrid validation

---

## 1. Introduction

### 1.1 Motivation

Grading programming assignments in business analytics courses presents unique challenges:
- **Scale**: Large class sizes (50-200 students) require significant grading time
- **Complexity**: Assignments combine code quality, statistical correctness, and business interpretation
- **Consistency**: Multiple graders or fatigue can lead to inconsistent evaluation
- **Feedback Quality**: Students need detailed, actionable feedback for learning

Traditional automated grading systems rely on test cases or simple pattern matching, which fail to capture the nuanced requirements of business analytics assignments that require both technical proficiency and conceptual understanding.

### 1.2 Contributions

This paper presents:
1. A **4-layer hybrid validation architecture** combining rule-based and AI-based grading
2. A **parallel dual-LLM orchestration** system for efficient, specialized analysis
3. **Production deployment results** from real business analytics courses
4. **Open-source implementation** for reproducibility and adoption


---

## 2. System Architecture

### 2.1 Overview

Our system processes student submissions through four sequential validation layers, with the final two layers executing in parallel for efficiency:

```
Layer 1: Systematic Validation (Rule-based)
    ↓
Layer 2: Smart Output Validation (Comparison-based)
    ↓
    ├─→ Layer 3: Technical Analysis (Qwen 3.0 Coder)
    └─→ Layer 4: Feedback Generation (Gemma 3.0)
    ↓
Result Merging & Structuring
```

### 2.2 Layer 1: Systematic Validation

**Purpose**: Verify structural completeness and execution

**Implementation**: `validators/rubric_driven_validator.py`

**Checks**:
- Required variables present in code
- Assignment sections completed
- Code execution rate (% of cells with outputs)
- Rubric-defined requirements met

**Output**: Base score (0-100) + completion metrics

**Algorithm**:
```python
def validate_notebook(notebook_path):
    # 1. Parse notebook and extract code
    # 2. Check for required variables
    # 3. Validate section completion
    # 4. Calculate execution rate
    # 5. Compute base score from rubric
    return {
        'base_score': float,
        'variable_check': dict,
        'section_breakdown': dict,
        'cell_stats': dict
    }
```

