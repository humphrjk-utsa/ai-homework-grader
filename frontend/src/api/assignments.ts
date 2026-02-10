import api from './client';
import type { Assignment } from '../types';

export async function listAssignments(courseId: number): Promise<Assignment[]> {
  const { data } = await api.get(`/courses/${courseId}/assignments`);
  return data.assignments;
}

export async function getAssignment(id: number): Promise<Assignment> {
  const { data } = await api.get(`/assignments/${id}`);
  return data.assignment;
}

export async function createAssignment(courseId: number, payload: {
  name: string;
  assignment_type: string;
  total_points: number;
  language?: string;
  description?: string;
}): Promise<Assignment> {
  const { data } = await api.post(`/courses/${courseId}/assignments`, payload);
  return data.assignment;
}

export async function updateAssignment(id: number, payload: Partial<Assignment>): Promise<Assignment> {
  const { data } = await api.put(`/assignments/${id}`, payload);
  return data.assignment;
}

export async function deleteAssignment(id: number): Promise<void> {
  await api.delete(`/assignments/${id}`);
}

export async function uploadRubric(id: number, file: File): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  await api.post(`/assignments/${id}/rubric`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export async function uploadSolution(id: number, file: File): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  await api.post(`/assignments/${id}/solution`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export async function uploadTemplate(id: number, file: File): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  await api.post(`/assignments/${id}/template`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}
