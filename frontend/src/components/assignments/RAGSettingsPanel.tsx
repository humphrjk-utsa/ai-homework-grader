import { useState, useEffect, useRef } from 'react';
import { getRAGStatus, indexAssignment, toggleRAG, uploadContextDoc } from '../../api/rag';
import type { RAGStatus } from '../../api/rag';

interface RAGSettingsPanelProps {
  assignmentId: number;
}

export default function RAGSettingsPanel({ assignmentId }: RAGSettingsPanelProps) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<RAGStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open && !status) {
      setLoading(true);
      getRAGStatus(assignmentId)
        .then(setStatus)
        .catch(() => setStatus(null))
        .finally(() => setLoading(false));
    }
  }, [open, assignmentId, status]);

  const handleToggle = async () => {
    if (!status) return;
    setToggling(true);
    try {
      const result = await toggleRAG(assignmentId, !status.rag_enabled);
      setStatus({ ...status, rag_enabled: result.rag_enabled });
    } catch {
      setMessage('Failed to toggle RAG');
    } finally {
      setToggling(false);
    }
  };

  const handleIndex = async () => {
    setIndexing(true);
    setMessage('');
    try {
      const result = await indexAssignment(assignmentId);
      setMessage(
        `Indexed ${result.documents_indexed} document(s) into ${result.num_chunks} chunks` +
          (result.reviewed_chunks_added
            ? ` + ${result.reviewed_chunks_added} reviewed submission chunks`
            : ''),
      );
      // Refresh status
      const updated = await getRAGStatus(assignmentId);
      setStatus(updated);
    } catch {
      setMessage('Indexing failed. Check that assignment has rubric/solution uploaded.');
    } finally {
      setIndexing(false);
    }
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage('');
    try {
      const result = await uploadContextDoc(assignmentId, file);
      setMessage(result.message);
      if (fileRef.current) fileRef.current.value = '';
    } catch (err: any) {
      setMessage(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-6 text-left"
      >
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Reference Materials for AI</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Give the AI access to rubrics, solutions, and your past feedback when grading
          </p>
        </div>
        <div className="flex items-center gap-3">
          {status?.rag_enabled && (
            <span className="px-2 py-0.5 text-xs font-medium rounded bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300">
              Active
            </span>
          )}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
          </svg>
        </div>
      </button>

      {open && (
        <div className="px-6 pb-6 space-y-4 border-t border-gray-200 dark:border-gray-700 pt-4">
          {loading ? (
            <p className="text-sm text-gray-400">Loading RAG status...</p>
          ) : (
            <>
              {/* Toggle */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Use Reference Materials When Grading
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500">
                    When enabled, the AI looks up your rubric, solution, and past reviewed feedback to grade more consistently
                  </p>
                </div>
                <button
                  onClick={handleToggle}
                  disabled={toggling}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    status?.rag_enabled
                      ? 'bg-indigo-600'
                      : 'bg-gray-300 dark:bg-gray-600'
                  } ${toggling ? 'opacity-50' : ''}`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      status?.rag_enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Index Status */}
              <div className="bg-gray-50 dark:bg-gray-900/30 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Index Status
                    </p>
                    {status?.indexed ? (
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400 space-y-0.5">
                        <p>{status.num_chunks} chunks indexed</p>
                        {status.source_counts && (
                          <p>
                            {Object.entries(status.source_counts)
                              .map(([src, count]) => `${src}: ${count}`)
                              .join(' | ')}
                          </p>
                        )}
                        <p>Files: {status.source_files.join(', ')}</p>
                      </div>
                    ) : (
                      <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                        Not indexed yet. Click "Index Materials" to build the search index.
                      </p>
                    )}
                  </div>
                  <button
                    onClick={handleIndex}
                    disabled={indexing}
                    className="px-3 py-1.5 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {indexing ? 'Indexing...' : status?.indexed ? 'Re-index' : 'Index Materials'}
                  </button>
                </div>
              </div>

              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <p className="text-xs text-green-700 dark:text-green-400">
                  When you edit and save feedback on graded submissions, those edits are included the next time you index. This helps the AI match your grading style over time.
                </p>
              </div>

              {/* Upload additional docs */}
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Additional Context Documents
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">
                  Upload extra reference materials (txt, md, csv, json, py, r, rmd, ipynb)
                </p>
                <div className="flex items-center gap-2">
                  <input
                    ref={fileRef}
                    type="file"
                    accept=".txt,.md,.csv,.json,.py,.r,.rmd,.ipynb"
                    className="block text-sm text-gray-500 dark:text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 dark:file:bg-indigo-900/30 dark:file:text-indigo-300 hover:file:bg-indigo-100"
                  />
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="px-3 py-1.5 text-sm font-medium rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </button>
                </div>
              </div>

              {/* Status message */}
              {message && (
                <p className="text-sm text-indigo-600 dark:text-indigo-400">{message}</p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
