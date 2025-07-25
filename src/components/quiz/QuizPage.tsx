import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  useQuiz,
  useSubmitQuiz,
} from "@/hooks/useApiQueries";
import { useParams } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";

export const QuizPage = () => {
  const { lessonId } = useParams();

  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<
    Record<string, string>
  >({});

  const onBack = () => {
    window.history.back();
  };

  const {
    data: quiz,
    isLoading: isQuizLoading,
    isError: isQuizError,
  } = useQuiz(lessonId);

  const submitQuizMutation = useSubmitQuiz();

  const handleQuizAnswer = (questionId: string, answer: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      const responses = Object.entries(selectedAnswers).map(
        ([question_id, answer]) => ({
          question_id,
          answer,
        })
      );

      submitQuizMutation.mutate(
        { quiz_id: quiz.id, responses },
        {
          onSuccess: () => {
            setQuizStarted(false);
            setCurrentQuestion(0);
            setSelectedAnswers({});
          },
        }
      );
    }
  };

  if (isQuizLoading) {
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

  if (isQuizError || !quiz) {
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
      {/* <div className="bg-gradient-primary text-white px-6 py-8">
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
      </div> */}

      <div className="max-w-4xl mx-auto px-6 py-8">
          {isQuizLoading ? (
            <p>Loading quiz...</p>
          ) : isQuizError ? (
            <p>Error loading quiz.</p>
          ) : !quiz ? (
            <p>No quiz available for this lesson.</p>
          ) : !quizStarted ? (
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>Knowledge Check Quiz</CardTitle>
                <CardDescription>
                  Test your understanding with {quiz.questions.length} questions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="text-2xl">🧠</div>
                    <div>
                      <p className="font-medium">
                        Ready to test your knowledge?
                      </p>
                      <p className="text-sm text-muted-foreground">
                        You need 70% or higher to pass
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="gradient"
                    onClick={() => setQuizStarted(true)}
                    size="lg"
                  >
                    Start Quiz
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="shadow-soft">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>
                    Question {currentQuestion + 1} of {quiz.questions.length}
                  </CardTitle>
                  <Progress
                    value={
                      ((currentQuestion + 1) / quiz.questions.length) * 100
                    }
                    className="w-32"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <h3 className="text-lg font-medium">
                    {quiz.questions[currentQuestion].question_text}
                  </h3>

                  <div className="space-y-3">
                    {[
                      quiz.questions[currentQuestion].option_a,
                      quiz.questions[currentQuestion].option_b,
                      quiz.questions[currentQuestion].option_c,
                      quiz.questions[currentQuestion].option_d,
                    ].map((option, index) => (
                      <label
                        key={index}
                        className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
                          selectedAnswers[
                            quiz.questions[currentQuestion].id
                          ] === option
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-muted/50"
                        }`}
                      >
                        <input
                          type="radio"
                          name={`question-${currentQuestion}`}
                          value={option}
                          checked={
                            selectedAnswers[
                              quiz.questions[currentQuestion].id
                            ] === option
                          }
                          onChange={() =>
                            handleQuizAnswer(
                              quiz.questions[currentQuestion].id,
                              option
                            )
                          }
                          className="mr-3"
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>

                  <Button
                    onClick={nextQuestion}
                    disabled={
                      !selectedAnswers[quiz.questions[currentQuestion].id]
                    }
                    className="w-full"
                  >
                    {currentQuestion === quiz.questions.length - 1
                      ? "Finish Quiz"
                      : "Next Question"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
      </div>
    </div>
  );
};
