"""Assignment CRUD endpoints with file uploads."""
import os
import re
import json
import tempfile

from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.assignment import Assignment
from app.models.course import Course
from app.utils.decorators import tenant_required, role_required

assignments_bp = Blueprint('assignments', __name__)

ALLOWED_NOTEBOOK_EXT = {'.ipynb'}
ALLOWED_RUBRIC_EXT = {'.json'}
ALLOWED_DOC_EXT = {'.pdf', '.docx', '.doc'}


def _slugify(text):
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    return re.sub(r'[\s_]+', '-', slug)[:100]


def _assignment_storage_path(course, assignment_slug):
    """Build absolute storage path for an assignment."""
    org_slug = course.organization.slug
    return os.path.join(
        current_app.config['STORAGE_ROOT'],
        org_slug, course.slug, 'assignments', assignment_slug
    )


def _atomic_write(dest_path, content_bytes):
    """Write bytes to a file atomically (write temp → rename)."""
    dest_dir = os.path.dirname(dest_path)
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, suffix='.tmp')
    closed = False
    try:
        os.write(fd, content_bytes)
        os.close(fd)
        closed = True
        os.replace(tmp_path, dest_path)  # atomic on POSIX
    except Exception:
        if not closed:
            os.close(fd)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _atomic_save_upload(dest_path, file_storage):
    """Save a Werkzeug FileStorage atomically."""
    dest_dir = os.path.dirname(dest_path)
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, suffix='.tmp')
    try:
        os.close(fd)
        file_storage.save(tmp_path)
        os.replace(tmp_path, dest_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _check_version(assignment, data):
    """Check optimistic lock version. Returns error response or None."""
    if 'version' in data:
        client_version = data['version']
        if client_version != assignment.version:
            return jsonify(
                error='Conflict: this assignment was modified by another user. Please refresh and try again.',
                current_version=assignment.version,
            ), 409
    return None


@assignments_bp.route('/courses/<int:course_id>/assignments', methods=['GET'])
@tenant_required
def list_assignments(course_id):
    """List assignments for a course."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    assignments = course.assignments.order_by(Assignment.created_at.desc()).all()
    return jsonify(assignments=[a.to_dict(include_stats=True) for a in assignments])


@assignments_bp.route('/courses/<int:course_id>/assignments', methods=['POST'])
@role_required('admin', 'instructor')
def create_assignment(course_id):
    """Create a new assignment (JSON metadata, files uploaded separately)."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    data = request.get_json() or {}

    if not data.get('name'):
        return jsonify(error='name is required'), 400

    slug = _slugify(data['name'])
    existing = Assignment.query.filter_by(course_id=course.id, slug=slug).first()
    if existing:
        return jsonify(error='Assignment with this name already exists in this course'), 409

    assignment = Assignment(
        course_id=course.id,
        name=data['name'],
        slug=slug,
        description=data.get('description', ''),
        assignment_type=data.get('assignment_type', 'coding'),
        total_points=float(data.get('total_points', 37.5)),
        language=data.get('language', 'R'),
        due_date=data.get('due_date'),
        grading_config=data.get('grading_config', {}),
    )
    db.session.add(assignment)
    db.session.commit()

    # Create storage directory
    storage_path = _assignment_storage_path(course, slug)
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(os.path.join(storage_path, 'data'), exist_ok=True)

    return jsonify(assignment=assignment.to_dict()), 201


@assignments_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@tenant_required
def get_assignment(assignment_id):
    """Get assignment details."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404
    return jsonify(assignment=assignment.to_dict(include_stats=True))


@assignments_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
@tenant_required
def update_assignment(assignment_id):
    """Update assignment metadata."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}

    # Optimistic locking: reject if client's version is stale
    conflict = _check_version(assignment, data)
    if conflict:
        return conflict

    for field in ['name', 'description', 'assignment_type', 'language', 'due_date',
                   'code_analysis_prompt', 'feedback_prompt']:
        if field in data:
            setattr(assignment, field, data[field])
    if 'total_points' in data:
        assignment.total_points = float(data['total_points'])
    if 'grading_config' in data:
        assignment.grading_config = data['grading_config']
    if 'is_published' in data:
        assignment.is_published = data['is_published']

    db.session.commit()
    return jsonify(assignment=assignment.to_dict())


@assignments_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@role_required('admin', 'instructor')
def delete_assignment(assignment_id):
    """Delete an assignment and its submissions."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    db.session.delete(assignment)
    db.session.commit()
    return jsonify(message='Assignment deleted')


@assignments_bp.route('/assignments/<int:assignment_id>/rubric', methods=['POST'])
@tenant_required
def upload_rubric(assignment_id):
    """Upload or replace rubric JSON."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if 'file' not in request.files:
        return jsonify(error='No file provided'), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_RUBRIC_EXT:
        return jsonify(error='Only .json files allowed for rubrics'), 400

    # Validate JSON
    try:
        content = file.read()
        json.loads(content)
        file.seek(0)
    except json.JSONDecodeError:
        return jsonify(error='Invalid JSON file'), 400

    storage_path = _assignment_storage_path(assignment.course, assignment.slug)
    os.makedirs(storage_path, exist_ok=True)
    dest = os.path.join(storage_path, 'rubric.json')
    _atomic_save_upload(dest, file)

    assignment.rubric_path = 'rubric.json'
    db.session.commit()

    return jsonify(message='Rubric uploaded', path=assignment.rubric_path)


@assignments_bp.route('/assignments/<int:assignment_id>/solution', methods=['POST'])
@tenant_required
def upload_solution(assignment_id):
    """Upload or replace solution notebook."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if 'file' not in request.files:
        return jsonify(error='No file provided'), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_NOTEBOOK_EXT:
        return jsonify(error='Only .ipynb files allowed for solutions'), 400

    storage_path = _assignment_storage_path(assignment.course, assignment.slug)
    os.makedirs(storage_path, exist_ok=True)
    dest = os.path.join(storage_path, 'solution.ipynb')
    _atomic_save_upload(dest, file)

    assignment.solution_path = 'solution.ipynb'
    db.session.commit()

    return jsonify(message='Solution uploaded', path=assignment.solution_path)


@assignments_bp.route('/assignments/<int:assignment_id>/template', methods=['POST'])
@tenant_required
def upload_template(assignment_id):
    """Upload or replace template notebook."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if 'file' not in request.files:
        return jsonify(error='No file provided'), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_NOTEBOOK_EXT:
        return jsonify(error='Only .ipynb files allowed for templates'), 400

    storage_path = _assignment_storage_path(assignment.course, assignment.slug)
    os.makedirs(storage_path, exist_ok=True)
    dest = os.path.join(storage_path, 'template.ipynb')
    _atomic_save_upload(dest, file)

    assignment.template_path = 'template.ipynb'
    db.session.commit()

    return jsonify(message='Template uploaded', path=assignment.template_path)


# --------------- Rubric Builder Endpoints ---------------

def _slugify_key(text):
    """Convert category name to a dict key, e.g. 'Technical Execution' → 'technical_execution'."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s]', '', s)
    return re.sub(r'\s+', '_', s)[:60]


@assignments_bp.route('/assignments/<int:assignment_id>/rubric/data', methods=['GET'])
@tenant_required
def get_rubric_data(assignment_id):
    """Load rubric JSON for the builder. Returns starter template if none exists."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    # Try to load existing rubric from disk
    if assignment.rubric_path:
        storage_path = _assignment_storage_path(assignment.course, assignment.slug)
        rubric_file = os.path.join(storage_path, assignment.rubric_path)
        if os.path.exists(rubric_file):
            with open(rubric_file, 'r', encoding='utf-8') as f:
                raw = json.load(f)

            # Normalize to builder format: extract categories list from various formats
            categories = []
            elements = raw.get('rubric_elements') or raw.get('components') or {}
            for key, elem in elements.items():
                cat = {
                    'key': key,
                    'name': key.replace('_', ' ').title(),
                    'max_points': elem.get('max_points', 0),
                    'description': elem.get('description', ''),
                    'criteria': {
                        'excellent': '', 'good': '',
                        'satisfactory': '', 'needs_improvement': '',
                    },
                }
                # Extract criteria descriptions from various formats
                crit = elem.get('criteria', {})
                if isinstance(crit, dict):
                    for level in ['excellent', 'good', 'satisfactory', 'needs_improvement']:
                        val = crit.get(level, '')
                        if isinstance(val, dict):
                            cat['criteria'][level] = val.get('description', '')
                        elif isinstance(val, str):
                            cat['criteria'][level] = val
                elif isinstance(crit, list):
                    cat['criteria']['excellent'] = '; '.join(crit)

                # Also check scoring_guide as fallback
                guide = elem.get('scoring_guide', {})
                if isinstance(guide, dict):
                    for level in ['excellent', 'good', 'satisfactory', 'needs_improvement']:
                        alt = 'poor' if level == 'needs_improvement' else level
                        if not cat['criteria'][level] and guide.get(alt):
                            cat['criteria'][level] = guide[alt]
                        if not cat['criteria'][level] and guide.get(level):
                            cat['criteria'][level] = guide[level]

                categories.append(cat)

            info = raw.get('assignment_info', {})
            return jsonify(rubric={
                'assignment_info': {
                    'name': info.get('name', assignment.slug),
                    'title': info.get('title', assignment.name),
                    'total_points': info.get('total_points', assignment.total_points),
                },
                'categories': categories,
            })

    # No rubric yet — return starter template
    return jsonify(rubric={
        'assignment_info': {
            'name': assignment.slug,
            'title': assignment.name,
            'total_points': assignment.total_points,
        },
        'categories': [],
    })


@assignments_bp.route('/assignments/<int:assignment_id>/rubric/data', methods=['PUT'])
@tenant_required
def save_rubric_data(assignment_id):
    """Save rubric from builder. Validates and writes rubric.json."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}

    # Optimistic locking
    conflict = _check_version(assignment, data)
    if conflict:
        return conflict

    categories = data.get('categories', [])

    if not categories:
        return jsonify(error='At least one rubric category is required'), 400

    # Validate each category
    errors = []
    total_points = 0
    for i, cat in enumerate(categories):
        if not cat.get('name', '').strip():
            errors.append(f'Category {i+1}: name is required')
        if not isinstance(cat.get('max_points'), (int, float)) or cat['max_points'] <= 0:
            errors.append(f'Category {i+1}: max_points must be positive')
        else:
            total_points += cat['max_points']
        if not cat.get('description', '').strip():
            errors.append(f'Category {i+1}: description is required')

    if errors:
        return jsonify(error='Validation failed', details=errors), 400

    points_match = abs(total_points - assignment.total_points) < 0.1

    # Build engine-compatible rubric JSON
    rubric_elements = {}
    for cat in categories:
        key = cat.get('key') or _slugify_key(cat['name'])
        weight = round(cat['max_points'] / assignment.total_points, 4) if assignment.total_points else 0
        crit = cat.get('criteria', {})
        rubric_elements[key] = {
            'weight': weight,
            'max_points': cat['max_points'],
            'description': cat['description'],
            'criteria': {
                'excellent': {'range': '90-100%', 'description': crit.get('excellent', '')},
                'good': {'range': '75-89%', 'description': crit.get('good', '')},
                'satisfactory': {'range': '60-74%', 'description': crit.get('satisfactory', '')},
                'needs_improvement': {'range': '0-59%', 'description': crit.get('needs_improvement', '')},
            },
        }

    rubric_json = {
        'assignment_info': {
            'name': assignment.slug,
            'title': assignment.name,
            'total_points': assignment.total_points,
        },
        'rubric_elements': rubric_elements,
    }

    # Write to disk atomically
    storage_path = _assignment_storage_path(assignment.course, assignment.slug)
    os.makedirs(storage_path, exist_ok=True)
    dest = os.path.join(storage_path, 'rubric.json')
    _atomic_write(dest, json.dumps(rubric_json, indent=2).encode('utf-8'))

    assignment.rubric_path = 'rubric.json'
    db.session.commit()

    return jsonify(
        message='Rubric saved',
        points_match=points_match,
        rubric={
            'assignment_info': rubric_json['assignment_info'],
            'categories': categories,
        },
    )


@assignments_bp.route('/assignments/<int:assignment_id>/generate-prompts', methods=['POST'])
@tenant_required
def generate_prompts(assignment_id):
    """Generate analysis + feedback prompts from rubric criteria."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if not assignment.rubric_path:
        return jsonify(error='No rubric uploaded. Build or upload a rubric first.'), 400

    storage_path = _assignment_storage_path(assignment.course, assignment.slug)
    rubric_file = os.path.join(storage_path, assignment.rubric_path)
    if not os.path.exists(rubric_file):
        return jsonify(error='Rubric file not found on disk'), 404

    with open(rubric_file, 'r', encoding='utf-8') as f:
        rubric = json.load(f)

    elements = rubric.get('rubric_elements') or rubric.get('components') or {}
    info = rubric.get('assignment_info', {})
    title = info.get('title', assignment.name)
    total = info.get('total_points', assignment.total_points)
    is_coding = assignment.assignment_type == 'coding'

    # Build criteria block
    criteria_lines = []
    for i, (key, elem) in enumerate(elements.items(), 1):
        name = key.replace('_', ' ').title()
        pts = elem.get('max_points', 0)
        weight = elem.get('weight', 0)
        desc = elem.get('description', '')
        criteria_lines.append(f'{i}. {name} ({weight*100:.0f}%, {pts} pts): {desc}')

        crit = elem.get('criteria', {})
        for level in ['excellent', 'good', 'satisfactory', 'needs_improvement']:
            label = level.replace('_', ' ').title()
            val = crit.get(level, '')
            if isinstance(val, dict):
                val = val.get('description', '')
            if val:
                criteria_lines.append(f'   - {label}: {val}')

    criteria_block = '\n'.join(criteria_lines)
    category_names = ', '.join(k.replace('_', ' ').title() for k in elements.keys())

    # Generate analysis prompt
    if is_coding:
        lang = assignment.language or 'R'
        analysis_prompt = (
            f'You are grading a {lang} coding assignment: "{title}" (total: {total} points).\n\n'
            f'Evaluate the student submission against these rubric criteria:\n\n'
            f'{criteria_block}\n\n'
            f'For each criterion:\n'
            f'1. Identify specific evidence from the student\'s code and outputs\n'
            f'2. Assign a score (0 to max_points for that criterion)\n'
            f'3. Note any issues, errors, or missing elements\n\n'
            f'Return valid JSON with this structure:\n'
            f'{{"component_scores": {{"category_name": {{"score": N, "max": N, "evidence": "..."}}}}, '
            f'"total_score": N, "max_score": {total}, '
            f'"strengths": ["..."], "weaknesses": ["..."], "specific_issues": ["..."]}}'
        )
    else:
        analysis_prompt = (
            f'You are grading a written assignment: "{title}" (total: {total} points).\n\n'
            f'Evaluate the student\'s written response against these rubric criteria:\n\n'
            f'{criteria_block}\n\n'
            f'For each criterion:\n'
            f'1. Assess the quality of the response (argument depth, evidence, accuracy, completeness)\n'
            f'2. Assign a score (0 to max_points for that criterion)\n'
            f'3. Provide specific quotes or references from the submission as evidence\n\n'
            f'Return valid JSON with this structure:\n'
            f'{{"component_scores": {{"category_name": {{"score": N, "max": N, "evidence": "..."}}}}, '
            f'"total_score": N, "max_score": {total}, '
            f'"strengths": ["..."], "areas_for_improvement": ["..."]}}'
        )

    # Generate feedback prompt
    feedback_prompt = (
        f'You are providing feedback on a student\'s submission for "{title}".\n\n'
        f'Based on the analysis results, write constructive, encouraging feedback that:\n'
        f'1. Acknowledges what the student did well (be specific)\n'
        f'2. Identifies areas for improvement with actionable suggestions\n'
        f'3. References the rubric criteria: {category_names}\n'
        f'4. Maintains an encouraging, educational tone\n\n'
        f'The feedback should be 3-5 paragraphs, suitable for a student report.'
    )

    assignment.code_analysis_prompt = analysis_prompt
    assignment.feedback_prompt = feedback_prompt
    db.session.commit()

    return jsonify(
        code_analysis_prompt=analysis_prompt,
        feedback_prompt=feedback_prompt,
    )
