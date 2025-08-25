import { useAuthStore } from "@/stores/authStore";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoute = () => {
  const { profile, isLoading, isAuthenticated } = useAuthStore();

  if (isLoading) {
    return <div>Loading...</div>; // Or a spinner
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // if (profile.user.role==='student' && !profile?.student_profile) {
  //   return <Navigate to="/profile-setup" replace />;
  // }

  return <Outlet />;
};

export default ProtectedRoute;
