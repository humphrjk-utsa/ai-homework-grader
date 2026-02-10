"""Canvas LMS integration service.

Wraps the canvasapi library to sync students, assignments, and submissions
between Canvas and the AI Homework Grader.
"""
import time
import logging

logger = logging.getLogger(__name__)


class CanvasService:
    """Thin wrapper around canvasapi with built-in rate limiting."""

    # Canvas rate limit: 700 cost units per 10 seconds.  We keep it
    # conservative at ~90 requests per minute to stay safely under.
    MIN_REQUEST_INTERVAL = 0.7  # seconds between Canvas API calls

    def __init__(self, canvas_url: str, api_token: str):
        from canvasapi import Canvas
        self._canvas = Canvas(canvas_url, api_token)
        self._last_request = 0.0

    def _throttle(self):
        """Simple rate limiter."""
        elapsed = time.time() - self._last_request
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request = time.time()

    # ------------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------------
    def test_connection(self) -> dict:
        """Test Canvas connection. Returns current user info."""
        self._throttle()
        user = self._canvas.get_current_user()
        return {'id': user.id, 'name': user.name}

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------
    def list_courses(self) -> list[dict]:
        """List courses the API token owner can see."""
        self._throttle()
        courses = self._canvas.get_courses(enrollment_type='teacher')
        results = []
        for c in courses:
            self._throttle()
            results.append({
                'canvas_id': str(c.id),
                'name': getattr(c, 'name', ''),
                'code': getattr(c, 'course_code', ''),
            })
        return results

    # ------------------------------------------------------------------
    # Students
    # ------------------------------------------------------------------
    def sync_students(self, canvas_course_id: int) -> list[dict]:
        """Fetch enrolled students from a Canvas course."""
        self._throttle()
        course = self._canvas.get_course(canvas_course_id)
        self._throttle()
        users = course.get_users(enrollment_type=['student'])
        results = []
        for u in users:
            self._throttle()
            results.append({
                'canvas_id': str(u.id),
                'first_name': getattr(u, 'first_name', '') or getattr(u, 'short_name', ''),
                'last_name': getattr(u, 'last_name', '') or '',
                'email': getattr(u, 'email', '') or getattr(u, 'login_id', ''),
            })
        return results

    # ------------------------------------------------------------------
    # Assignments
    # ------------------------------------------------------------------
    def list_assignments(self, canvas_course_id: int) -> list[dict]:
        """List assignments in a Canvas course."""
        self._throttle()
        course = self._canvas.get_course(canvas_course_id)
        self._throttle()
        assignments = course.get_assignments()
        results = []
        for a in assignments:
            self._throttle()
            results.append({
                'canvas_id': str(a.id),
                'name': a.name,
                'due_date': getattr(a, 'due_at', None),
                'points_possible': getattr(a, 'points_possible', 0),
            })
        return results

    # ------------------------------------------------------------------
    # Submissions
    # ------------------------------------------------------------------
    def download_submissions(self, canvas_course_id: int,
                             canvas_assignment_id: int) -> list[dict]:
        """Get submission metadata + attachment URLs from Canvas."""
        self._throttle()
        course = self._canvas.get_course(canvas_course_id)
        self._throttle()
        assignment = course.get_assignment(canvas_assignment_id)
        self._throttle()
        submissions = assignment.get_submissions(include=['user'])
        results = []
        for sub in submissions:
            self._throttle()
            attachments = getattr(sub, 'attachments', []) or []
            if not attachments:
                continue
            results.append({
                'canvas_user_id': str(sub.user_id),
                'canvas_submission_id': str(sub.id),
                'user_name': getattr(sub, 'user', {}).get('name', ''),
                'attachments': [{
                    'filename': att.get('filename', ''),
                    'url': att.get('url', ''),
                    'content_type': att.get('content-type', ''),
                } for att in attachments],
            })
        return results

    # ------------------------------------------------------------------
    # Grade push-back
    # ------------------------------------------------------------------
    def push_grade(self, canvas_course_id: int, canvas_assignment_id: int,
                   canvas_user_id: int, score: float,
                   comment: str = '') -> bool:
        """Push a grade + comment to Canvas."""
        self._throttle()
        course = self._canvas.get_course(canvas_course_id)
        self._throttle()
        assignment = course.get_assignment(canvas_assignment_id)
        self._throttle()
        submission = assignment.get_submission(canvas_user_id)
        self._throttle()
        update = {'posted_grade': score}
        submission.edit(submission=update)
        if comment:
            self._throttle()
            submission.edit(comment={'text_comment': comment})
        return True
