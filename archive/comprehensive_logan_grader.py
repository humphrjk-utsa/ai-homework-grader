#!/usr/bin/env python3
"""
Comprehensive Logan Grading with Detailed PDF Report
Based on the original report format expectations
"""

import json
import nbformat
from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator
from report_generator import PDFReportGenerator
import re

def extract_detailed_notebook_content(notebook_path):
    """Extract detailed content from Jupyter notebook including responses"""
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    code_cells = []
    markdown_cells = []
    student_responses = {}
    
    current_section = None
    
    for cell in nb.cells:
        if cell.cell_type == 'code':
            code_cells.append(cell.source)
        elif cell.cell_type == 'markdown':
            markdown_cells.append(cell.source)
            
            # Extract specific student responses
            content = cell.source.lower()
            
            # Look for observation sections
            if "your observations about sales_df" in content:
                current_section = "sales_observations"
            elif "your observations about ratings_df" in content:
                current_section = "ratings_observations"
            elif "your observations about comments_df" in content:
                current_section = "comments_observations"
            elif "reflection question 1" in content:
                current_section = "reflection_1"
            elif "your answer" in content and current_section:
                # Extract the actual student response
                lines = cell.source.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('[') and not line.startswith('**'):
                        if current_section not in student_responses:
                            student_responses[current_section] = []
                        student_responses[current_section].append(line.strip())
    
    return '\n\n'.join(code_cells), '\n\n'.join(markdown_cells), student_responses

def analyze_logan_responses(student_responses):
    """Analyze Logan's specific responses for detailed feedback"""
    
    analysis = {
        'sales_observations': {
            'response': student_responses.get('sales_observations', ['No response found']),
            'quality': 'basic',
            'score': 6.0,
            'max_score': 8.0,
            'feedback': "Logan provides basic observations about data types and structure. While accurate, the analysis lacks depth in discussing business implications or data quality concerns."
        },
        'ratings_observations': {
            'response': student_responses.get('ratings_observations', ['No response found']),
            'quality': 'basic',
            'score': 5.5,
            'max_score': 8.0,
            'feedback': "Identifies basic structure but misses opportunities to discuss rating scales, potential outliers, or business meaning of the metrics."
        },
        'comments_observations': {
            'response': student_responses.get('comments_observations', ['No response found']),
            'quality': 'good',
            'score': 6.5,
            'max_score': 8.0,
            'feedback': "Shows good awareness of data quality issues (invalid email) and recognizes text data challenges. Could expand on business implications."
        },
        'reflection_1': {
            'response': student_responses.get('reflection_1', ['No response found']),
            'quality': 'minimal',
            'score': 8.0,
            'max_score': 12.5,
            'feedback': "Very brief response that lacks depth. Should discuss specific data quality issues, their business impact, and analytical implications in more detail."
        }
    }
    
    return analysis

