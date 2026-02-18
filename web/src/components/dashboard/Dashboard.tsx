import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useStudentDashboard } from "@/hooks/useApiQueries";
import { Link } from "react-router-dom";
import { Skeleton } from "../ui/skeleton";
import { Calculator, Atom, FlaskConical, Dna, Code, Terminal } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";

const subjectIcons: { [key: string]: JSX.Element } = {
  Mathematics: <Calculator className="w-6 h-6 text-primary" />,
  Physics: <Atom className="w-6 h-6 text-primary" />,
  Chemistry: <FlaskConical className="w-6 h-6 text-primary" />,
  Biology: <Dna className="w-6 h-6 text-primary" />,
  "Computer Science": <Code className="w-6 h-6 text-primary" />,
};

 const onRefresh = () => {
    window.location.reload();
  };
export const Dashboard = () => {
  const { data: dashboardData, isLoading, error } = useStudentDashboard();

  if (isLoading) {
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


  if (error) {
      return (
        <div className="min-h-screen">
          <div className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-center">
            <Alert variant="destructive" className="max-w-lg shadow-lg">
              <Terminal className="h-4 w-4" />
              <AlertTitle>Error Loading Dashboard</AlertTitle>
              <AlertDescription className="mt-2">
                There was a problem  fetching the dashboard data. Please check your connection and try again.
                <Button onClick={onRefresh} variant="link" className="p-0 h-auto mt-3 text-red-600">
                  Refresh the page.
                </Button>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      );
    }

  const { enrollments: enrolledSubjects, stats } = dashboardData;

  const { completed_lessons, total_lessons, avg_score, streak } = stats;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5">
      {/* Header */}

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Stats Overview with staggered animations */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card
            variant="elevated"
            className="animate-spring-in"
            style={{ animationDelay: "0.1s" }}
          >
            <CardContent className="p-4 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground md:text-sm">
                    Progress
                  </p>
                  <p className="text-lg font-bold md:text-2xl">
                    {Math.round((completed_lessons / total_lessons) * 100) || 0}
                    %
                  </p>
                </div>
                <div className="text-xl md:text-2xl animate-float">📈</div>
              </div>
              <Progress
                value={(completed_lessons / total_lessons) * 100 || 0}
                className="mt-2 hidden md:block"
              />
            </CardContent>
          </Card>

          <Card
            variant="elevated"
            className="animate-spring-in"
            style={{ animationDelay: "0.2s" }}
          >
            <CardContent className="p-4 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground md:text-sm">
                    Avg Score
                  </p>
                  <p className="text-lg font-bold text-success md:text-2xl">
                    {(avg_score.toFixed(0))}%
                  </p>
                </div>
                <div
                  className="text-xl md:text-2xl animate-float"
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
            <CardContent className="p-4 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground md:text-sm">
                    Lessons
                  </p>
                  <p className="text-lg font-bold md:text-2xl">
                    {completed_lessons}/{total_lessons}
                  </p>
                </div>
                <div
                  className="text-xl md:text-2xl animate-float"
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
            <CardContent className="p-4 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground md:text-sm">
                    Streak
                  </p>
                  <p className="text-lg font-bold text-warning md:text-2xl">
                    {streak} days
                  </p>
                </div>
                <div className="text-xl md:text-2xl">🔥</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          {/* Enrolled Subjects */}
          <h2 className="text-2xl font-bold mb-6">Your Subjects</h2>
          <div
            className="animate-slide-up-fade col-span-1 grid grid-cols-1 lg:grid-cols-2 gap-4"
            style={{ animationDelay: "0.6s" }}
          >
            {enrolledSubjects.map((subject, index) => (
              <Link
                to={`/subjects/${subject.id}`}
                key={subject.id}
                className=""
              >
                <Card
                  key={subject.id}
                  variant="interactive"
                  className="animate-spring-in mb-4"
                  style={{ animationDelay: `${0.8 + index * 0.1}s` }}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {subjectIcons[subject.name]}
                          <h3 className="text-lg font-semibold">
                            {subject.name}
                          </h3>
                        </div>
                        <p className="text-muted-foreground text-sm mb-3">
                          {subject.description}
                        </p>

                        <div className="flex items-center gap-2 mb-3">
                          <Badge variant="secondary">
                            Grade {subject.grade_level}
                          </Badge>
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
        </div>
      </div>
    </div>
  );
};
