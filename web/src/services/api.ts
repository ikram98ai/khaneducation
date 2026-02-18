// API Service Layer with Dummy Data
import {
  User,
  AuthResponse,
  Subject,
  Lesson,
  Quiz,
  PracticeTask,
  StudentProfile,
  QuizAttempt,
  StudentDashboard,
  AdminDashboard,
  AIAssistRequest,
  AIAssistResponse,
  QuizSubmission,
  SubjectDetail,
  QuizAttemptOut,
} from "@/types/api";

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || (process.env.NODE_ENV === 'production'
  ? "https://api.khaneducation.ai"
  : "http://localhost:8000");

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    // Use Zustand store directly to get the token, since it's persisted and hydrated
    // const token = useAuthStore.getState().token;
    const token = localStorage.getItem("accessToken");

    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication APIs

export async function loginUser(
  email: string,
  password: string
): Promise<AuthResponse> {
  const response = await api.post("/login/", { email, password });
  localStorage.setItem("accessToken", response.data.access_token);
  return response.data;
}

export async function registerUser(userData: Partial<User>): Promise<User> {
  const response = await api.post("/users/", userData);
  return response.data;
}

export async function getCurrentUser(): Promise<StudentProfile> {
  const response = await api.get(`/users/profile/me/`);
  return response.data;
}

export async function updateUser(userData: Partial<User>): Promise<User> {
  const response = await api.put("/users/profile/me/", userData);
  return response.data;
}

export async function createStudentProfile(profileData: {
  language: string;
  current_grade: string;
}): Promise<StudentProfile> {
  const response = await api.post("/users/profile/me/", profileData);
  return response.data;
}

export async function getStudentProfile(): Promise<StudentProfile> {
  const response = await api.get("/users/profile/me/");
  return response.data;
}

export async function updateUserProfile(profileData: {
  first_name: string;
  last_name: string;
  email: string;
}): Promise<User> {
  const response = await api.put("/users/profile/me/", profileData);
  return response.data;
}

export async function updateStudentProfile(profileData: {
  language: string;
}): Promise<StudentProfile> {
  const response = await api.put("/users/profile/me/student", profileData);
  return response.data;
}



// Language APIs
export async function getLanguages(): Promise<string[]> {
  const response = await api.get("/languages/");
  return response.data;
}

// AI Assistant APIs
export async function getAiAssistance(
  request: AIAssistRequest
): Promise<AIAssistResponse> {
  const response = await api.post("/ai/assist/", request);
  return response.data;
}

// Content APIs
export async function getSubjects(params?: {
  grade_level?: number;
  language?: string;
  search?: string;
}): Promise<Subject[]> {
  const response = await api.get<Subject[]>("/subjects/", { params });
  return response.data;
}

export async function getSubject(id: string): Promise<Subject> {
  const response = await api.get(`/subjects/${id}/`);
  return response.data;
}

export async function getSubjectDetail(id: string): Promise<SubjectDetail> {
  const response = await api.get(`/subjects/${id}/details`);
  return response.data;
}
export async function getLesson(
  lessonId: string
): Promise<Lesson> {
  const response = await api.get(`lessons/${lessonId}/`);
  return response.data;
}

export async function getPracticeTasks(
  lessonId: string
): Promise<PracticeTask[]> {
  const response = await api.get(
    `/lessons/${lessonId}/tasks/`
  );
  return response.data;
}

export async function getQuiz(
  lessonId: string
): Promise<Quiz | null> {
  const response = await api.get(
    `/lessons/${lessonId}/quiz/`
  );
  return response.data;
}

export async function getQuizAttempts(
  lessonId: string
): Promise<QuizAttemptOut[] | []> {
  const response = await api.get(
    `/lessons/${lessonId}/attempts/`
  );
  return response.data;
}



// Quiz APIs


export async function submitQuiz(submission: Partial<QuizSubmission>): Promise<{
  attempt: QuizAttempt;
  ai_feedback: string;
  regenerated_quiz?: Quiz;
}> {
  const response = await api.post(`/quizzes/${submission.quiz_id}/submit/`, submission.responses);
  return response.data;
}

// Dashboard APIs

export async function getStudentDashboard(): Promise<StudentDashboard> {
  const response = await api.get("/dashboard/student/");
  return response.data;
}


