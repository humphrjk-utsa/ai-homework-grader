import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCourse } from '../../api/courses';

const inputCls = "mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500";

export default function NewCoursePage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', code: '', semester: 'Spring', year: new Date().getFullYear() });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const course = await createCourse({ ...form, year: Number(form.year) });
      navigate(`/courses/${course.id}`);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">New Course</h1>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        {error && <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-3 rounded text-sm">{error}</div>}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Course Name</label>
          <input type="text" required value={form.name} onChange={set('name')} placeholder="e.g. Business Analytics" className={inputCls} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Course Code</label>
          <input type="text" value={form.code} onChange={set('code')} placeholder="e.g. BA 501" className={inputCls} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Semester</label>
            <select value={form.semester} onChange={set('semester')} className={inputCls}>
              <option>Spring</option>
              <option>Summer</option>
              <option>Fall</option>
              <option>Winter</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Year</label>
            <input type="number" required value={form.year} onChange={set('year')} className={inputCls} />
          </div>
        </div>
        <div className="flex space-x-3 pt-2">
          <button type="submit" disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Course'}
          </button>
          <button type="button" onClick={() => navigate('/courses')}
            className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
