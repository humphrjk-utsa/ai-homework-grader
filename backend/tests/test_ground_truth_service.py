"""Tests for GroundTruthService: CSV parsing, comment classification, name matching, feedback conversion."""
import os
import csv
import tempfile

import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import Organization, User
from app.models.course import Course
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.services.ground_truth_service import (
    GroundTruthService,
    _classify_comment,
    _name_similarity,
)


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def service(app):
    with app.app_context():
        return GroundTruthService(app.config['STORAGE_ROOT'])


@pytest.fixture
def seed_data(db):
    """Seed org, user, course, assignment, and students for matching tests."""
    org = Organization(name='Test U', slug='test-u')
    db.session.add(org)
    db.session.flush()

    user = User(
        organization_id=org.id,
        email='prof@test.edu',
        first_name='Prof',
        last_name='Test',
        role='admin',
    )
    user.set_password('pw')
    db.session.add(user)
    db.session.flush()

    course = Course(
        organization_id=org.id,
        owner_id=user.id,
        name='BA 101',
        semester='Spring',
        year=2026,
        slug='ba-101',
    )
    db.session.add(course)
    db.session.flush()

    assignment = Assignment(
        course_id=course.id,
        name='HW 1',
        slug='hw-1',
        assignment_type='coding',
        total_points=100,
    )
    db.session.add(assignment)
    db.session.flush()

    s1 = Student(organization_id=org.id, first_name='Alice', last_name='Smith', canvas_id='12345')
    s2 = Student(organization_id=org.id, first_name='Bob', last_name='Jones', canvas_id='67890')
    s3 = Student(organization_id=org.id, first_name='Charlie', last_name='Brown')
    db.session.add_all([s1, s2, s3])
    db.session.flush()

    # Existing submission for Alice
    sub = Submission(
        assignment_id=assignment.id,
        student_id=s1.id,
        original_filename='alice.ipynb',
        file_type='ipynb',
        status='graded',
        ai_feedback={'overall_score': 80},
    )
    db.session.add(sub)
    db.session.commit()

    return {
        'org': org, 'user': user, 'course': course, 'assignment': assignment,
        'students': [s1, s2, s3], 'submission': sub,
    }


# ------- _classify_comment -------

class TestClassifyComment:
    def test_positive_comment(self):
        assert _classify_comment('Excellent work on this section!') == 'strength'

    def test_negative_comment(self):
        assert _classify_comment('There is an error in this calculation, needs fixing') == 'issue'

    def test_suggestion_comment(self):
        assert _classify_comment('Consider using a different approach, try plotting instead') == 'suggestion'

    def test_neutral_comment(self):
        assert _classify_comment('This section handles data loading.') == 'observation'

    def test_mixed_leans_negative(self):
        assert _classify_comment('Good start but missing key analysis and needs improvement') == 'issue'


# ------- _name_similarity -------

class TestNameSimilarity:
    def test_identical_names(self):
        assert _name_similarity('Alice Smith', 'Alice Smith') == 1.0

    def test_case_insensitive(self):
        assert _name_similarity('alice smith', 'ALICE SMITH') == 1.0

    def test_similar_names(self):
        score = _name_similarity('Alice Smth', 'Alice Smith')
        assert score > 0.85

    def test_dissimilar_names(self):
        score = _name_similarity('Alice Smith', 'Bob Jones')
        assert score < 0.5


# ------- extract_from_csv -------

class TestExtractFromCSV:
    def test_basic_csv(self, service, tmp_path):
        csv_file = tmp_path / 'scores.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_name', 'score', 'feedback'])
            writer.writerow(['Alice Smith', '85', 'Good work overall'])
            writer.writerow(['Bob Jones', '72', 'Needs more detail'])

        entries = service.extract_from_csv(str(csv_file))
        assert len(entries) == 2
        assert entries[0]['student_name'] == 'Alice Smith'
        assert entries[0]['score'] == 85.0
        assert entries[0]['feedback_text'] == 'Good work overall'
        assert entries[1]['student_name'] == 'Bob Jones'

    def test_column_name_variants(self, service, tmp_path):
        """Column names like 'name', 'grade', 'comments' should be detected."""
        csv_file = tmp_path / 'alt.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'grade', 'comments'])
            writer.writerow(['Charlie Brown', '90', 'Excellent'])

        entries = service.extract_from_csv(str(csv_file))
        assert len(entries) == 1
        assert entries[0]['student_name'] == 'Charlie Brown'
        assert entries[0]['score'] == 90.0
        assert entries[0]['feedback_text'] == 'Excellent'

    def test_component_scores(self, service, tmp_path):
        """Remaining numeric columns should be captured as component scores."""
        csv_file = tmp_path / 'components.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_name', 'score', 'technical', 'communication'])
            writer.writerow(['Alice', '80', '40', '35'])

        entries = service.extract_from_csv(str(csv_file))
        assert entries[0]['component_scores']['technical'] == 40.0
        assert entries[0]['component_scores']['communication'] == 35.0

    def test_student_id_column(self, service, tmp_path):
        csv_file = tmp_path / 'with_id.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'student_name', 'score'])
            writer.writerow(['12345', 'Alice Smith', '88'])

        entries = service.extract_from_csv(str(csv_file))
        assert entries[0]['student_id_hint'] == '12345'