export async function getAdminDashboard(): Promise<AdminDashboard> {
  const response = await api.get("/dashboard/admin/");
  return response.data;
}

// Admin APIs
export const adminAPI = {
  // User Management
  createUser: async (userData: Partial<User>): Promise<User> => {
    const response = await api.post("/admin/users/", userData);
    return response.data;
  },

  getUsers: async (params?: { skip?: number; limit?: number }): Promise<User[]> => {
    const response = await api.get("/admin/users/", { params });
    return response.data;
  },

  getUser: async (userId: string): Promise<User> => {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  },

  updateUser: async (userId: string, userData: Partial<User>): Promise<User> => {
    const response = await api.put(`/admin/users/${userId}`, userData);
    return response.data;
  },

  deleteUser: async (userId: string): Promise<User> => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },

  // Admin Subject Management
  createAdminSubject: async (subjectData: Omit<Subject, "id" | "total_lessons" | "completed_lessons" | "progress">): Promise<Subject> => {
    const response = await api.post("/admin/subjects/", subjectData);
    return response.data;
  },

  getAdminSubjects: async (params?: { skip?: number; limit?: number }): Promise<Subject[]> => {
    const response = await api.get("/admin/subjects/", { params });
    return response.data;
  },

  updateAdminSubject: async (subjectId: string, subjectData: Partial<Subject>): Promise<Subject> => {
    const response = await api.put(`/admin/subjects/${subjectId}`, subjectData);
    return response.data;
  },

  deleteAdminSubject: async (subjectId: string): Promise<Subject> => {
    const response = await api.delete(`/admin/subjects/${subjectId}`);
    return response.data;
  },

    // Admin Lesson Management
  createAdminLesson: async (subjectId: string, lessonData: Partial<Lesson>): Promise<Lesson> => {
    const response = await api.post(`/admin/subjects/${subjectId}/lessons/`, lessonData);
    return response.data;
  },

  getAdminLessons: async (subjectId: string, params?: { skip?: number; limit?: number }): Promise<Lesson[]> => {
    const response = await api.get(`/admin/subjects/${subjectId}/lessons/`, { params });
    return response.data;
  },

  getAdminLesson: async (lessonId: string): Promise<Lesson> => {
    const response = await api.get(`/admin/lessons/${lessonId}/`);
    return response.data;
  },

  updateAdminLesson: async (lessonId: string, lessonData: Partial<Lesson>): Promise<Lesson> => {
    const response = await api.put(`/admin/lessons/${lessonId}/`, lessonData);
    return response.data;
  },

  deleteAdminLesson: async (lessonId: string): Promise<Lesson> => {
    const response = await api.delete(`/admin/lessons/${lessonId}/`);
    return response.data;
  },

  regenerateAdminLessonContent: async (lessonId: string): Promise<void> => {
    await api.post(`/admin/lessons/${lessonId}/regenerate-content/`);
  },

  verifyAdminLesson: async (lessonId: string): Promise<Lesson> => {
    const response = await api.put(`/admin/lessons/${lessonId}/verify`);
    return response.data;
  },

  // Admin Practice Task Management
  createAdminPracticeTask: async (lessonId: string, taskData: { content: string; difficulty: "EA" | "ME" | "HA" }): Promise<PracticeTask> => {
    const response = await api.post(`/admin/lessons/${lessonId}/practice_tasks/`, taskData);
    return response.data;
  },

  getAdminPracticeTasks: async (lessonId: string, params?: { skip?: number; limit?: number }): Promise<PracticeTask[]> => {
    const response = await api.get(`/admin/lessons/${lessonId}/practice_tasks/`, { params });
    return response.data;
  },

  // Admin Quiz Management
  createAdminQuiz: async (lessonId: string, quizData: { version: number }): Promise<Quiz> => {
    const response = await api.post(`/admin/lessons/${lessonId}/quizzes/`, quizData);
    return response.data;
  },

  getAdminQuizzes: async (lessonId: string, params?: { skip?: number; limit?: number }): Promise<Quiz[]> => {
    const response = await api.get(`/admin/lessons/${lessonId}/quizzes/`, { params });
    return response.data;
  },
};

