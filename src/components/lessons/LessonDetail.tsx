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
import { useSubject, useLesson } from "@/hooks/useApiQueries";
import { useParams } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";
import { AIAssistant } from "../learning/AIAssistant";
import MarkdownViewer from "../mdviewer/MarkdownViewer";
import { Badge } from "../ui/badge";
import { QuizAttempts } from "./QuizAttempts";
import { LessonTasks } from "./LessonTasks";
import { Navbar } from "../navigation/Navbar";

export const LessonDetail = () => {
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
    <div className="bg-gradient-to-br from-background via-accent/5 to-primary/5">
      <Navbar />
      {/* Header */}
      <div className="py-8">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <Button variant="link" onClick={onBack} className="px-0 py-0 hover:font-bold mb-4">
            ← Back to {subject.name}
          </Button>
          <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
          <div className="flex items-center gap-3">
            <Badge className=" border-white/30">GR{subject.grade_level}</Badge>
            <Badge className=" border-white/30">{lesson.language}</Badge>
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
            <Card className="shadow-soft text-wrap">
              <CardHeader>
                <CardTitle>Lesson Content</CardTitle>
                <CardDescription>Learn the core concepts</CardDescription>
              </CardHeader>
              <CardContent className="prose max-w-none">
                <MarkdownViewer markdown={lesson.content} />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="practice" className="mt-6">
            <LessonTasks lessonId={lessonId} />
          </TabsContent>

          <TabsContent value="quiz" className="mt-6">
            <QuizAttempts lessonId={lessonId} />
          </TabsContent>
        </Tabs>
      </div>
      <AIAssistant
        subject_id={subject.id}
        subject={subject.name}
        lesson_id={lesson.id}
        lesson={lesson.title}
      />
    </div>
  );
};
