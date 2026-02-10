"""
GroundTruthService: Extract feedback from previously graded assignments
(Word docs, PDFs, CSVs) and convert to AIFeedback format for training.
"""
import os
import logging
from difflib import SequenceMatcher

from app.extensions import db

logger = logging.getLogger(__name__)

# Keyword sets for classifying extracted comments
_POSITIVE_KEYWORDS = {'good', 'excellent', 'well done', 'strong', 'great', 'correct', 'nice', 'impressive', 'solid'}
_NEGATIVE_KEYWORDS = {'missing', 'incorrect', 'wrong', 'error', 'issue', 'problem', 'needs', 'fix', 'improve', 'lack'}
_SUGGESTION_KEYWORDS = {'consider', 'try', 'suggest', 'could', 'should', 'recommend', 'alternative', 'better', 'instead'}


def _classify_comment(text: str) -> str:
    """Classify a comment into strength/suggestion/issue/observation."""
    lower = text.lower()
    pos = sum(1 for kw in _POSITIVE_KEYWORDS if kw in lower)
    neg = sum(1 for kw in _NEGATIVE_KEYWORDS if kw in lower)
    sug = sum(1 for kw in _SUGGESTION_KEYWORDS if kw in lower)

    if sug > pos and sug > neg:
        return 'suggestion'
    if pos > neg:
        return 'strength'
    if neg > pos:
        return 'issue'
    return 'observation'


