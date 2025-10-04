#!/usr/bin/env python3
"""
Demo: Review Deon's Notebook with Optimized Ollama System
Shows real-time grading process in terminal
"""

import time
import json
from ollama_two_model_grader import OllamaTwoModelGrader

def create_sample_deon_submission():
    """Create a sample submission representing Deon's work"""
    
    # Sample R code that might be in Deon's notebook
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

    # Sample markdown responses
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

## Areas for Improvement
In future analysis, I would like to:
- Investigate other factors that might influence grades
- Use more sophisticated statistical methods
- Include additional demographic variables
"""

    # Reference solution for comparison
    solution_code = """
# Reference Solution - Data Management Assignment 1

library(dplyr)
library(ggplot2)
library(readr)
library(skimr)

# Load and explore data
data <- read_csv("student_data.csv")

# Comprehensive data exploration
skim(data)
glimpse(data)

# Data quality assessment
data_quality <- data %>%
  summarise(
    total_rows = n(),
    missing_age = sum(is.na(age)),
    missing_grade = sum(is.na(grade)),
    complete_cases = sum(complete.cases(.))
  )

# Advanced data cleaning
clean_data <- data %>%
  filter(complete.cases(.)) %>%
  mutate(
    grade_category = cut(grade, 
                        breaks = c(0, 60, 70, 80, 90, 100),
                        labels = c("F", "D", "C", "B", "A"),
                        include.lowest = TRUE),
    age_group = cut(age,
                   breaks = c(0, 20, 25, 30, Inf),
                   labels = c("18-20", "21-25", "26-30", "30+"))
  )

# Statistical analysis
summary_stats <- clean_data %>%
  group_by(grade_category) %>%
  summarise(
    count = n(),
    mean_age = mean(age),
    sd_age = sd(age),
    .groups = 'drop'
  )

# Correlation analysis
correlation <- cor(clean_data$age, clean_data$grade)

