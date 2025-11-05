"""
Rubric-Driven Systematic Validator
Works with any assignment by reading requirements from the rubric JSON
"""

import json
import re
import nbformat
import os
from typing import Dict, List, Any, Optional


class RubricDrivenValidator:
    """Generic validator that reads all requirements from the rubric"""
    
    def __init__(self, rubric_path: str):
        """Initialize validator with rubric file"""
        with open(rubric_path, 'r') as f:
            self.rubric = json.load(f)
        
        # Check if rubric has autograder_checks
        if 'autograder_checks' not in self.rubric:
            raise ValueError(f"Rubric {rubric_path} missing 'autograder_checks' section")
        
        self.checks = self.rubric['autograder_checks']
        self.required_variables = self.checks.get('required_variables', [])
        self.sections = self.checks.get('sections', {})
        
        # Load flexible partial credit scorer if rubric has rules
        self.partial_credit_scorer = None
        if 'partial_credit_rules' in self.rubric:
            try:
                from validators.flexible_partial_credit import FlexiblePartialCreditScorer
                self.partial_credit_scorer = FlexiblePartialCreditScorer(self.rubric)
                print(f"✅ Loaded flexible partial credit system")
            except ImportError as e:
                print(f"⚠️ Could not load flexible partial credit scorer: {e}")
        
        print(f"✅ Loaded rubric-driven validator")
        print(f"   Required variables: {len(self.required_variables)}")
        print(f"   Sections to check: {len(self.sections)}")
    
    def validate_notebook(self, notebook_path: str) -> Dict[str, Any]:
        """
        Validate notebook against rubric requirements
        
        Returns:
            Dict with validation results including:
            - variable_check: which variables were found
            - section_breakdown: status of each section
            - cell_stats: execution statistics
            - overall_score: calculated score
        """
        # Load notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract all code
        all_code = self._extract_code(nb)
        
        # Check variables
        variable_check = self._check_variables(all_code)
        
        # Check sections
        section_breakdown = self._check_sections(all_code, nb)
        
        # Calculate cell statistics
        cell_stats = self._calculate_cell_stats(nb)
        
        # Calculate overall score
        overall_score = self._calculate_score(variable_check, section_breakdown)
        
        return {
            'variable_check': variable_check,
            'section_breakdown': section_breakdown,
            'cell_stats': cell_stats,
            'overall_score': overall_score,
            'final_score': overall_score['overall_score'],  # For compatibility with grader_v2
            'rubric_name': self.rubric.get('assignment_info', {}).get('name', 'unknown')
        }
    
    def _extract_code(self, nb) -> str:
        """Extract all code from notebook"""
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
        return '\n'.join(cell.source for cell in code_cells)
    
    def _check_variables(self, code: str) -> Dict[str, Any]:
        """Check which required variables are present"""
        found_variables = []
        missing_variables = []
        
        for var in self.required_variables:
            # Look for variable assignment patterns
            patterns = [
                rf'\b{var}\s*<-',  # R assignment
                rf'\b{var}\s*=',   # Alternative assignment
                rf'{var}\s*<-.*%>%',  # Pipe assignment
            ]
            
            if any(re.search(pattern, code, re.MULTILINE) for pattern in patterns):
                found_variables.append(var)
            else:
                missing_variables.append(var)
        
        return {
            'found': len(found_variables),
            'total_required': len(self.required_variables),
            'found_variables': found_variables,
            'missing_variables': missing_variables,
            'missing': missing_variables,  # For compatibility with grader_v2
            'completion_rate': len(found_variables) / len(self.required_variables) if self.required_variables else 1.0
        }
    
    def _check_sections(self, code: str, nb) -> Dict[str, Any]:
        """Check completion status of each section"""
        section_results = {}
        
        for section_id, section_info in self.sections.items():
            result = {
                'name': section_info.get('name', section_id),
                'points': section_info.get('points', 0),
                'status': 'incomplete',
                'found_items': [],
                'missing_items': [],
                'score': 0
            }
            
            # Check if this is a reflection section
            if section_info.get('check_type') == 'markdown':
                reflection_result = self._check_reflections(nb, section_info)
                result.update(reflection_result)
            else:
                # Check variables
                required_vars = section_info.get('variables', [])
                for var in required_vars:
                    if re.search(rf'\b{var}\s*<-', code):
                        result['found_items'].append(f"Variable: {var}")
                    else:
                        result['missing_items'].append(f"Variable: {var}")
                
                # Check functions
                required_funcs = section_info.get('functions', [])
                for func in required_funcs:
                    if re.search(rf'{func}\s*\(', code):
                        result['found_items'].append(f"Function: {func}()")
                    else:
                        result['missing_items'].append(f"Function: {func}()")
                
                # Check required columns
                required_cols = section_info.get('required_columns', [])
                for col in required_cols:
                    if col in code:
                        result['found_items'].append(f"Column: {col}")
                    else:
                        result['missing_items'].append(f"Column: {col}")
                
                # Determine status and initial score
                total_items = len(required_vars) + len(required_funcs) + len(required_cols)
                found_items = len(result['found_items'])
                
                if total_items > 0:
                    completion = found_items / total_items
                    if completion >= 0.8:
                        result['status'] = 'complete'
                        result['score'] = result['points']
                    elif completion >= 0.5:
                        result['status'] = 'partial'
                        result['score'] = result['points'] * 0.5
                    else:
                        result['status'] = 'incomplete'
                        result['score'] = 0
            
            # Apply flexible partial credit scoring if available
            if self.partial_credit_scorer:
                result = self.partial_credit_scorer.adjust_score(section_id, result, code, nb)
            
            section_results[section_id] = result
        
        return section_results
    
    def _check_reflections(self, nb, section_info: Dict) -> Dict:
        """Check reflection questions in markdown cells"""
        markdown_cells = [cell for cell in nb.cells if cell.cell_type == 'markdown']
        all_markdown = '\n'.join(cell.source for cell in markdown_cells)
        
        # Count reflection questions
        expected_questions = section_info.get('reflection_questions', 0)
        
        # Look for placeholder text
        placeholders = [
            '[YOUR ANSWER HERE]',
            '[Enter your',
            'Your answer here:',
            'TODO'
        ]
        
        placeholder_count = sum(1 for p in placeholders if p in all_markdown)
        
        # Estimate answered questions
        # If there are fewer placeholders, more questions are answered
        answered = max(0, expected_questions - placeholder_count)
        
        completion = answered / expected_questions if expected_questions > 0 else 1.0
        
        result = {
            'found_items': [f"Answered {answered}/{expected_questions} reflection questions"],
            'missing_items': [] if completion >= 0.8 else [f"{expected_questions - answered} questions unanswered"],
            'status': 'complete' if completion >= 0.8 else 'partial' if completion >= 0.5 else 'incomplete',
            'score': section_info.get('points', 0) * completion
        }
        
        return result
    
    def _calculate_cell_stats(self, nb) -> Dict[str, Any]:
        """Calculate cell execution statistics"""
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
        total_cells = len(code_cells)
        
        executed_cells = sum(1 for cell in code_cells 
                           if cell.get('execution_count') is not None or cell.get('outputs'))
        
        return {
            'total_cells': total_cells,
            'executed_cells': executed_cells,
            'execution_rate': executed_cells / total_cells if total_cells > 0 else 0
        }
    
    def _calculate_score(self, variable_check: Dict, section_breakdown: Dict) -> Dict[str, Any]:
        """Calculate overall score based on checks"""
        # Calculate section score
        total_section_points = sum(s['points'] for s in section_breakdown.values())
        earned_section_points = sum(s['score'] for s in section_breakdown.values())
        
        section_score = (earned_section_points / total_section_points * 100) if total_section_points > 0 else 0
        
        # Variable completion score
        variable_score = variable_check['completion_rate'] * 100
        
        # Weighted average (sections 80%, variables 20%)
        overall_score = (section_score * 0.8) + (variable_score * 0.2)
        
        return {
            'overall_score': overall_score,
            'section_score': section_score,
            'variable_score': variable_score,
            'total_possible_points': total_section_points,
            'earned_points': earned_section_points
        }


def validate_student_submission(notebook_path: str, rubric_path: str) -> Dict:
    """
    Main validation function
    
    Args:
        notebook_path: Path to student notebook
        rubric_path: Path to rubric JSON file
    
    Returns:
        Dict with validation results
    """
    validator = RubricDrivenValidator(rubric_path)
    result = validator.validate_notebook(notebook_path)
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        notebook_path = sys.argv[1]
        rubric_path = sys.argv[2]
        
        print(f"Validating: {notebook_path}")
        print(f"Using rubric: {rubric_path}")
        print("=" * 60)
        
        result = validate_student_submission(notebook_path, rubric_path)
        
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        print(f"\nVariables: {result['variable_check']['found']}/{result['variable_check']['total_required']}")
        print(f"Overall Score: {result['overall_score']['overall_score']:.1f}%")
        print(f"\nSection Breakdown:")
        for section_id, section in result['section_breakdown'].items():
            status_icon = "✅" if section['status'] == 'complete' else "⚠️" if section['status'] == 'partial' else "❌"
            print(f"  {status_icon} {section['name']}: {section['score']:.1f}/{section['points']} points")
    else:
        print("Usage: python rubric_driven_validator.py <notebook_path> <rubric_path>")
