#!/usr/bin/env python3
"""
Feedback Generator Service using Gemma-3-27B
Specialized for educational feedback and conceptual evaluation
"""

import json
from typing import Dict, List, Any, Optional
from simple_mlx_client import SimpleMLXClient
from two_model_config import get_model_config

class FeedbackGenerator:
    """Specialized feedback generation using Gemma-3-27B model"""
    
    def __init__(self):
        # Get model configuration
        config = get_model_config('feedback_generator')
        model_name = config.get('model_name', 'mlx-community/gemma-3-27b-it-bf16')
        
        # Initialize with configured model (bf16 for best quality) - no fallbacks
        self.feedback_model = SimpleMLXClient(model_name)
        self.model_loaded = False
    
    def generate_feedback(self, 
                         student_code: str, 
                         student_markdown: str,
                         code_analysis: Dict,
                         assignment_info: Dict,
                         rubric_elements: Dict) -> Dict[str, Any]:
        """
        Generate comprehensive educational feedback based on code analysis
        
        Args:
            student_code: Student's code
            student_markdown: Student's written responses
            code_analysis: Technical analysis from CodeAnalyzer
            assignment_info: Assignment details
            rubric_elements: Full rubric information
            
        Returns:
            Dict with comprehensive feedback and final scoring
        """
        
        prompt = self._create_feedback_prompt(
            student_code, student_markdown, code_analysis, 
            assignment_info, rubric_elements
        )
        
        try:
            if not self.model_loaded:
                print("🔄 Loading Gemma-3-27B for feedback generation...")
                self.feedback_model._load_model()
                self.model_loaded = True
            
            response = self.feedback_model.generate_response(prompt, max_tokens=3800)
            
            if response:
                print(f"🔍 DEBUG: Feedback response length: {len(response)} characters")
                print(f"🔍 DEBUG: First 200 chars: {response[:200]}...")
                if len(response) > 200:
                    print(f"🔍 DEBUG: Last 200 chars: ...{response[-200:]}")
                return self._parse_feedback_response(response, code_analysis)
            else:
                print("⚠️ Feedback generation returned None")
                return self._fallback_feedback(code_analysis)
                
        except Exception as e:
            print(f"⚠️ Feedback generation failed: {e}")
            return self._fallback_feedback(code_analysis)
    
    def _create_feedback_prompt(self, student_code: str, student_markdown: str, 
                               code_analysis: Dict, assignment_info: Dict, 
                               rubric_elements: Dict) -> str:
        """Create specialized prompt for educational feedback"""
        
        # Extract manual review elements
        manual_elements = []
        for element_name, element_data in rubric_elements.items():
            if element_data.get('category') == 'manual':
                manual_elements.append({
                    'name': element_name,
                    'points': element_data.get('max_points', 0),
                    'description': element_data.get('description', ''),
                    'criteria': element_data.get('evaluation_criteria', [])
                })
        
        prompt = f"""You are an expert data science educator providing comprehensive feedback on student work. You have received a detailed technical analysis of the student's code and now need to provide educational feedback.

ASSIGNMENT CONTEXT:
Title: {assignment_info.get('title', 'Data Analysis Assignment')}
Total Points: {assignment_info.get('total_points', 37.5)}
Learning Objectives: {', '.join(assignment_info.get('learning_objectives', []))}

TECHNICAL CODE ANALYSIS (from Code Specialist):
{json.dumps(code_analysis, indent=2)}

STUDENT'S WRITTEN RESPONSES:
{student_markdown}

STUDENT'S CODE (for context):
```r
{student_code}
```

MANUAL EVALUATION ELEMENTS:
"""
        
        for element in manual_elements:
            prompt += f"""
{element['name'].upper()} ({element['points']} points):
- Focus: {element['description']}
- Evaluation criteria:
"""
            for criteria in element['criteria']:
                prompt += f"  • {criteria}\n"
        
        prompt += """

YOUR TASK:
1. INTEGRATE TECHNICAL ANALYSIS: Use the code analysis results to inform your evaluation
2. EVALUATE CONCEPTUAL UNDERSTANDING: Assess written responses and reasoning  
3. PROVIDE EDUCATIONAL FEEDBACK: Focus on learning and improvement
4. CALCULATE FINAL SCORES: Combine technical and conceptual scores
5. APPLY BUSINESS-STUDENT-FRIENDLY GRADING: 
   - Reward completion and effort heavily - these are FIRST-TIME business students!
   - If student completed basic requirements, score should be 93-96% (34.9-36.0/37.5)
   - Students who get code working and complete all tasks deserve 94%+ 
   - For first-time students: working code + written responses = EXCELLENT work
   - Perfect technical execution isn't expected - completion and effort are the goals
   - Minor issues (file paths, comments, styling) should have minimal impact on scores
   - Focus on encouraging continued learning, not finding flaws
   - Emphasize business value and decision-making applications

IMPORTANT BUSINESS STUDENT CONTEXT:
- These students are learning R as a BUSINESS ANALYTICS TOOL for data-driven decision making
- They are FIRST-TIME R users - getting code to work is a major achievement
- EXCELLENT WORK (93-95%) includes: data imported successfully, basic exploration completed, written responses provided
- GOOD WORK (88-92%) includes: most requirements met with minor issues
- Explanations should be DETAILED and focus on "business value and practical applications"
- Use business terminology: "data quality," "business insights," "analytical findings"
- Focus on practical applications: "This enables trend analysis for strategic planning"
- Provide THOROUGH analysis - these students need comprehensive feedback to learn effectively
- Maintain professional, instructive tone throughout - like a senior business analyst mentoring

FEEDBACK REQUIREMENTS FOR BUSINESS ANALYTICS STUDENTS:
- Use PROFESSIONAL, BUSINESS-APPROPRIATE tone (supportive but not overly excited)
- Be COMPREHENSIVE and DETAILED in analysis - provide thorough feedback
- Acknowledge ALL completed work (technical analysis shows what was implemented)
- Focus on BUSINESS APPLICATIONS and practical use of R for analytics
- Provide SPECIFIC examples from student's work with detailed explanations
- Give CONSTRUCTIVE, business-focused suggestions for improvement
- Use BUSINESS LANGUAGE - avoid technical programming jargon
- Recognize that basic completion deserves strong credit (85-90%+)
- Connect R skills to real-world business decision-making scenarios
- Maintain PROFESSIONAL, INSTRUCTIVE tone - like a business mentor
- Remember: They need R for business insights and data-driven decisions

Respond in JSON format:
{
    "final_scores": {
        "technical_score": <from_code_analysis>,
        "conceptual_score": <your_evaluation>,
        "total_score": <combined_total>,
        "percentage": <percentage_of_total>
    },
    "element_breakdown": {
        "element_name": {
            "score": <points>,
            "max_points": <max>,
            "feedback": "detailed feedback",
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }
    },
    "comprehensive_feedback": {
        "overall_assessment": "summary of student performance",
        "technical_strengths": ["what they did well technically"],
        "conceptual_strengths": ["what they understood well"],
        "priority_improvements": ["most important areas to work on"],
        "learning_evidence": ["signs of understanding and growth"],
        "next_steps": ["recommendations for continued learning"]
    },
    "detailed_comments": {
        "code_quality": "assessment of code organization and style",
        "problem_solving": "evaluation of analytical approach",
        "communication": "quality of written explanations",
        "business_context": "understanding of real-world applications"
    },
    "encouragement": "positive, motivating message for the student"
}

IMPORTANT: Base your evaluation on BOTH the technical analysis AND the student's written work. Give credit for understanding even if technical implementation has minor issues. Focus on learning progress and provide guidance for improvement."""

        return prompt
    
    def _parse_feedback_response(self, response: str, code_analysis: Dict) -> Dict[str, Any]:
        """Parse feedback response and merge with code analysis"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            print(f"🔍 DEBUG: JSON bounds: start={json_start}, end={json_end}")
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                print(f"🔍 DEBUG: Extracted JSON length: {len(json_str)} characters")
                print(f"🔍 DEBUG: JSON preview: {json_str[:300]}...")
                
                feedback_data = json.loads(json_str)
                print("✅ Successfully parsed feedback JSON")
                
                # Merge with code analysis
                feedback_data['code_analysis'] = code_analysis
                return feedback_data
            else:
                print("⚠️ No valid JSON structure found in response")
                return self._fallback_feedback(code_analysis)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse feedback JSON: {e}")
            print(f"🔍 DEBUG: Problematic JSON: {json_str[:500]}...")
            return self._fallback_feedback(code_analysis)
    
    def _fallback_feedback(self, code_analysis: Dict) -> Dict[str, Any]:
        """Fallback feedback when GPT-OSS fails"""
        technical_score = code_analysis.get('technical_summary', {}).get('total_technical_score', 15)
        
        return {
            "final_scores": {
                "technical_score": technical_score,
                "conceptual_score": 15,
                "total_score": technical_score + 15,
                "percentage": ((technical_score + 15) / 37.5) * 100
            },
            "element_breakdown": {},
            "comprehensive_feedback": {
                "overall_assessment": "Technical analysis completed, detailed feedback unavailable",
                "technical_strengths": ["Code analysis completed"],
                "conceptual_strengths": ["Written responses provided"],
                "priority_improvements": ["Continue practicing"],
                "learning_evidence": ["Shows effort and engagement"],
                "next_steps": ["Keep developing skills"]
            },
            "detailed_comments": {
                "code_quality": "See technical analysis for details",
                "problem_solving": "Demonstrates analytical thinking",
                "communication": "Written responses show understanding",
                "business_context": "Shows awareness of practical applications"
            },
            "encouragement": "Keep up the good work! Your technical skills are developing well.",
            "code_analysis": code_analysis
        }
    
    def is_available(self) -> bool:
        """Check if feedback generator is available"""
        return self.feedback_model.is_available()