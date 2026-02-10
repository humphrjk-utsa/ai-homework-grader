#!/usr/bin/env python3
"""
Smart Output Validator
Uses solution notebook + rubric to dynamically validate outputs
Then uses AI models to analyze discrepancies
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class SmartOutputValidator:
    """
    Dynamically validates outputs by comparing with solution notebook
    Uses rubric to determine what to check
    """
    
    def __init__(
        self,
        solution_notebook_path: str,
        rubric_path: str,
        numerical_tolerance: float = 0.05,
        row_count_tolerance: int = 5
    ):
        self.solution_notebook_path = solution_notebook_path
        self.rubric_path = rubric_path
        self.numerical_tolerance = numerical_tolerance
        self.row_count_tolerance = row_count_tolerance
        
        # Load rubric first (needed for required_variables)
        with open(rubric_path, 'r') as f:
            self.rubric = json.load(f)
        
        # Get required variables from rubric
        self.required_variables = self.rubric.get('autograder_checks', {}).get('required_variables', [])
        
        # Load solution notebook
        with open(solution_notebook_path, 'r') as f:
            self.solution_notebook = json.load(f)
        
        # Extract solution outputs
        self.solution_outputs = self._extract_all_outputs(self.solution_notebook)
    
    def validate_student_outputs(self, student_notebook_path: str) -> Dict[str, Any]:
        """
        Compare student outputs with solution outputs
        """
        # Load student notebook
        with open(student_notebook_path, 'r') as f:
            student_notebook = json.load(f)
        
        # Extract student outputs
        student_outputs = self._extract_all_outputs(student_notebook)
        
        # Compare outputs
        comparisons = []
        
        # For each required variable, find and compare outputs
        for variable in self.required_variables:
            comparison = self._compare_variable_outputs(
                variable,
                student_outputs,
                self.solution_outputs
            )
            if comparison:
                comparisons.append(comparison)
        
        # Calculate overall match
        total_checks = len(comparisons)
        passed_checks = sum(1 for c in comparisons if c['match'])
        overall_match = passed_checks / total_checks if total_checks > 0 else 0
        
        # Categorize discrepancies
        discrepancies = [c for c in comparisons if not c['match']]
        
        return {
            'overall_match': overall_match,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'comparisons': comparisons,
            'discrepancies': discrepancies,
            'score_adjustment': self._calculate_adjustment(overall_match)
        }
    
    def _extract_all_outputs(self, notebook: Dict) -> Dict[str, List[Dict]]:
        """
        Extract all outputs with their context
        Returns: {variable_name: [outputs]}
        """
        outputs_by_variable = {}
        
        for idx, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                source = ''.join(cell['source'])
                
                # Find variable assignments - be more specific
                for variable in self.required_variables:
                    # Look for the exact assignment pattern
                    patterns = [
                        rf'^{variable}\s*<-',  # Start of line
                        rf'\n{variable}\s*<-',  # After newline
                        rf'#{variable}\s*<-',  # After comment
                    ]
                    
                    found = False
                    for pattern in patterns:
                        if re.search(pattern, source, re.MULTILINE):
                            found = True
                            break
                    
                    if found and variable not in outputs_by_variable:
                        # This cell creates this variable (first occurrence)
                        cell_outputs = []
                        
                        # Get outputs from this cell AND next 2 cells
                        # (Handles cases where errors/warnings appear before actual output)
                        for i in range(idx, min(idx + 3, len(notebook['cells']))):
                            for output in notebook['cells'][i].get('outputs', []):
                                if 'text' in output:
                                    text = ''.join(output['text'])
                                    cell_outputs.append({
                                        'text': text,
                                        'cell_index': i
                                    })
                        
                        if cell_outputs:
                            outputs_by_variable[variable] = cell_outputs
        
        return outputs_by_variable
    
    def _compare_variable_outputs(
        self,
        variable: str,
        student_outputs: Dict,
        solution_outputs: Dict
    ) -> Optional[Dict]:
        """
        Compare outputs for a specific variable
        Context-aware: Only look in the section where variable is created
        """
        if variable not in solution_outputs:
            return None
        
        solution_output = solution_outputs.get(variable, [])
        solution_values = self._extract_values(solution_output)
        
        # Look in the specific cell(s) for this variable
        student_output = student_outputs.get(variable, [])
        
        if not student_output:
            return {
                'variable': variable,
                'match': False,
                'issue': 'no_output',
                'message': f'{variable}: No output found in section',
                'student_value': None,
                'solution_value': solution_values
            }
        
        # Extract values from student output
        student_values = self._extract_values(student_output)
        
        # Compare values
        match, issue, message = self._compare_values(
            student_values,
            solution_values,
            variable
        )
        
        return {
            'variable': variable,
            'match': match,
            'issue': issue if not match else None,
            'message': message,
            'student_value': student_values if not match else None,
            'solution_value': solution_values if not match else None
        }
    
    def _extract_values(self, outputs: List[Dict]) -> Dict[str, Any]:
        """
        Extract numerical values, row counts, etc. from outputs
        """
        values = {}
        
        for output in outputs:
            text = output['text']
            
            # Extract row counts
            row_patterns = [
                r'(\d+)\s*rows',
                r'Rows:\s*(\d+)',
                r'Total rows:\s*(\d+)',
                r'Result:\s*(\d+)',
            ]
            for pattern in row_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    values['row_count'] = int(match.group(1))
                    break
            
            # Extract numerical values (money, percentages, etc.)
            num_patterns = [
                r'\$\s*([\d,]+\.?\d*)',
                r'([\d,]+\.?\d+)',
            ]
            for pattern in num_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    nums = []
                    for m in matches:
                        try:
                            nums.append(float(m.replace(',', '')))
                        except:
                            pass
                    if nums:
                        values['numbers'] = nums
                        break
            
            # Extract counts
            count_patterns = [
                r'(\d+)\s*customers',
                r'(\d+)\s*orders',
                r'(\d+)\s*products',
                r'without.*?(\d+)',
                r'invalid.*?(\d+)',
            ]
            for pattern in count_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if 'counts' not in values:
                        values['counts'] = []
                    values['counts'].append(int(match.group(1)))
        
        return values
    
    def _compare_values(
        self,
        student_values: Dict,
        solution_values: Dict,
        variable: str
    ) -> tuple:
        """
        Compare extracted values - LENIENT: if numbers match, format doesn't matter
        Returns: (match: bool, issue: str, message: str)
        """
        # Strategy: Look for ANY matching numbers between student and solution
        # If key numbers match, consider it correct regardless of format
        
        # Check row counts
        if 'row_count' in solution_values:
            solution_rows = solution_values['row_count']
            
            # Look for this number ANYWHERE in student output
            if 'row_count' in student_values:
                student_rows = student_values['row_count']
                diff = abs(student_rows - solution_rows)
                
                if diff <= self.row_count_tolerance:
                    return True, None, f'{variable}: ✅ {student_rows} rows (matches {solution_rows})'
            
            # Also check if the number appears in the 'numbers' list
            if 'numbers' in student_values:
                for num in student_values['numbers']:
                    if abs(num - solution_rows) <= self.row_count_tolerance:
                        return True, None, f'{variable}: ✅ {int(num)} rows (matches {solution_rows})'
            
            # If we have counts, check those too
            if 'counts' in student_values:
                for count in student_values['counts']:
                    if abs(count - solution_rows) <= self.row_count_tolerance:
                        return True, None, f'{variable}: ✅ {count} rows (matches {solution_rows})'
            
            # Only fail if we couldn't find the number anywhere
            return False, 'row_count_mismatch', f'{variable}: Expected {solution_rows} rows, not found in output'
        
        # Check numerical values (revenue, thresholds, etc.)
        if 'numbers' in solution_values and solution_values['numbers']:
            solution_nums = solution_values['numbers']
            student_nums = student_values.get('numbers', [])
            
            # Look for ANY solution number in student numbers
            for solution_val in solution_nums:
                tolerance = abs(solution_val * self.numerical_tolerance)
                
                for student_val in student_nums:
                    diff = abs(student_val - solution_val)
                    
                    if diff <= tolerance:
                        return True, None, f'{variable}: ✅ {student_val:.2f} (matches {solution_val:.2f})'
            
            # If no match found
            if student_nums:
                return False, 'numerical_mismatch', f'{variable}: {student_nums[0]:.2f} (expected {solution_nums[0]:.2f} ±{self.numerical_tolerance*100}%)'
        
        # Check counts (customers without orders, etc.)
        if 'counts' in solution_values and solution_values['counts']:
            solution_counts = solution_values['counts']
            student_counts = student_values.get('counts', [])
            
            # Look for ANY solution count in student counts
            for solution_count in solution_counts:
                for student_count in student_counts:
                    if abs(student_count - solution_count) <= 2:
                        return True, None, f'{variable}: ✅ count {student_count} (matches {solution_count})'
            
            # If no match found
            if student_counts:
                return False, 'count_mismatch', f'{variable}: count {student_counts[0]} (expected {solution_counts[0]})'
        
        # If we got here and have any values, consider it a match
        # (This handles cases where format is different but we extracted something)
        if student_values:
            return True, None, f'{variable}: ✅ Output present'
        
        # No values found at all
        return False, 'no_output', f'{variable}: No output found'
    
    def _calculate_adjustment(self, overall_match: float) -> int:
        """Calculate score adjustment based on match percentage"""
        if overall_match >= 0.95:
            return 0
        elif overall_match >= 0.90:
            return -2
        elif overall_match >= 0.80:
            return -5
        elif overall_match >= 0.70:
            return -10
        else:
            return -15
    
    def generate_report(self, validation_result: Dict) -> str:
        """Generate human-readable report"""
        report = []
        report.append("=" * 80)
        report.append("OUTPUT VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        report.append(f"Overall Match: {validation_result['overall_match']*100:.1f}%")
        report.append(f"Checks Passed: {validation_result['passed_checks']}/{validation_result['total_checks']}")
        report.append(f"Score Adjustment: {validation_result['score_adjustment']} points")
        report.append("")
        
        # Show all comparisons
        report.append("=" * 80)
        report.append("DETAILED COMPARISONS")
        report.append("=" * 80)
        report.append("")
        
        for comp in validation_result['comparisons']:
            status = "✅" if comp['match'] else "❌"
            report.append(f"{status} {comp['message']}")
        
        # Show discrepancies
        if validation_result['discrepancies']:
            report.append("")
            report.append("=" * 80)
            report.append("DISCREPANCIES FOR AI ANALYSIS")
            report.append("=" * 80)
            report.append("")
            
            for disc in validation_result['discrepancies']:
                report.append(f"Variable: {disc['variable']}")
                report.append(f"  Issue: {disc['issue']}")
                report.append(f"  Student: {disc['student_value']}")
                report.append(f"  Expected: {disc['solution_value']}")
                report.append("")
        
        return "\n".join(report)
    
    def prepare_for_ai_analysis(self, validation_result: Dict, student_notebook_path: str) -> Dict:
        """
        Prepare discrepancies for AI model analysis
        Returns structured data for Qwen to analyze
        """
        # Load student notebook to get code context
        with open(student_notebook_path, 'r') as f:
            student_notebook = json.load(f)
        
        ai_analysis_data = {
            'overall_match': validation_result['overall_match'],
            'score_adjustment': validation_result['score_adjustment'],
            'discrepancies_with_context': []
        }
        
        for disc in validation_result['discrepancies']:
            variable = disc['variable']
            
            # Find the cell where this variable is created
            code_context = None
            output_context = None
            
            for idx, cell in enumerate(student_notebook['cells']):
                if cell['cell_type'] == 'code':
                    source = ''.join(cell['source'])
                    if f'{variable} <-' in source or f'{variable}<-' in source:
                        code_context = source
                        
                        # Get outputs from this cell + next 2
                        outputs = []
                        for i in range(idx, min(idx + 3, len(student_notebook['cells']))):
                            for output in student_notebook['cells'][i].get('outputs', []):
                                if 'text' in output:
                                    outputs.append(''.join(output['text']))
                        output_context = '\n'.join(outputs)
                        break
            
            ai_analysis_data['discrepancies_with_context'].append({
                'variable': variable,
                'issue': disc['issue'],
                'expected_value': disc['solution_value'],
                'student_value': disc['student_value'],
                'code': code_context,
                'output': output_context
            })
        
        return ai_analysis_data


def validate_outputs(
    student_notebook_path: str,
    solution_notebook_path: str,
    rubric_path: str
) -> Dict:
    """Convenience function"""
    validator = SmartOutputValidator(solution_notebook_path, rubric_path)
    return validator.validate_student_outputs(student_notebook_path)


if __name__ == "__main__":
    # Test
    validator = SmartOutputValidator(
        solution_notebook_path="data/raw/homework_lesson_6_joins_SOLUTION.ipynb",
        rubric_path="rubrics/assignment_6_rubric.json"
    )
    
    result = validator.validate_student_outputs(
        "submissions/12/Emerickkathrynj_emerickkathrynj.ipynb"
    )
    
    report = validator.generate_report(result)
    print(report)
