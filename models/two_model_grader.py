#!/usr/bin/env python3
"""
Two-Model Grading System Orchestrator
Coordinates Qwen 3.0 Coder (technical) + GPT-OSS-120B (feedback)
"""

import json
import time
from typing import Dict, List, Any, Optional
from code_analyzer import CodeAnalyzer
from feedback_generator import FeedbackGenerator

class TwoModelGrader:
    """Orchestrates two-model grading system for optimal results"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.feedback_generator = FeedbackGenerator()
        self.grading_stats = {
            'code_analysis_time': 0,
            'feedback_generation_time': 0,
            'total_time': 0
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
        Grade submission using two-model approach
        
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
        
        print("🚀 Starting Two-Model Grading System...")
        
        # Check if parallel processing is enabled
        from two_model_config import is_feature_enabled
        
        if is_feature_enabled('enable_parallel_processing'):
            try:
                print("⚡ Attempting parallel processing for maximum speed...")
                code_analysis, comprehensive_feedback = self._run_parallel_grading(
                    student_code, student_markdown, solution_code, assignment_info, rubric_elements
                )
            except Exception as parallel_error:
                print(f"⚠️ Parallel processing failed: {parallel_error}")
                print("🔄 Falling back to sequential processing...")
                code_analysis, comprehensive_feedback = self._run_sequential_grading(
                    student_code, student_markdown, solution_code, assignment_info, rubric_elements
                )
        else:
            print("🔄 Running models sequentially...")
            code_analysis, comprehensive_feedback = self._run_sequential_grading(
                student_code, student_markdown, solution_code, assignment_info, rubric_elements
            )
        
        # Phase 3: Merge and Finalize Results
        print("🔄 Phase 3: Merging Results...")
        
        final_result = self._merge_results(code_analysis, comprehensive_feedback, assignment_info)
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        final_result['grading_stats'] = self.grading_stats.copy()
        final_result['grading_method'] = 'two_model_system'
        
        print(f"🎉 Two-model grading complete! Total time: {total_time:.1f}s")
        
        return final_result
    
    def clear_memory(self):
        """Clear GPU memory to improve performance"""
        try:
            import gc
            import mlx.core as mx
            mx.clear_cache()
            gc.collect()
            print("🧹 GPU memory cleared")
        except Exception as e:
            print(f"⚠️ Memory clear failed: {e}")
    
    def preload_models(self):
        """Preload both models for batch processing"""
        if self.models_preloaded:
            return
            
        print("🚀 Preloading models for batch processing...")
        start_time = time.time()
        
        # Preload code analyzer
        if not self.code_analyzer.model_loaded:
            print("📊 Preloading Qwen 3.0 Coder...")
            self.code_analyzer.coder_model.preload_model()
            self.code_analyzer.model_loaded = True
        
        # Preload feedback generator  
        if not self.feedback_generator.model_loaded:
            print("📝 Preloading GPT-OSS-120B...")
            self.feedback_generator.feedback_model.preload_model()
            self.feedback_generator.model_loaded = True
        
        preload_time = time.time() - start_time
        self.models_preloaded = True
        
        print(f"✅ Models preloaded in {preload_time:.1f}s")
        print("⚡ Ready for high-speed batch processing!")
    
    def enable_batch_mode(self):
        """Enable batch processing optimizations"""
        self.batch_mode = True
        self.preload_models()
    
    def grade_batch(self, submissions: List[Dict]) -> List[Dict]:
        """Grade multiple submissions efficiently"""
        print(f"🎯 Starting batch grading of {len(submissions)} submissions...")
        
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
            result['submission_time'] = submission_time
            result['student_name'] = submission.get('student_name', 'Unknown')
            
            results.append(result)
            
            print(f"✅ Completed in {submission_time:.1f}s")
        
        total_time = time.time() - total_start
        avg_time = total_time / len(submissions)
        
        print(f"\n🎉 Batch grading complete!")
        print(f"📊 Total time: {total_time:.1f}s")
        print(f"⚡ Average per submission: {avg_time:.1f}s")
        print(f"🚀 Estimated time saved: {(153 * len(submissions) - total_time):.1f}s")
        
        return results
    
    def _run_parallel_grading(self, student_code: str, student_markdown: str, 
                             solution_code: str, assignment_info: Dict, 
                             rubric_elements: Dict) -> tuple:
        """Run both models in parallel for maximum speed"""
        import threading
        import queue
        
        # Create result queues
        code_queue = queue.Queue()
        feedback_queue = queue.Queue()
        
        # Define worker functions
        def analyze_code():
            try:
                start_time = time.time()
                result = self.code_analyzer.analyze_code(
                    student_code=student_code,
                    solution_code=solution_code,
                    rubric_elements=rubric_elements
                )
                end_time = time.time()
                code_queue.put(('success', result, end_time - start_time))
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                code_queue.put(('error', error_msg, 0))
        
        def generate_feedback():
            try:
                # Small delay to avoid GPU/memory contention
                time.sleep(3)
                start_time = time.time()
                # Run feedback generation independently (doesn't need code_analysis)
                result = self.feedback_generator.generate_feedback(
                    student_code=student_code,
                    student_markdown=student_markdown,
                    code_analysis={},  # Empty - will be merged later
                    assignment_info=assignment_info,
                    rubric_elements=rubric_elements
                )
                end_time = time.time()
                feedback_queue.put(('success', result, end_time - start_time))
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                feedback_queue.put(('error', error_msg, 0))
        
        # Start both threads simultaneously
        overall_start = time.time()
        
        code_thread = threading.Thread(target=analyze_code, name="CodeAnalyzer")
        feedback_thread = threading.Thread(target=generate_feedback, name="FeedbackGenerator")
        
        print("📊 Starting code analysis (Qwen 3.0 Coder)...")
        print("📝 Starting feedback generation (GPT-OSS-120B)...")
        
        code_thread.start()
        feedback_thread.start()
        
        # Wait for both to complete
        code_status, code_result, code_time = code_queue.get()
        feedback_status, feedback_result, feedback_time = feedback_queue.get()
        
        # Ensure threads are finished
        code_thread.join()
        feedback_thread.join()
        
        total_parallel_time = time.time() - overall_start
        
        # Handle any errors
        if code_status == 'error':
            print(f"⚠️ Code analysis failed: {code_result}")
            code_result = {'technical_summary': {'total_technical_score': 15}}
            code_time = 0
        
        if feedback_status == 'error':
            print(f"⚠️ Feedback generation failed: {feedback_result}")
            feedback_result = self.feedback_generator._fallback_feedback({})
            feedback_time = 0
        
        # Update stats
        self.grading_stats['code_analysis_time'] = code_time
        self.grading_stats['feedback_generation_time'] = feedback_time
        self.grading_stats['parallel_processing'] = True
        self.grading_stats['max_parallel_time'] = max(code_time, feedback_time)
        self.grading_stats['time_saved'] = (code_time + feedback_time) - total_parallel_time
        
        print(f"✅ Parallel processing complete!")
        print(f"   📊 Code analysis: {code_time:.1f}s")
        print(f"   📝 Feedback generation: {feedback_time:.1f}s")
        print(f"   ⚡ Total parallel time: {total_parallel_time:.1f}s")
        print(f"   🚀 Time saved: {self.grading_stats['time_saved']:.1f}s")
        
        return code_result, feedback_result
    
    def _run_sequential_grading(self, student_code: str, student_markdown: str, 
                               solution_code: str, assignment_info: Dict, 
                               rubric_elements: Dict) -> tuple:
        """Run models sequentially (original method)"""
        
        # Phase 1: Technical Code Analysis
        print("📊 Phase 1: Technical Code Analysis...")
        code_start = time.time()
        
        code_analysis = self.code_analyzer.analyze_code(
            student_code=student_code,
            solution_code=solution_code,
            rubric_elements=rubric_elements
        )
        
        code_end = time.time()
        self.grading_stats['code_analysis_time'] = code_end - code_start
        
        print(f"✅ Code analysis complete ({self.grading_stats['code_analysis_time']:.1f}s)")
        
        # Phase 2: Educational Feedback Generation
        print("📝 Phase 2: Educational Feedback Generation...")
        feedback_start = time.time()
        
        comprehensive_feedback = self.feedback_generator.generate_feedback(
            student_code=student_code,
            student_markdown=student_markdown,
            code_analysis=code_analysis,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        feedback_end = time.time()
        self.grading_stats['feedback_generation_time'] = feedback_end - feedback_start
        self.grading_stats['parallel_processing'] = False
        
        print(f"✅ Feedback generation complete ({self.grading_stats['feedback_generation_time']:.1f}s)")
        
        return code_analysis, comprehensive_feedback
    
    def _merge_results(self, code_analysis: Dict, feedback: Dict, assignment_info: Dict) -> Dict[str, Any]:
        """Merge technical analysis and educational feedback into final result"""
        
        # Calculate final score
        technical_score = code_analysis.get('technical_summary', {}).get('total_technical_score', 0)
        conceptual_score = feedback.get('final_scores', {}).get('conceptual_score', 0)
        total_score = feedback.get('final_scores', {}).get('total_score', technical_score + conceptual_score)
        max_score = assignment_info.get('total_points', 37.5)
        
        # Create comprehensive result
        result = {
            'score': min(total_score, max_score),  # Cap at max possible
            'max_score': max_score,
            'percentage': min((total_score / max_score) * 100, 100),
            
            # Detailed breakdown
            'technical_analysis': code_analysis,
            'educational_feedback': feedback,
            
            # Combined feedback for display
            'feedback': self._format_combined_feedback(code_analysis, feedback),
            
            # Element scores for database
            'element_scores': self._extract_element_scores(code_analysis, feedback),
            
            # Summary information
            'strengths': self._combine_strengths(code_analysis, feedback),
            'improvements': self._combine_improvements(code_analysis, feedback),
            'overall_assessment': feedback.get('comprehensive_feedback', {}).get('overall_assessment', 'Analysis complete'),
            
            # Execution status
            'executed_successfully': True,
            'grading_method': 'two_model_system'
        }
        
        return result
    
    def _format_combined_feedback(self, code_analysis: Dict, feedback: Dict) -> List[str]:
        """Format combined feedback for display"""
        combined_feedback = []
        
        # Add header
        combined_feedback.append("🤖 **TWO-MODEL GRADING SYSTEM**")
        combined_feedback.append("📊 Technical Analysis (Qwen 3.0 Coder) + 📝 Educational Feedback (GPT-OSS-120B)")
        combined_feedback.append("")
        
        # Add technical summary
        tech_summary = code_analysis.get('technical_summary', {})
        combined_feedback.append("**TECHNICAL ANALYSIS:**")
        combined_feedback.append(f"• Syntax Score: {tech_summary.get('syntax_score', 0)}/10")
        combined_feedback.append(f"• Implementation Score: {tech_summary.get('implementation_score', 0)}/10")
        combined_feedback.append(f"• Correctness Score: {tech_summary.get('correctness_score', 0)}/10")
        combined_feedback.append("")
        
        # Add educational feedback
        comp_feedback = feedback.get('comprehensive_feedback', {})
        combined_feedback.append("**EDUCATIONAL ASSESSMENT:**")
        combined_feedback.append(f"• Overall: {comp_feedback.get('overall_assessment', 'Good work')}")
        
        # Add strengths
        if comp_feedback.get('technical_strengths') or comp_feedback.get('conceptual_strengths'):
            combined_feedback.append("")
            combined_feedback.append("**STRENGTHS:**")
            for strength in comp_feedback.get('technical_strengths', []):
                combined_feedback.append(f"• {strength}")
            for strength in comp_feedback.get('conceptual_strengths', []):
                combined_feedback.append(f"• {strength}")
        
        # Add improvements
        if comp_feedback.get('priority_improvements'):
            combined_feedback.append("")
            combined_feedback.append("**PRIORITY IMPROVEMENTS:**")
            for improvement in comp_feedback.get('priority_improvements', []):
                combined_feedback.append(f"• {improvement}")
        
        # Add encouragement
        if feedback.get('encouragement'):
            combined_feedback.append("")
            combined_feedback.append(f"**ENCOURAGEMENT:** {feedback['encouragement']}")
        
        return combined_feedback
    
    def _extract_element_scores(self, code_analysis: Dict, feedback: Dict) -> Dict[str, float]:
        """Extract element scores for database storage"""
        element_scores = {}
        
        # Technical element scores from code analysis
        for element_name, element_data in code_analysis.get('element_analysis', {}).items():
            element_scores[element_name] = element_data.get('score', 0)
        
        # Manual element scores from feedback
        for element_name, element_data in feedback.get('element_breakdown', {}).items():
            element_scores[element_name] = element_data.get('score', 0)
        
        return element_scores
    
    def _combine_strengths(self, code_analysis: Dict, feedback: Dict) -> List[str]:
        """Combine strengths from both analyses"""
        strengths = []
        
        # Technical strengths
        for element_data in code_analysis.get('element_analysis', {}).values():
            strengths.extend(element_data.get('strengths', []))
        
        # Conceptual strengths
        comp_feedback = feedback.get('comprehensive_feedback', {})
        strengths.extend(comp_feedback.get('technical_strengths', []))
        strengths.extend(comp_feedback.get('conceptual_strengths', []))
        
        return list(set(strengths))  # Remove duplicates
    
    def _combine_improvements(self, code_analysis: Dict, feedback: Dict) -> List[str]:
        """Combine improvement suggestions from both analyses"""
        improvements = []
        
        # Technical improvements
        for element_data in code_analysis.get('element_analysis', {}).values():
            improvements.extend(element_data.get('issues', []))
        
        # Educational improvements
        comp_feedback = feedback.get('comprehensive_feedback', {})
        improvements.extend(comp_feedback.get('priority_improvements', []))
        
        return list(set(improvements))  # Remove duplicates
    
    def _fallback_feedback(self, code_analysis: Dict) -> Dict[str, Any]:
        """Fallback when feedback generation fails"""
        technical_score = code_analysis.get('technical_summary', {}).get('total_technical_score', 15)
        
        return {
            "final_scores": {
                "technical_score": technical_score,
                "conceptual_score": 15,
                "total_score": technical_score + 15,
                "percentage": ((technical_score + 15) / 37.5) * 100
            },
            "comprehensive_feedback": {
                "overall_assessment": "Technical analysis completed successfully",
                "technical_strengths": ["Code implementation attempted"],
                "conceptual_strengths": ["Shows analytical thinking"],
                "priority_improvements": ["Continue developing skills"],
                "learning_evidence": ["Demonstrates effort and engagement"],
                "next_steps": ["Practice more complex problems"]
            },
            "encouragement": "Great effort! Keep practicing to strengthen your skills."
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the two-model system"""
        return {
            'code_analysis_time': self.grading_stats['code_analysis_time'],
            'feedback_generation_time': self.grading_stats['feedback_generation_time'],
            'total_time': self.grading_stats['total_time'],
            'efficiency_ratio': self.grading_stats['code_analysis_time'] / self.grading_stats['feedback_generation_time'] if self.grading_stats['feedback_generation_time'] > 0 else 0
        }
    
    def is_available(self) -> bool:
        """Check if both models are available"""
        return self.code_analyzer.is_available() and self.feedback_generator.is_available()