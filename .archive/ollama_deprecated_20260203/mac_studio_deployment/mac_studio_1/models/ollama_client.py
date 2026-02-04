#!/usr/bin/env python3
"""
Ollama Client for Homework Grader
Uses existing Ollama models for parallel processing
"""

import requests
import json
import time
import streamlit as st
from typing import Optional, Dict, Any, List

class OllamaClient:
    """Client for interacting with Ollama models"""
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Initialize Ollama client
        
        Args:
            model_name: Name of the Ollama model (e.g., 'qwen3:30b')
            base_url: Ollama server URL
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"
        self.model_loaded_in_memory = False
        self.last_response_time = None
        
        print(f"🤖 Initializing Ollama client with model: {model_name}")
        
        # Check if model is available
        self._check_model_availability()
    
    def _check_model_availability(self):
        """Check if the model is available in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                
                if self.model_name in available_models:
                    print(f"✅ Model {self.model_name} is available")
                    self.model_loaded_in_memory = True
                else:
                    print(f"❌ Model {self.model_name} not found in Ollama")
                    print(f"Available models: {available_models}")
            else:
                print(f"❌ Failed to connect to Ollama: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, show_progress: bool = False) -> Optional[str]:
        """Generate response using Ollama
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            show_progress: Show progress indicator
            
        Returns:
            Generated response or None if failed
        """
        if not self.model_loaded_in_memory:
            print(f"❌ Model {self.model_name} not available")
            return None
        
        try:
            start_time = time.time()
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text(f"🚀 Generating response with {self.model_name}...")
            
            # Prepare request
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            # Send request
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "")
            
            end_time = time.time()
            self.last_response_time = end_time - start_time
            
            if show_progress:
                progress_bar.progress(1.0)
                status_text.text(f"✅ Response generated in {self.last_response_time:.1f}s")
            
            return generated_text
            
        except Exception as e:
            if show_progress:
                st.error(f"❌ Ollama generation failed: {e}")
            else:
                print(f"❌ Ollama generation failed: {e}")
            return None
    
    def preload_model(self) -> bool:
        """Preload model (for Ollama, just check availability)"""
        return self.model_loaded_in_memory
    
    def check_model_memory_status(self) -> bool:
        """Check if model is loaded in memory"""
        return self.model_loaded_in_memory
    
    def _check_model_memory_status(self) -> bool:
        """Check if model is loaded in memory (internal method)"""
        return self.model_loaded_in_memory
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "loaded": self.model_loaded_in_memory,
            "backend": "Ollama",
            "last_response_time": self.last_response_time,
            "base_url": self.base_url
        }

class OllamaTwoModelGrader:
    """Two-model grader using Ollama models"""
    
    def __init__(self, 
                 code_model: str = "qwen3:30b",
                 feedback_model: str = "gemma3:27b-it-q8_0"):
        """Initialize Ollama two-model grader
        
        Args:
            code_model: Ollama model for code analysis
            feedback_model: Ollama model for feedback generation
        """
        
        print("🚀 Initializing Ollama Two-Model Grading System...")
        
        # Initialize clients
        self.code_analyzer = OllamaClient(code_model)
        self.feedback_generator = OllamaClient(feedback_model)
        
        self.grading_stats = {
            'code_analysis_time': 0,
            'feedback_generation_time': 0,
            'total_time': 0,
            'models_used': {
                'code_analyzer': code_model,
                'feedback_generator': feedback_model
            }
        }
        
        # Check if both models are available
        if not (self.code_analyzer.model_loaded_in_memory and 
                self.feedback_generator.model_loaded_in_memory):
            raise RuntimeError("One or both models are not available in Ollama")
        
        print(f"✅ Code Analyzer: {code_model}")
        print(f"✅ Feedback Generator: {feedback_model}")
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str, 
                        solution_code: str,
                        assignment_info: Dict,
                        rubric_elements: Dict) -> Dict[str, Any]:
        """Grade submission using Ollama models"""
        
        start_time = time.time()
        
        print("🚀 Starting Ollama Two-Model Grading...")
        
        # Phase 1: Code Analysis
        print("🔄 Phase 1: Code Analysis with Qwen 3.0...")
        code_analysis_start = time.time()
        
        code_analysis = self._analyze_code(
            student_code, solution_code, assignment_info, rubric_elements
        )
        
        self.grading_stats['code_analysis_time'] = time.time() - code_analysis_start
        
        # Phase 2: Feedback Generation
        print("🔄 Phase 2: Feedback Generation with Gemma 3.0...")
        feedback_start = time.time()
        
        comprehensive_feedback = self._generate_feedback(
            student_code, student_markdown, code_analysis, assignment_info, rubric_elements
        )
        
        self.grading_stats['feedback_generation_time'] = time.time() - feedback_start
        
        # Phase 3: Merge Results
        print("🔄 Phase 3: Merging Results...")
        
        final_result = self._merge_results(code_analysis, comprehensive_feedback, assignment_info)
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        final_result['grading_stats'] = self.grading_stats.copy()
        final_result['grading_method'] = 'ollama_two_model_system'
        
        print(f"🎉 Ollama grading complete! Total time: {total_time:.1f}s")
        
        return final_result
    
    def _analyze_code(self, student_code: str, solution_code: str, 
                     assignment_info: Dict, rubric_elements: Dict) -> Dict[str, Any]:
        """Analyze code using Qwen 3.0"""
        
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
        
        response = self.code_analyzer.generate_response(prompt, max_tokens=1500, show_progress=True)
        
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
                return self._parse_fallback_response(response, "code")
        except Exception as e:
            print(f"⚠️ Code analysis parsing failed: {e}")
            return self._parse_fallback_response(response, "code")
    
    def _generate_feedback(self, student_code: str, student_markdown: str,
                          code_analysis: Dict, assignment_info: Dict, 
                          rubric_elements: Dict) -> Dict[str, Any]:
        """Generate feedback using Gemma 3.0"""
        
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
        
        response = self.feedback_generator.generate_response(prompt, max_tokens=2000, show_progress=True)
        
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
                return self._parse_fallback_response(response, "feedback")
        except Exception as e:
            print(f"⚠️ Feedback parsing failed: {e}")
            return self._parse_fallback_response(response, "feedback")
    
    def _parse_fallback_response(self, response: str, response_type: str) -> Dict[str, Any]:
        """Fallback response parser"""
        if response_type == "code":
            return {
                "technical_score": 75,
                "syntax_correctness": 75,
                "logic_correctness": 75,
                "code_efficiency": 75,
                "best_practices": 75,
                "technical_issues": ["Could not parse detailed analysis"],
                "technical_strengths": ["Response received"],
                "code_suggestions": ["Review the generated feedback"]
            }
        else:
            return {
                "overall_score": 80,
                "conceptual_understanding": 80,
                "communication_clarity": 80,
                "data_interpretation": 80,
                "methodology_appropriateness": 80,
                "detailed_feedback": {
                    "strengths": ["Response generated"],
                    "areas_for_improvement": ["Could not parse detailed feedback"],
                    "suggestions": ["Review the raw response"]
                },
                "rubric_scores": {},
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
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "code_analyzer": self.code_analyzer.get_model_info(),
            "feedback_generator": self.feedback_generator.get_model_info()
        }

def get_available_ollama_models() -> List[Dict[str, Any]]:
    """Get available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [
                {
                    "name": model["name"],
                    "size": model.get("size", 0),
                    "modified": model.get("modified_at", ""),
                    "backend": "Ollama"
                }
                for model in models
            ]
    except Exception as e:
        print(f"❌ Error getting Ollama models: {e}")
    
    return []

# Convenience function
def create_ollama_grader(code_model: str = "qwen3:30b", 
                        feedback_model: str = "gemma3:27b-it-q8_0") -> OllamaTwoModelGrader:
    """Create an Ollama two-model grader instance"""
    return OllamaTwoModelGrader(code_model, feedback_model)