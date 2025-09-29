#!/usr/bin/env python3
"""
Grade Logan Balfour's Assignment
"""

import json
import nbformat
from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator

def extract_notebook_content(notebook_path):
    """Extract code and markdown from Jupyter notebook"""
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    code_cells = []
    markdown_cells = []
    
    for cell in nb.cells:
        if cell.cell_type == 'code':
            code_cells.append(cell.source)
        elif cell.cell_type == 'markdown':
            markdown_cells.append(cell.source)
    
    return '\n\n'.join(code_cells), '\n\n'.join(markdown_cells)

def main():
    """Grade Logan's assignment"""
    
    print("🎓 Grading Logan Balfour's Assignment")
    print("=" * 50)
    
    # Extract content from notebook
    notebook_path = "homework_grader/Balfour_Logan_homework_lesson_1.ipynb"
    student_code, student_markdown = extract_notebook_content(notebook_path)
    
    print(f"📝 Extracted {len(student_code)} characters of code")
    print(f"📝 Extracted {len(student_markdown)} characters of markdown")
    
    # Assignment info
    assignment_info = {
        "title": "Data Management Assignment 1: Introduction to R",
        "student_name": "Logan Balfour",
        "course": "Data Management",
        "assignment_date": "9/14/2025"
    }
    
    # Rubric elements
    rubric_elements = {
        "technical_execution": {"weight": 0.25, "max_score": 37.5},
        "business_thinking": {"weight": 0.30, "max_score": 37.5},
        "data_analysis": {"weight": 0.25, "max_score": 37.5},
        "communication": {"weight": 0.20, "max_score": 37.5}
    }
    
    # Solution code (basic reference)
    solution_code = '''
    library(tidyverse)
    library(readxl)
    
    # Import data
    sales_df <- read_csv("data/sales_data.csv")
    ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
    comments_df <- read_excel("data/customer_feedback.xlsx", sheet = "customer_feedback")
    
    # Data inspection
    head(sales_df)
    str(sales_df)
    summary(sales_df)
    '''
    
    # Initialize grader
    grader = BusinessAnalyticsGrader()
    
    # Grade the assignment
    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        # Validate the result
        validator = GradingValidator()
        is_valid, errors = validator.validate_grading_result(result)
        
        if not is_valid:
            print("⚠️ Validation errors found, attempting to fix...")
            result = validator.fix_calculation_errors(result)
            is_valid, errors = validator.validate_grading_result(result)
        
        # Display results
        print("\n" + "="*60)
        print("🎉 GRADING RESULTS FOR LOGAN BALFOUR")
        print("="*60)
        
        print(f"📊 Final Score: {result['final_score']}/37.5 ({result['final_score_percentage']:.1f}%)")
        
        # Calculate letter grade
        percentage = result['final_score_percentage']
        if percentage >= 97:
            letter_grade = "A+"
        elif percentage >= 93:
            letter_grade = "A"
        elif percentage >= 90:
            letter_grade = "A-"
        elif percentage >= 87:
            letter_grade = "B+"
        elif percentage >= 83:
            letter_grade = "B"
        elif percentage >= 80:
            letter_grade = "B-"
        else:
            letter_grade = "C+"
        
        print(f"📝 Letter Grade: {letter_grade}")
        print(f"✅ Validation Status: {'Valid' if is_valid else 'Invalid'}")
        
        print("\n📋 COMPONENT BREAKDOWN:")
        component_scores = result['component_scores']
        print(f"  • Technical Execution (25%): {component_scores['technical_points']}/9.375")
        print(f"  • Business Thinking (30%): {component_scores['business_points']}/11.25")
        print(f"  • Data Analysis (25%): {component_scores['analysis_points']}/9.375")
        print(f"  • Communication (20%): {component_scores['communication_points']}/7.5")
        print(f"  • Bonus Points: {component_scores['bonus_points']}/0.0")
        
        print("\n📊 COMPONENT PERCENTAGES:")
        component_percentages = result['component_percentages']
        print(f"  • Technical Score: {component_percentages['technical_score']}%")
        print(f"  • Business Understanding: {component_percentages['business_understanding']}%")
        print(f"  • Data Interpretation: {component_percentages['data_interpretation']}%")
        print(f"  • Communication Clarity: {component_percentages['communication_clarity']}%")
        
        # Show detailed feedback
        feedback = result.get('comprehensive_feedback', {})
        if 'instructor_comments' in feedback:
            print("\n💬 INSTRUCTOR COMMENTS:")
            print("-" * 40)
            print(feedback['instructor_comments'])
        
        # Save results to file
        with open('homework_grader/logan_grading_results.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Full results saved to: logan_grading_results.json")
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        return None
    
    return result

if __name__ == "__main__":
    main()