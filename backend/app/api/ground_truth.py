"""Ground truth upload endpoints for previously graded assignments."""
import os
from datetime import datetime

from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.assignment import Assignment
from app.models.student import Student
from app.models.submission import Submission
from app.utils.decorators import tenant_required, role_required
from app.api.submissions import _parse_canvas_filename

ground_truth_bp = Blueprint('ground_truth', __name__)

ALLOWED_GT_EXTENSIONS = {'.docx', '.pdf', '.csv', '.xlsx'}


@ground_truth_bp.route('/assignments/<int:assignment_id>/ground-truth/upload', methods=['POST'])
@role_required('admin', 'instructor')
def upload_ground_truth(assignment_id):
    """Upload files, extract feedback, match to students, return preview."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    files = request.files.getlist('files')
    if not files:
        return jsonify(error='No files provided'), 400

    from app.services.ground_truth_service import GroundTruthService
    service = GroundTruthService(current_app.config['STORAGE_ROOT'])

    # Storage directory for ground truth uploads
    org_slug = assignment.course.organization.slug
    gt_dir = os.path.join(
        current_app.config['STORAGE_ROOT'],
        org_slug, assignment.course.slug,
        'ground_truth', assignment.slug,
    )
    os.makedirs(gt_dir, exist_ok=True)

    all_results = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_GT_EXTENSIONS:
            all_results.append({'filename': file.filename, 'error': f'Unsupported format: {ext}'})
            continue

        safe_name = secure_filename(file.filename)
        dest = os.path.join(gt_dir, safe_name)
        file.save(dest)

        file_type = ext.lstrip('.')
        if file_type == 'xlsx':
            file_type = 'csv'  # pandas handles both

        try:
            result = service.process_upload(assignment_id, dest, file_type, g.organization_id)
            result['filename'] = file.filename
            all_results.append(result)
        except Exception as e:
            all_results.append({'filename': file.filename, 'error': str(e)})

    return jsonify(results=all_results)


@ground_truth_bp.route('/assignments/<int:assignment_id>/ground-truth/upload-batch-docs', methods=['POST'])
@role_required('admin', 'instructor')
def upload_batch_docs(assignment_id):
    """Upload multiple docx/pdf files (one per student), with filename-based matching."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    files = request.files.getlist('files')
    if not files:
        return jsonify(error='No files provided'), 400

    from app.services.ground_truth_service import GroundTruthService
    service = GroundTruthService(current_app.config['STORAGE_ROOT'])

    org_slug = assignment.course.organization.slug
    gt_dir = os.path.join(
        current_app.config['STORAGE_ROOT'],
        org_slug, assignment.course.slug,
        'ground_truth', assignment.slug,
    )
    os.makedirs(gt_dir, exist_ok=True)

    results = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in {'.docx', '.pdf'}:
            results.append({'filename': file.filename, 'error': 'Only .docx and .pdf supported'})
            continue

        # Parse filename for student identification
        name_part, canvas_id = _parse_canvas_filename(file.filename)
        student = None
        if canvas_id:
            student = Student.query.filter_by(
                organization_id=g.organization_id, canvas_id=canvas_id,
            ).first()

        # Save and extract
        safe_name = secure_filename(file.filename)
        dest = os.path.join(gt_dir, safe_name)
        file.save(dest)

        try:
            extracted = service.process_upload(assignment_id, dest, ext.lstrip('.'), g.organization_id)
            extracted['filename'] = file.filename
            extracted['parsed_name'] = name_part

            if student:
                extracted['matched_student'] = student.to_dict()
                existing_sub = Submission.query.filter_by(
                    assignment_id=assignment_id, student_id=student.id,
                ).first()
                extracted['existing_submission_id'] = existing_sub.id if existing_sub else None

            results.append(extracted)
        except Exception as e:
            results.append({'filename': file.filename, 'error': str(e)})

    return jsonify(results=results)


@ground_truth_bp.route('/assignments/<int:assignment_id>/ground-truth/commit', methods=['POST'])
@role_required('admin', 'instructor')
def commit_ground_truth(assignment_id):
    """Finalize reviewed entries → write to Submission.edited_feedback."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}
    entries = data.get('entries', [])
    if not entries:
        return jsonify(error='No entries to commit'), 400

    committed = 0
    skipped = 0
    errors = []

    for entry in entries:
        student_id = entry.get('student_id')
        feedback = entry.get('edited_feedback')
        score = entry.get('score')

        if not student_id:
            skipped += 1
            continue

        student = Student.query.filter_by(
            id=student_id, organization_id=g.organization_id,
        ).first()
        if not student:
            errors.append(f'Student {student_id} not found')
            continue

        # Find or create submission
        submission = Submission.query.filter_by(
            assignment_id=assignment_id,
            student_id=student_id,
        ).first()

        if not submission:
            submission = Submission(
                assignment_id=assignment_id,
                student_id=student_id,
                original_filename='ground_truth_upload',
                file_type='ground_truth',
                status='reviewed',
            )
            db.session.add(submission)

        submission.edited_feedback = feedback
        submission.status = 'reviewed'
        submission.reviewed_at = datetime.utcnow()
        submission.max_score = assignment.total_points

        if score is not None:
            submission.human_score = float(score)
            submission.final_score = float(score)
        elif feedback and feedback.get('final_score') is not None:
            submission.human_score = float(feedback['final_score'])
            submission.final_score = float(feedback['final_score'])

        committed += 1

    db.session.commit()

    return jsonify(committed=committed, skipped=skipped, errors=errors)
