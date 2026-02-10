import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import CourseListPage from './pages/courses/CourseListPage';
import NewCoursePage from './pages/courses/NewCoursePage';
import CourseDetailPage from './pages/courses/CourseDetailPage';
import NewAssignmentPage from './pages/assignments/NewAssignmentPage';
import AssignmentDetailPage from './pages/assignments/AssignmentDetailPage';
import RubricBuilderPage from './pages/assignments/RubricBuilderPage';
import NewStudentPage from './pages/students/NewStudentPage';
import ImportStudentsPage from './pages/students/ImportStudentsPage';
import SubmissionDetailPage from './pages/submissions/SubmissionDetailPage';
import BatchReviewPage from './pages/assignments/BatchReviewPage';
import TrainingDashboardPage from './pages/training/TrainingDashboardPage';
import GroundTruthUploadPage from './pages/assignments/GroundTruthUploadPage';
import PromptPlaygroundPage from './pages/assignments/PromptPlaygroundPage';
import CanvasSettingsPage from './pages/canvas/CanvasSettingsPage';

export default function App() {
  return (
    <ThemeProvider>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/courses" element={<CourseListPage />} />
            <Route path="/courses/new" element={<NewCoursePage />} />
            <Route path="/courses/:courseId" element={<CourseDetailPage />} />
            <Route path="/courses/:courseId/assignments/new" element={<NewAssignmentPage />} />
            <Route path="/courses/:courseId/students/new" element={<NewStudentPage />} />
            <Route path="/courses/:courseId/students/import" element={<ImportStudentsPage />} />
            <Route path="/assignments/:assignmentId" element={<AssignmentDetailPage />} />
            <Route path="/assignments/:assignmentId/rubric/edit" element={<RubricBuilderPage />} />
            <Route path="/assignments/:assignmentId/review" element={<BatchReviewPage />} />
            <Route path="/assignments/:assignmentId/ground-truth" element={<GroundTruthUploadPage />} />
            <Route path="/assignments/:assignmentId/playground" element={<PromptPlaygroundPage />} />
            <Route path="/submissions/:submissionId" element={<SubmissionDetailPage />} />
            <Route path="/courses/:courseId/training" element={<TrainingDashboardPage />} />
            <Route path="/canvas/settings" element={<CanvasSettingsPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
    </ThemeProvider>
  );
}
