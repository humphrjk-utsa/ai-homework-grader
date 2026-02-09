#!/usr/bin/env python3
"""
PDF Report Generator for AI Homework Grader
Produces section-by-section grading reports with specific feedback and deduction notes.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate section-by-section PDF grading reports"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.styles.add(ParagraphStyle(
            name='ReportTitle', parent=self.styles['Title'],
            fontSize=16, spaceAfter=20, alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeading', parent=self.styles['Heading1'],
            fontSize=13, spaceAfter=10, spaceBefore=14, textColor=colors.HexColor('#1a3a5c')
        ))
        self.styles.add(ParagraphStyle(
            name='SubHeading', parent=self.styles['Heading2'],
            fontSize=11, spaceAfter=6, spaceBefore=8, textColor=colors.HexColor('#2c5282')
        ))
        self.styles['BodyText'].fontSize = 10
        self.styles['BodyText'].spaceAfter = 6
        self.styles['BodyText'].leading = 14
        self.styles.add(ParagraphStyle(
            name='BulletItem', parent=self.styles['Normal'],
            fontSize=10, spaceAfter=4, leading=13, leftIndent=15, bulletIndent=5
        ))
        self.styles.add(ParagraphStyle(
            name='NumberedItem', parent=self.styles['Normal'],
            fontSize=10, spaceAfter=6, leading=13, leftIndent=15
        ))
        self.styles.add(ParagraphStyle(
            name='SmallNote', parent=self.styles['Normal'],
            fontSize=8, textColor=colors.grey, spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name='TableCell', parent=self.styles['Normal'],
            fontSize=8, leading=10
        ))

    # ── Utilities ──────────────────────────────────────────────────────

    def _clean(self, text: str) -> str:
        """Clean text for PDF: remove emojis, unicode artifacts, markdown"""
        if not text or not isinstance(text, str):
            return ""
        # Replace special dashes
        for ch in '\u2010\u2011\u2012\u2013\u2014\u2015':
            text = text.replace(ch, '-')
        # Remove problematic unicode ranges
        text = re.sub(r'[\u2500-\u257F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF]', '', text)
        # Remove emojis
        text = re.sub(r'[📋📈🗂️📦🔍📚🔧💭📝👍🤔💡🎯📊🚀⚡🎉🔥💪🎓✅❌⚠️✓✔●○•■▪▫]', '', text)
        # Replace smart quotes
        for old, new in {'\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"'}.items():
            text = text.replace(old, new)
        # Remove markdown bold/code markers
        text = text.replace('**', '').replace('```', '').replace('`', "'")
        return ' '.join(text.split())

    def _safe_para(self, text: str, style_name: str = 'BodyText') -> Paragraph:
        """Create a safe Paragraph, escaping XML special chars"""
        clean = self._clean(text) or ""
        # Escape XML special characters for reportlab
        clean = clean.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return Paragraph(clean, self.styles[style_name])

    def _xml_escape(self, text: str) -> str:
        """Escape XML special chars for use inside Paragraph markup"""
        if not text:
            return ""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def _get_assignment_folder(self, assignment_id: str) -> str:
        clean = re.sub(r'[^\w\s-]', '', assignment_id).replace(' ', '_')
        folder = os.path.join(self.output_dir, clean)
        os.makedirs(folder, exist_ok=True)
        return folder

    # ── Main Entry Point ──────────────────────────────────────────────

    def generate_report(self, student_name: str, assignment_id: str,
                        analysis_result: Dict[str, Any]) -> str:
        """Generate a section-by-section PDF grading report."""
        safe_name = re.sub(r'[^\w\s-]', '', student_name or "Unknown").replace(' ', '_')
        filename = f"{safe_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        folder = self._get_assignment_folder(assignment_id)
        filepath = os.path.join(folder, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []

        total_score = analysis_result.get('total_score', 0)
        max_score = analysis_result.get('max_score', 100)
        pct = (total_score / max_score * 100) if max_score > 0 else 0

        # ── Header ──
        self._add_header(story, student_name, assignment_id, total_score, max_score, pct)

        # ── Section Breakdown Table ──
        validation = analysis_result.get('validation_results', {})
        sys_results = validation.get('systematic_results', {})
        section_breakdown = sys_results.get('section_breakdown', {})

        if section_breakdown:
            self._add_section_table(story, section_breakdown, total_score, max_score, pct)

        # ── Horizontal rule ──
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e0')))
        story.append(Spacer(1, 10))

        # ── Detailed Feedback ──
        comp_feedback = analysis_result.get('comprehensive_feedback', {})
        tech_analysis = analysis_result.get('technical_analysis', {})
        self._add_detailed_feedback(story, comp_feedback, tech_analysis, section_breakdown)

        # ── Technical Stats (compact) ──
        self._add_technical_stats(story, validation, section_breakdown)

        # ── Footer ──
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e0')))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"Report generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')} "
            f"by AI Homework Grading System",
            self.styles['SmallNote']
        ))

        doc.build(story)
        return filepath

    # ── Header ────────────────────────────────────────────────────────

    def _add_header(self, story, student_name, assignment_id,
                    total_score, max_score, pct):
        story.append(Paragraph("Homework Grading Report", self.styles['ReportTitle']))
        story.append(Spacer(1, 10))

        letter_grade = self._letter_grade(pct)
        grade_text = self._xml_escape(f"{total_score:.1f} / {max_score:.0f}  ({pct:.0f}%)  {letter_grade}")
        data = [
            ['Student:', self._xml_escape(self._clean(student_name))],
            ['Assignment:', self._xml_escape(self._clean(assignment_id))],
            ['Date:', datetime.now().strftime('%B %d, %Y')],
            ['Grade:', grade_text],
        ]
        t = Table(data, colWidths=[1.5*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))

    def _letter_grade(self, pct):
        if pct >= 93: return "A"
        if pct >= 90: return "A-"
        if pct >= 87: return "B+"
        if pct >= 83: return "B"
        if pct >= 80: return "B-"
        if pct >= 77: return "C+"
        if pct >= 73: return "C"
        if pct >= 70: return "C-"
        if pct >= 60: return "D"
        return "F"

    # ── Section Breakdown Table ───────────────────────────────────────

    def _add_section_table(self, story, section_breakdown, total_score, max_score, pct):
        story.append(Paragraph("Section Breakdown", self.styles['SectionHeading']))

        header = ['Section', 'Points', 'Earned', 'Notes']
        table_data = [header]

        # Track numeric values for color-coding (separate from display)
        earned_numeric = []

        for sec_id, sec in section_breakdown.items():
            name = sec.get('name', sec_id.replace('_', ' ').title())
            pts_possible = sec.get('points_possible') or sec.get('points', 0)
            pts_earned = sec.get('points_earned') or sec.get('score', 0)
            status = sec.get('status', '')
            missing = sec.get('missing_items', [])

            earned_numeric.append((pts_possible, pts_earned))

            # Build notes with specifics
            if pts_earned >= pts_possible and not missing:
                notes = "All tasks completed"
            elif status == 'partial' or (missing and pts_earned > 0):
                missing_short = [m.replace('Variable: ', '').replace('Function: ', '')
                                 for m in missing[:3]]
                notes = f"Missing: {', '.join(missing_short)}"
                if len(missing) > 3:
                    notes += f" (+{len(missing)-3} more)"
            elif status == 'incomplete' or pts_earned == 0:
                notes = "Section not attempted or mostly incomplete"
            else:
                notes = "All tasks completed"

            display_name = name if len(name) <= 45 else name[:42] + "..."

            table_data.append([
                Paragraph(self._xml_escape(display_name), self.styles['TableCell']),
                f"{pts_possible:.0f}",
                Paragraph(f"<b>{pts_earned:.1f}</b>", self.styles['TableCell']),
                Paragraph(self._xml_escape(notes), self.styles['TableCell'])
            ])

        # Total row
        table_data.append([
            Paragraph("<b>TOTAL</b>", self.styles['TableCell']),
            Paragraph(f"<b>{max_score:.0f}</b>", self.styles['TableCell']),
            Paragraph(f"<b>{total_score:.1f}</b>", self.styles['TableCell']),
            Paragraph(f"<b>{pct:.0f}%</b>", self.styles['TableCell'])
        ])

        col_widths = [2.8*inch, 0.7*inch, 0.7*inch, 2.3*inch]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)

        style_cmds = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            # Body
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]

        # Alternate row shading
        for i in range(1, len(table_data) - 1):
            if i % 2 == 0:
                style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc')))

        # Color-code earned column using tracked numeric values
        for i, (pts, earned) in enumerate(earned_numeric):
            row_idx = i + 1  # offset for header
            if pts > 0:
                ratio = earned / pts
                if ratio >= 0.9:
                    style_cmds.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), colors.HexColor('#276749')))
                elif ratio >= 0.7:
                    style_cmds.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), colors.HexColor('#975a16')))
                else:
                    style_cmds.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), colors.HexColor('#9b2c2c')))

        t.setStyle(TableStyle(style_cmds))
        story.append(t)
        story.append(Spacer(1, 16))

    # ── Detailed Feedback ─────────────────────────────────────────────

    def _add_detailed_feedback(self, story, comp_feedback, tech_analysis, section_breakdown):
        """Add Detailed Feedback section matching sample report format"""

        story.append(Paragraph("Detailed Feedback", self.styles['SectionHeading']))

        # ── What You Did Well (bullet points) ──
        # Patterns to filter out from strengths (AI artifacts, not real observations)
        _skip_patterns = [
            'only the template code', 'no student work', 'template with no',
            'completed part ', 'completed section ',
        ]

        def _is_valid_strength(text: str) -> bool:
            lower = text.lower()
            return not any(p in lower for p in _skip_patterns)

        strengths_raw = []
        if isinstance(tech_analysis, dict):
            for s in tech_analysis.get('code_strengths', []):
                if isinstance(s, str) and len(s) > 10:
                    clean = self._clean(s)
                    if _is_valid_strength(clean):
                        strengths_raw.append(clean)

        detailed = {}
        if isinstance(comp_feedback, dict):
            detailed = comp_feedback.get('detailed_feedback', {})

        for s in detailed.get('analytical_strengths', []):
            if isinstance(s, str) and len(s) > 15:
                clean = self._clean(s)
                if _is_valid_strength(clean):
                    strengths_raw.append(clean)

        # Deduplicate: skip items that are substrings of another, or near-duplicates
        strengths = []
        seen_prefixes = set()
        for s in strengths_raw:
            # Normalize for comparison: first 40 chars lowercase
            prefix = s[:40].lower().strip()
            if prefix in seen_prefixes:
                continue
            # Also skip if this item is a substring of one already added
            is_dup = False
            for existing in strengths:
                if s in existing or existing in s:
                    is_dup = True
                    break
            if not is_dup:
                strengths.append(s)
                seen_prefixes.add(prefix)

        if strengths:
            story.append(Paragraph("What You Did Well", self.styles['SubHeading']))
            for s in strengths[:6]:
                escaped = self._xml_escape(s)
                story.append(Paragraph(
                    f"- {escaped}",
                    self.styles['BulletItem']
                ))
            story.append(Spacer(1, 8))

        # ── What to Fix (numbered items with context) ──
        issues = []
        if isinstance(tech_analysis, dict):
            for item in tech_analysis.get('code_suggestions', []):
                if isinstance(item, str) and len(item) > 15:
                    issues.append(self._clean(item))

        for item in detailed.get('areas_for_development', []):
            if isinstance(item, str) and len(item) > 15:
                clean = self._clean(item)
                if clean not in issues:
                    issues.append(clean)

        if issues:
            story.append(Paragraph("What to Fix", self.styles['SubHeading']))
            for idx, issue in enumerate(issues[:8], 1):
                escaped = self._xml_escape(issue)
                # Try to extract a short title from the first sentence
                title, body = self._split_issue_title(escaped)
                if title and body:
                    story.append(Paragraph(
                        f"<b>{idx}. {title}:</b> {body}",
                        self.styles['NumberedItem']
                    ))
                else:
                    story.append(Paragraph(
                        f"<b>{idx}.</b> {escaped}",
                        self.styles['NumberedItem']
                    ))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 8))

        # ── Reflection & Critical Thinking ──
        reflections = detailed.get('reflection_assessment', [])
        if reflections:
            clean_items = [self._clean(r) for r in reflections
                           if isinstance(r, str) and len(r) > 20]
            if clean_items:
                story.append(Paragraph("Reflection & Critical Thinking",
                                       self.styles['SubHeading']))
                for r in clean_items:
                    escaped = self._xml_escape(r)
                    story.append(Paragraph(escaped, self.styles['BodyText']))
                story.append(Spacer(1, 8))

        # ── Instructor Assessment ──
        instructor_comments = ""
        if isinstance(comp_feedback, dict):
            instructor_comments = comp_feedback.get('instructor_comments', '')
        elif isinstance(comp_feedback, str):
            instructor_comments = comp_feedback

        if instructor_comments:
            clean_comments = self._clean_instructor_text(instructor_comments)
            if clean_comments and len(clean_comments) > 30:
                story.append(Paragraph("Instructor Assessment", self.styles['SubHeading']))
                escaped = self._xml_escape(clean_comments)
                story.append(Paragraph(escaped, self.styles['BodyText']))
                story.append(Spacer(1, 8))

        # ── Key Takeaway (from recommendations) ──
        recs = detailed.get('recommendations', [])
        if recs:
            clean_items = [self._clean(r) for r in recs
                           if isinstance(r, str) and len(r) > 15]
            if clean_items:
                story.append(Paragraph("Key Takeaway", self.styles['SubHeading']))
                for r in clean_items:
                    escaped = self._xml_escape(r)
                    story.append(Paragraph(escaped, self.styles['BodyText']))
                story.append(Spacer(1, 8))

    def _split_issue_title(self, text: str) -> tuple:
        """Try to extract a task/topic title from the start of an issue.

        Patterns matched:
        - 'Part 2: Data Cleaning - Task 2.1: ...' -> title = 'Task 2.1', body = rest
        - 'Task X.Y: Description - Your code ...' -> title = 'Task X.Y: Description', body = rest
        - 'To strengthen your ...' -> no title, return ('', text)
        """
        # Pattern: "Part N: ... - Task N.N: Description - rest"
        m = re.match(r'^(.*?Task\s+\d+\.\d+[^-]*)\s*-\s*(.+)$', text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), m.group(2).strip()

        # Pattern: first sentence is short enough to be a title (< 80 chars) followed by " - "
        m = re.match(r'^([^-]{10,80})\s*-\s*(.+)$', text)
        if m and len(m.group(2)) > 30:
            return m.group(1).strip(), m.group(2).strip()

        return '', text

    # ── Technical Stats (compact, validator-only) ─────────────────────

    def _add_technical_stats(self, story, validation, section_breakdown):
        """Add compact technical stats from the validator (no AI-generated counts)"""
        sys_results = validation.get('systematic_results', {})
        output_results = validation.get('output_results', {})

        stats = []

        # Section completion from validator
        sections_complete = sys_results.get('sections_complete', 0)
        sections_total = sys_results.get('sections_total', 0)
        if sections_total > 0:
            stats.append(f"Sections completed: {sections_complete}/{sections_total}")

        # Variables found
        vars_found = sys_results.get('variables_found', 0)
        vars_total = sys_results.get('variables_total', 0)
        if vars_total > 0:
            stats.append(f"Variables found: {vars_found}/{vars_total}")

        # Output accuracy
        if output_results:
            match_rate = output_results.get('match_rate', 0)
            matches = output_results.get('matches', 0)
            total = output_results.get('total_comparisons', 0)
            if total > 0:
                stats.append(f"Output accuracy: {match_rate:.1f}% ({matches}/{total} checks passed)")

        if stats:
            story.append(Spacer(1, 6))
            stats_text = "  |  ".join(stats)
            story.append(Paragraph(
                self._xml_escape(stats_text),
                self.styles['SmallNote']
            ))

    # ── Text Cleaning Helpers ─────────────────────────────────────────

    def _clean_instructor_text(self, text: str) -> str:
        """Clean instructor comments of AI artifacts"""
        if not text:
            return ""
        clean = self._clean(text)
        # Remove common AI reasoning patterns
        for pattern in [
            r"We need to.*?\.", r"Let's.*?\.", r"First,.*?\.",
            r"The student provided.*?\.", r"<\|.*?\|>",
        ]:
            clean = re.sub(pattern, '', clean, flags=re.IGNORECASE | re.DOTALL)
        return ' '.join(clean.split()).strip()
