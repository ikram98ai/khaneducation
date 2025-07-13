import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";
import { useToast } from "@/hooks/use-toast";
import {
  loginUser,
  registerUser,
  getCurrentUser,
  getSubjects,
  getSubject,
  createStudentProfile,
  getStudentProfile,
  getLessons,
  getLesson,
  getQuizzes,
  getQuiz,
  submitQuiz,
  getPracticeTasks,
  getEnrollments,
  getStudentDashboard,
  getLanguages,
  getAiAssistance,
  getStudentDashboardStatistics,
} from "@/services/api";
import {
  User,
  QuizSubmission,
  AIAssistRequest,
  StudentProfile,
} from "@/types/api";

// Auth hooks
export const useLogin = () => {
  const { setAuth, setLoading } = useAuthStore();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      loginUser(email, password),
    onMutate: () => {
      setLoading(true);
    },
    onSuccess: async (data, variables) => {
      const profile = await getCurrentUser();

      setAuth(profile, data.access_token);

      toast({
        title: "Welcome back!",
        description: "Successfully logged in.",
      });
    },
    onError: (error: any) => {
      setLoading(false);
      toast({
        title: "Login Failed",
        description: error.message || "Invalid credentials. Please try again.",
        variant: "destructive",
      });
    },
  });
};

export const useRegister = () => {
  const { setAuth, setLoading } = useAuthStore();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (userData: Partial<User>) => registerUser(userData),
    onMutate: () => {
      setLoading(true);
    },
    onSuccess: async (user, variables) => {
      // variables contains the userData passed to mutationFn, including password if provided
      const response = await loginUser(user.email, variables.password);
      const profile = await getCurrentUser();
      setAuth(profile, response.access_token);
      toast({
        title: "Account Created!",
        description: "Welcome to our educational platform.",
      });
    },
    onError: (error: any) => {
      setLoading(false);
      toast({
        title: "Registration Failed",
        description:
          error.message || "Unable to create account. Please try again.",
        variant: "destructive",
      });
    },
  });
};

// Profile hooks
export const useCreateProfile = () => {
  const { setProfile } = useAuthStore();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (profileData: { language: string; current_grade: string }) =>
      createStudentProfile(profileData),
    onSuccess: (profile) => {
      setProfile(profile);
      toast({
        title: "Profile Created!",
        description: "Your learning profile has been set up.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Profile Creation Failed",
        description:
          error.message || "Unable to create profile. Please try again.",
        variant: "destructive",
      });
    },
  });
};

export const useStudentProfile = () => {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ["student-profile"],
    queryFn: getStudentProfile,
    enabled: isAuthenticated,
  });
};

// Subject hooks
export const useSubjects = (params?: {
  grade_level?: number;
  language?: string;
  search?: string;
}) => {
  return useQuery({
    queryKey: ["subjects", params],
    queryFn: () => getSubjects(params),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useSubject = (id: string) => {
  return useQuery({
    queryKey: ["subject", id],
    queryFn: () => getSubject(id),
    enabled: !!id,
  });
};

// Lesson hooks
export const useLessons = (subjectId: string) => {
  return useQuery({
    queryKey: ["lessons", subjectId],
    queryFn: () => getLessons(subjectId),
    enabled: !!subjectId,
  });
};

export const useLesson = (subjectId: string, lessonId: string) => {
  return useQuery({
    queryKey: ["lesson", subjectId, lessonId],
    queryFn: () => getLesson(subjectId, lessonId),
    enabled: !!subjectId && !!lessonId,
  });
};

// Quiz hooks
export const useQuizzes = (subjectId: string, lessonId: string) => {
  return useQuery({
    queryKey: ["quizzes", subjectId, lessonId],
    queryFn: () => getQuizzes(subjectId, lessonId),
    enabled: !!subjectId && !!lessonId,
  });
};

export const useQuiz = (
  subjectId: string,
  lessonId: string,
  quizId: string
) => {
  return useQuery({
    queryKey: ["quiz", subjectId, lessonId, quizId],
    queryFn: () => getQuiz(subjectId, lessonId, quizId),
    enabled: !!subjectId && !!lessonId && !!quizId,
  });
};

export const useSubmitQuiz = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (submission: QuizSubmission) => submitQuiz(submission),
    onSuccess: (data) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ["student-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["enrollments"] });

      const passed = data.attempt.passed;
      toast({
        title: passed ? "Quiz Passed!" : "Quiz Completed",
        description: `Score: ${Math.round(data.attempt.score)}%. ${
          data.ai_feedback
        }`,
        variant: passed ? "default" : "destructive",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Quiz Submission Failed",
        description:
          error.message || "Unable to submit quiz. Please try again.",
        variant: "destructive",
      });
    },
  });
};

// Practice tasks
export const usePracticeTasks = (subjectId: string, lessonId: string) => {
  return useQuery({
    queryKey: ["practice-tasks", subjectId, lessonId],
    queryFn: () => getPracticeTasks(subjectId, lessonId),
    enabled: !!subjectId && !!lessonId,
  });
};

// Enrollment hooks
export const useEnrollments = () => {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ["enrollments"],
    queryFn: getEnrollments,
    enabled: isAuthenticated,
  });
};

// Dashboard hooks
export const useStudentDashboard = () => {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ["student-dashboard"],
    queryFn: getStudentDashboard,
    enabled: isAuthenticated,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// Languages hooks
export const useLanguages = () => {
  return useQuery({
    queryKey: ["get-languages"],
    queryFn: getLanguages,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// AI Assistant hooks
export const useAiAssistance = () => {
  const { toast } = useToast();

  return useMutation({
    mutationFn: (request: AIAssistRequest) => getAiAssistance(request),
    onError: (error: any) => {
      toast({
        title: "AI Assistant Error",
        description:
          error.message || "Unable to get AI assistance. Please try again.",
        variant: "destructive",
      });
    },
  });
};

export const useStudentDashboardStatistics = () => {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ["student-dashboard-statistics"],
    queryFn: getStudentDashboardStatistics,
    enabled: isAuthenticated,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};
