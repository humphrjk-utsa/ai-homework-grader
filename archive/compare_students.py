#!/usr/bin/env python3
"""
Compare Deon's and Logan's Assignment Performance
"""

import json
from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator

def create_deon_submission():
    """Create Deon's submission based on the demo"""
    
    student_code = """
# Data Management Assignment 1 - Intro to R
# Student: Deon

# Load required libraries
library(dplyr)
library(ggplot2)
library(readr)

# 1. Data Loading and Exploration
data <- read_csv("student_data.csv")
print("Data loaded successfully")

# Basic data exploration
dim(data)
str(data)
summary(data)

# Check for missing values
sum(is.na(data))
colSums(is.na(data))

# 2. Data Cleaning
# Remove rows with missing values
clean_data <- data %>%
  filter(!is.na(age), !is.na(grade)) %>%
  mutate(grade_category = case_when(
    grade >= 90 ~ "A",
    grade >= 80 ~ "B", 
    grade >= 70 ~ "C",
    grade >= 60 ~ "D",
    TRUE ~ "F"
  ))

# 3. Basic Statistics
mean_age <- mean(clean_data$age)
mean_grade <- mean(clean_data$grade)

print(paste("Average age:", mean_age))
print(paste("Average grade:", mean_grade))

# 4. Data Visualization
ggplot(clean_data, aes(x = age, y = grade)) +
  geom_point() +
  geom_smooth(method = "lm") +
  labs(title = "Age vs Grade Relationship",
       x = "Age", y = "Grade") +
  theme_minimal()

# Grade distribution
ggplot(clean_data, aes(x = grade_category)) +
  geom_bar(fill = "steelblue") +
  labs(title = "Grade Distribution",
       x = "Grade Category", y = "Count")
"""

    student_markdown = """
# Data Management Assignment 1 - Analysis Report

## Introduction
In this assignment, I analyzed student data to understand the relationship between age and academic performance. The dataset contains information about students including their age and grades.

## Data Exploration
The dataset initially contained some missing values which I identified using `is.na()` functions. I found missing values in both the age and grade columns that needed to be addressed.

## Data Cleaning Process
I performed the following cleaning steps:
1. Removed rows with missing values in critical columns (age and grade)
2. Created a new categorical variable for grade categories (A, B, C, D, F)
3. Verified the cleaned dataset had no missing values in key variables

## Key Findings
- The average age of students is approximately 20.5 years
- The average grade is 78.3, which corresponds to a C+ level
- There appears to be a slight positive correlation between age and grade
- Most students fall into the B and C grade categories

## Visualizations
I created two main visualizations:
1. A scatter plot showing the relationship between age and grade with a trend line
2. A bar chart showing the distribution of grade categories

## Methodology
I used dplyr for data manipulation and ggplot2 for visualization. The approach was systematic:
- First explore the raw data
- Identify and handle missing values
- Create derived variables for analysis
- Generate summary statistics
- Create informative visualizations

## Conclusions
The analysis suggests that older students tend to perform slightly better academically, though the relationship is not very strong. The grade distribution shows a normal pattern with most students achieving average performance.

## Reflection Questions

**What challenges did you encounter?**
[The main challenge was handling missing data. I had to decide whether to remove incomplete records or try to impute missing values. I chose to remove them for simplicity, but I recognize this could introduce bias if the missing data isn't random.]

**What did you learn from this assignment?**
[I learned the importance of data quality assessment before analysis. The process of exploring, cleaning, and visualizing data gave me a better understanding of the analytical workflow. I also learned how to create categorical variables from continuous ones using case_when().]

**How would you improve your analysis?**
[I would like to explore more sophisticated imputation methods for missing data, investigate additional variables that might influence grades, and use statistical tests to determine if the age-grade correlation is significant. I'd also like to create more interactive visualizations.]

## Areas for Improvement
In future analysis, I would like to:
- Investigate other factors that might influence grades
- Use more sophisticated statistical methods
- Include additional demographic variables
- Perform statistical significance testing
- Create interactive dashboards for data exploration
"""

    assignment_info = {
        "title": "Data Management Assignment 1: Introduction to R",
        "student_name": "Deon",
        "course": "Data Management",
        "assignment_date": "9/14/2025"
    }

    rubric_elements = {
        "technical_execution": {"weight": 0.25, "max_score": 37.5},
        "business_thinking": {"weight": 0.30, "max_score": 37.5},
        "data_analysis": {"weight": 0.25, "max_score": 37.5},
        "communication": {"weight": 0.20, "max_score": 37.5}
    }

    return {
        "student_code": student_code,
        "student_markdown": student_markdown,
        "assignment_info": assignment_info,
        "rubric_elements": rubric_elements
    }

