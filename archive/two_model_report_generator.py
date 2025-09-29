#!/usr/bin/env python3
"""
Enhanced PDF Report Generator for Two-Model Grading System
Formats comprehensive feedback from Qwen 3.0 Coder + GPT-OSS-120B
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import re
from datetime import datetime
from typing import Dict, Any, List

class TwoModelReportGenerator:
    """Generate professional PDF reports for two-model grading system"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up enhanced styles
        self.styles = getSampleStyleSheet()
        
        # Helper function to safely add styles
        def safe_add_style(name, style):
            if name not in self.styles:
                self.styles.add(style)
        
        # Custom title style
        safe_add_style('ReportTitle', ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section headers
        safe_add_style('SectionHeader', ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=5
        ))
        
        # Subsection headers
        safe_add_style('SubsectionHeader', ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.darkgreen
        ))
        
        # Body text
        safe_add_style('TwoModelBodyText', ParagraphStyle(
            name='TwoModelBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
        
        # Bullet points
        safe_add_style('TwoModelBulletPoint', ParagraphStyle(
            name='TwoModelBulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6
        ))
        
        # Code style
        safe_add_style('TwoModelCodeBlock', ParagraphStyle(
            name='TwoModelCodeBlock',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            spaceBefore=10,
            backColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=8
        ))
        
        # Encouragement style
        safe_add_style('TwoModelEncouragement', ParagraphStyle(
            name='TwoModelEncouragement',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=10,
            textColor=colors.darkgreen,
            backColor=colors.lightgreen,
            borderWidth=1,
            borderColor=colors.green,
            borderPadding=10,
            alignment=TA_JUSTIFY
        ))
    
    def _clean_text(self, text: str) -> str:
        """Clean text for PDF generation"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove emojis and special characters
        emoji_pattern = r'[📋📈🗂️📦🔍📚✅❌🔧💭📝👍⚠️■▪▫●○🤖🎉🚀📊⏱️🔄]'
        text = re.sub(emoji_pattern, '', text)
        
        # Clean markdown
        text = text.replace('**', '')
        text = text.replace('*', '')
        text = text.replace('`', '')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def generate_two_model_report(self, student_name: str, assignment_info: Dict, 
                                 grading_result: Dict[str, Any]) -> str:
        """Generate comprehensive PDF report from two-model grading system"""
        
        # Create filename
        safe_student_name = student_name or "Unknown_Student"
        safe_name = re.sub(r'[^\w\s-]', '', safe_student_name).replace(' ', '_')
        filename = f"{safe_name}_two_model_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create assignment folder
        assignment_folder = self._get_assignment_folder(assignment_info.get('title', 'Assignment'))
        filepath = os.path.join(assignment_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Build report sections
        self._add_report_header(story, safe_student_name, assignment_info, grading_result)
        self._add_score_overview(story, grading_result)
        self._add_technical_analysis(story, grading_result)
        self._add_educational_feedback(story, grading_result)
        self._add_element_breakdown(story, grading_result)
        self._add_performance_stats(story, grading_result)
        self._add_next_steps(story, grading_result)
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _get_assignment_folder(self, assignment_title: str) -> str:
        """Create assignment-specific folder"""
        clean_title = re.sub(r'[^\w\s-]', '', assignment_title).replace(' ', '_')
        assignment_folder = os.path.join(self.output_dir, clean_title)
        os.makedirs(assignment_folder, exist_ok=True)
        return assignment_folder
    
    def _add_report_header(self, story: List, student_name: str, assignment_info: Dict, 
                          grading_result: Dict):
        """Add professional report header"""
        # Main title
        story.append(Paragraph("Homework Grading Report", self.styles['ReportTitle']))
        story.append(Spacer(1, 20))
        
        # Student and assignment info
        score = grading_result.get('score', 0)
        max_score = grading_result.get('max_score', 37.5)
        percentage = grading_result.get('percentage', 0)
        
        info_data = [
            ['Student Name:', self._clean_text(student_name)],
            ['Assignment:', self._clean_text(assignment_info.get('title', 'Assignment'))],
            ['Graded On:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Course:', 'Data Management'],
            ['Final Score:', f"{score:.1f} / {max_score} points ({percentage:.1f}%)"]
        ]
        
        table = Table(info_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 25))
    
    def _add_score_overview(self, story: List, grading_result: Dict):
        """Add score overview section"""
        story.append(Paragraph("Score Overview", self.styles['SectionHeader']))
        
        score = grading_result.get('score', 0)
        max_score = grading_result.get('max_score', 37.5)
        percentage = grading_result.get('percentage', 0)
        
        # Performance level
        if percentage >= 90:
            performance = "Excellent"
            color = colors.darkgreen
        elif percentage >= 80:
            performance = "Good"
            color = colors.green
        elif percentage >= 70:
            performance = "Satisfactory"
            color = colors.orange
        else:
            performance = "Needs Improvement"
            color = colors.red
        
        overview_text = f"<b>Overall Performance:</b> <font color='{color.hexval()}'>{performance} ({percentage:.1f}%)</font>"
        story.append(Paragraph(overview_text, self.styles['TwoModelBodyText']))
        story.append(Spacer(1, 15))
        
        # Assignment overview
        overview_text = """<b>Assignment Overview:</b> This report provides comprehensive feedback on your 
        R programming assignment, including technical analysis of your code implementation and educational 
        guidance to support your continued learning in data analytics."""
        story.append(Paragraph(overview_text, self.styles['TwoModelBodyText']))
        story.append(Spacer(1, 20))
    
    def _add_technical_analysis(self, story: List, grading_result: Dict):
        """Add technical analysis section"""
        story.append(Paragraph("Technical Analysis", self.styles['SectionHeader']))
        
        # Get code analysis from the result
        code_analysis = grading_result.get('code_analysis', {})
        technical_summary = code_analysis.get('technical_summary', {})
        
        if technical_summary:
            # Technical scores
            syntax_score = technical_summary.get('syntax_score', 0)
            implementation_score = technical_summary.get('implementation_score', 0)
            correctness_score = technical_summary.get('correctness_score', 0)
            
            tech_data = [
                ['Syntax & Structure:', f"{syntax_score}/10"],
                ['Implementation Quality:', f"{implementation_score}/10"],
                ['Correctness & Logic:', f"{correctness_score}/10"]
            ]
            
            tech_table = Table(tech_data, colWidths=[3*inch, 1.5*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(tech_table)
            story.append(Spacer(1, 15))
        
        # Technical findings
        findings = code_analysis.get('detailed_findings', [])
        if findings:
            story.append(Paragraph("Technical Findings:", self.styles['SubsectionHeader']))
            for finding in findings[:5]:  # Limit to top 5 findings
                clean_finding = self._clean_text(str(finding))
                story.append(Paragraph(f"• {clean_finding}", self.styles['BulletPoint']))
            story.append(Spacer(1, 15))
    
    def _add_educational_feedback(self, story: List, grading_result: Dict):
        """Add educational feedback section"""
        story.append(Paragraph("Detailed Feedback", self.styles['SectionHeader']))
        
        # Get feedback from the grading result
        feedback_lines = grading_result.get('feedback', [])
        comp_feedback = grading_result.get('comprehensive_feedback', {})
        
        # Display the main feedback content
        if feedback_lines:
            current_section = None
            for line in feedback_lines:
                clean_line = self._clean_text(str(line))
                
                # Skip the system header lines
                if 'TWO-MODEL GRADING SYSTEM' in clean_line or 'Technical Analysis' in clean_line:
                    continue
                
                # Handle section headers
                if clean_line.startswith('**') and clean_line.endswith(':**'):
                    section_title = clean_line.replace('**', '').replace(':', '')
                    story.append(Paragraph(section_title, self.styles['SubsectionHeader']))
                    current_section = section_title
                elif clean_line.startswith('**') and clean_line.endswith('**'):
                    section_title = clean_line.replace('**', '')
                    story.append(Paragraph(section_title, self.styles['SubsectionHeader']))
                    current_section = section_title
                elif clean_line.startswith('•'):
                    # Bullet point
                    story.append(Paragraph(clean_line, self.styles['TwoModelBulletPoint']))
                elif clean_line.strip():
                    # Regular content
                    story.append(Paragraph(clean_line, self.styles['TwoModelBodyText']))
            
            story.append(Spacer(1, 15))
        
        # Fallback to comprehensive feedback if main feedback is empty
        elif comp_feedback:
            # Overall assessment
            overall = comp_feedback.get('overall_assessment', '')
            if overall:
                story.append(Paragraph("Overall Assessment:", self.styles['SubsectionHeader']))
                story.append(Paragraph(self._clean_text(overall), self.styles['TwoModelBodyText']))
                story.append(Spacer(1, 10))
            
            # Strengths
            strengths = comp_feedback.get('technical_strengths', []) + comp_feedback.get('conceptual_strengths', [])
            if strengths:
                story.append(Paragraph("Strengths Identified:", self.styles['SubsectionHeader']))
                for strength in strengths:
                    clean_strength = self._clean_text(str(strength))
                    story.append(Paragraph(f"• {clean_strength}", self.styles['TwoModelBulletPoint']))
                story.append(Spacer(1, 10))
            
            # Priority improvements
            improvements = comp_feedback.get('priority_improvements', [])
            if improvements:
                story.append(Paragraph("Areas for Improvement:", self.styles['SubsectionHeader']))
                for improvement in improvements:
                    clean_improvement = self._clean_text(str(improvement))
                    story.append(Paragraph(f"• {clean_improvement}", self.styles['TwoModelBulletPoint']))
                story.append(Spacer(1, 10))
    
    def _add_element_breakdown(self, story: List, grading_result: Dict):
        """Add detailed element breakdown"""
        element_breakdown = grading_result.get('element_breakdown', {})
        
        if element_breakdown:
            story.append(Paragraph("Detailed Element Scores", self.styles['SectionHeader']))
            
            # Create table data
            table_data = [['Element', 'Score', 'Max Points', 'Percentage']]
            
            for element_name, element_data in element_breakdown.items():
                if isinstance(element_data, dict):
                    score = element_data.get('score', 0)
                    max_points = element_data.get('max_points', 0)
                    percentage = (score / max_points * 100) if max_points > 0 else 0
                    
                    # Clean element name
                    clean_name = element_name.replace('_', ' ').title()
                    
                    table_data.append([
                        clean_name,
                        f"{score:.1f}",
                        f"{max_points}",
                        f"{percentage:.1f}%"
                    ])
            
            if len(table_data) > 1:  # Has data beyond header
                element_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
                element_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                story.append(element_table)
                story.append(Spacer(1, 20))
    
    def _add_performance_stats(self, story: List, grading_result: Dict):
        """Add performance statistics - removed to keep report clean"""
        # Skip performance stats in student-facing report
        pass
    
    def _add_next_steps(self, story: List, grading_result: Dict):
        """Add next steps and encouragement"""
        story.append(Paragraph("Next Steps & Encouragement", self.styles['SectionHeader']))
        
        # Get encouragement from comprehensive feedback
        comp_feedback = grading_result.get('comprehensive_feedback', {})
        encouragement = grading_result.get('encouragement', '')
        next_steps = comp_feedback.get('next_steps', [])
        
        if encouragement:
            clean_encouragement = self._clean_text(encouragement)
            story.append(Paragraph(clean_encouragement, self.styles['TwoModelEncouragement']))
            story.append(Spacer(1, 15))
        
        if next_steps:
            story.append(Paragraph("Recommended Next Steps:", self.styles['SubsectionHeader']))
            for step in next_steps:
                clean_step = self._clean_text(str(step))
                story.append(Paragraph(f"• {clean_step}", self.styles['TwoModelBulletPoint']))
            story.append(Spacer(1, 15))
        
        # Footer message
        footer_text = """
        <b>About This Report:</b> This comprehensive evaluation provides detailed feedback on your 
        assignment to support your continued learning in data analytics. Keep up the excellent work!
        """
        story.append(Paragraph(footer_text, self.styles['TwoModelBodyText']))

def generate_two_model_pdf_report(student_name: str, assignment_info: Dict, 
                                 grading_result: Dict[str, Any], output_dir: str = "reports") -> str:
    """Convenience function to generate a two-model PDF report"""
    generator = TwoModelReportGenerator(output_dir)
    return generator.generate_two_model_report(student_name, assignment_info, grading_result)