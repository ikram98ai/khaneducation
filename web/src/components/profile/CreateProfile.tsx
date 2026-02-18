import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import {
  useCreateProfile,
  useLanguages,
  useStudentProfile,
} from "@/hooks/useApiQueries";
import { useNavigate } from "react-router-dom";
import { Skeleton } from "../ui/skeleton";
import { useAuthStore } from "@/stores/authStore";

const grades = [
  { code: "1", name: "Grade 1" },
  { code: "2", name: "Grade 2" },
  { code: "3", name: "Grade 3" },
  { code: "4", name: "Grade 4" },
  { code: "5", name: "Grade 5" },
  { code: "6", name: "Grade 6" },
  { code: "7", name: "Grade 7" },
  { code: "8", name: "Grade 8" },
  { code: "9", name: "Grade 9" },
  { code: "10", name: "Grade 10" },
  { code: "11", name: "Grade 11" },
  { code: "12", name: "Grade 12" },
];

export const CreateProfile = () => {
  const [formData, setFormData] = useState({
    language: "",
    current_grade: "",
  });

  const navigate = useNavigate();
  const { setProfile } = useAuthStore();
  const createProfileMutation = useCreateProfile();
  const {
    data: languages,
    isLoading: languagesLoading,
    error: languagesError,
  } = useLanguages();
  const {
    data: existingProfile,
    isLoading: profileLoading,
    error: profileError,
  } = useStudentProfile();

  // Check if profile already exists and redirect to dashboard
  useEffect(() => {
    if (existingProfile && existingProfile.student_profile) {
      setProfile(existingProfile);
      navigate("/dashboard", { replace: true });
    }
  }, [existingProfile, navigate, setProfile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.language || !formData.current_grade) {
      return;
    }

    try {
      const profile = await createProfileMutation.mutateAsync(formData);
      if (profile) {
        navigate("/dashboard");
      }
    } catch (error) {
      console.log(error);
      // Error handling is done in the mutation
    }
  };

  // Show loading while checking for existing profile or loading languages
  if (profileLoading || languagesLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5 p-6">
        <Skeleton className="h-10 w-48 mb-8" />
        <Skeleton className="h-16 w-full mb-4" />
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    );
  }

  // Handle error states
  if (languagesError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-accent/20 p-4">
        <Card className="shadow-large border-0">
          <CardContent className="text-center p-6">
            <p className="text-red-500 dark:text-red-400">
              Error loading languages. Please try again later.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-accent/20 p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-large border-0">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4">
              <img src="/logo.png" alt="khan education logo" />
            </div>
            <CardTitle className="text-2xl font-bold">
              Set Up Your Profile
            </CardTitle>
            <CardDescription>
              Tell us about your learning preferences
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="language">Preferred Language</Label>
                <Select
                  value={formData.language}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, language: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your language" />
                  </SelectTrigger>
                  <SelectContent>
                    {languages?.map((lang) => (
                      <SelectItem key={lang} value={lang}>
                        {lang}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="grade">Current Grade Level</Label>
                <Select
                  value={formData.current_grade}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, current_grade: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your grade" />
                  </SelectTrigger>
                  <SelectContent>
                    {grades.map((grade) => (
                      <SelectItem key={grade.code} value={grade.code}>
                        {grade.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>

            <CardContent>
              <Button
                type="submit"
                variant="gradient"
                size="lg"
                className="w-full"
                disabled={
                  !formData.language ||
                  !formData.current_grade ||
                  createProfileMutation.isPending
                }
              >
                {createProfileMutation.isPending
                  ? "Setting up..."
                  : "Complete Setup"}
              </Button>
            </CardContent>
          </form>
        </Card>
      </div>
    </div>
  );
};
