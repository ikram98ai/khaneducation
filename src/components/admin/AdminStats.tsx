import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAdminDashboard } from "@/hooks/useApiQueries";
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  BookOpen, 
  GraduationCap, 
  ClipboardCheck,
  Star,
  Award,
  Clock,
  Target
} from "lucide-react";

export const AdminStats = () => {
  const { data: dashboardData, isLoading, error } = useAdminDashboard();

  // Mock analytics data - in real app, this would come from API
  const mockAnalytics = {
    userGrowth: 15.3,
    completionRate: 78.5,
    averageScore: 82.1,
    activeToday: 342,
    topSubjects: [
      { name: "Mathematics", students: 156, completion: 85 },
      { name: "Science", students: 134, completion: 78 },
      { name: "History", students: 98, completion: 72 },
      { name: "English", students: 87, completion: 91 },
    ],
    recentActivity: [
      { action: "New user registered", user: "john.doe@example.com", time: "2 minutes ago" },
      { action: "Quiz completed", user: "jane.smith@example.com", time: "5 minutes ago" },
      { action: "Lesson verified", user: "admin", time: "10 minutes ago" },
      { action: "Subject created", user: "admin", time: "1 hour ago" },
    ]
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load analytics data. Please try again later.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Analytics & Statistics</h2>
        <p className="text-muted-foreground">
          Monitor platform performance and user engagement
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-green-500 dark:border-l-green-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-green-600 dark:text-green-400 font-medium flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              User Growth
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-green-700 dark:text-green-300">
              +{mockAnalytics.userGrowth}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-green-600 dark:text-green-400">
              This month vs last month
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500 dark:border-l-blue-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-blue-600 dark:text-blue-400 font-medium flex items-center">
              <Target className="w-4 h-4 mr-1" />
              Completion Rate
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-blue-700 dark:text-blue-300">
              {mockAnalytics.completionRate}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-blue-600 dark:text-blue-400">
              Average lesson completion
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500 dark:border-l-purple-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-purple-600 dark:text-purple-400 font-medium flex items-center">
              <Star className="w-4 h-4 mr-1" />
              Average Score
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-purple-700 dark:text-purple-300">
              {mockAnalytics.averageScore}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-purple-600 dark:text-purple-400">
              Across all quizzes
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500 dark:border-l-orange-600">
          <CardHeader className="pb-2">
            <CardDescription className="text-orange-600 dark:text-orange-400 font-medium flex items-center">
              <Users className="w-4 h-4 mr-1" />
              Active Today
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-orange-700 dark:text-orange-300">
              {mockAnalytics.activeToday}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-orange-600 dark:text-orange-400">
              Students online today
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performing Subjects */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Award className="w-5 h-5 mr-2 text-yellow-500 dark:text-yellow-400" />
              Top Performing Subjects
            </CardTitle>
            <CardDescription>
              Subjects with highest student engagement
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockAnalytics.topSubjects.map((subject, index) => (
              <div key={subject.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Badge variant="outline" className="mr-2">
                      #{index + 1}
                    </Badge>
                    <span className="font-medium">{subject.name}</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {subject.students} students
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Progress value={subject.completion} className="flex-1" />
                  <span className="text-sm font-medium">{subject.completion}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="w-5 h-5 mr-2 text-blue-500 dark:text-blue-400" />
              Recent Activity
            </CardTitle>
            <CardDescription>
              Latest system events and user actions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockAnalytics.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                <div className="w-2 h-2 bg-green-500 dark:bg-green-600 rounded-full mt-2 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{activity.action}</p>
                  <p className="text-sm text-muted-foreground">{activity.user}</p>
                </div>
                <div className="text-xs text-muted-foreground flex-shrink-0">
                  {activity.time}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">System Resources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Database Usage</span>
                <span>68%</span>
              </div>
              <Progress value={68} />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>API Requests</span>
                <span>45%</span>
              </div>
              <Progress value={45} />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Storage Used</span>
                <span>23%</span>
              </div>
              <Progress value={23} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Content Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <BookOpen className="w-4 h-4 mr-2 text-primary" />
                <span className="text-sm">Total Subjects</span>
              </div>
              <Badge variant="secondary">{dashboardData?.total_subjects || 0}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <GraduationCap className="w-4 h-4 mr-2 text-primary" />
                <span className="text-sm">Total Lessons</span>
              </div>
              <Badge variant="secondary">{dashboardData?.total_lessons || 0}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <ClipboardCheck className="w-4 h-4 mr-2 text-primary" />
                <span className="text-sm">Total Quizzes</span>
              </div>
              <Badge variant="secondary">{dashboardData?.total_quizzes || 0}</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">User Distribution</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 dark:bg-blue-600 rounded-full mr-2" />
                <span className="text-sm">Students</span>
              </div>
              <Badge variant="secondary">89%</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 dark:bg-green-600 rounded-full mr-2" />
                <span className="text-sm">Instructors</span>
              </div>
              <Badge variant="secondary">9%</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 dark:bg-red-600 rounded-full mr-2" />
                <span className="text-sm">Admins</span>
              </div>
              <Badge variant="secondary">2%</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};