#!/usr/bin/env python3
"""
Demo: Business Analytics Grading for Deon
Shows appropriate grading for first-year business students
"""

import time
from business_analytics_grader import BusinessAnalyticsGrader

def create_deon_business_submission():
    """Create Deon's submission with business context"""
    
    student_code = """
# Data Management Assignment 1 - Intro to R
# Student: Deon
# Business Analytics Program - First Year

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
# Business Analytics Assignment 1 - Student Performance Analysis

## Executive Summary
This analysis examines student performance data to understand factors that may influence academic success. As a business analytics student, I recognize the importance of data-driven insights for educational institutions and student success programs.

## Business Problem
Educational institutions need to understand student performance patterns to:
- Identify at-risk students early
- Allocate resources effectively
- Improve student retention rates
- Enhance academic support programs

## Data Analysis Process

### Data Exploration
I began by loading the student dataset and conducting initial exploration. The dataset contains student age and grade information, which are key metrics for understanding academic performance patterns.

### Data Quality Assessment
I identified missing values in the dataset using R's `is.na()` functions. Data quality is crucial for reliable business insights, so I documented:
- Total missing values across the dataset
- Missing values by column
- Impact on analysis scope

### Data Cleaning Strategy
I implemented a conservative approach by removing incomplete records. This ensures our analysis is based on reliable, complete data points. I also created grade categories (A-F) to facilitate business reporting and communication with stakeholders.

## Key Business Insights

### Performance Metrics
- Average student age: 20.5 years
- Average grade: 78.3% (C+ level)
- This suggests most students are performing at acceptable levels

### Relationship Analysis
The scatter plot reveals a slight positive correlation between age and academic performance. This could indicate:
- Older students may have better study habits
- Life experience contributes to academic success
- Maturity levels affect learning outcomes

### Grade Distribution
The bar chart shows grade distribution patterns that can inform:
- Academic support program targeting
- Resource allocation decisions
- Benchmark setting for performance standards

## Business Recommendations
1. **Student Support**: Focus additional support on younger student cohorts
2. **Program Design**: Consider age-appropriate learning strategies
3. **Performance Monitoring**: Use grade categories for regular performance tracking
4. **Data Collection**: Expand data collection to include additional success factors

## Methodology
I used industry-standard R packages (dplyr, ggplot2) following best practices for:
- Data manipulation and cleaning
- Statistical analysis
- Professional visualization
- Reproducible research

## Conclusion
This analysis provides a foundation for data-driven decision making in student success initiatives. The positive age-performance relationship suggests opportunities for targeted interventions and support programs.

## Next Steps
Future analysis should include:
- Additional demographic variables
- Longitudinal performance tracking
- Predictive modeling for early intervention
- Cost-benefit analysis of support programs

## Reflection Questions

**1. What was the most challenging aspect of this assignment?**
[The most challenging part was learning to handle missing data appropriately. I had to decide whether to remove incomplete records or try to estimate missing values. I chose the conservative approach of removing incomplete cases, but I recognize this might introduce bias if the missing data isn't random.]

**2. How did your understanding of data analysis change through this assignment?**
[I learned that data analysis isn't just about running code - it's about making thoughtful decisions at each step. From choosing how to handle missing data to deciding which visualizations best tell the story, every choice affects the conclusions. I also realized how important it is to consider the business context when interpreting results.]

**3. What would you do differently if you repeated this analysis?**
[I would explore the missing data patterns more thoroughly before deciding to remove cases. I'd also like to calculate correlation coefficients to quantify the relationships I observed. Additionally, I would create more detailed visualizations and perhaps explore other variables that might explain the age-performance relationship.]

**4. How do your findings relate to real-world business decisions?**
[The positive correlation between age and performance could inform student support programs. Educational institutions might consider providing additional support for younger students or designing age-appropriate learning interventions. However, I'd want to investigate the underlying causes before making major policy recommendations.]

**5. What limitations do you see in your analysis?**
[The main limitations are: (1) removing incomplete data may have introduced bias, (2) correlation doesn't imply causation - there could be confounding variables, (3) the sample might not be representative of all students, and (4) I only looked at two variables when student performance is likely influenced by many factors.]

**6. What did you learn about R programming through this assignment?**
[I learned that R is very powerful for data analysis, but it requires careful attention to syntax. The dplyr package made data manipulation much easier than I expected, and ggplot2 allowed me to create professional-looking visualizations. I also learned the importance of exploring data before jumping into analysis.]
"""

    assignment_info = {
        "title": "Business Analytics Assignment 1 - Student Performance Analysis",
        "description": "Introduction to R programming and business data analysis",
        "student_name": "Deon",
        "course": "Business Analytics 101",
        "level": "First Year",
        "submission_date": "2025-01-15"
    }

    rubric_elements = {
        "technical_execution": {"weight": 0.25, "max_score": 37.5, "points": 9.375, "description": "R code functionality and syntax"},
        "business_thinking": {"weight": 0.30, "max_score": 37.5, "points": 11.25, "description": "Business context and problem framing"},
        "data_analysis": {"weight": 0.25, "max_score": 37.5, "points": 9.375, "description": "Appropriate analysis methods and insights"},
        "communication": {"weight": 0.20, "max_score": 37.5, "points": 7.5, "description": "Clear business communication and reporting"}
    }

    return {
        "student_code": student_code,
        "student_markdown": student_markdown,
        "solution_code": "",  # Not as important for business context
        "assignment_info": assignment_info,
        "rubric_elements": rubric_elements
    }

