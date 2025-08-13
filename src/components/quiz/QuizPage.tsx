import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useQuiz, useSubmitQuiz } from "@/hooks/useApiQueries";
import { useParams } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Terminal,
  ArrowLeft,
  Clock,
  CheckCircle,
  AlertCircle,
  Brain,
  Trophy,
} from "lucide-react";
import { Navbar } from "../navigation/Navbar";

export const QuizPage = () => {
  const { lessonId } = useParams();

  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<
    Record<string, string>
  >({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  const onBack = () => {
    if (
      quizStarted &&
      !window.confirm(
        "Are you sure you want to leave? Your quiz will be submitted automatically."
      )
    ) {
      return;
    }
    window.history.back();
  };

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (quizStarted && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [quizStarted, startTime]);

  // Handle page unload
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (quizStarted) {
        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [quizStarted]);

  const {
    data: quiz,
    isLoading: isQuizLoading,
    isError: isQuizError,
  } = useQuiz(lessonId, {
    enabled: quizStarted,
  });

  const submitQuizMutation = useSubmitQuiz();

  const handleStartQuiz = () => {
    setQuizStarted(true);
    setStartTime(new Date());
  };

  const handleQuizAnswer = (questionId: string, student_answer: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: student_answer,
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < quiz.quiz_questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      handleSubmitQuiz();
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    setIsSubmitting(true);
    const responses = Object.entries(selectedAnswers).map(
      ([question_id, student_answer]) => ({
        question_id,
        student_answer,
      })
    );

    submitQuizMutation.mutate(
      { quiz_id: quiz.id, responses },
      {
        onSuccess: () => {
          setQuizStarted(false);
          setCurrentQuestion(0);
          setSelectedAnswers({});
          setStartTime(null);
          setElapsedTime(0);
        },
        onSettled: () => {
          setIsSubmitting(false);
        },
      }
    );
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  const getAnsweredCount = () => {
    return Object.keys(selectedAnswers).length;
  };

  // Header Component
  const QuizHeader = () => (
    <div className="px-4 sm:px-6 py-4">
      <Navbar />
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button
              variant="link"
              onClick={onBack}
              className="hover:font-bold px-2 sm:px-4"
              disabled={isSubmitting}
            >
              <ArrowLeft className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Back to Lesson</span>
            </Button>
          </div>

          {quizStarted && quiz && (
            <div className="flex items-center justify-between w-full sm:w-auto gap-4 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>
                  {getAnsweredCount()}/{quiz.quiz_questions.length}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>{formatTime(elapsedTime)}</span>
              </div>
            </div>
          )}
        </div>

        {quizStarted && (
          <div className="mt-4 p-3 bg-red-500/20 dark:bg-red-800/20 rounded-lg border dark:border-red-700/30 border-red-300/30">
            <div className="flex items-center gap-2 text-red-100 dark:text-red-300">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <p className="text-xs sm:text-sm">
                Warning: Leaving this page will automatically submit your quiz.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Loading state
  if (isQuizLoading) {
    return (
      <div className="min-h-screen">
        <QuizHeader />
        <div className="max-w-4xl mx-auto px-6 py-8">
          <Card className="shadow-lg">
            <CardHeader>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-6 w-full" />
              <div className="space-y-3">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Error state
  if (isQuizError) {
    return (
      <div className="min-h-screen">
        <QuizHeader />
        <div className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-center">
          <Alert variant="destructive" className="max-w-lg shadow-lg">
            <Terminal className="h-4 w-4" />
            <AlertTitle>Error Loading Quiz</AlertTitle>
            <AlertDescription className="mt-2">
              There was a problem fetching the quiz. Please check your
              connection and try again.
              <Button
                onClick={onBack}
                variant="link"
                className="p-0 h-auto mt-3 text-red-600 dark:text-red-400"
              >
                Go Back to Lesson
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  // Quiz start screen
  if (!quizStarted) {
    return (
      <div className="min-h-screen">
        <QuizHeader />
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 dark:bg-blue-900 rounded-full mb-4">
              <Trophy className="h-10 w-10 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Ready to Test Your Knowledge?
            </h2>
            <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Take this quiz to assess your understanding of the lesson
              material. You'll need to score 70% or higher to pass.
            </p>
          </div>

          <Card className="shadow-lg max-w-2xl mx-auto">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center gap-2">
                <Brain className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                Knowledge Check Quiz
              </CardTitle>
              <CardDescription>
                Test your understanding of the lesson concepts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-sm">Passing Score</p>
                    <p className="text-xs text-gray-600 dark:text-gray-300">
                      70% or higher required
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <Clock className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-sm">Time Tracking</p>
                    <p className="text-xs text-gray-600 dark:text-gray-300">
                      Monitor your progress
                    </p>
                  </div>
                </div>
              </div>

              <Alert className="border-amber-200 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20">
                <AlertCircle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                <AlertTitle className="text-amber-800 dark:text-amber-200">
                  Important Notice
                </AlertTitle>
                <AlertDescription className="text-amber-700 dark:text-amber-300">
                  Once you start the quiz, leaving this page will automatically
                  submit your answers. Make sure you're ready to complete it in
                  one session.
                </AlertDescription>
              </Alert>

              <Button
                onClick={handleStartQuiz}
                size="lg"
                className="w-full bg-gradient-primary text-white font-medium py-6"
              >
                <Brain className="h-5 w-5 mr-2" />
                Start Quiz
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // No quiz available
  if (!quiz) {
    return (
      <div className="min-h-screen">
        <QuizHeader />
        <div className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-center">
          <Alert className="max-w-lg shadow-lg">
            <Terminal className="h-4 w-4" />
            <AlertTitle>No Quiz Available</AlertTitle>
            <AlertDescription className="mt-2">
              There is no quiz available for this lesson at the moment.
              <Button
                onClick={onBack}
                variant="link"
                className="p-0 h-auto mt-3"
              >
                Return to Lesson
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  // Empty quiz
  if (quiz.quiz_questions.length === 0) {
    return (
      <div className="min-h-screen">
        <QuizHeader />
        <div className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-center">
          <Alert className="max-w-lg shadow-lg">
            <Terminal className="h-4 w-4" />
            <AlertTitle>No Questions Available</AlertTitle>
            <AlertDescription className="mt-2">
              This quiz doesn't have any questions yet. Please check back later.
              <Button
                onClick={onBack}
                variant="link"
                className="p-0 h-auto mt-3"
              >
                Return to Lesson
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  // Quiz interface
  return (
    <div className="min-h-screen">
      <QuizHeader />

      <div className="max-w-4xl mx-auto px-6 py-8">
        <Card className="shadow-lg">
          <CardHeader>
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-xl">
                Question {currentQuestion + 1} of {quiz.quiz_questions.length}
              </CardTitle>
              <Progress
                value={
                  ((currentQuestion + 1) / quiz.quiz_questions.length) * 100
                }
                className="w-40"
              />
            </div>
            <CardDescription>
              Choose the best answer for the following question
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="space-y-6">
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 leading-relaxed">
                  {quiz.quiz_questions[currentQuestion].question_text}
                </h3>
              </div>

              <div className="space-y-3">
                {quiz.quiz_questions[currentQuestion].options?.map(
                  (option, index) => (
                    <label
                      key={index}
                      className={`flex items-start p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
                        selectedAnswers[
                          quiz.quiz_questions[currentQuestion].question_id
                        ] === option
                          ? "border-blue-500 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20 shadow-md"
                          : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
                      }`}
                    >
                      <input
                        type="radio"
                        name={`question-${currentQuestion}`}
                        value={option}
                        checked={
                          selectedAnswers[
                            quiz.quiz_questions[currentQuestion].question_id
                          ] === option
                        }
                        onChange={() =>
                          handleQuizAnswer(
                            quiz.quiz_questions[currentQuestion].question_id,
                            option
                          )
                        }
                        className="mt-0.5 mr-4 h-4 w-4 text-blue-600 dark:text-blue-400"
                      />
                      <span className="text-gray-900 dark:text-gray-100 leading-relaxed">
                        {option}
                      </span>
                    </label>
                  )
                )}
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between pt-6 border-t gap-4 sm:gap-0">
                <Button
                  variant="outline"
                  onClick={previousQuestion}
                  disabled={currentQuestion === 0 || isSubmitting}
                  className="w-full sm:w-auto flex items-center gap-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Previous
                </Button>

                <div className="text-sm text-gray-500 dark:text-gray-400 order-first sm:order-none">
                  {getAnsweredCount()} of {quiz.quiz_questions.length} answered
                </div>

                <Button
                  onClick={nextQuestion}
                  disabled={
                    !selectedAnswers[
                      quiz.quiz_questions[currentQuestion].question_id
                    ] || isSubmitting
                  }
                  className="w-full sm:w-auto flex items-center gap-2 bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-800"
                >
                  {isSubmitting
                    ? "Submitting..."
                    : currentQuestion === quiz.quiz_questions.length - 1
                    ? "Finish Quiz"
                    : "Next Question"}
                  {!isSubmitting &&
                    currentQuestion < quiz.quiz_questions.length - 1 && (
                      <ArrowLeft className="h-4 w-4 rotate-180" />
                    )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
