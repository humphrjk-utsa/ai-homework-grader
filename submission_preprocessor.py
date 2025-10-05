#!/usr/bin/env python3
"""
Submission Preprocessor
Normalizes and cleans submissions before AI grading to improve parsing success
"""

import re
import json
import nbformat
from typing import Dict, List, Any, Tuple


class SubmissionPreprocessor:
    """Preprocess submissions to fix common issues before AI grading"""
    
    # Define penalty points for each type of fix (out of 37.5 total)
    FIX_PENALTIES = {
        'pipe_syntax_error': 0.5,      # Minor syntax error - small penalty
        'whitespace': 0.0,              # Style issue - no penalty
        'quotes': 0.0,                  # Style issue - no penalty
        'library_comment': 0.0,         # Works in Codespace - no penalty
    }
    
    def __init__(self):
        self.fixes_applied = []
        self.fix_types = []  # Track types for penalty calculation
    
    def preprocess_notebook(self, notebook_path: str) -> Tuple[str, str, List[str]]:
        """
        Preprocess notebook and return cleaned code and markdown
        
        Returns:
            Tuple of (cleaned_code, cleaned_markdown, list_of_fixes_applied)
        """
        self.fixes_applied = []
        
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            return "", "", [f"Failed to read notebook: {e}"]
        
        cleaned_code = ""
        cleaned_markdown = ""
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                # Clean and normalize code
                code_content = self._clean_code_cell(cell.source)
                cleaned_code += code_content + "\n\n"
                
                # Include outputs (already clean)
                if hasattr(cell, 'outputs') and cell.outputs:
                    cleaned_code += "# OUTPUT:\n"
                    for output in cell.outputs:
                        if output.output_type == 'stream':
                            cleaned_code += output.text + "\n"
                        elif output.output_type == 'execute_result' and 'text/plain' in output.data:
                            cleaned_code += output.data['text/plain'] + "\n"
                        elif output.output_type == 'display_data' and 'text/plain' in output.data:
                            cleaned_code += output.data['text/plain'] + "\n"
                    cleaned_code += "\n"
                    
            elif cell.cell_type == 'markdown':
                cleaned_markdown += cell.source + "\n\n"
        
        return cleaned_code, cleaned_markdown, self.fixes_applied
    
    def _clean_code_cell(self, code: str) -> str:
        """Clean and normalize a code cell"""
        original_code = code
        
        # NOTE: We DON'T uncomment libraries anymore because:
        # 1. Code may work without explicit library() if kernel has it loaded
        # 2. This is a style preference, not a syntax error
        # 3. We only want to fix things that break AI parsing
        
        # Fix 1: (Removed - see note above)
        
        # Fix 2: Fix pipe chain syntax errors
        # Pattern: %>% function(df$column) should be %>% function(column)
        pipe_with_dollar = re.findall(r'%>%\s+(\w+)\([^)]*\$[^)]*\)', code)
        if pipe_with_dollar:
            # Fix count(df$column) -> count(column)
            original = code
            code = re.sub(
                r'(%>%\s+count\()(\w+)\$(\w+)(\))',
                r'\1\3\4',
                code
            )
            if code != original:
                self.fixes_applied.append("Fixed pipe chain $ notation in count()")
                self.fix_types.append('pipe_syntax_error')
            
            # Fix select(df$column, df$column2) -> select(column, column2)
            original = code
            code = re.sub(
                r'(%>%\s+select\()([^)]*)',
                lambda m: m.group(1) + re.sub(r'\w+\$(\w+)', r'\1', m.group(2)),
                code
            )
            if code != original:
                self.fixes_applied.append("Fixed pipe chain $ notation in select()")
                self.fix_types.append('pipe_syntax_error')
            
            # Fix filter(df$column > value) -> filter(column > value)
            original = code
            code = re.sub(
                r'(%>%\s+filter\()([^)]*)',
                lambda m: m.group(1) + re.sub(r'\w+\$(\w+)', r'\1', m.group(2)),
                code
            )
            if code != original:
                self.fixes_applied.append("Fixed pipe chain $ notation in filter()")
                self.fix_types.append('pipe_syntax_error')
        
        # Fix 3: Normalize whitespace (REMOVED - not relevant for grading)
        # We don't track whitespace fixes anymore as they're style preferences
        
        # Fix 4: Fix common R syntax issues (REMOVED - too aggressive)
        # We only fix actual syntax errors, not style preferences
        
        # Fix 5: Normalize quotes (smart quotes to regular quotes)
        # We fix them silently but don't report it - it's not relevant to students
        if '"' in code or '"' in code or ''' in code or ''' in code:
            code = code.replace('"', '"').replace('"', '"')
            code = code.replace(''', "'").replace(''', "'")
            # Don't track this - it's automatic and not relevant
        
        return code
    
    def preprocess_code_string(self, code: str) -> Tuple[str, List[str]]:
        """
        Preprocess raw code string (for non-notebook submissions)
        
        Returns:
            Tuple of (cleaned_code, list_of_fixes_applied)
        """
        self.fixes_applied = []
        cleaned = self._clean_code_cell(code)
        return cleaned, self.fixes_applied
    
    def format_for_ai(self, code: str, markdown: str, max_code_length: int = 15000) -> Dict[str, Any]:
        """
        Format cleaned content for AI consumption
        
        Args:
            code: Cleaned code content
            markdown: Cleaned markdown content
            max_code_length: Maximum code length to send to AI
            
        Returns:
            Dict with formatted content and metadata
        """
        # Truncate if too long (but keep structure)
        if len(code) > max_code_length:
            # Try to keep complete cells
            code_parts = code.split('\n\n')
            truncated_code = ""
            for part in code_parts:
                if len(truncated_code) + len(part) < max_code_length:
                    truncated_code += part + "\n\n"
                else:
                    break
            
            code = truncated_code + "\n\n# [Code truncated for AI processing]"
            self.fixes_applied.append(f"Truncated code to {max_code_length} chars")
        
        return {
            'code': code,
            'markdown': markdown,
            'preprocessing_applied': self.fixes_applied,
            'needs_manual_review': len(self.fixes_applied) > 5  # Flag if many issues
        }
    
    def get_preprocessing_summary(self) -> str:
        """Get human-readable summary of preprocessing"""
        if not self.fixes_applied:
            return "No preprocessing needed - submission was clean"
        
        return "Preprocessing applied:\n" + "\n".join(f"  • {fix}" for fix in self.fixes_applied)
    
    def calculate_penalty(self) -> float:
        """
        Calculate penalty points for fixes applied
        
        Returns:
            Penalty in points (out of 37.5 total)
        """
        total_penalty = 0.0
        for fix_type in self.fix_types:
            total_penalty += self.FIX_PENALTIES.get(fix_type, 0.0)
        
        return total_penalty
    
    def get_penalty_explanation(self) -> str:
        """Get explanation of penalties"""
        if not self.fix_types:
            return "No penalties - submission was clean"
        
        penalty = self.calculate_penalty()
        if penalty == 0:
            return "No penalties - fixes were style-related only"
        
        explanation = f"Preprocessing penalty: -{penalty:.1f} points\n"
        explanation += "Breakdown:\n"
        
        # Count each type
        from collections import Counter
        type_counts = Counter(self.fix_types)
        
        for fix_type, count in type_counts.items():
            penalty_per = self.FIX_PENALTIES.get(fix_type, 0.0)
            if penalty_per > 0:
                total_for_type = penalty_per * count
                explanation += f"  • {fix_type}: {count} × {penalty_per} = -{total_for_type:.1f} points\n"
        
        return explanation


