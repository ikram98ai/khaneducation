import { useAuthStore } from "@/stores/authStore";
import { Navigate, Outlet } from "react-router-dom";
import { useStudentProfile } from "@/hooks/useApiQueries";
import { useEffect } from "react";

const ProtectedRoute = () => {
  const { profile, isLoading, setProfile, isAuthenticated } = useAuthStore();
  const { data: studentProfile, isLoading: isProfileLoading, error: profileError } = useStudentProfile();

  // Effect to sync profile from API if it's missing from store
  useEffect(() => {
    if (isAuthenticated && !profile?.student && studentProfile && !isProfileLoading) {
      console.log("Profile found in API but missing from store, syncing...");
      setProfile(studentProfile);
    }
  }, [isAuthenticated, profile?.student, studentProfile, isProfileLoading, setProfile]);

  // Show loading while auth is loading OR while we're fetching profile
  if (isLoading || (isAuthenticated && !profile?.student && isProfileLoading)) {
    return <div>Loading...</div>; // Or a spinner, or null
  }
  
  // If not authenticated, redirect to login
  if (!isAuthenticated || !profile) {
    return <Navigate to="/login" replace />;
  }

  // If authenticated but no student profile (and we're not loading), redirect to profile setup
  if (!profile.student && !isProfileLoading) {
    // Only redirect if we're sure there's no profile (API call completed)
    if (profileError || (!isProfileLoading && !studentProfile)) {
      return <Navigate to="/profile-setup" replace />;
    }
  }

  // If user is logged in and has a profile, allow access to the route
  return <Outlet />;
};

export default ProtectedRoute;