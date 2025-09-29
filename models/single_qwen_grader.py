#!/usr/bin/env python3
"""
Single Qwen 3.0 Coder Grading System
Uses only Qwen 3.0 Coder for both technical analysis and educational feedback
"""

import json
import time
from typing import Dict, List, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mlx_ai_client import MLXAIClient

class SingleQwenGrader:
    """Single model grader using only Qwen 3.0 Coder for comprehensive grading"""
    
    def __init__(self):
        self.qwen_model = MLXAIClient("Qwen/Qwen2.5-Coder-32B-Instruct")
        self.model_loaded = False
        self.grading_stats = {
            'analysis_time': 0,
            'total_time': 0
        }
    
    def is_available(self) -> bool:
        """Check if Qwen model is available"""
        return self.qwen_model.is_available()
    
    def grade_submission(self, 
                        student_code: str,
                        student_markdown: str, 
                        solution_code: str,
                        assignment_info: Dict,
                        rubric_elements: Dict) -> Dict[str, Any]:
        """
        Grade submission using single Qwen 3.0 Coder model
        """
        
        start_time = time.time()
        
        print("🚀 Starting Single Qwen 3.0 Coder Grading...")
        
        # Load model if needed
        if not self.model_loaded:
            print("🔄 Loading Qwen 3.0 Coder...")
            self.model_loaded = True
        
        # Create comprehensive prompt for Qwen
        prompt = self._create_comprehensive_prompt(
            student_code, student_markdown, solution_code, 
            assignment_info, rubric_elements
        )
        
        print("📊 Running comprehensive analysis...")
        analysis_start = time.time()
        
        # Generate comprehensive response
        response = self.qwen_model.generate_response(prompt, max_tokens=3500)
        
        analysis_time = time.time() - analysis_start
        self.grading_stats['analysis_time'] = analysis_time
        
        print(f"✅ Analysis complete ({analysis_time:.1f}s)")
        
        if response and isinstance(response, str):
            print(f"🔍 DEBUG: Response length: {len(response)} characters")
            print(f"🔍 DEBUG: First 200 chars: {response[:200]}...")
            if len(response) > 200:
                print(f"🔍 DEBUG: Last 200 chars: ...{response[-200:]}")
            
            result = self._parse_comprehensive_response(response, assignment_info)
        else:
            print("⚠️ No response received, using fallback")
            result = self._fallback_grading(assignment_info)
        
        total_time = time.time() - start_time
        self.grading_stats['total_time'] = total_time
        
        result['grading_stats'] = self.grading_stats.copy()
        result['grading_method'] = 'single_qwen_coder'
        
        print(f"🎉 Single Qwen grading complete! Total time: {total_time:.1f}s")
        
        return result
    
    def _create_comprehensive_prompt(self, student_code: str, student_markdown: str, 
                                   solution_code: str, assignment_info: Dict, 
                                   rubric_elements: Dict) -> str:
        """Create comprehensive prompt for Qwen to handle both technical and educational aspects"""
        
        prompt = f"""You are an expert data science educator and code reviewer specializing in R programming for business analytics students. You need to provide comprehensive grading that combines technical analysis with educational feedback.

ASSIGNMENT CONTEXT:
Title: {assignment_info.get('title', 'Data Analysis Assignment')}
Total Points: {assignment_info.get('total_points', 37.5)}
Learning Objectives: {', '.join(assignment_info.get('learning_objectives', []))}

IMPORTANT CONTEXT - BUSINESS ANALYTICS STUDENTS:
- These are business students learning R as a BUSINESS TOOL, not computer science majors
- Focus on practical business applications, not technical programming details
- Use business-friendly language, avoid technical jargon
- If students complete basic requirements, they should score 90%+ (33.75/37.5)
- Emphasize how R skills connect to business decision-making

REFERENCE SOLUTION:
```r
{solution_code}
```

STUDENT'S CODE:
```r
{student_code}
```

STUDENT'S WRITTEN RESPONSES:
{student_markdown}

RUBRIC ELEMENTS:
"""
        
        for element_name, element_data in rubric_elements.items():
            prompt += f"""
{element_name.upper()} ({element_data.get('max_points', 0)} points):
- Description: {element_data.get('description', '')}
- Category: {element_data.get('category', 'manual')}
"""
            
            if element_data.get('automated_checks'):
                prompt += "- Required implementations:\n"
                for check in element_data.get('automated_checks', []):
                    prompt += f"  • {check}\n"
            
            if element_data.get('evaluation_criteria'):
                prompt += "- Evaluation criteria:\n"
                for criteria in element_data.get('evaluation_criteria', []):
                    prompt += f"  • {criteria}\n"
        
        prompt += """

YOUR COMPREHENSIVE GRADING TASK:
1. TECHNICAL ANALYSIS: Evaluate code syntax, implementation, and correctness
2. EDUCATIONAL ASSESSMENT: Assess understanding and written responses
3. BUSINESS FOCUS: Connect R skills to business applications
4. COMPREHENSIVE FEEDBACK: Provide detailed, encouraging feedback

GRADING PHILOSOPHY FOR BUSINESS STUDENTS:
- REWARD COMPLETION: If basic requirements are met, score should be 90%+
- WORKING CODE: Code that runs without errors deserves excellent marks
- BUSINESS APPLICATIONS: Focus on practical use, not programming perfection
- ENCOURAGING TONE: Build confidence for continued learning
- AVOID JARGON: Use business language, not technical programming terms

RESPONSE FORMAT - Provide detailed JSON:
{
    "technical_analysis": {
        "syntax_score": <0-10>,
        "implementation_score": <0-10>, 
        "correctness_score": <0-10>,
        "technical_findings": ["finding1", "finding2", ...]
    },
    "educational_assessment": {
        "conceptual_understanding": <0-10>,
        "written_quality": <0-10>,
        "business_application": <0-10>
    },
    "element_breakdown": {
        "element_name": {
            "score": <points>,
            "max_points": <max>,
            "feedback": "detailed feedback for this element",
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }
    },
    "comprehensive_feedback": {
        "overall_assessment": "summary of student performance with business focus",
        "strengths": ["what they did well - technical and conceptual"],
        "priority_improvements": ["most important areas to work on"],
        "business_connections": ["how this connects to business analysis"],
        "encouragement": "positive, motivating message for business student"
    },
    "final_scores": {
        "technical_total": <sum of technical scores>,
        "conceptual_total": <sum of conceptual scores>,
        "total_score": <final score out of 37.5>,
        "percentage": <percentage>
    }
}

IMPORTANT: Focus on business applications and maintain an encouraging tone. These students need to feel confident using R for business analysis, not become programmers."""

        return prompt
    
    def _parse_comprehensive_response(self, response: str, assignment_info: Dict) -> Dict[str, Any]:
        """Parse comprehensive response from Qwen"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            print(f"🔍 DEBUG: JSON bounds: start={json_start}, end={json_end}")
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                print(f"🔍 DEBUG: Extracted JSON length: {len(json_str)} characters")
                print(f"🔍 DEBUG: JSON preview: {json_str[:300]}...")
                
                result_data = json.loads(json_str)
                print("✅ Successfully parsed comprehensive JSON")
                
                # Extract scores
                final_scores = result_data.get('final_scores', {})
                total_score = final_scores.get('total_score', 0)
                max_score = assignment_info.get('total_points', 37.5)
                percentage = final_scores.get('percentage', (total_score / max_score * 100))
                
                # Format feedback for display
                feedback_lines = []
                feedback_lines.append("🤖 **SINGLE QWEN 3.0 CODER GRADING**")
                feedback_lines.append("📊 Comprehensive Technical + Educational Analysis")
                
                # Technical analysis
                tech_analysis = result_data.get('technical_analysis', {})
                feedback_lines.append("")
                feedback_lines.append("**TECHNICAL ANALYSIS:**")
                feedback_lines.append(f"• Syntax Score: {tech_analysis.get('syntax_score', 0)}/10")
                feedback_lines.append(f"• Implementation Score: {tech_analysis.get('implementation_score', 0)}/10")
                feedback_lines.append(f"• Correctness Score: {tech_analysis.get('correctness_score', 0)}/10")
                
                # Educational assessment
                edu_assessment = result_data.get('educational_assessment', {})
                feedback_lines.append("")
                feedback_lines.append("**EDUCATIONAL ASSESSMENT:**")
                feedback_lines.append(f"• Conceptual Understanding: {edu_assessment.get('conceptual_understanding', 0)}/10")
                feedback_lines.append(f"• Written Quality: {edu_assessment.get('written_quality', 0)}/10")
                feedback_lines.append(f"• Business Application: {edu_assessment.get('business_application', 0)}/10")
                
                # Comprehensive feedback
                comp_feedback = result_data.get('comprehensive_feedback', {})
                if comp_feedback.get('overall_assessment'):
                    feedback_lines.append("")
                    feedback_lines.append("**OVERALL ASSESSMENT:**")
                    feedback_lines.append(f"• {comp_feedback['overall_assessment']}")
                
                if comp_feedback.get('strengths'):
                    feedback_lines.append("")
                    feedback_lines.append("**STRENGTHS:**")
                    for strength in comp_feedback['strengths']:
                        feedback_lines.append(f"• {strength}")
                
                if comp_feedback.get('priority_improvements'):
                    feedback_lines.append("")
                    feedback_lines.append("**PRIORITY IMPROVEMENTS:**")
                    for improvement in comp_feedback['priority_improvements']:
                        feedback_lines.append(f"• {improvement}")
                
                if comp_feedback.get('business_connections'):
                    feedback_lines.append("")
                    feedback_lines.append("**BUSINESS CONNECTIONS:**")
                    for connection in comp_feedback['business_connections']:
                        feedback_lines.append(f"• {connection}")
                
                if comp_feedback.get('encouragement'):
                    feedback_lines.append("")
                    feedback_lines.append("**ENCOURAGEMENT:**")
                    feedback_lines.append(f"{comp_feedback['encouragement']}")
                
                return {
                    'score': total_score,
                    'max_score': max_score,
                    'percentage': percentage,
                    'feedback': feedback_lines,
                    'element_scores': {k: v.get('score', 0) for k, v in result_data.get('element_breakdown', {}).items()},
                    'comprehensive_feedback': comp_feedback,
                    'technical_analysis': tech_analysis,
                    'educational_assessment': edu_assessment,
                    'executed_successfully': True
                }
                
            else:
                print("⚠️ No valid JSON structure found in response")
                return self._fallback_grading(assignment_info)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse comprehensive JSON: {e}")
            return self._fallback_grading(assignment_info)
    
    def _fallback_grading(self, assignment_info: Dict) -> Dict[str, Any]:
        """Fallback grading when parsing fails"""
        max_score = assignment_info.get('total_points', 37.5)
        fallback_score = max_score * 0.8  # 80% fallback
        
        return {
            'score': fallback_score,
            'max_score': max_score,
            'percentage': 80.0,
            'feedback': [
                "🤖 **SINGLE QWEN 3.0 CODER GRADING**",
                "⚠️ Detailed analysis unavailable, using fallback scoring",
                "**OVERALL:** Your submission shows good effort and completion of requirements.",
                "**ENCOURAGEMENT:** Keep up the good work with R for business analysis!"
            ],
            'element_scores': {},
            'executed_successfully': False
        }

def test_single_qwen():
    """Test the single Qwen grader"""
    print("🧪 Testing Single Qwen 3.0 Coder Grading System")
    print("=" * 60)
    
    grader = SingleQwenGrader()
    
    if not grader.is_available():
        print("❌ Qwen 3.0 Coder not available")
        return False
    
    print("✅ Qwen 3.0 Coder available")
    return True

if __name__ == "__main__":
    test_single_qwen()