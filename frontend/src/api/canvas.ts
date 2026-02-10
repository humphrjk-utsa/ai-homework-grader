import api from './client';

export interface CanvasSettings {
  canvas_url: string;
  has_token: boolean;
}

export interface CanvasCourse {
  canvas_id: string;
  name: string;
  code: string;
}

export async function getCanvasSettings(): Promise<CanvasSettings> {
  const { data } = await api.get('/canvas/settings');
  return data;
}

export async function updateCanvasSettings(payload: {
  canvas_url?: string;
  canvas_api_token?: string;
}): Promise<void> {
  await api.put('/canvas/settings', payload);
}

export async function testCanvasConnection(): Promise<{ connected: boolean; user?: { id: number; name: string }; error?: string }> {
  const { data } = await api.post('/canvas/test');
  return data;
}

export async function listCanvasCourses(): Promise<CanvasCourse[]> {
  const { data } = await api.get('/canvas/courses');
  return data.courses;
}

export async function syncStudents(courseId: number): Promise<{ created: number; updated: number; total: number }> {
  const { data } = await api.post(`/canvas/sync/students/${courseId}`);
  return data;
}

export async function pushGrades(assignmentId: number, canvasAssignmentId?: string): Promise<{ pushed: number; errors: string[]; total: number }> {
  const { data } = await api.post(`/canvas/push-grades/${assignmentId}`, {
    canvas_assignment_id: canvasAssignmentId,
  });
  return data;
}
