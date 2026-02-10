import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { getAssignment, updateAssignment, uploadRubric, uploadSolution, uploadTemplate } from '../../api/assignments';
import { listSubmissions, uploadSubmission, uploadBatch, gradeSingle, gradeBatch, getGradingJob, downloadReport } from '../../api/submissions';
import { generatePrompts } from '../../api/rubric';
import type { Assignment, Submission, GradingJob } from '../../types';

export default function AssignmentDetailPage() {
  const { user } = useAuth();
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [gradingJob, setGradingJob] = useState<GradingJob | null>(null);
  const [promptsOpen, setPromptsOpen] = useState(false);
  const [codePrompt, setCodePrompt] = useState('');
  const [feedbackPrompt, setFeedbackPrompt] = useState('');
  const [savingPrompts, setSavingPrompts] = useState(false);
  const [promptSaved, setPromptSaved] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const id = Number(assignmentId);

  const refresh = useCallback(() => {
    Promise.all([
      getAssignment(id),
      listSubmissions(id),
    ]).then(([a, s]) => {
      setAssignment(a);
      setSubmissions(s);
      setCodePrompt(a.code_analysis_prompt || '');
      setFeedbackPrompt(a.feedback_prompt || '');
    }).finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    if (!gradingJob || gradingJob.status === 'completed' || gradingJob.status === 'failed') return;
    const interval = setInterval(async () => {
      const job = await getGradingJob(gradingJob.id);
      setGradingJob(job);
      if (job.status === 'completed' || job.status === 'failed') {
        clearInterval(interval);
        refresh();
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [gradingJob, refresh]);

  const handleFileUpload = async (type: 'rubric' | 'solution' | 'template', file: File) => {
    const fn = { rubric: uploadRubric, solution: uploadSolution, template: uploadTemplate }[type];
    await fn(id, file);
    refresh();
  };

  const handleSubmissionUpload = async () => {
    const files = fileInputRef.current?.files;
    if (!files?.length) return;
    setUploading(true);
    try {
      if (files.length === 1) {
        await uploadSubmission(id, files[0]);
      } else {
        await uploadBatch(id, files);
      }
      refresh();
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleGradeAll = async () => {
    try {
      const job = await gradeBatch(id);
      setGradingJob(job);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to start grading');
    }
  };

  const handleGradeSingle = async (subId: number) => {
    try {
      await gradeSingle(subId);
      refresh();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Grading failed');
    }
  };

  const handleSavePrompts = async () => {
    setSavingPrompts(true);
    setPromptSaved(false);
    try {
      const updated = await updateAssignment(id, {
        code_analysis_prompt: codePrompt || null,
        feedback_prompt: feedbackPrompt || null,
        version: assignment!.version,
      });
      setAssignment(updated);
      setPromptSaved(true);
      setTimeout(() => setPromptSaved(false), 3000);
    } catch (err: any) {
      if (err.response?.status === 409) {
        alert('This assignment was modified by another user. The page will refresh with the latest data.');
        refresh();
      } else {
        alert(err.response?.data?.error || 'Failed to save prompts');
      }
    } finally {
      setSavingPrompts(false);
    }
  };

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Loading...</p>;
  if (!assignment) return <p className="text-red-500">Assignment not found</p>;

  const statusColor: Record<string, string> = {
    uploaded: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    queued: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
    grading: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    graded: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
    reviewed: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
    error: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  };

  return (
    <div>
      <Link to={`/courses/${assignment.course_id}`} className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Back to course
      </Link>

      <div className="mt-2 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{assignment.name}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
              assignment.assignment_type === 'coding'
                ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
                : 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
            }`}>{assignment.assignment_type}</span>
            {' '}{assignment.total_points} points
            {assignment.language && ` - ${assignment.language}`}
          </p>
        </div>
      </div>

      {/* Assignment Files */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Assignment Files</h2>
        <div className="mt-4 grid grid-cols-3 gap-4">
          {(['rubric', 'solution', 'template'] as const).map((type) => (
            <div key={type} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{type}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                {assignment[`${type}_path` as keyof Assignment] ? 'Uploaded' : 'Not uploaded'}
              </p>
              <div className="mt-2 flex items-center gap-2">
                <label className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 rounded-md cursor-pointer hover:bg-indigo-100 dark:hover:bg-indigo-900/50">
                  Upload
                  <input type="file" className="hidden" onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(type, file);
                  }} />
                </label>
                {type === 'rubric' && (
                  <Link to={`/assignments/${id}/rubric/edit`}
                    className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30 rounded-md hover:bg-green-100 dark:hover:bg-green-900/50">
                    Build
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Prompts */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setPromptsOpen(!promptsOpen)}
          className="w-full flex items-center justify-between p-6 text-left"
        >
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Prompts</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Custom prompts override the defaults for this assignment
            </p>
          </div>
          <svg className={`w-5 h-5 text-gray-400 transition-transform ${promptsOpen ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
          </svg>
        </button>
        {promptsOpen && (
          <div className="px-6 pb-6 space-y-4 border-t border-gray-200 dark:border-gray-700 pt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {assignment.assignment_type === 'coding' ? 'Code Analysis Prompt' : 'Content Analysis Prompt'}
              </label>
              <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">
                Sent to the analysis model. Leave blank to use the default prompt.
              </p>
              <textarea
                value={codePrompt}
                onChange={(e) => setCodePrompt(e.target.value)}
                rows={6}
                placeholder={assignment.assignment_type === 'coding'
                  ? 'e.g. Analyze the student R code for correctness, style, and output accuracy...'
                  : 'e.g. Analyze the student response for completeness, accuracy, and critical thinking...'}
                className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Feedback Prompt
              </label>
              <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">
                Sent to the feedback model. Leave blank to use the default prompt.
              </p>
              <textarea
                value={feedbackPrompt}
                onChange={(e) => setFeedbackPrompt(e.target.value)}
                rows={6}
                placeholder="e.g. Generate constructive feedback for the student based on the analysis..."
                className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleSavePrompts}
                disabled={savingPrompts}
                className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {savingPrompts ? 'Saving...' : 'Save Prompts'}
              </button>
              {assignment.rubric_path && (
                <button
                  onClick={async () => {
                    const hasExisting = codePrompt || feedbackPrompt;
                    if (hasExisting && !confirm('This will overwrite the current prompts with auto-generated ones from the rubric. Continue?')) return;
                    try {
                      const prompts = await generatePrompts(id);
                      setCodePrompt(prompts.code_analysis_prompt);
                      setFeedbackPrompt(prompts.feedback_prompt);
                      setPromptSaved(true);
                      setTimeout(() => setPromptSaved(false), 3000);
                    } catch (err: any) {
                      alert(err.response?.data?.error || 'Failed to generate prompts');
                    }
                  }}
                  className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                >
                  Generate from Rubric
                </button>
              )}
              {promptSaved && (
                <span className="text-sm text-green-600 dark:text-green-400">Saved</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Submissions */}
      <div className="mt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Submissions ({submissions.length})
          </h2>
          <div className="flex space-x-2">
            <label className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 cursor-pointer">
              Upload Files
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".ipynb,.pdf,.docx,.doc,.sas,.sql,.py,.r,.rmd"
                className="hidden"
                onChange={handleSubmissionUpload}
              />
            </label>
            {submissions.length > 0 && (
              <>
                {user?.role !== 'ta' && (
                  <button
                    onClick={handleGradeAll}
                    disabled={!!gradingJob && gradingJob.status === 'running'}
                    className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Grade All
                  </button>
                )}
                <a
                  href={`/api/reports/assignments/${id}/export/csv`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Export CSV
                </a>
                <a
                  href={`/api/reports/assignments/${id}/export/zip`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Download Reports
                </a>
              </>
            )}
          </div>
        </div>

        {gradingJob && gradingJob.status === 'running' && (
          <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="flex justify-between text-sm">
              <span className="text-blue-700 dark:text-blue-300">Grading in progress...</span>
              <span className="text-blue-700 dark:text-blue-300">
                {gradingJob.completed_submissions}/{gradingJob.total_submissions}
              </span>
            </div>
            <div className="mt-2 bg-blue-200 dark:bg-blue-800 rounded-full h-2">
              <div
                className="bg-blue-600 rounded-full h-2 transition-all"
                style={{ width: `${gradingJob.progress_percent}%` }}
              />
            </div>
          </div>
        )}

        {uploading && (
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Uploading...</p>
        )}

        {submissions.length === 0 ? (
          <div className="mt-4 p-8 text-center bg-white dark:bg-gray-800 rounded-lg border border-dashed border-gray-300 dark:border-gray-600">
            <p className="text-gray-500 dark:text-gray-400">No submissions yet. Upload student files to get started.</p>
          </div>
        ) : (
          <div className="mt-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Student</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">File</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {submissions.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                    <td className="px-6 py-4 text-sm">
                      <Link to={`/submissions/${s.id}`}
                        className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium">
                        {s.student ? `${s.student.first_name} ${s.student.last_name}` : `Student #${s.student_id}`}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 truncate max-w-48">
                      {s.original_filename}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${statusColor[s.status] || ''}`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {s.final_score != null ? `${s.final_score}/${s.max_score}` : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      {s.status === 'uploaded' && (
                        <button onClick={() => handleGradeSingle(s.id)}
                          className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
                          Grade
                        </button>
                      )}
                      {(s.status === 'graded' || s.status === 'reviewed') && (
                        <>
                          <Link to={`/submissions/${s.id}`}
                            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
                            Review
                          </Link>
                          <button onClick={() => downloadReport(s.id)}
                            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
                            Report
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
