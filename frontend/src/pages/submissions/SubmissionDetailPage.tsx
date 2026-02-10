import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSubmission, submitReview, generateReport } from '../../api/submissions';
import type { Submission } from '../../types';

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
  const [reviewScore, setReviewScore] = useState('');
  const [reviewFeedback, setReviewFeedback] = useState('');
  const [savingReview, setSavingReview] = useState(false);
  const [reviewSaved, setReviewSaved] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [analysisOpen, setAnalysisOpen] = useState(true);
  const [validationOpen, setValidationOpen] = useState(false);

  const refresh = useCallback(() => {
    getSubmission(id).then((s) => {
      setSubmission(s);
      setReviewScore(s.human_score != null ? String(s.human_score) : (s.ai_score != null ? String(s.ai_score) : ''));
      setReviewFeedback(s.human_feedback || '');
    }).finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleSaveReview = async () => {
    setSavingReview(true);
    setReviewSaved(false);
    try {
      const updated = await submitReview(id, {
        human_score: reviewScore ? Number(reviewScore) : undefined,
        human_feedback: reviewFeedback || undefined,
      });
      setSubmission(updated);
      setReviewSaved(true);
      setTimeout(() => setReviewSaved(false), 3000);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to save review');
    } finally {
      setSavingReview(false);
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
  const aiFeedback = (submission.ai_feedback || {}) as Record<string, unknown>;
  const validationResults = (submission.validation_results || {}) as Record<string, unknown>;

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
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {submission.final_score != null ? submission.final_score : '-'}
            <span className="text-lg text-gray-400 dark:text-gray-500">/{submission.max_score || submission.assignment?.total_points || '?'}</span>
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

      {/* AI Analysis */}
      {aiFeedback && Object.keys(aiFeedback).length > 0 && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setAnalysisOpen(!analysisOpen)}
            className="w-full flex items-center justify-between p-6 text-left"
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Analysis</h2>
            <svg className={`w-5 h-5 text-gray-400 transition-transform ${analysisOpen ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          {analysisOpen && (
            <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 pt-4 space-y-4">
              {/* Strengths */}
              {Array.isArray(aiFeedback.strengths) && aiFeedback.strengths.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-green-700 dark:text-green-400">Strengths</h3>
                  <ul className="mt-1 list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                    {(aiFeedback.strengths as string[]).map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
              {/* Weaknesses / Areas for improvement */}
              {(Array.isArray(aiFeedback.weaknesses) || Array.isArray(aiFeedback.areas_for_improvement)) && (
                <div>
                  <h3 className="text-sm font-medium text-amber-700 dark:text-amber-400">Areas for Improvement</h3>
                  <ul className="mt-1 list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                    {((aiFeedback.weaknesses || aiFeedback.areas_for_improvement) as string[]).map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
              {/* Specific issues */}
              {Array.isArray(aiFeedback.specific_issues) && aiFeedback.specific_issues.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-red-700 dark:text-red-400">Specific Issues</h3>
                  <ul className="mt-1 list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                    {(aiFeedback.specific_issues as string[]).map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
              {/* Comprehensive feedback (text block) */}
              {typeof aiFeedback.comprehensive_feedback === 'string' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Comprehensive Feedback</h3>
                  <div className="mt-1 text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-900/30 p-3 rounded">
                    {aiFeedback.comprehensive_feedback}
                  </div>
                </div>
              )}
              {/* Technical analysis (text block) */}
              {typeof aiFeedback.technical_analysis === 'string' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Technical Analysis</h3>
                  <div className="mt-1 text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-900/30 p-3 rounded">
                    {aiFeedback.technical_analysis}
                  </div>
                </div>
              )}
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

      {/* Human Review Form */}
      {(submission.status === 'graded' || submission.status === 'reviewed') && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Human Review</h2>
          <div className="mt-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Override Score (0 - {submission.max_score || submission.assignment?.total_points || '?'})
              </label>
              <input
                type="number"
                min={0}
                max={submission.max_score || submission.assignment?.total_points || undefined}
                step={0.5}
                value={reviewScore}
                onChange={(e) => setReviewScore(e.target.value)}
                className="mt-1 block w-40 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Instructor Feedback
              </label>
              <textarea
                value={reviewFeedback}
                onChange={(e) => setReviewFeedback(e.target.value)}
                rows={4}
                placeholder="Add feedback for the student..."
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleSaveReview}
                disabled={savingReview}
                className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {savingReview ? 'Saving...' : 'Save Review'}
              </button>
              {reviewSaved && (
                <span className="text-sm text-green-600 dark:text-green-400">Saved</span>
              )}
            </div>
          </div>
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
        {(submission.status === 'graded' || submission.status === 'reviewed') && (
          <button
            onClick={handleGenerateReport}
            disabled={generatingReport}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {generatingReport ? 'Generating...' : 'Generate & Download Report'}
          </button>
        )}
      </div>
    </div>
  );
}