# Advanced visualizations
p1 <- ggplot(clean_data, aes(x = age, y = grade)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(title = "Age vs Grade Relationship",
       subtitle = paste("Correlation:", round(correlation, 3)),
       x = "Age (years)", y = "Grade (%)") +
  theme_minimal()

p2 <- ggplot(clean_data, aes(x = grade_category, fill = age_group)) +
  geom_bar(position = "dodge") +
  labs(title = "Grade Distribution by Age Group",
       x = "Grade Category", y = "Count") +
  theme_minimal()
"""

    assignment_info = {
        "title": "Data Management Assignment 1 - Intro to R",
        "description": "Introduction to R programming and basic data analysis",
        "student_name": "Deon",
        "submission_date": "2025-01-15"
    }

    rubric_elements = {
        "data_loading": {"weight": 0.15, "max_score": 100, "description": "Proper data loading and initial exploration"},
        "data_cleaning": {"weight": 0.25, "max_score": 100, "description": "Identification and handling of data quality issues"},
        "analysis": {"weight": 0.25, "max_score": 100, "description": "Appropriate statistical analysis and calculations"},
        "visualization": {"weight": 0.20, "max_score": 100, "description": "Clear and informative data visualizations"},
        "communication": {"weight": 0.15, "max_score": 100, "description": "Clear written communication and interpretation"}
    }

    return {
        "student_code": student_code,
        "student_markdown": student_markdown,
        "solution_code": solution_code,
        "assignment_info": assignment_info,
        "rubric_elements": rubric_elements
    }

def print_grading_header():
    """Print grading session header"""
    print("🎓" + "=" * 80 + "🎓")
    print("                    HOMEWORK GRADING SYSTEM")
    print("                   RTX Pro 6000 + Ollama Optimized")
    print("🎓" + "=" * 80 + "🎓")
    print()

def print_submission_info(submission):
    """Print submission information"""
    info = submission["assignment_info"]
    print("📋 SUBMISSION DETAILS")
    print("-" * 40)
    print(f"Student: {info['student_name']}")
    print(f"Assignment: {info['title']}")
    print(f"Submitted: {info['submission_date']}")
    print(f"Description: {info['description']}")
    print()

def print_code_preview(code, max_lines=15):
    """Print a preview of the student's code"""
    print("💻 STUDENT CODE PREVIEW")
    print("-" * 40)
    lines = code.strip().split('\n')
    for i, line in enumerate(lines[:max_lines], 1):
        print(f"{i:2d}: {line}")
    
    if len(lines) > max_lines:
        print(f"... ({len(lines) - max_lines} more lines)")
    print()

def print_markdown_preview(markdown, max_chars=500):
    """Print a preview of the student's written responses"""
    print("📝 WRITTEN RESPONSE PREVIEW")
    print("-" * 40)
    
    if len(markdown) > max_chars:
        preview = markdown[:max_chars] + "..."
    else:
        preview = markdown
    
    print(preview)
    print()

def animate_grading_process():
    """Animate the grading process"""
    print("🚀 STARTING PARALLEL GRADING PROCESS")
    print("-" * 40)
    
    steps = [
        ("🔍 Initializing Ollama Two-Model System...", 1),
        ("🤖 Loading Qwen 3.0 Coder 30B (Code Analysis)...", 2),
        ("📝 Loading Gemma 3.0 27B (Feedback Generation)...", 2),
        ("✅ Both models loaded and optimized", 1),
        ("⚡ Starting parallel processing...", 1),
        ("", 0.5)
    ]
    
    for step, delay in steps:
        if step:
            print(step)
        time.sleep(delay)

def print_live_grading_status():
    """Print live grading status"""
    print("📊 LIVE GRADING STATUS")
    print("-" * 40)
    
    # Simulate parallel processing
    import threading
    import sys
    
    def print_code_analysis():
        for i in range(12):
            print(f"\r🔧 [CODE ANALYSIS] Processing... {i+1}/12s", end="", flush=True)
            time.sleep(1)
        print(f"\r🔧 [CODE ANALYSIS] ✅ Complete (12.0s)                    ")
    
    def print_feedback_generation():
        for i in range(24):
            print(f"\r📝 [FEEDBACK] Generating... {i+1}/24s", end="", flush=True)
            time.sleep(1)
        print(f"\r📝 [FEEDBACK] ✅ Complete (24.0s)                        ")
    
    # Start both threads
    code_thread = threading.Thread(target=print_code_analysis)
    feedback_thread = threading.Thread(target=print_feedback_generation)
    
    print("🔧 [CODE ANALYSIS] Starting with Qwen 3.0 Coder...")
    print("📝 [FEEDBACK] Starting with Gemma 3.0...")
    print()
    
    code_thread.start()
    time.sleep(0.5)  # Slight delay to show parallel execution
    feedback_thread.start()
    
    code_thread.join()
    feedback_thread.join()
    
    print()
    print("🔄 Merging results from both models...")
    time.sleep(2)
    print("✅ Parallel grading complete!")
    print()

def demo_grading_results():
    """Demo the actual grading with real models"""
    print("🎯 EXECUTING REAL GRADING WITH YOUR MODELS")
    print("-" * 50)
    
    # Get submission data
    submission = create_sample_deon_submission()
    
    try:
        # Initialize the grader
        print("🚀 Initializing Ollama Two-Model Grader...")
        grader = OllamaTwoModelGrader()
        
        # Check system status
        status = grader.get_system_status()
        if not status['ollama_connected']:
            print("❌ Ollama not connected. Please start Ollama first.")
            return False
        
        print("✅ Ollama connected, models ready")
        print()
        
        # Grade the submission
        print("⚡ Starting parallel grading process...")
        start_time = time.time()
        
        result = grader.grade_submission(
            student_code=submission["student_code"],
            student_markdown=submission["student_markdown"],
            solution_code=submission["solution_code"],
            assignment_info=submission["assignment_info"],
            rubric_elements=submission["rubric_elements"]
        )
        
        total_time = time.time() - start_time
        
        # Display results
        print_detailed_results(result, submission["assignment_info"])
        
        return True
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        print("💡 Make sure Ollama is running with the required models")
        return False

def print_detailed_results(result, assignment_info):
    """Print detailed grading results"""
    print("\n" + "🎉" + "=" * 78 + "🎉")
    print("                           GRADING RESULTS")
    print("🎉" + "=" * 78 + "🎉")
    
    # Overall score
    final_score = result.get('final_score', 0)
    print(f"\n📊 FINAL SCORE: {final_score}/100")
    
    # Letter grade
    if final_score >= 90:
        letter_grade = "A"
        emoji = "🌟"
    elif final_score >= 80:
        letter_grade = "B"
        emoji = "👍"
    elif final_score >= 70:
        letter_grade = "C"
        emoji = "👌"
    elif final_score >= 60:
        letter_grade = "D"
        emoji = "⚠️"
    else:
        letter_grade = "F"
        emoji = "❌"
    
    print(f"📝 LETTER GRADE: {letter_grade} {emoji}")
    print()
    
    # Technical Analysis Results
    technical = result.get('technical_analysis', {})
    print("🔧 TECHNICAL CODE ANALYSIS (Qwen 3.0 Coder 30B)")
    print("-" * 50)
    print(f"Overall Technical Score: {technical.get('technical_score', 'N/A')}/100")
    print(f"Syntax Correctness: {technical.get('syntax_correctness', 'N/A')}/100")
    print(f"Logic Correctness: {technical.get('logic_correctness', 'N/A')}/100")
    print(f"Code Efficiency: {technical.get('code_efficiency', 'N/A')}/100")
    print(f"Best Practices: {technical.get('best_practices', 'N/A')}/100")
    
    # Technical Issues
    issues = technical.get('technical_issues', [])
    if issues:
        print("\n🔍 Technical Issues Found:")
        for i, issue in enumerate(issues[:3], 1):
            print(f"  {i}. {issue}")
    
    # Technical Strengths
    strengths = technical.get('technical_strengths', [])
    if strengths:
        print("\n✅ Technical Strengths:")
        for i, strength in enumerate(strengths[:3], 1):
            print(f"  {i}. {strength}")
    
    print()
    
    # Comprehensive Feedback Results
    feedback = result.get('comprehensive_feedback', {})
    print("📝 COMPREHENSIVE FEEDBACK (Gemma 3.0 27B)")
    print("-" * 50)
    print(f"Overall Score: {feedback.get('overall_score', 'N/A')}/100")
    print(f"Conceptual Understanding: {feedback.get('conceptual_understanding', 'N/A')}/100")
    print(f"Communication Clarity: {feedback.get('communication_clarity', 'N/A')}/100")
    print(f"Data Interpretation: {feedback.get('data_interpretation', 'N/A')}/100")
    print(f"Methodology: {feedback.get('methodology_appropriateness', 'N/A')}/100")
    
    # Detailed Feedback
    detailed = feedback.get('detailed_feedback', {})
    
    # Strengths
    strengths = detailed.get('strengths', [])
    if strengths:
        print(f"\n🌟 What Deon Did Well:")
        for i, strength in enumerate(strengths[:3], 1):
            print(f"  {i}. {strength}")
    
    # Areas for Improvement
    improvements = detailed.get('areas_for_improvement', [])
    if improvements:
        print(f"\n📈 Areas for Improvement:")
        for i, improvement in enumerate(improvements[:3], 1):
            print(f"  {i}. {improvement}")
    
    # Learning Suggestions
    suggestions = detailed.get('learning_suggestions', [])
    if suggestions:
        print(f"\n💡 Learning Suggestions:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"  {i}. {suggestion}")
    
    # Instructor Comments
    comments = feedback.get('instructor_comments', '')
    if comments:
        print(f"\n👨‍🏫 INSTRUCTOR COMMENTS:")
        print("-" * 30)
        # Wrap text nicely
        import textwrap
        wrapped_comments = textwrap.fill(comments, width=70)
        print(wrapped_comments)
    
    print()
    
    # Performance Statistics
    stats = result.get('grading_stats', {})
    print("⚡ GRADING PERFORMANCE STATISTICS")
    print("-" * 40)
    print(f"Total Grading Time: {stats.get('total_time', 'N/A'):.1f}s")
    print(f"Parallel Processing Time: {stats.get('parallel_time', 'N/A'):.1f}s")
    print(f"Efficiency Gain: {stats.get('parallel_efficiency', 'N/A'):.1f}x speedup")
    print(f"Code Analysis Time: {stats.get('code_analysis_time', 'N/A'):.1f}s")
    print(f"Feedback Generation Time: {stats.get('feedback_generation_time', 'N/A'):.1f}s")
    
    # Models Used
    models = stats.get('models_used', {})
    print(f"\n🤖 AI Models Used:")
    print(f"Code Analyzer: {models.get('code_analyzer', 'N/A')}")
    print(f"Feedback Generator: {models.get('feedback_generator', 'N/A')}")
    
    print("\n" + "🎓" + "=" * 78 + "🎓")

def main():
    """Main demo function"""
    print_grading_header()
    
    # Get sample submission
    submission = create_sample_deon_submission()
    
    # Show submission info
    print_submission_info(submission)
    
    # Show code preview
    print_code_preview(submission["student_code"])
    
    # Show markdown preview
    print_markdown_preview(submission["student_markdown"])
    
    # Ask user if they want to see real grading
    print("🤔 Would you like to see the actual grading with your optimized models?")
    print("   This will use your Qwen 3.0 Coder + Gemma 3.0 setup")
    print("   (Make sure Ollama is running)")
    print()
    
    choice = input("Proceed with real grading? (y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        print()
        success = demo_grading_results()
        
        if success:
            print("\n🎉 Demo completed successfully!")
            print("💡 This is how your system will grade all student submissions")
        else:
            print("\n⚠️ Demo failed - check Ollama setup")
    else:
        print("\n👋 Demo cancelled. Run again when ready!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")