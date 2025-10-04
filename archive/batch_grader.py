#!/usr/bin/env python3
"""
Batch Grading System with Validation
Ensures mathematical consistency across all assignments
"""

import json
import time
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator

class BatchGrader:
    """Batch grading system with built-in validation"""
    
    def __init__(self):
        self.grader = BusinessAnalyticsGrader()
        self.validator = GradingValidator()
        self.results = []
        self.validation_errors = []
    
    def grade_batch(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Grade multiple submissions with validation
        
        Args:
            submissions: List of submission dictionaries containing:
                - student_code: R code
                - student_markdown: Written analysis
                - solution_code: Reference solution
                - assignment_info: Assignment details
                - rubric_elements: Grading rubric
        
        Returns:
            List of validated grading results
        """
        
        print(f"🎯 Starting batch grading of {len(submissions)} submissions...")
        print("🔍 Validation enabled to ensure mathematical consistency")
        
        results = []
        start_time = time.time()
        
        for i, submission in enumerate(submissions, 1):
            student_name = submission.get('assignment_info', {}).get('student_name', f'Student_{i}')
            print(f"\n📋 Grading {i}/{len(submissions)}: {student_name}")
            
            try:
                # Grade the submission
                result = self.grader.grade_submission(
                    student_code=submission['student_code'],
                    student_markdown=submission['student_markdown'],
                    solution_code=submission.get('solution_code', ''),
                    assignment_info=submission['assignment_info'],
                    rubric_elements=submission['rubric_elements']
                )
                
                # Validate the result
                is_valid, errors = self.validator.validate_grading_result(result)
                
                if not is_valid:
                    print(f"⚠️ Validation errors found for {student_name}:")
                    for error in errors:
                        print(f"   • {error}")
                    
                    # Attempt to fix calculation errors
                    print(f"🔧 Attempting to fix calculation errors...")
                    result = self.validator.fix_calculation_errors(result)
                    
                    # Re-validate
                    is_valid_fixed, errors_fixed = self.validator.validate_grading_result(result)
                    
                    if is_valid_fixed:
                        print(f"✅ Calculation errors fixed for {student_name}")
                    else:
                        print(f"❌ Could not fix all errors for {student_name}")
                        self.validation_errors.extend([f"{student_name}: {e}" for e in errors_fixed])
                
                result['validation_status'] = 'valid' if is_valid else 'fixed' if is_valid_fixed else 'invalid'
                results.append(result)
                
                # Show progress
                final_score = result.get('final_score', 0)
                final_percentage = result.get('final_score_percentage', 0)
                print(f"✅ {student_name}: {final_score}/37.5 ({final_percentage}%)")
                
            except Exception as e:
                print(f"❌ Grading failed for {student_name}: {e}")
                # Create error result
                error_result = {
                    "final_score": 0,
                    "final_score_percentage": 0,
                    "max_points": 37.5,
                    "assignment_info": submission['assignment_info'],
                    "error": str(e),
                    "validation_status": "error"
                }
                results.append(error_result)
        
        total_time = time.time() - start_time
        
        # Generate validation report
        validation_summary = self.validator.validate_batch_results(results)
        
        print(f"\n🎉 Batch grading complete!")
        print(f"📊 Total time: {total_time:.1f}s")
        print(f"📊 Average per submission: {total_time/len(submissions):.1f}s")
        print(f"✅ Validation rate: {validation_summary['validation_rate']:.1f}%")
        
        if validation_summary['errors']:
            print(f"⚠️ {len(validation_summary['errors'])} validation errors found")
        
        self.results = results
        return results
    
    def export_results(self, output_path: str = "grading_results.xlsx"):
        """Export results to Excel with validation report"""
        
        if not self.results:
            print("❌ No results to export")
            return
        
        # Prepare data for Excel
        export_data = []
        
        for result in self.results:
            assignment_info = result.get('assignment_info', {})
            component_scores = result.get('component_scores', {})
            component_percentages = result.get('component_percentages', {})
            
            row = {
                'Student Name': assignment_info.get('student_name', 'Unknown'),
                'Assignment': assignment_info.get('title', 'Unknown'),
                'Final Score': result.get('final_score', 0),
                'Final Percentage': result.get('final_score_percentage', 0),
                'Letter Grade': self._calculate_letter_grade(result.get('final_score_percentage', 0)),
                'Technical Points': component_scores.get('technical_points', 0),
                'Business Points': component_scores.get('business_points', 0),
                'Analysis Points': component_scores.get('analysis_points', 0),
                'Communication Points': component_scores.get('communication_points', 0),
                'Bonus Points': component_scores.get('bonus_points', 0),
                'Technical %': component_percentages.get('technical_score', 0),
                'Business %': component_percentages.get('business_understanding', 0),
                'Analysis %': component_percentages.get('data_interpretation', 0),
                'Communication %': component_percentages.get('communication_clarity', 0),
                'Validation Status': result.get('validation_status', 'unknown'),
                'Grading Time': result.get('grading_timestamp', ''),
                'Error': result.get('error', '')
            }
            export_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(export_data)
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main results
            df.to_excel(writer, sheet_name='Grading Results', index=False)
            
            # Summary statistics
            summary_data = {
                'Metric': [
                    'Total Submissions',
                    'Average Score',
                    'Average Percentage', 
                    'Highest Score',
                    'Lowest Score',
                    'Validation Rate',
                    'A Grades',
                    'B Grades',
                    'C Grades'
                ],
                'Value': [
                    len(self.results),
                    f"{df['Final Score'].mean():.1f}/37.5",
                    f"{df['Final Percentage'].mean():.1f}%",
                    f"{df['Final Score'].max():.1f}/37.5",
                    f"{df['Final Score'].min():.1f}/37.5",
                    f"{(df['Validation Status'] == 'valid').sum() / len(df) * 100:.1f}%",
                    len([g for g in df['Letter Grade'] if g.startswith('A')]),
                    len([g for g in df['Letter Grade'] if g.startswith('B')]),
                    len([g for g in df['Letter Grade'] if g.startswith('C')])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Validation report
            validation_report = self.validator.generate_validation_report(self.results)
            validation_df = pd.DataFrame({'Validation Report': validation_report.split('\n')})
            validation_df.to_excel(writer, sheet_name='Validation Report', index=False)
        
        print(f"📊 Results exported to {output_path}")
        print(f"📋 Sheets: Grading Results, Summary, Validation Report")
    
    def _calculate_letter_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage"""
        if percentage >= 97:
            return "A+"
        elif percentage >= 93:
            return "A"
        elif percentage >= 90:
            return "A-"
        elif percentage >= 87:
            return "B+"
        elif percentage >= 83:
            return "B"
        elif percentage >= 80:
            return "B-"
        else:
            return "C+"
    
    def print_validation_summary(self):
        """Print validation summary"""
        if not self.results:
            print("❌ No results to validate")
            return
        
        validation_summary = self.validator.validate_batch_results(self.results)
        
        print("\n📊 VALIDATION SUMMARY")
        print("=" * 40)
        print(f"Total Assignments: {validation_summary['total_results']}")
        print(f"Valid Results: {validation_summary['valid_results']}")
        print(f"Invalid Results: {validation_summary['invalid_results']}")
        print(f"Validation Rate: {validation_summary['validation_rate']:.1f}%")
        
        if validation_summary['errors']:
            print(f"\n⚠️ Validation Errors:")
            for error in validation_summary['errors'][:10]:  # Show first 10
                print(f"  • {error}")
            
            if len(validation_summary['errors']) > 10:
                print(f"  ... and {len(validation_summary['errors']) - 10} more errors")

def create_sample_submissions() -> List[Dict[str, Any]]:
    """Create sample submissions for testing"""
    
    sample_code = '''
library(dplyr)
library(ggplot2)
data <- read.csv("data.csv")
summary(data)
clean_data <- data %>% filter(!is.na(grade))
mean_grade <- mean(clean_data$grade)
ggplot(clean_data, aes(x=grade)) + geom_histogram()
'''
    
    sample_markdown = '''
# Analysis Report
This analysis examines student performance data.

## Reflection Questions
1. What was challenging? [Learning R syntax was difficult but rewarding]
2. What did you learn? [Data cleaning is crucial for accurate analysis]
'''
    
    submissions = []
    
    for i in range(3):
        submission = {
            "student_code": sample_code,
            "student_markdown": sample_markdown,
            "solution_code": "",
            "assignment_info": {
                "title": "Business Analytics Assignment 1",
                "student_name": f"Test Student {i+1}",
                "course": "Business Analytics 101"
            },
            "rubric_elements": {
                "technical_execution": {"weight": 0.25, "max_score": 37.5},
                "business_thinking": {"weight": 0.30, "max_score": 37.5},
                "data_analysis": {"weight": 0.25, "max_score": 37.5},
                "communication": {"weight": 0.20, "max_score": 37.5}
            }
        }
        submissions.append(submission)
    
    return submissions

def main():
    """Test batch grading with validation"""
    
    print("🧪 Testing Batch Grading with Validation")
    print("=" * 50)
    
    # Create sample submissions
    submissions = create_sample_submissions()
    
    # Initialize batch grader
    batch_grader = BatchGrader()
    
    # Grade submissions
    results = batch_grader.grade_batch(submissions)
    
    # Print validation summary
    batch_grader.print_validation_summary()
    
    # Export results
    batch_grader.export_results("test_grading_results.xlsx")

if __name__ == "__main__":
    main()