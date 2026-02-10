import api from './client';

export interface TrainingStats {
  total_graded: number;
  total_reviewed: number;
  total_edited: number;
  assignments: { id: number; name: string; graded: number; reviewed: number; edited: number }[];
}

export interface TrainingJob {
  id: number;
  course_id: number;
  created_by_id: number;
  base_model: string;
  training_config: Record<string, unknown>;
  status: 'pending' | 'preparing' | 'training' | 'completed' | 'failed';
  progress_percent: number;
  output_model_path: string | null;
  training_metrics: Record<string, unknown> | null;
  training_samples: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ExportResult {
  file_path: string;
  relative_path: string;
  num_samples: number;
}

export interface SamplePreview {
  student_name: string;
  assignment: string;
  score: number | null;
  max_score: number | null;
  feedback_keys: string[];
}

export async function getTrainingStats(courseId: number): Promise<TrainingStats> {
  const { data } = await api.get(`/training/courses/${courseId}/stats`);
  return data.stats;
}

export async function exportTrainingData(courseId: number): Promise<ExportResult> {
  const { data } = await api.post(`/training/courses/${courseId}/export`);
  return data.result;
}

export async function previewTrainingData(courseId: number): Promise<SamplePreview[]> {
  const { data } = await api.get(`/training/courses/${courseId}/preview`);
  return data.previews;
}

export async function createTrainingJob(courseId: number, config: {
  base_model: string;
  epochs?: number;
  learning_rate?: number;
  lora_rank?: number;
  batch_size?: number;
}): Promise<TrainingJob> {
  const { data } = await api.post(`/training/courses/${courseId}/jobs`, config);
  return data.job;
}

export async function getTrainingJob(jobId: number): Promise<TrainingJob> {
  const { data } = await api.get(`/training/jobs/${jobId}`);
  return data.job;
}

export async function listTrainingJobs(courseId: number): Promise<TrainingJob[]> {
  const { data } = await api.get(`/training/courses/${courseId}/jobs`);
  return data.jobs;
}

export async function cancelTrainingJob(jobId: number): Promise<TrainingJob> {
  const { data } = await api.post(`/training/jobs/${jobId}/cancel`);
  return data.job;
}
