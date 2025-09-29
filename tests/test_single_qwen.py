#!/usr/bin/env python3
"""
Test Single Qwen 3.0 Coder Grading System
"""

import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from single_qwen_grader import SingleQwenGrader
import nbformat

def extract_notebook_content(notebook_path):
    """Extract code and markdown from notebook"""
    try:
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
    except Exception as e:
        print(f"Error reading notebook: {e}")
        return "", ""

def test_single_qwen_submission():
    """Test Single Qwen with Deon's submission"""
    
    print("🧪 Testing Single Qwen 3.0 Coder with Deon's Assignment 1")
    print("=" * 60)
    
    # Path to Deon's submission
    notebook_path = "submissions/1/Deon_Schoeman_170956.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"❌ Notebook not found: {notebook_path}")
        return False
    
    # Extract content
    print("📖 Extracting notebook content...")
    student_code, student_markdown = extract_notebook_content(notebook_path)
    
    code_sections = len(student_code.split('\n\n'))
    markdown_sections = len(student_markdown.split('\n\n'))
    print(f"📊 Code cells: {code_sections} sections")
    print(f"📝 Markdown cells: {markdown_sections} sections")
    
    # Initialize single Qwen grader
    try:
        grader = SingleQwenGrader()
        print("✅ Single Qwen grader initialized")
    except Exception as e:
        print(f"❌ Failed to initialize grader: {e}")
        return False
    
    if not grader.is_available():
        print("❌ Qwen 3.0 Coder not available")
        return False
    
    print("✅ Qwen 3.0 Coder available")
    
    # Assignment 1 info
    assignment_info = {
        'title': 'Assignment 1: Introduction to R',
        'total_points': 37.5,
        'learning_objectives': [
            'Set up R environment and working directory',
            'Import and explore datasets using R functions',
            'Understand data types and structures in R',
            'Perform basic data quality assessment'
        ]
    }
    
    # Assignment 1 rubric elements
    rubric_elements = {
        'environment_setup': {
            'max_points': 7.5,
            'category': 'automated',
            'description': 'Working directory setup and package loading',
            'automated_checks': [
                'getwd() function used',
                'library() functions present',
                'Working directory correctly identified'
            ]
        },
        'data_import': {
            'max_points': 10,
            'category': 'automated',
            'description': 'Successful data import and initial exploration',
            'automated_checks': [
                'read_csv() or similar import functions',
                'head() function used',
                'str() function used',
                'summary() function used'
            ]
        },
        'data_exploration': {
            'max_points': 10,
            'category': 'manual',
            'description': 'Quality of data exploration and observations',
            'evaluation_criteria': [
                'Thorough examination of data structure',
                'Identification of data types',
                'Recognition of data quality issues',
                'Clear written observations'
            ]
        },
        'code_quality': {
            'max_points': 5,
            'category': 'manual',
            'description': 'Code organization and documentation',
            'evaluation_criteria': [
                'Clean, readable code',
                'Appropriate use of R functions',
                'Logical flow of analysis'
            ]
        },
        'written_responses': {
            'max_points': 5,
            'category': 'manual',
            'description': 'Quality of written analysis and responses',
            'evaluation_criteria': [
                'Clear communication of findings',
                'Understanding of data concepts',
                'Professional presentation'
            ]
        }
    }
    
    # Solution code
    solution_code = """
# Assignment 1 Solution Example
getwd()
library(readr)
library(dplyr)

# Import datasets
sales_df <- read_csv("data/sales_data.csv")
ratings_df <- read_csv("data/customer_ratings.csv") 
comments_df <- read_csv("data/customer_comments.csv")

# Explore each dataset
head(sales_df)
str(sales_df)
summary(sales_df)

head(ratings_df)
str(ratings_df)
summary(ratings_df)

head(comments_df)
str(comments_df)
summary(comments_df)
    """
    
    print("\n🚀 Running single Qwen grading...")
    start_time = time.time()
    
    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        end_time = time.time()
        
        print(f"\n✅ Grading completed in {end_time - start_time:.1f} seconds")
        print(f"📊 Score: {result['score']:.1f}/{result['max_score']} ({result['percentage']:.1f}%)")
        
        # Display performance stats
        if 'grading_stats' in result:
            stats = result['grading_stats']
            print(f"⏱️ Analysis Time: {stats['analysis_time']:.1f}s")
            print(f"⏱️ Total Time: {stats['total_time']:.1f}s")
        
        # Display detailed feedback
        print("\n📝 Detailed Feedback:")
        print("=" * 50)
        feedback = result.get('feedback', [])
        for line in feedback:
            print(line)
        
        # Display element scores
        if 'element_scores' in result:
            print("\n📊 Element Scores:")
            print("=" * 30)
            for element, score in result['element_scores'].items():
                max_score = rubric_elements.get(element, {}).get('max_points', 0)
                print(f"  {element}: {score:.1f}/{max_score}")
        
        # Generate PDF report
        print("\n📄 Generating PDF report...")
        try:
            from two_model_report_generator import generate_two_model_pdf_report
            
            pdf_path = generate_two_model_pdf_report(
                student_name="Deon Schoeman",
                assignment_info=assignment_info,
                grading_result=result,
                output_dir="reports"
            )
            
            print(f"✅ PDF report generated: {pdf_path}")
            
        except Exception as pdf_error:
            print(f"⚠️ PDF generation failed: {pdf_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_qwen_submission()
    
    if success:
        print("\n🎉 Single Qwen grading test completed!")
        print("\n📋 Key Benefits:")
        print("• Single model - faster processing")
        print("• Qwen 3.0 Coder - excellent code analysis")
        print("• Comprehensive feedback - technical + educational")
        print("• Business-focused approach")
        print("• Professional PDF report")
    else:
        print("\n❌ Single Qwen test failed.")
        
    print("\n📈 Expected Performance:")
    print("• Single model should be much faster than two-model")
    print("• Target: 60-120 seconds per submission")
    print("• Quality: Comprehensive analysis from specialized coder model")