import api from './client';
import type { RubricData } from '../types';

export async function getRubricData(assignmentId: number): Promise<RubricData> {
  const { data } = await api.get(`/assignments/${assignmentId}/rubric/data`);
  return data.rubric;
}

export async function saveRubricData(assignmentId: number, rubric: RubricData, version?: number): Promise<RubricData> {
  const { data } = await api.put(`/assignments/${assignmentId}/rubric/data`, {
    categories: rubric.categories,
    ...(version !== undefined && { version }),
  });
  return data.rubric;
}

export async function generatePrompts(assignmentId: number): Promise<{
  code_analysis_prompt: string;
  feedback_prompt: string;
}> {
  const { data } = await api.post(`/assignments/${assignmentId}/generate-prompts`);
  return data;
}
