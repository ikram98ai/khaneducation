import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import { AuthForm } from "./components/auth/AuthForm";
// import { CreateProfile } from "./components/profile/CreateProfile";
import { Dashboard } from "./components/dashboard/Dashboard";
import { SubjectDetail } from "./components/subjects/SubjectDetail";
import { LessonDetail } from "./components/lessons/LessonDetail";
import { AdminDashboard } from "./components/admin/AdminDashboard";
import { useAuthStore } from "./stores/authStore";
import { QuizPage } from "./components/quiz/QuizPage";
import { ProfilePage } from "./components/profile/ProfilePage";
import MainLayout from "./components/navigation/MainLayout";

const App = () => {
  const { profile } = useAuthStore();
  const isAdmin = profile?.user?.role === "admin";

  return (
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<AuthForm />} />
          {/* <Route path="/profile-setup" element={<CreateProfile />} /> */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/subjects/:subjectId" element={<SubjectDetail />} />
              <Route
                path="/subjects/:subjectId/lessons/:lessonId"
                element={<LessonDetail />}
              />
              <Route path="/lessons/:lessonId/quiz/" element={<QuizPage />} />
              <Route
                path="/dashboard"
                element={isAdmin ? <AdminDashboard /> : <Dashboard />}
              />
              <Route path="/profile/" element={<ProfilePage />} />
            </Route>
          </Route>
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  );
};

export default App;
