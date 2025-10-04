#!/usr/bin/env python3
"""
Notebook Validation Module
Checks for common submission issues before grading
"""

import nbformat
from typing import Dict, List, Tuple

class NotebookValidator:
    """Validates notebook submissions for common issues"""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_notebook(self, notebook_path: str) -> Dict:
        """
        Comprehensive notebook validation
        Returns validation results with penalties
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            return {
                'valid': False,
                'error': f"Could not read notebook: {e}",
                'penalty': 100,  # Cannot grade
                'issues': ['Notebook file is corrupted or unreadable']
            }
        
        issues = []
        penalties = []
        warnings = []
        
        # Check 1: Notebook execution
        execution_check = self._check_execution(nb)
        if not execution_check['executed']:
            issues.append("⚠️ CRITICAL: Notebook was not executed - no cell outputs found")
            penalties.append(('no_execution', 50))  # 50% penalty
        
        # Check 2: TODO sections
        todo_check = self._check_todos(nb)
        if todo_check['incomplete_todos'] > 0:
            issues.append(f"⚠️ Found {todo_check['incomplete_todos']} incomplete TODO sections with placeholder code")
            penalties.append(('incomplete_todos', todo_check['incomplete_todos'] * 5))  # 5% per TODO
        
        # Check 3: Reflection questions
        reflection_check = self._check_reflections(nb)
        if reflection_check['unanswered'] > 0:
            issues.append(f"⚠️ Found {reflection_check['unanswered']} unanswered reflection questions")
            penalties.append(('unanswered_reflections', reflection_check['unanswered'] * 5))  # 5% per question
        
        # Check 4: Code errors
        error_check = self._check_for_errors(nb)
        if error_check['has_errors']:
            warnings.append(f"Found {error_check['error_count']} cells with error outputs")
            penalties.append(('execution_errors', error_check['error_count'] * 3))  # 3% per error
        
        # Check 5: Empty code cells
        empty_check = self._check_empty_cells(nb)
        if empty_check['empty_code_cells'] > 0:
            warnings.append(f"Found {empty_check['empty_code_cells']} empty code cells")
            penalties.append(('empty_cells', empty_check['empty_code_cells'] * 2))  # 2% per empty cell
        
        # Calculate total penalty (cap at 90%)
        total_penalty = min(sum(p[1] for p in penalties), 90)
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'penalties': penalties,
            'total_penalty_percent': total_penalty,
            'execution_check': execution_check,
            'todo_check': todo_check,
            'reflection_check': reflection_check,
            'error_check': error_check,
            'empty_check': empty_check
        }
    
    def _check_execution(self, nb) -> Dict:
        """Check if notebook has been executed"""
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
        
        if not code_cells:
            return {'executed': True, 'reason': 'No code cells found'}
        
        executed_cells = 0
        for cell in code_cells:
            # Check for execution_count or outputs
            if cell.get('execution_count') is not None or cell.get('outputs'):
                executed_cells += 1
        
        execution_rate = executed_cells / len(code_cells) if code_cells else 0
        
        return {
            'executed': execution_rate > 0.5,  # At least 50% of cells executed
            'total_code_cells': len(code_cells),
            'executed_cells': executed_cells,
            'execution_rate': execution_rate,
            'reason': f"{executed_cells}/{len(code_cells)} cells executed"
        }
    
    def _check_todos(self, nb) -> Dict:
        """Check for incomplete TODO sections"""
        incomplete_todos = 0
        todo_locations = []
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code':
                source = cell.source.lower()
                # Check for common TODO patterns
                if any(pattern in source for pattern in [
                    '# your code here',
                    '# todo',
                    'your code here',
                    '# hint:',  # If hint is still there, likely not completed
                ]):
                    # Make sure it's not just a comment, check if there's actual code
                    lines = cell.source.split('\n')
                    has_real_code = any(
                        line.strip() and 
                        not line.strip().startswith('#') and
                        'your code here' not in line.lower() and
                        'todo' not in line.lower()
                        for line in lines
                    )
                    
                    if not has_real_code:
                        incomplete_todos += 1
                        todo_locations.append(f"Cell {i+1}")
        
        return {
            'incomplete_todos': incomplete_todos,
            'locations': todo_locations
        }
    
    def _check_reflections(self, nb) -> Dict:
        """Check for unanswered reflection questions"""
        unanswered = 0
        unanswered_locations = []
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'markdown':
                source = cell.source.lower()
                # Check for placeholder answers
                if any(pattern in source for pattern in [
                    '[your answer here]',
                    '[write your',
                    'your answer:',
                    'your response:',
                ]):
                    # Check if there's actual content after the placeholder
                    if '[your answer here]' in source or '[write your' in source:
                        unanswered += 1
                        unanswered_locations.append(f"Cell {i+1}")
        
        return {
            'unanswered': unanswered,
            'locations': unanswered_locations
        }
    
    def _check_for_errors(self, nb) -> Dict:
        """Check for error outputs in executed cells"""
        error_count = 0
        error_locations = []
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and cell.get('outputs'):
                for output in cell.outputs:
                    if output.get('output_type') == 'error':
                        error_count += 1
                        error_locations.append(f"Cell {i+1}: {output.get('ename', 'Unknown error')}")
        
        return {
            'has_errors': error_count > 0,
            'error_count': error_count,
            'locations': error_locations
        }
    
    def _check_empty_cells(self, nb) -> Dict:
        """Check for empty code cells"""
        empty_count = 0
        empty_locations = []
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code':
                if not cell.source.strip():
                    empty_count += 1
                    empty_locations.append(f"Cell {i+1}")
        
        return {
            'empty_code_cells': empty_count,
            'locations': empty_locations
        }
    
    def generate_validation_feedback(self, validation_results: Dict) -> str:
        """Generate human-readable feedback from validation results"""
        feedback = []
        
        if not validation_results.get('valid', True):
            feedback.append("## ⚠️ SUBMISSION ISSUES DETECTED\n")
            feedback.append("Your submission has critical issues that must be addressed:\n")
            
            for issue in validation_results.get('issues', []):
                feedback.append(f"- {issue}")
            
            penalty = validation_results.get('total_penalty_percent', 0)
            if penalty > 0:
                feedback.append(f"\n**Total Penalty: {penalty}% deduction**\n")
        
        if validation_results['warnings']:
            feedback.append("\n## ⚠️ Warnings:\n")
            for warning in validation_results['warnings']:
                feedback.append(f"- {warning}")
        
        # Specific guidance
        if not validation_results['execution_check']['executed']:
            feedback.append("\n### How to Fix: Notebook Not Executed")
            feedback.append("1. Open your notebook in Jupyter or VS Code")
            feedback.append("2. Click 'Run All' or 'Restart Kernel and Run All'")
            feedback.append("3. Verify all cells show output")
            feedback.append("4. Save and resubmit\n")
        
        if validation_results['todo_check']['incomplete_todos'] > 0:
            feedback.append("\n### How to Fix: Incomplete TODO Sections")
            feedback.append(f"You have {validation_results['todo_check']['incomplete_todos']} TODO sections that need completion:")
            for loc in validation_results['todo_check']['locations']:
                feedback.append(f"- {loc}")
            feedback.append("Replace '# YOUR CODE HERE' with your actual code\n")
        
        if validation_results['reflection_check']['unanswered'] > 0:
            feedback.append("\n### How to Fix: Unanswered Reflection Questions")
            feedback.append(f"You have {validation_results['reflection_check']['unanswered']} unanswered reflection questions:")
            for loc in validation_results['reflection_check']['locations']:
                feedback.append(f"- {loc}")
            feedback.append("Replace '[YOUR ANSWER HERE]' with your thoughtful responses\n")
        
        return '\n'.join(feedback)


# Convenience function
def validate_submission(notebook_path: str) -> Tuple[Dict, str]:
    """
    Validate a notebook submission
    Returns (validation_results, feedback_text)
    """
    validator = NotebookValidator()
    results = validator.validate_notebook(notebook_path)
    feedback = validator.generate_validation_feedback(results)
    return results, feedback


if __name__ == "__main__":
    # Test the validator
    import sys
    
    if len(sys.argv) > 1:
        notebook_path = sys.argv[1]
        results, feedback = validate_submission(notebook_path)
        
        print("=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        print(feedback)
        print("\n" + "=" * 60)
        print(f"Valid: {results['valid']}")
        print(f"Total Penalty: {results['total_penalty_percent']}%")
        print("=" * 60)
    else:
        print("Usage: python notebook_validation.py <notebook_path>")
