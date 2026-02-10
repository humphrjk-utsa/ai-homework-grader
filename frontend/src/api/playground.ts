import api from './client';

export interface PromptTestRunInput {
  assignment_id: number;
  run_type: 'single' | 'sample' | 'comparison';
  submission_ids: number[];
  label?: string;
  code_analysis_prompt?: string;
  feedback_prompt?: string;
  comparison_code_analysis_prompt?: string;
  comparison_feedback_prompt?: string;
}

export interface PromptTestResult {
  student_name: string;
  score: number | null;
  max_points?: number;
  feedback?: Record<string, unknown>;
  raw_prompts?: { code_analysis?: string; feedback?: string };
  grading_stats?: Record<string, unknown>;
  error?: string | null;
}

export interface PromptTestRun {
  id: number;
  assignment_id: number;
  created_by_id: number;
  run_type: 'single' | 'sample' | 'comparison';
  label: string | null;
  code_analysis_prompt: string | null;
  feedback_prompt: string | null;
  comparison_code_analysis_prompt: string | null;
  comparison_feedback_prompt: string | null;
  submission_ids: number[];
  results: Record<string, PromptTestResult> | { version_a: Record<string, PromptTestResult>; version_b: Record<string, PromptTestResult> } | null;
  status: 'pending' | 'running' | 'completed' | 'error';
  error_message: string | null;
  total_duration_seconds: number | null;
  grading_stats: Record<string, unknown> | null;
  created_at: string;
  completed_at: string | null;
}

export async function runPromptTest(input: PromptTestRunInput): Promise<{ test_run: PromptTestRun; async_mode: boolean }> {
  const { data } = await api.post('/playground/test', input);
  return data;
}

export async function getTestRun(testRunId: number): Promise<PromptTestRun> {
  const { data } = await api.get(`/playground/test/${testRunId}`);
  return data.test_run;
}

export async function getTestHistory(assignmentId: number): Promise<PromptTestRun[]> {
  const { data } = await api.get(`/playground/assignments/${assignmentId}/history`);
  return data.runs;
}

export async function applyTestPrompts(
  testRunId: number,
  version?: 'a' | 'b',
  assignmentVersion?: number,
): Promise<Record<string, unknown>> {
  const { data } = await api.post(`/playground/test/${testRunId}/apply`, {
    version,
    assignment_version: assignmentVersion,
  });
  return data.assignment;
}

export async function deleteTestRun(testRunId: number): Promise<void> {
  await api.delete(`/playground/test/${testRunId}`);
}
