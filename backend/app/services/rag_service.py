"""
RAGService: FAISS-based retrieval-augmented generation for grading context.

Each assignment gets its own FAISS index stored at:
  storage/{org}/{course}/rag/{assignment_slug}/

Indexes rubric text, solution code, and past reviewed submissions with
edited_feedback to give the grading models richer context.
"""
import os
import json
import logging
import hashlib
import pickle
from typing import List, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded globals to avoid import cost on every request
_model = None
_faiss = None


def _get_embedding_model():
    """Lazy-load sentence-transformers model (80MB, cached after first load)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def _get_faiss():
    """Lazy-load faiss module."""
    global _faiss
    if _faiss is None:
        import faiss as _f
        _faiss = _f
    return _faiss


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """Split text into overlapping chunks by words."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


class RAGService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def _index_dir(self, assignment) -> str:
        """Get the FAISS index directory for an assignment."""
        course = assignment.course
        org_slug = course.organization.slug
        return os.path.join(
            self.storage_root, org_slug, course.slug,
            'rag', assignment.slug,
        )

    def _load_index(self, assignment):
        """Load existing FAISS index and metadata, or return None."""
        faiss = _get_faiss()
        idx_dir = self._index_dir(assignment)
        index_path = os.path.join(idx_dir, 'index.faiss')
        meta_path = os.path.join(idx_dir, 'metadata.pkl')

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            return None, None

        index = faiss.read_index(index_path)
        with open(meta_path, 'rb') as f:
            metadata = pickle.load(f)
        return index, metadata

    def _save_index(self, assignment, index, metadata):
        """Persist FAISS index and metadata to disk."""
        faiss = _get_faiss()
        idx_dir = self._index_dir(assignment)
        os.makedirs(idx_dir, exist_ok=True)
        faiss.write_index(index, os.path.join(idx_dir, 'index.faiss'))
        with open(os.path.join(idx_dir, 'metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)

    def index_assignment_materials(self, assignment) -> Dict:
        """Index rubric, solution, and any uploaded context docs.

        Returns:
            dict with num_chunks, documents_indexed
        """
        faiss = _get_faiss()
        model = _get_embedding_model()

        course = assignment.course
        org_slug = course.organization.slug
        base = os.path.join(
            self.storage_root, org_slug, course.slug,
            'assignments', assignment.slug,
        )

        documents = []

        # Index rubric
        if assignment.rubric_path:
            rubric_abs = os.path.join(base, assignment.rubric_path)
            if os.path.exists(rubric_abs):
                try:
                    with open(rubric_abs) as f:
                        rubric_data = json.load(f)
                    rubric_text = self._rubric_to_text(rubric_data)
                    for chunk in _chunk_text(rubric_text):
                        documents.append({'text': chunk, 'source': 'rubric', 'file': assignment.rubric_path})
                except Exception as e:
                    logger.warning(f"Failed to index rubric: {e}")

        # Index solution
        if assignment.solution_path:
            sol_abs = os.path.join(base, assignment.solution_path)
            if os.path.exists(sol_abs):
                try:
                    sol_text = self._extract_notebook_text(sol_abs)
                    for chunk in _chunk_text(sol_text):
                        documents.append({'text': chunk, 'source': 'solution', 'file': assignment.solution_path})
                except Exception as e:
                    logger.warning(f"Failed to index solution: {e}")

        # Index additional context docs uploaded to rag/ directory
        idx_dir = self._index_dir(assignment)
        docs_dir = os.path.join(idx_dir, 'documents')
        if os.path.exists(docs_dir):
            for fname in os.listdir(docs_dir):
                fpath = os.path.join(docs_dir, fname)
                try:
                    with open(fpath) as f:
                        text = f.read()
                    for chunk in _chunk_text(text):
                        documents.append({'text': chunk, 'source': 'document', 'file': fname})
                except Exception as e:
                    logger.warning(f"Failed to index document {fname}: {e}")

        if not documents:
            return {'num_chunks': 0, 'documents_indexed': 0}

        # Build FAISS index
        texts = [d['text'] for d in documents]
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype='float32')

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product on normalized vectors = cosine similarity
        index.add(embeddings)

        # Store metadata alongside each vector
        metadata = {
            'documents': documents,
            'source_files': list({d['file'] for d in documents}),
            'num_chunks': len(documents),
            'dimension': dim,
        }
        self._save_index(assignment, index, metadata)

        return {
            'num_chunks': len(documents),
            'documents_indexed': len(metadata['source_files']),
        }

    def index_reviewed_submissions(self, assignment) -> Dict:
        """Add reviewed submissions with edited_feedback to the index.

        Appends to the existing index (doesn't replace rubric/solution chunks).
        """
        from app.models.submission import Submission

        faiss = _get_faiss()
        model = _get_embedding_model()

        # Load existing index
        index, metadata = self._load_index(assignment)
        if index is None:
            # Build base index first
            self.index_assignment_materials(assignment)
            index, metadata = self._load_index(assignment)
            if index is None:
                return {'num_chunks_added': 0}

        # Find reviewed submissions with edited feedback
        submissions = Submission.query.filter(
            Submission.assignment_id == assignment.id,
            Submission.status == 'reviewed',
            Submission.edited_feedback.isnot(None),
        ).all()

        if not submissions:
            return {'num_chunks_added': 0}

        # Build training-like examples from corrections
        new_docs = []
        existing_hashes = set()
        for doc in metadata.get('documents', []):
            if doc['source'] == 'reviewed_submission':
                existing_hashes.add(doc.get('hash'))

        for sub in submissions:
            feedback = sub.edited_feedback or {}
            student = sub.student
            name = f"{student.first_name} {student.last_name}" if student else "Unknown"

            # Create a text representation of the correction
            text_parts = [f"Student: {name}", f"Score: {sub.final_score}/{sub.max_score}"]

            ta = feedback.get('technical_analysis', {})
            cf = feedback.get('comprehensive_feedback', {})
            df = cf.get('detailed_feedback', {})

            for label, items in [
                ('Code Strengths', ta.get('code_strengths', [])),
                ('Code Suggestions', ta.get('code_suggestions', [])),
                ('Areas for Development', df.get('areas_for_development', [])),
                ('Recommendations', df.get('recommendations', [])),
            ]:
                if items:
                    text_parts.append(f"{label}: " + '; '.join(items))

            if cf.get('instructor_comments'):
                text_parts.append(f"Instructor Comments: {cf['instructor_comments']}")

            text = '\n'.join(text_parts)
            doc_hash = hashlib.md5(text.encode()).hexdigest()

            if doc_hash in existing_hashes:
                continue

            for chunk in _chunk_text(text):
                new_docs.append({
                    'text': chunk,
                    'source': 'reviewed_submission',
                    'file': f'submission_{sub.id}',
                    'hash': doc_hash,
                })

        if not new_docs:
            return {'num_chunks_added': 0}

        texts = [d['text'] for d in new_docs]
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype='float32')

        index.add(embeddings)
        metadata['documents'].extend(new_docs)
        metadata['num_chunks'] = len(metadata['documents'])

        self._save_index(assignment, index, metadata)

        return {'num_chunks_added': len(new_docs)}

    def retrieve_context(self, assignment, query_text: str, top_k: int = 5) -> List[Dict]:
        """Retrieve the most relevant chunks for a query.

        Returns:
            List of {text, source, score} dicts
        """
        model = _get_embedding_model()
        index, metadata = self._load_index(assignment)

        if index is None or index.ntotal == 0:
            return []

        query_vec = model.encode([query_text], normalize_embeddings=True)
        query_vec = np.array(query_vec, dtype='float32')

        k = min(top_k, index.ntotal)
        scores, indices = index.search(query_vec, k)

        results = []
        documents = metadata.get('documents', [])
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(documents):
                continue
            doc = documents[idx]
            results.append({
                'text': doc['text'],
                'source': doc['source'],
                'score': float(score),
            })

        return results

    def build_rag_prompt_section(self, assignment, student_code: str) -> str:
        """Build a prompt section with retrieved context for the grading models.

        Args:
            assignment: Assignment ORM object
            student_code: The student's code to use as query

        Returns:
            String to inject into the grading prompt, or empty string
        """
        config = assignment.grading_config or {}
        if not config.get('rag_enabled'):
            return ''

        # Use student code as the query
        results = self.retrieve_context(assignment, student_code, top_k=5)

        if not results:
            return ''

        sections = []
        sections.append("RETRIEVED CONTEXT (from assignment materials and past reviewed submissions):")
        sections.append("Use these examples to calibrate your scoring and feedback style.\n")

        for i, r in enumerate(results, 1):
            source_label = {
                'rubric': 'Rubric',
                'solution': 'Solution',
                'document': 'Reference Document',
                'reviewed_submission': 'Past Reviewed Submission',
            }.get(r['source'], r['source'])
            sections.append(f"--- Context {i} [{source_label}] (relevance: {r['score']:.2f}) ---")
            sections.append(r['text'])
            sections.append("")

        return '\n'.join(sections)

    def get_index_status(self, assignment) -> Dict:
        """Get status information about the RAG index for an assignment."""
        idx_dir = self._index_dir(assignment)
        index_path = os.path.join(idx_dir, 'index.faiss')

        if not os.path.exists(index_path):
            return {
                'indexed': False,
                'num_chunks': 0,
                'source_files': [],
                'rag_enabled': (assignment.grading_config or {}).get('rag_enabled', False),
            }

        _, metadata = self._load_index(assignment)
        if metadata is None:
            return {
                'indexed': False,
                'num_chunks': 0,
                'source_files': [],
                'rag_enabled': (assignment.grading_config or {}).get('rag_enabled', False),
            }

        # Count by source type
        docs = metadata.get('documents', [])
        source_counts = {}
        for d in docs:
            src = d['source']
            source_counts[src] = source_counts.get(src, 0) + 1

        return {
            'indexed': True,
            'num_chunks': metadata.get('num_chunks', 0),
            'source_files': metadata.get('source_files', []),
            'source_counts': source_counts,
            'rag_enabled': (assignment.grading_config or {}).get('rag_enabled', False),
        }

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _rubric_to_text(rubric_data: dict) -> str:
        """Convert rubric JSON to searchable text."""
        parts = []
        info = rubric_data.get('assignment_info', {})
        if info.get('title'):
            parts.append(f"Assignment: {info['title']}")
        if info.get('description'):
            parts.append(f"Description: {info['description']}")

        for section in rubric_data.get('sections', []):
            parts.append(f"\nSection: {section.get('name', '')}")
            if section.get('description'):
                parts.append(section['description'])
            for criterion in section.get('criteria', []):
                parts.append(f"  Criterion: {criterion.get('name', '')} ({criterion.get('points', 0)} pts)")
                if criterion.get('description'):
                    parts.append(f"    {criterion['description']}")
                for level in criterion.get('levels', []):
                    parts.append(f"    {level.get('label', '')}: {level.get('description', '')}")

        return '\n'.join(parts)

    @staticmethod
    def _extract_notebook_text(path: str) -> str:
        """Extract all text (code + markdown) from a Jupyter notebook."""
        try:
            import nbformat
            with open(path) as f:
                nb = nbformat.read(f, as_version=4)
            cells = [cell.source for cell in nb.cells]
            return '\n\n'.join(cells)
        except Exception:
            with open(path) as f:
                return f.read()
