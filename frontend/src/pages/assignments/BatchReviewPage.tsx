import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getReviewQueue, submitReview, previewReport } from '../../api/submissions';
import type { Submission, AIFeedback, Assignment } from '../../types';
import FeedbackEditor from '../../components/feedback/FeedbackEditor';

function scoreColor(score: number | null | undefined, max: number): string {
  if (score == null) return 'text-gray-400 dark:text-gray-500';
  const pct = max > 0 ? (score / max) * 100 : 0;
  if (pct >= 90) return 'text-green-600 dark:text-green-400';
  if (pct >= 75) return 'text-blue-600 dark:text-blue-400';
  if (pct >= 60) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-red-600 dark:text-red-400';
}

export default function BatchReviewPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const id = Number(assignmentId);

  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await getReviewQueue(id);
      setSubmissions(data.submissions);
      setAssignment(data.assignment);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (editing) return; // Don't capture keys while editing
      if (e.key === 'j' || e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIdx((i) => Math.min(i + 1, submissions.length - 1));
      } else if (e.key === 'k' || e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIdx((i) => Math.max(i - 1, 0));
      } else if (e.key === 'e') {
        e.preventDefault();
        setEditing(true);
      } else if (e.key === 'n') {
        e.preventDefault();
        goNextUnreviewed();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [submissions, editing]);

  // Scroll selected item into view
  useEffect(() => {
    const el = listRef.current?.querySelector(`[data-idx="${selectedIdx}"]`);
    el?.scrollIntoView({ block: 'nearest' });
  }, [selectedIdx]);

  const selected = submissions[selectedIdx] || null;
  const maxScore = assignment?.total_points || selected?.max_score || 100;

  const goNextUnreviewed = () => {
    const idx = submissions.findIndex((s, i) => i > selectedIdx && s.status !== 'reviewed');
    if (idx >= 0) setSelectedIdx(idx);
  };

  const handleSaveFeedback = async (feedback: AIFeedback) => {
    if (!selected) return;
    setSaving(true);
    setSaved(false);
    try {
      const updated = await submitReview(selected.id, {
        edited_feedback: feedback,
        human_score: feedback.final_score,
      });
      setSubmissions((prev) => prev.map((s) => (s.id === updated.id ? updated : s)));
      setEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      const updated = await submitReview(selected.id, {
        human_score: selected.final_score ?? selected.ai_score ?? undefined,
      });
      setSubmissions((prev) => prev.map((s) => (s.id === updated.id ? updated : s)));
      goNextUnreviewed();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to approve');
    } finally {
      setSaving(false);
    }
  };

  const handlePreview = async () => {
    if (!selected) return;
    setPreviewing(true);
    try {
      const blob = await previewReport(selected.id);
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to preview');
    } finally {
      setPreviewing(false);
    }
  };

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Loading...</p>;
  if (!assignment) return <p className="text-red-500">Assignment not found</p>;

  const reviewed = submissions.filter((s) => s.status === 'reviewed').length;
  const total = submissions.length;

  const aiFeedback = (selected?.ai_feedback || null) as AIFeedback | null;
  const editedFeedback = (selected?.edited_feedback || null) as AIFeedback | null;

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shrink-0">
        <div className="flex items-center gap-4">
          <Link
            to={`/assignments/${id}`}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          >
            Back to {assignment.name}
          </Link>
          <span className="text-sm text-gray-400 dark:text-gray-500">
            {reviewed}/{total} reviewed
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
          <kbd className="px-1.5 py-0.5 rounded border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">j/k</kbd> navigate
          <kbd className="px-1.5 py-0.5 rounded border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">e</kbd> edit
          <kbd className="px-1.5 py-0.5 rounded border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">n</kbd> next unreviewed
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div ref={listRef} className="w-72 shrink-0 border-r border-gray-200 dark:border-gray-700 overflow-y-auto bg-white dark:bg-gray-800">
          {submissions.map((s, idx) => {
            const name = s.student
              ? `${s.student.last_name}, ${s.student.first_name}`
              : `Student #${s.student_id}`;
            const isSelected = idx === selectedIdx;
            return (
              <button
                key={s.id}
                data-idx={idx}
                onClick={() => { setSelectedIdx(idx); setEditing(false); }}
                className={`w-full text-left px-4 py-3 border-b border-gray-100 dark:border-gray-700 transition-colors ${
                  isSelected
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 border-l-2 border-l-indigo-500'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/30 border-l-2 border-l-transparent'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{name}</span>
                  <span className={`text-sm font-bold ${scoreColor(s.final_score, maxScore)}`}>
                    {s.final_score != null ? s.final_score : '-'}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    s.status === 'reviewed'
                      ? 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300'
                      : 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
                  }`}>
                    {s.status}
                  </span>
                  {s.edited_feedback && (
                    <span className="text-xs text-purple-500 dark:text-purple-400">edited</span>
                  )}
                </div>
              </button>
            );
          })}
          {submissions.length === 0 && (
            <p className="p-4 text-sm text-gray-400 dark:text-gray-500">No graded submissions to review.</p>
          )}
        </div>

        {/* Detail panel */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900">
          {selected ? (
            <div className="max-w-3xl">
              {/* Student header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    {selected.student
                      ? `${selected.student.first_name} ${selected.student.last_name}`
                      : `Student #${selected.student_id}`}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{selected.original_filename}</p>
                </div>
                <div className="flex items-center gap-2">
                  {saved && <span className="text-sm text-green-600 dark:text-green-400">Saved</span>}
                  {!editing && (
                    <>
                      <button
                        onClick={() => setEditing(true)}
                        className="px-3 py-1.5 text-sm font-medium rounded-md bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-200 dark:hover:bg-indigo-900/60"
                      >
                        Edit
                      </button>
                      <button
                        onClick={handleApprove}
                        disabled={saving || selected.status === 'reviewed'}
                        className="px-3 py-1.5 text-sm font-medium rounded-md bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
                      >
                        {selected.status === 'reviewed' ? 'Approved' : 'Approve'}
                      </button>
                      <button
                        onClick={handlePreview}
                        disabled={previewing}
                        className="px-3 py-1.5 text-sm font-medium rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
                      >
                        {previewing ? 'Loading...' : 'Preview PDF'}
                      </button>
                    </>
                  )}
                  {editing && (
                    <button
                      onClick={() => setEditing(false)}
                      className="px-3 py-1.5 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>

              {/* Feedback editor */}
              {(aiFeedback || editedFeedback) ? (
                <FeedbackEditor
                  key={selected.id}
                  aiFeedback={aiFeedback}
                  editedFeedback={editedFeedback}
                  editing={editing}
                  onSave={handleSaveFeedback}
                  maxScore={maxScore}
                />
              ) : (
                <p className="text-gray-400 dark:text-gray-500">No AI feedback available for this submission.</p>
              )}

              {saving && (
                <p className="mt-4 text-sm text-gray-400 dark:text-gray-500">Saving...</p>
              )}
            </div>
          ) : (
            <p className="text-gray-400 dark:text-gray-500">Select a submission from the sidebar.</p>
          )}
        </div>
      </div>
    </div>
  );
}
