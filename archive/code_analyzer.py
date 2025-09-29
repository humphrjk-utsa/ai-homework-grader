#!/usr/bin/env python3
"""
Code Analyzer Service using Qwen 3.0 Coder
Specialized for technical code evaluation and analysis
"""

import json
from typing import Dict, List, Any, Optional
from simple_mlx_client import SimpleMLXClient

class CodeAnalyzer:
    """Specialized code analysis using Qwen 3.0 Coder model"""
    
    def __init__(self):
        # Initialize with Qwen 3.0 Coder model - no fallbacks
        self.coder_model = SimpleMLXClient("mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16")
        self.model_loaded = False
    
    def analyze_code(self, student_code: str, solution_code: str, rubric_elements: Dict) -> Dict[str, Any]:
        """
        Analyze student code for technical correctness and implementation quality
        
        Args:
            student_code: Student's R/Python code
            solution_code: Reference solution code
            rubric_elements: Technical rubric elements to evaluate
            
        Returns:
            Dict with technical analysis results
        """
        
        prompt = self._create_code_analysis_prompt(student_code, solution_code, rubric_elements)
        
        try:
            if not self.model_loaded:
                print("🔄 Loading Qwen 3.0 Coder for technical analysis...")
                self.coder_model._load_model()
                self.model_loaded = True
            
            response = self.coder_model.generate_response(prompt, max_tokens=2400)
            
            if response:
                return self._parse_code_analysis_response(response)
            else:
                return self._fallback_code_analysis()
                
        except Exception as e:
            print(f"⚠️ Code analysis failed: {e}")
            return self._fallback_code_analysis()
    
    def _create_code_analysis_prompt(self, student_code: str, solution_code: str, rubric_elements: Dict) -> str:
        """Create specialized prompt for code analysis"""
        
        # Extract technical rubric elements
        technical_elements = []
        for element_name, element_data in rubric_elements.items():
            if element_data.get('category') == 'automated':
                technical_elements.append({
                    'name': element_name,
                    'points': element_data.get('max_points', 0),
                    'description': element_data.get('description', ''),
                    'checks': element_data.get('automated_checks', [])
                })
        
        prompt = f"""You are an expert code reviewer specializing in R and Python data analysis code. Your task is to perform a detailed technical analysis of student code.

REFERENCE SOLUTION:
```r
{solution_code}
```

STUDENT CODE:
```r
{student_code}
```

TECHNICAL EVALUATION CRITERIA:
"""
        
        for element in technical_elements:
            prompt += f"""
{element['name'].upper()} ({element['points']} points):
- Description: {element['description']}
- Required implementations:
"""
            for check in element['checks']:
                prompt += f"  • {check}\n"
        
        prompt += """

ANALYSIS INSTRUCTIONS (BEGINNER-FRIENDLY APPROACH):
1. SYNTAX & EXECUTION: Check for syntax errors, proper R/Python syntax, executable code
2. FUNCTION USAGE: Verify correct use of required functions (tidyverse, base R, etc.)
3. DATA STRUCTURES: Analyze variable creation, data frame operations, proper data types
4. ALGORITHM IMPLEMENTATION: Check if statistical methods are correctly implemented
5. OUTPUT VERIFICATION: Assess if code produces expected results
6. CODE QUALITY: Evaluate structure, efficiency, and best practices

GRADING PHILOSOPHY FOR BUSINESS ANALYTICS STUDENTS:
- REWARD COMPLETION: If basic requirements are met, score should be 9+/10
- WORKING CODE: Code that runs without errors deserves excellent marks (9-10/10)
- BUSINESS FOCUS: These are business students, not computer science majors
- PRACTICAL APPROACH: Focus on business applications, not technical details
- COMPLETION = SUCCESS: If they got the data imported and explored, that's excellent work
- MINIMUM SCORE: Students who complete all requirements should get 94%+ (35.2/37.5)
- FIRST-TIME STUDENTS: These are beginners - working code deserves EXCELLENT marks
- COMPLETION BONUS: If code runs and requirements met, start scoring at 9/10 minimum

For each technical element, provide:
- IMPLEMENTED: Yes/No/Partial
- CORRECTNESS: Score out of max points
- ISSUES: List specific technical problems
- STRENGTHS: What was implemented well

Respond in JSON format:
{
    "technical_summary": {
        "syntax_score": <0-10>,
        "implementation_score": <0-10>,
        "correctness_score": <0-10>,
        "total_technical_score": <calculated_total>
    },
    "element_analysis": {
        "element_name": {
            "implemented": "Yes/No/Partial",
            "score": <points_earned>,
            "max_points": <max_possible>,
            "issues": ["issue1", "issue2"],
            "strengths": ["strength1", "strength2"],
            "code_snippets": ["relevant code that works/doesn't work"]
        }
    },
    "code_quality": {
        "syntax_errors": ["error1", "error2"],
        "best_practices": ["practice1", "practice2"],
        "efficiency_notes": "comments on code efficiency",
        "readability_score": <1-5>
    },
    "execution_analysis": {
        "likely_to_run": true/false,
        "expected_outputs": ["output1", "output2"],
        "potential_runtime_errors": ["error1", "error2"]
    }
}

Focus on TECHNICAL ACCURACY and CODE CORRECTNESS. Be precise and specific in your analysis."""

        return prompt
    
    def _parse_code_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the code analysis response from Qwen"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_code_analysis()
                
        except json.JSONDecodeError:
            print("⚠️ Failed to parse code analysis JSON, using fallback")
            return self._fallback_code_analysis()
    
    def _fallback_code_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when Qwen fails"""
        return {
            "technical_summary": {
                "syntax_score": 5,
                "implementation_score": 5,
                "correctness_score": 5,
                "total_technical_score": 15
            },
            "element_analysis": {},
            "code_quality": {
                "syntax_errors": [],
                "best_practices": [],
                "efficiency_notes": "Code analysis unavailable",
                "readability_score": 3
            },
            "execution_analysis": {
                "likely_to_run": True,
                "expected_outputs": [],
                "potential_runtime_errors": []
            }
        }
    
    def is_available(self) -> bool:
        """Check if code analyzer is available"""
        return self.coder_model.is_available()