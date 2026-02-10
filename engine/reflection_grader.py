#!/usr/bin/env python3
"""
AI-Powered Reflection Grader
Uses AI to assess the quality of reflection question answers
"""

import json
import requests
from typing import Dict, List
from reflection_extractor import ReflectionExtractor


class ReflectionGrader:
    """Grades reflection questions using AI comparison to solution"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
    
    def grade_reflections(self, student_path: str, solution_path: str, 
                         max_points: float = 5.0) -> Dict:
        """
        Grade reflection questions by comparing student to solution answers
        
        Returns:
            Dict with:
            - reflection_score: points earned (0 to max_points)
            - reflection_percentage: percentage score
            - question_scores: individual question assessments
            - feedback: detailed feedback on each question
        """
        # Extract reflections
        extractor = ReflectionExtractor(student_path, solution_path)
        comparison = extractor.compare_reflections()
        
        if comparison['student_count'] == 0:
            return {
                'reflection_score': 0,
                'reflection_percentage': 0,
                'question_scores': [],
                'feedback': ['No reflection questions found']
            }
        
        # Build AI prompt
        prompt = self._build_grading_prompt(comparison)
        
        # Get AI assessment
        try:
            ai_response = self._call_ai(prompt)
            assessment = self._parse_ai_response(ai_response)
        except Exception as e:
            print(f"⚠️ AI grading failed: {e}")
            # Fallback: give credit for answered questions
            answered = sum(1 for p in comparison['comparison_pairs'] if p['has_student_answer'])
            total = comparison['student_count']
            percentage = (answered / total * 100) if total > 0 else 0
            
            question_scores = []
            for i, p in enumerate(comparison['comparison_pairs']):
                score = 100 if p['has_student_answer'] else 0
                reasoning = f"Answered with {p['student_word_count']} words" if p['has_student_answer'] else "Not answered"
                question_scores.append({
                    'question': p['question_number'],
                    'score': score,
                    'reasoning': reasoning
                })
            
            return {
                'reflection_score': (percentage / 100) * max_points,
                'reflection_percentage': percentage,
                'question_scores': question_scores,
                'feedback': [f"Question {q['question']}: {q['reasoning']}" for q in question_scores]
            }
        
        # Calculate score
        avg_percentage = sum(q['score'] for q in assessment['question_scores']) / len(assessment['question_scores'])
        reflection_score = (avg_percentage / 100) * max_points
        
        return {
            'reflection_score': round(reflection_score, 2),
            'reflection_percentage': round(avg_percentage, 1),
            'question_scores': assessment['question_scores'],
            'feedback': assessment['feedback']
        }
    
    def _build_grading_prompt(self, comparison: Dict) -> str:
        """Build prompt for AI to grade reflections"""
        prompt = """You are grading reflection questions for a business analytics course.

TASK: Compare student answers to solution answers and assign a quality score (0-100) for each question.

GRADING CRITERIA:
1. Understanding (40%): Does the student demonstrate understanding of the concept?
2. Depth (30%): Does the answer go beyond surface-level? Are there examples?
3. Business Application (20%): Does the student connect to real-world business use?
4. Communication (10%): Is the answer clear and well-articulated?

IMPORTANT RULES:
- DO NOT require exact wording - accept equivalent understanding
- DO NOT penalize for different examples if they show understanding
- DO reward specific examples and business connections
- DO recognize partial understanding (give 60-80% for adequate answers)
- A good answer that differs from solution can still get 90-100%

"""
        
        for i, pair in enumerate(comparison['comparison_pairs']):
            prompt += f"\n{'='*80}\n"
            prompt += f"QUESTION {pair['question_number']}: {pair['question_text']}\n"
            prompt += f"{'='*80}\n\n"
            
            prompt += f"STUDENT ANSWER ({pair['student_word_count']} words):\n"
            prompt += f"{pair['student_answer']}\n\n"
            
            if pair['solution_answer']:
                prompt += f"SOLUTION ANSWER ({pair['solution_word_count']} words):\n"
                prompt += f"{pair['solution_answer']}\n\n"
            
            prompt += f"YOUR ASSESSMENT FOR QUESTION {pair['question_number']}:\n"
            prompt += "- Score (0-100): \n"
            prompt += "- Reasoning: \n\n"
        
        prompt += """
OUTPUT FORMAT (JSON ONLY):
{
  "question_scores": [
    {
      "question": "9.1",
      "score": 85,
      "reasoning": "Good understanding of data cleaning importance. Mentions accuracy and reliability. Could add specific example of how outliers skew results."
    },
    {
      "question": "9.2",
      "score": 90,
      "reasoning": "Excellent answer. Identifies patterns, mentions resource allocation and business applications. Slightly less detailed than solution but demonstrates solid understanding."
    }
  ]
}

Output ONLY the JSON, no other text.
"""
        
        return prompt
    
    def _call_ai(self, prompt: str, model: str = "gemma3:27b-it-q8_0") -> str:
        """Call Ollama API to grade reflections"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 2000,
                "temperature": 0.3,  # Lower temperature for more consistent grading
                "top_p": 0.9
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            raise RuntimeError(f"Ollama API error: {response.status_code}")
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured assessment"""
        # Try to extract JSON
        try:
            # Look for JSON in response
            if "```json" in response:
                json_part = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_part = response[start:end]
            else:
                json_part = response
            
            assessment = json.loads(json_part)
            
            # Build feedback list
            feedback = []
            for q in assessment['question_scores']:
                feedback.append(f"Question {q['question']}: {q['reasoning']}")
            
            assessment['feedback'] = feedback
            return assessment
            
        except Exception as e:
            print(f"⚠️ Could not parse AI response: {e}")
            print(f"Response: {response[:200]}")
            raise
    
    def generate_feedback_summary(self, grading_result: Dict) -> str:
        """Generate human-readable feedback summary"""
        summary = f"Reflection Questions: {grading_result['reflection_percentage']:.0f}%\n\n"
        
        for item in grading_result['feedback']:
            summary += f"• {item}\n"
        
        return summary


def grade_reflections_for_assignment(student_path: str, solution_path: str, 
                                     max_points: float = 5.0) -> Dict:
    """Convenience function to grade reflections"""
    grader = ReflectionGrader()
    return grader.grade_reflections(student_path, solution_path, max_points)
