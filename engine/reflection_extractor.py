#!/usr/bin/env python3
"""
Reflection Question Extractor
Extracts reflection questions and answers from notebooks for AI comparison
"""

import nbformat
from typing import Dict, List, Tuple
import re


class ReflectionExtractor:
    """Extracts and compares reflection questions between student and solution"""
    
    def __init__(self, student_notebook_path: str, solution_notebook_path: str = None):
        self.student_path = student_notebook_path
        self.solution_path = solution_notebook_path
        
        with open(student_notebook_path, 'r', encoding='utf-8') as f:
            self.student_nb = nbformat.read(f, as_version=4)
        
        if solution_notebook_path:
            with open(solution_notebook_path, 'r', encoding='utf-8') as f:
                self.solution_nb = nbformat.read(f, as_version=4)
        else:
            self.solution_nb = None
    
    def extract_reflections(self, notebook) -> List[Dict]:
        """Extract reflection questions and answers from a notebook"""
        markdown_cells = [cell for cell in notebook.cells if cell.cell_type == 'markdown']
        
        reflections = []
        in_reflection_section = False
        
        for cell in markdown_cells:
            source = cell.get('source', '')
            
            # Check if we've entered the reflection section
            if 'Part 9' in source or 'Reflection' in source:
                in_reflection_section = True
                continue
            
            # Only process cells in the reflection section
            if not in_reflection_section:
                continue
            
            # Look for numbered question patterns (Question 9.1, Question 9.2, etc.)
            if re.search(r'Question\s+\d+\.\d+', source, re.IGNORECASE):
                # Extract question number
                question_match = re.search(r'Question\s+(\d+\.\d+)', source, re.IGNORECASE)
                question_num = question_match.group(1) if question_match else 'Unknown'
                
                # Extract the question text (usually in bold or after "Question X:")
                question_text = self._extract_question_text(source)
                
                # Extract the answer (after "Your answer here:" or similar)
                answer_text = self._extract_answer_text(source)
                
                # Count words in answer
                word_count = len(answer_text.split()) if answer_text else 0
                
                reflections.append({
                    'question_number': question_num,
                    'question_text': question_text,
                    'answer_text': answer_text,
                    'word_count': word_count,
                    'has_answer': word_count > 20  # Minimum threshold
                })
        
        return reflections
    
    def _extract_question_text(self, source: str) -> str:
        """Extract the actual question from markdown"""
        # Look for text in bold (**text**) or after question number
        bold_match = re.search(r'\*\*(.*?)\*\*', source)
        if bold_match:
            return bold_match.group(1).strip()
        
        # Fallback: get first line with a question mark
        lines = source.split('\n')
        for line in lines:
            if '?' in line:
                return line.strip('*#- ').strip()
        
        return source[:200]  # Fallback to first 200 chars
    
    def _extract_answer_text(self, source: str) -> str:
        """Extract the answer portion from markdown"""
        # Look for answer indicators
        indicators = ['Your answer here:', 'Answer:', 'Response:', 'your answer:']
        
        for indicator in indicators:
            if indicator in source:
                # Get everything after the indicator
                answer = source.split(indicator, 1)[1].strip()
                
                # Remove common placeholders
                placeholders = [
                    '[YOUR ANSWER HERE]',
                    '[Enter your answer]',
                    '[Write your response]',
                    'TODO',
                    '[...]'
                ]
                
                for placeholder in placeholders:
                    answer = answer.replace(placeholder, '').strip()
                
                return answer
        
        # If no indicator found, check if there's substantial text after the question
        lines = source.split('\n')
        question_line_idx = 0
        for i, line in enumerate(lines):
            if '?' in line or '**' in line:
                question_line_idx = i
                break
        
        # Get text after question
        answer_lines = lines[question_line_idx + 1:]
        answer = '\n'.join(answer_lines).strip()
        
        return answer if len(answer) > 20 else ''
    
    def compare_reflections(self) -> Dict:
        """Compare student reflections to solution reflections"""
        student_reflections = self.extract_reflections(self.student_nb)
        
        if self.solution_nb:
            solution_reflections = self.extract_reflections(self.solution_nb)
        else:
            solution_reflections = []
        
        comparison = {
            'student_count': len(student_reflections),
            'solution_count': len(solution_reflections),
            'student_reflections': student_reflections,
            'solution_reflections': solution_reflections,
            'comparison_pairs': []
        }
        
        # Pair up questions by number
        for student_q in student_reflections:
            q_num = student_q['question_number']
            
            # Find matching solution question
            solution_q = next(
                (sq for sq in solution_reflections if sq['question_number'] == q_num),
                None
            )
            
            comparison['comparison_pairs'].append({
                'question_number': q_num,
                'question_text': student_q['question_text'],
                'student_answer': student_q['answer_text'],
                'student_word_count': student_q['word_count'],
                'solution_answer': solution_q['answer_text'] if solution_q else None,
                'solution_word_count': solution_q['word_count'] if solution_q else 0,
                'has_student_answer': student_q['has_answer'],
                'has_solution_answer': solution_q['has_answer'] if solution_q else False
            })
        
        return comparison
    
    def generate_ai_prompt_section(self) -> str:
        """Generate a section for AI prompts with reflection comparison"""
        comparison = self.compare_reflections()
        
        prompt = f"""
REFLECTION QUESTIONS ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Student answered {comparison['student_count']} reflection questions.

"""
        
        for pair in comparison['comparison_pairs']:
            prompt += f"\nQUESTION {pair['question_number']}: {pair['question_text'][:100]}...\n"
            prompt += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            if pair['has_student_answer']:
                prompt += f"STUDENT ANSWER ({pair['student_word_count']} words):\n"
                prompt += f"{pair['student_answer'][:300]}\n"
                if len(pair['student_answer']) > 300:
                    prompt += "...\n"
            else:
                prompt += "STUDENT ANSWER: [Not answered or insufficient detail]\n"
            
            if pair['solution_answer']:
                prompt += f"\nSOLUTION ANSWER ({pair['solution_word_count']} words):\n"
                prompt += f"{pair['solution_answer'][:300]}\n"
                if len(pair['solution_answer']) > 300:
                    prompt += "...\n"
            
            prompt += "\n"
        
        prompt += """
GRADING INSTRUCTIONS FOR REFLECTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Compare student answers to solution answers for DEPTH and QUALITY
2. Look for:
   - Understanding of concepts (not just memorization)
   - Business application and real-world connections
   - Critical thinking and analysis
   - Specific examples and details
3. DO NOT require exact wording - accept equivalent understanding
4. DO NOT penalize for different examples if they demonstrate understanding
5. Provide specific feedback on what was good and what could be improved
6. Be nuanced - recognize partial understanding vs complete misunderstanding

SCORING GUIDANCE:
- Excellent (90-100%): Demonstrates deep understanding, provides specific examples, makes business connections
- Good (80-89%): Shows solid understanding, provides some examples, makes some connections
- Adequate (70-79%): Shows basic understanding, limited examples, minimal connections
- Needs Improvement (<70%): Superficial understanding, no examples, missing key concepts
"""
        
        return prompt


def extract_reflections_for_grading(student_path: str, solution_path: str = None) -> Dict:
    """Convenience function to extract reflections for grading"""
    extractor = ReflectionExtractor(student_path, solution_path)
    return extractor.compare_reflections()