def grade_deon():
    """Grade Deon's assignment"""
    
    print("🎓 Grading Deon's Assignment")
    print("=" * 40)
    
    submission = create_deon_submission()
    
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
    
    grader = BusinessAnalyticsGrader()
    
    result = grader.grade_submission(
        student_code=submission["student_code"],
        student_markdown=submission["student_markdown"],
        solution_code=solution_code,
        assignment_info=submission["assignment_info"],
        rubric_elements=submission["rubric_elements"]
    )
    
    # Validate result
    validator = GradingValidator()
    is_valid, errors = validator.validate_grading_result(result)
    
    if not is_valid:
        print("⚠️ Validation errors found, attempting to fix...")
        result = validator.fix_calculation_errors(result)
    
    return result

def load_logan_results():
    """Load Logan's grading results"""
    try:
        with open('homework_grader/logan_grading_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Logan's results not found. Please grade Logan first.")
        return None

def compare_students(deon_result, logan_result):
    """Compare the two students' performance"""
    
    print("\n" + "🔍" + "=" * 80 + "🔍")
    print("                    STUDENT PERFORMANCE COMPARISON")
    print("🔍" + "=" * 80 + "🔍")
    
    # Basic comparison
    print(f"\n📊 OVERALL SCORES:")
    print(f"{'Student':<15} {'Score':<12} {'Percentage':<12} {'Letter Grade':<12}")
    print("-" * 55)
    
    # Calculate letter grades
    def get_letter_grade(percentage):
        if percentage >= 97: return "A+"
        elif percentage >= 93: return "A"
        elif percentage >= 90: return "A-"
        elif percentage >= 87: return "B+"
        elif percentage >= 83: return "B"
        elif percentage >= 80: return "B-"
        else: return "C+"
    
    deon_grade = get_letter_grade(deon_result['final_score_percentage'])
    logan_grade = get_letter_grade(logan_result['final_score_percentage'])
    
    print(f"{'Deon':<15} {deon_result['final_score']:<12} {deon_result['final_score_percentage']:.1f}%{'':<7} {deon_grade:<12}")
    print(f"{'Logan':<15} {logan_result['final_score']:<12} {logan_result['final_score_percentage']:.1f}%{'':<7} {logan_grade:<12}")
    
    # Component comparison
    print(f"\n📋 COMPONENT BREAKDOWN:")
    print(f"{'Component':<25} {'Deon':<15} {'Logan':<15} {'Difference':<15}")
    print("-" * 70)
    
    components = [
        ("Technical Execution", "technical_points"),
        ("Business Thinking", "business_points"),
        ("Data Analysis", "analysis_points"),
        ("Communication", "communication_points")
    ]
    
    for comp_name, comp_key in components:
        deon_score = deon_result['component_scores'][comp_key]
        logan_score = logan_result['component_scores'][comp_key]
        difference = deon_score - logan_score
        diff_str = f"+{difference:.1f}" if difference > 0 else f"{difference:.1f}"
        
        print(f"{comp_name:<25} {deon_score:<15.1f} {logan_score:<15.1f} {diff_str:<15}")
    
    # Percentage comparison
    print(f"\n📊 COMPONENT PERCENTAGES:")
    print(f"{'Component':<25} {'Deon':<15} {'Logan':<15} {'Difference':<15}")
    print("-" * 70)
    
    percentage_components = [
        ("Technical Score", "technical_score"),
        ("Business Understanding", "business_understanding"),
        ("Data Interpretation", "data_interpretation"),
        ("Communication Clarity", "communication_clarity")
    ]
    
    for comp_name, comp_key in percentage_components:
        deon_pct = deon_result['component_percentages'][comp_key]
        logan_pct = logan_result['component_percentages'][comp_key]
        difference = deon_pct - logan_pct
        diff_str = f"+{difference:.0f}%" if difference > 0 else f"{difference:.0f}%"
        
        print(f"{comp_name:<25} {deon_pct:.0f}%{'':<12} {logan_pct:.0f}%{'':<12} {diff_str:<15}")
    
    # Strengths and weaknesses analysis
    print(f"\n🌟 STRENGTHS COMPARISON:")
    print("-" * 40)
    
    print("🔹 Deon's Key Strengths:")
    deon_tech = deon_result.get('technical_analysis', {})
    deon_strengths = deon_tech.get('code_strengths', [])[:3]
    for i, strength in enumerate(deon_strengths, 1):
        print(f"  {i}. {strength}")
    
    print("\n🔹 Logan's Key Strengths:")
    logan_tech = logan_result.get('technical_analysis', {})
    logan_strengths = logan_tech.get('code_strengths', [])[:3]
    for i, strength in enumerate(logan_strengths, 1):
        print(f"  {i}. {strength}")
    
    # Areas for improvement
    print(f"\n📈 AREAS FOR IMPROVEMENT:")
    print("-" * 40)
    
    print("🔹 Deon's Development Areas:")
    deon_feedback = deon_result.get('comprehensive_feedback', {}).get('detailed_feedback', {})
    deon_improvements = deon_feedback.get('areas_for_development', [])[:3]
    for i, improvement in enumerate(deon_improvements, 1):
        print(f"  {i}. {improvement}")
    
    print("\n🔹 Logan's Development Areas:")
    logan_feedback = logan_result.get('comprehensive_feedback', {}).get('detailed_feedback', {})
    logan_improvements = logan_feedback.get('areas_for_development', [])[:3]
    for i, improvement in enumerate(logan_improvements, 1):
        print(f"  {i}. {improvement}")
    
    # Overall analysis
    print(f"\n🎯 COMPARATIVE ANALYSIS:")
    print("-" * 40)
    
    total_diff = deon_result['final_score'] - logan_result['final_score']
    
    if abs(total_diff) < 1.0:
        print("📊 Performance: Very similar overall performance")
    elif deon_result['final_score'] > logan_result['final_score']:
        print(f"📊 Performance: Deon scored {total_diff:.1f} points higher than Logan")
    else:
        print(f"📊 Performance: Logan scored {abs(total_diff):.1f} points higher than Deon")
    
    # Identify strongest areas for each student
    deon_components = deon_result['component_percentages']
    logan_components = logan_result['component_percentages']
    
    deon_strongest = max(deon_components.items(), key=lambda x: x[1])
    logan_strongest = max(logan_components.items(), key=lambda x: x[1])
    
    print(f"🌟 Deon's strongest area: {deon_strongest[0]} ({deon_strongest[1]}%)")
    print(f"🌟 Logan's strongest area: {logan_strongest[0]} ({logan_strongest[1]}%)")
    
    # Reflection quality comparison
    deon_reflection = deon_result.get('comprehensive_feedback', {}).get('reflection_quality', 0)
    logan_reflection = logan_result.get('comprehensive_feedback', {}).get('reflection_quality', 0)
    
    print(f"\n💭 REFLECTION QUALITY:")
    print(f"Deon: {deon_reflection}% | Logan: {logan_reflection}%")
    
    if deon_reflection > logan_reflection:
        print("🏆 Deon shows stronger reflective thinking")
    elif logan_reflection > deon_reflection:
        print("🏆 Logan shows stronger reflective thinking")
    else:
        print("🤝 Both students show similar reflection quality")

def main():
    """Main comparison function"""
    
    print("🔍 Student Performance Comparison Tool")
    print("=" * 50)
    
    # Load Logan's results
    logan_result = load_logan_results()
    if not logan_result:
        return
    
    # Grade Deon's assignment
    deon_result = grade_deon()
    
    # Save Deon's results
    with open('homework_grader/deon_grading_results.json', 'w') as f:
        json.dump(deon_result, f, indent=2, default=str)
    
    # Compare both students
    compare_students(deon_result, logan_result)
    
    print(f"\n💾 Results saved:")
    print(f"  - Deon: deon_grading_results.json")
    print(f"  - Logan: logan_grading_results.json")

if __name__ == "__main__":
    main()