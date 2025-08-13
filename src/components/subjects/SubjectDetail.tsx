import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {  useSubjectDetail } from "@/hooks/useApiQueries";
import { Link, useParams } from "react-router-dom";
import { AIAssistant } from "../learning/AIAssistant";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";
import { Navbar } from "../navigation/Navbar";

export const SubjectDetail = () => {
  const { subjectId } = useParams();
  const {
    data: subject,
    isLoading: isSubjectLoading,
    isError: isSubjectError,
  } = useSubjectDetail(subjectId);

  const onBack = () => {
    window.history.back();
  };

  if (isSubjectLoading) {
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

  if (isSubjectError || !subject) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5 p-6 flex items-center justify-center">
        <Alert variant="destructive" className="max-w-lg">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Error Loading Subject</AlertTitle>
          <AlertDescription>
            There was a problem fetching the details for this subject. Please
            try again later.
            <Button onClick={onBack} variant="link" className="p-0 h-auto mt-2">
              Go Back
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5">
      {/* Header */}
      <Navbar />
      
      <div className="py-8">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <Button
          variant="link"
            onClick={onBack}
            className="px-0 py-0 hover:font-bold mb-4"
          >
            ← Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold mb-2">{subject.name}</h1>
          <p className="mb-4">{subject.description}</p>
          <div className="flex items-center gap-3">
            <Badge className="border-white/30">
              GR{subject.grade_level}
            </Badge>
           {subject.lessons && <Badge className="border-white/30">
              {subject.lessons[0].language}
            </Badge>}
            <span className="">
              • {subject.total_lessons} Lessons
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Units Sidebar */}
          <div className="col-span-1 lg:col-span-2">
            {/* Progress Overview */}
            <Card className="shadow-soft my-6">
              <CardHeader>
                <CardTitle>Your Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Overall Progress</span>
                      <span>
                        {subject.progress||0}%
                      </span>
                    </div>
                    <Progress
                      value={(subject.progress)||0}
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {subject.completed_lessons} of {subject.total_lessons}{" "}
                    lessons completed
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Lessons Content */}
          {subject.lessons
            .sort((a, b) => a.order_in_subject - b.order_in_subject)
            .map((lesson, index) => (
            <Link
              to={`/subjects/${subject.id}/lessons/${lesson.id}`}
              key={lesson.id}
              className="col-span-1"
            >
              <Card
                className="shadow-soft hover:shadow-medium transition-all duration-200 cursor-pointer"
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                            lesson.progress === 100
                              ? "bg-success text-success-foreground"
                              : lesson.progress > 0
                              ? "bg-warning text-warning-foreground"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {lesson.progress === 100 ? "✓" : lesson.order_in_subject}
                        </div>
                        <h3 className="text-lg font-semibold">
                          {lesson.title}
                        </h3>
                      </div>

                      <p className="text-muted-foreground mb-4 ml-11">
                        {lesson.content.slice(0, 50)}
                      </p>

                      {/* <div className="flex items-center gap-4 mb-3 ml-11">
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <span>⏱️</span>
                              <span>{lesson.duration}</span>
                            </div>
                          </div> */}

                      {lesson.progress >= 0 && (
                        <div className="ml-11">
                          <div className="flex justify-between text-sm mb-1">
                            <span>Progress</span>
                            <span>{lesson.progress||0}%</span>
                          </div>
                          <Progress
                            value={lesson.progress||0}
                            className="w-full max-w-xs"
                          />
                        </div>
                      )}
                    </div>

                    <Button
                      variant={
                        lesson.progress === 100
                          ? "secondary"
                          : lesson.progress > 0
                          ? "outline"
                          : "default"
                      }
                      size="sm"
                    >
                      {lesson.progress === 100
                        ? "Review"
                        : lesson.progress > 0
                        ? "Continue"
                        : "Start"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
      <AIAssistant subject_id={subject.id} subject={subject.name} />
    </div>
  );
};
