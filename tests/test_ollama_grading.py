#!/usr/bin/env python3
"""
Test Ollama Two-Model Grading System
"""

from ollama_two_model_grader import OllamaTwoModelGrader
import json

def test_ollama_grading():
    """Test the Ollama grading system"""
    
    print("🧪 Testing Ollama Two-Model Grading System")
    print("=" * 50)
    
    # Initialize grader
    grader = OllamaTwoModelGrader()
    
    # Check system status
    status = grader.get_system_status()
    print(f"System Status: {json.dumps(status, indent=2)}")
    
    if not status['ollama_connected']:
        print("❌ Ollama not connected")
        return False
    
    # Test data
    student_code = """
# Data Analysis Assignment
library(dplyr)
library(ggplot2)

# Load data
data <- read.csv("dataset.csv")

# Basic statistics
summary(data)
mean_value <- mean(data$value, na.rm = TRUE)
print(paste("Mean value:", mean_value))

# Create visualization
ggplot(data, aes(x = category, y = value)) +
  geom_boxplot() +
  labs(title = "Distribution by Category")
"""
    
    student_markdown = """
## Analysis Summary

I analyzed the dataset to understand the distribution of values across different categories. 
The data shows interesting patterns with some categories having higher variability than others.

### Key Findings:
1. The mean value is approximately 45.2
2. Category A shows the highest median values
3. There are some outliers in Category C that need investigation

### Methodology:
I used descriptive statistics and box plots to visualize the data distribution.
"""
    
    solution_code = """
# Reference Solution
library(dplyr)
library(ggplot2)

data <- read.csv("dataset.csv")
summary_stats <- data %>%
  group_by(category) %>%
  summarise(
    mean_val = mean(value, na.rm = TRUE),
    median_val = median(value, na.rm = TRUE),
    sd_val = sd(value, na.rm = TRUE)
  )

ggplot(data, aes(x = category, y = value)) +
  geom_boxplot() +
  geom_point(alpha = 0.3) +
  labs(title = "Value Distribution by Category",
       x = "Category", y = "Value")
"""
    
    assignment_info = {
        "title": "Data Exploration Assignment",
        "description": "Analyze the provided dataset and create visualizations"
    }
    
    rubric_elements = {
        "code_correctness": {"weight": 0.4, "max_score": 100},
        "data_analysis": {"weight": 0.3, "max_score": 100},
        "communication": {"weight": 0.3, "max_score": 100}
    }
    
    print("\n🚀 Starting test grading...")
    
    try:
        # Grade the submission
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        print("\n🎉 Grading Results:")
        print("=" * 30)
        print(f"Final Score: {result['final_score']}/100")
        
        # Technical Analysis
        technical = result.get('technical_analysis', {})
        print(f"\n🔧 Technical Analysis:")
        print(f"  Technical Score: {technical.get('technical_score', 'N/A')}/100")
        print(f"  Syntax Correctness: {technical.get('syntax_correctness', 'N/A')}/100")
        print(f"  Logic Correctness: {technical.get('logic_correctness', 'N/A')}/100")
        
        # Feedback
        feedback = result.get('comprehensive_feedback', {})
        print(f"\n📝 Comprehensive Feedback:")
        print(f"  Overall Score: {feedback.get('overall_score', 'N/A')}/100")
        print(f"  Conceptual Understanding: {feedback.get('conceptual_understanding', 'N/A')}/100")
        
        # Performance Stats
        stats = result.get('grading_stats', {})
        print(f"\n⚡ Performance Stats:")
        print(f"  Total Time: {stats.get('total_time', 'N/A'):.1f}s")
        print(f"  Parallel Time: {stats.get('parallel_time', 'N/A'):.1f}s")
        print(f"  Efficiency Gain: {stats.get('parallel_efficiency', 'N/A'):.1f}x")
        print(f"  Code Analysis Time: {stats.get('code_analysis_time', 'N/A'):.1f}s")
        print(f"  Feedback Generation Time: {stats.get('feedback_generation_time', 'N/A'):.1f}s")
        
        # Models Used
        models = stats.get('models_used', {})
        print(f"\n🤖 Models Used:")
        print(f"  Code Analyzer: {models.get('code_analyzer', 'N/A')}")
        print(f"  Feedback Generator: {models.get('feedback_generator', 'N/A')}")
        
        print(f"\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama_grading()
    if success:
        print("\n🎉 Ollama grading system is working perfectly!")
        print("💡 You can now use your existing Qwen 3.0 Coder and Gemma 3.0 models")
        print("💡 Run: streamlit run pc_start.py (and select Ollama backend)")
    else:
        print("\n❌ Test failed. Check Ollama setup.")