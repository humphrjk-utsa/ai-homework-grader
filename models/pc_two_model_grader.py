#!/usr/bin/env python3
"""
PC Two-Model Grading System Orchestrator
Coordinates two llama.cpp models for optimal grading on PC systems
"""

import json
import time
from typing import Dict, List, Any, Optional
from pc_llamacpp_client import PCLlamaCppClient

class PCTwoModelGrader:
    """PC-optimized two-model grading system using llama.cpp"""
    
    def __init__(self, 
                 code_model_path: str = None,
                 feedback_model_path: str = None):
        """Initialize PC two-model grader
        
        Args:
            code_model_path: Path to GGUF model for code analysis
            feedback_model_path: Path to GGUF model for feedback generation
        """
        
        # Initialize models
        print("🚀 Initializing PC Two-Model Grading System...")
        
        # Code analysis model (prefer coding-focused models)
        self.code_analyzer = PCLlamaCppClient(
            model_path=code_model_path,
            model_name="qwen" if not code_model_path else None
        )
        
        # Feedback generation model (prefer general language models)
        self.feedback_generator = PCLlamaCppClient(
            model_path=feedback_model_path,
            model_name="llama" if not feedback_model_path else None
        )
        
        self.grading_stats = {
            'code_analysis_time': 0,
            'feedback_generation_time': 0,
            'total_time': 0,
            'models_used': {
                'code_analyzer': self.code_analyzer.model_name,
                'feedback_generator': self.feedback_generator.model_name
            }
        }
        
        # Batch processing optimization
        self.models_preloaded = False
        self.batch_mode = False
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str, 
                        solution_code: str,
                        assignment_info: Dict,
                        rubric_elements: Dict) -> Dict[str, Any]:
        """
        Grade submission using PC two-model approach
        
        Args:
            student_code: Student's code
            student_markdown: Student's written responses
            solution_code: Reference solution
            assignment_info: Assignment details
            rubric_elements: Detailed rubric
            
        Returns:
            Comprehensive grading results
        """
        
        start_time = time.time()
        
        print("🚀 Starting PC Two-Model Grading System...")
        
        # Phase 1: Code Analysis
        print("🔄 Phase 1: Technical Code Analysis...")
        code_analysis_start = time.time()
        
        code_analysis = self._analyze_code(
            student_code, solution_code, assignment_info, rubric_elements
        )
        
        self.grading_stats['code_analysis_time'] = time.time() - code_analysis_start
        
        # Phase 2: Comprehensive Feedback Generation
        print("🔄 Phase 2: Generating Comprehensive Feedback...")
        feedback_start = time.time()
        
        comprehensive_feedback = self._generate_feedback(
            student_code, student_markdown, code_analysis, assignment_info, rubric_elements
        )
        
        self.grading_stats['feedback_generation_time'] = time.time() - feedback_start
        
        # Phase 3: Merge and Finalize Results
        print("🔄 Phase 3: Merging Results...")
        
        final_result = self._merge_results(code_analysis, comprehensive_feedback, assignment_info)
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        final_result['grading_stats'] = self.grading_stats.copy()
        final_result['grading_method'] = 'pc_two_model_system'
        
        print(f"🎉 PC two-model grading complete! Total time: {total_time:.1f}s")
        
        return final_result
    
    def _analyze_code(self, student_code: str, solution_code: str, 
                     assignment_info: Dict, rubric_elements: Dict) -> Dict[str, Any]:
        """Analyze code using the code analysis model"""
        
        prompt = self._build_code_analysis_prompt(
            student_code, solution_code, assignment_info, rubric_elements
        )
        
        response = self.code_analyzer.generate_response(
            prompt, max_tokens=1500, show_progress=True
        )
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 0}
        
        try:
            # Try to parse JSON response
            if "```json" in response:
                json_part = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_part)
            elif "{" in response and "}" in response:
                # Extract JSON from response
                start = response.find("{")
                end = response.rfind("}") + 1
                json_part = response[start:end]
                return json.loads(json_part)
            else:
                # Fallback: parse structured response
                return self._parse_code_analysis_response(response)
        except Exception as e:
            print(f"⚠️ Code analysis parsing failed: {e}")
            return self._parse_code_analysis_response(response)
    
    def _generate_feedback(self, student_code: str, student_markdown: str,
                          code_analysis: Dict, assignment_info: Dict, 
                          rubric_elements: Dict) -> Dict[str, Any]:
        """Generate comprehensive feedback using the feedback model"""
        
        prompt = self._build_feedback_prompt(
            student_code, student_markdown, code_analysis, assignment_info, rubric_elements
        )
        
        response = self.feedback_generator.generate_response(
            prompt, max_tokens=2000, show_progress=True
        )
        
        if not response:
            return {"error": "Feedback generation failed", "overall_score": 0}
        
        try:
            # Try to parse JSON response
            if "```json" in response:
                json_part = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_part)
            elif "{" in response and "}" in response:
                # Extract JSON from response
                start = response.find("{")
                end = response.rfind("}") + 1
                json_part = response[start:end]
                return json.loads(json_part)
            else:
                # Fallback: parse structured response
                return self._parse_feedback_response(response)
        except Exception as e:
            print(f"⚠️ Feedback parsing failed: {e}")
            return self._parse_feedback_response(response)
    
    def _build_code_analysis_prompt(self, student_code: str, solution_code: str,
                                   assignment_info: Dict, rubric_elements: Dict) -> str:
        """Build prompt for code analysis"""
        
        prompt = f"""You are an expert code reviewer analyzing student R code for data science assignments.

ASSIGNMENT: {assignment_info.get('title', 'Data Analysis Assignment')}
DESCRIPTION: {assignment_info.get('description', 'Analyze the provided dataset')}

STUDENT CODE:
```r
{student_code}
```

REFERENCE SOLUTION:
```r
{solution_code}
```

RUBRIC ELEMENTS:
{json.dumps(rubric_elements, indent=2)}

Analyze the student's code and provide a technical assessment in JSON format:

```json
{{
    "technical_score": <0-100>,
    "syntax_correctness": <0-100>,
    "logic_correctness": <0-100>,
    "code_efficiency": <0-100>,
    "best_practices": <0-100>,
    "technical_issues": [
        "List specific technical problems"
    ],
    "technical_strengths": [
        "List what the student did well technically"
    ],
    "code_suggestions": [
        "Specific code improvement suggestions"
    ]
}}
```

Focus on technical accuracy, R syntax, data manipulation correctness, and coding best practices."""
        
        return prompt
    
    def _build_feedback_prompt(self, student_code: str, student_markdown: str,
                              code_analysis: Dict, assignment_info: Dict, 
                              rubric_elements: Dict) -> str:
        """Build prompt for comprehensive feedback"""
        
        prompt = f"""You are an experienced data science instructor providing comprehensive feedback on student work.

ASSIGNMENT: {assignment_info.get('title', 'Data Analysis Assignment')}

STUDENT'S WRITTEN RESPONSES:
{student_markdown}

TECHNICAL CODE ANALYSIS RESULTS:
{json.dumps(code_analysis, indent=2)}

RUBRIC ELEMENTS:
{json.dumps(rubric_elements, indent=2)}

Provide comprehensive feedback in JSON format:

```json
{{
    "overall_score": <0-100>,
    "conceptual_understanding": <0-100>,
    "communication_clarity": <0-100>,
    "data_interpretation": <0-100>,
    "methodology_appropriateness": <0-100>,
    "detailed_feedback": {{
        "strengths": [
            "What the student did well"
        ],
        "areas_for_improvement": [
            "Specific areas needing work"
        ],
        "suggestions": [
            "Actionable improvement suggestions"
        ]
    }},
    "rubric_scores": {{
        "criterion_1": <score>,
        "criterion_2": <score>
    }},
    "instructor_comments": "Detailed paragraph of feedback for the student"
}}
```

Provide constructive, encouraging feedback that helps the student learn and improve."""
        
        return prompt
    
    def _parse_code_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse code analysis response when JSON parsing fails"""
        
        # Extract scores using regex or simple parsing
        import re
        
        result = {
            "technical_score": 75,  # Default
            "syntax_correctness": 75,
            "logic_correctness": 75,
            "code_efficiency": 75,
            "best_practices": 75,
            "technical_issues": [],
            "technical_strengths": [],
            "code_suggestions": []
        }
        
        # Try to extract scores
        score_patterns = [
            r"technical_score[:\s]*(\d+)",
            r"syntax[:\s]*(\d+)",
            r"logic[:\s]*(\d+)",
            r"efficiency[:\s]*(\d+)"
        ]
        
        for i, pattern in enumerate(score_patterns):
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if i == 0:
                    result["technical_score"] = score
                elif i == 1:
                    result["syntax_correctness"] = score
                elif i == 2:
                    result["logic_correctness"] = score
                elif i == 3:
                    result["code_efficiency"] = score
        
        # Extract issues and suggestions from text
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['issue', 'problem', 'error', 'incorrect']):
                result["technical_issues"].append(line)
            elif any(word in line.lower() for word in ['good', 'correct', 'well', 'strength']):
                result["technical_strengths"].append(line)
            elif any(word in line.lower() for word in ['suggest', 'improve', 'consider', 'recommend']):
                result["code_suggestions"].append(line)
        
        return result
    
    def _parse_feedback_response(self, response: str) -> Dict[str, Any]:
        """Parse feedback response when JSON parsing fails"""
        
        import re
        
        result = {
            "overall_score": 80,  # Default
            "conceptual_understanding": 80,
            "communication_clarity": 80,
            "data_interpretation": 80,
            "methodology_appropriateness": 80,
            "detailed_feedback": {
                "strengths": [],
                "areas_for_improvement": [],
                "suggestions": []
            },
            "rubric_scores": {},
            "instructor_comments": response[:500] + "..." if len(response) > 500 else response
        }
        
        # Try to extract overall score
        score_match = re.search(r"overall[_\s]*score[:\s]*(\d+)", response, re.IGNORECASE)
        if score_match:
            result["overall_score"] = int(score_match.group(1))
        
        return result
    
    def _merge_results(self, code_analysis: Dict, feedback: Dict, 
                      assignment_info: Dict) -> Dict[str, Any]:
        """Merge code analysis and feedback results"""
        
        # Calculate weighted final score
        technical_weight = 0.6
        feedback_weight = 0.4
        
        technical_score = code_analysis.get("technical_score", 0)
        overall_score = feedback.get("overall_score", 0)
        
        final_score = (technical_score * technical_weight + 
                      overall_score * feedback_weight)
        
        return {
            "final_score": round(final_score, 1),
            "technical_analysis": code_analysis,
            "comprehensive_feedback": feedback,
            "assignment_info": assignment_info,
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def preload_models(self):
        """Preload both models for batch processing"""
        if self.models_preloaded:
            return
            
        print("🚀 Preloading PC models for batch processing...")
        start_time = time.time()
        
        # Preload code analyzer
        print("📊 Preloading code analysis model...")
        self.code_analyzer.preload_model()
        
        # Preload feedback generator  
        print("📝 Preloading feedback generation model...")
        self.feedback_generator.preload_model()
        
        preload_time = time.time() - start_time
        self.models_preloaded = True
        
        print(f"✅ PC models preloaded in {preload_time:.1f}s")
        print("⚡ Ready for high-speed batch processing!")
    
    def enable_batch_mode(self):
        """Enable batch processing optimizations"""
        self.batch_mode = True
        self.preload_models()
    
    def grade_batch(self, submissions: List[Dict]) -> List[Dict]:
        """Grade multiple submissions efficiently"""
        print(f"🎯 Starting PC batch grading of {len(submissions)} submissions...")
        
        # Enable batch optimizations
        self.enable_batch_mode()
        
        results = []
        total_start = time.time()
        
        for i, submission in enumerate(submissions, 1):
            print(f"\n📋 Grading submission {i}/{len(submissions)}: {submission.get('student_name', 'Unknown')}")
            
            submission_start = time.time()
            
            result = self.grade_submission(
                student_code=submission['student_code'],
                student_markdown=submission['student_markdown'],
                solution_code=submission.get('solution_code', ''),
                assignment_info=submission['assignment_info'],
                rubric_elements=submission['rubric_elements']
            )
            
            submission_time = time.time() - submission_start
            result['submission_grading_time'] = submission_time
            result['student_name'] = submission.get('student_name', 'Unknown')
            
            results.append(result)
            
            print(f"✅ Completed in {submission_time:.1f}s")
        
        total_time = time.time() - total_start
        avg_time = total_time / len(submissions)
        
        print(f"\n🎉 Batch grading complete!")
        print(f"📊 Total time: {total_time:.1f}s")
        print(f"📊 Average per submission: {avg_time:.1f}s")
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "code_analyzer": self.code_analyzer.get_model_info(),
            "feedback_generator": self.feedback_generator.get_model_info(),
            "models_preloaded": self.models_preloaded,
            "batch_mode": self.batch_mode
        }

# Convenience function for easy import
def create_pc_grader(code_model_path: str = None, feedback_model_path: str = None) -> PCTwoModelGrader:
    """Create a PC two-model grader instance"""
    return PCTwoModelGrader(code_model_path, feedback_model_path)