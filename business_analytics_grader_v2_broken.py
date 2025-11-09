#!/usr/bin/env python3
"""
Business Analytics Grading System V2
Integrates 4-layer validation system with structured feedback generation
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

# Import new validators
from validators.assignment_6_systematic_validator import Assignment6SystematicValidator
from validators.rubric_driven_validator import RubricDrivenValidator
from validators.smart_output_validator import SmartOutputValidator


class BusinessAnalyticsGraderV2:
    """
    Enhanced grader with 4-layer validation system
    - Layer 1: Systematic validation (variables, sections, execution)
    - Layer 2: Smart output validation (compare with solution)
    - Layer 3: AI code analysis (Qwen Coder)
    - Layer 4: AI feedback synthesis (GPT-OSS 120B)
    """
    
    def __init__(self, 
                 code_model: str = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
                 feedback_model: str = "gemma3:27b-it-q8_0",
                 ollama_url: str = "http://localhost:11434",
                 rubric_path: str = None,
                 solution_path: str = None):
        """Initialize enhanced business analytics grader"""
        
        # Check for disaggregated inference system (DGX prefill + Mac decode)
        self.use_disaggregated = False
        self.disaggregated_client = None
        
        if os.path.exists('disaggregated_inference/config_current.json'):
            try:
                from disaggregated_client import DisaggregatedClient
                self.disaggregated_client = DisaggregatedClient()
                self.use_disaggregated = True
                self.code_model = code_model
                self.feedback_model = feedback_model
                print(f"🚀 Using Disaggregated Inference System:")
                print(f"   DGX Sparks (prefill) + Mac Studios (decode)")
                print(f"   Qwen: DGX Spark 1 → Mac Studio 1")
                print(f"   GPT-OSS: DGX Spark 2 → Mac Studio 2")
            except Exception as e:
                print(f"⚠️ Disaggregated system failed to load: {e}")
                import traceback
                traceback.print_exc()
                self.use_disaggregated = False
        
        # Fallback to separate Ollama servers if no disaggregated system
        if not self.use_disaggregated:
            if os.path.exists('ollama_servers.json'):
                with open('ollama_servers.json', 'r') as f:
                    ollama_config = json.load(f)
                    self.qwen_server = ollama_config.get('qwen_server', ollama_url)
                    self.gptoss_server = ollama_config.get('gptoss_server', ollama_url)
                    self.code_model = ollama_config.get('code_model', code_model)
                    self.feedback_model = ollama_config.get('feedback_model', feedback_model)
                    print(f"🔧 Using separate Ollama servers:")
                    print(f"   Qwen: {self.qwen_server}")
                    print(f"   GPT-OSS: {self.gptoss_server}")
            else:
                self.qwen_server = ollama_url
                self.gptoss_server = ollama_url
                self.code_model = code_model
                self.feedback_model = feedback_model
        
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager()
        
        # Initialize validators
        self.legacy_validator = NotebookValidator()  # Fallback
        
        # Initialize new validators if paths provided
        self.systematic_validator = None
        self.output_validator = None
        
        if rubric_path and os.path.exists(rubric_path):
            print(f"📋 Loading systematic validator with rubric: {rubric_path}")
            # Try to use rubric-driven validator first (works for any assignment with autograder_checks)
            try:
                self.systematic_validator = RubricDrivenValidator(rubric_path)
                print(f"✅ Using RubricDrivenValidator (generic)")
            except (ValueError, KeyError) as e:
                # Fallback to Assignment 6 validator if rubric doesn't have autograder_checks
                print(f"⚠️ Rubric missing autograder_checks: {e}")
                print(f"⚠️ Falling back to Assignment6SystematicValidator")
                self.systematic_validator = Assignment6SystematicValidator(rubric_path)
            except Exception as e:
                print(f"❌ Error loading RubricDrivenValidator: {e}")
                print(f"⚠️ Falling back to Assignment6SystematicValidator")
                import traceback
                traceback.print_exc()
                self.systematic_validator = Assignment6SystematicValidator(rubric_path)
            
            if solution_path and os.path.exists(solution_path):
                print(f"📊 Loading output validator with solution: {solution_path}")
                self.output_validator = SmartOutputValidator(solution_path, rubric_path)
            else:
                print(f"⚠️ No solution path provided, output validation disabled")
        else:
            print(f"⚠️ No rubric path provided, using legacy validator")
        
        # Check for distributed MLX system
        self.use_distributed_mlx = False
        self.distributed_client = None
        
        if os.path.exists('distributed_config.json'):
            try:
                from models.distributed_mlx_client import DistributedMLXClient
                
                with open('distributed_config.json', 'r') as f:
                    config = json.load(f)
                
                qwen_url = config['urls']['qwen_server']
                gemma_url = config['urls']['gemma_server']
                
                self.distributed_client = DistributedMLXClient(qwen_url, gemma_url)
                
                status = self.distributed_client.get_system_status()
                if status['distributed_ready']:
                    self.use_distributed_mlx = True
                    print(f"🖥️ Using Distributed MLX System!")
                    print(f"📡 Qwen Server: {qwen_url}")
                    print(f"📡 GPT-OSS Server: {gemma_url}")
            except Exception as e:
                print(f"⚠️ Distributed MLX setup failed: {e}, using Ollama")
        
        print(f"🎓 Business Analytics Grading System V2 Initialized")
        print(f"🤖 Code Analyzer: {code_model}")
        print(f"📝 Feedback Generator: {feedback_model}")
        print(f"✅ 4-Layer Validation: {'Enabled' if self.systematic_validator else 'Disabled (Legacy Mode)'}")
        
        # Performance tracking
        self.grading_stats = {
            'validation_time': 0,
            'code_analysis_time': 0,
            'feedback_generation_time': 0,
            'total_time': 0
        }
        
        # Parallel processing
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    
    def _run_4layer_validation(self, notebook_path: str) -> Dict[str, Any]:
        """
        Run 4-layer validation system
        Returns comprehensive validation results
        """
        print("\n" + "="*80)
        print("🔍 RUNNING 4-LAYER VALIDATION SYSTEM")
        print("="*80)
        
        validation_start = time.time()
        
        # LAYER 1: Systematic Validation
        print("\n[LAYER 1: SYSTEMATIC VALIDATION]")
        print("-"*80)
        print(f"DEBUG: Validator type: {type(self.systematic_validator).__name__}")
        sys_result = self.systematic_validator.validate_notebook(notebook_path)
        print(f"DEBUG: Section breakdown keys: {list(sys_result.get('section_breakdown', {}).keys())}")
        
        print(f"✅ Variables Found: {sys_result['variable_check']['found']}/{sys_result['variable_check']['total_required']}")
        total_sections = len(sys_result['section_breakdown'])
        complete_sections = sum(1 for s in sys_result['section_breakdown'].values() if s['status'] == 'complete')
        print(f"✅ Sections Complete: {complete_sections}/{total_sections}")
        print(f"✅ Execution Rate: {sys_result['cell_stats']['execution_rate']*100:.1f}%")
        print(f"✅ Base Score: {sys_result['final_score']:.1f}/100")
        
        # LAYER 2: Smart Output Validation
        output_result = None
        if self.output_validator:
            print(f"\n[LAYER 2: SMART OUTPUT VALIDATION]")
            print("-"*80)
            output_result = self.output_validator.validate_student_outputs(notebook_path)
            
            print(f"✅ Output Match: {output_result['overall_match']*100:.1f}%")
            print(f"✅ Checks Passed: {output_result['passed_checks']}/{output_result['total_checks']}")
            print(f"✅ Discrepancies: {len(output_result['discrepancies'])}")
            print(f"✅ Score Adjustment: {output_result['score_adjustment']:+.1f} points")
            
            if output_result['discrepancies']:
                print(f"\nKey Discrepancies:")
                for disc in output_result['discrepancies'][:5]:  # Show first 5
                    print(f"  ❌ {disc['variable']}: {disc['issue']}")
        
        validation_time = time.time() - validation_start
        self.grading_stats['validation_time'] = validation_time
        
        print(f"\n⏱️ Validation completed in {validation_time:.1f}s")
        print("="*80 + "\n")
        
        # Merge results
        return self._merge_validation_results(sys_result, output_result)
    
    def _merge_validation_results(self, sys_result: Dict, output_result: Optional[Dict]) -> Dict[str, Any]:
        """Merge systematic and output validation into comprehensive results"""
        
        # Calculate adjusted score
        base_score = sys_result['final_score']
        if output_result:
            # Smart penalty application:
            # - If base_score is already low (< 30%), don't apply output penalties
            #   (missing outputs are already reflected in the base score)
            # - If base_score is decent (>= 30%), apply penalties for wrong outputs
            #   (student did the work but got wrong answers)
            if base_score < 30:
                # Student hasn't done much work - don't double-penalize for missing outputs
                adjusted_score = base_score
            else:
                # Student did substantial work - penalize for incorrect outputs
                # But cap penalty to not exceed base score
                if output_result['score_adjustment'] < 0:
                    max_penalty = min(abs(output_result['score_adjustment']), base_score * 0.5)  # Max 50% penalty
                    adjusted_score = max(0, base_score - max_penalty)
                else:
                    adjusted_score = base_score + output_result['score_adjustment']
        else:
            adjusted_score = base_score
        
        # Build issue list for AI analysis
        issues = []
        
        # Add missing variable issues
        if sys_result['variable_check']['missing']:
            for var in sys_result['variable_check']['missing']:
                issues.append(f"Missing required variable: {var}")
        
        # Add incomplete section issues
        for section_id, section_data in sys_result['section_breakdown'].items():
            if section_data['status'] == 'incomplete':
                issues.append(f"Incomplete section: {section_data['name']}")
        
        # Add output discrepancy issues
        if output_result and output_result['discrepancies']:
            for disc in output_result['discrepancies']:
                issues.append(f"Output mismatch for {disc['variable']}: {disc['issue']}")
        
        # Calculate penalty
        penalty_percent = max(0, 100 - adjusted_score)
        
        return {
            'total_penalty_percent': penalty_percent,
            'adjusted_score': adjusted_score,
            'base_score': base_score,
            'issues': issues,
            'systematic_results': sys_result,
            'output_results': output_result,
            'validation_summary': self._create_validation_summary(sys_result, output_result)
        }
    
    def _create_validation_summary(self, sys_result: Dict, output_result: Optional[Dict]) -> str:
        """Create human-readable validation summary for AI prompts"""
        
        summary_lines = []
        summary_lines.append("VALIDATION RESULTS:")
        summary_lines.append(f"- Variables Found: {sys_result['variable_check']['found']}/{sys_result['variable_check']['total_required']}")
        
        complete_sections = sum(1 for s in sys_result['section_breakdown'].values() if s['status'] == 'complete')
        total_sections = len(sys_result['section_breakdown'])
        section_pct = (complete_sections/total_sections*100) if total_sections > 0 else 0
        summary_lines.append(f"- Sections Complete: {complete_sections}/{total_sections} ({section_pct:.0f}%)")
        
        summary_lines.append(f"- Execution Rate: {sys_result['cell_stats']['execution_rate']*100:.1f}%")
        summary_lines.append(f"- Base Score: {sys_result['final_score']:.1f}/100")
        
        if output_result:
            summary_lines.append(f"- Output Match Rate: {output_result['overall_match']*100:.1f}%")
            summary_lines.append(f"- Output Checks Passed: {output_result['passed_checks']}/{output_result['total_checks']}")
        
        # Add completed sections
        completed = [s['name'] for s in sys_result['section_breakdown'].values() if s['status'] == 'complete']
        if completed:
            summary_lines.append(f"\nCOMPLETED SECTIONS:")
            for section in completed[:10]:  # Limit to first 10
                summary_lines.append(f"  ✅ {section}")
        
        # Add incomplete sections
        incomplete = [s['name'] for s in sys_result['section_breakdown'].values() if s['status'] == 'incomplete']
        if incomplete:
            summary_lines.append(f"\nINCOMPLETE SECTIONS:")
            for section in incomplete[:10]:  # Limit to first 10
                summary_lines.append(f"  ❌ {section}")
        
        return "\n".join(summary_lines)
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str,
                        template_code: str = "",
                        solution_code: str = "",
                        assignment_info: Dict = None,
                        notebook_path: str = None,
                        preprocessing_info: Dict = None) -> Dict[str, Any]:
        """
        Grade submission using 4-layer validation + AI analysis
        Returns structured feedback in the standard format
        """
        
        start_time = time.time()
        
        print("🎓 Starting Enhanced Business Analytics Grading...")
        
        # Run validation (Layer 1 & 2)
        if self.systematic_validator and notebook_path:
            validation_results = self._run_4layer_validation(notebook_path)
        else:
            # Fallback to legacy validator
            print("⚠️ Using legacy validator (4-layer system not available)")
            validation_results = self.legacy_validator.validate_notebook(notebook_path)
        
        # Layer 3 & 4: AI Code Analysis and Feedback Generation
        print("\n[LAYER 3 & 4: AI ANALYSIS AND FEEDBACK GENERATION]")
        print("-"*80)
        
        # Identify what code the student actually wrote (vs template)
        student_changes = self._identify_student_changes(student_code, template_code, solution_code)
        
        # Prepare prompts with validation context
        validation_summary = validation_results.get('validation_summary', '')
        
        # Get assignment name for prompt manager
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        
        # Build rubric summary
        rubric_summary = ""
        if assignment_info.get('rubric'):
            try:
                import json
                rubric_data = json.loads(assignment_info['rubric']) if isinstance(assignment_info['rubric'], str) else assignment_info['rubric']
                if 'rubric_elements' in rubric_data:
                    rubric_summary = "Rubric Elements:\n"
                    for key, value in rubric_data['rubric_elements'].items():
                        rubric_summary += f"- {key}: {value.get('weight', 0)*100}%\n"
            except:
                pass
        
        # Execute AI analysis in parallel
        parallel_start = time.time()
        
        if self.use_distributed_mlx:
            # Use distributed MLX system
            print("🖥️ Using Distributed MLX System for AI analysis...")
            
            # Build enhanced context with student changes analysis
            enhanced_context = f"{student_changes['ai_context']}\n\n{validation_summary}"
            
            code_prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "code_analysis",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                template_code=template_code if template_code else "# No template provided",
                student_code=student_code,
                solution_code=solution_code,
                rubric_criteria=rubric_summary,
                validation_context=enhanced_context
            )
            
            feedback_prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "feedback",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                student_markdown=student_markdown,
                student_code_summary=student_code[:800],
                rubric_criteria=rubric_summary,
                validation_context=enhanced_context
            )
            
            try:
                result = self.distributed_client.generate_parallel_sync(code_prompt, feedback_prompt)
                
                if result.get('error'):
                    raise RuntimeError(f"Distributed MLX generation failed: {result['error']}")
                
                # Parse the responses
                code_analysis = self._parse_code_analysis_response(result['code_analysis'])
                comprehensive_feedback = self._parse_feedback_response(result['feedback'])
                
                # Update timing stats with detailed metrics
                self.grading_stats['code_analysis_time'] = result.get('qwen_time', 0)
                self.grading_stats['feedback_generation_time'] = result.get('gemma_time', 0)
                
                # Extract detailed performance metrics if available
                if 'qwen_metrics' in result:
                    qwen_metrics = result['qwen_metrics']
                    self.grading_stats['qwen_tokens_per_second'] = qwen_metrics.get('tokens_per_second', 0)
                    self.grading_stats['qwen_total_tokens'] = qwen_metrics.get('total_tokens', 0)
                    self.grading_stats['qwen_prompt_eval_time'] = qwen_metrics.get('prompt_eval_time', 0)
                
                if 'gemma_metrics' in result:
                    gemma_metrics = result['gemma_metrics']
                    self.grading_stats['gemma_tokens_per_second'] = gemma_metrics.get('tokens_per_second', 0)
                    self.grading_stats['gemma_total_tokens'] = gemma_metrics.get('total_tokens', 0)
                    self.grading_stats['gemma_prompt_eval_time'] = gemma_metrics.get('prompt_eval_time', 0)
                
                # Store parallel efficiency
                if 'parallel_efficiency' in result:
                    self.grading_stats['parallel_efficiency'] = result['parallel_efficiency']
                
                print(f"✅ AI analysis completed")
                print(f"   🔧 Qwen: {result.get('qwen_time', 0):.1f}s")
                print(f"   📝 GPT-OSS: {result.get('gemma_time', 0):.1f}s")
                
            except Exception as e:
                print(f"⚠️ AI analysis failed: {e}")
                print("📝 Using validation-only feedback")
                code_analysis = None
                comprehensive_feedback = None
        else:
            # Use Ollama system (fallback to original grader methods)
            print("🤖 Using Ollama for AI analysis...")
            try:
                from business_analytics_grader import BusinessAnalyticsGrader
                temp_grader = BusinessAnalyticsGrader()
                
                # Submit both tasks simultaneously
                future_code = self.executor.submit(
                    temp_grader._execute_business_code_analysis, 
                    student_code, template_code, solution_code, assignment_info
                )
                
                future_feedback = self.executor.submit(
                    temp_grader._execute_business_feedback_generation,
                    student_code, student_markdown, assignment_info
                )
                
                # Wait for both results
                code_analysis = future_code.result()
                comprehensive_feedback = future_feedback.result()
                
                print(f"✅ AI analysis completed")
                
            except Exception as e:
                print(f"⚠️ AI analysis failed: {e}")
                print("📝 Using validation-only feedback")
                code_analysis = None
                comprehensive_feedback = None
        
        parallel_time = time.time() - parallel_start
        self.grading_stats['parallel_time'] = parallel_time
        
        # Merge AI feedback with validation results
        if code_analysis and comprehensive_feedback:
            structured_feedback = self._merge_ai_and_validation_feedback(
                validation_results, code_analysis, comprehensive_feedback
            )
        else:
            # Fallback to validation-only feedback
            structured_feedback = self._create_structured_feedback_from_validation(validation_results)
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        print(f"\n✅ Grading completed in {total_time:.1f}s")
        
        return structured_feedback
    
    def _create_structured_feedback_from_validation(self, validation_results: Dict) -> Dict[str, Any]:
        """
        Create structured feedback from validation results
        Maintains the standard feedback format
        """
        
        sys_result = validation_results['systematic_results']
        output_result = validation_results.get('output_results')
        
        # Calculate scores
        final_score = validation_results['adjusted_score']
        final_score_37_5 = (final_score / 100) * 37.5
        
        # Build code strengths from completed sections
        code_strengths = []
        for section_id, section_data in sys_result['section_breakdown'].items():
            if section_data['status'] == 'complete':
                # Handle both old and new validator formats
                points_earned = section_data.get('points_earned', section_data.get('score', 0))
                points_possible = section_data.get('points_possible', section_data.get('points', 0))
                code_strengths.append(f"✅ Completed {section_data['name']} ({points_earned:.1f}/{points_possible} points)")
        
        if not code_strengths:
            code_strengths = ["Submission received and processed"]
        
        # Build code suggestions from incomplete sections
        code_suggestions = []
        for section_id, section_data in sys_result['section_breakdown'].items():
            if section_data['status'] == 'incomplete':
                points_possible = section_data.get('points_possible', section_data.get('points', 0))
                code_suggestions.append(
                    f"• WHAT: Complete {section_data['name']}\n"
                    f"  WHY: This section is worth {points_possible} points and tests key learning objectives\n"
                    f"  HOW: Implement the required code as specified in the assignment instructions\n"
                    f"  EXAMPLE: See the solution notebook for reference implementation"
                )
        
        # Build technical observations
        complete_sections = sum(1 for s in sys_result['section_breakdown'].values() if s['status'] == 'complete')
        total_sections = len(sys_result['section_breakdown'])
        completion_pct = (complete_sections / total_sections * 100) if total_sections > 0 else 0
        
        technical_observations = [
            f"Completion: {complete_sections} out of {total_sections} sections ({completion_pct:.0f}%). Calculated score: {final_score:.0f}%.",
            f"Variables found: {sys_result['variable_check']['found']}/{sys_result['variable_check']['total_required']}",
            f"Execution rate: {sys_result['cell_stats']['execution_rate']*100:.1f}%"
        ]
        
        if output_result:
            technical_observations.append(
                f"Output accuracy: {output_result['overall_match']*100:.1f}% ({output_result['passed_checks']}/{output_result['total_checks']} checks passed)"
            )
        
        # Build comprehensive feedback
        instructor_comments = self._generate_instructor_comments(validation_results)
        
        # Calculate component scores for backward compatibility
        # Use default weights: Technical 40%, Analysis 40%, Business 10%, Communication 10%
        technical_points = (final_score / 100) * (37.5 * 0.40)
        analysis_points = (final_score / 100) * (37.5 * 0.40)
        business_points = (final_score / 100) * (37.5 * 0.10)
        communication_points = (final_score / 100) * (37.5 * 0.10)
        
        return {
            "final_score": round(final_score_37_5, 1),
            "final_score_percentage": round(final_score, 1),
            "max_points": 37.5,
            "component_scores": {
                "technical_points": round(technical_points, 1),
                "business_points": round(business_points, 1),
                "analysis_points": round(analysis_points, 1),
                "communication_points": round(communication_points, 1),
                "bonus_points": 0.0
            },
            "component_percentages": {
                "technical_score": final_score,
                "business_understanding": final_score,
                "data_interpretation": final_score,
                "communication_clarity": final_score
            },
            "technical_analysis": {
                "code_strengths": code_strengths[:10],  # Limit to 10
                "code_suggestions": code_suggestions[:10],  # Limit to 10
                "technical_observations": technical_observations
            },
            "comprehensive_feedback": {
                "instructor_comments": instructor_comments,
                "detailed_feedback": {
                    "reflection_assessment": [
                        "Submission processed through systematic validation",
                        "Review feedback carefully to understand areas for improvement"
                    ],
                    "analytical_strengths": code_strengths[:5],  # Top 5
                    "business_application": [
                        "Assignment demonstrates understanding of data analysis workflow",
                        "Continue developing analytical skills through practice"
                    ],
                    "areas_for_development": code_suggestions[:5],  # Top 5
                    "recommendations": [
                        "Focus on completing all required sections of the assignment",
                        "Verify your outputs match expected results",
                        "Review solution notebook for reference implementations"
                    ]
                }
            },
            "validation_results": validation_results,
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "grading_system": "4-Layer Validation + AI Analysis",
            "grading_stats": self.grading_stats
        }
    
    def _merge_ai_and_validation_feedback(self, validation_results: Dict, 
                                          code_analysis: Dict, 
                                          comprehensive_feedback: Dict) -> Dict[str, Any]:
        """Merge AI-generated feedback with validation results"""
        
        sys_result = validation_results['systematic_results']
        output_result = validation_results.get('output_results')
        
        # Use validation score as base
        final_score = validation_results['adjusted_score']
        final_score_37_5 = (final_score / 100) * 37.5
        
        # Calculate component scores
        technical_points = (final_score / 100) * (37.5 * 0.40)
        analysis_points = (final_score / 100) * (37.5 * 0.40)
        business_points = (final_score / 100) * (37.5 * 0.10)
        communication_points = (final_score / 100) * (37.5 * 0.10)
        
        # Merge code strengths from AI and validation
        code_strengths = []
        if code_analysis.get('code_strengths'):
            code_strengths.extend(code_analysis['code_strengths'])
        
        # Add validation-based strengths
        for section_id, section_data in sys_result['section_breakdown'].items():
            if section_data['status'] == 'complete':
                # Handle both old and new validator formats
                points_earned = section_data.get('points_earned', section_data.get('score', 0))
                points_possible = section_data.get('points_possible', section_data.get('points', 0))
                code_strengths.append(f"✅ Completed {section_data['name']} ({points_earned:.1f}/{points_possible} points)")
        
        # Merge code suggestions from AI and validation
        code_suggestions = []
        if code_analysis.get('code_suggestions'):
            code_suggestions.extend(code_analysis['code_suggestions'])
        
        # Add validation-based suggestions
        for section_id, section_data in sys_result['section_breakdown'].items():
            if section_data['status'] == 'incomplete':
                points_possible = section_data.get('points_possible', section_data.get('points', 0))
                code_suggestions.append(
                    f"• WHAT: Complete {section_data['name']}\n"
                    f"  WHY: This section is worth {points_possible} points\n"
                    f"  HOW: Implement the required code as specified\n"
                    f"  EXAMPLE: See solution notebook for reference"
                )
        
        # Build technical observations
        complete_sections = sum(1 for s in sys_result['section_breakdown'].values() if s['status'] == 'complete')
        total_sections = len(sys_result['section_breakdown'])
        
        technical_observations = []
        if code_analysis.get('technical_observations'):
            technical_observations.extend(code_analysis['technical_observations'])
        
        section_pct = (complete_sections/total_sections*100) if total_sections > 0 else 0
        technical_observations.append(
            f"Completion: {complete_sections}/{total_sections} sections ({section_pct:.0f}%). Score: {final_score:.0f}%"
        )
        technical_observations.append(f"Variables found: {sys_result['variable_check']['found']}/{sys_result['variable_check']['total_required']}")
        
        if output_result:
            technical_observations.append(
                f"Output accuracy: {output_result['overall_match']*100:.1f}% ({output_result['passed_checks']}/{output_result['total_checks']} checks passed)"
            )
        
        # Use AI-generated comprehensive feedback but enhance with validation context
        detailed_feedback = comprehensive_feedback.get('detailed_feedback', {})
        
        # Enhance reflection assessment with validation info
        reflection = detailed_feedback.get('reflection_assessment', [])
        if not reflection:
            reflection = [
                f"Completed {complete_sections}/{total_sections} required sections",
                "Review feedback carefully to understand areas for improvement"
            ]
        
        # Use AI analytical strengths but add validation strengths
        analytical_strengths = detailed_feedback.get('analytical_strengths', [])
        if not analytical_strengths:
            analytical_strengths = code_strengths[:5]
        
        # Use AI business application
        business_application = detailed_feedback.get('business_application', [
            "Assignment demonstrates understanding of data analysis workflow",
            "Continue developing analytical skills through practice"
        ])
        
        # Use AI areas for development but add validation-based ones
        areas_for_development = detailed_feedback.get('areas_for_development', [])
        if not areas_for_development and code_suggestions:
            areas_for_development = code_suggestions[:5]
        
        # Use AI recommendations
        recommendations = detailed_feedback.get('recommendations', [
            "Focus on completing all required sections",
            "Verify outputs match expected results",
            "Review solution notebook for reference"
        ])
        
        # Use AI instructor comments or generate from validation
        instructor_comments = comprehensive_feedback.get('instructor_comments')
        if not instructor_comments:
            instructor_comments = self._generate_instructor_comments(validation_results)
        
        return {
            "final_score": round(final_score_37_5, 1),
            "final_score_percentage": round(final_score, 1),
            "max_points": 37.5,
            "component_scores": {
                "technical_points": round(technical_points, 1),
                "business_points": round(business_points, 1),
                "analysis_points": round(analysis_points, 1),
                "communication_points": round(communication_points, 1),
                "bonus_points": 0.0
            },
            "component_percentages": {
                "technical_score": final_score,
                "business_understanding": final_score,
                "data_interpretation": final_score,
                "communication_clarity": final_score
            },
            "technical_analysis": {
                "code_strengths": code_strengths[:10],
                "code_suggestions": code_suggestions[:10],
                "technical_observations": technical_observations
            },
            "comprehensive_feedback": {
                "instructor_comments": instructor_comments,
                "detailed_feedback": {
                    "reflection_assessment": reflection,
                    "analytical_strengths": analytical_strengths[:5],
                    "business_application": business_application,
                    "areas_for_development": areas_for_development[:5],
                    "recommendations": recommendations
                }
            },
            "validation_results": validation_results,
            "grading_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "grading_system": "4-Layer Validation + AI Analysis",
            "grading_stats": self.grading_stats
        }
    
    def _identify_student_changes(self, student_code: str, template_code: str, solution_code: str) -> Dict[str, Any]:
        """
        Identify what code the student actually wrote vs what was in the template.
        This helps the AI focus on student work and not penalize template code.
        """
        
        # Split into lines for comparison
        student_lines = student_code.split('\n')
        template_lines = template_code.split('\n') if template_code else []
        solution_lines = solution_code.split('\n') if solution_code else []
        
        # Identify student-written code
        student_written = []
        template_unchanged = []
        
        # Simple line-by-line comparison
        template_set = set(template_lines)
        
        for line in student_lines:
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Skip TODO markers
            if 'TODO' in stripped.upper() or 'YOUR CODE HERE' in stripped.upper():
                continue
            
            # Check if this line was in the template
            if line in template_set:
                template_unchanged.append(line)
            else:
                # This is student-written code
                student_written.append(line)
        
        # Build a summary for the AI
        changes_summary = {
            'student_written_lines': len(student_written),
            'template_unchanged_lines': len(template_unchanged),
            'student_code_only': '\n'.join(student_written),
            'has_template': bool(template_code),
            'has_solution': bool(solution_code)
        }
        
        # Create enhanced context for AI
        context = f"""
