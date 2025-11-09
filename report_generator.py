#!/usr/bin/env python3
"""
Generate PDF reports for graded homework submissions
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generate professional PDF reports for homework grading"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6
        ))
    
    def _get_assignment_folder(self, assignment_id: str) -> str:
        """Create and return assignment-specific folder path"""
        # Clean assignment name for folder
        clean_assignment = re.sub(r'[^\w\s-]', '', assignment_id).replace(' ', '_')
        assignment_folder = os.path.join(self.output_dir, clean_assignment)
        os.makedirs(assignment_folder, exist_ok=True)
        return assignment_folder
    
    def _safe_paragraph(self, text: str, style):
        """Create a Paragraph with extra Unicode cleaning to prevent black squares"""
        if not text:
            return Paragraph("", style)
        
        # AGGRESSIVE cleaning - replace problematic characters with safe alternatives
        import re
        
        # Replace non-breaking hyphens and special dashes with regular hyphens
        safe_text = text.replace('\u2011', '-')  # Non-breaking hyphen (causes black squares)
        safe_text = safe_text.replace('\u2010', '-')  # Hyphen
        safe_text = safe_text.replace('\u2012', '-')  # Figure dash
        safe_text = safe_text.replace('\u2013', '-')  # En dash
        safe_text = safe_text.replace('\u2014', '-')  # Em dash
        safe_text = safe_text.replace('\u2015', '-')  # Horizontal bar
        
        # Remove box drawing characters (U+2500-U+257F)
        safe_text = re.sub(r'[\u2500-\u257F]', '', safe_text)
        # Remove geometric shapes (U+25A0-U+25FF) - this includes ■
        safe_text = re.sub(r'[\u25A0-\u25FF]', '', safe_text)
        # Remove dingbats (U+2700-U+27BF)
        safe_text = re.sub(r'[\u2700-\u27BF]', '', safe_text)
        # Remove miscellaneous symbols (U+2600-U+26FF)
        safe_text = re.sub(r'[\u2600-\u26FF]', '', safe_text)
        
        # Clean up any double spaces left by removals
        safe_text = ' '.join(safe_text.split())
        return Paragraph(safe_text, style)
    
    def _format_structured_feedback(self, text: str, story, style_name='Normal'):
        """Format feedback with WHAT/WHY/HOW/EXAMPLE structure into separate sections"""
        if not text or not isinstance(text, str):
            return
        
        # Check if this has the structured format
        if 'WHAT:' in text and 'WHY:' in text:
            # Split into sections
            sections = {}
            current_section = None
            current_text = []
            
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('WHAT:'):
                    if current_section and current_text:
                        sections[current_section] = ' '.join(current_text)
                    current_section = 'WHAT'
                    current_text = [line[5:].strip()]
                elif line.startswith('WHY:'):
                    if current_section and current_text:
                        sections[current_section] = ' '.join(current_text)
                    current_section = 'WHY'
                    current_text = [line[4:].strip()]
                elif line.startswith('HOW:'):
                    if current_section and current_text:
                        sections[current_section] = ' '.join(current_text)
                    current_section = 'HOW'
                    current_text = [line[4:].strip()]
                elif line.startswith('EXAMPLE:'):
                    if current_section and current_text:
                        sections[current_section] = ' '.join(current_text)
                    current_section = 'EXAMPLE'
                    current_text = [line[8:].strip()]
                elif line and current_section:
                    current_text.append(line)
            
            # Add the last section
            if current_section and current_text:
                sections[current_section] = ' '.join(current_text)
            
            # Format each section on separate lines with bold labels
            if 'WHAT' in sections:
                story.append(self._safe_paragraph(f"<b>What:</b> {self._clean_text(sections['WHAT'])}", self.styles[style_name]))
                story.append(Spacer(1, 3))
            if 'WHY' in sections:
                story.append(self._safe_paragraph(f"<b>Why:</b> {self._clean_text(sections['WHY'])}", self.styles[style_name]))
                story.append(Spacer(1, 3))
            if 'HOW' in sections:
                story.append(self._safe_paragraph(f"<b>How:</b> {self._clean_text(sections['HOW'])}", self.styles[style_name]))
                story.append(Spacer(1, 3))
            if 'EXAMPLE' in sections:
                # Format code examples with monospace
                example_text = self._clean_text(sections['EXAMPLE'])
                story.append(self._safe_paragraph(f"<b>Example:</b> {example_text}", self.styles[style_name]))
            
            story.append(Spacer(1, 8))
        else:
            # No structure, just add as normal paragraph
            clean_text = self._clean_text(text)
            if clean_text:
                story.append(self._safe_paragraph(clean_text, self.styles[style_name]))
    
    def _clean_text(self, text: str) -> str:
        """Clean text for PDF generation - remove internal AI dialog and formatting"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove internal AI dialog and reasoning patterns
        internal_patterns = [
            r"What I'm looking for:.*?(?=\n|$)",
            r"What to focus on:.*?(?=\n|$)",
            r"Internal reasoning:.*?(?=\n|$)",
            r"AI thinking:.*?(?=\n|$)",
            r"Model dialog:.*?(?=\n|$)",
            r"Express version:.*?(?=\n|$)",
            r"Quick assessment:.*?(?=\n|$)",
            r"\[Internal:.*?\]",
            r"\[AI:.*?\]",
            r"\[Reasoning:.*?\]"
        ]
        
        for pattern in internal_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove ALL problematic Unicode characters that cause black squares
        # This must happen BEFORE any PDF rendering
        removals = ['■', '▪', '▫', '●', '○', '•', '✓', '✔', '✅', '❌', '⚠', '⚠️']
        for char in removals:
            text = text.replace(char, '')
        
        # Replace arrows and quotes with safe alternatives
        replacements = {
            '→': '->',
            '←': '<-',
            '↑': '^',
            '↓': 'v',
            ''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
            '–': '-',
            '—': '-',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove any remaining emojis
        emoji_pattern = r'[📋📈🗂️📦🔍📚🔧💭📝👍🤔💡🎯📊🚀⚡🎉🔥💪🎓]'
        text = re.sub(emoji_pattern, '', text)
        
        # Remove markdown formatting
        text = text.replace('**', '')  # Remove markdown bold
        text = text.replace('*', '')   # Remove markdown italic
        text = text.replace('```', '')  # Remove code block markers
        
        # Clean up extra whitespace and multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_json_from_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Extract only the JSON content from AI response, ignoring all internal monologue"""
        if not ai_response:
            return None
        
        try:
            # Find JSON content - look for the last complete JSON object
            import re
            
            # Pattern to find JSON objects
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, ai_response, re.DOTALL)
            
            if not json_matches:
                return None
            
            # Try to parse each JSON match, starting from the last one
            for json_text in reversed(json_matches):
                try:
                    # Clean up the JSON text
                    clean_json = json_text.strip()
                    
                    # Remove any trailing text after the JSON
                    if clean_json.endswith('```'):
                        clean_json = clean_json[:-3].strip()
                    
                    # Parse the JSON
                    parsed_json = json.loads(clean_json)
                    
                    # Validate it has the expected structure
                    if isinstance(parsed_json, dict) and ('detailed_feedback' in parsed_json or 'instructor_comments' in parsed_json):
                        return parsed_json
                        
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting JSON from AI response: {e}")
            return None
    
    def _clean_instructor_comments(self, comments: str) -> str:
        """Clean instructor comments of any remaining AI artifacts"""
        if not comments:
            return ""
        
        # Remove AI artifacts
        clean_comments = comments
        
        # Remove internal reasoning patterns
        patterns_to_remove = [
            r"We need to.*?\.",
            r"Let's.*?\.",
            r"First,.*?\.",
            r"Now.*?\.",
            r"The student provided.*?\.",
            r"They have.*?\.",
            r"<\|.*?\|>",
            r"\{.*?\}",
            r"JSON.*?"
        ]
        
        for pattern in patterns_to_remove:
            clean_comments = re.sub(pattern, '', clean_comments, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up whitespace
        clean_comments = re.sub(r'\s+', ' ', clean_comments).strip()
        
        return clean_comments
    
    def _clean_instructor_comments_thoroughly(self, comments: str) -> str:
        """Thoroughly clean instructor comments - remove ALL prompt text and artifacts"""
        if not comments:
            return ""
        
        # Remove prompt text patterns
        prompt_patterns = [
            r"Must reference specific.*?(?=\n|$)",
            r"Provide reflection assessment.*?(?=\n|$)",
            r"Must be pure.*?(?=\n|$)",
            r"Student's reflection.*?(?=\n\n|\Z)",
            r"Reflection assessment items:.*?(?=\n\n|\Z)",
            r"Analytical strengths:.*?(?=\n\n|\Z)",
            r"Business application:.*?(?=\n\n|\Z)",
            r"Learning demonstration:.*?(?=\n\n|\Z)",
            r"Areas for development:.*?(?=\n\n|\Z)",
            r"Recommendations:.*?(?=\n\n|\Z)",
            r"Instructor comments:.*?(?=\n\n|\Z)",
            r"assistantfinal\{.*?\}",
            r"Make sure.*?(?=\n|$)",
            r"Ensure.*?(?=\n|$)",
            r"- \".*?\"",  # Remove quoted items
        ]
        
        clean_comments = comments
        for pattern in prompt_patterns:
            clean_comments = re.sub(pattern, '', clean_comments, flags=re.IGNORECASE | re.DOTALL)
        
        # NOW call _clean_text to handle Unicode characters
        clean_comments = self._clean_text(clean_comments)
        
        # If too short after cleaning, return empty (don't use fallback)
        if len(clean_comments) < 50:
            logger.warning(f"Instructor comments too short after cleaning ({len(clean_comments)} chars) - AI needs to generate more verbose feedback")
            return ""
        
        return clean_comments
    
    def _generate_fallback_instructor_comment(self) -> str:
        """Generate appropriate fallback instructor comment - SHOULD NOT BE USED"""
        # This should never be called - feedback should be generated per student
        return ""
    
    def generate_report(self, student_name: str, assignment_id: str, analysis_result: Dict[str, Any]) -> str:
        """
        Generate a comprehensive PDF report for a graded submission
        
        This is the ONLY PDF generation method - no express or quick versions.
        All content is filtered to include only instructor-relevant feedback.
        """
        
        # Validate inputs
        if not student_name or not assignment_id:
            raise ValueError("Student name and assignment ID are required")
        
        # Create filename in assignment-specific folder
        safe_student_name = student_name or "Unknown_Student"
        safe_name = re.sub(r'[^\w\s-]', '', safe_student_name).replace(' ', '_')
        filename = f"{safe_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Get assignment-specific folder
        assignment_folder = self._get_assignment_folder(assignment_id)
        filepath = os.path.join(assignment_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch)
        story = []
        
        # Add header with student and assignment info
        self._add_header(story, safe_student_name, assignment_id, analysis_result)
        
        # Add score summary
        self._add_score_summary(story, analysis_result)
        
        # Add validation issues if present (CRITICAL - show first)
        if analysis_result.get('validation'):
            self._add_validation_section(story, analysis_result['validation'])
        
        # Add human feedback if available (takes priority)
        if analysis_result.get('human_feedback'):
            story.append(Paragraph("Instructor Review", self.styles['CustomHeading']))
            human_feedback = self._clean_text(analysis_result['human_feedback'])
            story.append(Paragraph(human_feedback, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Add comprehensive feedback (filtered for instructor content only)
        if 'comprehensive_feedback' in analysis_result:
            self._add_comprehensive_feedback(story, analysis_result['comprehensive_feedback'])
        
        # Add preprocessing info if available
        if 'preprocessing' in analysis_result:
            self._add_preprocessing_info(story, analysis_result['preprocessing'])
        
        # Add technical analysis (filtered for instructor content only)
        if 'technical_analysis' in analysis_result:
            self._add_technical_analysis(story, analysis_result['technical_analysis'])
        
        # Add detailed breakdown (legacy support, filtered)
        self._add_detailed_breakdown(story, analysis_result)
        
        # Add code fixes if there are issues (filtered for instructor content only)
        if analysis_result.get('code_issues'):
            self._add_code_fixes(story, analysis_result)
        
        # Add reflection questions analysis (filtered for instructor content only)
        if 'question_analysis' in analysis_result:
            self._add_question_analysis(story, analysis_result['question_analysis'])
        
        # Add final recommendations (filtered for instructor content only)
        self._add_recommendations(story, analysis_result)
        
        # Build PDF - this creates the final report
        doc.build(story)
        
        return filepath
    
    def _add_header(self, story, student_name: str, assignment_id: str, analysis_result: Dict[str, Any]):
        """Add report header"""
        # Title
        story.append(Paragraph("Homework Grading Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Student info table
        total_score = analysis_result.get('total_score', 0)
        max_score = analysis_result.get('max_score', 37.5)
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        data = [
            ['Student Name:', self._clean_text(student_name)],
            ['Assignment:', self._clean_text(assignment_id)],
            ['Graded On:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Final Score:', f"{total_score:.1f} / {max_score} points ({percentage:.1f}%)"]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    def _add_validation_section(self, story, validation: Dict[str, Any]):
        """Add validation issues section - shown prominently if issues exist"""
        penalty = validation.get('penalty_percent', 0)
        issues = validation.get('issues', [])
        warnings = validation.get('warnings', [])
        
        if penalty > 0 or issues or warnings:
            story.append(Paragraph("⚠️ SUBMISSION ISSUES", self.styles['CustomHeading']))
            
            if penalty > 0:
                story.append(Paragraph(
                    f"<b>Penalty Applied: {penalty}% deduction</b>",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 6))
            
            if issues:
                story.append(Paragraph("<b>Critical Issues:</b>", self.styles['Heading2']))
                for issue in issues:
                    clean_issue = self._clean_text(issue)
                    story.append(Paragraph(f"• {clean_issue}", self.styles['CustomBullet']))
                story.append(Spacer(1, 6))
            
            if warnings:
                story.append(Paragraph("<b>Warnings:</b>", self.styles['Heading2']))
                for warning in warnings:
                    clean_warning = self._clean_text(warning)
                    story.append(Paragraph(f"• {clean_warning}", self.styles['CustomBullet']))
                story.append(Spacer(1, 6))
            
            # Add guidance from validation feedback
            feedback_text = validation.get('feedback', '')
            if feedback_text:
                story.append(Paragraph("<b>How to Fix:</b>", self.styles['Heading2']))
                # Extract just the "How to Fix" sections
                if "### How to Fix:" in feedback_text:
                    fix_sections = feedback_text.split("### How to Fix:")[1:]
                    for section in fix_sections:
                        clean_section = self._clean_text(section.strip())
                        if clean_section:
                            story.append(Paragraph(clean_section, self.styles['Normal']))
                            story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 20))
    
    def _add_score_summary(self, story, analysis_result: Dict[str, Any]):
        """Add score summary section"""
        story.append(Paragraph("Score Summary", self.styles['CustomHeading']))
        
        # Show if human reviewed
        if analysis_result.get('human_reviewed'):
            story.append(Paragraph("<b>✓ Human Reviewed</b>", self.styles['Heading2']))
            # Show both AI and final (human) scores
            ai_score = analysis_result.get('ai_score', 0)
            story.append(Paragraph(f"Original AI Score: {ai_score:.1f} / 37.5", self.styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Overall performance (final score)
        total_score = analysis_result.get('total_score', 0)
        max_score = analysis_result.get('max_score', 37.5)
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        if percentage >= 90:
            performance = "Excellent"
        elif percentage >= 80:
            performance = "Good"
        elif percentage >= 70:
            performance = "Satisfactory"
        elif percentage >= 60:
            performance = "Needs Improvement"
        else:
            performance = "Unsatisfactory"
        
        story.append(Paragraph(f"<b>Overall Performance:</b> {performance} ({percentage:.1f}%)", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Element scores breakdown
        if 'element_scores' in analysis_result:
            story.append(Paragraph("Component Scores:", self.styles['Heading2']))
            
            for element, score in analysis_result['element_scores'].items():
                element_name = element.replace('_', ' ').title()
                story.append(Paragraph(f"• {element_name}: {score:.1f} points", self.styles['CustomBullet']))
            
            story.append(Spacer(1, 12))
    
    def _add_detailed_breakdown(self, story, analysis_result: Dict[str, Any]):
        """Add comprehensive feedback breakdown"""
        
        # Performance by Category
        story.append(Paragraph("Performance by Category", self.styles['CustomHeading']))
        
        if 'element_scores' in analysis_result:
            for element, score in analysis_result['element_scores'].items():
                element_name = element.replace('_', ' ').title()
                # Create a clean score display
                if element == 'working_directory':
                    max_score = 2
                elif element == 'package_loading':
                    max_score = 4
                elif element in ['csv_import', 'excel_import']:
                    max_score = 6
                elif element == 'data_inspection':
                    max_score = 8
                elif element == 'reflection_questions':
                    max_score = 12.5
                elif element == 'technical_execution':
                    max_score = 15  # 40% of 37.5
                elif element == 'data_analysis':
                    max_score = 15  # 40% of 37.5
                elif element == 'business_thinking':
                    max_score = 3.75  # 10% of 37.5
                elif element == 'communication':
                    max_score = 3.75  # 10% of 37.5
                else:
                    max_score = 5
                
                percentage = (score / max_score) * 100 if max_score > 0 else 0
                
                if percentage >= 90:
                    status = "✅ Excellent"
                elif percentage >= 80:
                    status = "✅ Good"
                elif percentage >= 70:
                    status = "⚠️ Satisfactory"
                else:
                    status = "❌ Needs Work"
                
                story.append(Paragraph(f"{status} <b>{element_name}:</b> {score:.1f}/{max_score} points ({percentage:.0f}%)", self.styles['Normal']))
        
        # Add detailed feedback if available
        if analysis_result.get('detailed_feedback'):
            story.append(Spacer(1, 12))
            story.append(Paragraph("Detailed Analysis:", self.styles['Heading2']))
            
            for feedback in analysis_result['detailed_feedback'][:8]:  # Limit to first 8 items
                if not isinstance(feedback, str) or len(feedback.strip()) < 10:
                    continue
                
                # Clean and process feedback - keep it simple
                clean_feedback = self._clean_text(feedback)
                if clean_feedback.strip() and len(clean_feedback) > 10:
                    # For very long feedback, split only on clear paragraph breaks
                    if len(clean_feedback) > 1000:
                        # Split on double line breaks or major section indicators
                        parts = re.split(r'\n\n+|What I\'m looking for:', clean_feedback)
                        for i, part in enumerate(parts):
                            clean_part = part.strip()
                            if clean_part and len(clean_part) > 20:
                                if i == 0:
                                    story.append(Paragraph(f"• {clean_part}", self.styles['CustomBullet']))
                                else:
                                    # Subsequent parts are explanations
                                    story.append(Paragraph(f"  {clean_part}", self.styles['Normal']))
                    else:
                        # Keep shorter feedback intact
                        story.append(Paragraph(f"• {clean_feedback}", self.styles['CustomBullet']))
        
        story.append(Spacer(1, 20))
    
    def _process_feedback_with_squares(self, story, feedback: str):
        """Process feedback text that contains dark squares (■) for better formatting"""
        # Split on dark squares
        parts = feedback.split('■')
        
        # Process the first part (before any dark squares)
        if parts[0].strip():
            main_content = self._clean_text(parts[0]).strip()
            if main_content and len(main_content) > 5:
                story.append(Paragraph(f"• {main_content}", self.styles['CustomBullet']))
        
        # Process each part after a dark square
        for part in parts[1:]:
            if not part.strip():
                continue
                
            clean_part = self._clean_text(part).strip()
            if len(clean_part) < 5:
                continue
            
            # Check if this looks like a section header
            if any(header in clean_part for header in [
                'Data Types Analysis', 'Data Quality Assessment', 'Analysis Readiness',
                'Reflection Questions', 'Overall Reflection Quality'
            ]):
                # Extract score if present
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', clean_part)
                if score_match:
                    header_text = clean_part.split('(')[0].strip()
                    score_text = f"({score_match.group(1)}/{score_match.group(2)} points)"
                    story.append(Paragraph(f"<b>{header_text}</b> {score_text}", self.styles['Heading2']))
                else:
                    story.append(Paragraph(f"<b>{clean_part}</b>", self.styles['Heading2']))
            else:
                # Regular content - check if it contains detailed explanations
                if 'What I\'m looking for:' in clean_part:
                    # Split into feedback and explanation
                    parts_split = clean_part.split('What I\'m looking for:')
                    if parts_split[0].strip():
                        story.append(Paragraph(f"  • {parts_split[0].strip()}", self.styles['CustomBullet']))
                    if len(parts_split) > 1 and parts_split[1].strip():
                        story.append(Paragraph(f"<i>What to focus on: {parts_split[1].strip()}</i>", self.styles['Normal']))
                else:
                    # Regular sub-content
                    story.append(Paragraph(f"  • {clean_part}", self.styles['CustomBullet']))
    
    def _add_code_fixes(self, story, analysis_result: Dict[str, Any]):
        """Add comprehensive code fixes from AI analysis"""
        story.append(Paragraph("Code Issues & Fixes", self.styles['CustomHeading']))
        
        # Show code issues first
        code_issues = analysis_result.get('code_issues', [])
        if code_issues:
            story.append(Paragraph("<b>Issues Found:</b>", self.styles['Heading2']))
            for issue in code_issues[:5]:  # Limit to first 5 issues
                clean_issue = self._clean_text(issue).replace('ERROR: ERROR:', 'ERROR:')
                story.append(Paragraph(f"• {clean_issue}", self.styles['CustomBullet']))
            story.append(Spacer(1, 12))
        
        # Extract and format code fixes from code_fixes array or overall assessment
        code_fixes_text = ''
        if analysis_result.get('code_fixes'):
            code_fixes_text = analysis_result['code_fixes'][0]  # Get the first (main) code fixes item
        elif '🔧' in analysis_result.get('overall_assessment', ''):
            code_fixes_text = analysis_result['overall_assessment']
        
        if code_fixes_text and '🔧' in code_fixes_text:
            story.append(Paragraph("<b>Specific Code Solutions:</b>", self.styles['Heading2']))
            
            # Split by the wrench emoji to get individual fixes
            fixes = code_fixes_text.split('🔧')
            for fix in fixes[1:]:  # Skip the first part (before first wrench)
                if fix.strip():
                    # Extract the title and code
                    lines = fix.strip().split('\n')
                    if lines:
                        title = lines[0].replace('*', '').strip().rstrip(':')
                        story.append(Paragraph(f"<b>{title}</b>", self.styles['Heading2']))
                        
                        # Extract R code blocks
                        in_code_block = False
                        code_lines = []
                        explanation_lines = []
                        
                        for line in lines[1:]:
                            line = line.strip()
                            if line.startswith('```r') or line == '```':
                                in_code_block = not in_code_block
                                continue
                            elif in_code_block:
                                if line and not line.startswith('#'):
                                    code_lines.append(line)
                                elif line.startswith('#'):
                                    code_lines.append(f"<i>{line}</i>")
                            elif line and not line.startswith('```'):
                                explanation_lines.append(line)
                        
                        # Add explanation with improved working directory guidance
                        if explanation_lines:
                            explanation = ' '.join(explanation_lines)
                            explanation = explanation.replace('# Make sure:', '<b>Make sure:</b>')
                            explanation = explanation.replace('# 1.', '<br/>1.')
                            explanation = explanation.replace('# 2.', '<br/>2.')
                            explanation = explanation.replace('# 3.', '<br/>3.')
                            story.append(Paragraph(explanation, self.styles['Normal']))
                            story.append(Spacer(1, 6))
                        
                        # Add working directory specific guidance for file path issues
                        if 'Data Import Fix' in title and 'File Not Found' in title:
                            wd_guidance = """<b>Working Directory Solutions:</b><br/>
                            <b>Option 1:</b> If your working directory is set to the data folder:<br/>
                            • Use: read_csv("sales_data.csv") - just the filename<br/>
                            <b>Option 2:</b> If your working directory is the project root:<br/>
                            • Use: read_csv("data/sales_data.csv") - include the data/ folder<br/>
                            <b>Check your setup:</b> Run getwd() to see where you are, then adjust your file paths accordingly."""
                            story.append(Paragraph(wd_guidance, self.styles['Normal']))
                            story.append(Spacer(1, 6))
                        
                        # Add code block
                        if code_lines:
                            # Create a code style
                            code_style = ParagraphStyle(
                                name='Code',
                                parent=self.styles['Normal'],
                                fontName='Courier',
                                fontSize=9,
                                leftIndent=20,
                                backgroundColor=colors.lightgrey,
                                borderWidth=1,
                                borderColor=colors.grey
                            )
                            
                            for code_line in code_lines:
                                story.append(Paragraph(code_line, code_style))
                            story.append(Spacer(1, 12))
        
        story.append(Spacer(1, 12))
    
    def _filter_instructor_feedback(self, feedback_text: str) -> str:
        """Filter feedback to include only instructor-relevant content - STRICT filtering"""
        if not feedback_text:
            return ""
        
        # First, try to extract JSON and use only structured content
        json_data = self._extract_json_from_response(feedback_text)
        if json_data:
            # If we have JSON, extract instructor comments from it
            if 'instructor_comments' in json_data:
                return self._clean_instructor_comments(json_data['instructor_comments'])
        
        # Fallback: aggressive filtering of raw text
        lines = feedback_text.split('\n')
        clean_lines = []
        
        # Skip everything that looks like internal AI reasoning
        for line in lines:
            line = line.strip()
            
            # Skip lines with internal AI patterns
            if any(pattern in line.lower() for pattern in [
                "we need to", "let's", "first, check", "now evaluate", "now assign",
                "now produce", "let's craft", "the student provided", "they have code",
                "did they complete", "the assignment required", "good.", "thus they",
                "reflection quality:", "business understanding:", "communication clarity:",
                "data interpretation:", "methodology appropriateness:", "overall score:",
                "maybe", "now produce json", "<|end|>", "<|start|>", "assistant", "channel",
                "final", "message"
            ]):
                continue
            
            # Skip empty lines or very short lines
            if len(line) < 15:
                continue
            
            # Skip lines that are clearly internal reasoning
            if line.startswith(("We ", "Let's ", "First ", "Now ", "The student ", "They ")):
                continue
            
            # Include lines that look like actual feedback
            if line and not any(skip_word in line.lower() for skip_word in [
                "evaluate", "assess", "check completeness", "assign scores", "craft feedback"
            ]):
                clean_lines.append(line)
        
        return ' '.join(clean_lines[:3])  # Limit to first 3 clean lines
    
    def _add_question_analysis(self, story, question_analysis: Dict[str, Any]):
        """Add clean reflection questions analysis - instructor feedback only"""
        story.append(Paragraph("Reflection Questions Feedback", self.styles['CustomHeading']))
        
        for q_key, q_data in question_analysis.items():
            question_title = q_key.replace('_', ' ').title()
            
            # Question header with score
            score_text = f"<b>{question_title}:</b> {q_data['score']:.1f}/{q_data['max_score']} points ({q_data['quality']})"
            story.append(Paragraph(score_text, self.styles['Heading2']))
            
            # Filter feedback for instructor-relevant content only
            if q_data.get('detailed_feedback'):
                clean_feedback = self._filter_instructor_feedback(q_data['detailed_feedback'])
                clean_feedback = self._clean_text(clean_feedback)
                
                if clean_feedback and len(clean_feedback) > 20:
                    story.append(Paragraph(clean_feedback, self.styles['Normal']))
                else:
                    # No fallback - AI must provide real feedback
                    logger.warning(f"No valid feedback for question {q_key} - AI needs to generate more verbose, personalized feedback")
                    story.append(Paragraph("Feedback not available - please regenerate with more verbose AI model.", self.styles['Normal']))
            
            story.append(Spacer(1, 12))
    
    def _add_comprehensive_feedback(self, story, comprehensive_feedback):
        """Add comprehensive feedback from Business Analytics Grader - instructor content only"""
        
        # Extract clean instructor comments from JSON structure only
        story.append(Paragraph("Instructor Assessment", self.styles['CustomHeading']))
        
        # PRIORITY: Use human feedback if available (from analysis_result passed to _add_comprehensive_feedback)
        # Note: This is a workaround - we need to pass analysis_result to this method
        # For now, check if instructor_comments was replaced by human feedback in the calling code
        
        # Try to extract structured feedback from the comprehensive feedback
        json_data = None
        if isinstance(comprehensive_feedback, dict):
            json_data = comprehensive_feedback
        elif isinstance(comprehensive_feedback, str):
            json_data = self._extract_json_from_response(comprehensive_feedback)
        
        if json_data and 'instructor_comments' in json_data:
            # Clean instructor comments - remove prompt text and artifacts
            raw_comments = json_data['instructor_comments']
            clean_comments = self._clean_instructor_comments_thoroughly(raw_comments)
            
            if clean_comments and len(clean_comments) > 30:
                story.append(self._safe_paragraph(clean_comments, self.styles['Normal']))
            else:
                logger.warning("Instructor comments too short or missing - AI needs to generate more verbose feedback")
                story.append(Paragraph("Instructor feedback not available - please regenerate with more verbose AI model settings.", self.styles['Normal']))
        else:
            # No valid instructor comments found - don't use fallback
            logger.warning("No instructor comments found in feedback - AI needs to generate comprehensive feedback")
            story.append(Paragraph("Instructor feedback not available - please regenerate with more verbose AI model settings.", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Extract detailed feedback from JSON structure if available
        if json_data and 'detailed_feedback' in json_data:
            detailed = json_data['detailed_feedback']
            
            # Reflection & Critical Thinking - PARAGRAPH FORMAT
            if 'reflection_assessment' in detailed and detailed['reflection_assessment']:
                story.append(Paragraph("Reflection & Critical Thinking", self.styles['CustomHeading']))
                
                clean_items = []
                for item in detailed['reflection_assessment']:
                    if isinstance(item, str) and len(item) > 20:
                        # Filter out AI reasoning patterns
                        if not any(pattern in item.lower() for pattern in [
                            "first, check", "part 1:", "part 2:", "part 3:", "part 4:", "part 5:",
                            "they did", "they completed", "they gave", "they answered", "good.",
                            "thus they", "now evaluate", "did they complete"
                        ]):
                            clean_item = self._clean_text(item)
                            if clean_item and len(clean_item) > 15:
                                clean_items.append(clean_item)
                
                # Convert bullets to paragraph - USE ALL ITEMS for detailed feedback
                if clean_items:
                    paragraph_text = " ".join(clean_items)  # Combine ALL items into one paragraph
                    story.append(Paragraph(paragraph_text, self.styles['Normal']))
                else:
                    story.append(Paragraph("The responses to the reflection questions demonstrate engagement with the assignment concepts and show developing analytical thinking.", self.styles['Normal']))
                
                story.append(Spacer(1, 15))
            
            # Analytical Strengths - PARAGRAPH FORMAT
            if 'analytical_strengths' in detailed and detailed['analytical_strengths']:
                story.append(Paragraph("Analytical Strengths", self.styles['CustomHeading']))
                
                clean_items = []
                for item in detailed['analytical_strengths']:
                    if isinstance(item, str) and len(item) > 20:
                        # Filter out AI reasoning
                        if not any(pattern in item.lower() for pattern in [
                            "first, check", "part 1:", "part 2:", "part 3:", "they did", "they completed",
                            "they computed", "they printed", "they wrote", "they also", "good.", "thus"
                        ]):
                            clean_item = self._clean_text(item)
                            if clean_item and len(clean_item) > 15:
                                clean_items.append(clean_item)
                
                # Convert bullets to paragraph - USE ALL ITEMS
                if clean_items:
                    paragraph_text = " ".join(clean_items)  # Combine ALL items
                    story.append(Paragraph(paragraph_text, self.styles['Normal']))
                else:
                    story.append(Paragraph("The student demonstrates solid analytical approach and technical execution throughout the assignment.", self.styles['Normal']))
                
                story.append(Spacer(1, 15))
            
            # Business Application - PARAGRAPH FORMAT
            if 'business_application' in detailed and detailed['business_application']:
                story.append(Paragraph("Business Application", self.styles['CustomHeading']))
                
                clean_items = []
                for item in detailed['business_application']:
                    if isinstance(item, str) and len(item) > 20:
                        clean_item = self._clean_text(item)
                        if clean_item and len(clean_item) > 15:
                            clean_items.append(clean_item)
                
                # Convert bullets to paragraph - USE ALL ITEMS
                if clean_items:
                    paragraph_text = " ".join(clean_items)  # Combine ALL items
                    story.append(Paragraph(paragraph_text, self.styles['Normal']))
                else:
                    story.append(Paragraph("The student shows understanding of business context and demonstrates awareness of practical applications.", self.styles['Normal']))
                
                story.append(Spacer(1, 15))
            
            # Learning Demonstration - PARAGRAPH FORMAT
            if 'learning_demonstration' in detailed and detailed['learning_demonstration']:
                story.append(Paragraph("Learning Demonstration", self.styles['CustomHeading']))
                
                clean_items = []
                for item in detailed['learning_demonstration']:
                    if isinstance(item, str) and len(item) > 20:
                        clean_item = self._clean_text(item)
                        if clean_item and len(clean_item) > 15:
                            clean_items.append(clean_item)
                
                # Convert bullets to paragraph - USE ALL ITEMS
                if clean_items:
                    paragraph_text = " ".join(clean_items)  # Combine ALL items
                    story.append(Paragraph(paragraph_text, self.styles['Normal']))
                else:
                    story.append(Paragraph("The student demonstrates developing competency in analytical methods and tools throughout the assignment.", self.styles['Normal']))
                
                story.append(Spacer(1, 15))
            
            # Areas for Development - STRUCTURED FORMAT
            if 'areas_for_development' in detailed and detailed['areas_for_development']:
                story.append(Paragraph("Areas for Development", self.styles['CustomHeading']))
                
                for item in detailed['areas_for_development']:
                    if isinstance(item, str) and len(item) > 15:
                        # Use structured formatter for WHAT/WHY/HOW/EXAMPLE
                        self._format_structured_feedback(item, story, 'Normal')
                
                if not detailed['areas_for_development']:
                    story.append(Paragraph("Continue developing analytical depth and technical documentation skills to strengthen future work.", self.styles['Normal']))
                
                story.append(Spacer(1, 15))
            
            # Recommendations - PARAGRAPH FORMAT
            if 'recommendations' in detailed and detailed['recommendations']:
                story.append(Paragraph("Recommendations for Future Work", self.styles['CustomHeading']))
                
                clean_items = []
                for item in detailed['recommendations']:
                    if isinstance(item, str) and len(item) > 15:
                        clean_item = self._clean_text(item)
                        if clean_item and len(clean_item) > 15:
                            clean_items.append(clean_item)
                
                # Convert bullets to paragraph - USE ALL ITEMS
                if clean_items:
                    paragraph_text = " ".join(clean_items)  # Combine ALL items
                    story.append(Paragraph(paragraph_text, self.styles['Normal']))
                else:
                    story.append(Paragraph("Continue practicing with diverse datasets and advanced analytical techniques to build on this foundation.", self.styles['Normal']))
                
                story.append(Spacer(1, 20))
    
    def _add_preprocessing_info(self, story, preprocessing: Dict[str, Any]):
        """Add preprocessing information if fixes were applied"""
        
        fixes_applied = preprocessing.get('fixes_applied', [])
        penalty_points = preprocessing.get('penalty_points', 0.0)
        
        # Only show preprocessing section if there are actual fixes with penalties
        if not fixes_applied or penalty_points == 0:
            return  # No relevant preprocessing to report
        
        story.append(Paragraph("Submission Preprocessing", self.styles['CustomHeading']))
        
        # Get penalty info
        penalty_points = preprocessing.get('penalty_points', 0.0)
        penalty_explanation = preprocessing.get('penalty_explanation', '')
        
        # Info box style
        if penalty_points > 0:
            info_text = f"Your submission was automatically normalized before grading to fix {len(fixes_applied)} syntax error(s). A penalty of {penalty_points:.1f} points was applied for these errors."
        else:
            info_text = f"Your submission was automatically normalized before grading to fix {len(fixes_applied)} style issue(s). No penalty was applied as these were formatting preferences, not syntax errors."
        
        story.append(Paragraph(info_text, self.styles['Normal']))
        story.append(Spacer(1, 8))
        
        # List fixes
        story.append(Paragraph("Fixes Applied:", self.styles['Heading2']))
        for fix in fixes_applied:
            clean_fix = self._clean_text(fix)
            story.append(Paragraph(f"• {clean_fix}", self.styles['CustomBullet']))
        
        story.append(Spacer(1, 12))
        
        # Show penalty breakdown if applicable
        if penalty_points > 0:
            penalty_style = ParagraphStyle(
                name='PenaltyStyle',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#721c24'),
                backgroundColor=colors.HexColor('#f8d7da'),
                borderWidth=1,
                borderColor=colors.HexColor('#f5c6cb'),
                leftIndent=10,
                rightIndent=10,
                spaceAfter=12
            )
            story.append(Paragraph(
                self._clean_text(penalty_explanation),
                penalty_style
            ))
        
        # Add note if manual review flagged
        if preprocessing.get('needs_manual_review'):
            note_style = ParagraphStyle(
                name='NoteStyle',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#856404'),
                backgroundColor=colors.HexColor('#fff3cd'),
                borderWidth=1,
                borderColor=colors.HexColor('#ffc107'),
                leftIndent=10,
                rightIndent=10,
                spaceAfter=12
            )
            story.append(Paragraph(
                "Note: Multiple preprocessing fixes were needed. Your instructor may review this submission manually to ensure accuracy.",
                note_style
            ))
        
        # Add output comparison results if available
        output_comparison = preprocessing.get('output_comparison')
        if output_comparison and output_comparison.get('total_comparisons', 0) > 0:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Output Verification:", self.styles['Heading2']))
            
            match_rate = output_comparison.get('match_rate', 0)
            matches = output_comparison.get('matches', 0)
            total = output_comparison.get('total_comparisons', 0)
            
            if match_rate >= 90:
                icon = "✅"
                color = colors.HexColor('#155724')
            elif match_rate >= 75:
                icon = "⚠️"
                color = colors.HexColor('#856404')
            else:
                icon = "❌"
                color = colors.HexColor('#721c24')
            
            comparison_style = ParagraphStyle(
                name='ComparisonStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=color,
                spaceAfter=6
            )
            
            story.append(Paragraph(
                f"{icon} {matches}/{total} outputs match solution ({match_rate:.1f}%)",
                comparison_style
            ))
            
            # Show mismatches if any
            mismatches = output_comparison.get('mismatch_details', [])
            if mismatches:
                story.append(Paragraph(f"Output differences detected in {len(mismatches)} section(s)", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    def _add_technical_analysis(self, story, technical_analysis: Dict[str, Any]):
        """Add technical analysis from Business Analytics Grader with code examples"""
        
        story.append(Paragraph("Technical Analysis", self.styles['CustomHeading']))
        
        # Code Strengths
        if 'code_strengths' in technical_analysis and technical_analysis['code_strengths']:
            story.append(Paragraph("Code Strengths:", self.styles['Heading2']))
            for item in technical_analysis['code_strengths']:
                clean_item = self._clean_text(item)
                story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
            story.append(Spacer(1, 12))
        
        # Code Suggestions with Examples
        if 'code_suggestions' in technical_analysis and technical_analysis['code_suggestions']:
            story.append(Paragraph("Code Improvement Suggestions:", self.styles['Heading2']))
            
            # Create a code style for examples
            code_style = ParagraphStyle(
                name='CodeExample',
                parent=self.styles['Normal'],
                fontName='Courier',
                fontSize=9,
                leftIndent=30,
                backgroundColor=colors.lightgrey,
                borderWidth=1,
                borderColor=colors.grey,
                spaceAfter=6
            )
            
            for item in technical_analysis['code_suggestions']:
                if isinstance(item, str) and len(item) > 15:
                    # Use structured formatter for WHAT/WHY/HOW/EXAMPLE
                    self._format_structured_feedback(item, story, 'Normal')
                
                # Add code examples for common suggestions
                if 'complete.cases()' in item:
                    story.append(Paragraph("Example:", self.styles['Normal']))
                    story.append(Paragraph("# Remove rows with missing values", code_style))
                    story.append(Paragraph("clean_data <- sales_df[complete.cases(sales_df), ]", code_style))
                    story.append(Paragraph("# Or check for missing values first", code_style))
                    story.append(Paragraph("sum(is.na(sales_df))", code_style))
                
                elif 'cut()' in item:
                    story.append(Paragraph("Example:", self.styles['Normal']))
                    story.append(Paragraph("# Create categorical variables from continuous data", code_style))
                    story.append(Paragraph("sales_df$amount_category <- cut(sales_df$amount,", code_style))
                    story.append(Paragraph("    breaks = c(0, 100, 500, 1000, Inf),", code_style))
                    story.append(Paragraph("    labels = c('Low', 'Medium', 'High', 'Very High'))", code_style))
                
                elif 'cor()' in item:
                    story.append(Paragraph("Example:", self.styles['Normal']))
                    story.append(Paragraph("# Calculate correlation between numeric variables", code_style))
                    story.append(Paragraph("cor(sales_df$amount, sales_df$rating, use = 'complete.obs')", code_style))
                    story.append(Paragraph("# Or correlation matrix", code_style))
                    story.append(Paragraph("cor(sales_df[, c('amount', 'rating', 'quantity')])", code_style))
                
                elif 'standard deviation' in item or 'quartiles' in item:
                    story.append(Paragraph("Example:", self.styles['Normal']))
                    story.append(Paragraph("# Additional summary statistics", code_style))
                    story.append(Paragraph("sd(sales_df$amount, na.rm = TRUE)  # Standard deviation", code_style))
                    story.append(Paragraph("quantile(sales_df$amount, na.rm = TRUE)  # Quartiles", code_style))
                    story.append(Paragraph("IQR(sales_df$amount, na.rm = TRUE)  # Interquartile range", code_style))
                
                elif 'read_csv()' in item or 'portable' in item:
                    story.append(Paragraph("Example:", self.styles['Normal']))
                    story.append(Paragraph("# More portable approach (no setwd needed)", code_style))
                    story.append(Paragraph("library(here)", code_style))
                    story.append(Paragraph("sales_df <- read_csv(here('data', 'sales_data.csv'))", code_style))
                    story.append(Paragraph("# Or use relative paths", code_style))
                    story.append(Paragraph("sales_df <- read_csv('data/sales_data.csv')", code_style))
                
                story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 12))
        
        # Technical Observations
        if 'technical_observations' in technical_analysis and technical_analysis['technical_observations']:
            story.append(Paragraph("Technical Observations:", self.styles['Heading2']))
            for item in technical_analysis['technical_observations']:
                clean_item = self._clean_text(item)
                story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
            story.append(Spacer(1, 12))
        
        # Add general code improvement examples
        story.append(Paragraph("Additional Code Enhancement Examples:", self.styles['Heading2']))
        
        code_style = ParagraphStyle(
            name='CodeExample',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=30,
            backgroundColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.grey,
            spaceAfter=6
        )
        
        story.append(Paragraph("**Data Exploration Enhancement:**", self.styles['Normal']))
        story.append(Paragraph("# More comprehensive data inspection", code_style))
        story.append(Paragraph("glimpse(sales_df)  # dplyr alternative to str()", code_style))
        story.append(Paragraph("skimr::skim(sales_df)  # Detailed summary statistics", code_style))
        story.append(Paragraph("DataExplorer::plot_missing(sales_df)  # Visualize missing data", code_style))
        story.append(Spacer(1, 8))
        
        story.append(Paragraph("**Data Visualization:**", self.styles['Normal']))
        story.append(Paragraph("# Basic plots for data exploration", code_style))
        story.append(Paragraph("ggplot(sales_df, aes(x = amount)) + geom_histogram()", code_style))
        story.append(Paragraph("ggplot(sales_df, aes(x = category, y = amount)) + geom_boxplot()", code_style))
        story.append(Spacer(1, 8))
        
        story.append(Paragraph("**Data Cleaning:**", self.styles['Normal']))
        story.append(Paragraph("# Handle missing values", code_style))
        story.append(Paragraph("sales_df <- sales_df %>%", code_style))
        story.append(Paragraph("  filter(!is.na(amount)) %>%", code_style))
        story.append(Paragraph("  mutate(amount = ifelse(amount < 0, 0, amount))", code_style))
        
        story.append(Spacer(1, 20))
    
    def _add_recommendations(self, story, analysis_result: Dict[str, Any]):
        """Add clean recommendations section"""
        
        # Only add this section if we don't have comprehensive feedback (legacy support)
        if 'comprehensive_feedback' in analysis_result:
            return  # Skip legacy recommendations if we have comprehensive feedback
        
        story.append(Paragraph("Next Steps", self.styles['CustomHeading']))
        
        # Clean overall assessment (remove AI debugging text)
        if 'overall_assessment' in analysis_result:
            assessment = self._clean_text(analysis_result['overall_assessment'])
            # Remove AI debugging sections
            assessment_lines = assessment.split('\n')
            clean_lines = []
            skip_ai_section = False
            
            for line in assessment_lines:
                if any(ai_term in line.lower() for ai_term in ['ai enhancement', 'ai analysis', 'ai-generated', 'we need to']):
                    skip_ai_section = True
                    continue
                if not skip_ai_section and line.strip() and not line.startswith('■'):
                    clean_lines.append(line.strip())
            
            if clean_lines:
                clean_assessment = ' '.join(clean_lines)
                story.append(Paragraph(clean_assessment, self.styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Study tips based on performance
        total_score = analysis_result.get('total_score', 0)
        max_score = analysis_result.get('max_score', 37.5)
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        story.append(Paragraph("Study Tips:", self.styles['Heading2']))
        
        if percentage < 70:
            tips = [
                "Review the lecture notebook and practice running the examples yourself",
                "Make sure to execute all code cells and check for outputs",
                "Focus on understanding the fundamental concepts before moving to advanced topics"
            ]
        elif percentage < 85:
            tips = [
                "Good foundation! Focus on providing more detailed explanations in reflection questions",
                "Practice connecting technical concepts to business applications"
            ]
        else:
            tips = [
                "Excellent work! Consider exploring additional data analysis techniques",
                "Try applying these concepts to your own datasets"
            ]
        
        for tip in tips:
            story.append(Paragraph(f"• {tip}", self.styles['CustomBullet']))
        
        # Clean ending
        story.append(Spacer(1, 20))    
    
def _add_recommendations(self, story, analysis_result: Dict[str, Any]):
        """Add final recommendations section - instructor content only"""
        
        # Check if we have recommendations in various places
        recommendations = []
        
        # From comprehensive feedback
        if 'comprehensive_feedback' in analysis_result:
            comp_feedback = analysis_result['comprehensive_feedback']
            if 'detailed_feedback' in comp_feedback:
                detailed = comp_feedback['detailed_feedback']
                if 'recommendations' in detailed:
                    recommendations.extend(detailed['recommendations'])
        
        # From technical analysis
        if 'technical_analysis' in analysis_result:
            tech_analysis = analysis_result['technical_analysis']
            if 'recommendations' in tech_analysis:
                recommendations.extend(tech_analysis['recommendations'])
        
        # From overall assessment
        if 'recommendations' in analysis_result:
            recommendations.extend(analysis_result['recommendations'])
        
        # Add recommendations section if we have any
        if recommendations:
            story.append(Paragraph("Next Steps & Recommendations", self.styles['CustomHeading']))
            
            for rec in recommendations[:5]:  # Limit to top 5 recommendations
                filtered_rec = self._filter_instructor_feedback(rec)
                clean_rec = self._clean_text(filtered_rec)
                
                if clean_rec and len(clean_rec) > 15:
                    story.append(Paragraph(f"• {clean_rec}", self.styles['CustomBullet']))
            
            story.append(Spacer(1, 20))
        
        # Add footer
        story.append(Paragraph("---", self.styles['Normal']))
        story.append(Paragraph(
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Normal']
        ))