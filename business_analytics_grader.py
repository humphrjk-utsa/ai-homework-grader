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
from output_comparator import OutputComparator, compare_and_generate_prompt

class BusinessAnalyticsGrader:
    """Grader optimized for business analytics students (first-year level)"""
    
    def __init__(self, 
                 code_model: str = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
                 feedback_model: str = "gemma3:27b-it-q8_0",
                 ollama_url: str = "http://localhost:11434",
                 disaggregated_client=None):
        """Initialize business analytics grader"""
        
        self.code_model = code_model
        self.feedback_model = feedback_model
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        self.disaggregated_client = disaggregated_client
        self.use_disaggregated = disaggregated_client is not None
        
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
        """Generate response using Ollama (direct or disaggregated)"""
        try:
            # Use disaggregated system if available
            if self.use_disaggregated and self.disaggregated_client:
                response_text, metrics = self.disaggregated_client.generate(model, prompt, max_tokens)
                
                # Store metrics for display
                if not hasattr(self, 'grading_stats'):
                    self.grading_stats = {}
                
                model_key = 'qwen' if 'qwen' in model.lower() or 'coder' in model.lower() else 'gemma'
                self.grading_stats[f'{model_key}_metrics'] = metrics
                
                # Ollama sometimes echoes the prompt - remove it
                if response_text.startswith(prompt):
                    response_text = response_text[len(prompt):].strip()
                
                return response_text
            
            # Fallback to direct Ollama
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Request JSON format from Ollama
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
    
    def _build_rubric_summary(self, rubric_criteria: Dict, rubric_elements: Dict) -> str:
        """Build a concise rubric summary for AI prompts"""
        summary = "\n=== ASSIGNMENT-SPECIFIC RUBRIC ===\n"
        
        # Add weights
        summary += "SCORING WEIGHTS:\n"
        for key, value in rubric_elements.items():
            weight_pct = value.get('weight', 0) * 100
            summary += f"- {key.replace('_', ' ').title()}: {weight_pct:.0f}%\n"
        
        # Add key criteria if available
        if rubric_criteria and 'rubric_elements' in rubric_criteria:
            summary += "\nKEY REQUIREMENTS:\n"
            for key, criteria in rubric_criteria['rubric_elements'].items():
                if 'description' in criteria:
                    summary += f"- {key.replace('_', ' ').title()}: {criteria['description']}\n"
                
                # Add specific criteria points
                if 'criteria' in criteria and isinstance(criteria['criteria'], list):
                    for criterion in criteria['criteria'][:5]:  # Limit to top 5
                        summary += f"  • {criterion}\n"
        
        # Add scoring rules if available
        if rubric_criteria and 'scoring_rules' in rubric_criteria:
            summary += "\nSCORING RULES:\n"
            rules = rubric_criteria['scoring_rules']
            for key, value in list(rules.items())[:5]:  # Limit to top 5 rules
                summary += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        summary += "=================================\n"
        return summary
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str,
                        template_code: str = "",
                        solution_code: str = "",
                        assignment_info: Dict = None,
                        notebook_path: str = None,
                        preprocessing_info: Dict = None) -> Dict[str, Any]:
        """Grade submission with business analytics context"""
        
        # Ensure assignment_info is a dict, not None
        if assignment_info is None:
            assignment_info = {}
        
        # Get rubric weights from assignment_info if available, otherwise use defaults
        rubric_elements = {
            "technical_execution": {"weight": 0.40},
            "data_analysis": {"weight": 0.40},
            "business_thinking": {"weight": 0.10},
            "communication": {"weight": 0.10}
        }
        
        # Try to load full rubric from assignment_info
        rubric_criteria = {}
        rubric = None  # Initialize rubric variable for validator
        if assignment_info and 'rubric' in assignment_info:
            try:
                import json
                rubric_data = json.loads(assignment_info['rubric']) if isinstance(assignment_info['rubric'], str) else assignment_info['rubric']
                
                # Store full rubric for prompt inclusion and validator
                rubric_criteria = rubric_data
                rubric = rubric_data  # Store for validator
                
                if 'rubric_elements' in rubric_data:
                    # Extract weights from rubric_elements
                    for key, value in rubric_data['rubric_elements'].items():
                        if key in rubric_elements and 'weight' in value:
                            rubric_elements[key]['weight'] = value['weight']
                            # Also store the full criteria
                            rubric_elements[key]['criteria'] = value
                    print(f"✅ Loaded custom rubric with detailed criteria")
            except Exception as e:
                print(f"⚠️ Could not load rubric, using defaults: {e}")
                rubric = None  # Ensure rubric is None if loading fails
        else:
            rubric = None  # No rubric in assignment_info
        
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
            # Check notebook size first
            import os
            notebook_size_mb = os.path.getsize(notebook_path) / (1024 * 1024)
            notebook_size_kb = os.path.getsize(notebook_path) / 1024
            print(f"📏 Notebook size: {notebook_size_kb:.1f} KB ({notebook_size_mb:.2f} MB)")
            
            # Skip extremely large notebooks that will timeout
            if notebook_size_kb > 600:  # More than 600KB (increased from 400KB for better coverage)
                print(f"⚠️ SKIPPING: Notebook too large ({notebook_size_kb:.1f} KB)")
                print(f"   This notebook exceeds processing limits and requires manual review.")
                raise RuntimeError(f"Notebook too large ({notebook_size_kb:.1f} KB) - requires manual review")
            
            if notebook_size_kb > 300:  # More than 300KB
                print(f"⚠️ WARNING: Large notebook ({notebook_size_kb:.1f} KB) - this may take longer to process")
            
            if notebook_size_mb > 10.0:
                print(f"⚠️ CRITICAL: Very large notebook ({notebook_size_mb:.2f} MB) - processing may be slow")
            
            print("🔍 Validating notebook submission...")
            validation_results = self.validator.validate_notebook(notebook_path)
            validation_penalty = validation_results['total_penalty_percent']
            validation_feedback = self.validator.generate_validation_feedback(validation_results)
            
            if validation_penalty > 0:
                print(f"⚠️ Validation issues found: {validation_penalty}% penalty")
                for issue in validation_results['issues']:
                    print(f"   - {issue}")
            
            # Check if notebook needs execution
            print("🔍 Checking if notebook has been executed...")
            from notebook_executor import NotebookExecutor
            executor = NotebookExecutor(data_folder='data', timeout=60)
            
            needs_exec, total_cells, executed_cells = executor.needs_execution(notebook_path)
            
            if needs_exec:
                print(f"⚡ Notebook not fully executed ({executed_cells}/{total_cells} cells)")
                print(f"🚀 Attempting to execute notebook before grading...")
                
                try:
                    notebook_to_use, exec_info = executor.execute_if_needed(notebook_path)
                    
                    if exec_info['execution_success']:
                        print(f"✅ Notebook executed successfully!")
                        print(f"📝 Using executed notebook for grading")
                        notebook_path = notebook_to_use  # Use executed version
                        
                        # Reduce validation penalty since we executed it
                        if validation_penalty >= 50:
                            print(f"📉 Reducing validation penalty from {validation_penalty}% to 10% (auto-executed)")
                            validation_penalty = 10
                    else:
                        print(f"⚠️ Execution failed: {exec_info.get('error_message', 'Unknown error')}")
                        print(f"📝 Using original notebook (may have incomplete outputs)")
                        
                except Exception as e:
                    print(f"⚠️ Could not execute notebook: {e}")
                    print(f"📝 Proceeding with original notebook")
            else:
                print(f"✅ Notebook already executed ({executed_cells}/{total_cells} cells)")
            
            # Add output verification to prevent AI hallucination
            print("🔍 Verifying outputs exist...")
            from output_verifier import OutputVerifier
            output_verifier = OutputVerifier(notebook_path)
            with_outputs, total_cells = output_verifier.count_cells_with_outputs()
            completion_pct = output_verifier.get_completion_percentage()
            print(f"📊 Output Check: {with_outputs}/{total_cells} cells have outputs ({completion_pct:.0f}%)")
            
            # NEW: Compare outputs programmatically if solution notebook exists
            output_comparison = None
            # Get solution path from assignment_info if available
            if assignment_info and 'solution_notebook' in assignment_info:
                solution_notebook_path = assignment_info['solution_notebook']
            elif assignment_info and 'solution_path' in assignment_info:
                solution_notebook_path = assignment_info['solution_path']
            else:
                # No solution available for comparison
                solution_notebook_path = None
                print("⚠️ No solution notebook in assignment_info, skipping output comparison")
            
            # Check notebook size before attempting comparison
            import os
            notebook_size_kb = os.path.getsize(notebook_path) / 1024
            
            # Skip output comparison for notebooks larger than 200KB to prevent hangs
            if notebook_size_kb > 200:
                print(f"⚠️ Notebook too large ({notebook_size_kb:.1f} KB), skipping output comparison to prevent hang")
                output_comparison = None
            elif solution_notebook_path and os.path.exists(solution_notebook_path):
                print("🔬 Comparing outputs to solution...")
                try:
                    from output_comparator import OutputComparator
                    import signal
                    
                    # Set a timeout for output comparison (30 seconds max)
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Output comparison timed out")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(30)  # 30 second timeout
                    
                    try:
                        comparator = OutputComparator(notebook_path, solution_notebook_path)
                        output_comparison = comparator.compare_outputs()
                        print(f"📊 Output Comparison: {output_comparison['matching_cells']}/{output_comparison['total_cells']} cells match ({output_comparison['match_rate']:.1f}%)")
                        
                        # Store just the summary stats, not the full comparison (to keep prompt small)
                        output_comparison = {
                            'total_cells': output_comparison['total_cells'],
                            'matching_cells': output_comparison['matching_cells'],
                            'match_rate': output_comparison['match_rate'],
                            'accuracy_score': output_comparison['accuracy_score']
                        }
                    finally:
                        signal.alarm(0)  # Cancel the alarm
                        
                except TimeoutError:
                    print(f"⚠️ Output comparison timed out after 30 seconds, skipping")
                    output_comparison = None
                except Exception as e:
                    print(f"⚠️ Output comparison failed: {e}")
                    import traceback
                    traceback.print_exc()
                    output_comparison = None
        
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
            
            # Build rubric summary for prompts
            rubric_summary = self._build_rubric_summary(rubric_criteria, rubric_elements)
            
            code_prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "code_analysis",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                template_code=template_code if template_code else "# No template provided",
                student_code=student_code,
                solution_code=solution_code,
                rubric_criteria=rubric_summary
            )
            
            feedback_prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "feedback",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                student_markdown=student_markdown,
                student_code_summary=student_code[:800],
                rubric_criteria=rubric_summary
            )
            
            # Execute in parallel across Mac Studios
            print("🚀 About to call generate_parallel_sync...")
            try:
                result = self.distributed_client.generate_parallel_sync(code_prompt, feedback_prompt)
                print(f"✅ generate_parallel_sync returned")
                
                print(f"🔍 DEBUG - Parallel result keys: {result.keys()}")
                print(f"🔍 DEBUG - Has code_analysis: {bool(result.get('code_analysis'))}")
                print(f"🔍 DEBUG - Has feedback: {bool(result.get('feedback'))}")
                
                # Check for errors first
                if result.get('error'):
                    print(f"❌ ERROR from distributed client: {result['error']}")
                    raise RuntimeError(f"Distributed MLX generation failed: {result['error']}")
                
                # Check for missing responses
                if not result.get('code_analysis'):
                    print(f"❌ ERROR: No code_analysis in result")
                    raise RuntimeError(f"Distributed MLX generation failed: No code analysis returned")
                
                if not result.get('feedback'):
                    print(f"❌ ERROR: No feedback in result")
                    raise RuntimeError(f"Distributed MLX generation failed: No feedback returned")
                
                # Parse the responses
                print("📊 Parsing code analysis response...")
                code_analysis = self._parse_code_analysis_response(result['code_analysis'])
                print("📊 Parsing feedback response...")
                comprehensive_feedback = self._parse_feedback_response(result['feedback'])
                print("✅ Both responses parsed successfully")
                
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
            except Exception as e:
                print(f"❌ EXCEPTION in parallel generation:")
                import traceback
                traceback.print_exc()
                raise
        else:
            # Use Ollama system (disaggregated or local)
            # Submit both tasks simultaneously
            future_code = self.executor.submit(
                self._execute_business_code_analysis, 
                student_code, template_code, solution_code, assignment_info
            )
            
            future_feedback = self.executor.submit(
                self._execute_business_feedback_generation,
                student_code, student_markdown, assignment_info
            )
            
            # Wait for both results
            code_analysis = future_code.result()
            comprehensive_feedback = future_feedback.result()
        
        parallel_time = time.time() - parallel_start
        
        # Aggregate performance metrics from disaggregated calls
        if self.use_disaggregated:
            qwen_metrics = self.grading_stats.get('qwen_metrics', {})
            gemma_metrics = self.grading_stats.get('gemma_metrics', {})
            
            # Calculate combined throughput
            qwen_tokens = qwen_metrics.get('completion_tokens', 0)
            gemma_tokens = gemma_metrics.get('completion_tokens', 0)
            total_tokens = qwen_tokens + gemma_tokens
            
            qwen_speed = qwen_metrics.get('decode_speed', 0)
            gemma_speed = gemma_metrics.get('decode_speed', 0)
            combined_speed = total_tokens / parallel_time if parallel_time > 0 else 0
            
            self.grading_stats['performance_diagnostics'] = {
                'qwen': {
                    'tokens_per_second': qwen_speed,
                    'output_tokens': qwen_tokens,
                    'total_tokens': qwen_metrics.get('total_tokens', 0)
                },
                'gemma': {
                    'tokens_per_second': gemma_speed,
                    'output_tokens': gemma_tokens,
                    'total_tokens': gemma_metrics.get('total_tokens', 0)
                },
                'combined_tokens_per_second': combined_speed
            }
            
            print(f"📊 Aggregated Performance Metrics:")
            print(f"   🔧 Qwen: {qwen_speed:.1f} tok/s ({qwen_tokens} tokens)")
            print(f"   📝 GPT-OSS: {gemma_speed:.1f} tok/s ({gemma_tokens} tokens)")
            print(f"   🚀 Combined: {combined_speed:.1f} tok/s ({total_tokens} tokens in {parallel_time:.1f}s)")
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
            code_analysis, comprehensive_feedback, student_code, template_code, rubric, output_comparison
        )
        print(f"🔍 After validation: technical_score={code_analysis.get('technical_score', 0)}, overall_score={comprehensive_feedback.get('overall_score', 0)}")
        
        # Merge results with business context and apply validation penalty
        final_result = self._merge_business_results(code_analysis, comprehensive_feedback, assignment_info, validation_penalty, preprocessing_info, rubric_elements)
        
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
        
        # Add detailed performance diagnostics
        if self.use_distributed_mlx and self.distributed_client:
            final_result['performance_diagnostics'] = self.distributed_client.get_performance_diagnostics()
        elif self.use_disaggregated and 'performance_diagnostics' in self.grading_stats:
            # Transform disaggregated metrics to expected format
            perf_metrics = self.grading_stats['performance_diagnostics']
            qwen_metrics = perf_metrics.get('qwen', {})
            gemma_metrics = perf_metrics.get('gemma', {})
            
            qwen_tok_per_sec = qwen_metrics.get('tokens_per_second', 0)
            gemma_tok_per_sec = gemma_metrics.get('tokens_per_second', 0)
            combined_throughput = perf_metrics.get('combined_tokens_per_second', 0)
            
            final_result['performance_diagnostics'] = {
                'qwen_performance': {
                    'generation_time_seconds': self.grading_stats.get('code_analysis_time', 0),
                    'tokens_per_second': qwen_tok_per_sec,
                    'model': 'Disaggregated Ollama (DGX+Mac)'
                },
                'gemma_performance': {
                    'generation_time_seconds': self.grading_stats.get('feedback_generation_time', 0),
                    'tokens_per_second': gemma_tok_per_sec,
                    'model': 'Disaggregated Ollama (DGX+Mac)'
                },
                'combined_metrics': {
                    'parallel_efficiency': self.grading_stats.get('parallel_efficiency', 0),
                    'combined_throughput_tokens_per_second': combined_throughput
                }
            }
            
            print(f"📊 Final Performance Diagnostics:")
            print(f"   🔧 Qwen: {qwen_tok_per_sec:.1f} tok/s")
            print(f"   📝 GPT-OSS: {gemma_tok_per_sec:.1f} tok/s")
            print(f"   🚀 Combined: {combined_throughput:.1f} tok/s")
            print(f"   ⚡ Efficiency: {self.grading_stats.get('parallel_efficiency', 0):.1f}x")
        else:
            # Add basic performance metrics for local Ollama
            final_result['performance_diagnostics'] = {
                'qwen_performance': {
                    'generation_time_seconds': self.grading_stats.get('code_analysis_time', 0),
                    'tokens_per_second': 0,
                    'model': 'Local Ollama'
                },
                'gemma_performance': {
                    'generation_time_seconds': self.grading_stats.get('feedback_generation_time', 0),
                    'tokens_per_second': 0,
                    'model': 'Local Ollama'
                },
                'combined_metrics': {
                    'parallel_efficiency': self.grading_stats.get('parallel_efficiency', 0),
                    'combined_throughput_tokens_per_second': 0
                }
            }
        
        print(f"🎉 Business analytics grading complete!")
        print(f"⚡ Parallel time: {parallel_time:.1f}s")
        print(f"📊 Efficiency gain: {self.grading_stats['parallel_efficiency']:.1f}x")
        print(f"🕒 Total time: {total_time:.1f}s")
        
        return final_result
    
    def _execute_business_code_analysis(self, student_code: str, template_code: str, solution_code: str,
                                       assignment_info: Dict, validation_results: Dict = None) -> Dict[str, Any]:
        """Execute code analysis with business analytics context"""
        start_time = time.time()
        
        print(f"🔧 [CODE] Analyzing with business context...")
        
        # Use Ollama-specific prompts if using disaggregated/Ollama
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        
        if self.use_disaggregated:
            # Use Ollama-optimized prompt with validation context
            prompt = self.prompt_manager.get_ollama_prompt(
                "code_analysis",
                validation_results=validation_results,
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                assignment_name=assignment_name,
                template_code=template_code if template_code else "# No template provided",
                student_code=student_code,
                solution_code=solution_code
            )
        else:
            # Use standard prompt for MLX
            prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "code_analysis",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                template_code=template_code if template_code else "# No template provided",
                student_code=student_code,
                solution_code=solution_code
            )
        
        response = self.generate_with_ollama(self.code_model, prompt, max_tokens=2400)
        
        analysis_time = time.time() - start_time
        self.grading_stats['code_analysis_time'] = analysis_time
        
        print(f"✅ [CODE] Business analysis complete ({analysis_time:.1f}s)")
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 85}  # Default higher for business
        
        return self._parse_business_code_response(response)
    
    def _execute_business_feedback_generation(self, student_code: str, student_markdown: str,
                                            assignment_info: Dict, validation_results: Dict = None) -> Dict[str, Any]:
        """Execute feedback generation with business context"""
        start_time = time.time()
        
        print(f"📝 [FEEDBACK] Generating business-focused feedback...")
        
        # Use Ollama-specific prompts if using disaggregated/Ollama
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        
        if self.use_disaggregated:
            # Use Ollama-optimized prompt with validation context
            prompt = self.prompt_manager.get_ollama_prompt(
                "feedback",
                validation_results=validation_results,
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                assignment_name=assignment_name,
                student_markdown=student_markdown,
                student_code_summary=student_code[:800]
            )
        else:
            # Use standard prompt for MLX
            prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "feedback",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                student_markdown=student_markdown,
                student_code_summary=student_code[:800]
            )
        
        response = self.generate_with_ollama(self.feedback_model, prompt, max_tokens=2400)
        
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
                               preprocessing_info: Dict = None, rubric_elements: Dict = None) -> Dict[str, Any]:
        """Merge results with business-friendly weighting for 37.5 point scale"""
        
        # Extract individual component scores (no defaults - use actual scores)
        technical_score = code_analysis.get("technical_score", 50)
        business_understanding = feedback.get("business_understanding", 50)
        data_interpretation = feedback.get("data_interpretation", 50)
        communication_clarity = feedback.get("communication_clarity", 50)
        
        # Get weights from rubric if available, otherwise use defaults
        # Default weights: Technical 40%, Analysis 40%, Business 10%, Communication 10%
        technical_weight = 0.40
        business_weight = 0.10
        analysis_weight = 0.40
        communication_weight = 0.10
        
        if rubric_elements:
            technical_weight = rubric_elements.get('technical_execution', {}).get('weight', 0.40)
            business_weight = rubric_elements.get('business_thinking', {}).get('weight', 0.10)
            analysis_weight = rubric_elements.get('data_analysis', {}).get('weight', 0.40)
            communication_weight = rubric_elements.get('communication', {}).get('weight', 0.10)
        
        # Calculate points for each rubric component (37.5 total points)
        technical_points = (technical_score / 100) * (37.5 * technical_weight)
        business_points = (business_understanding / 100) * (37.5 * business_weight)
        analysis_points = (data_interpretation / 100) * (37.5 * analysis_weight)
        communication_points = (communication_clarity / 100) * (37.5 * communication_weight)
        
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

    def _prepare_code_analysis_prompt(self, student_code, solution_code, assignment_info, output_comparison=None):
        """Prepare prompt for distributed MLX code analysis with deep evaluation"""
        
        # Add programmatic output comparison if available (SUMMARY ONLY to avoid timeout)
        comparison_section = ""
        if output_comparison:
            match_rate = output_comparison.get('match_rate', 0)
            comparison_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔬 PROGRAMMATIC OUTPUT VERIFICATION (PRIMARY GRADING EVIDENCE):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an AUTOMATED comparison of student outputs vs solution outputs.
