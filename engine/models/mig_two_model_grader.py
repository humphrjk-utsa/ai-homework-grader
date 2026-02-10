#!/usr/bin/env python3
"""
MIG Two-Model Grading System for RTX Pro 6000
Enables true parallel execution of code analysis and feedback models
"""

import json
import time
import asyncio
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from mig_llamacpp_client import MIGLlamaCppClient, get_mig_pool
from mig_manager import MIGManager

@dataclass
class GradingTask:
    """Represents a grading task"""
    task_id: str
    task_type: str  # 'code_analysis' or 'feedback_generation'
    prompt: str
    max_tokens: int
    student_code: str
    assignment_info: Dict[str, Any]

class MIGTwoModelGrader:
    """MIG-enabled two-model grader for true parallel processing"""
    
    def __init__(self, 
                 code_model_path: str = None,
                 feedback_model_path: str = None):
        """Initialize MIG two-model grader
        
        Args:
            code_model_path: Path to GGUF model for code analysis
            feedback_model_path: Path to GGUF model for feedback generation
        """
        
        print("🚀 Initializing MIG Two-Model Grading System...")
        
        # Get MIG pool
        self.mig_pool = get_mig_pool()
        
        # Initialize MIG
        if not self.mig_pool.initialize():
            raise RuntimeError("Failed to initialize MIG. Run 'sudo python mig_manager.py --setup' first.")
        
        # Create MIG-aware clients
        self.code_analyzer = None
        self.feedback_generator = None
        
        # Model paths
        self.code_model_path = code_model_path
        self.feedback_model_path = feedback_model_path
        
        # Performance tracking
        self.grading_stats = {
            'code_analysis_time': 0,
            'feedback_generation_time': 0,
            'parallel_time': 0,
            'total_time': 0,
            'parallel_efficiency': 0.0,
            'models_used': {}
        }
        
        # Parallel processing
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.models_preloaded = False
    
    def _setup_models(self):
        """Setup MIG-enabled models"""
        if self.code_analyzer and self.feedback_generator:
            return True
        
        print("🔧 Setting up MIG models...")
        
        # Auto-select models if not specified
        if not self.code_model_path:
            self.code_model_path = self._find_best_code_model()
        
        if not self.feedback_model_path:
            self.feedback_model_path = self._find_best_feedback_model()
        
        if not self.code_model_path or not self.feedback_model_path:
            print("❌ Could not find suitable models")
            return False
        
        # Create MIG clients
        self.code_analyzer = self.mig_pool.create_client(
            model_path=self.code_model_path,
            model_id="code_analyzer"
        )
        
        self.feedback_generator = self.mig_pool.create_client(
            model_path=self.feedback_model_path,
            model_id="feedback_generator"
        )
        
        if not self.code_analyzer or not self.feedback_generator:
            print("❌ Failed to create MIG clients")
            return False
        
        # Update stats
        self.grading_stats['models_used'] = {
            'code_analyzer': self.code_analyzer.model_name,
            'feedback_generator': self.feedback_generator.model_name
        }
        
        print("✅ MIG models setup complete")
        return True
    
    def _find_best_code_model(self) -> Optional[str]:
        """Find best available code analysis model"""
        from pc_llamacpp_client import PCLlamaCppClient
        
        client = PCLlamaCppClient()
        models = client.list_available_models()
        
        # Prefer Qwen2.5-Coder models
        code_patterns = ["qwen2.5-coder", "qwen-coder", "codellama", "code"]
        
        for pattern in code_patterns:
            for model in models:
                if pattern in model["name"].lower():
                    print(f"🔍 Selected code model: {model['name']}")
                    return model["path"]
        
        # Fallback to any available model
        if models:
            print(f"⚠️ Using fallback code model: {models[0]['name']}")
            return models[0]["path"]
        
        return None
    
    def _find_best_feedback_model(self) -> Optional[str]:
        """Find best available feedback generation model"""
        from pc_llamacpp_client import PCLlamaCppClient
        
        client = PCLlamaCppClient()
        models = client.list_available_models()
        
        # Prefer general language models
        feedback_patterns = ["llama-3.1", "llama-3", "gemma-2", "mistral"]
        
        for pattern in feedback_patterns:
            for model in models:
                if pattern in model["name"].lower():
                    print(f"🔍 Selected feedback model: {model['name']}")
                    return model["path"]
        
        # Fallback to largest available model
        if models:
            largest = max(models, key=lambda x: x["size_gb"])
            print(f"⚠️ Using fallback feedback model: {largest['name']}")
            return largest["path"]
        
        return None
    
    def preload_models(self):
        """Preload both models in parallel"""
        if self.models_preloaded:
            return True
        
        if not self._setup_models():
            return False
        
        print("🚀 Preloading models in parallel on MIG instances...")
        start_time = time.time()
        
        # Preload both models simultaneously
        def preload_code_model():
            return self.code_analyzer.preload_model()
        
        def preload_feedback_model():
            return self.feedback_generator.preload_model()
        
        # Execute in parallel
        future_code = self.executor.submit(preload_code_model)
        future_feedback = self.executor.submit(preload_feedback_model)
        
        # Wait for both to complete
        code_success = future_code.result()
        feedback_success = future_feedback.result()
        
        preload_time = time.time() - start_time
        
        if code_success and feedback_success:
            self.models_preloaded = True
            print(f"✅ Both models preloaded in {preload_time:.1f}s (parallel)")
            return True
        else:
            print(f"❌ Model preloading failed")
            return False
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str, 
                        solution_code: str,
                        assignment_info: Dict,
                        rubric_elements: Dict) -> Dict[str, Any]:
        """
        Grade submission using MIG parallel processing
        """
        
        start_time = time.time()
        
        print("🚀 Starting MIG Parallel Grading System...")
        
        # Ensure models are loaded
        if not self.preload_models():
            raise RuntimeError("Failed to preload models")
        
        # Create grading tasks
        code_task = GradingTask(
            task_id="code_analysis",
            task_type="code_analysis",
            prompt=self._build_code_analysis_prompt(
                student_code, solution_code, assignment_info, rubric_elements
            ),
            max_tokens=1500,
            student_code=student_code,
            assignment_info=assignment_info
        )
        
        feedback_task = GradingTask(
            task_id="feedback_generation", 
            task_type="feedback_generation",
            prompt=self._build_feedback_prompt(
                student_code, student_markdown, {}, assignment_info, rubric_elements
            ),
            max_tokens=2000,
            student_code=student_code,
            assignment_info=assignment_info
        )
        
        # Execute tasks in parallel
        print("⚡ Executing code analysis and feedback generation in parallel...")
        parallel_start = time.time()
        
        # Submit both tasks simultaneously
        future_code = self.executor.submit(self._execute_code_analysis, code_task)
        future_feedback = self.executor.submit(self._execute_feedback_generation, feedback_task)
        
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
        final_result['grading_method'] = 'mig_parallel_system'
        
        print(f"🎉 MIG parallel grading complete!")
        print(f"⚡ Parallel time: {parallel_time:.1f}s")
        print(f"📊 Efficiency gain: {self.grading_stats['parallel_efficiency']:.1f}x")
        print(f"🕒 Total time: {total_time:.1f}s")
        
        return final_result
    
    def _execute_code_analysis(self, task: GradingTask) -> Dict[str, Any]:
        """Execute code analysis task"""
        start_time = time.time()
        
        print(f"🔧 [{task.task_id}] Starting code analysis...")
        
        response = self.code_analyzer.generate_response(
            task.prompt, 
            max_tokens=task.max_tokens,
            show_progress=False  # Disable progress for parallel execution
        )
        
        analysis_time = time.time() - start_time
        self.grading_stats['code_analysis_time'] = analysis_time
        
        print(f"✅ [{task.task_id}] Code analysis complete ({analysis_time:.1f}s)")
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 0}
        
        return self._parse_code_analysis_response(response)
    
    def _execute_feedback_generation(self, task: GradingTask) -> Dict[str, Any]:
        """Execute feedback generation task"""
        start_time = time.time()
        
        print(f"📝 [{task.task_id}] Starting feedback generation...")
        
        response = self.feedback_generator.generate_response(
            task.prompt,
            max_tokens=task.max_tokens,
            show_progress=False  # Disable progress for parallel execution
        )
        
        feedback_time = time.time() - start_time
        self.grading_stats['feedback_generation_time'] = feedback_time
        
        print(f"✅ [{task.task_id}] Feedback generation complete ({feedback_time:.1f}s)")
        
        if not response:
            return {"error": "Feedback generation failed", "overall_score": 0}
        
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
        """Parse code analysis response"""
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
    
    def _parse_feedback_response(self, response: str) -> Dict[str, Any]:
        """Parse feedback response"""
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
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "parallel_processing": True
        }
    
    def get_mig_status(self) -> Dict[str, Any]:
        """Get MIG system status"""
        pool_status = self.mig_pool.get_pool_status()
        
        return {
            "mig_initialized": pool_status["initialized"],
            "total_instances": pool_status["total_instances"],
            "available_instances": pool_status["available_instances"],
            "models_loaded": self.models_preloaded,
            "code_analyzer": self.code_analyzer.get_model_info() if self.code_analyzer else None,
            "feedback_generator": self.feedback_generator.get_model_info() if self.feedback_generator else None
        }
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)

# Convenience function
def create_mig_grader(code_model_path: str = None, feedback_model_path: str = None) -> MIGTwoModelGrader:
    """Create a MIG two-model grader instance"""
    return MIGTwoModelGrader(code_model_path, feedback_model_path)