def preprocess_submission_for_grading(notebook_path: str) -> Dict[str, Any]:
    """
    Convenience function to preprocess a submission
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Dict with cleaned content and preprocessing metadata
    """
    preprocessor = SubmissionPreprocessor()
    code, markdown, fixes = preprocessor.preprocess_notebook(notebook_path)
    formatted = preprocessor.format_for_ai(code, markdown)
    
    return {
        'cleaned_code': formatted['code'],
        'cleaned_markdown': formatted['markdown'],
        'fixes_applied': fixes,
        'needs_manual_review': formatted['needs_manual_review'],
        'preprocessing_summary': preprocessor.get_preprocessing_summary(),
        'penalty_points': preprocessor.calculate_penalty(),
        'penalty_explanation': preprocessor.get_penalty_explanation()
    }


if __name__ == "__main__":
    # Test the preprocessor
    import sys
    
    if len(sys.argv) > 1:
        notebook_path = sys.argv[1]
        print(f"Testing preprocessor on: {notebook_path}")
        print("=" * 80)
        
        result = preprocess_submission_for_grading(notebook_path)
        
        print("\n📋 Preprocessing Summary:")
        print(result['preprocessing_summary'])
        
        if result['needs_manual_review']:
            print("\n⚠️ This submission may need manual review (many issues fixed)")
        
        print(f"\n📊 Stats:")
        print(f"  Code length: {len(result['cleaned_code'])} chars")
        print(f"  Markdown length: {len(result['cleaned_markdown'])} chars")
        print(f"  Fixes applied: {len(result['fixes_applied'])}")
    else:
        print("Usage: python submission_preprocessor.py <notebook_path>")
