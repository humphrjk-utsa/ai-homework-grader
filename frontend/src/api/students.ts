import api from './client';
import type { Student } from '../types';

export async function listStudents(courseId: number): Promise<Student[]> {
  const { data } = await api.get(`/courses/${courseId}/students`);
  return data.students;
}

export async function addStudent(courseId: number, payload: {
  first_name: string;
  last_name: string;
  email: string;
  canvas_id?: string;
}): Promise<Student> {
  const { data } = await api.post(`/courses/${courseId}/students`, payload);
  return data.student;
}

export async function importStudentsCsv(courseId: number, file: File): Promise<{ imported: number; errors: string[] }> {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post(`/courses/${courseId}/students/import`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