def print_business_header():
    """Print business grading header"""
    print("🎓" + "=" * 80 + "🎓")
    print("                    BUSINESS ANALYTICS GRADING SYSTEM")
    print("                   Encouraging • Supportive • Business-Focused")
    print("🎓" + "=" * 80 + "🎓")
    print()

def print_business_context():
    """Print business grading context"""
    print("📊 GRADING CONTEXT")
    print("-" * 40)
    print("Course Level: First-Year Business Analytics")
    print("Student Background: Business major, new to R programming")
    print("Grading Philosophy: Encourage learning, reward effort, build confidence")
    print("Focus Areas: Business thinking, practical application, communication")
    print()

def demo_business_grading():
    """Demo business-appropriate grading"""
    print_business_header()
    print_business_context()
    
    # Get submission
    submission = create_deon_business_submission()
    
    print("📋 STUDENT SUBMISSION")
    print("-" * 40)
    print(f"Student: {submission['assignment_info']['student_name']}")
    print(f"Course: {submission['assignment_info']['course']}")
    print(f"Level: {submission['assignment_info']['level']}")
    print(f"Assignment: {submission['assignment_info']['title']}")
    print()
    
    print("🤔 Ready to grade with business-appropriate standards?")
    choice = input("Proceed with business grading? (y/N): ").strip().lower()
    
    if choice not in ['y', 'yes']:
        print("👋 Demo cancelled")
        return
    
    try:
        print("\n🎓 Starting Business Analytics Grading...")
        grader = BusinessAnalyticsGrader()
        
        # Check system
        if not grader.check_ollama_connection():
            print("❌ Ollama not connected")
            return
        
        if not grader.check_models_available():
            print("❌ Models not available")
            return
        
        print("✅ System ready for business grading")
        
        # Grade with business context
        result = grader.grade_submission(
            student_code=submission["student_code"],
            student_markdown=submission["student_markdown"],
            solution_code=submission["solution_code"],
            assignment_info=submission["assignment_info"],
            rubric_elements=submission["rubric_elements"]
        )
        
        # Display business-appropriate results
        print_business_results(result)
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")

