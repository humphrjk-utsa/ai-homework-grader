import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSubmission, submitReview, previewReport, generateReport } from '../../api/submissions';
import type { Submission, AIFeedback } from '../../types';
import FeedbackEditor from '../../components/feedback/FeedbackEditor';

const statusColor: Record<string, string> = {
  uploaded: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  queued: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
  grading: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  graded: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
  reviewed: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
  error: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
};

export default function SubmissionDetailPage() {
  const { submissionId } = useParams<{ submissionId: string }>();
  const id = Number(submissionId);

  const [submission, setSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [savingReview, setSavingReview] = useState(false);
  const [reviewSaved, setReviewSaved] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [analysisOpen, setAnalysisOpen] = useState(true);
  const [validationOpen, setValidationOpen] = useState(false);

  const refresh = useCallback(() => {
    getSubmission(id)
      .then((s) => setSubmission(s))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  const maxScore = submission?.max_score || submission?.assignment?.total_points || 100;

  const handleSaveFeedback = async (feedback: AIFeedback) => {
    setSavingReview(true);
    setReviewSaved(false);
    try {
      const updated = await submitReview(id, {
        edited_feedback: feedback,
        human_score: feedback.final_score,
      });
      setSubmission(updated);
      setEditing(false);
      setReviewSaved(true);
      setTimeout(() => setReviewSaved(false), 3000);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to save review');
    } finally {
      setSavingReview(false);
    }
  };

  const handlePreviewReport = async () => {
    setPreviewing(true);
    try {
      const blob = await previewReport(id);
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to generate preview');
    } finally {
      setPreviewing(false);
    }
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const report = await generateReport(id);
      if (report?.id) {
        window.open(`/api/reports/${report.id}/download`, '_blank');
      }
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to generate report');
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Loading...</p>;
  if (!submission) return <p className="text-red-500">Submission not found</p>;

  const studentName = submission.student
    ? `${submission.student.first_name} ${submission.student.last_name}`
    : `Student #${submission.student_id}`;
  const assignmentName = submission.assignment?.name || `Assignment #${submission.assignment_id}`;
  const componentScores = (submission.component_scores || {}) as Record<string, { score: number; max: number; evidence?: string }>;
  const aiFeedback = (submission.ai_feedback || null) as AIFeedback | null;
  const editedFeedback = (submission.edited_feedback || null) as AIFeedback | null;
  const validationResults = (submission.validation_results || {}) as Record<string, unknown>;
  const hasFeedback = aiFeedback || editedFeedback;
  const isGraded = submission.status === 'graded' || submission.status === 'reviewed';

  return (
    <div className="max-w-4xl">
      {/* Navigation */}
      <Link
        to={`/assignments/${submission.assignment_id}`}
        className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
      >
        Back to {assignmentName}
      </Link>

      {/* Header */}
      <div className="mt-2 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{studentName}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {submission.original_filename}
            <span className="mx-2">-</span>
            <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${statusColor[submission.status] || ''}`}>
              {submission.status}
            </span>
            {editedFeedback && (
              <span className="ml-2 inline-flex px-2 py-0.5 rounded text-xs font-medium bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300">
                edited
              </span>
            )}
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {submission.final_score != null ? submission.final_score : '-'}
            <span className="text-lg text-gray-400 dark:text-gray-500">/{maxScore}</span>
          </p>
          {submission.ai_score != null && submission.human_score != null && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              AI: {submission.ai_score} | Override: {submission.human_score}
            </p>
          )}
        </div>
      </div>

      {/* Component Scores */}
      {Object.keys(componentScores).length > 0 && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Component Scores</h2>
          <div className="mt-4 space-y-3">
            {Object.entries(componentScores).map(([key, val]) => {
              const pct = val.max > 0 ? (val.score / val.max) * 100 : 0;
              const color = pct >= 90 ? 'bg-green-500' : pct >= 75 ? 'bg-blue-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-red-500';
              return (
                <div key={key}>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="text-gray-500 dark:text-gray-400 font-medium">{val.score}/{val.max}</span>
                  </div>
                  <div className="mt-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                    <div className={`${color} rounded-full h-2.5 transition-all`} style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  {val.evidence && (
                    <p className="mt-1 text-xs text-gray-400 dark:text-gray-500 line-clamp-2">{val.evidence}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AI Feedback */}
      {hasFeedback && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setAnalysisOpen(!analysisOpen)}
            className="w-full flex items-center justify-between p-6 text-left"
          >
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                {editedFeedback ? 'Edited Feedback' : 'AI Analysis'}
              </h2>
              {isGraded && !editing && (
                <button
                  onClick={(e) => { e.stopPropagation(); setEditing(true); }}
                  className="px-3 py-1 text-xs font-medium rounded-md bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-200 dark:hover:bg-indigo-900/60"
                  title="Edit this feedback to refine the AI's grading for future submissions"
                >
                  Edit Feedback
                </button>
              )}
              {editing && (
                <button
                  onClick={(e) => { e.stopPropagation(); setEditing(false); }}
                  className="px-3 py-1 text-xs font-medium rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
              )}
              {reviewSaved && (
                <span className="text-xs text-green-600 dark:text-green-400">Saved — your edits will help improve future AI grading</span>
              )}
            </div>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${analysisOpen ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          {analysisOpen && (
            <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 pt-4">
              {savingReview && (
                <p className="text-sm text-gray-400 dark:text-gray-500 mb-3">Saving...</p>
              )}
              <FeedbackEditor
                aiFeedback={aiFeedback}
                editedFeedback={editedFeedback}
                editing={editing}
                onSave={handleSaveFeedback}
                maxScore={maxScore}
              />
            </div>
          )}
        </div>
      )}

      {/* Validation Results */}
      {validationResults && Object.keys(validationResults).length > 0 && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setValidationOpen(!validationOpen)}
            className="w-full flex items-center justify-between p-6 text-left"
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Validation Results</h2>
            <svg className={`w-5 h-5 text-gray-400 transition-transform ${validationOpen ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          {validationOpen && (
            <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 pt-4">
              <pre className="text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-900/30 p-3 rounded overflow-x-auto max-h-96">
                {JSON.stringify(validationResults, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Error message */}
      {submission.status === 'error' && submission.error_message && (
        <div className="mt-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-700 dark:text-red-400">Grading Error</h3>
          <p className="mt-1 text-sm text-red-600 dark:text-red-300">{submission.error_message}</p>
        </div>
      )}

      {/* Actions */}
      <div className="mt-6 flex items-center gap-3 pb-8">
        <a
          href={`/api/submissions/${id}/download`}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600"
        >
          Download Original
        </a>
        {isGraded && (
          <>
            <button
              onClick={handlePreviewReport}
              disabled={previewing}
              className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
            >
              {previewing ? 'Generating...' : 'Preview Report'}
            </button>
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {generatingReport ? 'Generating...' : 'Generate & Download Report'}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