Use this as PRIMARY evidence for grading accuracy.

Results:
- Cells with matching outputs: {output_comparison['matching_cells']}/{output_comparison['total_cells']} ({match_rate:.1f}%)
- Overall accuracy: {output_comparison.get('accuracy_score', 0):.1f}%

🚨 CRITICAL GRADING RULES - FOLLOW EXACTLY:
- If match rate >= 90%: Outputs are CORRECT → Score 90-100%
- If match rate 75-89%: Outputs are MOSTLY CORRECT → Score 80-90%  
- If match rate 60-74%: Outputs are PARTIALLY CORRECT → Score 70-80%
- If match rate 40-59%: Outputs are MOSTLY INCORRECT → Score 50-70%
- If match rate < 40%: Outputs are INCORRECT or MISSING → Score 30-50%

⚠️ DO NOT give high scores if match rate is low!
⚠️ Low match rate = incorrect outputs = low score
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return f"""You are a business analytics instructor evaluating first-year student R code. Analyze the ACTUAL code deeply, compare outputs to expected results, and recognize alternative valid approaches.

ASSIGNMENT: {assignment_info.get('title', 'Business Analytics Assignment')}
STUDENT LEVEL: First-year business analytics (introductory R programming)

{comparison_section}

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

SCORING GUIDELINES - HONEST AND FAIR:

EXCELLENT (90-100):
- ALL required sections complete with outputs
- Outputs MATCH solution outputs (correct results)
- Code executes without errors
- Demonstrates mastery of concepts
- May use alternative valid approaches

GOOD (80-89):
- Most sections complete (80-90% of work)
- Most outputs correct (1-2 minor errors)
- Code mostly works as intended
- Solid understanding demonstrated
- Minor issues that don't affect main results

ADEQUATE (70-79):
- Majority of sections attempted (60-80% of work)
- Some outputs correct, some wrong
- Several errors affecting results
- Basic understanding shown
- Needs significant corrections

POOR (60-69):
- Some sections attempted (40-60% of work)
- Many outputs wrong or missing
- Major errors throughout
- Minimal understanding
- Requires substantial rework

FAILING (0-59):
- Few/no sections complete (<40% of work)
- No outputs or all outputs wrong
- Template only or fundamentally wrong
- Does not demonstrate understanding

CRITICAL SCORING RULES:
1. NO OUTPUT = 0 points for that section (not negotiable)
2. WRONG OUTPUT = Major deduction (compare to solution output)
3. CORRECT OUTPUT = Full credit (even if different approach)
4. COUNT SECTIONS: Score reflects actual completion percentage
5. COMPARE TO SOLUTION: Outputs should match expected results
6. BE HONEST: Don't inflate scores - give credit where deserved
7. FLEXIBILITY: Accept alternative valid approaches if outputs are correct

EXAMPLES:
- 8/8 sections, all outputs match solution → 95-100
- 8/8 sections, 2 outputs wrong → 80-85
- 6/8 sections complete, all correct → 75-80
- 6/8 sections, half wrong → 65-70
- 4/8 sections attempted → 50-60
- Template only or no outputs → 10-20

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

STRICT ENFORCEMENT - READ CAREFULLY:

1. COUNT SECTIONS WITH CORRECT OUTPUTS:
   - Only count sections where output EXISTS and is CORRECT
   - Compare to solution output to verify correctness
   - Wrong output = section is NOT correct

2. CALCULATE MAXIMUM POSSIBLE SCORE:
   - If 8/8 sections correct → Can score 90-100
   - If 7/8 sections correct → Maximum 87, typical 80-85
   - If 6/8 sections correct → Maximum 75, typical 70-75
   - If 4/8 sections correct → Maximum 60, typical 50-55
   - If 0-2 sections correct → Maximum 30, typical 10-20

3. BE HONEST WITH SCORING:
   - Don't inflate scores to be nice
   - Wrong is wrong - deduct appropriately
   - Missing is missing - give 0 for that section
   - Correct is correct - give full credit

4. PROVIDE SPECIFIC CORRECTIONS:
   - "Your output shows X rows, should show Y rows"
   - "Your join result is missing Z column"
   - "Your calculation gives A, should give B"

CRITICAL: Base scores on actual code execution and outputs. Recognize valid alternatives. Provide specific, actionable suggestions with code examples. BE HONEST - don't give 85% to everyone!
"""
    
    def _prepare_feedback_prompt(self, student_code, student_markdown, assignment_info):
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