# ------- match_to_students -------

class TestMatchToStudents:
    def test_canvas_id_match(self, app, db, service, seed_data):
        with app.app_context():
            items = [{'student_id_hint': '12345', 'student_name': None}]
            results = service.match_to_students(items, seed_data['assignment'].id, seed_data['org'].id)
            assert results[0]['match_method'] == 'canvas_id'
            assert results[0]['matched_student']['first_name'] == 'Alice'

    def test_exact_name_match(self, app, db, service, seed_data):
        with app.app_context():
            items = [{'student_id_hint': None, 'student_name': 'Smith Alice'}]
            results = service.match_to_students(items, seed_data['assignment'].id, seed_data['org'].id)
            assert results[0]['match_method'] == 'exact_name'

    def test_fuzzy_name_match(self, app, db, service, seed_data):
        with app.app_context():
            items = [{'student_id_hint': None, 'student_name': 'Allice Smith'}]
            results = service.match_to_students(items, seed_data['assignment'].id, seed_data['org'].id)
            assert results[0]['match_method'] is not None
            assert 'fuzzy' in results[0]['match_method']

    def test_no_match(self, app, db, service, seed_data):
        with app.app_context():
            items = [{'student_id_hint': None, 'student_name': 'Zara Xenon'}]
            results = service.match_to_students(items, seed_data['assignment'].id, seed_data['org'].id)
            assert results[0]['matched_student'] is None
            assert results[0]['match_method'] is None

    def test_existing_submission_detected(self, app, db, service, seed_data):
        with app.app_context():
            items = [{'student_id_hint': '12345', 'student_name': None}]
            results = service.match_to_students(items, seed_data['assignment'].id, seed_data['org'].id)
            assert results[0]['existing_submission_id'] is not None
            assert results[0]['has_existing_feedback'] is True


# ------- convert_to_ai_feedback -------

class TestConvertToAIFeedback:
    def test_basic_conversion(self, service):
        extracted = {
            'score': 85.0,
            'feedback_text': 'Overall good work.',
            'component_scores': {'technical': 40, 'communication': 35},
            'comments': [
                {'text': 'Excellent analysis of the data'},
                {'text': 'Missing error handling needs fix'},
                {'text': 'Consider using ggplot for visualization'},
                {'text': 'The data loading section works.'},
            ],
        }
        result = service.convert_to_ai_feedback(extracted, 100)

        assert result['final_score'] == 85.0
        assert result['max_points'] == 100
        assert result['component_scores']['technical'] == 40
        assert result['component_percentages']['technical'] == 40.0
        assert result['comprehensive_feedback']['instructor_comments'] == 'Overall good work.'
        assert len(result['comprehensive_feedback']['detailed_feedback']['analytical_strengths']) >= 1
        assert len(result['comprehensive_feedback']['detailed_feedback']['areas_for_development']) >= 1
        assert len(result['technical_analysis']['code_suggestions']) >= 1

    def test_empty_extraction(self, service):
        result = service.convert_to_ai_feedback({}, 50)
        assert result['final_score'] == 0
        assert result['max_points'] == 50
        assert result['comprehensive_feedback']['instructor_comments'] == ''

    def test_revisions_as_observations(self, service):
        extracted = {
            'revisions': [
                {'type': 'insertion', 'text': 'added new analysis'},
                {'type': 'deletion', 'text': 'removed duplicate code'},
            ],
        }
        result = service.convert_to_ai_feedback(extracted, 100)
        obs = result['technical_analysis']['technical_observations']
        assert len(obs) == 2
        assert '[insertion]' in obs[0]
        assert '[deletion]' in obs[1]
