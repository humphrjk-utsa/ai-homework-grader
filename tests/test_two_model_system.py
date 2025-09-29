#!/usr/bin/env python3
"""
Test script for Two-Model Grading System
"""

import os
import sys
import json
import time
from pathlib import Path

# Add homework_grader to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from two_model_grader import TwoModelGrader
from two_model_config import get_model_config, is_feature_enabled

def test_two_model_system():
    """Test the two-model grading system"""
    
    print("🧪 Testing Two-Model Grading System")
    print("=" * 50)
    
    # Check if feature is enabled
    if not is_feature_enabled('enable_two_model_system'):
        print("❌ Two-model system is disabled in config")
        return False
    
    # Initialize grader
    try:
        grader = TwoModelGrader()
        print("✅ Two-model grader initialized")
    except Exception as e:
        print(f"❌ Failed to initialize grader: {e}")
        return False
    
    # Check model availability
    if not grader.is_available():
        print("❌ Models not available")
        return False
    
    print("✅ Both models available")
    
    # Test with sample data
    sample_student_code = """
# Load required packages
library(tidyverse)

# Import data
messy_sales <- read_csv("data/messy_sales_data.csv")

# Calculate missing values
total_missing <- sum(is.na(messy_sales))
missing_per_column <- colSums(is.na(messy_sales))

# Remove missing values
sales_clean <- na.omit(messy_sales)

# Outlier detection
Q1 <- quantile(sales_clean$Sales_Amount, 0.25)
Q3 <- quantile(sales_clean$Sales_Amount, 0.75)
IQR_val <- IQR(sales_clean$Sales_Amount)

# Create boxplot
ggplot(sales_clean, aes(y = Sales_Amount)) + geom_boxplot()
    """
    
    sample_markdown = """
# Data Cleaning Assignment

## Analysis
I found several data quality issues:
1. Missing values in customer names and sales amounts
2. Outliers in the sales data that seem unrealistic
3. Inconsistent formatting in product categories

## Approach
I decided to remove missing values rather than impute them because the dataset is large enough and the missing data appears to be random.

For outliers, I used the IQR method to identify extreme values and created visualizations to understand their impact.

## Business Impact
Removing these data quality issues will improve the accuracy of our sales analysis and forecasting models.
    """
    
    sample_solution = """
# Complete solution with all required elements
library(tidyverse)
library(readxl)

# Data import and assessment
messy_sales <- read_csv("data/messy_sales_data.csv")
head(messy_sales)
str(messy_sales)
summary(messy_sales)

# Missing value analysis
total_missing <- sum(is.na(messy_sales))
missing_per_column <- colSums(is.na(messy_sales))
incomplete_rows <- messy_sales[!complete.cases(messy_sales), ]

# Missing value treatment
sales_removed_na <- na.omit(messy_sales)
sales_imputed <- messy_sales
get_mode <- function(v) {
  uniqv <- unique(v[!is.na(v)])
  uniqv[which.max(tabulate(match(v, uniqv)))]
}

# Outlier detection
Q1_sales <- quantile(sales_imputed$Sales_Amount, 0.25, na.rm = TRUE)
Q3_sales <- quantile(sales_imputed$Sales_Amount, 0.75, na.rm = TRUE)
IQR_sales <- IQR(sales_imputed$Sales_Amount, na.rm = TRUE)
upper_threshold <- Q3_sales + 1.5 * IQR_sales
lower_threshold <- Q1_sales - 1.5 * IQR_sales

# Visualization
ggplot(sales_imputed, aes(y = Sales_Amount)) + 
  geom_boxplot(outlier.colour = "red") +
  ggtitle("Sales Amount Outliers")
    """
    
    assignment_info = {
        'title': 'Homework 2: Data Cleaning - Handling Missing Values and Outliers',
        'total_points': 37.5,
        'learning_objectives': [
            'Identify and handle missing values using multiple strategies',
            'Detect and treat outliers using statistical methods',
            'Make informed decisions about data quality trade-offs'
        ]
    }
    
    rubric_elements = {
        'data_import_assessment': {
            'max_points': 7.5,
            'category': 'automated',
            'description': 'Successful data import and initial assessment',
            'automated_checks': [
                'Dataset loaded successfully',
                'Correct dimensions identified',
                'Structure and summary functions executed'
            ]
        },
        'missing_value_identification': {
            'max_points': 5,
            'category': 'automated', 
            'description': 'Accurate identification and quantification of missing values',
            'automated_checks': [
                'total_missing variable correctly calculated',
                'missing_per_column uses colSums(is.na())',
                'incomplete_rows uses complete.cases()'
            ]
        },
        'methodology_justification': {
            'max_points': 5,
            'category': 'manual',
            'description': 'Quality of reasoning for chosen cleaning approaches',
            'evaluation_criteria': [
                'Clear rationale for final dataset choice',
                'Business impact assessment',
                'Understanding of trade-offs'
            ]
        }
    }
    
    print("\n🚀 Running test grading...")
    start_time = time.time()
    
    try:
        result = grader.grade_submission(
            student_code=sample_student_code,
            student_markdown=sample_markdown,
            solution_code=sample_solution,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        end_time = time.time()
        
        print(f"\n✅ Grading completed in {end_time - start_time:.1f} seconds")
        print(f"📊 Score: {result['score']:.1f}/{result['max_score']} ({result['percentage']:.1f}%)")
        
        # Display performance stats
        if 'grading_stats' in result:
            stats = result['grading_stats']
            print(f"⏱️ Code Analysis: {stats['code_analysis_time']:.1f}s")
            print(f"⏱️ Feedback Generation: {stats['feedback_generation_time']:.1f}s")
        
        # Display sample feedback
        print("\n📝 Sample Feedback:")
        feedback = result.get('feedback', [])
        for line in feedback[:10]:  # Show first 10 lines
            print(f"   {line}")
        
        if len(feedback) > 10:
            print(f"   ... and {len(feedback) - 10} more lines")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components"""
    
    print("\n🔧 Testing Individual Components")
    print("=" * 40)
    
    # Test Code Analyzer
    try:
        from code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        
        if analyzer.is_available():
            print("✅ Code Analyzer available")
        else:
            print("❌ Code Analyzer not available")
            
    except Exception as e:
        print(f"❌ Code Analyzer error: {e}")
    
    # Test Feedback Generator
    try:
        from feedback_generator import FeedbackGenerator
        generator = FeedbackGenerator()
        
        if generator.is_available():
            print("✅ Feedback Generator available")
        else:
            print("❌ Feedback Generator not available")
            
    except Exception as e:
        print(f"❌ Feedback Generator error: {e}")

if __name__ == "__main__":
    print("🧪 Two-Model Grading System Test Suite")
    print("=" * 60)
    
    # Test individual components first
    test_individual_components()
    
    # Test full system
    success = test_two_model_system()
    
    if success:
        print("\n🎉 All tests passed! Two-model system is ready.")
    else:
        print("\n❌ Tests failed. Check configuration and model availability.")
        
    print("\n📋 Next Steps:")
    print("1. Ensure both Qwen 3.0 Coder and GPT-OSS-120B (bf16) are available")
    print("2. Test with real student submissions")
    print("3. Compare results with single-model approach")
    print("4. Monitor performance and adjust configurations")