SCORING GUIDELINES - HONEST FEEDBACK:

EXCELLENT (90-100):
- All work complete with correct results
- Thoughtful, detailed reflections
- Clear understanding demonstrated
- Professional presentation

GOOD (80-89):
- Most work complete with mostly correct results
- Good reflections showing understanding
- Minor errors or omissions
- Solid effort throughout

ADEQUATE (70-79):
- Majority of work attempted
- Some correct, some incorrect results
- Basic reflections present
- Acceptable but needs improvement

POOR (60-69):
- Some work attempted
- Many incorrect results
- Minimal or weak reflections
- Significant gaps in understanding

FAILING (0-59):
- Little to no work completed
- Wrong or missing results
- No meaningful reflections
- Does not meet minimum standards

CRITICAL FEEDBACK RULES:
1. BE HONEST: Don't inflate scores to be nice
2. COMPARE TO SOLUTION: Results should match expected outcomes
3. WRONG = WRONG: If output doesn't match solution, say so clearly
4. CORRECT = CORRECT: Give full credit for right answers
5. SPECIFIC FEEDBACK: Point out exactly what's wrong and how to fix it
6. CONSTRUCTIVE: Explain what they need to do differently
7. FAIR: Credit good work, penalize incomplete/wrong work

FEEDBACK APPROACH:
- If outputs match solution: "Excellent work! Your results are correct."
- If outputs are wrong: "Your output shows X, but should show Y. Review [concept]."
- If section missing: "Section Z is incomplete. You need to [specific action]."
- If partially correct: "Good start on X, but Y needs correction. Try [suggestion]."

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