import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getAssignment } from '../../api/assignments';
import {
  uploadGroundTruth,
  uploadBatchDocs,
  commitGroundTruth,
} from '../../api/groundTruth';
import type { GroundTruthEntry, GroundTruthUploadResult, CommitEntry } from '../../api/groundTruth';
import type { Assignment, AIFeedback } from '../../types';
import FeedbackEditor from '../../components/feedback/FeedbackEditor';

type Step = 'upload' | 'preview' | 'review';
type UploadMode = 'csv' | 'docs';

export default function GroundTruthUploadPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const id = Number(assignmentId);
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [step, setStep] = useState<Step>('upload');
  const [mode, setMode] = useState<UploadMode>('csv');
  const [uploading, setUploading] = useState(false);
  const [entries, setEntries] = useState<GroundTruthEntry[]>([]);
  const [singleResults, setSingleResults] = useState<GroundTruthUploadResult[]>([]);
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [committing, setCommitting] = useState(false);
  const [commitResult, setCommitResult] = useState<{ committed: number; skipped: number; errors: string[] } | null>(null);

  useEffect(() => {
    getAssignment(id).then(setAssignment);
  }, [id]);

  const handleUpload = async (files: FileList) => {
    setUploading(true);
    try {
      if (mode === 'csv') {
        const results = await uploadGroundTruth(id, files);
        // Flatten batch entries from all CSV files
        const allEntries: GroundTruthEntry[] = [];
        for (const r of results) {
          if (r.error) {
            alert(`Error processing ${r.filename}: ${r.error}`);
            continue;
          }
          if (r.entries) allEntries.push(...r.entries);
        }
        setEntries(allEntries);
        if (allEntries.length > 0) setStep('preview');
      } else {
        const results = await uploadBatchDocs(id, files);
        setSingleResults(results);
        // Convert single-mode results to entries for preview
        const allEntries: GroundTruthEntry[] = results
          .filter((r) => !r.error)
          .map((r) => ({
            filename: r.filename,
            student_name: r.parsed_name || r.filename,
            converted_feedback: r.converted_feedback,
            matched_student: r.matched_student ?? null,
            existing_submission_id: r.existing_submission_id ?? null,
            score: r.converted_feedback?.final_score ?? null,
          }));
        setEntries(allEntries);
        const errors = results.filter((r) => r.error);
        if (errors.length > 0) {
          alert(`${errors.length} file(s) had errors:\n${errors.map((e) => `${e.filename}: ${e.error}`).join('\n')}`);
        }
        if (allEntries.length > 0) setStep('preview');
      }
    } catch (err: any) {
      alert(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleCommit = async () => {
    setCommitting(true);
    try {
      const toCommit: CommitEntry[] = entries
        .filter((e) => e.matched_student && e.converted_feedback)
        .map((e) => ({
          student_id: e.matched_student!.id,
          score: e.score ?? e.converted_feedback?.final_score ?? null,
          edited_feedback: e.converted_feedback!,
        }));
      const result = await commitGroundTruth(id, toCommit);
      setCommitResult(result);
      setStep('upload');
    } catch (err: any) {
      alert(err.response?.data?.error || 'Commit failed');
    } finally {
      setCommitting(false);
    }
  };

  const updateEntryFeedback = (idx: number, feedback: AIFeedback) => {
    setEntries((prev) => prev.map((e, i) => (i === idx ? { ...e, converted_feedback: feedback } : e)));
    setEditingIdx(null);
  };

  if (!assignment) return <p className="text-gray-400">Loading...</p>;

  const inputCls = 'mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm';

  return (
    <div>
      <div className="mb-4">
        <Link to={`/assignments/${id}`} className="text-indigo-600 dark:text-indigo-400 text-sm hover:underline">
          &larr; Back to {assignment.name}
        </Link>
      </div>

      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Import Existing Grades</h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Already graded this assignment by hand? Import your scores and feedback here.
      </p>

      <div className="mb-6 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
        <p className="text-sm font-medium text-indigo-700 dark:text-indigo-300 mb-2">How this works</p>
        <ol className="text-sm text-indigo-600 dark:text-indigo-400 space-y-1 list-decimal list-inside">
          <li>Upload a CSV grade sheet or annotated Word/PDF files from your previous grading</li>
          <li>The system extracts scores and feedback, then matches them to enrolled students</li>
          <li>Review and edit the imported feedback — your edits become examples the AI learns from</li>
          <li>When you grade future submissions, the AI references your past feedback to match your style</li>
        </ol>
      </div>

      {commitResult && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <p className="text-green-700 dark:text-green-300 font-medium">
            Committed {commitResult.committed} entries ({commitResult.skipped} skipped)
          </p>
          {commitResult.errors.length > 0 && (
            <p className="text-red-600 text-sm mt-1">{commitResult.errors.join(', ')}</p>
          )}
        </div>
      )}

      {/* Step indicators */}
      <div className="flex space-x-4 mb-6">
        {(['upload', 'preview', 'review'] as Step[]).map((s, i) => (
          <div key={s} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step === s ? 'bg-indigo-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
            }`}>
              {i + 1}
            </div>
            <span className={`ml-2 text-sm ${step === s ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-400'}`}>
              {s === 'upload' ? 'Upload' : s === 'preview' ? 'Preview & Match' : 'Review & Commit'}
            </span>
          </div>
        ))}
      </div>

      {/* Step 1: Upload */}
      {step === 'upload' && (
        <div className="space-y-4">
          {/* Mode selector */}
          <div className="flex space-x-4">
            <button
              onClick={() => setMode('csv')}
              className={`px-4 py-3 rounded-lg border text-sm font-medium ${
                mode === 'csv'
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              CSV Score Sheet
              <p className="text-xs font-normal mt-1">Upload a CSV/XLSX with student scores and feedback</p>
            </button>
            <button
              onClick={() => setMode('docs')}
              className={`px-4 py-3 rounded-lg border text-sm font-medium ${
                mode === 'docs'
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              Graded Documents
              <p className="text-xs font-normal mt-1">Upload Word docs with comments or annotated PDFs</p>
            </button>
          </div>

          {/* File input */}
          <div className="p-8 bg-white dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 text-center">
            <input
              type="file"
              accept={mode === 'csv' ? '.csv,.xlsx' : '.docx,.pdf'}
              multiple={mode === 'docs'}
              onChange={(e) => e.target.files && handleUpload(e.target.files)}
              className="hidden"
              id="gt-file-input"
            />
            <label htmlFor="gt-file-input" className="cursor-pointer">
              <p className="text-gray-500 dark:text-gray-400">
                {uploading ? 'Processing...' : `Click to select ${mode === 'csv' ? 'CSV/XLSX file' : 'Word/PDF files'}`}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {mode === 'csv'
                  ? 'Expected columns: student_name, score, feedback (+ optional component score columns)'
                  : 'One file per student. Uses Canvas filename format for matching.'}
              </p>
            </label>
          </div>
        </div>
      )}

      {/* Step 2: Preview & Match */}
      {step === 'preview' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {entries.filter((e) => e.matched_student).length}/{entries.length} entries matched to students
            </p>
            <div className="flex gap-2">
              <button onClick={() => setStep('upload')} className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                Back
              </button>
              <button
                onClick={() => setStep('review')}
                disabled={entries.filter((e) => e.matched_student).length === 0}
                className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                Continue to Review
              </button>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Source</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Matched To</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Method</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Score</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Feedback</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {entries.map((e, i) => (
                  <tr key={i} className={e.matched_student ? '' : 'bg-red-50 dark:bg-red-900/10'}>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                      {e.student_name || e.filename || `Entry ${i + 1}`}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {e.matched_student ? (
                        <span className="text-green-600 dark:text-green-400">
                          {e.matched_student.first_name} {e.matched_student.last_name}
                        </span>
                      ) : (
                        <span className="text-red-500">Unmatched</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">
                      {e.match_method || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-right text-gray-500 dark:text-gray-400">
                      {e.score ?? e.converted_feedback?.final_score ?? '-'}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400 max-w-xs truncate">
                      {e.converted_feedback?.comprehensive_feedback?.instructor_comments?.slice(0, 100) ||
                       `${(e.converted_feedback?.technical_analysis?.code_suggestions?.length || 0) +
                          (e.converted_feedback?.comprehensive_feedback?.detailed_feedback?.analytical_strengths?.length || 0)} items`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Step 3: Review & Commit */}
      {step === 'review' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Review extracted feedback before committing
            </p>
            <div className="flex gap-2">
              <button onClick={() => setStep('preview')} className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                Back
              </button>
              <button
                onClick={handleCommit}
                disabled={committing}
                className="px-4 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {committing ? 'Committing...' : `Commit ${entries.filter((e) => e.matched_student).length} Entries`}
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {entries.filter((e) => e.matched_student).map((e, i) => {
              const realIdx = entries.indexOf(e);
              return (
                <div key={realIdx} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {e.matched_student!.first_name} {e.matched_student!.last_name}
                      </span>
                      <span className="ml-2 text-xs text-gray-400">
                        Score: {e.converted_feedback?.final_score ?? '-'}/{assignment.total_points}
                      </span>
                      {e.has_existing_feedback && (
                        <span className="ml-2 px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300">
                          Has existing feedback
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => setEditingIdx(editingIdx === realIdx ? null : realIdx)}
                      className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                    >
                      {editingIdx === realIdx ? 'Collapse' : 'Edit Feedback'}
                    </button>
                  </div>

                  {editingIdx === realIdx && e.converted_feedback && (
                    <FeedbackEditor
                      key={realIdx}
                      aiFeedback={null}
                      editedFeedback={e.converted_feedback}
                      editing={true}
                      onSave={(fb) => updateEntryFeedback(realIdx, fb)}
                      maxScore={assignment.total_points}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
