import { useState, useEffect } from 'react';
import { getTrainingStats, exportTrainingData, previewTrainingData } from '../../api/training';
import type { TrainingStats, SamplePreview } from '../../api/training';

interface Props {
  courseId: number;
}

export default function TrainingDataTab({ courseId }: Props) {
  const [stats, setStats] = useState<TrainingStats | null>(null);
  const [previews, setPreviews] = useState<SamplePreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState('');

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getTrainingStats(courseId),
      previewTrainingData(courseId),
    ])
      .then(([s, p]) => { setStats(s); setPreviews(p); })
      .finally(() => setLoading(false));
  }, [courseId]);

  const handleExport = async () => {
    setExporting(true);
    setExportMessage('');
    try {
      const result = await exportTrainingData(courseId);
      setExportMessage(`Exported ${result.num_samples} samples to ${result.relative_path}`);
    } catch (err: any) {
      setExportMessage(err.response?.data?.error || 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <p className="text-gray-400">Loading training data stats...</p>;
  if (!stats) return <p className="text-red-500">Failed to load stats</p>;

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Graded Submissions', value: stats.total_graded, color: 'text-blue-600 dark:text-blue-400' },
          { label: 'Reviewed', value: stats.total_reviewed, color: 'text-green-600 dark:text-green-400' },
          { label: 'Edited (Ready to Learn From)', value: stats.total_edited, color: 'text-purple-600 dark:text-purple-400' },
        ].map((card) => (
          <div key={card.label} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">{card.label}</p>
            <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
          </div>
        ))}
      </div>

      {/* Per-assignment breakdown */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Assignment</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Graded</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Reviewed</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Edited</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {stats.assignments.map((a) => (
              <tr key={a.id}>
                <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{a.name}</td>
                <td className="px-4 py-3 text-sm text-right text-gray-500 dark:text-gray-400">{a.graded}</td>
                <td className="px-4 py-3 text-sm text-right text-gray-500 dark:text-gray-400">{a.reviewed}</td>
                <td className="px-4 py-3 text-sm text-right text-purple-600 dark:text-purple-400 font-medium">{a.edited}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Sample preview */}
      {previews.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sample Training Data</h3>
          <div className="space-y-2">
            {previews.map((p, i) => (
              <div key={i} className="bg-gray-50 dark:bg-gray-900/30 rounded p-3 text-sm">
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.student_name}</span>
                <span className="text-gray-400 mx-2">-</span>
                <span className="text-gray-500 dark:text-gray-400">{p.assignment}</span>
                <span className="text-gray-400 mx-2">-</span>
                <span className="text-gray-500 dark:text-gray-400">{p.score}/{p.max_score}</span>
                <span className="ml-2 text-xs text-gray-400">keys: {p.feedback_keys.join(', ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Export button */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleExport}
          disabled={exporting || stats.total_edited === 0}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {exporting ? 'Exporting...' : 'Export JSONL Training Data'}
        </button>
        {stats.total_edited === 0 && (
          <span className="text-xs text-gray-400">Review and edit AI feedback, or import existing grades, to build training data</span>
        )}
        {exportMessage && (
          <span className="text-sm text-indigo-600 dark:text-indigo-400">{exportMessage}</span>
        )}
      </div>
    </div>
  );
}
