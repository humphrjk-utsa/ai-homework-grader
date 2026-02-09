#!/usr/bin/env python3
"""
Submission Preprocessor
Normalizes and cleans submissions before AI grading to improve parsing success
"""

import re
import json
import nbformat
from typing import Dict, List, Any, Optional, Tuple


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

    # ─── Prompt Optimization Methods ─────────────────────────────────────────

    def extract_paired_diff(self, student_notebook_path: str, solution_notebook_path: str,
                            template_code_string: str) -> Tuple[Optional[str], int]:
        """Extract student and solution cells paired by position for side-by-side comparison.

        Walks both notebooks in lockstep, matching code cells by index.
        For each position where either the student or solution differs from the
        template, includes both side by side so the AI can directly compare
        student work against the correct answer.

        Uses markdown headers from the notebook as section labels.

        Args:
            student_notebook_path: Path to student's notebook file
            solution_notebook_path: Path to solution notebook file
            template_code_string: Concatenated template code string

        Returns:
            Tuple of (paired_diff_string, student_modified_count) or (None, 0) if failed
        """
        try:
            with open(student_notebook_path, 'r', encoding='utf-8') as f:
                student_nb = nbformat.read(f, as_version=4)
            with open(solution_notebook_path, 'r', encoding='utf-8') as f:
                solution_nb = nbformat.read(f, as_version=4)
        except Exception:
            return None, 0

        # Build template line set
        template_lines = set()
        for line in template_code_string.split('\n'):
            normalized = line.strip()
            if normalized and not normalized.startswith('#'):
                template_lines.add(normalized)

        # Extract code cells with section labels from both notebooks
        student_sections = self._extract_sections_with_labels(student_nb)
        solution_sections = self._extract_sections_with_labels(solution_nb)

        max_sections = max(len(student_sections), len(solution_sections))
        paired: List[Dict[str, Any]] = []

        for i in range(max_sections):
            student_sec = student_sections[i] if i < len(student_sections) else None
            solution_sec = solution_sections[i] if i < len(solution_sections) else None

            # Check if student modified this cell
            student_modified = False
            student_code = ""
            student_output = ""
            student_error = False
            section_label = ""

            if student_sec:
                section_label = student_sec['label']
                student_code = student_sec['source']
                student_lines = [l.strip() for l in student_code.split('\n')
                                 if l.strip() and not l.strip().startswith('#')
                                 and 'YOUR CODE HERE' not in l.upper()
                                 and 'TODO' not in l.upper()]
                student_modified = bool(student_lines) and not all(
                    l in template_lines for l in student_lines)
                student_output = self._extract_and_compress_output(student_sec['cell'])
                student_error = self._check_cell_for_errors(student_sec['cell'])

            # Check if solution has an answer for this cell
            solution_has_answer = False
            solution_code = ""
            solution_output = ""

            if solution_sec:
                if not section_label:
                    section_label = solution_sec['label']
                solution_code = solution_sec['source']
                sol_lines = [l.strip() for l in solution_code.split('\n')
                             if l.strip() and not l.strip().startswith('#')]
                solution_has_answer = bool(sol_lines) and not all(
                    l in template_lines for l in sol_lines)
                solution_output = self._extract_and_compress_output(solution_sec['cell'])

            # Include if either has non-template content
            if student_modified or solution_has_answer:
                paired.append({
                    'label': section_label or f"Section {i+1}",
                    'student_code': self._clean_code_cell(student_code) if student_modified else '[Template only - no student work]',
                    'student_output': student_output if student_modified else '',
                    'student_error': student_error,
                    'student_modified': student_modified,
                    'solution_code': solution_code if solution_has_answer else '[Same as template]',
                    'solution_output': solution_output if solution_has_answer else '',
                })

        if not paired:
            return None, 0

        modified_count = sum(1 for p in paired if p['student_modified'])
        parts = [f"PAIRED CODE COMPARISON ({modified_count} sections with student work, {len(paired)} total answer sections):\n"]

        for section in paired:
            parts.append(f"=== {section['label']} ===")
            parts.append("YOUR CODE:")
            parts.append(section['student_code'])
            if section['student_output']:
                parts.append(f"# OUTPUT:\n{section['student_output']}")
            if section['student_error']:
                parts.append("# ⚠ ERROR IN OUTPUT")
            parts.append("")
            parts.append("REFERENCE SOLUTION:")
            parts.append(section['solution_code'])
            if section['solution_output']:
                parts.append(f"# EXPECTED OUTPUT:\n{section['solution_output']}")

            # Status with inline output comparison
            if not section['student_modified']:
                parts.append("STATUS: ❌ Section not attempted")
            elif section['student_error']:
                parts.append("STATUS: ⚠ Student code has errors - compare to reference solution")
            elif section['student_output'] and section['solution_output']:
                match = self._quick_output_match(section['student_output'], section['solution_output'])
                if match == 'match':
                    parts.append("STATUS: ✅ Outputs match — different approach is valid, give FULL CREDIT")
                elif match == 'partial':
                    parts.append("STATUS: ⚠ Outputs partially match — check for minor differences")
                else:
                    parts.append("STATUS: ❌ Outputs differ — review student code for errors")
            parts.append("")

        return '\n'.join(parts), modified_count

    @staticmethod
    def _quick_output_match(student_output: str, solution_output: str) -> str:
        """Quick heuristic comparison of two output strings.

        Extracts key numbers and row counts from both outputs and checks overlap.
        Strips ANSI escape codes first to avoid false mismatches.
        Returns 'match', 'partial', or 'mismatch'.
        """
        import re

        def strip_ansi(text: str) -> str:
            return re.sub(r'\x1b\[[0-9;]*m', '', text)

        def extract_numbers(text: str) -> set:
            clean_text = strip_ansi(text)
            # Extract all numbers (integers and decimals) from output
            nums = re.findall(r'[\d,]+\.?\d*', clean_text)
            normalized = set()
            for n in nums:
                clean = n.replace(',', '')
                try:
                    val = float(clean)
                    # Round to 1 decimal to handle rounding differences
                    normalized.add(round(val, 1))
                except ValueError:
                    pass
            return normalized

        student_nums = extract_numbers(student_output)
        solution_nums = extract_numbers(solution_output)

        if not student_nums or not solution_nums:
            # No numbers to compare — fall back to text similarity
            s_clean = ' '.join(strip_ansi(student_output).split()).lower()
            r_clean = ' '.join(strip_ansi(solution_output).split()).lower()
            if s_clean == r_clean:
                return 'match'
            if len(s_clean) < 100 and len(r_clean) < 100:
                return 'partial' if (s_clean in r_clean or r_clean in s_clean) else 'mismatch'
            return 'partial'

        # Number-based comparison (order independent)
        intersection = student_nums & solution_nums
        union = student_nums | solution_nums
        overlap = len(intersection) / len(union) if union else 0

        if overlap >= 0.8:
            return 'match'
        elif overlap >= 0.5:
            return 'partial'
        else:
            return 'mismatch'

    def _extract_sections_with_labels(self, nb) -> List[Dict[str, Any]]:
        """Extract code cells with preceding markdown section headers as labels."""
        sections: List[Dict[str, Any]] = []
        current_label = ""

        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                # Grab the first header line as section label
                for line in cell.source.strip().split('\n'):
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        current_label = stripped.lstrip('#').strip()
                        break
            elif cell.cell_type == 'code':
                source = cell.source.strip()
                if source:
                    sections.append({
                        'label': current_label or f"Code Cell {len(sections)+1}",
                        'source': source,
                        'cell': cell,
                    })

        return sections

    def extract_student_diff(self, student_notebook_path: str, template_code_string: str) -> Tuple[Optional[str], int]:
        """Extract only cells where student added code beyond the template.

        Compares each code cell against template lines. Only includes cells
        where the student wrote new code (not just template boilerplate).
        Outputs are compressed to remove package loading noise and truncate
        large data frames.

        Args:
            student_notebook_path: Path to student's notebook file
            template_code_string: Concatenated template code string

        Returns:
            Tuple of (diff_code_string, modified_cell_count) or (None, 0) if failed
        """
        try:
            with open(student_notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception:
            return None, 0

        # Build set of normalized template lines for comparison
        template_lines = set()
        for line in template_code_string.split('\n'):
            normalized = line.strip()
            if normalized and not normalized.startswith('#'):
                template_lines.add(normalized)

        modified_cells = []
        total_code_cells = 0

        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue
            total_code_cells += 1

            source = cell.source.strip()
            if not source:
                continue

            # Get student's substantive code lines (non-comment, non-blank, non-TODO)
            student_lines = []
            for line in source.split('\n'):
                stripped = line.strip()
                if (stripped and not stripped.startswith('#')
                    and 'YOUR CODE HERE' not in stripped.upper()
                    and 'TODO' not in stripped.upper()):
                    student_lines.append(stripped)

            # Skip if all code lines are from template
            if not student_lines or all(line in template_lines for line in student_lines):
                continue

            # This cell has student modifications - include it
            code_text = self._clean_code_cell(source)
            output_text = self._extract_and_compress_output(cell)
            has_error = self._check_cell_for_errors(cell)

            modified_cells.append({
                'code': code_text,
                'output': output_text,
                'has_error': has_error
            })

        if not modified_cells:
            return None, 0

        # Format for prompt
        parts = [f"STUDENT-MODIFIED CODE ({len(modified_cells)}/{total_code_cells} cells changed):\n"]
        for i, cell in enumerate(modified_cells):
            parts.append(f"--- Section {i+1} ---")
            parts.append(cell['code'])
            if cell['output']:
                parts.append(f"# OUTPUT:\n{cell['output']}")
            if cell['has_error']:
                parts.append("# ⚠ ERROR IN OUTPUT")
            parts.append("")

        return '\n'.join(parts), len(modified_cells)

    def extract_relevant_solution(self, solution_notebook_path: str, template_code_string: str) -> Optional[str]:
        """Extract solution cells that have changes beyond the template.

        Only returns solution code for sections where the template had TODOs
        or where the solution differs from the template (i.e., the actual
        answer cells, not boilerplate setup).

        Args:
            solution_notebook_path: Path to solution notebook file
            template_code_string: Concatenated template code string

        Returns:
            Optimized solution code string, or None if failed
        """
        try:
            with open(solution_notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception:
            return None

        template_lines = set()
        for line in template_code_string.split('\n'):
            normalized = line.strip()
            if normalized and not normalized.startswith('#'):
                template_lines.add(normalized)

        solution_cells = []
        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue

            source = cell.source.strip()
            if not source:
                continue

            sol_lines = [l.strip() for l in source.split('\n')
                         if l.strip() and not l.strip().startswith('#')]

            if sol_lines and all(line in template_lines for line in sol_lines):
                continue  # Boilerplate - skip

            output_text = self._extract_and_compress_output(cell)
            solution_cells.append({'code': source, 'output': output_text})

        if not solution_cells:
            return None

        parts = [f"REFERENCE SOLUTION ({len(solution_cells)} sections):\n"]
        for i, cell in enumerate(solution_cells):
            parts.append(f"--- Section {i+1} ---")
            parts.append(cell['code'])
            if cell['output']:
                parts.append(f"# EXPECTED OUTPUT:\n{cell['output']}")
            parts.append("")

        return '\n'.join(parts)

    def _extract_and_compress_output(self, cell, max_rows: int = 5) -> str:
        """Extract and compress cell output, removing boilerplate noise.

        Strips package loading messages, truncates large data frame prints
        to first/last N rows, and preserves error messages in full.
        """
        if not hasattr(cell, 'outputs') or not cell.outputs:
            return ""

        output_parts = []
        for output in cell.outputs:
            text = ""
            if output.output_type == 'stream':
                text = output.text
            elif output.output_type == 'execute_result' and 'text/plain' in output.data:
                text = output.data['text/plain']
            elif output.output_type == 'display_data' and 'text/plain' in output.data:
                text = output.data['text/plain']
            elif output.output_type == 'error':
                # Always include full error messages
                traceback_lines = output.get('traceback', [])
                if traceback_lines:
                    text = '\n'.join(str(t) for t in traceback_lines)
                else:
                    text = output.get('evalue', 'Error')

            if text:
                output_parts.append(self._compress_output_text(text, max_rows))

        return '\n'.join(output_parts)

    @staticmethod
    def _compress_output_text(text: str, max_rows: int = 5) -> str:
        """Compress verbose output text by removing boilerplate and truncating."""
        # Strip ANSI escape codes (color codes from R/IRkernel output)
        text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        lines = text.split('\n')

        # Filter out package loading noise
        skip_patterns = [
            'Loading required package', 'Attaching package',
            'The following objects are masked', 'Registered S3 method',
            '── Attaching', '── Conflicts', '✔ ', 'ℹ ',
            'Warning message:', 'also defined by', 'Rows:',
            'Delimiter:', '── Column specification'
        ]

        filtered = [l for l in lines
                     if not any(p in l for p in skip_patterns)]

        # Remove consecutive blank lines
        deduped: List[str] = []
        for line in filtered:
            if line.strip() == '' and deduped and deduped[-1].strip() == '':
                continue
            deduped.append(line)

        lines = deduped

        # Truncate if too many lines (e.g., large data frame print)
        if len(lines) > max_rows * 2 + 3:
            head = lines[:max_rows]
            tail = lines[-max_rows:]
            omitted = len(lines) - max_rows * 2
            return '\n'.join(head + [f'[... {omitted} rows omitted ...]'] + tail)

        return '\n'.join(lines)

    @staticmethod
    def _check_cell_for_errors(cell) -> bool:
        """Check if cell output contains errors."""
        if not hasattr(cell, 'outputs') or not cell.outputs:
            return False
        for output in cell.outputs:
            if output.output_type == 'error':
                return True
            if output.output_type == 'stream':
                text = output.get('text', '')
                if 'Error in ' in text or 'Error:' in text:
                    return True
        return False

    @staticmethod
    def create_smart_code_summary(student_code: str, template_code: str = "", max_chars: int = 2000) -> str:
        """Create a smart summary of student-written code for feedback prompt.

        Prioritizes student additions over template boilerplate. Extracts only
        the lines the student actually wrote, skipping template code, comments,
        and output sections.

        Args:
            student_code: Full concatenated student code
            template_code: Full concatenated template code
            max_chars: Maximum characters for the summary

        Returns:
            Condensed code summary focusing on student work
        """
        if not template_code:
            return student_code[:max_chars]

        # Build set of template lines
        template_lines = set()
        for line in template_code.split('\n'):
            normalized = line.strip()
            if normalized and not normalized.startswith('#'):
                template_lines.add(normalized)

        # Extract student-written code blocks
        student_additions = []
        current_block: List[str] = []
        in_output = False

        for line in student_code.split('\n'):
            stripped = line.strip()

            # Skip output sections
            if stripped == '# OUTPUT:':
                if current_block:
                    student_additions.append('\n'.join(current_block))
                    current_block = []
                in_output = True
                continue

            if in_output:
                if stripped == '':
                    in_output = False
                continue

            # Skip comments and blanks for block boundaries
            if not stripped or stripped.startswith('#'):
                if current_block and stripped == '':
                    student_additions.append('\n'.join(current_block))
                    current_block = []
                continue

            # Include if not in template
            if stripped not in template_lines:
                current_block.append(line)

        if current_block:
            student_additions.append('\n'.join(current_block))

        summary = '\n\n'.join(s for s in student_additions if s.strip())

        if not summary.strip():
            return student_code[:max_chars]  # Fallback

        if len(summary) > max_chars:
            summary = summary[:max_chars] + '\n# [Summary truncated]'

        return summary


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
