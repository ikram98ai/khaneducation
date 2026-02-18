import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Bot, CheckCircle, XCircle } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export interface Answer {
  text: string;
  isCorrect: boolean;
}

export interface QuizQuestion {
  question: string;
  answers: Answer[];
  subject: string;
}

export interface DailyQuiz {
  [subject: string]: QuizQuestion[];
}

const AITutorQuiz = () => {
  const [dailyQuiz, setDailyQuiz] = useState<DailyQuiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('Mathematics');
  const [questionIndex, setQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [completedQuestions, setCompletedQuestions] = useState<Set<number>>(new Set());
  const [correctAnswers, setCorrectAnswers] = useState<Set<number>>(new Set());

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const mockData: DailyQuiz = {
          Mathematics: [
            { 
              subject: 'Mathematics', 
              question: 'What is 2 + 2?', 
              answers: [
                { text: '3', isCorrect: false },
                { text: '5', isCorrect: false },
                { text: '4', isCorrect: true }, 
                { text: '6', isCorrect: false }
              ] 
            },
            { 
              subject: 'Mathematics', 
              question: 'What is the square root of 16?', 
              answers: [
                { text: '8', isCorrect: false },
                { text: '4', isCorrect: true }, 
                { text: '2', isCorrect: false },
                { text: '6', isCorrect: false }
              ] 
            },
            { 
              subject: 'Mathematics', 
              question: 'What is 15% of 200?', 
              answers: [
                { text: '25', isCorrect: false },
                { text: '35', isCorrect: false },
                { text: '40', isCorrect: false },
                { text: '30', isCorrect: true }, 
              ] 
            },
          ],
          Physics: [
            { 
              subject: 'Physics', 
              question: 'What is the formula for force?', 
              answers: [
                { text: 'E = mc²', isCorrect: false },
                { text: 'F = ma', isCorrect: true }, 
                { text: 'P = mv', isCorrect: false },
                { text: 'W = Fd', isCorrect: false }
              ] 
            },
            { 
              subject: 'Physics', 
              question: 'What is the unit of energy?', 
              answers: [
                { text: 'Joule', isCorrect: true }, 
                { text: 'Watt', isCorrect: false },
                { text: 'Newton', isCorrect: false },
                { text: 'Pascal', isCorrect: false }
              ] 
            },
            { 
              subject: 'Physics', 
              question: 'What is the acceleration due to gravity on Earth?', 
              answers: [
                { text: '10 m/s²', isCorrect: false },
                { text: '9.8 m/s²', isCorrect: true }, 
                { text: '8.9 m/s²', isCorrect: false },
                { text: '11.2 m/s²', isCorrect: false }
              ] 
            },
          ],
          Chemistry: [
            { 
              subject: 'Chemistry', 
              question: 'What is the chemical symbol for water?', 
              answers: [
                { text: 'CO₂', isCorrect: false },
                { text: 'H₂SO₄', isCorrect: false },
                { text: 'NaCl', isCorrect: false },
                { text: 'H₂O', isCorrect: true }, 
              ] 
            },
            { 
              subject: 'Chemistry', 
              question: 'What is the most abundant gas in Earth\'s atmosphere?', 
              answers: [
                { text: 'Oxygen', isCorrect: false },
                { text: 'Nitrogen', isCorrect: true }, 
                { text: 'Carbon Dioxide', isCorrect: false },
                { text: 'Argon', isCorrect: false }
              ] 
            },
            { 
              subject: 'Chemistry', 
              question: 'What is the pH of a neutral solution?', 
              answers: [
                { text: '7', isCorrect: true }, 
                { text: '8', isCorrect: false },
                { text: '6', isCorrect: false },
                { text: '9', isCorrect: false }
              ] 
            },
          ],
          Biology: [
            { 
              subject: 'Biology', 
              question: 'What is the powerhouse of the cell?', 
              answers: [
                { text: 'Nucleus', isCorrect: false },
                { text: 'Ribosome', isCorrect: false },
                { text: 'Mitochondria', isCorrect: true }, 
                { text: 'Endoplasmic Reticulum', isCorrect: false }
              ] 
            },
            { 
              subject: 'Biology', 
              question: 'What is the process by which plants make their food?', 
              answers: [
                { text: 'Respiration', isCorrect: false },
                { text: 'Digestion', isCorrect: false },
                { text: 'Photosynthesis', isCorrect: true }, 
                { text: 'Fermentation', isCorrect: false }
              ] 
            },
            { 
              subject: 'Biology', 
              question: 'What is the largest organ in the human body?', 
              answers: [
                { text: 'Liver', isCorrect: false },
                { text: 'Skin', isCorrect: true }, 
                { text: 'Brain', isCorrect: false },
                { text: 'Heart', isCorrect: false }
              ] 
            },
          ],
          'Computer Science': [
            { 
              subject: 'Computer Science', 
              question: 'What does CPU stand for?', 
              answers: [
                { text: 'Central Power Unit', isCorrect: false },
                { text: 'Computer Processing Unit', isCorrect: false },
                { text: 'Central Processing Unit', isCorrect: true }, 
                { text: 'Central Program Unit', isCorrect: false }
              ] 
            },
            { 
              subject: 'Computer Science', 
              question: 'Which of these is a programming language?', 
              answers: [
                { text: 'HTTP', isCorrect: false },
                { text: 'Python', isCorrect: true }, 
                { text: 'CSS', isCorrect: false },
                { text: 'JSON', isCorrect: false }
              ] 
            },
            { 
              subject: 'Computer Science', 
              question: 'What does HTML stand for?', 
              answers: [
                { text: 'HyperText Markup Language', isCorrect: true }, 
                { text: 'High Tech Modern Language', isCorrect: false },
                { text: 'Home Tool Markup Language', isCorrect: false },
                { text: 'Hyperlink and Text Markup Language', isCorrect: false }
              ] 
            },
          ],
        };
        setDailyQuiz(mockData);
      } catch (err) {
        setError('Failed to load the quiz. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchQuiz();
  }, []);

  // Reset states when subject changes
  useEffect(() => {
    setQuestionIndex(0);
    setSelectedAnswer(null);
    setShowResult(false);
    setCompletedQuestions(new Set());
    setCorrectAnswers(new Set());
  }, [selectedSubject]);

  const handleAnswerSelect = (answerIndex: number) => {
    if (!showResult) {
      setSelectedAnswer(answerIndex);
    }
  };

  const handleAnswerSubmit = () => {
    if (selectedAnswer === null) return;
    
    setShowResult(true);
    setCompletedQuestions(prev => new Set([...prev, questionIndex]));
    
    // Track if answer was correct
    const isCorrect = currentQuestion?.answers[selectedAnswer].isCorrect;
    if (isCorrect) {
      setCorrectAnswers(prev => new Set([...prev, questionIndex]));
    }
    
    // Auto advance to next question after 2 seconds
    setTimeout(() => {
      if (dailyQuiz && dailyQuiz[selectedSubject]) {
        const totalQuestions = dailyQuiz[selectedSubject].length;
        setQuestionIndex((prevIndex) => (prevIndex + 1) % totalQuestions);
        setSelectedAnswer(null);
        setShowResult(false);
      }
    }, 2000);
  };

  const currentQuestion: QuizQuestion | undefined = dailyQuiz?.[selectedSubject]?.[questionIndex];
  const totalQuestions = dailyQuiz?.[selectedSubject]?.length || 0;

  const getAnswerStyle = (answerIndex: number, answer: Answer) => {
    if (!showResult) {
      return selectedAnswer === answerIndex 
        ? "bg-white/40 dark:bg-gray-700/40 border-2 border-white dark:border-gray-600" 
        : "bg-white/20 dark:bg-gray-700/20 border-2 border-transparent hover:bg-white/30 dark:hover:bg-gray-700/30";
    }
    
    if (answer.isCorrect) {
      return "bg-green-500 dark:bg-green-600 border-2 border-green-400 dark:border-green-500";
    } else if (selectedAnswer === answerIndex) {
      return "bg-red-500 dark:bg-red-600 border-2 border-red-400 dark:border-red-500";
    } else {
      return "bg-white/20 dark:bg-gray-700/20 border-2 border-transparent opacity-60";
    }
  };

  const getProgressDotStyle = (index: number) => {
    if (completedQuestions.has(index)) {
      // If question was completed, show green for correct, red for incorrect
      return correctAnswers.has(index) ? "bg-green-500" : "bg-red-500";
    } else if (index === questionIndex) {
      // If this is current question and result is shown, show immediate feedback
      if (showResult && selectedAnswer !== null) {
        const isCorrect = currentQuestion?.answers[selectedAnswer].isCorrect;
        return isCorrect ? "bg-green-500" : "bg-red-500";
      }
      return "bg-indigo-400";
    } else {
      return "bg-gray-300";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading Quiz...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500 text-center p-4">{error}</div>
      </div>
    );
  }

  return (
    <div className="md:p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="relative max-w-4xl mx-auto"
      >
        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border dark:border-gray-700 border-white/40 dark:border-gray-600/40 rounded-3xl shadow-xl p-4 md:p-8">
          {/* Progress Dots */}
          <div className="flex gap-2 mb-6 justify-center md:justify-start">
            {Array.from({ length: totalQuestions }, (_, index) => (
              <div 
                key={index}
                className={`w-3 h-3 rounded-full transition-colors duration-300 ${getProgressDotStyle(index)}`}
              />
            ))}
          </div>

          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-4 md:p-6 text-white">
            <Tabs value={selectedSubject} onValueChange={setSelectedSubject} className="w-full">
              {/* Mobile-optimized tabs */}
              <div className="overflow-x-auto pb-2">
                <TabsList className="flex w-max bg-indigo-400/20 dark:bg-indigo-600/20  text-white dark:text-gray-100 h-auto">
                  {dailyQuiz && Object.keys(dailyQuiz).map((subject) => (
                    <TabsTrigger 
                      key={subject} 
                      value={subject}
                      className="text-xs md:text-sm p-2 md:p-3 data-[state=active]:bg-white/20 dark:data-[state=active]:bg-gray-700/20"
                    >
                      {subject}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </div>
              
              {dailyQuiz && Object.keys(dailyQuiz).map((subject) => (
                <TabsContent key={subject} value={subject}>
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={questionIndex}
                      initial={{ opacity: 0, x: 50 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -50 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h3 className="text-lg md:text-xl font-bold mb-2">{currentQuestion?.subject}</h3>
                      <p className="text-indigo-100 mb-4 text-sm md:text-base">
                        Question {questionIndex + 1} of {totalQuestions}
                      </p>

                      <div className="bg-indigo-400/20 rounded-xl p-4 mb-6">
                        <p className="text-sm md:text-base leading-relaxed">{currentQuestion?.question}</p>
                      </div>

                      {/* Mobile-optimized answer grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
                        {currentQuestion?.answers.map((answer, index) => (
                          <motion.div
                            key={index}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleAnswerSelect(index)}
                            className={`
                              rounded-xl p-4 text-center cursor-pointer transition-all duration-300 
                              text-sm md:text-base font-medium min-h-[60px] flex items-center justify-center
                              ${getAnswerStyle(index, answer)}
                              ${!showResult ? 'active:scale-95' : 'cursor-default'}
                            `}
                          >
                            <div className="flex items-center justify-center gap-2">
                              <span>{answer.text}</span>
                              {showResult && answer.isCorrect && (
                                <CheckCircle size={20} className="text-white" />
                              )}
                              {showResult && selectedAnswer === index && !answer.isCorrect && (
                                <XCircle size={20} className="text-white" />
                              )}
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  </AnimatePresence>
                </TabsContent>
              ))}
            </Tabs>

            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-indigo-200 text-sm md:text-base">
                <Bot size={18} />
                <span>AI Tutor Available</span>
              </div>
              
              <Button 
                onClick={handleAnswerSubmit} 
                disabled={selectedAnswer === null || showResult}
                className="
                  bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 py-2 px-6 rounded-xl text-sm font-semibold 
                  hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed
                  w-full md:w-auto
                "
              >
                {showResult ? 'Next Question...' : 'Submit Answer'}
              </Button>
            </div>

            {/* Result feedback */}
            {showResult && selectedAnswer !== null && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 bg-white/10 dark:bg-gray-800/10 rounded-xl text-center"
              >
                {currentQuestion?.answers[selectedAnswer].isCorrect ? (
                  <div className="flex items-center justify-center gap-2 text-green-300">
                    <CheckCircle size={20} />
                    <span className="font-semibold">Correct! Well done!</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2 text-red-300">
                    <XCircle size={20} />
                    <span className="font-semibold">
                      Incorrect. The correct answer is: {currentQuestion?.answers.find(a => a.isCorrect)?.text}
                    </span>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-yellow-400 rounded-full opacity-20 blur-3xl hidden md:block"></div>
        <div className="absolute -top-6 -right-6 w-32 h-32 bg-indigo-500 rounded-full opacity-20 blur-3xl hidden md:block"></div>
      </motion.div>
    </div>
  );
};

export default AITutorQuiz;