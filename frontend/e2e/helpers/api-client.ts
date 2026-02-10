const API_BASE = 'http://localhost:5001/api';

export class ApiClient {
  constructor(private token: string) {}

  private async request(method: string, path: string, body?: unknown) {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.token}`,
    };
    const init: RequestInit = { method, headers };

    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(body);
    } else if (body instanceof FormData) {
      init.body = body;
    }

    const res = await fetch(`${API_BASE}${path}`, init);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`API ${method} ${path} → ${res.status}: ${text}`);
    }
    return res.json();
  }

  async createCourse(data: { name: string; code?: string; semester: string; year: number }) {
    const res = await this.request('POST', '/courses', data);
    return res.course;
  }

  async createAssignment(
    courseId: number,
    data: { name: string; assignment_type: string; total_points: number; language?: string },
  ) {
    const res = await this.request('POST', `/courses/${courseId}/assignments`, data);
    return res.assignment;
  }

  async addStudent(courseId: number, data: { first_name: string; last_name: string; email: string; canvas_id?: string }) {
    const res = await this.request('POST', `/courses/${courseId}/students`, data);
    return res.student;
  }

  async uploadRubric(assignmentId: number, rubricJson: object) {
    const form = new FormData();
    const blob = new Blob([JSON.stringify(rubricJson)], { type: 'application/json' });
    form.append('file', blob, 'rubric.json');
    return this.request('POST', `/assignments/${assignmentId}/rubric`, form);
  }

  async saveRubricData(assignmentId: number, categories: unknown[]) {
    return this.request('PUT', `/assignments/${assignmentId}/rubric/data`, { categories });
  }

  async uploadSubmission(assignmentId: number, content: string, filename: string) {
    const form = new FormData();
    const blob = new Blob([content], { type: 'application/octet-stream' });
    form.append('file', blob, filename);
    return this.request('POST', `/assignments/${assignmentId}/submissions`, form);
  }

  async gradeBatch(assignmentId: number) {
    return this.request('POST', `/grading/batch/${assignmentId}`);
  }

  async submitReview(submissionId: number, data: { human_score: number; human_feedback: string }) {
    return this.request('PUT', `/grading/submissions/${submissionId}/review`, data);
  }
}

export async function loginViaApi(email: string, password: string): Promise<string> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  return data.access_token;
}
