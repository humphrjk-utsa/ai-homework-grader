import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getAssignment } from '../../api/assignments';
import { getRubricData, saveRubricData, generatePrompts } from '../../api/rubric';
import type { Assignment, RubricCategory } from '../../types';

const inputCls = 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500';

function emptyCategory(): RubricCategory {
  return {
    key: '',
    name: '',
    max_points: 0,
    description: '',
    criteria: { excellent: '', good: '', satisfactory: '', needs_improvement: '' },
  };
}

export default function RubricBuilderPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const navigate = useNavigate();
  const id = Number(assignmentId);

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [categories, setCategories] = useState<RubricCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([getAssignment(id), getRubricData(id)])
      .then(([a, r]) => {
        setAssignment(a);
        setCategories(r.categories.length > 0 ? r.categories : [emptyCategory()]);
      })
      .catch(() => setError('Failed to load assignment'))
      .finally(() => setLoading(false));
  }, [id]);

  const totalCatPoints = categories.reduce((s, c) => s + (Number(c.max_points) || 0), 0);
  const totalAssignment = assignment?.total_points ?? 0;
  const pointsMatch = Math.abs(totalCatPoints - totalAssignment) < 0.1;

  const updateCategory = (idx: number, patch: Partial<RubricCategory>) => {
    setCategories(cats => cats.map((c, i) => (i === idx ? { ...c, ...patch } : c)));
  };

  const updateCriteria = (idx: number, level: keyof RubricCategory['criteria'], value: string) => {
    setCategories(cats =>
      cats.map((c, i) =>
        i === idx ? { ...c, criteria: { ...c.criteria, [level]: value } } : c
      )
    );
  };

  const removeCategory = (idx: number) => {
    setCategories(cats => cats.filter((_, i) => i !== idx));
    if (expandedIdx === idx) setExpandedIdx(null);
  };

  const moveCategory = (idx: number, dir: -1 | 1) => {
    const newIdx = idx + dir;
    if (newIdx < 0 || newIdx >= categories.length) return;
    setCategories(cats => {
      const arr = [...cats];
      [arr[idx], arr[newIdx]] = [arr[newIdx], arr[idx]];
      return arr;
    });
    if (expandedIdx === idx) setExpandedIdx(newIdx);
  };

  const handleSave = async (andGenerate = false) => {
    setError('');
    setSaving(true);
    setSaved(false);
    try {
      const rubric = {
        assignment_info: {
          name: assignment!.slug,
          title: assignment!.name,
          total_points: totalAssignment,
        },
        categories,
      };
      await saveRubricData(id, rubric, assignment!.version);

      // Refresh assignment to get updated version
      const refreshed = await getAssignment(id);
      setAssignment(refreshed);

      if (andGenerate) {
        await generatePrompts(id);
        navigate(`/assignments/${id}`);
        return;
      }

      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('This assignment was modified by another user. Please reload and try again.');
        const refreshed = await getAssignment(id);
        setAssignment(refreshed);
      } else {
        const details = err.response?.data?.details;
        if (details) {
          setError(details.join('. '));
        } else {
          setError(err.response?.data?.error || 'Failed to save rubric');
        }
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Loading...</p>;
  if (!assignment) return <p className="text-red-500">Assignment not found</p>;

  return (
    <div className="max-w-3xl">
      <Link
        to={`/assignments/${id}`}
        className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
      >
        Back to assignment
      </Link>

      <div className="mt-2">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Rubric Builder</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {assignment.name} &middot; {totalAssignment} points
        </p>
      </div>

      {error && (
        <div className="mt-4 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-3 rounded text-sm">
          {error}
        </div>
      )}

      {/* Points validation bar */}
      <div className={`mt-4 flex items-center justify-between px-4 py-2 rounded-md text-sm font-medium ${
        pointsMatch
          ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400'
          : 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
      }`}>
        <span>Category points: {totalCatPoints} / {totalAssignment}</span>
        <span>{pointsMatch ? 'Points match' : 'Points do not match assignment total'}</span>
      </div>

      {/* Category cards */}
      <div className="mt-4 space-y-4">
        {categories.map((cat, idx) => {
          const weight = totalAssignment > 0 ? ((Number(cat.max_points) || 0) / totalAssignment * 100) : 0;
          const isExpanded = expandedIdx === idx;

          return (
            <div key={idx} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              {/* Category header row */}
              <div className="flex items-start gap-3">
                <div className="flex-1 grid grid-cols-[1fr_100px] gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                      Category Name
                    </label>
                    <input
                      type="text"
                      value={cat.name}
                      onChange={e => updateCategory(idx, { name: e.target.value })}
                      placeholder="e.g. Technical Execution"
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                      Points <span className="text-gray-400">({weight.toFixed(0)}%)</span>
                    </label>
                    <input
                      type="number"
                      min={0}
                      step={0.5}
                      value={cat.max_points || ''}
                      onChange={e => updateCategory(idx, { max_points: Number(e.target.value) || 0 })}
                      className={inputCls}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-1 pt-5">
                  <button onClick={() => moveCategory(idx, -1)} disabled={idx === 0}
                    className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-30"
                    title="Move up">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
                    </svg>
                  </button>
                  <button onClick={() => moveCategory(idx, 1)} disabled={idx === categories.length - 1}
                    className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-30"
                    title="Move down">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                    </svg>
                  </button>
                  <button onClick={() => removeCategory(idx)}
                    className="p-1 text-red-400 hover:text-red-600 dark:hover:text-red-300"
                    title="Remove category">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Description */}
              <div className="mt-3">
                <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                  Description
                </label>
                <textarea
                  value={cat.description}
                  onChange={e => updateCategory(idx, { description: e.target.value })}
                  rows={2}
                  placeholder="What does this category assess?"
                  className={inputCls}
                />
              </div>

              {/* Scoring levels (collapsible) */}
              <button
                onClick={() => setExpandedIdx(isExpanded ? null : idx)}
                className="mt-3 flex items-center text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
              >
                <svg className={`w-4 h-4 mr-1 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                  fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                </svg>
                Scoring Levels
                {cat.criteria.excellent || cat.criteria.good ? ' (defined)' : ' (optional)'}
              </button>
              {isExpanded && (
                <div className="mt-2 space-y-2 pl-5 border-l-2 border-indigo-200 dark:border-indigo-800">
                  {(['excellent', 'good', 'satisfactory', 'needs_improvement'] as const).map(level => (
                    <div key={level}>
                      <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 capitalize">
                        {level.replace('_', ' ')}
                        <span className="text-gray-400 ml-1">
                          ({level === 'excellent' ? '90-100%' : level === 'good' ? '75-89%' : level === 'satisfactory' ? '60-74%' : '<60%'})
                        </span>
                      </label>
                      <input
                        type="text"
                        value={cat.criteria[level]}
                        onChange={e => updateCriteria(idx, level, e.target.value)}
                        placeholder={`Describe ${level.replace('_', ' ')} performance...`}
                        className={inputCls + ' mt-0.5'}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Add category */}
      <button
        onClick={() => {
          setCategories(cats => [...cats, emptyCategory()]);
          setExpandedIdx(null);
        }}
        className="mt-4 w-full py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-500 dark:text-gray-400 hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-500 dark:hover:text-indigo-400"
      >
        + Add Category
      </button>

      {/* Action buttons */}
      <div className="mt-6 flex items-center gap-3 pb-8">
        <button
          onClick={() => handleSave(false)}
          disabled={saving}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Rubric'}
        </button>
        <button
          onClick={() => handleSave(true)}
          disabled={saving}
          className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          Save & Generate Prompts
        </button>
        <button
          onClick={() => navigate(`/assignments/${id}`)}
          className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        {saved && (
          <span className="text-sm text-green-600 dark:text-green-400">Saved</span>
        )}
      </div>
    </div>
  );
}
