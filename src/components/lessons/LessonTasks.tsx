import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePracticeTasks } from "@/hooks/useApiQueries";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";
import MarkdownViewer from "../mdviewer/MarkdownViewer";

export const LessonTasks = ({ lessonId }: { lessonId: string }) => {
  const {
    data: practiceTasks = [],
    isLoading: isTasksLoading,
    isError: isTasksError,
  } = usePracticeTasks(lessonId);

  if (isTasksLoading) {
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

  if (isTasksError || !practiceTasks) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-primary/5 p-6 flex items-center justify-center">
        <Alert variant="destructive" className="max-w-lg">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Error Loading Lesson</AlertTitle>
          <AlertDescription>
            There was a problem fetching the tasks for this lesson. Please try
            again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        <h2 className="text-xl font-bold">Practice Problems</h2>
        {isTasksLoading ? (
          <p>Loading practice problems...</p>
        ) : isTasksError ? (
          <p>Error loading practice problems.</p>
        ) : (
          practiceTasks.map((task, index) => (
            <Card key={task.id} className="shadow-soft text-wrap">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Problem {index + 1}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="text-wrap">
                <MarkdownViewer markdown={task.content} />
                <details className="cursor-pointer">
                  <summary className="text-primary hover:underline">
                    Show Solution
                  </summary>
                  <div className="mt-2 p-3 bg-muted/50 rounded">
                    <strong>Solution:</strong> {task.solution}
                  </div>
                </details>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </>
  );
};