def _name_similarity(a: str, b: str) -> float:
    """Fuzzy name similarity score."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


class GroundTruthService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def extract_from_docx(self, file_path: str) -> dict:
        """Extract comments and track changes from a Word document."""
        import docx
        from lxml import etree

        doc = docx.Document(file_path)
        W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

        # Extract comments from word/comments.xml
        comments = []
        for rel in doc.part.rels.values():
            if 'comments' in rel.reltype:
                try:
                    root = etree.fromstring(rel.target_part.blob)
                    for comment_el in root.findall(f'{{{W_NS}}}comment'):
                        author = comment_el.get(f'{{{W_NS}}}author', '')
                        text_parts = []
                        for t in comment_el.iter(f'{{{W_NS}}}t'):
                            if t.text:
                                text_parts.append(t.text)
                        text = ' '.join(text_parts).strip()
                        if text:
                            comments.append({'author': author, 'text': text})
                except Exception as e:
                    logger.warning(f'Failed to parse comments XML: {e}')
                break

        # Extract body text
        full_text = '\n'.join(p.text for p in doc.paragraphs if p.text)

        # Extract track changes (insertions/deletions)
        revisions = []
        body_xml = doc.element.body
        for ins in body_xml.iter(f'{{{W_NS}}}ins'):
            texts = [t.text for t in ins.iter(f'{{{W_NS}}}t') if t.text]
            if texts:
                revisions.append({'type': 'insertion', 'text': ' '.join(texts)})
        for deletion in body_xml.iter(f'{{{W_NS}}}del'):
            texts = [t.text for t in deletion.iter(f'{{{W_NS}}}delText') if t.text]
            if texts:
                revisions.append({'type': 'deletion', 'text': ' '.join(texts)})

        return {
            'comments': comments,
            'body_text': full_text,
            'revisions': revisions,
            'source_type': 'docx',
        }

    def extract_from_pdf(self, file_path: str) -> dict:
        """Extract annotations from a PDF document."""
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        annotations = []
        full_text = []

        for page_num, page in enumerate(doc):
            full_text.append(page.get_text())

            for annot in page.annots() or []:
                annot_data = {
                    'page': page_num + 1,
                    'type': annot.type[1],
                    'content': annot.info.get('content', ''),
                    'author': annot.info.get('title', ''),
                }

                # For highlights, extract underlying text
                if annot.type[0] == fitz.PDF_ANNOT_HIGHLIGHT:
                    rect = annot.rect
                    highlighted = page.get_text('text', clip=rect).strip()
                    annot_data['highlighted_text'] = highlighted

                if annot_data['content'] or annot_data.get('highlighted_text'):
                    annotations.append(annot_data)

        doc.close()

        return {
            'annotations': annotations,
            'body_text': '\n'.join(full_text),
            'source_type': 'pdf',
        }

    def extract_from_csv(self, file_path: str) -> list:
        """Parse a CSV/XLSX with student scores and feedback."""
        import pandas as pd

        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.xlsx', '.xls'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path, sep=None, engine='python')

        # Normalize column names
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # Map common column name variants
        name_variants = ['student_name', 'student', 'name', 'full_name']
        score_variants = ['score', 'grade', 'total_score', 'points', 'final_score']
        feedback_variants = ['feedback', 'feedback_text', 'comments', 'instructor_comments']
        id_variants = ['student_id', 'canvas_id', 'id', 'student_id_external']

        name_col = next((c for c in name_variants if c in df.columns), None)
        score_col = next((c for c in score_variants if c in df.columns), None)
        feedback_col = next((c for c in feedback_variants if c in df.columns), None)
        id_col = next((c for c in id_variants if c in df.columns), None)

        # Component score columns = remaining numeric columns
        known = {name_col, score_col, feedback_col, id_col} - {None}
        component_cols = [
            c for c in df.columns
            if c not in known and pd.api.types.is_numeric_dtype(df[c])
        ]

        entries = []
        for _, row in df.iterrows():
            entry = {
                'student_name': str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else None,
                'student_id_hint': str(row[id_col]).strip() if id_col and pd.notna(row[id_col]) else None,
                'score': float(row[score_col]) if score_col and pd.notna(row[score_col]) else None,
                'feedback_text': str(row[feedback_col]).strip() if feedback_col and pd.notna(row[feedback_col]) else None,
                'component_scores': {},
            }
            for cc in component_cols:
                if pd.notna(row[cc]):
                    entry['component_scores'][cc] = float(row[cc])
            entries.append(entry)

        return entries

    def match_to_students(self, items: list, assignment_id: int, org_id: int) -> list:
        """Match extracted entries to Student records using fuzzy name matching."""
        from app.models.student import Student
        from app.models.submission import Submission

        students = Student.query.filter_by(organization_id=org_id).all()

        # Build lookup structures
        by_canvas_id = {s.canvas_id: s for s in students if s.canvas_id}
        by_name = {}
        for s in students:
            for key in [
                f'{s.last_name} {s.first_name}'.lower().strip(),
                f'{s.first_name} {s.last_name}'.lower().strip(),
            ]:
                by_name[key] = s

        results = []
        for item in items:
            matched = None
            method = None

            # Try ID match first
            if item.get('student_id_hint'):
                hint = item['student_id_hint']
                matched = by_canvas_id.get(hint)
                if matched:
                    method = 'canvas_id'

            # Try exact name match
            if not matched and item.get('student_name'):
                name = item['student_name'].lower().strip()
                matched = by_name.get(name)
                if matched:
                    method = 'exact_name'

                # Try fuzzy match
                if not matched:
                    best_score, best_student = 0, None
                    for key, s in by_name.items():
                        score = _name_similarity(name, key)
                        if score > best_score and score > 0.8:
                            best_score = score
                            best_student = s
                    if best_student:
                        matched = best_student
                        method = f'fuzzy_{best_score:.0%}'

            # Check existing submission
            existing_sub = None
            if matched:
                existing_sub = Submission.query.filter_by(
                    assignment_id=assignment_id,
                    student_id=matched.id,
                ).first()

            results.append({
                **item,
                'matched_student': matched.to_dict() if matched else None,
                'match_method': method,
                'existing_submission_id': existing_sub.id if existing_sub else None,
                'has_existing_feedback': bool(
                    existing_sub and (existing_sub.edited_feedback or existing_sub.ai_feedback)
                ) if existing_sub else False,
            })

        return results

    def convert_to_ai_feedback(self, extracted: dict, max_points: float) -> dict:
        """Convert extracted feedback into the AIFeedback JSON shape."""
        feedback = {
            'final_score': extracted.get('score') or 0,
            'max_points': max_points,
            'component_scores': extracted.get('component_scores', {}),
            'component_percentages': {},
            'technical_analysis': {
                'code_strengths': [],
                'code_suggestions': [],
                'technical_observations': [],
            },
            'comprehensive_feedback': {
                'instructor_comments': '',
                'detailed_feedback': {
                    'reflection_assessment': [],
                    'analytical_strengths': [],
                    'business_application': [],
                    'areas_for_development': [],
                    'recommendations': [],
                },
            },
        }

        # Classify comments/annotations into feedback categories
        items = extracted.get('comments', []) or extracted.get('annotations', [])
        for item in items:
            text = item.get('text', '') or item.get('content', '')
            if not text:
                continue
            cat = _classify_comment(text)
            if cat == 'strength':
                feedback['comprehensive_feedback']['detailed_feedback']['analytical_strengths'].append(text)
            elif cat == 'suggestion':
                feedback['technical_analysis']['code_suggestions'].append(text)
            elif cat == 'issue':
                feedback['comprehensive_feedback']['detailed_feedback']['areas_for_development'].append(text)
            else:
                feedback['technical_analysis']['technical_observations'].append(text)

        # Track changes as observations
        for rev in extracted.get('revisions', []):
            feedback['technical_analysis']['technical_observations'].append(
                f"[{rev['type']}] {rev['text']}"
            )

        # General feedback text goes to instructor_comments
        if extracted.get('feedback_text'):
            feedback['comprehensive_feedback']['instructor_comments'] = extracted['feedback_text']

        # Calculate component percentages
        if feedback['component_scores'] and max_points > 0:
            for key, score in feedback['component_scores'].items():
                feedback['component_percentages'][key] = round(
                    float(score) / max_points * 100, 1
                )

        return feedback

    def process_upload(self, assignment_id: int, file_path: str, file_type: str, org_id: int) -> dict:
        """Main entry: extract, match, convert. Returns preview data."""
        from app.models.assignment import Assignment
        assignment = Assignment.query.get(assignment_id)
        max_points = assignment.total_points or 100

        if file_type == 'csv':
            raw_entries = self.extract_from_csv(file_path)
            for entry in raw_entries:
                entry['converted_feedback'] = self.convert_to_ai_feedback(entry, max_points)
            matched = self.match_to_students(raw_entries, assignment_id, org_id)
            return {
                'mode': 'batch',
                'total_entries': len(matched),
                'matched_count': sum(1 for m in matched if m['matched_student']),
                'entries': matched,
            }

        elif file_type == 'docx':
            extracted = self.extract_from_docx(file_path)
            converted = self.convert_to_ai_feedback(extracted, max_points)
            return {
                'mode': 'single',
                'extracted': extracted,
                'converted_feedback': converted,
            }

        elif file_type == 'pdf':
            extracted = self.extract_from_pdf(file_path)
            converted = self.convert_to_ai_feedback(extracted, max_points)
            return {
                'mode': 'single',
                'extracted': extracted,
                'converted_feedback': converted,
            }

        else:
            raise ValueError(f'Unsupported file type: {file_type}')
