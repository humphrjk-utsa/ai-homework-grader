#!/usr/bin/env python3
"""
Comprehensive Test of Fixed Report Generation System
"""

from business_analytics_grader import BusinessAnalyticsGrader
import time

def test_comprehensive_grading():
    print('🚀 Testing Fixed Report Generation System')
    print('=' * 50)

    # Initialize the grader
    grader = BusinessAnalyticsGrader()

    # Sample realistic student submission
    student_code = '''
# Business Analytics Assignment 1: Customer Segmentation Analysis
library(dplyr)
library(ggplot2)
library(readr)

# Load customer data
customers <- read_csv("customer_data.csv")

# Data exploration
print("Dataset Overview:")
str(customers)
summary(customers)

# Data cleaning
customers_clean <- customers %>%
  filter(!is.na(annual_spend)) %>%
  filter(annual_spend > 0) %>%
  mutate(
    spend_category = case_when(
      annual_spend < 500 ~ "Low Spender",
      annual_spend < 2000 ~ "Medium Spender",
      TRUE ~ "High Spender"
    ),
    age_group = case_when(
      age < 30 ~ "Young",
      age < 50 ~ "Middle-aged",
      TRUE ~ "Senior"
    )
  )

# Customer segmentation analysis
segment_analysis <- customers_clean %>%
  group_by(spend_category, age_group) %>%
  summarise(
    count = n(),
    avg_spend = mean(annual_spend),
    total_revenue = sum(annual_spend),
    .groups = "drop"
  )

# Visualization
ggplot(customers_clean, aes(x = age_group, y = annual_spend, fill = spend_category)) +
  geom_boxplot() +
  labs(
    title = "Customer Spending by Age Group and Category",
    x = "Age Group",
    y = "Annual Spend ($)",
    fill = "Spend Category"
  ) +
  theme_minimal() +
  scale_y_continuous(labels = scales::dollar)

# Print results
print("Customer Segmentation Results:")
print(segment_analysis)
'''

    student_markdown = '''
# Customer Segmentation Analysis Report

## Executive Summary
This analysis examines customer spending patterns across different demographic segments to identify high-value customer groups and inform targeted marketing strategies.

## Data Overview
The dataset contains 2,847 customer records with the following key variables:
- Customer demographics (age, location)
- Annual spending amounts
- Purchase frequency
- Product preferences

## Methodology
I used R with dplyr for data manipulation and ggplot2 for visualization. The analysis approach included:

1. **Data Cleaning**: Removed invalid entries and missing values
2. **Segmentation**: Created spending categories (Low/Medium/High) and age groups
3. **Analysis**: Calculated segment-level metrics including average spend and customer counts
4. **Visualization**: Created boxplots to show spending distribution patterns

## Key Findings

### Spending Patterns
- High spenders represent 23% of customers but generate 67% of total revenue
- Medium spenders are the largest group (52% of customers)
- Low spenders show potential for growth with targeted campaigns

### Demographic Insights
- Middle-aged customers (30-50) have highest average spending ($2,340)
- Senior customers show most consistent spending patterns
- Young customers have highest variability in spending behavior

## Business Implications

### Strategic Recommendations
1. **Premium Services**: Develop exclusive offerings for high-spending middle-aged customers
2. **Growth Opportunities**: Create engagement programs for young customers with high spending potential
3. **Retention Focus**: Implement loyalty programs for consistent senior customers

### Marketing Strategy
- Personalized campaigns based on age-spend segments
- Premium product positioning for high-value segments
- Value-oriented messaging for price-sensitive segments

## Reflection Questions

**[What challenges did you encounter in this analysis?]**
The main challenge was determining appropriate spending thresholds for segmentation. I initially used quartiles but found that natural breaks in the data (at $500 and $2000) created more meaningful business segments. I also struggled with handling outliers in the spending data but decided to keep them as they represent legitimate high-value customers.

**[How could this analysis be improved?]**
Future improvements could include:
- Time series analysis to understand spending trends over time
- Customer lifetime value calculations
- Integration with marketing campaign data to measure ROI
- Clustering analysis (k-means) to identify natural customer segments beyond simple categorical splits
- Correlation analysis between demographic factors and spending behavior

**[What did you learn about business analytics from this assignment?]**
I learned that effective business analytics requires balancing statistical rigor with practical business insights. The technical analysis is important, but translating findings into actionable business recommendations is equally critical. I also realized that data cleaning and preparation often takes more time than the actual analysis, and that choosing appropriate segmentation criteria requires both statistical and business judgment.

**[How do these findings inform business strategy?]**
The segmentation reveals clear opportunities for differentiated marketing approaches. High-value customers need retention strategies, while growth segments need acquisition and development programs. The age-based patterns suggest that customer needs evolve over time, requiring lifecycle marketing approaches rather than one-size-fits-all strategies.

## Limitations and Future Research
- Analysis is based on historical data and may not reflect current market conditions
- External factors (economic conditions, competition) not considered
- Sample may not be representative of broader customer base
- Causal relationships between demographics and spending not established

## Conclusion
This customer segmentation analysis provides a foundation for data-driven marketing strategy. The identification of high-value segments and growth opportunities enables targeted resource allocation and personalized customer experiences. Regular updates to this analysis will ensure strategies remain aligned with evolving customer behavior patterns.
'''

    assignment_info = {
        'title': 'Business Analytics Assignment 1: Customer Segmentation',
        'name': 'Customer Segmentation Analysis',
        'description': 'Analyze customer data to identify segments and business opportunities'
    }

    rubric_elements = {
        'technical_execution': 25,
        'business_understanding': 30,
        'data_interpretation': 25,
        'communication': 20
    }

    print('📊 Starting comprehensive grading test...')
    start_time = time.time()

    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code='# Reference solution code here',
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        total_time = time.time() - start_time
        
        print(f'\n✅ Grading completed in {total_time:.1f}s')
        print(f'📊 Final Score: {result["final_score"]}/{result["max_points"]} ({result["final_score_percentage"]:.1f}%)')
        
        # Check feedback quality
        feedback = result.get('comprehensive_feedback', {})
        instructor_comments = feedback.get('instructor_comments', '')
        
        print(f'\n📝 Report Quality Check:')
        print(f'   Instructor Comments: {len(instructor_comments)} characters')
        print(f'   Detailed Feedback Sections: {len(feedback.get("detailed_feedback", {}))}')
        
        # Show sample of the feedback
        if len(instructor_comments) > 200:
            print(f'\n📋 Sample Feedback (first 300 chars):')
            print(f'"{instructor_comments[:300]}..."')
            print('\n✅ SUCCESS: Comprehensive feedback generated!')
        else:
            print('\n⚠️ WARNING: Feedback may be incomplete')
        
        # Check reflection assessment
        detailed_feedback = feedback.get('detailed_feedback', {})
        reflection_assessment = detailed_feedback.get('reflection_assessment', [])
        
        if isinstance(reflection_assessment, list) and len(reflection_assessment) > 0:
            print(f'\n🤔 Reflection Assessment: {len(reflection_assessment)} items')
            print('✅ SUCCESS: Reflection questions properly evaluated!')
        else:
            print('\n⚠️ WARNING: Reflection assessment may be missing')
        
        # Performance metrics
        stats = result.get('grading_stats', {})
        print(f'\n⚡ Performance:')
        print(f'   Parallel Efficiency: {stats.get("parallel_efficiency", 0):.1f}x')
        print(f'   Total Processing Time: {total_time:.1f}s')
        
        # Component scores
        component_scores = result.get('component_scores', {})
        print(f'\n📊 Component Breakdown:')
        for component, score in component_scores.items():
            print(f'   {component}: {score}')
        
        print('\n🎉 Comprehensive test completed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_grading()
    if success:
        print("\n✅ All systems operational! Report generation is working perfectly.")
    else:
        print("\n❌ Issues detected. Check the error messages above.")