import api from './client';
import type { AIFeedback } from '../types';

export interface GroundTruthEntry {
  filename?: string;
  student_name?: string | null;
  student_id_hint?: string | null;
  score?: number | null;
  feedback_text?: string | null;
  component_scores?: Record<string, number>;
  converted_feedback?: AIFeedback;
  matched_student?: { id: number; first_name: string; last_name: string; email: string } | null;
  match_method?: string | null;
  existing_submission_id?: number | null;
  has_existing_feedback?: boolean;
  error?: string;
}

export interface GroundTruthUploadResult {
  filename: string;
  mode?: 'single' | 'batch';
  total_entries?: number;
  matched_count?: number;
  entries?: GroundTruthEntry[];
  extracted?: Record<string, unknown>;
  converted_feedback?: AIFeedback;
  parsed_name?: string;
  matched_student?: { id: number; first_name: string; last_name: string } | null;
  existing_submission_id?: number | null;
  error?: string;
}

export interface CommitEntry {
  student_id: number;
  score?: number | null;
  edited_feedback: AIFeedback;
}

export interface CommitResult {
  committed: number;
  skipped: number;
  errors: string[];
}

export async function uploadGroundTruth(
  assignmentId: number,
  files: FileList | File[],
): Promise<GroundTruthUploadResult[]> {
  const form = new FormData();
  for (let i = 0; i < files.length; i++) {
    form.append('files', files[i]);
  }
  const { data } = await api.post(
    `/assignments/${assignmentId}/ground-truth/upload`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return data.results;
}

export async function uploadBatchDocs(
  assignmentId: number,
  files: FileList | File[],
): Promise<GroundTruthUploadResult[]> {
  const form = new FormData();
  for (let i = 0; i < files.length; i++) {
    form.append('files', files[i]);
  }
  const { data } = await api.post(
    `/assignments/${assignmentId}/ground-truth/upload-batch-docs`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return data.results;
}

export async function commitGroundTruth(
  assignmentId: number,
  entries: CommitEntry[],
): Promise<CommitResult> {
  const { data } = await api.post(
    `/assignments/${assignmentId}/ground-truth/commit`,
    { entries },
  );
  return data;
}
