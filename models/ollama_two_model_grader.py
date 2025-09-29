#!/usr/bin/env python3
"""
Ollama Two-Model Grading System
Uses your existing Ollama models for parallel homework grading
"""

import json
import time
import requests
import concurrent.futures
from typing import Dict, List, Any, Optional

class OllamaTwoModelGrader:
    """Two-model grader using Ollama with your existing models"""
    
    def __init__(self, 
                 code_model: str = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
                 feedback_model: str = "gemma3:27b-it-q8_0",
                 ollama_url: str = "http://localhost:11434"):
        """Initialize Ollama two-model grader
        
        Args:
            code_model: Ollama model for code analysis (Qwen 3.0 Coder)
            feedback_model: Ollama model for feedback generation (Gemma 3.0)
            ollama_url: Ollama server URL
        """
        
        self.code_model = code_model
        self.feedback_model = feedback_model
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        
        print(f"🚀 Initializing Ollama Two-Model Grading System...")
        print(f"🤖 Code Analyzer: {code_model}")
        print(f"📝 Feedback Generator: {feedback_model}")
        
        # Performance tracking
        self.grading_stats = {
            'code_analysis_time': 0,
            'feedback_generation_time': 0,
            'parallel_time': 0,
            'total_time': 0,
            'parallel_efficiency': 0.0,
            'models_used': {
                'code_analyzer': code_model,
                'feedback_generator': feedback_model
            }
        }
        
        # Parallel processing
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.models_ready = False
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server is running")
                return True
            else:
                print(f"❌ Ollama server error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            return False
    
    def check_models_available(self) -> bool:
        """Check if required models are available in Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                code_available = self.code_model in available_models
                feedback_available = self.feedback_model in available_models
                
                print(f"🤖 Code model ({self.code_model}): {'✅' if code_available else '❌'}")
                print(f"📝 Feedback model ({self.feedback_model}): {'✅' if feedback_available else '❌'}")
                
                if code_available and feedback_available:
                    print("✅ All required models are available")
                    self.models_ready = True
                    return True
                else:
                    print("❌ Some models are missing")
                    return False
            else:
                print("❌ Failed to get model list from Ollama")
                return False
        except Exception as e:
            print(f"❌ Error checking models: {e}")
            return False
    
    def generate_with_ollama(self, model: str, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=300)  # 5 min timeout
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            return None
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str, 
                        solution_code: str,
                        assignment_info: Dict,
                        rubric_elements: Dict) -> Dict[str, Any]:
        """
        Grade submission using Ollama parallel processing
        """
        
        start_time = time.time()
        
        print("🚀 Starting Ollama Parallel Grading System...")
        
        # Check prerequisites
        if not self.check_ollama_connection():
            raise RuntimeError("Ollama server not accessible")
        
        if not self.check_models_available():
            raise RuntimeError("Required models not available in Ollama")
        
        # Execute tasks in parallel
        print("⚡ Executing code analysis and feedback generation in parallel...")
        parallel_start = time.time()
        
        # Submit both tasks simultaneously
        future_code = self.executor.submit(
            self._execute_code_analysis, 
            student_code, solution_code, assignment_info, rubric_elements
        )
        
        future_feedback = self.executor.submit(
            self._execute_feedback_generation,
            student_code, student_markdown, assignment_info, rubric_elements
        )
        
        # Wait for both results
        code_analysis = future_code.result()
        comprehensive_feedback = future_feedback.result()
        
        parallel_time = time.time() - parallel_start
        self.grading_stats['parallel_time'] = parallel_time
        
        # Calculate efficiency (how much faster than sequential)
        sequential_time = (self.grading_stats['code_analysis_time'] + 
                          self.grading_stats['feedback_generation_time'])
        
        if sequential_time > 0:
            self.grading_stats['parallel_efficiency'] = sequential_time / parallel_time
        
        # Merge results
        print("🔄 Merging parallel results...")
        final_result = self._merge_results(code_analysis, comprehensive_feedback, assignment_info)
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        final_result['grading_stats'] = self.grading_stats.copy()
        final_result['grading_method'] = 'ollama_parallel_system'
        
        print(f"🎉 Ollama parallel grading complete!")
        print(f"⚡ Parallel time: {parallel_time:.1f}s")
        print(f"📊 Efficiency gain: {self.grading_stats['parallel_efficiency']:.1f}x")
        print(f"🕒 Total time: {total_time:.1f}s")
        
        return final_result
    
    def _execute_code_analysis(self, student_code: str, solution_code: str,
                              assignment_info: Dict, rubric_elements: Dict) -> Dict[str, Any]:
        """Execute code analysis task using Qwen 3.0 Coder"""
        start_time = time.time()
        
        print(f"🔧 [CODE] Starting analysis with {self.code_model}...")
        
        prompt = self._build_code_analysis_prompt(
            student_code, solution_code, assignment_info, rubric_elements
        )
        
        response = self.generate_with_ollama(self.code_model, prompt, max_tokens=1500)
        
        analysis_time = time.time() - start_time
        self.grading_stats['code_analysis_time'] = analysis_time
        
        print(f"✅ [CODE] Analysis complete ({analysis_time:.1f}s)")
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 0}
        
        return self._parse_code_analysis_response(response)
    
    def _execute_feedback_generation(self, student_code: str, student_markdown: str,
                                   assignment_info: Dict, rubric_elements: Dict) -> Dict[str, Any]:
        """Execute feedback generation task using Gemma 3.0"""
        start_time = time.time()
        
        print(f"📝 [FEEDBACK] Starting generation with {self.feedback_model}...")
        
        prompt = self._build_feedback_prompt(
            student_code, student_markdown, assignment_info, rubric_elements
        )
        
        response = self.generate_with_ollama(self.feedback_model, prompt, max_tokens=2000)
        
        feedback_time = time.time() - start_time
        self.grading_stats['feedback_generation_time'] = feedback_time
        
        print(f"✅ [FEEDBACK] Generation complete ({feedback_time:.1f}s)")
        
        if not response:
            return {"error": "Feedback generation failed", "overall_score": 0}
        
        return self._parse_feedback_response(response)
    
    def _build_code_analysis_prompt(self, student_code: str, solution_code: str,
                                   assignment_info: Dict, rubric_elements: Dict) -> str:
        """Build prompt for code analysis using Qwen 3.0 Coder"""
        
        prompt = f"""You are an expert R code reviewer specializing in data science assignments. Analyze the student's code with technical precision.

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

Provide a detailed technical analysis in JSON format:

```json
{{
    "technical_score": <0-100>,
    "syntax_correctness": <0-100>,
    "logic_correctness": <0-100>,
    "code_efficiency": <0-100>,
    "best_practices": <0-100>,
    "technical_issues": [
        "List specific technical problems found"
    ],
    "technical_strengths": [
        "List what the student did well technically"
    ],
    "code_suggestions": [
        "Specific actionable code improvement suggestions"
    ],
    "r_specific_feedback": [
        "R language specific observations and recommendations"
    ]
}}
```

Focus on R syntax accuracy, data manipulation correctness, statistical methods, and coding best practices."""
        
        return prompt
    
    def _build_feedback_prompt(self, student_code: str, student_markdown: str,
                              assignment_info: Dict, rubric_elements: Dict) -> str:
        """Build prompt for comprehensive feedback using Gemma 3.0"""
        
        prompt = f"""You are an experienced data science instructor providing comprehensive educational feedback.

ASSIGNMENT: {assignment_info.get('title', 'Data Analysis Assignment')}

STUDENT'S WRITTEN RESPONSES:
{student_markdown}

STUDENT'S CODE SUMMARY:
{student_code[:500]}...

RUBRIC ELEMENTS:
{json.dumps(rubric_elements, indent=2)}

Provide comprehensive educational feedback in JSON format:

```json
{{
    "overall_score": <0-100>,
    "conceptual_understanding": <0-100>,
    "communication_clarity": <0-100>,
    "data_interpretation": <0-100>,
    "methodology_appropriateness": <0-100>,
    "detailed_feedback": {{
        "strengths": [
            "What the student demonstrated well"
        ],
        "areas_for_improvement": [
            "Specific areas needing development"
        ],
        "learning_suggestions": [
            "Educational recommendations for improvement"
        ]
    }},
    "rubric_scores": {{
        "understanding": <score>,
        "application": <score>,
        "communication": <score>
    }},
    "instructor_comments": "Detailed constructive feedback paragraph for the student focusing on learning outcomes"
}}
```

Provide encouraging, constructive feedback that promotes learning and improvement."""
        
        return prompt
    
    def _parse_code_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse code analysis response from Qwen 3.0 Coder"""
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
                # Fallback: create structured response
                return self._create_fallback_code_analysis(response)
        except Exception as e:
            print(f"⚠️ Code analysis parsing failed: {e}")
            return self._create_fallback_code_analysis(response)
    
    def _parse_feedback_response(self, response: str) -> Dict[str, Any]:
        """Parse feedback response from Gemma 3.0"""
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
                # Fallback: create structured response
                return self._create_fallback_feedback(response)
        except Exception as e:
            print(f"⚠️ Feedback parsing failed: {e}")
            return self._create_fallback_feedback(response)
    
    def _create_fallback_code_analysis(self, response: str) -> Dict[str, Any]:
        """Create fallback code analysis structure"""
        return {
            "technical_score": 75,
            "syntax_correctness": 75,
            "logic_correctness": 75,
            "code_efficiency": 75,
            "best_practices": 75,
            "technical_issues": ["Analysis completed but JSON parsing failed"],
            "technical_strengths": ["Code was analyzed by Qwen 3.0 Coder"],
            "code_suggestions": ["Review the detailed response below"],
            "r_specific_feedback": [response[:200] + "..." if len(response) > 200 else response]
        }
    
    def _create_fallback_feedback(self, response: str) -> Dict[str, Any]:
        """Create fallback feedback structure"""
        return {
            "overall_score": 80,
            "conceptual_understanding": 80,
            "communication_clarity": 80,
            "data_interpretation": 80,
            "methodology_appropriateness": 80,
            "detailed_feedback": {
                "strengths": ["Feedback generated by Gemma 3.0"],
                "areas_for_improvement": ["Review detailed response"],
                "learning_suggestions": ["See instructor comments"]
            },
            "rubric_scores": {
                "understanding": 80,
                "application": 80,
                "communication": 80
            },
            "instructor_comments": response[:500] + "..." if len(response) > 500 else response
        }
    
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
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "parallel_processing": True,
            "models_used": {
                "code_analyzer": self.code_model,
                "feedback_generator": self.feedback_model
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "ollama_connected": self.check_ollama_connection(),
            "models_ready": self.models_ready,
            "code_model": self.code_model,
            "feedback_model": self.feedback_model,
            "parallel_processing": True
        }
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)

# Convenience function
def create_ollama_grader(code_model: str = None, feedback_model: str = None) -> OllamaTwoModelGrader:
    """Create an Ollama two-model grader instance"""
    return OllamaTwoModelGrader(code_model, feedback_model)