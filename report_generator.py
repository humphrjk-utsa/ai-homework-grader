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
from datetime import datetime
from typing import Dict, Any

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
    
    def _clean_text(self, text: str) -> str:
        """Clean text for PDF generation - simple removal approach"""
        if not isinstance(text, str):
            text = str(text)
        
        # Simply remove problematic characters - don't replace with brackets
        emoji_pattern = r'[📋📈🗂️📦🔍📚✅❌🔧💭📝👍⚠️■▪▫●○]'
        text = re.sub(emoji_pattern, '', text)
        
        # Remove markdown formatting
        text = text.replace('**', '')  # Remove markdown bold
        text = text.replace('*', '')   # Remove markdown italic
        
        # Clean up extra whitespace and multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def generate_report(self, student_name: str, assignment_id: str, analysis_result: Dict[str, Any]) -> str:
        """Generate a PDF report for a graded submission with comprehensive feedback"""
        
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
        
        # Add content in clean, organized sections
        self._add_header(story, safe_student_name, assignment_id, analysis_result)
        self._add_score_summary(story, analysis_result)
        
        # Add comprehensive feedback from Business Analytics Grader
        if 'comprehensive_feedback' in analysis_result:
            self._add_comprehensive_feedback(story, analysis_result['comprehensive_feedback'])
        
        # Add technical analysis
        if 'technical_analysis' in analysis_result:
            self._add_technical_analysis(story, analysis_result['technical_analysis'])
        
        # Legacy support for older format
        self._add_detailed_breakdown(story, analysis_result)
        
        # Add code fixes if there are issues
        if analysis_result.get('code_issues'):
            self._add_code_fixes(story, analysis_result)
        
        if 'question_analysis' in analysis_result:
            self._add_question_analysis(story, analysis_result['question_analysis'])
        
        self._add_recommendations(story, analysis_result)
        
        # Build PDF
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
    
    def _add_score_summary(self, story, analysis_result: Dict[str, Any]):
        """Add score summary section"""
        story.append(Paragraph("Score Summary", self.styles['CustomHeading']))
        
        # Overall performance
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
    
    def _add_question_analysis(self, story, question_analysis: Dict[str, Any]):
        """Add clean reflection questions analysis"""
        story.append(Paragraph("Reflection Questions Feedback", self.styles['CustomHeading']))
        
        for q_key, q_data in question_analysis.items():
            question_title = q_key.replace('_', ' ').title()
            
            # Question header with score
            score_text = f"<b>{question_title}:</b> {q_data['score']:.1f}/{q_data['max_score']} points ({q_data['quality']})"
            story.append(Paragraph(score_text, self.styles['Heading2']))
            
            # Clean feedback only (remove "What I'm looking for" sections)
            if q_data.get('detailed_feedback'):
                feedback = self._clean_text(q_data['detailed_feedback'])
                # Extract only the personalized feedback, not the template text
                feedback_lines = feedback.split('\n')
                clean_lines = []
                skip_template = False
                
                for line in feedback_lines:
                    if "What I'm looking for:" in line or "What to focus on:" in line:
                        skip_template = True
                        continue
                    if not skip_template and line.strip():
                        clean_lines.append(line.strip())
                
                if clean_lines:
                    story.append(Paragraph(' '.join(clean_lines), self.styles['Normal']))
            
            story.append(Spacer(1, 12))
    
    def _add_comprehensive_feedback(self, story, comprehensive_feedback: Dict[str, Any]):
        """Add comprehensive feedback from Business Analytics Grader"""
        
        # Overall instructor comments
        if 'instructor_comments' in comprehensive_feedback:
            story.append(Paragraph("Instructor Assessment", self.styles['CustomHeading']))
            comments = self._clean_text(comprehensive_feedback['instructor_comments'])
            story.append(Paragraph(comments, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Detailed feedback sections
        if 'detailed_feedback' in comprehensive_feedback:
            detailed = comprehensive_feedback['detailed_feedback']
            
            # Reflection & Critical Thinking
            if 'reflection_assessment' in detailed and detailed['reflection_assessment']:
                story.append(Paragraph("Reflection & Critical Thinking", self.styles['CustomHeading']))
                for item in detailed['reflection_assessment']:
                    clean_item = self._clean_text(item)
                    story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
                story.append(Spacer(1, 15))
            
            # Analytical Strengths
            if 'analytical_strengths' in detailed and detailed['analytical_strengths']:
                story.append(Paragraph("Analytical Strengths", self.styles['CustomHeading']))
                for item in detailed['analytical_strengths']:
                    clean_item = self._clean_text(item)
                    story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
                story.append(Spacer(1, 15))
            
            # Business Application
            if 'business_application' in detailed and detailed['business_application']:
                story.append(Paragraph("Business Application", self.styles['CustomHeading']))
                for item in detailed['business_application']:
                    clean_item = self._clean_text(item)
                    story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
                story.append(Spacer(1, 15))
            
            # Learning Demonstration
            if 'learning_demonstration' in detailed and detailed['learning_demonstration']:
                story.append(Paragraph("Learning Demonstration", self.styles['CustomHeading']))
                for item in detailed['learning_demonstration']:
                    clean_item = self._clean_text(item)
                    story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
                story.append(Spacer(1, 15))
            
            # Areas for Development
            if 'areas_for_development' in detailed and detailed['areas_for_development']:
                story.append(Paragraph("Areas for Development", self.styles['CustomHeading']))
                for item in detailed['areas_for_development']:
                    clean_item = self._clean_text(item)
                    story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
                story.append(Spacer(1, 15))
            
            # Recommendations
            if 'recommendations' in detailed and detailed['recommendations']:
                story.append(Paragraph("Recommendations for Future Work", self.styles['CustomHeading']))
                for item in detailed['recommendations']:
                    clean_item = self._clean_text(item)
                    story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
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
                clean_item = self._clean_text(item)
                story.append(Paragraph(f"• {clean_item}", self.styles['CustomBullet']))
                
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