IMPORTANT GRADING CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TEMPLATE vs STUDENT CODE ANALYSIS:
- Template provided: {'Yes' if template_code else 'No'}
- Student wrote: {len(student_written)} lines of new code
- Template unchanged: {len(template_unchanged)} lines

🎯 GRADING RULES - CRITICAL:
1. ONLY evaluate code the STUDENT wrote (not template code)
2. IGNORE all TODO comments and placeholder comments
3. IGNORE commented-out code
4. Compare STUDENT code to SOLUTION code (not template)
5. If student used template code correctly, that's GOOD (not bad)

🔬 OUTPUT VALIDATION RULES - MOST IMPORTANT:
1. IF OUTPUT MATCHES SOLUTION → Student's approach is CORRECT (even if different variable names)
2. IF OUTPUT MATCHES → DO NOT penalize for different variable names or code style
3. IF OUTPUT MATCHES → DO NOT suggest "fixing" working code
4. ONLY flag issues when OUTPUT DOES NOT MATCH or is MISSING
5. Different approach with same result = GOOD, not bad!

EXAMPLES:
✅ CORRECT: Student used "my_analysis" instead of "customer_metrics" but output matches → FULL CREDIT
✅ CORRECT: Student used different grouping order but got same result → FULL CREDIT
❌ WRONG: Student used inner_join instead of full_join and output has wrong row count → DEDUCT POINTS

