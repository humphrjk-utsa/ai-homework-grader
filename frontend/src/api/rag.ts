import api from './client';

export interface RAGStatus {
  indexed: boolean;
  num_chunks: number;
  source_files: string[];
  source_counts?: Record<string, number>;
  rag_enabled: boolean;
}

export interface RAGIndexResult {
  num_chunks: number;
  documents_indexed: number;
  reviewed_chunks_added?: number;
}

export async function getRAGStatus(assignmentId: number): Promise<RAGStatus> {
  const { data } = await api.get(`/rag/assignments/${assignmentId}/status`);
  return data.status;
}

export async function indexAssignment(assignmentId: number): Promise<RAGIndexResult> {
  const { data } = await api.post(`/rag/assignments/${assignmentId}/index`);
  return data.result;
}

export async function toggleRAG(assignmentId: number, enabled: boolean): Promise<{ rag_enabled: boolean }> {
  const { data } = await api.put(`/rag/assignments/${assignmentId}/toggle`, { enabled });
  return data;
}

export async function uploadContextDoc(assignmentId: number, file: File): Promise<{ message: string }> {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post(`/rag/assignments/${assignmentId}/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
