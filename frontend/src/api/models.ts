import api from './client';

export interface CustomModel {
  id: number | null;
  name: string;
  model_id: string;
  model_type: 'base' | 'finetuned' | 'custom';
  status: 'available' | 'deploying' | 'running' | 'stopped' | 'error';
  server_url: string | null;
  container_id: string | null;
  deployment_config: Record<string, unknown>;
  is_builtin: boolean;
  organization_id?: number;
  course_id?: number | null;
  training_job_id?: number | null;
  description?: string;
  created_at?: string;
}

export async function listModels(courseId?: number): Promise<CustomModel[]> {
  const params = courseId ? { course_id: courseId } : {};
  const { data } = await api.get('/models', { params });
  return data.models;
}

export async function registerModel(payload: {
  name: string;
  model_id: string;
  model_type?: string;
  course_id?: number;
  deployment_config?: Record<string, unknown>;
}): Promise<CustomModel> {
  const { data } = await api.post('/models', payload);
  return data.model;
}

export async function deployModel(modelId: number, config?: Record<string, unknown>): Promise<{
  container_id: string;
  server_url: string;
  status: string;
}> {
  const { data } = await api.post(`/models/${modelId}/deploy`, config || {});
  return data.result;
}

export async function stopModel(modelId: number): Promise<{ status: string }> {
  const { data } = await api.post(`/models/${modelId}/stop`);
  return data.result;
}

export async function getRunningModels(): Promise<CustomModel[]> {
  const { data } = await api.get('/models/running');
  return data.models;
}

export async function setCourseModelConfig(courseId: number, config: Record<string, unknown>): Promise<Record<string, unknown>> {
  const { data } = await api.put(`/models/course-config/${courseId}`, config);
  return data.settings;
}
