import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useQuizAttempts,
  usePracticeTasks,
  useSubject,
  useLesson,
} from "@/hooks/useApiQueries";
import { useNavigate, useParams } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";
import { AIAssistant } from "../learning/AIAssistant";

export const LessonDetail = () => {
  const navigate = useNavigate()
  const { subjectId, lessonId } = useParams();

  const {
    data: subject,
    isLoading: isSubjectLoading,
    isError: isSubjectError,
  } = useSubject(subjectId);
  const {
    data: lesson,
    isLoading: isLessonLoading,
    isError: isLessonError,
  } = useLesson(lessonId);

  const [activeTab, setActiveTab] = useState("content");

  const onBack = () => {
    window.history.back();
  };

  const startQuiz = () => {
    navigate(`/lessons/${lessonId}/quiz/`, { replace: true })
  };

  const {
    data: quizAttempts,
    isLoading: isAttemptsLoading,
    isError: isAttemptsError,
  } = useQuizAttempts(lesson?.id);
  const {
    data: practiceTasks = [],
    isLoading: isTasksLoading,
    isError: isTasksError,
  } = usePracticeTasks(lesson?.id);


  if (isSubjectLoading || isLessonLoading) {
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

  if (isSubjectError || isLessonError || !subject || !lesson) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5 p-6 flex items-center justify-center">
        <Alert variant="destructive" className="max-w-lg">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Error Loading Lesson</AlertTitle>
          <AlertDescription>
            There was a problem fetching the details for this lesson. Please try
            again later.
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
      <div className="bg-gradient-primary text-white px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-white hover:bg-white/20 mb-4"
          >
            ← Back to {subject.name}
          </Button>
          <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
          <div className="flex items-center gap-3">
            <span className="text-blue-100">
              • Progress: {lesson.progress || 0}%
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="content">📖 Content</TabsTrigger>
            <TabsTrigger value="practice">✏️ Practice</TabsTrigger>
            <TabsTrigger value="quiz">🎯 Quiz</TabsTrigger>
          </TabsList>

          <TabsContent value="content" className="mt-6">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>Lesson Content</CardTitle>
                <CardDescription>Learn the core concepts</CardDescription>
              </CardHeader>
              <CardContent className="prose max-w-none">
                <div
                  dangerouslySetInnerHTML={{
                    __html: lesson.content,
                  }}
                />
                <Button variant="gradient" className="mt-6">
                  Mark as Complete
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="practice" className="mt-6">
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Practice Problems</h2>
              {isTasksLoading ? (
                <p>Loading practice problems...</p>
              ) : isTasksError ? (
                <p>Error loading practice problems.</p>
              ) : (
                practiceTasks.map((task, index) => (
                  <Card key={task.id} className="shadow-soft">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">
                          Problem {index + 1}
                        </CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="mb-4">{task.content}</p>
                      {/* <details className="cursor-pointer">
                        <summary className="text-primary hover:underline">
                          Show Solution
                        </summary>
                        <div className="mt-2 p-3 bg-muted/50 rounded">
                          <strong>Solution:</strong> {task.solution}
                        </div>
                      </details> */}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="quiz" className="mt-6">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>Knowledge Check Quiz</CardTitle>
                <CardDescription>
                  Test your understanding of the lesson content.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="gradient"
                  onClick={startQuiz}
                  size="lg"
                  className="w-full"
                >
                  Start New Quiz
                </Button>
              </CardContent>
            </Card>

            <div className="mt-8">
              <h3 className="text-lg font-bold mb-4">Your Quiz History</h3>
              {isAttemptsLoading ? (
                <p>Loading history...</p>
              ) : isAttemptsError ? (
                <p>Could not load history.</p>
              ) : quizAttempts && quizAttempts.length > 0 ? (
                <div className="space-y-4">
                  {quizAttempts.map((attempt) => (
                    <Card key={attempt.id} className="shadow-soft">
                      <CardContent className="p-4 flex items-center justify-between">
                        <div>
                          <p className="font-semibold">
                            Quiz Attempt on{" "}
                            {new Date(attempt.start_time).toLocaleString()}
                          </p>

                          <p
                            className="text-sm"
                          >
                            Quiz Version • {attempt.quiz_version}

                          </p> 
                          <p
                            className={`text-sm ${
                              attempt.passed
                                ? "text-green-500"
                                : "text-red-500"
                            }`}
                          >
                            {attempt.passed ? "Passed" : "Failed"} • Score:{" "}
                            {attempt.score}%
                          </p>
                        </div>
                        <Button variant="outline" size="sm">
                          Review
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p>You haven't attempted any quizzes for this lesson yet.</p>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
      <AIAssistant subject={subject.name} lesson={lesson.title} />
    </div>
  )
}