def print_business_results(result):
    """Print professional business-focused results"""
    print("\n" + "=" * 80)
    print("                     BUSINESS ANALYTICS ASSESSMENT REPORT")
    print("=" * 80)
    
    # Get calculated scores
    final_score = result.get('final_score', 0)
    max_points = result.get('max_points', 37.5)
    final_percentage = result.get('final_score_percentage', 0)
    
    print(f"\nFINAL SCORE: {final_score}/{max_points} points ({final_percentage}%)")
    
    # Business-appropriate letter grade scale based on percentage
    if final_percentage >= 97:
        letter_grade = "A+"
        comment = "Exceptional performance"
    elif final_percentage >= 93:
        letter_grade = "A"
        comment = "Excellent work"
    elif final_percentage >= 90:
        letter_grade = "A-"
        comment = "Very good work"
    elif final_percentage >= 87:
        letter_grade = "B+"
        comment = "Good performance"
    elif final_percentage >= 83:
        letter_grade = "B"
        comment = "Satisfactory work"
    elif final_percentage >= 80:
        letter_grade = "B-"
        comment = "Acceptable completion"
    else:
        letter_grade = "C+"
        comment = "Needs improvement"
    
    print(f"LETTER GRADE: {letter_grade}")
    print(f"PERFORMANCE LEVEL: {comment}")
    print()
    
    # Rubric Breakdown
    print("RUBRIC BREAKDOWN")
    print("-" * 30)
    
    # Get component scores from the calculation
    component_scores = result.get('component_scores', {})
    component_percentages = result.get('component_percentages', {})
    
    technical_points = component_scores.get('technical_points', 0)
    business_points = component_scores.get('business_points', 0)
    analysis_points = component_scores.get('analysis_points', 0)
    communication_points = component_scores.get('communication_points', 0)
    bonus_points = component_scores.get('bonus_points', 0)
    
    technical_pct = component_percentages.get('technical_score', 0)
    business_pct = component_percentages.get('business_understanding', 0)
    analysis_pct = component_percentages.get('data_interpretation', 0)
    communication_pct = component_percentages.get('communication_clarity', 0)
    
    print(f"Technical Execution (25%):     {technical_points}/9.4 points ({technical_pct}%)")
    print(f"Business Thinking (30%):       {business_points}/11.3 points ({business_pct}%)")
    print(f"Data Analysis (25%):           {analysis_points}/9.4 points ({analysis_pct}%)")
    print(f"Communication (20%):           {communication_points}/7.5 points ({communication_pct}%)")
    if bonus_points > 0:
        print(f"Bonus Points:                  +{bonus_points} points")
    print("-" * 50)
    print(f"TOTAL:                         {final_score}/37.5 points ({final_percentage}%)")
    print()
    
    # Technical Analysis
    technical = result.get('technical_analysis', {})
    print("TECHNICAL IMPLEMENTATION ASSESSMENT")
    print("-" * 50)
    print(f"Overall Technical Score: {technical.get('technical_score', 'N/A')}/100")
    print(f"Code Functionality: {technical.get('syntax_correctness', 'N/A')}/100")
    print(f"Logical Approach: {technical.get('logic_correctness', 'N/A')}/100")
    print(f"Business Relevance: {technical.get('business_relevance', 'N/A')}/100")
    print(f"Effort & Completion: {technical.get('effort_and_completion', 'N/A')}/100")
    
    # Code Strengths
    strengths = technical.get('code_strengths', [])
    if strengths:
        print(f"\nCode Implementation Strengths:")
        for i, strength in enumerate(strengths, 1):
            print(f"  {i}. {strength}")
    
    # Code Suggestions (Corrections/Improvements)
    suggestions = technical.get('code_suggestions', [])
    if suggestions:
        print(f"\nCode Improvement Recommendations:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    # Technical Observations
    observations = technical.get('technical_observations', [])
    if observations:
        print(f"\nTechnical Assessment Notes:")
        for i, observation in enumerate(observations, 1):
            print(f"  {i}. {observation}")
    
    print()
    
    # Business Analytics Assessment
    feedback = result.get('comprehensive_feedback', {})
    print("BUSINESS ANALYTICS EVALUATION")
    print("-" * 50)
    print(f"Overall Score: {feedback.get('overall_score', 'N/A')}/100")
    print(f"Business Understanding: {feedback.get('business_understanding', 'N/A')}/100")
    print(f"Communication Clarity: {feedback.get('communication_clarity', 'N/A')}/100")
    print(f"Data Interpretation: {feedback.get('data_interpretation', 'N/A')}/100")
    print(f"Methodology: {feedback.get('methodology_appropriateness', 'N/A')}/100")
    print(f"Reflection Quality: {feedback.get('reflection_quality', 'N/A')}/100")
    
    # Detailed Feedback
    detailed = feedback.get('detailed_feedback', {})
    
    # Reflection Assessment (Priority)
    reflection_assessment = detailed.get('reflection_assessment', [])
    if reflection_assessment:
        print(f"\nReflection Assessment:")
        for i, assessment in enumerate(reflection_assessment, 1):
            print(f"  {i}. {assessment}")
    
    # Learning Demonstration
    learning_demo = detailed.get('learning_demonstration', [])
    if learning_demo:
        print(f"\nLearning Demonstration:")
        for i, demo in enumerate(learning_demo, 1):
            print(f"  {i}. {demo}")
    
    # Analytical Strengths
    analytical_strengths = detailed.get('analytical_strengths', [])
    if analytical_strengths:
        print(f"\nAnalytical Strengths:")
        for i, strength in enumerate(analytical_strengths, 1):
            print(f"  {i}. {strength}")
    
    # Business Application
    business_app = detailed.get('business_application', [])
    if business_app:
        print(f"\nBusiness Application:")
        for i, app in enumerate(business_app, 1):
            print(f"  {i}. {app}")
    
    # Areas for Development
    development = detailed.get('areas_for_development', [])
    if development:
        print(f"\nAreas for Development:")
        for i, area in enumerate(development, 1):
            print(f"  {i}. {area}")
    
    # Recommendations
    recommendations = detailed.get('recommendations', [])
    if recommendations:
        print(f"\nRecommendations for Future Work:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Instructor Comments
    comments = feedback.get('instructor_comments', '')
    if comments:
        print(f"\nINSTRUCTOR FEEDBACK:")
        print("-" * 30)
        import textwrap
        wrapped_comments = textwrap.fill(comments, width=70)
        print(wrapped_comments)
    
    print()
    
    # Performance Stats
    stats = result.get('grading_stats', {})
    print("⚡ GRADING PERFORMANCE")
    print("-" * 30)
    print(f"Total Time: {stats.get('total_time', 'N/A'):.1f}s")
    print(f"Parallel Efficiency: {stats.get('parallel_efficiency', 'N/A'):.1f}x")
    
    # Course Context
    print(f"\n🎓 COURSE CONTEXT")
    print("-" * 20)
    print(f"Course: {result.get('course_context', 'Business Analytics')}")
    print(f"Grading Approach: {result.get('grading_philosophy', 'Encouraging')}")
    
    print("\n" + "🎓" + "=" * 78 + "🎓")

def main():
    """Main demo function"""
    demo_business_grading()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")