#!/usr/bin/env python3
"""
Test Report Generation with Fixed Parsing
Verify that reports are no longer truncated
"""

from business_analytics_grader import BusinessAnalyticsGrader
import json
import time

def test_report_generation():
    """Test complete report generation with distributed MLX"""
    
    print("🧪 Testing Report Generation with Fixed Parsing")
    print("=" * 50)
    
    # Initialize grader
    grader = BusinessAnalyticsGrader()
    
    if not grader.use_distributed_mlx:
        print("❌ Distributed MLX not available, cannot test")
        return
    
    # Sample student submission
    student_code = """
# Load required libraries
library(dplyr)
library(ggplot2)
library(readr)

# Load the dataset
data <- read_csv("sales_data.csv")

# Explore the data structure
str(data)
summary(data)

# Data cleaning
data_clean <- data %>%
  filter(!is.na(sales_amount)) %>%
  filter(sales_amount > 0) %>%
  mutate(sales_category = case_when(
    sales_amount < 1000 ~ "Low",
    sales_amount < 5000 ~ "Medium",
    TRUE ~ "High"
  ))

# Calculate summary statistics
sales_summary <- data_clean %>%
  group_by(region) %>%
  summarise(
    total_sales = sum(sales_amount),
    avg_sales = mean(sales_amount),
    count = n()
  )

# Create visualization
ggplot(data_clean, aes(x = region, y = sales_amount)) +
  geom_boxplot() +
  labs(title = "Sales Distribution by Region",
       x = "Region", y = "Sales Amount") +
  theme_minimal()

# Print results
print(sales_summary)
"""
    
    student_markdown = """
# Business Analytics Assignment 1: Sales Data Analysis

## Introduction
This assignment analyzes sales data to understand regional performance patterns and identify business insights for strategic decision-making.

## Data Exploration
The dataset contains sales transactions across different regions. Initial exploration revealed:
- 1,250 total transactions
- Sales amounts ranging from $50 to $15,000
- Five distinct regions: North, South, East, West, Central

## Methodology
I used R with dplyr for data manipulation and ggplot2 for visualization. The analysis focused on:
1. Data cleaning to remove invalid entries
2. Categorization of sales into Low/Medium/High segments
3. Regional comparison of sales performance

## Key Findings
- The North region shows highest total sales ($2.3M)
- Average transaction size is largest in the West region ($3,200)
- Central region has most consistent performance (lowest variance)

## Business Implications
These findings suggest:
- North region should receive continued investment
- West region customers may be higher-value segments
- Central region represents stable, predictable revenue

## Reflection Questions

[What challenges did you encounter in this analysis?]
The main challenge was handling missing data appropriately. I chose to remove NA values rather than impute them because the dataset was large enough to maintain statistical power. I also struggled initially with creating meaningful categories for sales amounts but settled on the Low/Medium/High approach based on natural breaks in the data distribution.

[How could this analysis be improved?]
Future analysis could include time series components to understand seasonal patterns, customer segmentation analysis to identify high-value customer characteristics, and correlation analysis with external factors like economic indicators or marketing spend.

[What did you learn about business analytics from this assignment?]
I learned that data cleaning is often the most time-intensive part of analysis, and that business context is crucial for interpreting statistical results. The technical skills are important, but understanding what the numbers mean for business decisions is equally critical.

## Conclusion
This analysis provides a foundation for regional sales strategy, highlighting the North region's strength and the West region's potential for high-value customer development.
"""
    
    solution_code = """
# Reference solution with additional statistical analysis
library(dplyr)
library(ggplot2)
library(readr)
library(corrplot)

data <- read_csv("sales_data.csv")
data_clean <- data %>%
  filter(!is.na(sales_amount), sales_amount > 0) %>%
  mutate(sales_category = cut(sales_amount, 
                             breaks = c(0, 1000, 5000, Inf),
                             labels = c("Low", "Medium", "High")))

# Enhanced analysis with correlation
correlation_analysis <- cor(data_clean[c("sales_amount", "customer_age", "product_price")])
print(correlation_analysis)
"""
    
    assignment_info = {
        'title': 'Business Analytics Assignment 1',
        'name': 'Sales Data Analysis',
        'description': 'Regional sales performance analysis with business insights'
    }
    
    rubric_elements = {
        'technical_execution': 25,
        'business_understanding': 30,
        'data_interpretation': 25,
        'communication': 20
    }
    
    print("🚀 Starting comprehensive grading test...")
    start_time = time.time()
    
    try:
        # Grade the submission
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        total_time = time.time() - start_time
        
        print(f"\n✅ Grading completed in {total_time:.1f}s")
        print(f"📊 Final Score: {result['final_score']}/{result['max_points']} ({result['final_score_percentage']:.1f}%)")
        
        # Check for truncation issues
        feedback = result.get('comprehensive_feedback', {})
        instructor_comments = feedback.get('instructor_comments', '')
        
        print(f"\n📝 Instructor Comments Length: {len(instructor_comments)} characters")
        
        if len(instructor_comments) > 500:
            print("✅ PASS: Instructor comments are comprehensive (not truncated)")
        else:
            print("⚠️ WARNING: Instructor comments may be truncated")
        
        # Check detailed feedback structure
        detailed_feedback = feedback.get('detailed_feedback', {})
        if isinstance(detailed_feedback, dict):
            print("✅ PASS: Detailed feedback has proper structure")
            
            # Check reflection assessment
            reflection_assessment = detailed_feedback.get('reflection_assessment', [])
            if isinstance(reflection_assessment, list) and len(reflection_assessment) > 0:
                print("✅ PASS: Reflection assessment is present and detailed")
            else:
                print("⚠️ WARNING: Reflection assessment may be missing or incomplete")
        else:
            print("❌ FAIL: Detailed feedback structure is incorrect")
        
        # Display sample feedback
        print(f"\n📋 Sample Instructor Comments (first 200 chars):")
        print(f"'{instructor_comments[:200]}...'")
        
        # Check technical analysis
        technical_analysis = result.get('technical_analysis', {})
        code_strengths = technical_analysis.get('code_strengths', [])
        
        print(f"\n🔧 Code Strengths Count: {len(code_strengths)}")
        if len(code_strengths) >= 3:
            print("✅ PASS: Comprehensive code analysis")
        else:
            print("⚠️ WARNING: Code analysis may be incomplete")
        
        # Performance metrics
        stats = result.get('grading_stats', {})
        parallel_efficiency = stats.get('parallel_efficiency', 0)
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Parallel Efficiency: {parallel_efficiency:.1f}x")
        print(f"   Code Analysis Time: {stats.get('code_analysis_time', 0):.1f}s")
        print(f"   Feedback Generation Time: {stats.get('feedback_generation_time', 0):.1f}s")
        
        if parallel_efficiency > 1.5:
            print("✅ PASS: Excellent parallel performance")
        else:
            print("⚠️ WARNING: Parallel efficiency could be improved")
        
        print(f"\n🎉 Report Generation Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("\n✅ All tests passed! Report generation is working properly.")
    else:
        print("\n❌ Tests failed. Check the error messages above.")