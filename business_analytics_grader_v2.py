#!/usr/bin/env python3
"""
Business Analytics Grading System V2
Integrates 4-layer validation system with structured feedback generation
"""

print("🔄 LOADING business_analytics_grader_v2.py - CODE UPDATED")

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

# Import validators
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
        
        self.code_model = code_model
        self.feedback_model = feedback_model
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        self.solution_path = solution_path  # Store for output comparison
        self.rubric_path = rubric_path  # Store for reflection grading
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager()
        
        # Initialize validators
        self.systematic_validator = None
        self.output_validator = None
        self.max_points = 37.5  # Default for homework assignments
        
        if rubric_path and os.path.exists(rubric_path):
            print(f"📋 Loading systematic validator with rubric: {rubric_path}")
            
            # Load rubric to get total_points
            try:
                with open(rubric_path, 'r') as f:
                    rubric_data = json.load(f)
                    self.max_points = rubric_data.get('assignment_info', {}).get('total_points', 37.5)
                    print(f"📊 Assignment max points: {self.max_points}")
            except Exception as e:
                print(f"⚠️ Could not read total_points from rubric: {e}")
                self.max_points = 37.5
            
            # Use rubric-driven validator (works for any assignment with autograder_checks)
            try:
                self.systematic_validator = RubricDrivenValidator(rubric_path)
                print(f"✅ Using RubricDrivenValidator")
            except (ValueError, KeyError) as e:
                # Rubric must have autograder_checks section
                raise ValueError(f"Rubric missing required 'autograder_checks' section: {e}")
            except Exception as e:
                print(f"❌ Error loading RubricDrivenValidator: {e}")
                import traceback
                traceback.print_exc()
                raise
            
            if solution_path and os.path.exists(solution_path):
                print(f"📊 Loading output validator with solution: {solution_path}")
                self.output_validator = SmartOutputValidator(solution_path, rubric_path)
            else:
                print(f"⚠️ No solution path provided, output validation disabled")
        else:
            raise ValueError("Rubric path is required - cannot grade without a rubric")
        
        # Check for disaggregated inference system (DGX prefill + Mac decode)
        self.use_disaggregated = False
        self.disaggregated_client = None
        
        if os.path.exists('disaggregated_inference/config_current.json'):
            try:
                from disaggregated_client import DisaggregatedClient
                self.disaggregated_client = DisaggregatedClient()
                self.use_disaggregated = True
                print(f"🚀 Using Disaggregated Inference System:")
                print(f"   DGX Sparks (prefill) + Mac Studios (decode)")
                print(f"   Qwen: DGX Spark 1 → Mac Studio 2")
                print(f"   GPT-OSS: DGX Spark 2 → Mac Studio 1")
            except Exception as e:
                print(f"⚠️ Disaggregated system failed to load: {e}")
                import traceback
                traceback.print_exc()
                self.use_disaggregated = False
        
        # Check for distributed MLX system (fallback)
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
        
        # LAYER 2: Output Comparison (cell-by-cell)
        output_result = None
        if self.solution_path and os.path.exists(self.solution_path):
            print(f"\n[LAYER 2: OUTPUT COMPARISON]")
            print("-"*80)
            try:
                from output_comparator import OutputComparator
                print(f"🔍 Comparing: {notebook_path}")
                print(f"🔍 Against: {self.solution_path}")
                comparator = OutputComparator(notebook_path, self.solution_path)
                comparison = comparator.compare_outputs()
                print(f"🔍 Raw comparison result: matches={comparison.get('matches')}, total={comparison.get('total_comparisons')}")
                
                # Convert to format expected by rest of system
                match_rate = comparison['match_rate'] / 100  # Convert to 0-1
                
                # Calculate output score as percentage (0-100)
                output_score = comparison['match_rate']  # Already a percentage
                
                output_result = {
                    'overall_match': match_rate,
                    'total_checks': comparison['total_comparisons'],
                    'passed_checks': comparison['matches'],
                    'discrepancies': [c for c in comparison['comparisons'] if not c['match']],
                    'output_score': output_score,  # Store as percentage for merging
                    'score_adjustment': 0  # Deprecated - use output_score instead
                }
                
                print(f"✅ Output Match: {comparison['match_rate']:.1f}%")
                print(f"✅ Cells Matched: {comparison['matches']}/{comparison['total_comparisons']}")
                print(f"✅ Accuracy Score: {comparison['accuracy_score']:.1f}%")
                
                mismatches = [c for c in comparison['comparisons'] if not c['match']]
                if mismatches:
                    print(f"\nMismatched Cells: {len(mismatches)}")
                    for i, cell in enumerate(mismatches[:3]):  # Show first 3
                        print(f"  ❌ Cell {cell['cell_index']}: {cell['reason'][:60]}")
            except Exception as e:
                print(f"⚠️ Output comparison failed: {e}")
                output_result = None
        
        # LAYER 2.5: Reflection Grading (if applicable)
        reflection_grading = None
        if self.solution_path and os.path.exists(self.solution_path):
            try:
                from reflection_extractor import ReflectionExtractor
                from reflection_grader import ReflectionGrader
                
                # Check if there's a reflection section in the rubric
                has_reflection_section = False
                for section_id, section_data in sys_result.get('section_breakdown', {}).items():
                    if 'reflection' in section_data.get('name', '').lower():
                        has_reflection_section = True
                        break
                
                if has_reflection_section:
                    print(f"\n[LAYER 2.5: REFLECTION GRADING]")
                    print("-"*80)
                    
                    grader = ReflectionGrader(self.ollama_url)
                    
                    # Get max points for reflections from rubric
                    reflection_max_points = 5.0  # Default
                    try:
                        with open(self.rubric_path if hasattr(self, 'rubric_path') else '', 'r') as f:
                            rubric = json.load(f)
                            sections = rubric.get('autograder_checks', {}).get('sections', {})
                            
                            # Find the reflection section
                            for section_id, section_data in sections.items():
                                if section_data.get('check_type') == 'markdown' or 'reflection' in section_data.get('name', '').lower():
                                    reflection_max_points = section_data.get('points', 5.0)
                                    print(f"   Found reflection section: {section_data.get('name')} ({reflection_max_points} points)")
                                    break
                    except Exception as e:
                        print(f"   Using default reflection points: {reflection_max_points}")
                    
                    reflection_grading = grader.grade_reflections(notebook_path, self.solution_path, reflection_max_points)
                    
                    print(f"✅ Reflection Score: {reflection_grading['reflection_score']:.1f}/{reflection_max_points}")
                    print(f"✅ Reflection Quality: {reflection_grading['reflection_percentage']:.0f}%")
                    
            except Exception as e:
                print(f"⚠️ Could not grade reflections: {e}")
                import traceback
                traceback.print_exc()
                reflection_grading = None
        
        validation_time = time.time() - validation_start
        self.grading_stats['validation_time'] = validation_time
        
        print(f"\n⏱️ Validation completed in {validation_time:.1f}s")
        print("="*80 + "\n")
        
        # Merge results
        return self._merge_validation_results(sys_result, output_result, reflection_grading)
    
    def _merge_validation_results(self, sys_result: Dict, output_result: Optional[Dict], 
                                  reflection_grading: Optional[Dict] = None) -> Dict[str, Any]:
        """Merge systematic, output, and reflection validation into comprehensive results"""
        
        # Calculate adjusted score by combining systematic and output scores
        base_score = sys_result['final_score']
        
        # If we have AI-graded reflections, replace the simple completion score
        if reflection_grading:
            # Find the reflection section (could be any part number)
            reflection_section_id = None
            for section_id, section_data in sys_result.get('section_breakdown', {}).items():
                # Check if this section is marked as reflection type
                if 'reflection' in section_data.get('name', '').lower():
                    reflection_section_id = section_id
                    break
            
            if reflection_section_id:
                # Get the reflection section
                reflection_section = sys_result['section_breakdown'][reflection_section_id]
                old_score = reflection_section.get('score', 0)
                new_score = reflection_grading['reflection_score']
                
                # Update the section score
                reflection_section['score'] = new_score
                reflection_section['ai_graded'] = True
                reflection_section['reflection_percentage'] = reflection_grading['reflection_percentage']
                
                # Recalculate base_score with new reflection score
                total_section_points = sum(s.get('points', 0) for s in sys_result['section_breakdown'].values())
                earned_section_points = sum(s.get('score', 0) for s in sys_result['section_breakdown'].values())
                
                if total_section_points > 0:
                    section_score = (earned_section_points / total_section_points * 100)
                else:
                    section_score = 0
                
                # Recalculate base score (80% sections, 20% variables)
                variable_score = sys_result['variable_check']['completion_rate'] * 100
                base_score = (section_score * 0.8) + (variable_score * 0.2)
                
                section_name = reflection_section.get('name', 'Reflection Section')
                print(f"\n🎯 REFLECTION ADJUSTMENT:")
                print(f"  Section: {section_name}")
                print(f"  Old score: {old_score:.1f} (completion-based)")
                print(f"  New score: {new_score:.1f} (AI-graded quality)")
                print(f"  Adjusted base score: {base_score:.1f}%")
            else:
                print(f"\n⚠️ Reflection grading available but no reflection section found in rubric")
        
        if output_result and output_result.get('total_checks', 0) > 0:
            # We have output comparison results - blend the scores
            output_score = output_result.get('output_score', 0)
            
            print(f"🔍 SCORE MERGE:")
            print(f"  Base score (systematic): {base_score:.1f}%")
            print(f"  Output score (comparison): {output_score:.1f}%")
            
            # Weighted blend: 50% systematic, 50% output accuracy
            # This ensures both code structure AND correct outputs matter
            adjusted_score = (base_score * 0.5) + (output_score * 0.5)
            
            print(f"  Adjusted score (50/50 blend): {adjusted_score:.1f}%")
        else:
            # No output validation or it failed - use base score only
            adjusted_score = base_score
            print(f"🔍 SCORE: Using base score only: {adjusted_score:.1f}%")
        
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
                # Handle both SmartOutputValidator format (variable/issue) and OutputComparator format (cell_index/reason)
                if 'variable' in disc:
                    issues.append(f"Output mismatch for {disc['variable']}: {disc['issue']}")
                elif 'cell_index' in disc:
                    issues.append(f"Cell {disc['cell_index']} output mismatch: {disc.get('reason', 'differs from solution')}")
        
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
        if not self.systematic_validator:
            raise ValueError("No systematic validator available - rubric is required for grading")
        if not notebook_path:
            raise ValueError("Notebook path is required for grading")
        
        validation_results = self._run_4layer_validation(notebook_path)
        
        # Layer 3 & 4: AI Code Analysis and Feedback Generation
        print("\n[LAYER 3 & 4: AI ANALYSIS AND FEEDBACK GENERATION]")
        print("-"*80)
        
        # Identify what code the student actually wrote (vs template)
        student_changes = self._identify_student_changes(student_code, template_code, solution_code)
        
        # Extract reflection questions for AI context (already graded in validation)
        reflection_comparison = ""
        if self.solution_path and os.path.exists(self.solution_path):
            try:
                from reflection_extractor import ReflectionExtractor
                extractor = ReflectionExtractor(notebook_path, self.solution_path)
                reflection_comparison = extractor.generate_ai_prompt_section()
            except Exception as e:
                print(f"⚠️ Could not extract reflections for AI context: {e}")
                reflection_comparison = ""
        
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
            
            # Build enhanced context with student changes analysis and reflections
            enhanced_context = f"{student_changes['ai_context']}\n\n{validation_summary}"
            if reflection_comparison:
                enhanced_context += f"\n\n{reflection_comparison}"
            
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
                validation_context=enhanced_context,
                reflection_comparison=reflection_comparison
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
            # Use Ollama system (fallback)
            print("🤖 Using Ollama for AI analysis...")
            try:
                # Add reflection comparison to validation results for Ollama
                if reflection_comparison:
                    validation_results['reflection_comparison'] = reflection_comparison
                
                # Submit both tasks simultaneously with validation context
                future_code = self.executor.submit(
                    self._execute_ollama_code_analysis, 
                    student_code, template_code, solution_code, assignment_info, validation_results
                )
                
                future_feedback = self.executor.submit(
                    self._execute_ollama_feedback_generation,
                    student_code, student_markdown, assignment_info, validation_results
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
            print(f"📦 AFTER MERGE: structured_feedback['final_score'] = {structured_feedback.get('final_score', 'NOT SET')}")
        else:
            # Fallback to validation-only feedback
            structured_feedback = self._create_structured_feedback_from_validation(validation_results)
            print(f"📦 FALLBACK: structured_feedback['final_score'] = {structured_feedback.get('final_score', 'NOT SET')}")
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        # Add performance diagnostics if using disaggregated system
        if self.use_disaggregated and 'qwen_metrics' in self.grading_stats and 'gemma_metrics' in self.grading_stats:
            qwen_m = self.grading_stats['qwen_metrics']
            gemma_m = self.grading_stats['gemma_metrics']
            
            structured_feedback['performance_diagnostics'] = {
                'qwen_performance': {
                    'tokens_per_second': qwen_m.get('decode_speed', 0),
                    'generation_time_seconds': self.grading_stats.get('code_analysis_time', 0),
                    'model': 'Disaggregated (DGX+Mac)'
                },
                'gemma_performance': {
                    'tokens_per_second': gemma_m.get('decode_speed', 0),
                    'generation_time_seconds': self.grading_stats.get('feedback_generation_time', 0),
                    'model': 'Disaggregated (DGX+Mac)'
                },
                'combined_metrics': {
                    'parallel_efficiency': self.grading_stats.get('parallel_efficiency', 0),
                    'combined_throughput_tokens_per_second': (
                        qwen_m.get('completion_tokens', 0) + gemma_m.get('completion_tokens', 0)
                    ) / parallel_time if parallel_time > 0 else 0
                }
            }
            structured_feedback['grading_stats'] = self.grading_stats
        
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
        print(f"DEBUG: final_score (percentage) = {final_score}")
        print(f"DEBUG: self.max_points = {self.max_points}")
        final_score_points = (final_score / 100) * self.max_points
        print(f"DEBUG: final_score_points = {final_score_points}")
        
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
        
        # Calculate component scores for backward compatibility with explicit max caps
        # Use default weights: Technical 40%, Analysis 40%, Business 10%, Communication 10%
        technical_points = min((final_score / 100) * (self.max_points * 0.40), self.max_points * 0.40)
        analysis_points = min((final_score / 100) * (self.max_points * 0.40), self.max_points * 0.40)
        business_points = min((final_score / 100) * (self.max_points * 0.10), self.max_points * 0.10)
        communication_points = min((final_score / 100) * (self.max_points * 0.10), self.max_points * 0.10)
        
        return {
            "final_score": round(final_score_points, 1),
            "final_score_percentage": round(final_score, 1),
            "max_points": self.max_points,
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
        
        # Handle case where validation_results doesn't have systematic_results
        if 'systematic_results' not in validation_results:
            print("⚠️ Warning: validation_results missing 'systematic_results', using validation_results directly")
            sys_result = validation_results
            output_result = None
        else:
            sys_result = validation_results['systematic_results']
            output_result = validation_results.get('output_results')
        
        # Use validation score as base
        final_score = validation_results['adjusted_score']
        print(f"🔍 MERGE DEBUG: final_score (percentage) = {final_score}")
        print(f"🔍 MERGE DEBUG: self.max_points = {self.max_points}")
        final_score_points = (final_score / 100) * self.max_points
        print(f"🔍 MERGE DEBUG: final_score_points = {final_score_points}")
        
        # Calculate component scores with explicit max caps
        technical_points = min((final_score / 100) * (self.max_points * 0.40), self.max_points * 0.40)
        analysis_points = min((final_score / 100) * (self.max_points * 0.40), self.max_points * 0.40)
        business_points = min((final_score / 100) * (self.max_points * 0.10), self.max_points * 0.10)
        communication_points = min((final_score / 100) * (self.max_points * 0.10), self.max_points * 0.10)
        
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
            "final_score": round(final_score_points, 1),
            "final_score_percentage": round(final_score, 1),
            "max_points": self.max_points,
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
                                     solution_code: str, assignment_info: Dict, 
                                     validation_results: Dict = None) -> Dict[str, Any]:
        """Execute code analysis using Ollama"""
        start_time = time.time()
        
        print(f"🔧 [CODE] Analyzing with Ollama...")
        
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        
        # Use Ollama-specific prompts if using disaggregated
        if self.use_disaggregated:
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
            prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "code_analysis",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                template_code=template_code if template_code else "# No template provided",
                student_code=student_code,
                solution_code=solution_code
            )
        
        response = self._generate_with_ollama(self.code_model, prompt, max_tokens=3000)
        
        analysis_time = time.time() - start_time
        self.grading_stats['code_analysis_time'] = analysis_time
        
        print(f"✅ [CODE] Analysis complete ({analysis_time:.1f}s)")
        
        if not response:
            return {"error": "Code analysis failed", "technical_score": 85}
        
        return self._parse_code_analysis_response(response)
    
    def _execute_ollama_feedback_generation(self, student_code: str, student_markdown: str,
                                           assignment_info: Dict, validation_results: Dict = None) -> Dict[str, Any]:
        """Execute feedback generation using Ollama"""
        start_time = time.time()
        
        print(f"📝 [FEEDBACK] Generating with Ollama...")
        
        assignment_name = assignment_info.get('name', assignment_info.get('title', 'Unknown'))
        
        # Use Ollama-specific prompts if using disaggregated
        if self.use_disaggregated:
            prompt = self.prompt_manager.get_ollama_prompt(
                "feedback",
                validation_results=validation_results,
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                assignment_name=assignment_name,
                student_markdown=student_markdown,
                student_code_summary=student_code[:800]
            )
        else:
            prompt = self.prompt_manager.get_combined_prompt(
                assignment_name,
                "feedback",
                assignment_title=assignment_info.get('title', 'Business Analytics Assignment'),
                student_markdown=student_markdown,
                student_code_summary=student_code[:800]
            )
        
        response = self._generate_with_ollama(self.feedback_model, prompt, max_tokens=3500)
        
        feedback_time = time.time() - start_time
        self.grading_stats['feedback_generation_time'] = feedback_time
        
        print(f"✅ [FEEDBACK] Generation complete ({feedback_time:.1f}s)")
        
        if not response:
            return {"error": "Feedback generation failed", "overall_score": 85}
        
        return self._parse_feedback_response(response)
    
    def _generate_with_ollama(self, model: str, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Generate response using Ollama (disaggregated or local) and capture metrics"""
        try:
            # Use disaggregated system if available
            if self.use_disaggregated and self.disaggregated_client:
                response_text, metrics = self.disaggregated_client.generate(model, prompt, max_tokens)
                
                # Store metrics
                model_key = 'qwen' if 'qwen' in model.lower() or 'coder' in model.lower() else 'gpt-oss'
                self.grading_stats[f'{model_key}_metrics'] = metrics
                
                # Ollama sometimes echoes the prompt - remove it
                if response_text and response_text.startswith(prompt):
                    response_text = response_text[len(prompt):].strip()
                
                return response_text
            
            # Fallback to direct Ollama
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
            
            response = requests.post(self.api_url, json=payload, timeout=300)
            
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
            print(f"⚠️ Ollama generation failed: {e}")
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
