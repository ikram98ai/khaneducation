import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { SmartSearch } from "@/components/search/SmartSearch";
import {
  useStudentDashboard,
  useStudentDashboardStatistics,
} from "@/hooks/useApiQueries";
import { Link } from "react-router-dom";
import { Navbar } from "../navigation/Navbar";
import { formatDistanceToNow } from "date-fns";
import { Skeleton } from "../ui/skeleton";

export const Dashboard = () => {
  const { data: dashboardData, isLoading, error } = useStudentDashboard();
  const {
    data: statistics,
    isLoading: statsLoading,
    error: statsError,
  } = useStudentDashboardStatistics();

  if (isLoading || statsLoading) {
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

  if (error || statsError) {
    return <div>Error loading dashboard data.</div>;
  }

  const { enrollments: enrolledSubjects, recent_attempts: recentAttempts } =
    dashboardData;

  const { completedLessons, totalLessons, avgScore, streak } = statistics;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5">
      {/* Header */}
      <Navbar />

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Smart Search */}
        {/* <div className="mb-8 flex justify-center">
          <SmartSearch
            onSelectResult={(result) => console.log("Selected:", result)}
          />
        </div> */}
        {/* Stats Overview with staggered animations */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card
            variant="elevated"
            className="animate-spring-in"
            style={{ animationDelay: "0.1s" }}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Progress</p>
                  <p className="text-2xl font-bold">
                    {Math.round((completedLessons / totalLessons) * 100) || 0}%
                  </p>
                </div>
                <div className="text-2xl animate-float">📈</div>
              </div>
              <Progress
                value={completedLessons / totalLessons || 0 * 100}
                className="mt-2"
              />
            </CardContent>
          </Card>

          <Card
            variant="elevated"
            className="animate-spring-in"
            style={{ animationDelay: "0.2s" }}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Score</p>
                  <p className="text-2xl font-bold text-success">{avgScore}%</p>
                </div>
                <div
                  className="text-2xl animate-float"
                  style={{ animationDelay: "0.5s" }}
                >
                  🎯
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            variant="elevated"
            className="animate-spring-in"
            style={{ animationDelay: "0.3s" }}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Lessons</p>
                  <p className="text-2xl font-bold">
                    {completedLessons}/{totalLessons}
                  </p>
                </div>
                <div
                  className="text-2xl animate-float"
                  style={{ animationDelay: "1s" }}
                >
                  📚
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            variant="floating"
            className="animate-spring-in"
            style={{ animationDelay: "0.4s" }}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Streak</p>
                  <p className="text-2xl font-bold text-warning">
                    {streak} days
                  </p>
                </div>
                <div className="text-2xl">🔥</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Enrolled Subjects */}
          <div
            className="animate-slide-up-fade"
            style={{ animationDelay: "0.6s" }}
          >
            <h2 className="text-2xl font-bold mb-6">Your Subjects</h2>
            {enrolledSubjects.map((subject, index) => (
              <Link to={`/subjects/${subject.id}`} key={subject.id}>
                <Card
                  key={subject.id}
                  variant="interactive"
                  className="animate-spring-in my-4"
                  style={{ animationDelay: `${0.8 + index * 0.1}s` }}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold mb-2">
                          {subject.name}
                        </h3>
                        <p className="text-muted-foreground text-sm mb-3">
                          {subject.description}
                        </p>

                        <div className="flex items-center gap-2 mb-3">
                          <Badge variant="secondary">
                            GR{subject.grade_level}
                          </Badge>
                          <Badge variant="outline">{subject.language}</Badge>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="text-sm text-muted-foreground">
                            Progress: {subject.progress || 0}% complete
                          </div>
                          <Button variant="glass" size="sm">
                            Continue Learning
                          </Button>
                        </div>

                        <Progress value={subject.progress} className="mt-2" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Recent Activity */}
          <div
            className="animate-slide-up-fade"
            style={{ animationDelay: "0.7s" }}
          >
            <h2 className="text-2xl font-bold mb-6">Recent Activity</h2>
            <Card
              variant="glass"
              className="animate-spring-in"
              style={{ animationDelay: "0.9s" }}
            >
              <CardContent className="p-6">
                <div className="space-y-4">
                  {recentAttempts.map((activity, index) => (
                    <div
                      key={activity.id}
                      className="flex items-center justify-between p-3 bg-surface-hover rounded-lg hover:bg-surface-pressed transition-all duration-300 animate-spring-in"
                      style={{ animationDelay: `${1.1 + index * 0.1}s` }}
                    >
                      <div>
                        <p className="font-medium">{activity.lesson_title}</p>
                        <p className="text-sm text-muted-foreground">
                          Quiz Version: {activity.quiz_version}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(activity.start_time))}{" "}
                          ago
                        </p>
                      </div>
                      <Badge
                        variant={
                          activity.score >= 90
                            ? "default"
                            : activity.score >= 80
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {activity.score}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            {/* <Card
              variant="floating"
              className="mt-6 animate-spring-in"
              style={{ animationDelay: "1.2s" }}
            >
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Jump back into your learning</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button variant="glass" className="w-full justify-start">
                    📝 Take a Practice Quiz
                  </Button>
                  <Button variant="glass" className="w-full justify-start">
                    📖 Review Past Lessons
                  </Button>
                  <Button variant="glass" className="w-full justify-start">
                    🎯 View Learning Goals
                  </Button>
                </div>
              </CardContent>
            </Card> */}
          </div>
        </div>

        {/* Progress Analytics */}
        {/* <div className="mt-12">
          <ProgressAnalytics user={user} enrollments={enrollments} />
        </div> */}
      </div>
    </div>
  );
};
