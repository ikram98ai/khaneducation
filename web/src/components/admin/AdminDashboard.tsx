import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAdminDashboard } from "@/hooks/useApiQueries";
import { Users, BookOpen, GraduationCap, ClipboardCheck, TrendingUp, Activity } from "lucide-react";
import { UserManagement } from "./UserManagement";
import { SubjectManagement } from "./SubjectManagement";
import { LessonManagement } from "./LessonManagement";
import { AdminStats } from "./AdminStats";
import { Navbar } from "../navigation/Navbar";

export const AdminDashboard = () => {
  const { data: dashboardData, isLoading, error } = useAdminDashboard();

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-8 w-16" />
              </CardHeader>
            </Card>
          ))}
        </div>
        
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertDescription>
            Failed to load admin dashboard. Please try again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Manage users, subjects, lessons, and monitor system activity
          </p>
        </div>
        <Badge variant="secondary" className="bg-gradient-to-r from-primary/10 to-primary/20">
          <Activity className="w-4 h-4 mr-1" />
          System Active
        </Badge>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-blue-500 dark:border-l-blue-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-blue-600 dark:text-blue-400 font-medium">Total Students</CardDescription>
            <CardTitle className="text-2xl font-bold text-blue-700 dark:text-blue-300">
              {dashboardData?.total_students || 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-sm text-blue-600 dark:text-blue-400">
              <Users className="w-4 h-4 mr-1" />
              Active Learners
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500 dark:border-l-green-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-green-600 dark:text-green-400 font-medium">Total Subjects</CardDescription>
            <CardTitle className="text-2xl font-bold text-green-700 dark:text-green-300">
              {dashboardData?.total_subjects || 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-sm text-green-600 dark:text-green-400">
              <BookOpen className="w-4 h-4 mr-1" />
              Subject Areas
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500 dark:border-l-purple-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-purple-600 dark:text-purple-400 font-medium">Total Lessons</CardDescription>
            <CardTitle className="text-2xl font-bold text-purple-700 dark:text-purple-300">
              {dashboardData?.total_lessons || 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-sm text-purple-600 dark:text-purple-400">
              <GraduationCap className="w-4 h-4 mr-1" />
              Learning Materials
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500 dark:border-l-orange-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-orange-600 dark:text-orange-400 font-medium">Total Quizzes</CardDescription>
            <CardTitle className="text-2xl font-bold text-orange-700 dark:text-orange-300">
              {dashboardData?.total_quizzes || 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-sm text-orange-600 dark:text-orange-400">
              <ClipboardCheck className="w-4 h-4 mr-1" />
              Assessments
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="subjects">Subjects</TabsTrigger>
          <TabsTrigger value="lessons">Lessons</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-500 dark:text-green-400" />
                  Recent Lessons
                </CardTitle>
                <CardDescription>
                  Latest lessons created in the system
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {dashboardData?.recent_lessons?.slice(0, 5).map((lesson) => (
                  <div key={lesson.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{lesson.title}</p>
                      <div className="text-sm text-muted-foreground">
                        Status: <Badge variant={lesson.status === 'verified' ? 'default' : 'secondary'}>
                          {lesson.status === 'verified' ? 'Verified' : 'Draft'}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(lesson.created_at).toLocaleDateString()}
                    </div>
                  </div>
                )) || (
                  <p className="text-muted-foreground">No recent lessons available</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-blue-500 dark:text-blue-400" />
                  Recent Quiz Attempts
                </CardTitle>
                <CardDescription>
                  Latest student quiz attempts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {dashboardData?.recent_attempts?.slice(0, 5).map((attempt) => (
                  <div key={attempt.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Student ID: {attempt.student_id}</p>
                      <p className="text-sm text-muted-foreground">
                        Score: <span className={`font-medium ${attempt.passed ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                          {Math.round(attempt.score)}%
                        </span>
                      </p>
                    </div>
                    <Badge variant={attempt.passed ? 'default' : 'destructive'}>
                      {attempt.passed ? 'Passed' : 'Failed'}
                    </Badge>
                  </div>
                )) || (
                  <p className="text-muted-foreground">No recent attempts available</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="users">
          <UserManagement />
        </TabsContent>

        <TabsContent value="subjects">
          <SubjectManagement />
        </TabsContent>

        <TabsContent value="lessons">
          <LessonManagement />
        </TabsContent>

        <TabsContent value="analytics">
          <AdminStats />
        </TabsContent>
      </Tabs>
    </div>
  );
};