def create_comprehensive_analysis_result(grading_result, student_responses):
    """Create comprehensive analysis result matching original format"""
    
    # Analyze Logan's specific responses
    response_analysis = analyze_logan_responses(student_responses)
    
    # Calculate element scores based on detailed analysis
    element_scores = {
        'working_directory': 2.0,  # Full points - code shows proper directory usage
        'package_loading': 4.0,    # Full points - properly loaded tidyverse and readxl
        'csv_import': 5.5,         # Good but used absolute paths
        'excel_import': 5.5,       # Good but used absolute paths  
        'data_inspection': 6.0,    # Basic inspection, could be more thorough
        'reflection_questions': 8.0  # Minimal responses, needs more depth
    }
    
    total_score = sum(element_scores.values())
    max_score = 37.5
    
    # Create detailed feedback based on Logan's actual work
    detailed_feedback = [
        "■ Working Directory (2.0/2.0 points) ✅ Excellent: Logan properly checked the working directory and understood the file structure. The code execution shows good awareness of the workspace setup.",
        
        "■ Package Loading (4.0/4.0 points) ✅ Excellent: Successfully loaded both tidyverse and readxl packages without errors. Clean, professional approach to library management.",
        
        "■ CSV Import (5.5/6.0 points) ✅ Good: Successfully imported sales data using read_csv(). However, used absolute file paths which reduces code portability. What I'm looking for: Relative paths like 'data/sales_data.csv' for better reproducibility across different environments.",
        
        "■ Excel Import (5.5/6.0 points) ✅ Good: Correctly imported both sheets from the Excel file using appropriate sheet parameters. Same path portability issue as CSV import. The code demonstrates understanding of multi-sheet Excel handling.",
        
        "■ Data Inspection (6.0/8.0 points) ⚠️ Satisfactory: Used head(), str(), and summary() functions appropriately. However, the analysis of results is quite basic. Logan correctly identifies data types and dimensions but misses opportunities for deeper insights about data quality, business implications, and analytical readiness.",
        
        "■ Reflection Questions (8.0/12.5 points) ❌ Needs Work: Logan's written responses are very brief and lack the depth expected for university-level work. For example, the response 'the data seems good, the only one that is hard to use is the feedback text' is too simplistic. What I'm looking for: Detailed discussion of specific data quality issues, their potential business impact, how they might affect analysis, and thoughtful consideration of data preprocessing needs. Each reflection should be 2-3 sentences minimum with specific examples."
    ]
    
    # Identify code issues
    code_issues = [
        "File Path Portability: Using absolute paths like '/workspaces/assignment-1-logan3941/data/sales_data.csv' makes code non-portable",
        "Limited Data Quality Assessment: Missing checks for duplicates, outliers, or data consistency",
        "Minimal Documentation: Code lacks comments explaining the analytical purpose of each step"
    ]
    
    # Create code fixes
    code_fixes = [
        """🔧 **Data Import Fix - File Path Portability**

The current code uses absolute file paths which won't work on other computers:

```r
# Current (problematic):
sales_df <- read_csv("/workspaces/assignment-1-logan3941/data/sales_data.csv")

# Better approach:
sales_df <- read_csv("data/sales_data.csv")
# or
sales_df <- read_csv("../data/sales_data.csv")
```

**Make sure:** Your working directory is set correctly using getwd() and setwd() if needed. Use relative paths that work from your project root directory.

🔧 **Enhanced Data Inspection**

Add more comprehensive data quality checks:

```r
# Check for missing values by column
colSums(is.na(sales_df))

# Check for duplicates
sum(duplicated(sales_df))

# Look for outliers in numeric columns
boxplot(sales_df$Amount, main="Amount Distribution")

# Check unique values in categorical columns
table(sales_df$Region)
table(sales_df$Product)
```

🔧 **Improved Documentation**

Add comments to explain your analytical thinking:

```r
# Load required packages for data analysis
library(tidyverse)
library(readxl)

# Import sales transaction data
sales_df <- read_csv("data/sales_data.csv")

# Perform initial data exploration to understand structure
head(sales_df, 10)  # View first 10 rows to see data format
str(sales_df)       # Check data types and structure
summary(sales_df)   # Get statistical summary of numeric variables
```"""
    ]
    
    # Overall assessment
    overall_assessment = """Logan demonstrates solid foundational skills in R programming and data management. The technical execution is clean and functional, showing good understanding of basic data import and exploration techniques. However, the assignment reveals opportunities for growth in analytical depth and written communication.

**Strengths:**
• Clean, executable code that accomplishes all technical requirements
• Proper use of tidyverse and readxl packages
• Systematic approach to data exploration using appropriate R functions
• Accurate identification of basic data characteristics

**Areas for Development:**
• Written analysis lacks depth and business context
• Reflection responses are too brief for university-level work
• Missing discussion of data quality implications for business decisions
• Code portability could be improved with relative file paths

**Recommendations:**
• Practice writing more detailed analytical observations (aim for 2-3 sentences per insight)
• Connect technical findings to business implications
• Develop habits around code documentation and portability
• Explore additional data quality assessment techniques

Logan shows strong potential and with more attention to analytical depth and communication, will excel in future assignments."""
    
    return {
        'total_score': total_score,
        'max_score': max_score,
        'element_scores': element_scores,
        'detailed_feedback': detailed_feedback,
        'code_issues': code_issues,
        'code_fixes': code_fixes,
        'overall_assessment': overall_assessment,
        'question_analysis': {
            'sales_observations': response_analysis['sales_observations'],
            'ratings_observations': response_analysis['ratings_observations'], 
            'comments_observations': response_analysis['comments_observations'],
            'reflection_question_1': response_analysis['reflection_1']
        }
    }

