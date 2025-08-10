// API Types based on apidocs.md

export interface User {
  id: string;
  username: string;
  email: string;
  password?: string;
  role: string;
  first_name: string;
  last_name: string;
  dp?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Subject {
  id?: string;
  name: string;
  description: string;
  total_lessons?: number;
  completed_lessons?: number;
  progress?: number;
  grade_level: number;
}

export interface Lesson {
  id: string;
  instructor_id: string;
  subject_id: string;
  title: string;
  content: string;
  status: "verified" | "draft" | "pending" | "failed";
  language: "Arabic" | "English" | "Pashto" | "Persian" | "Urdu";
  order_in_subject?: number;
  created_at: string;
  updated_at: string;
  verified_at: string | null;
  progress?: number;
}

export interface SubjectDetail extends Subject {
  lessons?: Lesson[];
}

export interface Question {
  question_id: string;
  question_text: string;
  question_type: string;
  options?: string[];
  correct_answer: string;
  points?: number;
}

export interface Quiz {
  id: string;
  lesson_title: string;
  quiz_questions: Question[];
  ai_generated: boolean;
  created_at: string;
}

export interface PracticeTask {
  id: string;
  lesson: string;
  lesson_title: string;
  content: string;
  solution: string;
  difficulty: "EA" | "ME" | "HA"; // Easy, Medium, Hard
  ai_generated: boolean;
  created_at: string;
}

export interface Student {
  id?: string;
  language: string;
  current_grade: string;
}

export interface StudentProfile {
  user: User;
  student_profile?: Student;
}

export interface Enrollment extends Subject {
  enrolled_at: string;
}

export interface QuizAttempt {
  id: string;
  student_id?: string;
  quiz_id: string;
  quiz_version: number;
  start_time: string;
  lesson_title?: string;
  end_time: string;
  score: number;
  passed: boolean;
  ai_feedback?:string;
  cheating_detected: boolean;
}

export interface QuizResponse {
  question_id: string;
  student_answer: string;
}

export interface QuizSubmission {
  quiz_id: string;
  responses: QuizResponse[];
}

export interface StudentDashboard {
  enrollments: Enrollment[];
  recent_attempts: QuizAttempt[];
}

export interface AdminDashboard {
  total_students: number;
  total_lessons: number;
  total_subjects: number;
  total_quizzes: number;
  recent_lessons: Lesson[];
  recent_attempts: QuizAttempt[];
}

interface AIMessage{
  role:string;
  content:string;
}
export interface AIAssistRequest {
  subject_id: string;
  lesson_id?: string;
  user_messages:  AIMessage[];
}

export interface AIAssistResponse {
  ai_response: string;
}

export interface StudentDashboardStats {
  completed_lessons: number;
  total_lessons: number;
  avg_score: number;
  streak: number;
}
