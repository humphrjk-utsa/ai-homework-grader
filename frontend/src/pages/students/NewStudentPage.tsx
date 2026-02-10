import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { addStudent } from '../../api/students';

const inputCls = "mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500";

export default function NewStudentPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', canvas_id: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await addStudent(Number(courseId), form);
      navigate(`/courses/${courseId}`);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to add student');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Add Student</h1>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        {error && <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-3 rounded text-sm">{error}</div>}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">First Name</label>
            <input type="text" required value={form.first_name} onChange={set('first_name')} className={inputCls} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Last Name</label>
            <input type="text" required value={form.last_name} onChange={set('last_name')} className={inputCls} />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
          <input type="email" required value={form.email} onChange={set('email')} className={inputCls} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Canvas ID (optional)</label>
          <input type="text" value={form.canvas_id} onChange={set('canvas_id')} className={inputCls} />
        </div>
        <div className="flex space-x-3 pt-2">
          <button type="submit" disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50">
            {loading ? 'Adding...' : 'Add Student'}
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
