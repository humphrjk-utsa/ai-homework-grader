#!/usr/bin/env python3
"""
Grading Validation System
Ensures mathematical consistency in automatic grading
"""

from typing import Dict, List, Any, Tuple
import json

class GradingValidator:
    """Validates grading calculations for consistency"""
    
    def __init__(self, max_points: float = 37.5):
        self.max_points = max_points
        self.rubric_weights = {
            "technical_execution": 0.25,
            "business_thinking": 0.30,
            "data_analysis": 0.25,
            "communication": 0.20
        }
    
    def validate_grading_result(self, result: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a grading result for mathematical consistency
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if required fields exist
        required_fields = ['final_score', 'component_scores', 'component_percentages']
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")
                return False, errors
        
        # Get values
        final_score = result.get('final_score', 0)
        component_scores = result.get('component_scores', {})
        component_percentages = result.get('component_percentages', {})
        
        # Validate component score calculation
        expected_technical = (component_percentages.get('technical_score', 0) / 100) * 9.375
        expected_business = (component_percentages.get('business_understanding', 0) / 100) * 11.25
        expected_analysis = (component_percentages.get('data_interpretation', 0) / 100) * 9.375
        expected_communication = (component_percentages.get('communication_clarity', 0) / 100) * 7.5
        
        actual_technical = component_scores.get('technical_points', 0)
        actual_business = component_scores.get('business_points', 0)
        actual_analysis = component_scores.get('analysis_points', 0)
        actual_communication = component_scores.get('communication_points', 0)
        
        # Check component calculations (allow 0.2 tolerance for rounding)
        tolerance = 0.2  # Increased to handle floating-point rounding
        
        if abs(expected_technical - actual_technical) > tolerance:
            errors.append(f"Technical points mismatch: expected {expected_technical:.1f}, got {actual_technical:.1f}")
        
        if abs(expected_business - actual_business) > tolerance:
            errors.append(f"Business points mismatch: expected {expected_business:.1f}, got {actual_business:.1f}")
        
        if abs(expected_analysis - actual_analysis) > tolerance:
            errors.append(f"Analysis points mismatch: expected {expected_analysis:.1f}, got {actual_analysis:.1f}")
        
        if abs(expected_communication - actual_communication) > tolerance:
            errors.append(f"Communication points mismatch: expected {expected_communication:.1f}, got {actual_communication:.1f}")
        
        # Check total calculation
        bonus_points = component_scores.get('bonus_points', 0)
        expected_total = actual_technical + actual_business + actual_analysis + actual_communication + bonus_points
        
        if abs(expected_total - final_score) > tolerance:
            errors.append(f"Total score mismatch: expected {expected_total:.1f}, got {final_score:.1f}")
        
        # Check score bounds
        if final_score < 0:
            errors.append(f"Final score cannot be negative: {final_score}")
        
        if final_score > self.max_points:
            errors.append(f"Final score exceeds maximum: {final_score} > {self.max_points}")
        
        # Check percentage consistency
        final_percentage = result.get('final_score_percentage', 0)
        expected_percentage = (final_score / self.max_points) * 100
        
        if abs(expected_percentage - final_percentage) > tolerance:
            errors.append(f"Percentage mismatch: expected {expected_percentage:.1f}%, got {final_percentage:.1f}%")
        
        # Check component percentages are within bounds
        for component, percentage in component_percentages.items():
            if percentage < 0 or percentage > 100:
                errors.append(f"{component} percentage out of bounds: {percentage}%")
        
        return len(errors) == 0, errors
    
    def validate_batch_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of grading results
        
        Returns:
            Summary of validation results
        """
        total_results = len(results)
        valid_results = 0
        all_errors = []
        
        for i, result in enumerate(results):
            is_valid, errors = self.validate_grading_result(result)
            
            if is_valid:
                valid_results += 1
            else:
                student_name = result.get('assignment_info', {}).get('student_name', f'Student_{i}')
                for error in errors:
                    all_errors.append(f"{student_name}: {error}")
        
        return {
            "total_results": total_results,
            "valid_results": valid_results,
            "invalid_results": total_results - valid_results,
            "validation_rate": (valid_results / total_results) * 100 if total_results > 0 else 0,
            "errors": all_errors
        }
    
    def fix_calculation_errors(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix calculation errors in a grading result"""
        
        print(f"🔧 VALIDATOR FIX: Input final_score = {result.get('final_score')}")
        print(f"🔧 VALIDATOR FIX: self.max_points = {self.max_points}")
        
        # Recalculate component scores from percentages
        component_percentages = result.get('component_percentages', {})
        
        # Use dynamic weights based on max_points
        technical_points = (component_percentages.get('technical_score', 0) / 100) * (self.max_points * 0.25)
        business_points = (component_percentages.get('business_understanding', 0) / 100) * (self.max_points * 0.30)
        analysis_points = (component_percentages.get('data_interpretation', 0) / 100) * (self.max_points * 0.25)
        communication_points = (component_percentages.get('communication_clarity', 0) / 100) * (self.max_points * 0.20)
        
        # Keep existing bonus points
        bonus_points = result.get('component_scores', {}).get('bonus_points', 0)
        
        # Recalculate total
        final_score = technical_points + business_points + analysis_points + communication_points + bonus_points
        final_score = min(self.max_points, final_score)  # Cap at maximum
        
        # Recalculate percentage
        final_percentage = (final_score / self.max_points) * 100
        
        # Update result
        result['final_score'] = round(final_score, 1)
        result['final_score_percentage'] = round(final_percentage, 1)
        
        print(f"🔧 VALIDATOR FIX: Output final_score = {result['final_score']}")
        result['component_scores'] = {
            'technical_points': round(technical_points, 1),
            'business_points': round(business_points, 1),
            'analysis_points': round(analysis_points, 1),
            'communication_points': round(communication_points, 1),
            'bonus_points': round(bonus_points, 1)
        }
        
        return result
    
    def generate_validation_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a detailed validation report"""
        
        validation_summary = self.validate_batch_results(results)
        
        report = f"""
GRADING VALIDATION REPORT
========================
Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total Assignments: {validation_summary['total_results']}
Valid Results: {validation_summary['valid_results']}
Invalid Results: {validation_summary['invalid_results']}
Validation Rate: {validation_summary['validation_rate']:.1f}%

"""
        
        if validation_summary['errors']:
            report += "ERRORS FOUND:\n"
            report += "-" * 40 + "\n"
            for error in validation_summary['errors']:
                report += f"• {error}\n"
        else:
            report += "✅ All grading calculations are mathematically consistent!\n"
        
        # Add score distribution
        if results:
            scores = [r.get('final_score', 0) for r in results]
            percentages = [r.get('final_score_percentage', 0) for r in results]
            
            report += f"\nSCORE DISTRIBUTION:\n"
            report += "-" * 20 + "\n"
            report += f"Average Score: {sum(scores)/len(scores):.1f}/{self.max_points}\n"
            report += f"Average Percentage: {sum(percentages)/len(percentages):.1f}%\n"
            report += f"Highest Score: {max(scores):.1f}/{self.max_points}\n"
            report += f"Lowest Score: {min(scores):.1f}/{self.max_points}\n"
        
        return report

def validate_grading_system():
    """Test the validation system"""
    validator = GradingValidator()
    
    # Test with sample data
    test_result = {
        "final_score": 34.9,
        "final_score_percentage": 93.1,
        "component_scores": {
            "technical_points": 8.6,
            "business_points": 10.7,
            "analysis_points": 8.6,
            "communication_points": 7.0,
            "bonus_points": 0.0
        },
        "component_percentages": {
            "technical_score": 92,
            "business_understanding": 95,
            "data_interpretation": 92,
            "communication_clarity": 94
        },
        "assignment_info": {
            "student_name": "Test Student"
        }
    }
    
    is_valid, errors = validator.validate_grading_result(test_result)
    
    print("Validation Test Results:")
    print(f"Valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ No errors found!")

if __name__ == "__main__":
    import time
    validate_grading_system()