import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAssignment } from '../../api/assignments';
import { listSubmissions } from '../../api/submissions';
import {
  runPromptTest,
  getTestRun,
  getTestHistory,
  applyTestPrompts,
  deleteTestRun,
} from '../../api/playground';
import type { PromptTestRun, PromptTestResult } from '../../api/playground';
import type { Assignment, Submission } from '../../types';

type RunType = 'single' | 'sample' | 'comparison';

export default function PromptPlaygroundPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const id = Number(assignmentId);

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);

  // Mode & selection
  const [mode, setMode] = useState<RunType>('single');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [label, setLabel] = useState('');

  // Prompts
  const [codePrompt, setCodePrompt] = useState('');
  const [feedbackPrompt, setFeedbackPrompt] = useState('');
  const [codePromptB, setCodePromptB] = useState('');
  const [feedbackPromptB, setFeedbackPromptB] = useState('');

  // Test run state
  const [activeRun, setActiveRun] = useState<PromptTestRun | null>(null);
  const [running, setRunning] = useState(false);

  // History
  const [history, setHistory] = useState<PromptTestRun[]>([]);
  const [historyOpen, setHistoryOpen] = useState(false);

  // Expanded result details
  const [expandedSub, setExpandedSub] = useState<string | null>(null);
  const [expandedPrompt, setExpandedPrompt] = useState<string | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadData = useCallback(() => {
    Promise.all([getAssignment(id), listSubmissions(id)]).then(([a, s]) => {
      setAssignment(a);
      setSubmissions(s);
      setCodePrompt(a.code_analysis_prompt || '');
      setFeedbackPrompt(a.feedback_prompt || '');
      setCodePromptB(a.code_analysis_prompt || '');
      setFeedbackPromptB(a.feedback_prompt || '');
    }).finally(() => setLoading(false));
  }, [id]);

  const loadHistory = useCallback(() => {
    getTestHistory(id).then(setHistory);
  }, [id]);

  useEffect(() => { loadData(); loadHistory(); }, [loadData, loadHistory]);

  // Poll for completion
  useEffect(() => {
    if (!activeRun || activeRun.status === 'completed' || activeRun.status === 'error') {
      if (pollRef.current) clearInterval(pollRef.current);
      return;
    }
    pollRef.current = setInterval(async () => {
      const updated = await getTestRun(activeRun.id);
      setActiveRun(updated);
      if (updated.status === 'completed' || updated.status === 'error') {
        setRunning(false);
        loadHistory();
      }
    }, 2000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [activeRun, loadHistory]);

  const handleRunTest = async () => {
    if (!selectedIds.length) { alert('Select at least one submission'); return; }
    setRunning(true);
    setActiveRun(null);
    setExpandedSub(null);
    setExpandedPrompt(null);
    try {
      const { test_run, async_mode } = await runPromptTest({
        assignment_id: id,
        run_type: mode,
        submission_ids: selectedIds,
        label: label || undefined,
        code_analysis_prompt: codePrompt || undefined,
        feedback_prompt: feedbackPrompt || undefined,
        comparison_code_analysis_prompt: mode === 'comparison' ? codePromptB || undefined : undefined,
        comparison_feedback_prompt: mode === 'comparison' ? feedbackPromptB || undefined : undefined,
      });
      setActiveRun(test_run);
      if (!async_mode && (test_run.status === 'completed' || test_run.status === 'error')) {
        setRunning(false);
        loadHistory();
      }
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to start test');
      setRunning(false);
    }
  };

  const handleApply = async (version?: 'a' | 'b') => {
    if (!activeRun) return;
    if (!confirm(`Apply ${version === 'b' ? 'Version B' : 'Version A'} prompts to this assignment?`)) return;
    try {
      await applyTestPrompts(activeRun.id, version, assignment?.version);
      loadData();
      alert('Prompts applied successfully');
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to apply prompts');
    }
  };

  const handleLoadRun = (run: PromptTestRun) => {
    setActiveRun(run);
    setMode(run.run_type);
    setCodePrompt(run.code_analysis_prompt || '');
    setFeedbackPrompt(run.feedback_prompt || '');
    setCodePromptB(run.comparison_code_analysis_prompt || '');
    setFeedbackPromptB(run.comparison_feedback_prompt || '');
    setSelectedIds(run.submission_ids || []);
    setLabel(run.label || '');
    setRunning(false);
  };

  const handleDeleteRun = async (runId: number) => {
    if (!confirm('Delete this test run?')) return;
    await deleteTestRun(runId);
    if (activeRun?.id === runId) setActiveRun(null);
    loadHistory();
  };

  const handleResetPrompts = () => {
    setCodePrompt(assignment?.code_analysis_prompt || '');
    setFeedbackPrompt(assignment?.feedback_prompt || '');
    setCodePromptB(assignment?.code_analysis_prompt || '');
    setFeedbackPromptB(assignment?.feedback_prompt || '');
  };

  const toggleSubmission = (subId: number) => {
    setSelectedIds((prev) =>
      prev.includes(subId) ? prev.filter((x) => x !== subId) : [...prev, subId]
    );
  };

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Loading...</p>;
  if (!assignment) return <p className="text-red-500">Assignment not found</p>;

  // Extract results for display
  const isComparison = activeRun?.run_type === 'comparison';
  const resultsA: Record<string, PromptTestResult> = isComparison
    ? (activeRun?.results as any)?.version_a || {}
    : (activeRun?.results as Record<string, PromptTestResult>) || {};
  const resultsB: Record<string, PromptTestResult> = isComparison
    ? (activeRun?.results as any)?.version_b || {}
    : {};
  const statsA = isComparison
    ? (activeRun?.grading_stats as any)?.version_a
    : activeRun?.grading_stats;
  const statsB = isComparison ? (activeRun?.grading_stats as any)?.version_b : null;

  const gradedSubs = submissions.filter((s) => s.status !== 'error');

  return (
    <div className="max-w-7xl mx-auto">
      <Link to={`/assignments/${id}`} className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Back to assignment
      </Link>

      <div className="mt-2 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Prompt Playground</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">{assignment.name}</p>
        </div>
        <button
          onClick={() => setHistoryOpen(!historyOpen)}
          className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          History ({history.length})
        </button>
      </div>

      {/* History sidebar */}
      {historyOpen && (
        <div className="mt-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 max-h-64 overflow-y-auto">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Test Run History</h3>
          {history.length === 0 ? (
            <p className="text-xs text-gray-400">No test runs yet</p>
          ) : (
            <div className="space-y-2">
              {history.map((run) => (
                <div key={run.id} className="flex items-center justify-between text-xs border-b border-gray-100 dark:border-gray-700 pb-2">
                  <button onClick={() => handleLoadRun(run)} className="text-left hover:text-indigo-600 dark:hover:text-indigo-400">
                    <span className="font-medium">{run.label || `Run #${run.id}`}</span>
                    <span className="ml-2 text-gray-400">{run.run_type}</span>
                    <span className={`ml-2 ${run.status === 'completed' ? 'text-green-600 dark:text-green-400' : run.status === 'error' ? 'text-red-600 dark:text-red-400' : 'text-yellow-600 dark:text-yellow-400'}`}>
                      {run.status}
                    </span>
                    {run.total_duration_seconds && (
                      <span className="ml-2 text-gray-400">{run.total_duration_seconds}s</span>
                    )}
                  </button>
                  <button onClick={() => handleDeleteRun(run.id)} className="text-red-400 hover:text-red-600 ml-2">x</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Mode + Submissions + Prompts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Mode selector */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Test Mode</h3>
            <div className="flex space-x-2">
              {(['single', 'sample', 'comparison'] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => { setMode(m); setSelectedIds([]); }}
                  className={`px-4 py-2 text-sm rounded-md ${
                    mode === m
                      ? 'bg-amber-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {m === 'single' ? 'Single' : m === 'sample' ? 'Sample Set' : 'Comparison'}
                </button>
              ))}
            </div>

            {/* Label */}
            <div className="mt-3">
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Optional label (e.g. 'v3 strict rubric')"
                className="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Submission picker */}
            <div className="mt-3">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {mode === 'single' ? 'Select one submission:' : `Select ${mode === 'sample' ? '3-5' : '1+'} submissions:`}
              </p>
              <div className="max-h-40 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded">
                {gradedSubs.map((sub) => {
                  const checked = selectedIds.includes(sub.id);
                  const isRadio = mode === 'single';
                  return (
                    <label key={sub.id} className={`flex items-center px-3 py-1.5 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer ${
                      checked ? 'bg-amber-50 dark:bg-amber-900/20' : ''
                    }`}>
                      <input
                        type={isRadio ? 'radio' : 'checkbox'}
                        name="submission"
                        checked={checked}
                        onChange={() => {
                          if (isRadio) setSelectedIds([sub.id]);
                          else toggleSubmission(sub.id);
                        }}
                        className="mr-2"
                      />
                      <span className="text-gray-700 dark:text-gray-300">
                        {sub.student ? `${sub.student.first_name} ${sub.student.last_name}` : `#${sub.student_id}`}
                      </span>
                      {sub.final_score != null && (
                        <span className="ml-auto text-xs text-gray-400">{sub.final_score}/{sub.max_score}</span>
                      )}
                    </label>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Prompt editors */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                {mode === 'comparison' ? 'Version A Prompts' : 'Prompts'}
              </h3>
              <button onClick={handleResetPrompts} className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                Reset to Saved
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Code Analysis Prompt</label>
                <textarea
                  value={codePrompt}
                  onChange={(e) => setCodePrompt(e.target.value)}
                  rows={5}
                  placeholder="Leave blank for default..."
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Feedback Prompt</label>
                <textarea
                  value={feedbackPrompt}
                  onChange={(e) => setFeedbackPrompt(e.target.value)}
                  rows={5}
                  placeholder="Leave blank for default..."
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono"
                />
              </div>
            </div>
          </div>

          {/* Version B prompts (comparison only) */}
          {mode === 'comparison' && (
            <div className="bg-white dark:bg-gray-800 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-blue-700 dark:text-blue-300 mb-3">Version B Prompts</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Code Analysis Prompt (B)</label>
                  <textarea
                    value={codePromptB}
                    onChange={(e) => setCodePromptB(e.target.value)}
                    rows={5}
                    placeholder="Leave blank for default..."
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Feedback Prompt (B)</label>
                  <textarea
                    value={feedbackPromptB}
                    onChange={(e) => setFeedbackPromptB(e.target.value)}
                    rows={5}
                    placeholder="Leave blank for default..."
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Run button */}
          <button
            onClick={handleRunTest}
            disabled={running || !selectedIds.length}
            className="w-full px-4 py-3 bg-amber-600 text-white text-sm font-medium rounded-md hover:bg-amber-700 disabled:opacity-50"
          >
            {running ? 'Running test...' : 'Run Test'}
          </button>
        </div>

        {/* Right column: Results */}
        <div className="space-y-6">
          {/* Status */}
          {activeRun && (
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {activeRun.label || `Test #${activeRun.id}`}
                </h3>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  activeRun.status === 'completed' ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' :
                  activeRun.status === 'error' ? 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300' :
                  'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300'
                }`}>
                  {activeRun.status}
                </span>
              </div>

              {activeRun.status === 'running' && (
                <div className="animate-pulse bg-amber-200 dark:bg-amber-800 rounded-full h-2" />
              )}

              {activeRun.error_message && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-2">{activeRun.error_message}</p>
              )}

              {activeRun.total_duration_seconds && (
                <p className="text-xs text-gray-400 mt-1">Duration: {activeRun.total_duration_seconds}s</p>
              )}

              {/* Stats summary */}
              {statsA && (
                <div className="mt-3 text-xs">
                  <p className="font-medium text-gray-600 dark:text-gray-400">
                    {isComparison ? 'Version A: ' : ''}
                    {statsA.successful}/{statsA.total} graded
                    {statsA.avg_score != null && ` | avg: ${statsA.avg_score}`}
                    {statsA.min_score != null && ` | range: ${statsA.min_score}-${statsA.max_score}`}
                  </p>
                  {statsB && (
                    <p className="font-medium text-blue-600 dark:text-blue-400 mt-1">
                      Version B: {statsB.successful}/{statsB.total} graded
                      {statsB.avg_score != null && ` | avg: ${statsB.avg_score}`}
                      {statsB.min_score != null && ` | range: ${statsB.min_score}-${statsB.max_score}`}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Results list */}
          {activeRun?.status === 'completed' && (
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Results</h3>
              <div className="space-y-3">
                {Object.entries(resultsA).map(([subId, result]) => {
                  const resultB = resultsB[subId];
                  const isExpanded = expandedSub === subId;
                  const showPrompt = expandedPrompt === subId;

                  return (
                    <div key={subId} className="border border-gray-100 dark:border-gray-700 rounded p-3">
                      <button
                        onClick={() => setExpandedSub(isExpanded ? null : subId)}
                        className="w-full flex items-center justify-between text-left text-sm"
                      >
                        <span className="font-medium text-gray-700 dark:text-gray-300">{result.student_name}</span>
                        <div className="flex items-center space-x-2">
                          {result.error ? (
                            <span className="text-red-500 text-xs">Error</span>
                          ) : (
                            <>
                              <span className="text-gray-600 dark:text-gray-400">
                                {result.score}/{result.max_points}
                              </span>
                              {isComparison && resultB && !resultB.error && (
                                <span className={`text-xs ${
                                  (resultB.score || 0) > (result.score || 0) ? 'text-green-600 dark:text-green-400' :
                                  (resultB.score || 0) < (result.score || 0) ? 'text-red-600 dark:text-red-400' :
                                  'text-gray-400'
                                }`}>
                                  B: {resultB.score}/{resultB.max_points}
                                </span>
                              )}
                            </>
                          )}
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="mt-3 space-y-2">
                          {result.error && <p className="text-xs text-red-500">{result.error}</p>}

                          {result.feedback && (
                            <div className="text-xs">
                              {/* Key feedback points */}
                              {(result.feedback as any)?.comprehensive_feedback?.instructor_comments && (
                                <p className="text-gray-600 dark:text-gray-400 mt-1">
                                  <span className="font-medium">Comments:</span>{' '}
                                  {String((result.feedback as any).comprehensive_feedback.instructor_comments).slice(0, 300)}
                                </p>
                              )}
                              {(result.feedback as any)?.technical_analysis?.code_strengths?.length > 0 && (
                                <div className="mt-1">
                                  <span className="font-medium text-green-600 dark:text-green-400">Strengths:</span>
                                  <ul className="ml-3 list-disc text-gray-600 dark:text-gray-400">
                                    {(result.feedback as any).technical_analysis.code_strengths.slice(0, 3).map((s: string, i: number) => (
                                      <li key={i}>{s.slice(0, 150)}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {(result.feedback as any)?.technical_analysis?.code_suggestions?.length > 0 && (
                                <div className="mt-1">
                                  <span className="font-medium text-amber-600 dark:text-amber-400">Suggestions:</span>
                                  <ul className="ml-3 list-disc text-gray-600 dark:text-gray-400">
                                    {(result.feedback as any).technical_analysis.code_suggestions.slice(0, 3).map((s: string, i: number) => (
                                      <li key={i}>{s.slice(0, 150)}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Raw prompt toggle */}
                          {result.raw_prompts && (
                            <div>
                              <button
                                onClick={() => setExpandedPrompt(showPrompt ? null : subId)}
                                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                              >
                                {showPrompt ? 'Hide raw prompts' : 'Show raw prompts'}
                              </button>
                              {showPrompt && (
                                <div className="mt-2 space-y-2">
                                  {result.raw_prompts.code_analysis && (
                                    <div>
                                      <p className="text-xs font-medium text-gray-500">Code Analysis Prompt:</p>
                                      <pre className="mt-1 text-xs bg-gray-50 dark:bg-gray-900 p-2 rounded overflow-x-auto max-h-48 whitespace-pre-wrap text-gray-600 dark:text-gray-400">
                                        {result.raw_prompts.code_analysis}
                                      </pre>
                                    </div>
                                  )}
                                  {result.raw_prompts.feedback && (
                                    <div>
                                      <p className="text-xs font-medium text-gray-500">Feedback Prompt:</p>
                                      <pre className="mt-1 text-xs bg-gray-50 dark:bg-gray-900 p-2 rounded overflow-x-auto max-h-48 whitespace-pre-wrap text-gray-600 dark:text-gray-400">
                                        {result.raw_prompts.feedback}
                                      </pre>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}

                          {/* Comparison Version B result */}
                          {isComparison && resultB && (
                            <div className="mt-2 pt-2 border-t border-blue-100 dark:border-blue-800">
                              <p className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1">Version B</p>
                              {resultB.error ? (
                                <p className="text-xs text-red-500">{resultB.error}</p>
                              ) : (
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                  Score: {resultB.score}/{resultB.max_points}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Apply buttons */}
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => handleApply('a')}
                  className="px-3 py-1.5 text-xs bg-amber-600 text-white rounded-md hover:bg-amber-700"
                >
                  Apply {isComparison ? 'Version A' : 'These Prompts'}
                </button>
                {isComparison && (
                  <button
                    onClick={() => handleApply('b')}
                    className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Apply Version B
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
