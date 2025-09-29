import re
from typing import Dict, Optional

def match_assignment_to_rubric(assignment_name: str, available_rubrics: Dict[str, dict]) -> Optional[str]:
    """
    Intelligently match an assignment name to the most appropriate rubric
    
    Args:
        assignment_name: Name of the assignment (e.g., "2.3", "Homework 2", etc.)
        available_rubrics: Dictionary of available rubrics {name: rubric_data}
    
    Returns:
        Best matching rubric name or None if no good match found
    """
    if not assignment_name or not available_rubrics:
        return None
    
    assignment_lower = assignment_name.lower().strip()
    
    # Direct matching patterns
    patterns = [
        # Match "2.3" or "Assignment 2.3" to Assignment 2
        (r'(?:assignment\s*)?2\.?\d*', 'Assignment 2'),
        (r'(?:assignment\s*)?1\.?\d*', 'Assignment 1'),
        (r'homework\s*2', 'Assignment 2'),
        (r'homework\s*1', 'Assignment 1'),
        (r'data\s*cleaning', 'Assignment 2'),
        (r'intro.*r|environment.*setup', 'Assignment 1'),
        (r'missing.*values|outliers', 'Assignment 2'),
    ]
    
    # Try pattern matching first
    for pattern, target_rubric in patterns:
        if re.search(pattern, assignment_lower):
            if target_rubric in available_rubrics:
                return target_rubric
    
    # Fallback: try to find the best match by keywords
    rubric_scores = {}
    for rubric_name, rubric_data in available_rubrics.items():
        score = 0
        rubric_lower = rubric_name.lower()
        
        # Check if assignment name contains rubric keywords
        if 'assignment' in assignment_lower and 'assignment' in rubric_lower:
            score += 10
        
        # Extract numbers and match
        assignment_numbers = re.findall(r'\d+', assignment_name)
        rubric_numbers = re.findall(r'\d+', rubric_name)
        
        if assignment_numbers and rubric_numbers:
            if assignment_numbers[0] == rubric_numbers[0]:
                score += 20
        
        # Check rubric content for matching keywords
        if isinstance(rubric_data, dict):
            rubric_content = str(rubric_data).lower()
            
            # Assignment 2 keywords
            if any(keyword in assignment_lower for keyword in ['data', 'cleaning', 'missing', 'outlier']):
                if any(keyword in rubric_content for keyword in ['missing', 'outlier', 'cleaning', 'imputation']):
                    score += 15
            
            # Assignment 1 keywords  
            if any(keyword in assignment_lower for keyword in ['intro', 'environment', 'setup', 'import']):
                if any(keyword in rubric_content for keyword in ['environment', 'import', 'tidyverse', 'readxl']):
                    score += 15
        
        rubric_scores[rubric_name] = score
    
    # Return the highest scoring rubric if score > 0
    if rubric_scores:
        best_match = max(rubric_scores.items(), key=lambda x: x[1])
        if best_match[1] > 0:
            return best_match[0]
    
    return None

def suggest_rubric_for_assignment(assignment_name: str) -> str:
    """
    Suggest which predefined rubric to use based on assignment name
    
    Args:
        assignment_name: Name of the assignment
        
    Returns:
        Suggested rubric filename or general advice
    """
    assignment_lower = assignment_name.lower().strip()
    
    # Specific suggestions
    if re.search(r'(?:assignment\s*)?2\.?\d*|homework\s*2|data\s*cleaning', assignment_lower):
        return "assignment_2_rubric.json (Data Cleaning - Missing Values and Outliers)"
    
    if re.search(r'(?:assignment\s*)?1\.?\d*|homework\s*1|intro.*r|environment', assignment_lower):
        return "assignment_1_rubric.json (Introduction to R - Environment Setup)"
    
    # General advice
    if 'data' in assignment_lower:
        return "Consider assignment_2_rubric.json for data-related assignments"
    
    if 'intro' in assignment_lower or 'setup' in assignment_lower:
        return "Consider assignment_1_rubric.json for introductory assignments"
    
    return "Create a custom rubric or use the default template"

def get_assignment_type_from_name(assignment_name: str) -> str:
    """
    Determine the type/category of assignment from its name
    
    Args:
        assignment_name: Name of the assignment
        
    Returns:
        Assignment type/category
    """
    assignment_lower = assignment_name.lower().strip()
    
    if re.search(r'data\s*cleaning|missing.*values|outliers', assignment_lower):
        return "Data Cleaning"
    
    if re.search(r'intro|environment|setup|import', assignment_lower):
        return "Introduction/Setup"
    
    if re.search(r'analysis|statistics|modeling', assignment_lower):
        return "Data Analysis"
    
    if re.search(r'visualization|plot|chart|graph', assignment_lower):
        return "Data Visualization"
    
    if re.search(r'machine.*learning|ml|prediction', assignment_lower):
        return "Machine Learning"
    
    return "General Assignment"