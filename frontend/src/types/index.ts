export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'instructor' | 'ta';
  organization_id: number;
  is_active: boolean;
  created_at: string;
}

export interface Course {
  id: number;
  name: string;
  code: string;
  semester: string;
  year: number;
  slug: string;
  owner_id: number;
  is_active: boolean;
  settings: Record<string, unknown>;
  created_at: string;
  assignment_count?: number;
  student_count?: number;
}

export interface Assignment {
  id: number;
  course_id: number;
  name: string;
  slug: string;
  description: string | null;
  assignment_type: 'coding' | 'written';
  total_points: number;
  language: string;
  rubric_path: string | null;
  solution_path: string | null;
  template_path: string | null;
  due_date: string | null;
  is_published: boolean;
  created_at: string;
  code_analysis_prompt: string | null;
  feedback_prompt: string | null;
  grading_config: Record<string, unknown> | null;
  version: number;
  total_submissions?: number;
  graded_submissions?: number;
}

export interface Student {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  canvas_id: string | null;
  student_id_external: string | null;
  created_at: string;
}

export interface TechnicalAnalysis {
  code_strengths: string[];
  code_suggestions: string[];
  technical_observations: string[];
}

export interface DetailedFeedback {
  reflection_assessment: string[];
  analytical_strengths: string[];
  business_application: string[];
  areas_for_development: string[];
  recommendations: string[];
}

export interface ComprehensiveFeedback {
  instructor_comments: string;
  detailed_feedback: DetailedFeedback;
}

export interface AIFeedback {
  final_score: number;
  final_score_percentage?: number;
  max_points: number;
  component_scores: Record<string, number>;
  component_percentages: Record<string, number>;
  technical_analysis: TechnicalAnalysis;
  comprehensive_feedback: ComprehensiveFeedback;
  validation_results?: Record<string, unknown>;
  grading_timestamp?: string;
  grading_system?: string;
  grading_stats?: Record<string, unknown>;
}

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  file_path: string;
  file_type: string;
  original_filename: string;
  status: 'uploaded' | 'queued' | 'grading' | 'graded' | 'reviewed' | 'error';
  ai_score: number | null;
  human_score: number | null;
  final_score: number | null;
  max_score: number | null;
  error_message: string | null;
  submitted_at: string;
  graded_at: string | null;
  reviewed_at: string | null;
  student?: Student;
  assignment?: Assignment;
  ai_feedback?: AIFeedback | null;
  edited_feedback?: AIFeedback | null;
  human_feedback?: string | null;
  component_scores?: Record<string, { score: number; max: number; evidence?: string }> | null;
  component_percentages?: Record<string, number> | null;
  validation_results?: Record<string, unknown> | null;
}

export interface Report {
  id: number;
  submission_id: number;
  file_path: string;
  file_size: number;
  generated_at: string;
}

export interface GradingJob {
  id: number;
  assignment_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  total_submissions: number;
  completed_submissions: number;
  failed_submissions: number;
  progress_percent: number;
  created_at: string;
}

export interface RubricCriteria {
  excellent: string;
  good: string;
  satisfactory: string;
  needs_improvement: string;
}

export interface RubricCategory {
  key: string;
  name: string;
  max_points: number;
  description: string;
  criteria: RubricCriteria;
}

export interface RubricData {
  assignment_info: {
    name: string;
    title: string;
    total_points: number;
  };
  categories: RubricCategory[];
}

export interface DashboardData {
  recent_jobs: GradingJob[];
  pending_review_count: number;
  upcoming_deadlines: {
    id: number;
    name: string;
    course_id: number;
    due_date: string | null;
    total_submissions: number;
  }[];
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
}
