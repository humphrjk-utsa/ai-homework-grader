#!/usr/bin/env python3
"""
Corrected Logan Grading - Remove File Path Penalty
"""

import json
from comprehensive_logan_grader import extract_detailed_notebook_content, analyze_logan_responses
from report_generator import PDFReportGenerator

def create_corrected_analysis_result(student_responses):
    """Create corrected analysis result without file path penalties"""
    
    # Analyze Logan's specific responses
    response_analysis = analyze_logan_responses(student_responses)
    
    # Calculate element scores - CORRECTED (no path penalty)
    element_scores = {
        'working_directory': 2.0,  # Full points - code shows proper directory usage
        'package_loading': 4.0,    # Full points - properly loaded tidyverse and readxl
        'csv_import': 6.0,         # CORRECTED: Full points - absolute paths are acceptable
        'excel_import': 6.0,       # CORRECTED: Full points - absolute paths are acceptable
        'data_inspection': 6.0,    # Basic inspection, could be more thorough
        'reflection_questions': 8.0  # Minimal responses, needs more depth
    }
    
    total_score = sum(element_scores.values())
    max_score = 37.5
    
    # Create corrected detailed feedback
    detailed_feedback = [
        "■ Working Directory (2.0/2.0 points) ✅ Excellent: Logan properly checked the working directory and understood the file structure. The code execution shows good awareness of the workspace setup.",
        
        "■ Package Loading (4.0/4.0 points) ✅ Excellent: Successfully loaded both tidyverse and readxl packages without errors. Clean, professional approach to library management.",
        
        "■ CSV Import (6.0/6.0 points) ✅ Excellent: Successfully imported sales data using read_csv() with proper file paths. The absolute paths work correctly in the given environment and demonstrate understanding of file system navigation.",
        
        "■ Excel Import (6.0/6.0 points) ✅ Excellent: Correctly imported both sheets from the Excel file using appropriate sheet parameters. Demonstrates solid understanding of multi-sheet Excel handling with readxl package.",
        
        "■ Data Inspection (6.0/8.0 points) ⚠️ Satisfactory: Used head(), str(), and summary() functions appropriately. However, the analysis of results is quite basic. Logan correctly identifies data types and dimensions but misses opportunities for deeper insights about data quality, business implications, and analytical readiness.",
        
        "■ Reflection Questions (8.0/12.5 points) ❌ Needs Work: Logan's written responses are very brief and lack the depth expected for university-level work. For example, responses like 'there are 3 number variables, 2 character variables, and a date variable' are factually correct but too simplistic. What I'm looking for: Detailed discussion of specific data quality issues, their potential business impact, how they might affect analysis, and thoughtful consideration of data preprocessing needs. Each reflection should be 2-3 sentences minimum with specific examples and business context."
    ]
    
    # Updated code issues (removed file path issue)
    code_issues = [
        "Limited Data Quality Assessment: Missing checks for duplicates, outliers, or data consistency",
        "Minimal Documentation: Code lacks comments explaining the analytical purpose of each step",
        "Basic Analysis: Could benefit from more comprehensive exploration techniques"
    ]
    
    # Updated code fixes (removed file path section)
    code_fixes = [
        """🔧 **Enhanced Data Quality Assessment**

Add more comprehensive data quality checks to your analysis:

```r
# Check for missing values by column
colSums(is.na(sales_df))
colSums(is.na(ratings_df))
colSums(is.na(comments_df))

# Check for duplicates
sum(duplicated(sales_df))

# Look for outliers in numeric columns
boxplot(sales_df$Amount, main="Sales Amount Distribution")
summary(sales_df$Amount)

# Check unique values in categorical columns
table(sales_df$Region)
table(sales_df$Product)

# Check data ranges and consistency
range(sales_df$Date)
range(ratings_df$ProductRating)
```

🔧 **Improved Data Exploration**

Expand your analysis to uncover business insights:

```r
# Calculate key business metrics
sales_by_region <- sales_df %>%
  group_by(Region) %>%
  summarise(
    total_sales = sum(Amount),
    avg_transaction = mean(Amount),
    transaction_count = n()
  )

# Examine rating distributions
ratings_summary <- ratings_df %>%
  summarise(
    avg_product_rating = mean(ProductRating),
    avg_service_rating = mean(ServiceRating),
    avg_satisfaction = mean(OverallSatisfaction)
  )

print(sales_by_region)
print(ratings_summary)
```

🔧 **Better Documentation and Comments**

Add analytical context to your code:

```r
# Load required packages for data analysis
library(tidyverse)  # For data manipulation and visualization
library(readxl)     # For reading Excel files

# Import sales transaction data for business analysis
sales_df <- read_csv("/workspaces/assignment-1-logan3941/data/sales_data.csv")
print("Sales data imported successfully!")

# Perform initial data exploration to understand business context
head(sales_df, 10)  # View sample transactions
str(sales_df)       # Understand data structure for analysis planning
summary(sales_df)   # Get statistical overview of business metrics
```"""
    ]
    
    # Updated overall assessment
    overall_assessment = """Logan demonstrates solid foundational skills in R programming and data management. The technical execution is clean and functional, showing good understanding of data import and exploration techniques. The code runs successfully and accomplishes all required tasks effectively.

**Strengths:**
• Clean, executable code that accomplishes all technical requirements
• Proper use of tidyverse and readxl packages
• Successful data import from multiple sources (CSV and Excel)
• Systematic approach to data exploration using appropriate R functions
• Accurate identification of basic data characteristics

**Areas for Development:**
• Written analysis lacks depth and business context
• Reflection responses are too brief for university-level work
• Missing discussion of data quality implications for business decisions
• Could benefit from more comprehensive data exploration techniques

**Recommendations:**
• Practice writing more detailed analytical observations (aim for 2-3 sentences per insight)
• Connect technical findings to business implications (e.g., "What do missing values mean for business decisions?")
• Explore additional data quality assessment techniques
• Develop habits around comprehensive data exploration

Logan shows strong technical competency and with more attention to analytical depth and communication, will excel in future assignments. The foundation is solid - now focus on building analytical thinking skills."""
    
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
    """Generate corrected grading for Logan"""
    
    print("🔧 Corrected Logan Balfour Grading")
    print("=" * 50)
    print("📝 Removing file path penalty - absolute paths are acceptable")
    
    # Extract content from notebook
    notebook_path = "homework_grader/Balfour_Logan_homework_lesson_1.ipynb"
    student_code, student_markdown, student_responses = extract_detailed_notebook_content(notebook_path)
    
    # Create corrected analysis
    corrected_result = create_corrected_analysis_result(student_responses)
    
    # Display corrected results
    print("\n" + "="*60)
    print("🎉 CORRECTED GRADING RESULTS")
    print("="*60)
    
    print(f"📊 Final Score: {corrected_result['total_score']:.1f}/{corrected_result['max_score']} points")
    percentage = (corrected_result['total_score'] / corrected_result['max_score']) * 100
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
    
    print("\n📋 CORRECTED ELEMENT BREAKDOWN:")
    for element, score in corrected_result['element_scores'].items():
        element_name = element.replace('_', ' ').title()
        max_scores = {
            'working_directory': 2.0,
            'package_loading': 4.0,
            'csv_import': 6.0,
            'excel_import': 6.0,
            'data_inspection': 8.0,
            'reflection_questions': 12.5
        }
        max_score = max_scores.get(element, 5.0)
        percentage = (score / max_score) * 100
        status = "✅" if percentage >= 90 else "⚠️" if percentage >= 70 else "❌"
        print(f"  {status} {element_name}: {score:.1f}/{max_score} points ({percentage:.0f}%)")
    
    print(f"\n📈 SCORE CHANGE:")
    print(f"  • Previous: 31.0/37.5 (82.7%) - B")
    print(f"  • Corrected: {corrected_result['total_score']:.1f}/37.5 ({percentage:.1f}%) - {letter_grade}")
    print(f"  • Improvement: +{corrected_result['total_score'] - 31.0:.1f} points")
    
    # Generate corrected PDF report
    print("\n📄 Generating Corrected PDF Report...")
    report_generator = PDFReportGenerator()
    
    pdf_path = report_generator.generate_report(
        student_name="Logan Balfour",
        assignment_id="Assignment_1_Intro_to_R_CORRECTED",
        analysis_result=corrected_result
    )
    
    print(f"✅ Corrected PDF Report generated: {pdf_path}")
    
    # Save corrected results
    with open('homework_grader/logan_corrected_results.json', 'w') as f:
        json.dump({
            'corrected_analysis': corrected_result,
            'student_responses': student_responses,
            'correction_notes': 'Removed file path penalty - absolute paths are acceptable in this context'
        }, f, indent=2, default=str)
    
    print(f"💾 Corrected results saved to: logan_corrected_results.json")
    
    return corrected_result

if __name__ == "__main__":
    main()