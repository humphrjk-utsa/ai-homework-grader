import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listCourses } from '../../api/courses';
import type { Course } from '../../types';

export default function CourseListPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCourses().then(setCourses).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Courses</h1>
        <Link
          to="/courses/new"
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
        >
          New Course
        </Link>
      </div>

      {loading ? (
        <p className="mt-4 text-gray-500 dark:text-gray-400">Loading...</p>
      ) : (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Code</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Semester</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Assignments</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Students</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {courses.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="px-6 py-4">
                    <Link to={`/courses/${c.id}`} className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium">
                      {c.name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{c.code}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{c.semester} {c.year}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{c.assignment_count || 0}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{c.student_count || 0}</td>
                </tr>
              ))}
              {courses.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                    No courses yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
