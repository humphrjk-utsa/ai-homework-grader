#!/usr/bin/env python3
"""
Validate Report Content
Ensures PDF reports contain only instructor-relevant content without internal AI dialog
"""

import re
import json
from typing import Dict, Any, List, Tuple

class ReportContentValidator:
    """Validates that report content is clean and instructor-appropriate"""
    
    def __init__(self):
        # Patterns that should NOT appear in student reports
        self.forbidden_patterns = [
            r"what i'm looking for",
            r"what to focus on",
            r"internal reasoning",
            r"ai thinking",
            r"model dialog",
            r"express version",
            r"quick assessment",
            r"ai assessment",
            r"model thinking",
            r"\[internal:.*?\]",
            r"\[ai:.*?\]",
            r"\[reasoning:.*?\]",
            r"express.*pdf",
            r"quick.*pdf",
            r"simple.*pdf"
        ]
        
        # Patterns that SHOULD appear in instructor feedback
        self.required_patterns = [
            r"(excellent|good|satisfactory|needs improvement)",
            r"(strengths?|areas? for development|recommendations?)",
            r"(reflection|analysis|understanding)"
        ]
    
    def validate_feedback_content(self, feedback_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that feedback content is appropriate for student reports
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check comprehensive feedback
        if 'comprehensive_feedback' in feedback_data:
            comp_feedback = feedback_data['comprehensive_feedback']
            
            # Check instructor comments
            if 'instructor_comments' in comp_feedback:
                comment_issues = self._check_text_content(
                    comp_feedback['instructor_comments'], 
                    "instructor_comments"
                )
                issues.extend(comment_issues)
            
            # Check detailed feedback sections
            if 'detailed_feedback' in comp_feedback:
                detailed = comp_feedback['detailed_feedback']
                
                for section_name, section_content in detailed.items():
                    if isinstance(section_content, list):
                        for item in section_content:
                            item_issues = self._check_text_content(item, f"detailed_feedback.{section_name}")
                            issues.extend(item_issues)
        
        # Check technical analysis
        if 'technical_analysis' in feedback_data:
            tech_analysis = feedback_data['technical_analysis']
            for key, value in tech_analysis.items():
                if isinstance(value, list):
                    for item in value:
                        item_issues = self._check_text_content(item, f"technical_analysis.{key}")
                        issues.extend(item_issues)
                elif isinstance(value, str):
                    item_issues = self._check_text_content(value, f"technical_analysis.{key}")
                    issues.extend(item_issues)
        
        # Check question analysis
        if 'question_analysis' in feedback_data:
            q_analysis = feedback_data['question_analysis']
            for q_key, q_data in q_analysis.items():
                if 'detailed_feedback' in q_data:
                    item_issues = self._check_text_content(
                        q_data['detailed_feedback'], 
                        f"question_analysis.{q_key}"
                    )
                    issues.extend(item_issues)
        
        return len(issues) == 0, issues
    
    def _check_text_content(self, text: str, context: str) -> List[str]:
        """Check individual text content for forbidden patterns"""
        issues = []
        
        if not isinstance(text, str):
            return issues
        
        text_lower = text.lower()
        
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(f"Found forbidden pattern '{pattern}' in {context}")
        
        # Check for overly technical AI language
        ai_language_patterns = [
            r"model output",
            r"algorithm determined",
            r"neural network",
            r"machine learning model",
            r"ai generated",
            r"automated assessment"
        ]
        
        for pattern in ai_language_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(f"Found technical AI language '{pattern}' in {context} - should use instructor language")
        
        return issues
    
    def validate_pdf_generation_methods(self, code_content: str) -> Tuple[bool, List[str]]:
        """Validate that there's only one PDF generation method"""
        issues = []
        
        # Check for multiple PDF generation methods
        pdf_method_patterns = [
            r"def.*generate.*express.*pdf",
            r"def.*generate.*quick.*pdf", 
            r"def.*generate.*simple.*pdf",
            r"def.*express.*report",
            r"def.*quick.*report"
        ]
        
        for pattern in pdf_method_patterns:
            matches = re.findall(pattern, code_content, re.IGNORECASE)
            if matches:
                issues.append(f"Found express/quick PDF method: {matches}")
        
        # Check for single main generation method
        main_method_pattern = r"def generate_report\("
        main_methods = re.findall(main_method_pattern, code_content)
        
        if len(main_methods) != 1:
            issues.append(f"Expected exactly 1 main generate_report method, found {len(main_methods)}")
        
        return len(issues) == 0, issues
    
    def clean_feedback_for_instructor(self, feedback_text: str) -> str:
        """Clean feedback text to be instructor-appropriate"""
        if not isinstance(feedback_text, str):
            return str(feedback_text)
        
        # Remove forbidden patterns
        cleaned = feedback_text
        for pattern in self.forbidden_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Replace AI language with instructor language
        replacements = {
            r"the model determined": "the analysis shows",
            r"ai assessment": "instructor assessment", 
            r"algorithm found": "analysis reveals",
            r"automated grading": "evaluation",
            r"machine learning": "analytical methods"
        }
        
        for pattern, replacement in replacements.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def generate_instructor_fallback(self, score: float, max_score: float) -> str:
        """Generate appropriate instructor feedback when original is filtered out"""
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        if percentage >= 90:
            return "Excellent work that demonstrates strong understanding of the concepts and thorough engagement with the assignment requirements."
        elif percentage >= 80:
            return "Good work that shows solid understanding. Continue to develop your analytical skills and deepen your insights."
        elif percentage >= 70:
            return "Satisfactory work that meets the basic requirements. Focus on expanding your analysis and making stronger connections."
        elif percentage >= 60:
            return "Your work shows effort but needs development. Review the key concepts and work on strengthening your analytical approach."
        else:
            return "This work needs significant improvement. Please review the assignment requirements and seek additional support to strengthen your understanding."

def validate_report_system():
    """Validate the entire report generation system"""
    validator = ReportContentValidator()
    
    print("🔍 Validating Report Content System")
    print("=" * 50)
    
    # Test sample feedback data
    sample_feedback = {
        "comprehensive_feedback": {
            "instructor_comments": "Good work on this assignment. What I'm looking for: better analysis.",
            "detailed_feedback": {
                "reflection_assessment": [
                    "Shows good critical thinking",
                    "Internal reasoning: student needs more depth"
                ],
                "analytical_strengths": [
                    "Clear code structure",
                    "AI thinking: this is well organized"
                ]
            }
        }
    }
    
    # Validate content
    is_valid, issues = validator.validate_feedback_content(sample_feedback)
    
    print(f"📊 Content Validation Results:")
    print(f"   Valid: {is_valid}")
    if issues:
        print(f"   Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"   ✅ No content issues found")
    
    # Test cleaning
    dirty_text = "Good work. What I'm looking for: more depth. AI thinking: needs improvement."
    clean_text = validator.clean_feedback_for_instructor(dirty_text)
    print(f"\n🧹 Text Cleaning Example:")
    print(f"   Original: {dirty_text}")
    print(f"   Cleaned:  {clean_text}")
    
    # Test fallback generation
    fallback = validator.generate_instructor_fallback(32.5, 37.5)
    print(f"\n💬 Instructor Fallback Example:")
    print(f"   Score: 32.5/37.5 (86.7%)")
    print(f"   Fallback: {fallback}")
    
    print("\n✅ Report validation system ready!")

if __name__ == "__main__":
    validate_report_system()