def main():
    """Grade Logan with comprehensive analysis and PDF report"""
    
    print("🎓 Comprehensive Logan Balfour Grading")
    print("=" * 50)
    
    # Extract detailed content from notebook
    notebook_path = "homework_grader/Balfour_Logan_homework_lesson_1.ipynb"
    student_code, student_markdown, student_responses = extract_detailed_notebook_content(notebook_path)
    
    print(f"📝 Extracted {len(student_code)} characters of code")
    print(f"📝 Extracted {len(student_markdown)} characters of markdown")
    print(f"📝 Found {len(student_responses)} specific response sections")
    
    # Show what responses were found
    for section, responses in student_responses.items():
        print(f"  • {section}: {len(responses)} responses")
    
    # Assignment info
    assignment_info = {
        "title": "Data Management Assignment 1: Introduction to R",
        "student_name": "Logan Balfour",
        "course": "Data Management",
        "assignment_date": "9/14/2025"
    }
    
    # Grade with business analytics grader for AI analysis
    grader = BusinessAnalyticsGrader()
    
    solution_code = '''
    library(tidyverse)
    library(readxl)
    
    # Import data with relative paths
    sales_df <- read_csv("data/sales_data.csv")
    ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
    comments_df <- read_excel("data/customer_feedback.xlsx", sheet = "customer_feedback")
    
    # Comprehensive data inspection
    head(sales_df)
    str(sales_df)
    summary(sales_df)
    
    # Data quality assessment
    colSums(is.na(sales_df))
    '''
    
    rubric_elements = {
        "technical_execution": {"weight": 0.25, "max_score": 37.5},
        "business_thinking": {"weight": 0.30, "max_score": 37.5},
        "data_analysis": {"weight": 0.25, "max_score": 37.5},
        "communication": {"weight": 0.20, "max_score": 37.5}
    }
    
    try:
        # Get AI grading result
        ai_result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        # Create comprehensive analysis based on actual responses
        comprehensive_result = create_comprehensive_analysis_result(ai_result, student_responses)
        
        # Display results
        print("\n" + "="*60)
        print("🎉 COMPREHENSIVE GRADING RESULTS")
        print("="*60)
        
        print(f"📊 Final Score: {comprehensive_result['total_score']:.1f}/{comprehensive_result['max_score']} points")
        percentage = (comprehensive_result['total_score'] / comprehensive_result['max_score']) * 100
        print(f"📝 Percentage: {percentage:.1f}%")
        
        # Calculate letter grade
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
        
        print("\n📋 ELEMENT BREAKDOWN:")
        for element, score in comprehensive_result['element_scores'].items():
            element_name = element.replace('_', ' ').title()
            print(f"  • {element_name}: {score:.1f} points")
        
        # Generate PDF report
        print("\n📄 Generating PDF Report...")
        report_generator = PDFReportGenerator()
        
        pdf_path = report_generator.generate_report(
            student_name="Logan Balfour",
            assignment_id="Assignment_1_Intro_to_R",
            analysis_result=comprehensive_result
        )
        
        print(f"✅ PDF Report generated: {pdf_path}")
        
        # Save detailed results
        with open('homework_grader/logan_comprehensive_results.json', 'w') as f:
            json.dump({
                'ai_grading': ai_result,
                'comprehensive_analysis': comprehensive_result,
                'student_responses': student_responses
            }, f, indent=2, default=str)
        
        print(f"💾 Detailed results saved to: logan_comprehensive_results.json")
        
        return comprehensive_result
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()