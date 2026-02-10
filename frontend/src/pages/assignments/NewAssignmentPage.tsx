import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createAssignment } from '../../api/assignments';

const inputCls = "mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500";

export default function NewAssignmentPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    assignment_type: 'coding',
    total_points: 100,
    language: 'R',
    description: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const assignment = await createAssignment(Number(courseId), {
        ...form,
        total_points: Number(form.total_points),
      });
      navigate(`/assignments/${assignment.id}`);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create assignment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">New Assignment</h1>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        {error && <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-3 rounded text-sm">{error}</div>}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Assignment Name</label>
          <input type="text" required value={form.name} onChange={set('name')}
            placeholder="e.g. Homework 3" className={inputCls} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Type</label>
            <select value={form.assignment_type} onChange={set('assignment_type')} className={inputCls}>
              <option value="coding">Coding</option>
              <option value="written">Written</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Total Points</label>
            <input type="number" required value={form.total_points} onChange={set('total_points')} className={inputCls} />
          </div>
        </div>
        {form.assignment_type === 'coding' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Language</label>
            <select value={form.language} onChange={set('language')} className={inputCls}>
              <option value="R">R</option>
              <option value="Python">Python</option>
              <option value="SQL">SQL</option>
              <option value="SAS">SAS</option>
            </select>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
          <textarea value={form.description} onChange={set('description')} rows={3} className={inputCls} />
        </div>
        <div className="flex space-x-3 pt-2">
          <button type="submit" disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Assignment'}
          </button>
          <button type="button" onClick={() => navigate(`/courses/${courseId}`)}
            className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
