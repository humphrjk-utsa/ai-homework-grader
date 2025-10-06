#!/usr/bin/env python3
"""
Output Comparator
Programmatically compares student notebook outputs to solution outputs
"""

import nbformat
from typing import Dict, List, Tuple, Any
import re
from difflib import SequenceMatcher

class OutputComparator:
    """Compares notebook cell outputs between student and solution"""
    
    def __init__(self, student_notebook_path: str, solution_notebook_path: str):
        self.student_path = student_notebook_path
        self.solution_path = solution_notebook_path
        
        with open(student_notebook_path, 'r', encoding='utf-8') as f:
            self.student_nb = nbformat.read(f, as_version=4)
        
        with open(solution_notebook_path, 'r', encoding='utf-8') as f:
            self.solution_nb = nbformat.read(f, as_version=4)
    
    def extract_code_cells(self, notebook) -> List[Dict]:
        """Extract code cells with their outputs"""
        cells = []
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                cell_data = {
                    'source': cell.get('source', ''),
                    'outputs': self._extract_outputs(cell),
                    'execution_count': cell.get('execution_count')
                }
                cells.append(cell_data)
        return cells
    
    def _extract_outputs(self, cell) -> List[str]:
        """Extract text outputs from a cell"""
        outputs = []
        for output in cell.get('outputs', []):
            if output.get('output_type') == 'stream':
                outputs.append(output.get('text', ''))
            elif output.get('output_type') == 'execute_result':
                data = output.get('data', {})
                if 'text/plain' in data:
                    outputs.append(data['text/plain'])
            elif output.get('output_type') == 'display_data':
                data = output.get('data', {})
                if 'text/plain' in data:
                    outputs.append(data['text/plain'])
        return outputs

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text outputs (0-1)"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Normalize whitespace
        text1 = ' '.join(text1.split())
        text2 = ' '.join(text2.split())
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, text1, text2).ratio()
    
    def compare_outputs(self) -> Dict[str, Any]:
        """Compare all outputs between student and solution"""
        student_cells = self.extract_code_cells(self.student_nb)
        solution_cells = self.extract_code_cells(self.solution_nb)
        
        comparisons = []
        total_similarity = 0
        matching_count = 0
        
        # Compare cell by cell
        max_cells = max(len(student_cells), len(solution_cells))
        
        for i in range(max_cells):
            student_cell = student_cells[i] if i < len(student_cells) else None
            solution_cell = solution_cells[i] if i < len(solution_cells) else None
            
            if not student_cell:
                # Student missing this cell
                comparisons.append({
                    'cell_index': i,
                    'status': 'missing',
                    'match': False,
                    'similarity': 0.0,
                    'solution_code': solution_cell['source'] if solution_cell else '',
                    'solution_output': solution_cell['outputs'] if solution_cell else [],
                    'student_output': []
                })
                continue
            
            if not solution_cell:
                # Extra student cell (no solution to compare)
                comparisons.append({
                    'cell_index': i,
                    'status': 'extra',
                    'match': True,  # Don't penalize extra work
                    'similarity': 1.0,
                    'student_output': student_cell['outputs']
                })
                total_similarity += 1.0
                matching_count += 1
                continue

            # Compare outputs
            student_out = '\n'.join(student_cell['outputs'])
            solution_out = '\n'.join(solution_cell['outputs'])
            
            similarity = self.calculate_similarity(student_out, solution_out)
            is_match = similarity >= 0.80  # 80% similarity threshold
            
            comparison = {
                'cell_index': i,
                'status': 'match' if is_match else 'mismatch',
                'match': is_match,
                'similarity': similarity,
                'student_code': student_cell['source'],
                'student_output': student_cell['outputs'],
                'solution_code': solution_cell['source'],
                'solution_output': solution_cell['outputs']
            }
            
            comparisons.append(comparison)
            total_similarity += similarity
            if is_match:
                matching_count += 1
        
        # Calculate overall metrics
        accuracy = (total_similarity / max_cells * 100) if max_cells > 0 else 0
        match_rate = (matching_count / max_cells * 100) if max_cells > 0 else 0
        
        return {
            'total_cells': max_cells,
            'student_cells': len(student_cells),
            'solution_cells': len(solution_cells),
            'matching_cells': matching_count,
            'match_rate': match_rate,
            'accuracy_score': accuracy,
            'comparisons': comparisons
        }

    def generate_comparison_report(self) -> str:
        """Generate human-readable comparison report"""
        results = self.compare_outputs()
        
        report = f"""
📊 OUTPUT COMPARISON REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Cells: {results['total_cells']}
Matching Outputs: {results['matching_cells']}/{results['total_cells']} ({results['match_rate']:.1f}%)
Overall Accuracy: {results['accuracy_score']:.1f}%

"""
        
        # List mismatches
        mismatches = [c for c in results['comparisons'] if not c['match']]
        if mismatches:
            report += "❌ MISMATCHED CELLS:\n"
            for comp in mismatches:
                report += f"\nCell {comp['cell_index']}:\n"
                if comp['status'] == 'missing':
                    report += "  Status: Student did not complete this cell\n"
                    report += f"  Expected output: {comp['solution_output'][:100]}...\n"
                else:
                    report += f"  Similarity: {comp['similarity']*100:.1f}%\n"
                    report += f"  Student output: {comp['student_output'][:100] if comp['student_output'] else 'No output'}...\n"
                    report += f"  Expected output: {comp['solution_output'][:100]}...\n"
        
        return report
    
    def generate_ai_prompt_section(self) -> str:
        """Generate section for AI grading prompt with comparison results"""
        results = self.compare_outputs()
        
        prompt = f"""
OUTPUT COMPARISON ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Programmatic comparison of student outputs vs solution outputs:
- Total cells compared: {results['total_cells']}
- Matching outputs: {results['matching_cells']}/{results['total_cells']} ({results['match_rate']:.1f}%)
- Overall accuracy: {results['accuracy_score']:.1f}%

"""

        # Add details for mismatched cells
        mismatches = [c for c in results['comparisons'] if not c['match']]
        if mismatches:
            prompt += "CELLS WITH INCORRECT OUTPUTS:\n\n"
            for comp in mismatches[:5]:  # Limit to first 5 mismatches
                prompt += f"Cell {comp['cell_index']} - {comp['status'].upper()}:\n"
                
                if comp['status'] == 'missing':
                    prompt += f"  ❌ Student did not complete this cell\n"
                    prompt += f"  ✅ Expected code:\n```r\n{comp['solution_code'][:200]}\n```\n"
                    prompt += f"  ✅ Expected output: {comp['solution_output']}\n\n"
                else:
                    prompt += f"  Similarity: {comp['similarity']*100:.1f}%\n"
                    prompt += f"  ❌ Student output: {comp['student_output']}\n"
                    prompt += f"  ✅ Expected output: {comp['solution_output']}\n"
                    prompt += f"  💡 Solution code:\n```r\n{comp['solution_code'][:200]}\n```\n\n"
        
        prompt += """
GRADING INSTRUCTION:
- Use this programmatic comparison as PRIMARY evidence
- If match_rate >= 90%: Student has correct outputs (score 90-100)
- If match_rate 75-89%: Student has mostly correct outputs (score 80-90)
- If match_rate 60-74%: Student has some correct outputs (score 70-80)
- If match_rate < 60%: Student has incorrect outputs (score 50-70)
- For mismatched cells: Include the expected solution in feedback
"""
        
        return prompt


def compare_and_generate_prompt(student_nb_path: str, solution_nb_path: str) -> Dict[str, Any]:
    """Convenience function to compare notebooks and generate AI prompt section"""
    comparator = OutputComparator(student_nb_path, solution_nb_path)
    results = comparator.compare_outputs()
    ai_prompt = comparator.generate_ai_prompt_section()
    
    return {
        'results': results,
        'ai_prompt_section': ai_prompt,
        'report': comparator.generate_comparison_report()
    }
