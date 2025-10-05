#!/usr/bin/env python3
"""
Business Analytics Grading System
Adjusted for first-year business students learning R
More encouraging and appropriate for introductory level
"""

import json
import time
import requests
import concurrent.futures
import os
from typing import Dict, List, Any, Optional
from prompt_manager import PromptManager
from notebook_validation import NotebookValidator
from score_validator import validate_and_adjust_scores

class BusinessAnalyticsGrader:
    """Grader optimized for business analytics students (first-year level)"""
    
    def __init__(self, 
                 code_model: str = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
                 feedback_model: str = "gemma3:27b-it-q8_0",
                 ollama_url: str = "http://localhost:11434"):
        """Initialize business analytics grader"""
        
        self.code_model = code_model
        self.feedback_model = feedback_model
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        
        # Initialize prompt manager and validator
        self.prompt_manager = PromptManager()
        self.validator = NotebookValidator()
        
        # Check for distributed MLX system
        self.use_distributed_mlx = False
        self.distributed_client = None
        
        if os.path.exists('distributed_config.json'):
            try:
                from models.distributed_mlx_client import DistributedMLXClient
                import json
                
                with open('distributed_config.json', 'r') as f:
                    config = json.load(f)
                
                qwen_url = config['urls']['qwen_server']
                gemma_url = config['urls']['gemma_server']
                
                self.distributed_client = DistributedMLXClient(qwen_url, gemma_url)
                
                # Test if both servers are available
                status = self.distributed_client.get_system_status()
                if status['distributed_ready']:
                    self.use_distributed_mlx = True
                    print(f"🖥️ Using Distributed MLX System!")
                    print(f"📡 Qwen Server: {qwen_url}")
                    print(f"📡 GPT-OSS Server: {gemma_url}")
                else:
                    print(f"⚠️ Distributed MLX not ready, falling back to Ollama")
            except Exception as e:
                print(f"⚠️ Distributed MLX setup failed: {e}, using Ollama")
        
        print(f"🎓 Initializing Business Analytics Grading System...")
        print(f"📊 Optimized for first-year business students")
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
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def check_models_available(self) -> bool:
        """Check if required models are available (MLX distributed or Ollama)"""
        
        # If using distributed MLX, check that system
        if self.use_distributed_mlx and self.distributed_client:
            try:
                status = self.distributed_client.get_system_status()
                if status['distributed_ready']:
                    self.models_ready = True
                    return True
                else:
                    return False
            except Exception as e:
                print(f"❌ Distributed MLX check failed: {e}")
                return False
        
        # Otherwise check Ollama
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                code_available = self.code_model in available_models
                feedback_available = self.feedback_model in available_models
                
                if code_available and feedback_available:
                    self.models_ready = True
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
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
                    "temperature": 0.2,  # Lower temperature for more consistent grading
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return None
                
        except Exception as e:
            return None
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str,
                        template_code: str = "",
                        solution_code: str = "",
                        assignment_info: Dict = None,
                        rubric_elements: Dict = None,
                        notebook_path: str = None,
                        preprocessing_info: Dict = None) -> Dict[str, Any]:
        """Grade submission with business analytics context"""
        
        start_time = time.time()
        
        print("🎓 Starting Business Analytics Grading...")
        
        # Track preprocessing if provided
        if preprocessing_info:
            print(f"📋 Preprocessing applied: {len(preprocessing_info.get('fixes_applied', []))} fixes")
        
        # Validate notebook first if path provided
        validation_results = None
        validation_penalty = 0
        validation_feedback = ""
        
        if notebook_path:
            print("🔍 Validating notebook submission...")
            validation_results = self.validator.validate_notebook(notebook_path)
            validation_penalty = validation_results['total_penalty_percent']
            validation_feedback = self.validator.generate_validation_feedback(validation_results)
            
            if validation_penalty > 0:
                print(f"⚠️ Validation issues found: {validation_penalty}% penalty")
                for issue in validation_results['issues']:
                    print(f"   - {issue}")
            
            # Add output verification to prevent AI hallucination
            print("🔍 Verifying outputs exist...")
            from output_verifier import OutputVerifier
            output_verifier = OutputVerifier(notebook_path)
            with_outputs, total_cells = output_verifier.count_cells_with_outputs()
            completion_pct = output_verifier.get_completion_percentage()
            print(f"📊 Output Check: {with_outputs}/{total_cells} cells have outputs ({completion_pct:.0f}%)")
        
        # Check prerequisites
        if self.use_distributed_mlx:
            if not self.check_models_available():
                raise RuntimeError("Distributed MLX system not available")
        else:
            if not self.check_ollama_connection():
                raise RuntimeError("Ollama server not accessible")
            
            if not self.check_models_available():
                raise RuntimeError("Required models not available in Ollama")
        
        # Execute tasks in parallel
        print("⚡ Executing parallel grading for business context...")
        parallel_start = time.time()
        
        if self.use_distributed_mlx:
            # Use distributed MLX system
            print("🖥️ Using Distributed MLX System for parallel processing...")
            
            # Prepare prompts using prompt manager (combines general + assignment-specific)
            assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
            
            code_prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "code_analysis",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                template_code=template_code if template_code else "# No template provided",
                student_code=student_code,
                solution_code=solution_code
            )
            
            feedback_prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "feedback",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                student_markdown=student_markdown,
                student_code_summary=student_code[:800]
            )
            
            # Execute in parallel across Mac Studios
            result = self.distributed_client.generate_parallel_sync(code_prompt, feedback_prompt)
            
            if result.get('code_analysis') and result.get('feedback'):
                code_analysis = self._parse_code_analysis_response(result['code_analysis'])
                comprehensive_feedback = self._parse_feedback_response(result['feedback'])
                
                # Update timing stats
                self.grading_stats['code_analysis_time'] = result.get('qwen_time', 0)
                self.grading_stats['feedback_generation_time'] = result.get('gemma_time', 0)
                
                # Add performance metrics
                performance_metrics = result.get('performance_metrics', {})
                self.grading_stats['performance_diagnostics'] = performance_metrics
                
                # Print performance diagnostics
                qwen_perf = performance_metrics.get('qwen', {})
                gemma_perf = performance_metrics.get('gemma', {})
                
                print(f"📊 Performance Diagnostics:")
                print(f"   🔧 Qwen (Code): {qwen_perf.get('output_tokens', 0)} tokens @ {qwen_perf.get('tokens_per_second', 0):.1f} tok/s")
                print(f"   📝 GPT-OSS (Feedback): {gemma_perf.get('output_tokens', 0)} tokens @ {gemma_perf.get('tokens_per_second', 0):.1f} tok/s")
                print(f"   🚀 Combined Throughput: {performance_metrics.get('combined_tokens_per_second', 0):.1f} tok/s")
            else:
                raise RuntimeError(f"Distributed MLX generation failed: {result.get('error', 'Unknown error')}")
        else:
            # Use Ollama system
            # Submit both tasks simultaneously
            future_code = self.executor.submit(
                self._execute_business_code_analysis, 
                student_code, template_code, solution_code, assignment_info, rubric_elements
            )
            
            future_feedback = self.executor.submit(
                self._execute_business_feedback_generation,
                student_code, student_markdown, assignment_info, rubric_elements
            )
            
            # Wait for both results
            code_analysis = future_code.result()
            comprehensive_feedback = future_feedback.result()
        
        parallel_time = time.time() - parallel_start
        self.grading_stats['parallel_time'] = parallel_time
        
        # Calculate efficiency
        sequential_time = (self.grading_stats['code_analysis_time'] + 
                          self.grading_stats['feedback_generation_time'])
        
        if sequential_time > 0:
            self.grading_stats['parallel_efficiency'] = sequential_time / parallel_time
        
        # Validate and adjust scores if AI was too generous
        print("="*80)
        print("🔍 ABOUT TO CALL VALIDATOR")
        print("="*80)
        print(f"🔍 Before validation: technical_score={code_analysis.get('technical_score', 0)}, overall_score={comprehensive_feedback.get('overall_score', 0)}")
        code_analysis, comprehensive_feedback = validate_and_adjust_scores(
            code_analysis, comprehensive_feedback, student_code, template_code
        )
        print(f"🔍 After validation: technical_score={code_analysis.get('technical_score', 0)}, overall_score={comprehensive_feedback.get('overall_score', 0)}")
        
        # Merge results with business context and apply validation penalty
        final_result = self._merge_business_results(code_analysis, comprehensive_feedback, assignment_info, validation_penalty, preprocessing_info)
        
        # FIX AI HALLUCINATION: Verify outputs exist and override if AI is wrong
        if notebook_path:
            print("🔧 Fixing AI hallucinations with output verification...")
            from output_verifier import verify_and_fix_grading
            final_result = verify_and_fix_grading(notebook_path, final_result)
        
        # Add validation info to result
        if validation_results:
            final_result['validation'] = {
                'penalty_percent': validation_penalty,
                'issues': validation_results.get('issues', []),
                'warnings': validation_results.get('warnings', []),
                'feedback': validation_feedback
            }
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        final_result['grading_stats'] = self.grading_stats.copy()
        final_result['grading_method'] = 'business_analytics_system'
        
        # Add preprocessing info if provided
        if preprocessing_info:
            final_result['preprocessing'] = preprocessing_info
        
        # Add detailed performance diagnostics if using distributed MLX
        if self.use_distributed_mlx and self.distributed_client:
            final_result['performance_diagnostics'] = self.distributed_client.get_performance_diagnostics()
        
        print(f"🎉 Business analytics grading complete!")
        print(f"⚡ Parallel time: {parallel_time:.1f}s")
        print(f"📊 Efficiency gain: {self.grading_stats['parallel_efficiency']:.1f}x")
        print(f"🕒 Total time: {total_time:.1f}s")
        
        return final_result
    
    def _execute_business_code_analysis(self, student_code: str, template_code: str, solution_code: str,
                                       assignment_info: Dict, rubric_elements: Dict) -> Dict[str, Any]:
        """Execute code analysis with business analytics context"""
        start_time = time.time()
        
        print(f"🔧 [CODE] Analyzing with business context...")
        
        # Use prompt manager for consistency (single source of truth)
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        prompt = self.prompt_manager.get_combined_prompt(
            assignment_name,
            "code_analysis",
            assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
            template_code=template_code if template_code else "# No template provided",
            student_code=student_code,
            solution_code=solution_code
        )
        
        response = self.generate_with_ollama(self.code_model, prompt, max_tokens=1500)
        
        analysis_time = time.time() - start_time
        self.grading_stats['code_analysis_time'] = analysis_time
        
        print(f"✅ [CODE] Business analysis complete ({analysis_time:.1f}s)")
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 85}  # Default higher for business
        
        return self._parse_business_code_response(response)
    
    def _execute_business_feedback_generation(self, student_code: str, student_markdown: str,
                                            assignment_info: Dict, rubric_elements: Dict) -> Dict[str, Any]:
        """Execute feedback generation with business context"""
        start_time = time.time()
        
        print(f"📝 [FEEDBACK] Generating business-focused feedback...")
        
        # Use prompt manager for consistency (single source of truth)
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        prompt = self.prompt_manager.get_combined_prompt(
            assignment_name,
            "feedback",
            assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
            student_markdown=student_markdown,
            student_code_summary=student_code[:800]
        )
        
        response = self.generate_with_ollama(self.feedback_model, prompt, max_tokens=2000)
        
        feedback_time = time.time() - start_time
        self.grading_stats['feedback_generation_time'] = feedback_time
        
        print(f"✅ [FEEDBACK] Business feedback complete ({feedback_time:.1f}s)")
        
        if not response:
            return {"error": "Feedback generation failed", "overall_score": 85}  # Default higher for business
        
        return self._parse_business_feedback_response(response)
    
    # NOTE: Prompts are now managed by PromptManager (single source of truth)
    # See prompt_templates/general_code_analysis_prompt.txt and general_feedback_prompt.txt
    # These can be customized per assignment in the Prompt Manager UI
    
    def _parse_business_code_response(self, response: str) -> Dict[str, Any]:
        """Parse business-focused code analysis response"""
        try:
            # Try to parse JSON response
            if "```json" in response:
                json_part = response.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_part)
                return result
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_part = response[start:end]
                result = json.loads(json_part)
                return result
            else:
                return self._create_default_code_analysis(response)
        except Exception as e:
            return self._create_default_code_analysis(response)
    
    def _parse_business_feedback_response(self, response: str) -> Dict[str, Any]:
        """Parse business-focused feedback response"""
        try:
            # Try to parse JSON response
            if "```json" in response:
                json_part = response.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_part)
                return result
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_part = response[start:end]
                result = json.loads(json_part)
                return result
            else:
                return self._create_default_feedback(response)
        except Exception as e:
            return self._create_default_feedback(response)
    
    def _create_default_code_analysis(self, response: str) -> Dict[str, Any]:
        """Create default code analysis when parsing fails"""
        return {
            "technical_score": 50,
            "syntax_correctness": 50,
            "logic_correctness": 50,
            "business_relevance": 50,
            "effort_and_completion": 50,
            "code_strengths": [
                "Unable to parse AI response - manual review required"
            ],
            "code_suggestions": [
                "Code analysis could not be completed automatically",
                "Please review submission manually"
            ],
            "technical_observations": [
                "Automated grading encountered an error",
                "Manual review recommended"
            ]
        }
    
    def _create_default_feedback(self, response: str) -> Dict[str, Any]:
        """Create default feedback when parsing fails"""
        return {
            "overall_score": 50,
            "business_understanding": 50,
            "communication_clarity": 50,
            "data_interpretation": 50,
            "methodology_appropriateness": 50,
            "reflection_quality": 50,
            "detailed_feedback": {
                "reflection_assessment": [
                    "Unable to parse AI response - manual review required"
                ],
                "analytical_strengths": [
                    "Automated feedback generation encountered an error"
                ],
                "business_application": [
                    "Manual review recommended"
                ],
                "learning_demonstration": [
                    "Please review submission manually"
                ],
                "areas_for_development": [
                    "Automated grading could not be completed"
                ],
                "recommendations": [
                    "Manual review required"
                ]
            },
            "instructor_comments": "Automated grading could not be completed. Please review this submission manually."
        }
    
    def _create_encouraging_feedback_from_text(self, response: str) -> Dict[str, Any]:
        """Create structured feedback from plain text response without truncation"""
        # Extract key insights from the full response
        lines = response.split('\n')
        strengths = []
        suggestions = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section indicators
            if any(word in line.lower() for word in ['strength', 'good', 'excellent', 'well done']):
                current_section = 'strengths'
                strengths.append(line)
            elif any(word in line.lower() for word in ['improve', 'suggest', 'recommend', 'consider']):
                current_section = 'suggestions'
                suggestions.append(line)
            elif current_section == 'strengths':
                strengths.append(line)
            elif current_section == 'suggestions':
                suggestions.append(line)
        
        # If no clear structure found, use the full response intelligently
        if not strengths and not suggestions:
            # Split response into meaningful chunks
            response_parts = response.split('. ')
            mid_point = len(response_parts) // 2
            strengths = response_parts[:mid_point]
            suggestions = response_parts[mid_point:]
        
        return {
            "overall_score": 94,
            "business_understanding": 92,
            "communication_clarity": 90,
            "data_interpretation": 92,
            "methodology_appropriateness": 90,
            "reflection_quality": 93,
            "detailed_feedback": {
                "reflection_assessment": [
                    "Good engagement with reflection components of the assignment",
                    "Shows developing critical thinking about analytical processes"
                ],
                "analytical_strengths": strengths[:5] if strengths else [
                    "Completed all required components of the assignment",
                    "Demonstrated understanding of basic analytical concepts"
                ],
                "business_application": [
                    "Shows awareness of business context in analytical work",
                    "Appropriate framing of data analysis objectives"
                ],
                "learning_demonstration": [
                    "Evidence of learning progression in analytical skills",
                    "Developing understanding of data analysis methodology"
                ],
                "areas_for_development": suggestions[:3] if suggestions else [
                    "Continue developing analytical depth and business connections",
                    "Focus on strengthening reflection and critical thinking skills"
                ],
                "recommendations": [
                    "Continue practicing with diverse datasets and analytical scenarios",
                    "Strengthen connections between technical analysis and business implications"
                ]
            },
            "instructor_comments": response  # Use the full response without truncation
        }
    
    def _merge_business_results(self, code_analysis: Dict, feedback: Dict, 
                               assignment_info: Dict, validation_penalty: float = 0,
                               preprocessing_info: Dict = None) -> Dict[str, Any]:
        """Merge results with business-friendly weighting for 37.5 point scale"""
        
        # Extract individual component scores (no defaults - use actual scores)
        technical_score = code_analysis.get("technical_score", 50)
        business_understanding = feedback.get("business_understanding", 50)
        data_interpretation = feedback.get("data_interpretation", 50)
        communication_clarity = feedback.get("communication_clarity", 50)
        
        # Calculate points for each rubric component (37.5 total points)
        technical_points = (technical_score / 100) * 9.375      # 25% of 37.5
        business_points = (business_understanding / 100) * 11.25 # 30% of 37.5
        analysis_points = (data_interpretation / 100) * 9.375   # 25% of 37.5
        communication_points = (communication_clarity / 100) * 7.5 # 20% of 37.5
        
        # Calculate actual total from components
        final_score_37_5 = technical_points + business_points + analysis_points + communication_points
        
        # Apply validation penalty (e.g., unexecuted notebook, incomplete TODOs)
        if validation_penalty > 0:
            penalty_points = (validation_penalty / 100) * final_score_37_5
            final_score_37_5 = final_score_37_5 - penalty_points
        
        # Apply preprocessing penalty (syntax errors that were auto-fixed)
        preprocessing_penalty = 0.0
        if preprocessing_info:
            preprocessing_penalty = preprocessing_info.get('penalty_points', 0.0)
            if preprocessing_penalty > 0:
                final_score_37_5 = final_score_37_5 - preprocessing_penalty
                print(f"⚠️ Preprocessing penalty applied: -{preprocessing_penalty:.1f} points")
        
        # Cap final score at 37.5 points maximum and 0 minimum
        final_score_37_5 = max(0, min(37.5, final_score_37_5))
        
        # Calculate percentage AFTER capping
        final_percentage = (final_score_37_5 / 37.5) * 100
        
        # Ensure technical analysis always has required fields
        if not code_analysis.get('code_suggestions'):
            code_analysis['code_suggestions'] = [
                "Consider adding more detailed comments to explain your analytical approach",
                "Explore additional R functions for data exploration (glimpse(), skimr::skim())",
                "Practice with different visualization techniques to enhance data presentation"
            ]
        
        if not code_analysis.get('code_strengths'):
            code_analysis['code_strengths'] = [
                "Proper use of R packages for data analysis",
                "Good foundation in data import and exploration techniques",
                "Clear code structure and organization"
            ]
        
        if not code_analysis.get('technical_observations'):
            code_analysis['technical_observations'] = [
                "Demonstrates understanding of basic R programming concepts",
                "Shows appropriate approach to data analysis workflow",
                "Code is readable and follows good practices for introductory level"
            ]
        
        return {
            "final_score": round(final_score_37_5, 1),
            "final_score_percentage": round(final_percentage, 1),
            "max_points": 37.5,
            "component_scores": {
                "technical_points": round(technical_points, 1),
                "business_points": round(business_points, 1),
                "analysis_points": round(analysis_points, 1),
                "communication_points": round(communication_points, 1),
                "bonus_points": 0.0
            },
            "component_percentages": {
                "technical_score": technical_score,
                "business_understanding": business_understanding,
                "data_interpretation": data_interpretation,
                "communication_clarity": communication_clarity
            },
            "technical_analysis": code_analysis,
            "comprehensive_feedback": feedback,
            "assignment_info": assignment_info,
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "parallel_processing": True,
            "course_context": "First-year Business Analytics",
            "grading_philosophy": "Encouraging and supportive for beginning students"
        }

    def _prepare_code_analysis_prompt(self, student_code, solution_code, assignment_info, rubric_elements):
        """Prepare prompt for distributed MLX code analysis with deep evaluation"""
        return f"""You are a business analytics instructor evaluating first-year student R code. Analyze the ACTUAL code deeply, compare outputs to expected results, and recognize alternative valid approaches.

ASSIGNMENT: {assignment_info.get('title', 'Business Analytics Assignment')}
STUDENT LEVEL: First-year business analytics (introductory R programming)

STUDENT'S CODE:
```r
{student_code}
```

REFERENCE SOLUTION:
```r
{solution_code}
```

DEEP ANALYSIS REQUIREMENTS:

1. CODE EXECUTION & OUTPUTS:
   - Examine what the code actually produces
   - Compare student outputs to solution outputs
   - Ignore warnings that don't affect results (e.g., package loading messages, deprecation warnings)
   - Focus on whether results are correct, not just code style

2. LOGIC & APPROACH:
   - Analyze the analytical logic and reasoning
   - Recognize valid alternative approaches (different methods achieving same goal)
   - Evaluate if different approach is feasible/valid for the question
   - Don't penalize for using different but valid methods

3. ALTERNATIVE SOLUTIONS:
   - If student uses different method than solution, evaluate if it's valid
   - Suggest improvements while acknowledging their approach
   - Provide specific code examples for suggestions
   - Example: "Your use of base R is valid; alternatively, dplyr could simplify: mutate(col = ...)"

4. SPECIFIC FEEDBACK:
   - Reference actual function names, variable names from their code
   - Quote specific lines when giving suggestions
   - Provide concrete code examples for improvements

SCORING GUIDELINES:
- Complete working code with correct outputs: 95-100
- Working code with minor issues: 90-95
- Mostly working with some errors: 85-90
- Partial implementation: 75-85

OUTPUT ONLY THIS JSON (no explanations, no markdown blocks, just JSON):

{{
    "technical_score": 95,
    "syntax_correctness": 98,
    "logic_correctness": 94,
    "business_relevance": 96,
    "effort_and_completion": 97,
    "code_strengths": [
        "Successfully implements [specific function/analysis] producing correct results",
        "Uses [specific package/function] appropriately for [specific task]",
        "Code executes without errors and generates expected outputs"
    ],
    "code_suggestions": [
        "Consider using [specific alternative]: [code example]",
        "Could enhance [specific section] by: [code example]",
        "Alternative approach for [specific task]: [code example]"
    ],
    "technical_observations": [
        "Demonstrates solid understanding of [specific concept]",
        "Appropriate use of [specific technique] for business analytics",
        "Code organization supports reproducible analysis"
    ]
}}

CRITICAL: Base scores on actual code execution and outputs. Recognize valid alternatives. Provide specific, actionable suggestions with code examples."""

    def _prepare_feedback_prompt(self, student_code, student_markdown, assignment_info, rubric_elements):
        """Prepare prompt for comprehensive feedback with reflection focus"""
        return f"""You are a business analytics instructor providing feedback on first-year student work. Focus heavily on reflection questions and critical thinking. Output ONLY valid JSON.

ASSIGNMENT: {assignment_info.get('title', 'Business Analytics Assignment')}

STUDENT'S WRITTEN ANALYSIS (contains reflection questions and responses):
{student_markdown}

CODE SUMMARY:
{student_code[:800]}

EVALUATION PRIORITIES:

1. REFLECTION QUESTIONS (HIGHEST PRIORITY):
   - Look for reflection question responses (often in brackets [] or after question prompts)
   - Evaluate depth of critical thinking and self-assessment
   - Assess understanding of methodology and limitations
   - Value thoughtful consideration over perfect answers

2. OUTPUT ACCURACY:
   - Compare student's reported results to expected outcomes
   - Evaluate interpretation of results
   - Assess if conclusions match the data
   - Recognize valid alternative interpretations

3. ALTERNATIVE APPROACHES:
   - If student uses different valid method, acknowledge it
   - Don't penalize for different but correct approaches
   - Suggest alternatives as enhancements, not corrections

4. SPECIFIC FEEDBACK:
   - Reference actual content from their submission
   - Quote specific reflections or findings
   - Provide concrete examples

SCORING GUIDELINES:
- Complete work with thoughtful reflections: 92-100
- Complete work with basic reflections: 88-92
- Mostly complete with good effort: 85-88
- Partial completion: 75-85

OUTPUT ONLY THIS JSON (no text before/after, no markdown blocks):

{{
    "overall_score": 94,
    "business_understanding": 92,
    "communication_clarity": 90,
    "data_interpretation": 91,
    "methodology_appropriateness": 93,
    "reflection_quality": 95,
    "detailed_feedback": {{
        "reflection_assessment": [
            "Demonstrates thoughtful consideration of [specific reflection topic]",
            "Shows critical thinking about [specific analytical choice]",
            "Articulates understanding of [specific concept] clearly"
        ],
        "analytical_strengths": [
            "Successfully completes [specific analysis] with correct results",
            "Appropriate use of [specific method] for [specific purpose]",
            "Clear presentation of [specific findings]"
        ],
        "business_application": [
            "Effectively connects [specific analysis] to business context",
            "Demonstrates understanding of practical implications",
            "Frames analysis in terms of business objectives"
        ],
        "learning_demonstration": [
            "Shows solid grasp of [specific concept]",
            "Applies [specific technique] appropriately",
            "Demonstrates developing analytical maturity"
        ],
        "areas_for_development": [
            "Consider exploring [specific enhancement] in future work",
            "Could strengthen [specific aspect] by [specific suggestion]",
            "Opportunity to deepen analysis of [specific area]"
        ],
        "recommendations": [
            "Practice [specific skill] with varied datasets",
            "Explore [specific advanced technique] as next step",
            "Continue developing [specific competency]"
        ]
    }},
    "instructor_comments": "Your work demonstrates strong engagement with the assignment, particularly in your thoughtful reflection responses. You've successfully completed the required analyses and shown good understanding of the concepts. Your [specific strength] is particularly well done. For future work, consider [specific suggestion]. Overall, excellent progress in developing your analytical skills."
}}

CRITICAL: Output pure JSON only. Reference specific content from student work. Prioritize reflection quality. Recognize valid alternatives."""

    def _parse_code_analysis_response(self, response):
        """Parse code analysis response from distributed MLX with better error handling"""
        import re
        import json
        
        try:
            # Clean the response first
            response = response.strip()
            
            # Try multiple JSON extraction methods
            json_part = None
            
            # Method 1: Look for ```json blocks
            if "```json" in response:
                parts = response.split("```json")
                if len(parts) > 1:
                    json_part = parts[1].split("```")[0].strip()
            
            # Method 2: Look for { } blocks
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_part = response[start:end]
            
            # Method 3: Try to find JSON-like structure
            else:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_part = json_match.group()
            
            # Parse the JSON if found
            if json_part:
                # Clean common JSON issues
                json_part = json_part.replace('\n', ' ').replace('\r', '')
                json_part = re.sub(r'\s+', ' ', json_part)
                
                result = json.loads(json_part)
                
                # Ensure required fields exist
                if not isinstance(result, dict):
                    raise ValueError("Response is not a dictionary")
                
                # Ensure minimum scores for business students
                result["technical_score"] = max(result.get("technical_score", 85), 75)
                result["syntax_correctness"] = max(result.get("syntax_correctness", 90), 80)
                result["logic_correctness"] = max(result.get("logic_correctness", 85), 75)
                result["business_relevance"] = max(result.get("business_relevance", 85), 80)
                result["effort_and_completion"] = max(result.get("effort_and_completion", 85), 75)
                
                # Ensure arrays exist
                if "code_strengths" not in result or not isinstance(result["code_strengths"], list):
                    result["code_strengths"] = []
                if "code_suggestions" not in result or not isinstance(result["code_suggestions"], list):
                    result["code_suggestions"] = []
                if "technical_observations" not in result or not isinstance(result["technical_observations"], list):
                    result["technical_observations"] = []
                
                return result
            else:
                print(f"⚠️ No JSON found in code analysis response, using fallback")
                return self._create_default_code_analysis(response)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error in code analysis: {e}")
            return self._create_default_code_analysis(response)
        except Exception as e:
            print(f"⚠️ Unexpected error in code analysis parsing: {e}")
            return self._create_default_code_analysis(response)

    def _parse_feedback_response(self, response):
        """Parse feedback response from distributed MLX with improved handling for GPT-OSS"""
        import re
        import json
        
        try:
            # Clean the response first
            response = response.strip()
            
            # DEBUG: Print first 500 chars of response to see what we're getting
            print(f"🔍 DEBUG - First 500 chars of feedback response:")
            print(f"{response[:500]}")
            print(f"🔍 DEBUG - Response length: {len(response)} chars")
            
            # STEP 1: Remove GPT-OSS internal thinking patterns
            # These patterns appear before the actual JSON output
            thinking_patterns = [
                r"We need to.*?(?=\{)",  # "We need to produce JSON..." before {
                r"I need to.*?(?=\{)",   # "I need to analyze..." before {
                r"Let me.*?(?=\{)",      # "Let me create..." before {
                r"First,.*?(?=\{)",      # "First, I'll..." before {
                r"The task is.*?(?=\{)", # "The task is to..." before {
                r"^[^{]*?(?=\{)"         # Any text before first {
            ]
            
            cleaned_response = response
            for pattern in thinking_patterns:
                cleaned_response = re.sub(pattern, '', cleaned_response, flags=re.DOTALL | re.IGNORECASE)
            
            print(f"🔍 DEBUG - After removing thinking patterns: {len(cleaned_response)} chars")
            print(f"🔍 DEBUG - Cleaned preview: {cleaned_response[:200]}")
            
            # Try multiple JSON extraction methods (in order of likelihood)
            json_part = None
            
            # Method 1: Look for ```json blocks (most explicit)
            if "```json" in cleaned_response:
                parts = cleaned_response.split("```json")
                if len(parts) > 1:
                    json_part = parts[1].split("```")[0].strip()
                print(f"🔍 DEBUG - Extracted JSON from ```json blocks, length: {len(json_part)}")
            
            # Method 2: Look for { } blocks (most common for GPT-OSS)
            elif "{" in cleaned_response and "}" in cleaned_response:
                # Find the first { and last }
                start = cleaned_response.find("{")
                end = cleaned_response.rfind("}") + 1
                json_part = cleaned_response[start:end]
                print(f"🔍 DEBUG - Extracted JSON from {{ }} markers, length: {len(json_part)}")
            
            # Method 3: Try to find JSON-like structure with regex
            else:
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_part = json_match.group()
                    print(f"🔍 DEBUG - Extracted JSON from regex, length: {len(json_part)}")
            
            # Parse the JSON if found
            if json_part:
                # Clean common JSON issues
                json_part = json_part.strip()
                
                # Remove any trailing text after the final }
                last_brace = json_part.rfind('}')
                if last_brace != -1:
                    json_part = json_part[:last_brace + 1]
                
                # Fix common encoding issues
                json_part = json_part.replace('■', '-').replace('▪', '-').replace('●', '-')
                
                # Remove internal comments that might appear in JSON
                json_part = re.sub(r'//.*?(?=\n|$)', '', json_part)  # Remove // comments
                
                print(f"🔍 DEBUG - Final JSON to parse (first 300 chars): {json_part[:300]}")
                
                result = json.loads(json_part)
                
                # Ensure required fields exist
                if not isinstance(result, dict):
                    raise ValueError("Response is not a dictionary")
                
                # Ensure minimum scores for business students
                result["overall_score"] = max(result.get("overall_score", 85), 70)
                result["business_understanding"] = max(result.get("business_understanding", 85), 75)
                result["communication_clarity"] = max(result.get("communication_clarity", 85), 75)
                result["data_interpretation"] = max(result.get("data_interpretation", 80), 70)
                result["methodology_appropriateness"] = max(result.get("methodology_appropriateness", 80), 70)
                result["reflection_quality"] = max(result.get("reflection_quality", 80), 70)
                
                # Ensure detailed_feedback structure exists
                if "detailed_feedback" not in result or not isinstance(result["detailed_feedback"], dict):
                    result["detailed_feedback"] = {}
                
                detailed = result["detailed_feedback"]
                
                # Ensure all required arrays exist
                required_arrays = [
                    "reflection_assessment", "analytical_strengths", "business_application",
                    "learning_demonstration", "areas_for_development", "recommendations"
                ]
                
                for array_name in required_arrays:
                    if array_name not in detailed or not isinstance(detailed[array_name], list):
                        detailed[array_name] = []
                
                # Ensure instructor_comments exists and clean it
                if "instructor_comments" not in result or not isinstance(result["instructor_comments"], str):
                    result["instructor_comments"] = "Good work on this assignment. Continue developing your analytical skills."
                else:
                    # Clean bullet characters and Unicode hyphens from instructor comments
                    result["instructor_comments"] = (result["instructor_comments"]
                        .replace('■', '-').replace('▪', '-').replace('●', '-')
                        .replace('\u2011', '-')  # Non-breaking hyphen (shows as ■ in PDF)
                        .replace('\u2010', '-')  # Hyphen
                        .replace('\u2012', '-')  # Figure dash
                        .replace('\u2013', '-')  # En dash
                        .replace('\u2014', '-')  # Em dash
                    )
                
                # Clean bullet characters and Unicode hyphens from all feedback arrays
                for array_name in required_arrays:
                    if array_name in detailed and isinstance(detailed[array_name], list):
                        detailed[array_name] = [
                            (item.replace('■', '-').replace('▪', '-').replace('●', '-')
                             .replace('\u2011', '-').replace('\u2010', '-')
                             .replace('\u2012', '-').replace('\u2013', '-').replace('\u2014', '-')
                            ) if isinstance(item, str) else item
                            for item in detailed[array_name]
                        ]
                
                return result
            else:
                print(f"⚠️ No JSON found in feedback response, using fallback")
                return self._create_encouraging_feedback_from_text(response)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error in feedback: {e}")
            return self._create_encouraging_feedback_from_text(response)
        except Exception as e:
            print(f"⚠️ Unexpected error in feedback parsing: {e}")
            return self._create_encouraging_feedback_from_text(response)

# Convenience function
def create_business_grader(code_model: str = None, feedback_model: str = None) -> BusinessAnalyticsGrader:
    """Create a business analytics grader instance"""
    return BusinessAnalyticsGrader(code_model, feedback_model)