import api from './client';
import type { Course } from '../types';

export async function listCourses(): Promise<Course[]> {
  const { data } = await api.get('/courses');
  return data.courses;
}

export async function getCourse(id: number): Promise<Course> {
  const { data } = await api.get(`/courses/${id}`);
  return data.course;
}

export async function createCourse(payload: {
  name: string;
  code?: string;
  semester: string;
  year: number;
}): Promise<Course> {
  const { data } = await api.post('/courses', payload);
  return data.course;
}

export async function updateCourse(id: number, payload: Partial<Course>): Promise<Course> {
  const { data } = await api.put(`/courses/${id}`, payload);
  return data.course;
}

export async function deleteCourse(id: number): Promise<void> {
  await api.delete(`/courses/${id}`);
}

export async function getCourseStats(id: number) {
  const { data } = await api.get(`/courses/${id}/stats`);
  return data;
}
