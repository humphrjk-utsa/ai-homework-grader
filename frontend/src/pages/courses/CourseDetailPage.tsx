import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { getCourse } from '../../api/courses';
import { listAssignments } from '../../api/assignments';
import { listStudents } from '../../api/students';
import { syncStudents } from '../../api/canvas';
import type { Course, Assignment, Student } from '../../types';

export default function CourseDetailPage() {
  const { user } = useAuth();
  const { courseId } = useParams<{ courseId: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [tab, setTab] = useState<'assignments' | 'students'>('assignments');
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    const id = Number(courseId);
    Promise.all([
      getCourse(id),
      listAssignments(id),
      listStudents(id),
    ]).then(([c, a, s]) => {
      setCourse(c);
      setAssignments(a);
      setStudents(s);
    }).finally(() => setLoading(false));
  }, [courseId]);

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Loading...</p>;
  if (!course) return <p className="text-red-500">Course not found</p>;

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{course.name}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {course.code && `${course.code} - `}{course.semester} {course.year}
          </p>
        </div>
        {user?.role !== 'ta' && (
          <Link
            to={`/courses/${courseId}/training`}
            className="px-4 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700"
          >
            Training & Models
          </Link>
        )}
      </div>

      {/* Tabs */}
      <div className="mt-6 border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8">
          <button
            onClick={() => setTab('assignments')}
            className={`pb-3 text-sm font-medium border-b-2 ${
              tab === 'assignments'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            Assignments ({assignments.length})
          </button>
          <button
            onClick={() => setTab('students')}
            className={`pb-3 text-sm font-medium border-b-2 ${
              tab === 'students'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            Students ({students.length})
          </button>
        </nav>
      </div>

      {/* Assignments tab */}
      {tab === 'assignments' && (
        <div className="mt-4">
          <div className="flex justify-end mb-4">
            <Link
              to={`/courses/${courseId}/assignments/new`}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
            >
              New Assignment
            </Link>
          </div>
          {assignments.length === 0 ? (
            <div className="p-8 text-center bg-white dark:bg-gray-800 rounded-lg border border-dashed border-gray-300 dark:border-gray-600">
              <p className="text-gray-500 dark:text-gray-400">No assignments yet.</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Points</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Submissions</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Graded</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {assignments.map((a) => (
                    <tr key={a.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                      <td className="px-6 py-4">
                        <Link to={`/assignments/${a.id}`} className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium">
                          {a.name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                          a.assignment_type === 'coding'
                            ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
                            : 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
                        }`}>
                          {a.assignment_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{a.total_points}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{a.total_submissions ?? 0}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{a.graded_submissions ?? 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Students tab */}
      {tab === 'students' && (
        <div className="mt-4">
          <div className="flex justify-end mb-4 space-x-2">
            {user?.role !== 'ta' && course?.settings && (
              <button
                onClick={async () => {
                  setSyncing(true);
                  try {
                    const result = await syncStudents(Number(courseId));
                    alert(`Synced ${result.total} students (${result.created} new, ${result.updated} updated)`);
                    // Refresh students
                    const s = await listStudents(Number(courseId));
                    setStudents(s);
                  } catch (err: any) {
                    alert(err.response?.data?.error || 'Canvas sync failed');
                  } finally {
                    setSyncing(false);
                  }
                }}
                disabled={syncing}
                className="px-4 py-2 bg-orange-600 text-white text-sm rounded-md hover:bg-orange-700 disabled:opacity-50"
              >
                {syncing ? 'Syncing...' : 'Sync from Canvas'}
              </button>
            )}
            <Link
              to={`/courses/${courseId}/students/import`}
              className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              Import CSV
            </Link>
            <Link
              to={`/courses/${courseId}/students/new`}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
            >
              Add Student
            </Link>
          </div>
          {students.length === 0 ? (
            <div className="p-8 text-center bg-white dark:bg-gray-800 rounded-lg border border-dashed border-gray-300 dark:border-gray-600">
              <p className="text-gray-500 dark:text-gray-400">No students enrolled yet.</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Canvas ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {students.map((s) => (
                    <tr key={s.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                        {s.first_name} {s.last_name}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{s.email}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{s.canvas_id || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
