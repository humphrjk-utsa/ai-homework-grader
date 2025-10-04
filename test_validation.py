#!/usr/bin/env python3
"""
Quick test of the notebook validation system
"""

from notebook_validation import NotebookValidator
import json

def test_validation():
    """Test the validation system with a sample notebook"""
    
    validator = NotebookValidator()
    
    # Test with a real student notebook if available
    import os
    
    # Look for student notebooks in data folder
    data_folder = "data"
    if os.path.exists(data_folder):
        for root, dirs, files in os.walk(data_folder):
            for file in files:
                if file.endswith('.ipynb') and 'checkpoint' not in file:
                    notebook_path = os.path.join(root, file)
                    print(f"\n{'='*60}")
                    print(f"Testing: {notebook_path}")
                    print('='*60)
                    
                    try:
                        results = validator.validate_notebook(notebook_path)
                        feedback = validator.generate_validation_feedback(results)
                        
                        print(f"\nValid: {results['valid']}")
                        print(f"Total Penalty: {results['total_penalty_percent']}%")
                        
                        if results['issues']:
                            print(f"\nIssues ({len(results['issues'])}):")
                            for issue in results['issues']:
                                print(f"  - {issue}")
                        
                        if results['warnings']:
                            print(f"\nWarnings ({len(results['warnings'])}):")
                            for warning in results['warnings']:
                                print(f"  - {warning}")
                        
                        print(f"\nExecution Check:")
                        exec_check = results['execution_check']
                        print(f"  Executed: {exec_check['executed']}")
                        print(f"  Rate: {exec_check['executed_cells']}/{exec_check['total_code_cells']} cells")
                        
                        print(f"\nTODO Check:")
                        todo_check = results['todo_check']
                        print(f"  Incomplete TODOs: {todo_check['incomplete_todos']}")
                        if todo_check['locations']:
                            print(f"  Locations: {', '.join(todo_check['locations'])}")
                        
                        print(f"\nReflection Check:")
                        refl_check = results['reflection_check']
                        print(f"  Unanswered: {refl_check['unanswered']}")
                        if refl_check['locations']:
                            print(f"  Locations: {', '.join(refl_check['locations'])}")
                        
                        if feedback:
                            print(f"\n{'-'*60}")
                            print("FEEDBACK:")
                            print(f"{'-'*60}")
                            print(feedback)
                        
                        # Only test first notebook
                        break
                    except Exception as e:
                        print(f"Error testing {notebook_path}: {e}")
                        import traceback
                        traceback.print_exc()
            break
    else:
        print("No data folder found - create test notebook manually")

if __name__ == "__main__":
    test_validation()
