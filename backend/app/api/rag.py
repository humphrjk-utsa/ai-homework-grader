"""RAG (Retrieval-Augmented Generation) API endpoints."""
import os
from flask import Blueprint, jsonify, request, g, current_app
from werkzeug.utils import secure_filename

from app.utils.decorators import tenant_required
from app.models.assignment import Assignment
from app.extensions import db

rag_bp = Blueprint('rag', __name__)


def _get_rag_service():
    from app.services.rag_service import RAGService
    return RAGService(current_app.config['STORAGE_ROOT'])


@rag_bp.route('/assignments/<int:assignment_id>/index', methods=['POST'])
@tenant_required
def index_assignment(assignment_id):
    """Trigger indexing of assignment materials (rubric, solution, context docs)."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    svc = _get_rag_service()

    # Index base materials
    result = svc.index_assignment_materials(assignment)

    # Also index reviewed submissions if any exist
    sub_result = svc.index_reviewed_submissions(assignment)
    result['reviewed_chunks_added'] = sub_result.get('num_chunks_added', 0)

    return jsonify(result=result)


@rag_bp.route('/assignments/<int:assignment_id>/status', methods=['GET'])
@tenant_required
def index_status(assignment_id):
    """Get RAG index status for an assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    svc = _get_rag_service()
    status = svc.get_index_status(assignment)
    return jsonify(status=status)


@rag_bp.route('/assignments/<int:assignment_id>/upload', methods=['POST'])
@tenant_required
def upload_context_doc(assignment_id):
    """Upload additional context documents for RAG indexing."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if 'file' not in request.files:
        return jsonify(error='No file provided'), 400

    file = request.files['file']
    if not file.filename:
        return jsonify(error='No filename'), 400

    # Only allow text-based files
    allowed_ext = {'.txt', '.md', '.csv', '.json', '.py', '.r', '.rmd', '.ipynb'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_ext:
        return jsonify(error=f'File type not supported. Allowed: {", ".join(allowed_ext)}'), 400

    svc = _get_rag_service()
    idx_dir = svc._index_dir(assignment)
    docs_dir = os.path.join(idx_dir, 'documents')
    os.makedirs(docs_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    file.save(os.path.join(docs_dir, filename))

    return jsonify(message=f'Document "{filename}" uploaded. Re-index to include it in searches.')


@rag_bp.route('/assignments/<int:assignment_id>/toggle', methods=['PUT'])
@tenant_required
def toggle_rag(assignment_id):
    """Enable or disable RAG for an assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}
    enabled = bool(data.get('enabled', False))

    config = assignment.grading_config or {}
    config['rag_enabled'] = enabled
    assignment.grading_config = config
    # Flag the column as modified so SQLAlchemy detects the JSON mutation
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(assignment, 'grading_config')
    db.session.commit()

    return jsonify(rag_enabled=enabled, grading_config=assignment.grading_config)
