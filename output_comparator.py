#!/usr/bin/env python3
"""
Output Comparator
Compares student outputs to solution outputs with flexibility
"""

import re
from typing import Dict, List, Tuple, Any
from difflib import SequenceMatcher


class OutputComparator:
    """Compare student outputs to solution outputs with smart flexibility"""
    
    # Tolerance for numeric comparisons
    NUMERIC_TOLERANCE = 0.01  # 1% difference allowed
    
    # Similarity threshold for text comparison
    TEXT_SIMILARITY_THRESHOLD = 0.50  # 50% similar is acceptable (focus on numbers)
    
    def __init__(self):
        self.comparisons = []
        self.mismatches = []
    
    def compare_outputs(self, student_output: str, solution_output: str, 
                       question_context: str = "") -> Dict[str, Any]:
        """
        Compare student output to solution output
        
        Args:
            student_output: The student's output
            solution_output: The expected solution output
            question_context: Context about what the question asks for
            
        Returns:
            Dict with comparison results
        """
        # Normalize outputs
        student_norm = self._normalize_output(student_output)
        solution_norm = self._normalize_output(solution_output)
        
        # Extract numbers from both
        student_numbers = self._extract_numbers(student_norm)
        solution_numbers = self._extract_numbers(solution_norm)
        
        # Compare numbers with tolerance
        numbers_match = self._compare_numbers(student_numbers, solution_numbers)
        
        # Compare text structure
        text_similarity = self._calculate_similarity(student_norm, solution_norm)
        
        # Determine if outputs are equivalent
        is_equivalent = numbers_match and text_similarity >= self.TEXT_SIMILARITY_THRESHOLD
        
        result = {
            'is_equivalent': is_equivalent,
            'numbers_match': numbers_match,
            'text_similarity': text_similarity,
            'student_output': student_output,
            'solution_output': solution_output,
            'explanation': self._generate_explanation(
                is_equivalent, numbers_match, text_similarity
            )
        }
        
        self.comparisons.append(result)
        if not is_equivalent:
            self.mismatches.append(result)
        
        return result
    
    def _normalize_output(self, output: str) -> str:
        """Normalize output for comparison"""
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', output.strip())
        
        # Normalize common variations
        normalized = normalized.lower()
        
        # Remove formatting characters
        normalized = re.sub(r'[_*`]', '', normalized)
        
        return normalized
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        # Match integers and floats
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers
    
    def _compare_numbers(self, student_nums: List[float], 
                        solution_nums: List[float]) -> bool:
        """Compare numbers with tolerance"""
        if len(student_nums) != len(solution_nums):
            return False
        
        for s_num, sol_num in zip(student_nums, solution_nums):
            # Check if within tolerance
            if sol_num == 0:
                # Absolute difference for zero
                if abs(s_num - sol_num) > 0.01:
                    return False
            else:
                # Relative difference
                rel_diff = abs(s_num - sol_num) / abs(sol_num)
                if rel_diff > self.NUMERIC_TOLERANCE:
                    return False
        
        return True
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity ratio"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _generate_explanation(self, is_equivalent: bool, 
                            numbers_match: bool, 
                            text_similarity: float) -> str:
        """Generate human-readable explanation"""
        if is_equivalent:
            return "Output matches solution (within acceptable tolerance)"
        
        issues = []
        if not numbers_match:
            issues.append("numeric values differ from expected")
        if text_similarity < self.TEXT_SIMILARITY_THRESHOLD:
            issues.append(f"output format differs (similarity: {text_similarity:.0%})")
        
        return "Output differs: " + ", ".join(issues)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all comparisons"""
        total = len(self.comparisons)
        matches = total - len(self.mismatches)
        
        return {
            'total_comparisons': total,
            'matches': matches,
            'mismatches': len(self.mismatches),
            'match_rate': (matches / total * 100) if total > 0 else 100,
            'mismatch_details': self.mismatches
        }
    
    def compare_cell_outputs(self, student_cells: List[Dict], 
                            solution_cells: List[Dict]) -> Dict[str, Any]:
        """
        Compare outputs from notebook cells
        
        Args:
            student_cells: List of student code cells with outputs
            solution_cells: List of solution code cells with outputs
            
        Returns:
            Comparison summary
        """
        # Match cells by code similarity (in case order differs)
        cell_matches = self._match_cells(student_cells, solution_cells)
        
        for student_cell, solution_cell in cell_matches:
            student_out = self._extract_cell_output(student_cell)
            solution_out = self._extract_cell_output(solution_cell)
            
            if student_out and solution_out:
                self.compare_outputs(student_out, solution_out)
        
        return self.get_summary()
    
    def _match_cells(self, student_cells: List[Dict], 
                    solution_cells: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """Match student cells to solution cells by code similarity"""
        matches = []
        
        for s_cell in student_cells:
            best_match = None
            best_similarity = 0
            
            s_code = s_cell.get('source', '')
            
            for sol_cell in solution_cells:
                sol_code = sol_cell.get('source', '')
                similarity = self._calculate_similarity(
                    self._normalize_output(s_code),
                    self._normalize_output(sol_code)
                )
                
                if similarity > best_similarity and similarity > 0.5:
                    best_similarity = similarity
                    best_match = sol_cell
            
            if best_match:
                matches.append((s_cell, best_match))
        
        return matches
    
    def _extract_cell_output(self, cell: Dict) -> str:
        """Extract output text from a notebook cell"""
        outputs = cell.get('outputs', [])
        output_text = ""
        
        for output in outputs:
            if output.get('output_type') == 'stream':
                output_text += output.get('text', '')
            elif output.get('output_type') == 'execute_result':
                data = output.get('data', {})
                output_text += data.get('text/plain', '')
            elif output.get('output_type') == 'display_data':
                data = output.get('data', {})
                output_text += data.get('text/plain', '')
        
        return output_text


def compare_notebook_outputs(student_notebook_path: str, 
                            solution_notebook_path: str) -> Dict[str, Any]:
    """
    Convenience function to compare notebook outputs
    
    Args:
        student_notebook_path: Path to student notebook
        solution_notebook_path: Path to solution notebook
        
    Returns:
        Comparison summary with match rate and details
    """
    import nbformat
    
    # Read notebooks
    with open(student_notebook_path, 'r') as f:
        student_nb = nbformat.read(f, as_version=4)
    
    with open(solution_notebook_path, 'r') as f:
        solution_nb = nbformat.read(f, as_version=4)
    
    # Extract code cells
    student_cells = [cell for cell in student_nb.cells if cell.cell_type == 'code']
    solution_cells = [cell for cell in solution_nb.cells if cell.cell_type == 'code']
    
    # Compare
    comparator = OutputComparator()
    summary = comparator.compare_cell_outputs(student_cells, solution_cells)
    
    return summary


if __name__ == "__main__":
    # Test the comparator
    comparator = OutputComparator()
    
    # Test 1: Exact match
    result1 = comparator.compare_outputs(
        "Total: 500 rows",
        "Total: 500 rows"
    )
    print(f"Test 1 (exact match): {result1['is_equivalent']} - {result1['explanation']}")
    
    # Test 2: Numeric tolerance
    result2 = comparator.compare_outputs(
        "Mean: 123.45",
        "Mean: 123.46"
    )
    print(f"Test 2 (within tolerance): {result2['is_equivalent']} - {result2['explanation']}")
    
    # Test 3: Different format, same numbers
    result3 = comparator.compare_outputs(
        "Count: 100 items",
        "Total count is 100"
    )
    print(f"Test 3 (different format): {result3['is_equivalent']} - {result3['explanation']}")
    
    # Test 4: Wrong numbers
    result4 = comparator.compare_outputs(
        "Total: 500",
        "Total: 600"
    )
    print(f"Test 4 (wrong numbers): {result4['is_equivalent']} - {result4['explanation']}")
    
    print(f"\nSummary: {comparator.get_summary()}")
