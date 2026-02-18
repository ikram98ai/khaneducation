import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
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
  updateUserProfile,
  updateStudentProfile,
  getLesson,
  getQuiz,
  submitQuiz,
  getPracticeTasks,
  getStudentDashboard,
  getLanguages,
  getAiAssistance,
  getAdminDashboard,
  adminAPI,
  getSubjectDetail,
  getQuizAttempts,
} from "@/services/api";
import {
  User,
  QuizSubmission,
  AIAssistRequest,
  Subject,
  Lesson,
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
    onError: (error: AxiosError) => {
      setLoading(false);
      toast({
        title: "Login Failed",
        description: (error.response?.data as { detail: string })?.detail || "Invalid credentials. Please try again.",
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
    onError: (error: AxiosError) => {
      setLoading(false);
      toast({
        title: "Registration Failed",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "Unable to create account. Please try again.",
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
    onError: (error: AxiosError) => {
      toast({
        title: "Profile Creation Failed",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "Unable to create profile. Please try again.",
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

export const useUpdateUserProfile = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (profileData: {
      first_name: string;
      last_name: string;
      email: string;
    }) => updateUserProfile(profileData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["student-profile"] });
      toast({
        title: "Profile Updated",
        description: "Your profile has been updated successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Profile Update Failed",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "Unable to update profile. Please try again.",
        variant: "destructive",
      });
    },
  });
};

export const useUpdateStudentProfile = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (profileData: { language: string }) =>
      updateStudentProfile(profileData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["student-profile"] });
      toast({
        title: "Profile Updated",
        description: "Your profile has been updated successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Profile Update Failed",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "Unable to update profile. Please try again.",
        variant: "destructive",
      });
    },
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

export const useSubjectDetail = (id: string) => {
  return useQuery({
    queryKey: ["subject-detail", id],
    queryFn: () => getSubjectDetail(id),
    enabled: !!id,
  });
};
export const useLesson = (lessonId: string) => {
  return useQuery({
    queryKey: ["lesson", lessonId],
    queryFn: () => getLesson(lessonId),
    enabled: !!lessonId,
  });
};

// Quiz hooks
export const useQuiz = (lessonId: string, options?: { enabled: boolean }) => {
  return useQuery({
    queryKey: ["quiz", lessonId],
    queryFn: () => getQuiz(lessonId),
    enabled: !!lessonId,
    gcTime: 0, // Disable cache
    ...options,
  });
};

export const useQuizAttempts = (lessonId: string) => {
  return useQuery({
    queryKey: ["quiz-attempts", lessonId],
    queryFn: () => getQuizAttempts(lessonId),
    enabled: !!lessonId,
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
    onError: (error: AxiosError) => {
      toast({
        title: "Quiz Submission Failed",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "Unable to submit quiz. Please try again.",
        variant: "destructive",
      });
    },
  });
};

// Practice tasks
export const usePracticeTasks = (lessonId: string) => {
  return useQuery({
    queryKey: ["practice-tasks", lessonId],
    queryFn: () => getPracticeTasks(lessonId),
    enabled: !!lessonId,
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
    onError: (error: AxiosError) => {
      toast({
        title: "AI Assistant Error",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "Unable to get AI assistance. Please try again.",
        variant: "destructive",
      });
    },
  });
};


// Admin hooks with comprehensive error handling
export const useAdminUsers = (params?: { skip?: number; limit?: number }) => {
  const { profile } = useAuthStore();
  const isAdmin = profile?.user?.role === "admin";

  return useQuery({
    queryKey: ["admin-users", params],
    queryFn: () => adminAPI.getUsers(params),
    enabled: isAdmin,
    retry: 3,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (userData: Partial<User>) => adminAPI.createUser(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      toast({
        title: "User Created",
        description: "New user has been created successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Create User",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      userId,
      userData,
    }: {
      userId: string;
      userData: Partial<User>;
    }) => adminAPI.updateUser(userId, userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      toast({
        title: "User Updated",
        description: "User information has been updated successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Update User",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (userId: string) => adminAPI.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      toast({
        title: "User Deleted",
        description: "User has been deleted successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Delete User",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useAdminSubjects = (params?: {
  skip?: number;
  limit?: number;
}) => {
  const { profile } = useAuthStore();
  const isAdmin = profile?.user?.role === "admin";

  return useQuery({
    queryKey: ["admin-subjects", params],
    queryFn: () => adminAPI.getAdminSubjects(params),
    enabled: isAdmin,
    retry: 3,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateAdminSubject = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (
      subjectData: Omit<
        Subject,
        "id" | "total_lessons" | "completed_lessons" | "progress"
      >
    ) => adminAPI.createAdminSubject(subjectData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subjects"] });
      toast({
        title: "Subject Created",
        description: "New subject has been created successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Create Subject",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useUpdateAdminSubject = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      subjectId,
      subjectData,
    }: {
      subjectId: string;
      subjectData: Partial<Subject>;
    }) => adminAPI.updateAdminSubject(subjectId, subjectData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subjects"] });
      toast({
        title: "Subject Updated",
        description: "Subject has been updated successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Update Subject",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useDeleteAdminSubject = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (subjectId: string) => adminAPI.deleteAdminSubject(subjectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subjects"] });
      toast({
        title: "Subject Deleted",
        description: "Subject has been deleted successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Delete Subject",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useAdminDashboard = () => {
  const { profile } = useAuthStore();
  const isAdmin = profile?.user?.role === "admin";

  return useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: getAdminDashboard,
    enabled: isAdmin,
    staleTime: 2 * 60 * 1000,
    retry: 3,
  });
};

export const useAdminLessons = (
  subjectId: string,
  params?: { skip?: number; limit?: number }
) => {
  const { profile } = useAuthStore();
  const isAdmin = profile?.user?.role === "admin";

  return useQuery({
    queryKey: ["admin-lessons", subjectId, params],
    queryFn: () => adminAPI.getAdminLessons(subjectId as string, params),
    enabled: isAdmin && !!subjectId,
    retry: 3,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateAdminLesson = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      subjectId,
      lessonData,
    }: {
      subjectId: string;
      lessonData: { title: string; language: "Arabic" | "English" | "Pashto" | "Persian" | "Urdu" };
    }) => adminAPI.createAdminLesson(subjectId, lessonData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-lessons"] });
      toast({
        title: "Lesson Creation Initiated",
        description: "New lesson is being created in the background.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Create Lesson",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useRegenerateAdminLessonContent = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (lessonId: string) =>
      adminAPI.regenerateAdminLessonContent(lessonId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-lessons"] });
      toast({
        title: "Content Regeneration Started",
        description: "Lesson content is being regenerated in the background.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Regenerate Content",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useUpdateAdminLesson = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      lessonId,
      lessonData,
    }: {
      lessonId: string;
      lessonData: Partial<Lesson>;
    }) => adminAPI.updateAdminLesson(lessonId, lessonData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-lessons"] });
      toast({
        title: "Lesson Updated",
        description: "Lesson information has been updated successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Update Lesson",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useDeleteAdminLesson = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (lessonId: string) => adminAPI.deleteAdminLesson(lessonId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-lessons"] });
      toast({
        title: "Lesson Deleted",
        description: "Lesson has been deleted successfully.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Delete Lesson",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};

export const useVerifyAdminLesson = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (lessonId: string) => adminAPI.verifyAdminLesson(lessonId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-lessons"] });
      toast({
        title: "Lesson Verified",
        description: "Lesson has been marked as verified.",
      });
    },
    onError: (error: AxiosError) => {
      toast({
        title: "Failed to Verify Lesson",
        description:
          (error.response?.data as { detail: string })?.detail ||
          "An error occurred",
        variant: "destructive",
      });
    },
  });
};