⚠️ COMMON MISTAKES TO AVOID:
- DO NOT penalize students for template code they didn't write
- DO NOT suggest fixing code that was already correct in template
- DO NOT count TODO comments as missing work if code is present
- DO NOT flag issues in commented-out code
- DO NOT penalize for different variable names if outputs match
- DO NOT penalize for different code style if outputs match
- DO NOT suggest "missing variables" if the work was done with different names

✅ WHAT TO FOCUS ON:
- Code the student actually wrote
- OUTPUT ACCURACY (does it match solution?)
- Logic errors that cause WRONG outputs
- Missing required functionality (not missing variable names)
- Incorrect use of R functions that cause WRONG results

🚨 PRIORITY ORDER:
1. Output correctness (most important)
2. Logic correctness
3. Code quality
4. Variable naming (least important)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        changes_summary['ai_context'] = context
        
        return changes_summary
    
    def _generate_instructor_comments(self, validation_results: Dict) -> str:
        """Generate instructor comments from validation results"""
        
        sys_result = validation_results['systematic_results']
        output_result = validation_results.get('output_results')
        
        complete_sections = sum(1 for s in sys_result['section_breakdown'].values() if s['status'] == 'complete')
        total_sections = len(sys_result['section_breakdown'])
        completion_pct = (complete_sections / total_sections * 100) if total_sections > 0 else 0
        
        score = validation_results['adjusted_score']
        
        if score >= 90:
            tone = "Excellent work!"
        elif score >= 80:
            tone = "Good work overall."
        elif score >= 70:
            tone = "Satisfactory effort."
        else:
            tone = "Your submission shows partial completion."
        
        comments = f"{tone} You completed {complete_sections} out of {total_sections} sections ({completion_pct:.0f}%). "
        
        if output_result:
            match_rate = output_result['overall_match'] * 100
            if match_rate >= 90:
                comments += f"Your outputs are highly accurate ({match_rate:.0f}% match with solution). "
            elif match_rate >= 70:
                comments += f"Most of your outputs are correct ({match_rate:.0f}% match), but some discrepancies were found. "
            else:
                comments += f"Several output discrepancies were detected ({match_rate:.0f}% match). Review the feedback to identify areas for correction. "
        
        if sys_result['variable_check']['missing']:
            comments += f"Note: {len(sys_result['variable_check']['missing'])} required variables are missing. "
        
        comments += "Review the detailed feedback below for specific areas to improve."
        
        return comments
    
    def _execute_ollama_code_analysis(self, student_code: str, template_code: str, 
                                     solution_code: str, assignment_info: Dict) -> Dict[str, Any]:
        """Execute code analysis using Ollama"""
        start_time = time.time()
        
        print(f"🔧 [CODE] Analyzing with Ollama...")
        
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        prompt = self.prompt_manager.get_combined_prompt(
            assignment_name,
            "code_analysis",
            assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
            template_code=template_code if template_code else "# No template provided",
            student_code=student_code,
            solution_code=solution_code
        )
        
        response = self._generate_with_ollama(self.code_model, prompt, max_tokens=1500)
        
        analysis_time = time.time() - start_time
        self.grading_stats['code_analysis_time'] = analysis_time
        
        print(f"✅ [CODE] Analysis complete ({analysis_time:.1f}s)")
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 85}
        
        return self._parse_code_analysis_response(response)
    
    def _execute_ollama_feedback_generation(self, student_code: str, student_markdown: str,
                                           assignment_info: Dict) -> Dict[str, Any]:
        """Execute feedback generation using Ollama"""
        start_time = time.time()
        
        print(f"📝 [FEEDBACK] Generating with Ollama...")
        
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        prompt = self.prompt_manager.get_combined_prompt(
            assignment_name,
            "feedback",
            assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
            student_markdown=student_markdown,
            student_code_summary=student_code[:800]
        )
        
        response = self._generate_with_ollama(self.feedback_model, prompt, max_tokens=2000)
        
        feedback_time = time.time() - start_time
        self.grading_stats['feedback_generation_time'] = feedback_time
        
        print(f"✅ [FEEDBACK] Generation complete ({feedback_time:.1f}s)")
        
        if not response:
            return {"error": "Feedback generation failed", "overall_score": 85}
        
        return self._parse_feedback_response(response)
    
    def _generate_with_ollama(self, model: str, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Generate response using Ollama (direct or disaggregated) and capture metrics"""
        try:
            # Use disaggregated system if available
            if self.use_disaggregated and self.disaggregated_client:
                response_text, metrics = self.disaggregated_client.generate(model, prompt, max_tokens)
                
                # Store metrics for display
                model_key = 'qwen' if 'qwen' in model.lower() or 'coder' in model.lower() else 'gemma'
                self.grading_stats[f'{model_key}_metrics'] = {
                    'prefill_tokens_per_second': metrics.get('prefill_speed', 0),
                    'decode_tokens_per_second': metrics.get('decode_speed', 0),
                    'prompt_tokens': metrics.get('prompt_tokens', 0),
                    'completion_tokens': metrics.get('completion_tokens', 0),
                    'total_tokens': metrics.get('total_tokens', 0),
                    'prefill_time': metrics.get('prefill_time', 0),
                    'decode_time': metrics.get('decode_time', 0),
                    'total_time': metrics.get('total_time', 0),
                    'method': 'disaggregated',
                    'prefill_server': metrics.get('prefill_server', ''),
                    'decode_server': metrics.get('decode_server', '')
                }
                return response_text
            
            # Fallback to direct Ollama
            # Determine which server to use based on model
            if 'qwen' in model.lower() or 'coder' in model.lower():
                server_url = self.qwen_server
            else:
                server_url = self.gptoss_server
            
            api_url = f"{server_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(api_url, json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                
                # Capture performance metrics
                if 'prompt_eval_count' in result or 'eval_count' in result:
                    metrics = {
                        'prompt_tokens': result.get('prompt_eval_count', 0),
                        'completion_tokens': result.get('eval_count', 0),
                        'total_tokens': result.get('prompt_eval_count', 0) + result.get('eval_count', 0),
                        'prompt_eval_duration_ms': result.get('prompt_eval_duration', 0) / 1_000_000,
                        'eval_duration_ms': result.get('eval_duration', 0) / 1_000_000,
                        'total_duration_ms': result.get('total_duration', 0) / 1_000_000,
                        'method': 'direct_ollama'
                    }
                    
                    # Calculate tokens per second
                    if metrics['eval_duration_ms'] > 0:
                        metrics['decode_tokens_per_second'] = (metrics['completion_tokens'] / metrics['eval_duration_ms']) * 1000
                    else:
                        metrics['decode_tokens_per_second'] = 0
                    
                    if metrics['prompt_eval_duration_ms'] > 0:
                        metrics['prefill_tokens_per_second'] = (metrics['prompt_tokens'] / metrics['prompt_eval_duration_ms']) * 1000
                    else:
                        metrics['prefill_tokens_per_second'] = 0
                    
                    # Store metrics
                    model_key = 'qwen' if 'qwen' in model.lower() or 'coder' in model.lower() else 'gemma'
                    self.grading_stats[f'{model_key}_metrics'] = metrics
                
                return result.get('response', '')
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_code_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse code analysis response"""
        try:
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
        except:
            pass
        
        # Fallback parsing
        return {
            "technical_score": 85,
            "code_strengths": ["Code analysis completed"],
            "code_suggestions": ["Review feedback for details"],
            "technical_observations": [response[:200]]
        }
    
    def _parse_feedback_response(self, response: str) -> Dict[str, Any]:
        """Parse feedback response"""
        try:
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
        except:
            pass
        
        # Fallback parsing
        return {
            "overall_score": 85,
            "instructor_comments": response[:500] if response else "Feedback generated",
            "detailed_feedback": {
                "reflection_assessment": ["Review submission"],
                "analytical_strengths": ["Analysis completed"],
                "business_application": ["Business context considered"],
                "areas_for_development": ["See detailed feedback"],
                "recommendations": ["Continue practicing"]
            }
        }


# Convenience function
def create_business_grader_v2(code_model: str = None, 
                              feedback_model: str = None,
                              rubric_path: str = None,
                              solution_path: str = None) -> BusinessAnalyticsGraderV2:
    """Create an enhanced business analytics grader instance"""
    return BusinessAnalyticsGraderV2(code_model, feedback_model, rubric_path=rubric_path, solution_path=solution_path)
