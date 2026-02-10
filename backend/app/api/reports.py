"""Report generation and download endpoints."""
import os

from flask import Blueprint, request, jsonify, g, current_app, send_file

from app.extensions import db
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.report import Report
from app.utils.decorators import tenant_required

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/generate/<int:submission_id>', methods=['POST'])
@tenant_required
def generate_report(submission_id):
    """Generate PDF report for a graded submission."""
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if submission.status not in ('graded', 'reviewed'):
        return jsonify(error='Submission must be graded before generating report'), 400

    from app.services.report_service import ReportService
    service = ReportService(current_app.config['STORAGE_ROOT'])

    try:
        report = service.generate_report(submission, g.current_user.id)
        return jsonify(report=report.to_dict()), 201
    except Exception as e:
        return jsonify(error='Report generation failed', message=str(e)), 500


@reports_bp.route('/generate/batch/<int:assignment_id>', methods=['POST'])
@tenant_required
def generate_batch_reports(assignment_id):
    """Generate reports for all graded submissions in an assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    graded = assignment.submissions.filter(
        Submission.status.in_(['graded', 'reviewed'])
    ).all()

    if not graded:
        return jsonify(error='No graded submissions found'), 400

    from app.services.report_service import ReportService
    service = ReportService(current_app.config['STORAGE_ROOT'])

    generated = 0
    errors = []

    for sub in graded:
        try:
            service.generate_report(sub, g.current_user.id)
            generated += 1
        except Exception as e:
            errors.append(f'Student {sub.student_id}: {str(e)}')

    return jsonify(generated=generated, errors=errors)


@reports_bp.route('/<int:report_id>/download', methods=['GET'])
@tenant_required
def download_report(report_id):
    """Download a report PDF."""
    report = Report.query.get_or_404(report_id)
    submission = report.submission
    if submission.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    full_path = os.path.join(current_app.config['STORAGE_ROOT'], report.file_path)
    if not os.path.exists(full_path):
        return jsonify(error='Report file not found'), 404

    student = submission.student
    download_name = f'{student.last_name}_{student.first_name}_report.pdf'
    return send_file(full_path, as_attachment=True, download_name=download_name)


@reports_bp.route('/assignments/<int:assignment_id>/export/zip', methods=['GET'])
@tenant_required
def export_reports_zip(assignment_id):
    """Download all PDF reports for an assignment as a ZIP archive."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    reports = Report.query.join(Submission).filter(
        Submission.assignment_id == assignment.id
    ).all()

    if not reports:
        return jsonify(error='No reports found for this assignment'), 404

    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for report in reports:
            full_path = os.path.join(current_app.config['STORAGE_ROOT'], report.file_path)
            if os.path.exists(full_path):
                student = report.submission.student
                arcname = f'{student.last_name}_{student.first_name}_report.pdf'
                zf.write(full_path, arcname)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{assignment.slug}_reports.zip',
    )


@reports_bp.route('/assignments/<int:assignment_id>/export/csv', methods=['GET'])
@tenant_required
def export_grades_csv(assignment_id):
    """Export grades as CSV."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Student ID', 'Canvas ID', 'First Name', 'Last Name', 'Email',
        'AI Score', 'Human Score', 'Final Score', 'Max Score', 'Status',
    ])

    for sub in assignment.submissions.all():
        student = sub.student
        writer.writerow([
            student.student_id_external or '', student.canvas_id or '',
            student.first_name, student.last_name, student.email or '',
            sub.ai_score or '', sub.human_score or '',
            sub.final_score or '', sub.max_score or '', sub.status,
        ])

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={assignment.slug}_grades.csv'}
    )
