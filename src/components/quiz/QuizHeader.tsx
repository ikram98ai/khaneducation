import { Button } from "@/components/ui/button";
import { ArrowLeft, Clock, CheckCircle, AlertCircle } from "lucide-react";
import { Quiz } from "@/types/api";
interface QuizHeaderProps {
  isSubmitting: boolean;
  elapsedTime: number;
  quizStarted: boolean;
  quiz: Quiz;
  answeredCount?: number;
}
// Header Component
const QuizHeader = ({
  isSubmitting,
  elapsedTime,
  quizStarted,
  quiz,
  answeredCount,
}: QuizHeaderProps) => {
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

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  return (
    <div className="py-4">
      <div className="max-w-6xl mx-auto px-4 md:px-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button
              variant="link"
              onClick={onBack}
              className="hover:font-bold px-0 py-0"
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
                  {answeredCount}/{quiz.quiz_questions.length}
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
          <div className="mt-4 p-3 bg-red-500/50 dark:bg-red-800/20 rounded-lg border dark:border-red-700/30 border-red-300/30">
            <div className="flex items-center gap-2 text-white dark:text-red-300">
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
};

export default QuizHeader;
