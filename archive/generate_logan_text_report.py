#!/usr/bin/env python3
"""
Generate a comprehensive text-based report for Logan Balfour
"""

import json
from datetime import datetime

def generate_text_report():
    """Generate a comprehensive text report for Logan"""
    
    # Load the corrected results
    try:
        with open('homework_grader/logan_corrected_results.json', 'r') as f:
            data = json.load(f)
        corrected_result = data['corrected_analysis']
    except FileNotFoundError:
        print("❌ Corrected results not found. Please run corrected_logan_grader.py first.")
        return
    
    # Generate report content
    report_content = f"""
================================================================================
                        HOMEWORK GRADING REPORT
================================================================================

Student Name:           Logan Balfour
Assignment:             Data Management Assignment 1: Introduction to R
Graded On:              {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Final Score:            {corrected_result['total_score']:.1f} / {corrected_result['max_score']} points ({(corrected_result['total_score']/corrected_result['max_score']*100):.1f}%)

================================================================================
                              SCORE SUMMARY
================================================================================

Overall Performance: Good ({(corrected_result['total_score']/corrected_result['max_score']*100):.1f}%)

Component Scores:
• Working Directory: {corrected_result['element_scores']['working_directory']:.1f} points
• Package Loading: {corrected_result['element_scores']['package_loading']:.1f} points
• CSV Import: {corrected_result['element_scores']['csv_import']:.1f} points
• Excel Import: {corrected_result['element_scores']['excel_import']:.1f} points
• Data Inspection: {corrected_result['element_scores']['data_inspection']:.1f} points
• Reflection Questions: {corrected_result['element_scores']['reflection_questions']:.1f} points

================================================================================
                        PERFORMANCE BY CATEGORY
================================================================================

✅ Excellent Working Directory: 2.0/2.0 points (100%)
✅ Excellent Package Loading: 4.0/4.0 points (100%)
✅ Excellent CSV Import: 6.0/6.0 points (100%)
✅ Excellent Excel Import: 6.0/6.0 points (100%)
⚠️ Satisfactory Data Inspection: 6.0/8.0 points (75%)
❌ Needs Work Reflection Questions: 8.0/12.5 points (64%)

================================================================================
                           DETAILED ANALYSIS
================================================================================

WORKING DIRECTORY (2.0/2.0 points) - EXCELLENT
Logan properly checked the working directory and understood the file structure. 
The code execution shows good awareness of the workspace setup.

PACKAGE LOADING (4.0/4.0 points) - EXCELLENT  
Successfully loaded both tidyverse and readxl packages without errors. Clean, 
professional approach to library management.

CSV IMPORT (6.0/6.0 points) - EXCELLENT
Successfully imported sales data using read_csv() with proper file paths. The 
absolute paths work correctly in the given environment and demonstrate 
understanding of file system navigation.

EXCEL IMPORT (6.0/6.0 points) - EXCELLENT
Correctly imported both sheets from the Excel file using appropriate sheet 
parameters. Demonstrates solid understanding of multi-sheet Excel handling 
with readxl package.

DATA INSPECTION (6.0/8.0 points) - SATISFACTORY
Used head(), str(), and summary() functions appropriately. However, the analysis 
of results is quite basic. Logan correctly identifies data types and dimensions 
but misses opportunities for deeper insights about data quality, business 
implications, and analytical readiness.

REFLECTION QUESTIONS (8.0/12.5 points) - NEEDS WORK
Logan's written responses are very brief and lack the depth expected for 
university-level work. For example, responses like 'there are 3 number variables, 
2 character variables, and a date variable' are factually correct but too 
simplistic. 

What I'm looking for: Detailed discussion of specific data quality issues, their 
potential business impact, how they might affect analysis, and thoughtful 
consideration of data preprocessing needs. Each reflection should be 2-3 sentences 
minimum with specific examples and business context.

================================================================================
                          CODE ISSUES & FIXES
================================================================================

Issues Found:
• Limited Data Quality Assessment: Missing checks for duplicates, outliers, or 
  data consistency
• Minimal Documentation: Code lacks comments explaining the analytical purpose 
  of each step
• Basic Analysis: Could benefit from more comprehensive exploration techniques

SPECIFIC CODE SOLUTIONS:

🔧 Enhanced Data Quality Assessment

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

🔧 Improved Data Exploration

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

🔧 Better Documentation and Comments

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
```

================================================================================
                              NEXT STEPS
================================================================================

Logan demonstrates solid foundational skills in R programming and data management. 
The technical execution is clean and functional, showing good understanding of 
data import and exploration techniques. The code runs successfully and accomplishes 
all required tasks effectively.

STRENGTHS:
• Clean, executable code that accomplishes all technical requirements
• Proper use of tidyverse and readxl packages
• Successful data import from multiple sources (CSV and Excel)
• Systematic approach to data exploration using appropriate R functions
• Accurate identification of basic data characteristics

AREAS FOR DEVELOPMENT:
• Written analysis lacks depth and business context
• Reflection responses are too brief for university-level work
• Missing discussion of data quality implications for business decisions
• Could benefit from more comprehensive data exploration techniques

RECOMMENDATIONS:
• Practice writing more detailed analytical observations (aim for 2-3 sentences 
  per insight)
• Connect technical findings to business implications (e.g., "What do missing 
  values mean for business decisions?")
• Explore additional data quality assessment techniques
• Develop habits around comprehensive data exploration

Logan shows strong technical competency and with more attention to analytical 
depth and communication, will excel in future assignments. The foundation is 
solid - now focus on building analytical thinking skills.

Study Tips:
• Good foundation! Focus on providing more detailed explanations in reflection 
  questions
• Practice connecting technical concepts to business applications
• Try applying these concepts to your own datasets

================================================================================
                              END OF REPORT
================================================================================

Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Grading System: Business Analytics Grader v2.0
"""
    
    # Save the report
    report_filename = f"homework_grader/Logan_Balfour_Detailed_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("📄 COMPREHENSIVE TEXT REPORT GENERATED")
    print("=" * 50)
    print(f"📁 File: {report_filename}")
    print(f"📊 Final Score: {corrected_result['total_score']:.1f}/{corrected_result['max_score']} points")
    print(f"📝 Grade: B ({(corrected_result['total_score']/corrected_result['max_score']*100):.1f}%)")
    print("\n✅ Report includes:")
    print("  • Detailed component breakdown")
    print("  • Specific code fixes with examples")
    print("  • Reflection analysis")
    print("  • Study recommendations")
    print("  • Next steps for improvement")
    
    return report_filename

if __name__ == "__main__":
    generate_text_report()