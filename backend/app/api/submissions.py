"""Submission upload endpoints (single and batch)."""
import os
import re

from flask import Blueprint, request, jsonify, g, current_app, send_file

from app.extensions import db
from app.models.assignment import Assignment
from app.models.student import Student
from app.models.submission import Submission
from app.utils.decorators import tenant_required

submissions_bp = Blueprint('submissions', __name__)

ALLOWED_EXTENSIONS = {'.ipynb', '.pdf', '.docx', '.doc'}


def _parse_canvas_filename(filename):
    """Extract student name and canvas ID from Canvas-format filename.

    Canvas format: lastname_firstname_canvasid_assignmentinfo.ipynb
    """
    base = os.path.splitext(filename)[0]
    # Try Canvas format: name_canvasid_...
    match = re.match(r'^(.+?)_(\d{4,})_', base)
    if match:
        name_part = match.group(1).replace('_', ' ').strip()
        canvas_id = match.group(2)
        return name_part, canvas_id
    return base, None


@submissions_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@tenant_required
def list_submissions(assignment_id):
    """List submissions for an assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    submissions = assignment.submissions.order_by(Submission.submitted_at.desc()).all()
    result = []
    for s in submissions:
        d = s.to_dict()
        d['student'] = s.student.to_dict() if s.student else None
        result.append(d)
    return jsonify(submissions=result)


@submissions_bp.route('/assignments/<int:assignment_id>/submissions', methods=['POST'])
@tenant_required
def upload_submission(assignment_id):
    """Upload a single submission file."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if 'file' not in request.files:
        return jsonify(error='No file provided'), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(error=f'Unsupported file type: {ext}'), 400

    student_id = request.form.get('student_id')
    student = None

    if student_id:
        student = Student.query.filter_by(
            id=int(student_id), organization_id=g.organization_id
        ).first()

    # Try to identify student from filename
    if student is None:
        name, canvas_id = _parse_canvas_filename(file.filename)
        if canvas_id:
            student = Student.query.filter_by(
                organization_id=g.organization_id, canvas_id=canvas_id
            ).first()

    if student is None:
        return jsonify(error='Could not identify student. Provide student_id or use Canvas-format filename.'), 400

    # Build storage path
    org_slug = assignment.course.organization.slug
    storage_base = os.path.join(
        current_app.config['STORAGE_ROOT'],
        org_slug, assignment.course.slug,
        'submissions', assignment.slug, str(student.id)
    )
    os.makedirs(storage_base, exist_ok=True)

    dest_filename = f'submission{ext}'
    dest_path = os.path.join(storage_base, dest_filename)
    file.save(dest_path)

    # Relative path for DB
    relative_path = os.path.join(str(student.id), dest_filename)

    # Create or update submission
    submission = Submission.query.filter_by(
        assignment_id=assignment.id, student_id=student.id
    ).first()

    if submission:
        submission.file_path = relative_path
        submission.file_type = ext.lstrip('.')
        submission.original_filename = file.filename
        submission.status = 'uploaded'
        submission.ai_score = None
        submission.ai_feedback = None
        submission.final_score = None
        submission.error_message = None
    else:
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            file_path=relative_path,
            file_type=ext.lstrip('.'),
            original_filename=file.filename,
            status='uploaded',
        )
        db.session.add(submission)

    db.session.commit()

    return jsonify(submission=submission.to_dict()), 201


@submissions_bp.route('/assignments/<int:assignment_id>/submissions/batch', methods=['POST'])
@tenant_required
def upload_batch(assignment_id):
    """Upload multiple submission files at once."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    files = request.files.getlist('files')
    if not files:
        return jsonify(error='No files provided'), 400

    results = {'uploaded': 0, 'skipped': 0, 'errors': []}

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            results['errors'].append(f'{file.filename}: unsupported format')
            continue

        name, canvas_id = _parse_canvas_filename(file.filename)
        student = None
        if canvas_id:
            student = Student.query.filter_by(
                organization_id=g.organization_id, canvas_id=canvas_id
            ).first()

        if student is None:
            results['errors'].append(f'{file.filename}: could not identify student')
            continue

        # Save file
        org_slug = assignment.course.organization.slug
        storage_base = os.path.join(
            current_app.config['STORAGE_ROOT'],
            org_slug, assignment.course.slug,
            'submissions', assignment.slug, str(student.id)
        )
        os.makedirs(storage_base, exist_ok=True)

        dest_filename = f'submission{ext}'
        file.save(os.path.join(storage_base, dest_filename))
        relative_path = os.path.join(str(student.id), dest_filename)

        # Create/update submission
        submission = Submission.query.filter_by(
            assignment_id=assignment.id, student_id=student.id
        ).first()
        if submission:
            submission.file_path = relative_path
            submission.file_type = ext.lstrip('.')
            submission.original_filename = file.filename
            submission.status = 'uploaded'
        else:
            submission = Submission(
                assignment_id=assignment.id, student_id=student.id,
                file_path=relative_path, file_type=ext.lstrip('.'),
                original_filename=file.filename, status='uploaded',
            )
            db.session.add(submission)

        results['uploaded'] += 1

    db.session.commit()
    return jsonify(**results)


@submissions_bp.route('/submissions/<int:submission_id>', methods=['GET'])
@tenant_required
def get_submission(submission_id):
    """Get submission details including grading results."""
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    d = submission.to_dict(include_feedback=True)
    d['student'] = submission.student.to_dict()
    d['assignment'] = submission.assignment.to_dict()
    return jsonify(submission=d)


@submissions_bp.route('/submissions/<int:submission_id>/download', methods=['GET'])
@tenant_required
def download_submission(submission_id):
    """Download the original submission file."""
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    assignment = submission.assignment
    org_slug = assignment.course.organization.slug
    full_path = os.path.join(
        current_app.config['STORAGE_ROOT'],
        org_slug, assignment.course.slug,
        'submissions', assignment.slug, submission.file_path
    )

    if not os.path.exists(full_path):
        return jsonify(error='File not found on disk'), 404

    return send_file(full_path, as_attachment=True,
                     download_name=submission.original_filename)
