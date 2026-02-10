import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { listCourses } from '../../api/courses';
import { getDashboard } from '../../api/dashboard';
import type { Course, DashboardData } from '../../types';

export default function DashboardPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      listCourses(),
      getDashboard(),
    ]).then(([c, d]) => {
      setCourses(c);
      setDashboard(d);
    }).catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const totalAssignments = courses.reduce((s, c) => s + (c.assignment_count || 0), 0);
  const totalStudents = courses.reduce((s, c) => s + (c.student_count || 0), 0);

  const jobStatusColor: Record<string, string> = {
    pending: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
    running: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    completed: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
    failed: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
    cancelled: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
        Welcome, {user?.first_name}
      </h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Here's an overview of your grading workspace.</p>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-4 gap-6">
        <StatCard label="Courses" value={courses.length} />
        <StatCard label="Assignments" value={totalAssignments} />
        <StatCard label="Students" value={totalStudents} />
        <StatCard
          label="Pending Reviews"
          value={dashboard?.pending_review_count ?? 0}
          highlight={!!dashboard?.pending_review_count}
        />
      </div>

      {/* Recent Grading Jobs */}
      {dashboard && dashboard.recent_jobs.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Grading Jobs</h2>
          <div className="mt-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Job ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Progress</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {dashboard.recent_jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="px-6 py-3 text-sm text-gray-900 dark:text-white">#{job.id}</td>
                    <td className="px-6 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${jobStatusColor[job.status] || ''}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                          <div
                            className="bg-indigo-600 rounded-full h-2 transition-all"
                            style={{ width: `${job.progress_percent}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {job.completed_submissions}/{job.total_submissions}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-sm text-gray-500 dark:text-gray-400">
                      {new Date(job.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Upcoming Deadlines */}
      {dashboard && dashboard.upcoming_deadlines.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Upcoming Deadlines</h2>
          <div className="mt-3 space-y-2">
            {dashboard.upcoming_deadlines.map((d) => (
              <Link
                key={d.id}
                to={`/assignments/${d.id}`}
                className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition"
              >
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{d.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{d.total_submissions} submissions</p>
                </div>
                <span className="text-sm text-orange-600 dark:text-orange-400 font-medium">
                  {d.due_date ? new Date(d.due_date).toLocaleDateString() : 'No date'}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Courses */}
      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Your Courses</h2>
          {user?.role !== 'ta' && (
            <Link
              to="/courses/new"
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
            >
              New Course
            </Link>
          )}
        </div>

        {loading ? (
          <p className="mt-4 text-gray-500 dark:text-gray-400">Loading...</p>
        ) : courses.length === 0 ? (
          <div className="mt-4 p-8 text-center bg-white dark:bg-gray-800 rounded-lg border border-dashed border-gray-300 dark:border-gray-600">
            <p className="text-gray-500 dark:text-gray-400">No courses yet. Create your first course to get started.</p>
          </div>
        ) : (
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((course) => (
              <Link
                key={course.id}
                to={`/courses/${course.id}`}
                className="block p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-sm transition"
              >
                <h3 className="font-semibold text-gray-900 dark:text-white">{course.name}</h3>
                {course.code && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">{course.code}</p>
                )}
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {course.semester} {course.year}
                </p>
                <div className="mt-3 flex space-x-4 text-xs text-gray-400 dark:text-gray-500">
                  <span>{course.assignment_count || 0} assignments</span>
                  <span>{course.student_count || 0} students</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: number; highlight?: boolean }) {
  return (
    <div className={`p-6 rounded-lg border ${
      highlight
        ? 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-700'
        : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
    }`}>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className={`mt-1 text-3xl font-bold ${
        highlight ? 'text-orange-600 dark:text-orange-400' : 'text-gray-900 dark:text-white'
      }`}>{value}</p>
    </div>
  );
}
