import api from './client';
import type { Submission, GradingJob, Report } from '../types';

export async function listSubmissions(assignmentId: number): Promise<Submission[]> {
  const { data } = await api.get(`/assignments/${assignmentId}/submissions`);
  return data.submissions;
}

export async function uploadSubmission(assignmentId: number, file: File): Promise<Submission> {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post(`/assignments/${assignmentId}/submissions`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data.submission;
}

export async function uploadBatch(assignmentId: number, files: FileList): Promise<{ uploaded: number }> {
  const form = new FormData();
  for (let i = 0; i < files.length; i++) {
    form.append('files', files[i]);
  }
  const { data } = await api.post(`/assignments/${assignmentId}/submissions/batch`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function gradeSingle(submissionId: number): Promise<Submission> {
  const { data } = await api.post(`/grading/single/${submissionId}`);
  return data.submission;
}

export async function gradeBatch(assignmentId: number): Promise<GradingJob> {
  const { data } = await api.post(`/grading/batch/${assignmentId}`);
  return data.job;
}

export async function getGradingJob(jobId: number): Promise<GradingJob> {
  const { data } = await api.get(`/grading/jobs/${jobId}`);
  return data.job;
}

export async function getSubmission(submissionId: number): Promise<Submission> {
  const { data } = await api.get(`/submissions/${submissionId}`);
  return data.submission;
}

export async function submitReview(submissionId: number, payload: {
  human_score?: number;
  human_feedback?: string;
}): Promise<Submission> {
  const { data } = await api.put(`/grading/submissions/${submissionId}/review`, payload);
  return data.submission;
}

export async function generateReport(submissionId: number): Promise<Report> {
  const { data } = await api.post(`/reports/generate/${submissionId}`);
  return data.report;
}

export async function downloadReport(submissionId: number): Promise<void> {
  const { data } = await api.post(`/reports/generate/${submissionId}`);
  const reportId = data.report?.id;
  if (reportId) {
    window.open(`/api/reports/${reportId}/download`, '_blank');
  }
}
