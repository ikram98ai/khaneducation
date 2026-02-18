import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { QuizAttemptOut } from "@/types/api";


export const QuizAttemptDetail = ({ attempt }: {attempt: QuizAttemptOut;}) => {
  return (
    <ScrollArea className="h-[calc(100vh-100px)] px-4 py-6">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <div>
              <p className="font-semibold">Score</p>
              <p>{attempt.score}%</p>
            </div>
            <div>
              <p className="font-semibold">Result</p>
              <p>{attempt.passed ? "Passed" : "Failed"}</p>
            </div>
            <div>
              <p className="font-semibold">Date</p>
              <p>{new Date(attempt.start_time).toLocaleString()}</p>
            </div>
            <div>
              <p className="font-semibold">Version</p>
              <p>{attempt.quiz_version}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{attempt.ai_feedback}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your Responses</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {attempt.responses.map((response, index) => {
              const isCorrect = response.student_answer === response.correct_answer;
              return (
                <div key={response.question_id} className="border-b pb-4">
                  <p className="font-semibold">Question {index + 1}</p>
                  <p>{response.question_text}</p>
                  <div className="mt-2">
                    <p className="text-sm">Your answer: {response.student_answer}</p>
                    <p className="text-sm">Correct answer: {response.correct_answer}</p>
                    <Badge variant={isCorrect ? "default" : "destructive"}>
                      {isCorrect ? "Correct" : "Incorrect"}
                    </Badge>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>
    </ScrollArea>
  );
};
