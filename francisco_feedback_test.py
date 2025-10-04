#!/usr/bin/env python3
"""
Test Francisco's Data Cleaning Assignment
Generate natural instructor feedback for his comprehensive submission
"""

from business_analytics_grader import BusinessAnalyticsGrader
import json

def grade_francisco_assignment():
    """Grade Francisco's data cleaning assignment"""
    
    print("🧪 Grading Francisco's Data Cleaning Assignment")
    print("=" * 60)
    
    # Francisco's code (comprehensive R data cleaning)
    student_code = '''
# Load required packages for data cleaning 
library(tidyverse) # For data manipulation and visualization  
getwd()

# Import the messy sales dataset
messy_sales <- read_csv("/workspaces/assignment-2-version3-zfrank33/data/messy_sales_data.csv")
print("Messy sales dataset imported successfully!")
print(paste("Dataset contains", nrow(messy_sales), "rows and", ncol(messy_sales), "columns"))

# Inspect the messy dataset
print("=== DATASET OVERVIEW ===")
head(messy_sales, 10)
str(messy_sales)
summary(messy_sales)

# Calculate missing values
total_missing <- sum(is.na(messy_sales))
missing_per_column <- colSums(is.na(messy_sales))
incomplete_rows <- messy_sales[!complete.cases(messy_sales), ]

# Missing value treatment - removal
messy_sales_complete <- messy_sales[complete.cases(messy_sales), ]

# Missing value treatment - imputation
get_mode <- function(v) {
  v <- v[!is.na(v)]
  if (length(v) == 0) return(NA)
  u <- unique(v)
  u[which.max(tabulate(match(v, u)))]
}

sales_imputed <- messy_sales
name_mode <- get_mode(sales_imputed$Customer_Name)
sales_imputed$Customer_Name[is.na(sales_imputed$Customer_Name)] <- name_mode

qty_median <- median(sales_imputed$Quantity, na.rm = TRUE)
sales_imputed$Quantity[is.na(sales_imputed$Quantity)] <- qty_median

# Outlier detection using IQR
Q1_sales <- quantile(sales_imputed$Sales_Amount, 0.25, na.rm = TRUE)
Q3_sales <- quantile(sales_imputed$Sales_Amount, 0.75, na.rm = TRUE)
IQR_sales <- IQR(sales_imputed$Sales_Amount, na.rm = TRUE)
upper_threshold <- Q3_sales + 1.5 * IQR_sales
lower_threshold <- Q1_sales - 1.5 * IQR_sales

# Outlier treatment - capping/winsorization
q1 <- quantile(sales_imputed$Sales_Amount, 0.25, na.rm = TRUE)
q3 <- quantile(sales_imputed$Sales_Amount, 0.75, na.rm = TRUE)
iqr <- q3 - q1
lower_cap <- q1 - 1.5 * iqr
upper_cap <- q3 + 1.5 * iqr

sales_outliers_capped <- sales_imputed
sales_outliers_capped$Sales_Amount <- ifelse(
  sales_imputed$Sales_Amount < lower_cap, lower_cap,
  ifelse(sales_imputed$Sales_Amount > upper_cap, upper_cap, sales_imputed$Sales_Amount)
)

# Final dataset selection
final_dataset <- sales_outliers_capped
'''
    
    # Francisco's written analysis (excellent reflection and justification)
    student_markdown = '''
# Homework Assignment - Lesson 2: Data Cleaning
**Student Name:** Francisco Guadarrama  
**Date:** 9/11/2025  
**Course:** Data Management

## Part 1: Data Import and Initial Assessment

### 1.3 Initial Data Assessment
**Data Quality Assessment:**

**YOUR OBSERVATIONS:**
1. **Missing Values:** Customer_Name has NA's, Sales_Amount has 22 NA's and Purchase_Date has 14 NA's.
2. **Potential Outliers:** The -$100 and the $100,000 in column Sales_Amount and the -1.00 and max of 100 in the Quantity columns are potential outliers.
3. **Data Inconsistencies:** The Product_Category column contains inconsistent capitalization (Electronics vs electronics).
4. **Data Types:** Purchase_Date is using appropriate data types but contains NA's and that will affect time-based analysis. Sales_Amount is using appropriate data types but also contains NA's.
5. **Invalid Values:** It is hard to buy a -1.00 amount of most things unless it's a return (which I assume it is).

## Part 2: Missing Value Analysis and Treatment

### Analysis Questions:

**Which approach would you recommend for this dataset and why?**
For analyses that depend on accurate monetary totals or pricing, drop rows with missing Sales_Amount and treat negative Sales_Amount as returns with a flag. Sales_Amount has strong skew and extreme outliers (max 100,000). Median imputation on numeric fields can distort distributions less than mean imputation, but for a key target like Sales_Amount, any imputation can bias totals and variance. Removing observations with missing Sales_Amount is usually safer for revenue analyses, especially with only 22 NAs out of 200 (11% loss). Do not impute Sales_Amount.

**What are the trade-offs between removal and imputation?**
Complete-case removal keeps only observed data without making model-based assumptions and is simple to implement and interpret, but it reduces sample size (about 11% here), which lowers statistical power, and can introduce bias if the data are not missing completely at random. Imputation preserves sample size and power and, for variables like Quantity or categorical fields, median or mode imputation is simple and often acceptable; however, it can bias distributions toward the center by shrinking variance, may distort totals, relationships, and inference if applied to key targets like Sales_Amount.

## Part 4: Final Data Quality Assessment and Decision Making

### Justification for Your Choice:
I selected sales_outliers_capped as the final cleaned dataset.

**Sample size preservation** - Winsorization caps extreme values instead of deleting rows, keeping the full sample size intact. This is important for maintaining statistical power and avoiding sampling bias that can arise when rare but valid observations are removed.

**Data quality improvements** - Capping using the IQR rule reduces the undue influence of extreme values on means, variances, correlations, and downstream models while preserving the original distribution's central tendency and rank order for most observations.

**Business impact** - Sales processes often generate legitimate spikes (e.g., promotions, bulk orders). Completely removing such cases risks losing meaningful revenue signals. Capping preserves their presence while preventing them from dominating KPIs and models.

**Analysis requirements** - The project's outlier strategy explicitly called for Option B (Capping). The chosen dataset aligns with that requirement. Capped data is well-suited for models sensitive to outliers and for reporting where stability is valued.
'''
    
    grader = BusinessAnalyticsGrader()
    
    if not grader.use_distributed_mlx:
        print("❌ Distributed MLX not available")
        return False
    
    print("🚀 Generating comprehensive feedback for Francisco's excellent work...")
    
    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code='# Complete data cleaning solution with all steps',
            assignment_info={
                'title': 'Assignment 2: Data Cleaning - Handling Missing Values and Outliers',
                'name': 'Data Cleaning Assignment',
                'description': 'Comprehensive data cleaning with missing values and outlier treatment'
            },
            rubric_elements={}
        )
        
        print(f"✅ Grading completed!")
        print(f"📊 Final Score: {result['final_score']}/37.5 ({result['final_score_percentage']:.1f}%)")
        
        # Display the natural feedback
        feedback = result.get('comprehensive_feedback', {})
        
        print(f"\n" + "="*80)
        print(f"📝 INSTRUCTOR FEEDBACK FOR FRANCISCO")
        print(f"="*80)
        
        comments = feedback.get('instructor_comments', '')
        print(comments)
        
        print(f"\n🤔 REFLECTION & CRITICAL THINKING:")
        print("-" * 50)
        detailed = feedback.get('detailed_feedback', {})
        reflection_assessment = detailed.get('reflection_assessment', [])
        for i, comment in enumerate(reflection_assessment, 1):
            print(f"{i}. {comment}")
        
        print(f"\n💪 ANALYTICAL STRENGTHS:")
        print("-" * 50)
        strengths = detailed.get('analytical_strengths', [])
        for i, strength in enumerate(strengths, 1):
            print(f"{i}. {strength}")
        
        print(f"\n🏢 BUSINESS APPLICATION:")
        print("-" * 50)
        business_app = detailed.get('business_application', [])
        for i, app in enumerate(business_app, 1):
            print(f"{i}. {app}")
        
        print(f"\n📈 LEARNING DEMONSTRATION:")
        print("-" * 50)
        learning = detailed.get('learning_demonstration', [])
        for i, learn in enumerate(learning, 1):
            print(f"{i}. {learn}")
        
        print(f"\n🔧 TECHNICAL ANALYSIS:")
        print("-" * 50)
        technical = result.get('technical_analysis', {})
        code_strengths = technical.get('code_strengths', [])
        for i, strength in enumerate(code_strengths, 1):
            print(f"{i}. {strength}")
        
        print(f"\n💡 CODE SUGGESTIONS:")
        print("-" * 50)
        code_suggestions = technical.get('code_suggestions', [])
        for i, suggestion in enumerate(code_suggestions, 1):
            print(f"{i}. {suggestion}")
        
        # Performance metrics
        perf_diag = result.get('performance_diagnostics', {})
        if perf_diag:
            print(f"\n⚡ PERFORMANCE METRICS:")
            print("-" * 50)
            qwen_perf = perf_diag.get('qwen_performance', {})
            gemma_perf = perf_diag.get('gemma_performance', {})
            print(f"🔧 Qwen (Code Analysis): {qwen_perf.get('tokens_per_second', 0):.1f} tok/s")
            print(f"📝 GPT-OSS (Feedback): {gemma_perf.get('tokens_per_second', 0):.1f} tok/s")
            print(f"🚀 Combined Throughput: {perf_diag.get('combined_metrics', {}).get('combined_throughput_tokens_per_second', 0):.1f} tok/s")
        
        return True
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = grade_francisco_assignment()
    if success:
        print(f"\n🎉 Francisco's assignment graded successfully!")
        print(f"💡 This demonstrates the improved natural feedback generation system.")
    else:
        print(f"\n❌ Grading failed - check system status.")