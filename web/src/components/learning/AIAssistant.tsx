import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Send, Lightbulb, Brain, Target } from "lucide-react";
import { useAiAssistance } from "@/hooks/useApiQueries";
import MarkdownViewer from "../mdviewer/MarkdownViewer";

interface Message {
  id?: string;
  content: string;
  role: "user" | "assistant";
  timestamp?: Date;
}

export const AIAssistant = ({
  subject_id,
  subject,
  lesson_id,
  lesson,
}: {
  subject_id: string;
  subject: string;
  lesson_id?: string;
  lesson?: string;
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const aiAssistanceMutation = useAiAssistance();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage: Message = {
        id: "1",
        content: `Hi! I'm your AI learning assistant. I'm here to help you understand ${subject}${
          lesson ? ` • ${lesson}` : ""
        } better. 
        Feel free to ask me questions about the concepts, request explanations, or get study tips!`,
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length, subject_id]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };

    const messagesToSend = [...messages, userMessage]; // Include the new user message
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setIsLoading(true);

    const requestData = {
      subject_id: subject_id,
      lesson_id: lesson_id,
      user_messages: messagesToSend
        .slice(-10)
        .map(({ role, content }) => ({ role, content })),
    };

    try {
      const response = await aiAssistanceMutation.mutateAsync(requestData);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content:
          response.ai_response ||
          "I am sorry, I cannot provide a response at the moment. Please try again later.",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("AI Assistance Error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Oops! Something went wrong. Please try again.",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    {
      icon: Lightbulb,
      label: "Explain concept",
      action: "Can you explain this concept in simpler terms?",
    },
    {
      icon: Brain,
      label: "Study tips",
      action: "What are some effective study strategies for this topic?",
    },
    {
      icon: Target,
      label: "Practice problems",
      action: "Can you give me some practice problems?",
    },
  ];

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        variant="floating"
        size="lg"
        className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 shadow-floating animate-float"
      >
        <Sparkles className="h-5 w-5 mr-2" />
        AI Assistant
      </Button>
    );
  }
  return (
    <>
      <div
        className="fixed inset-0 bg-black/30 z-40"
        onClick={() => setIsOpen(false)}
        aria-hidden="true"
      ></div>
      <Card className="fixed bottom-0 right-0 w-full h-full flex flex-col md:w-[440px] lg:w-[540px] md:h-[80vh] md:max-h-[700px] md:bottom-6 md:right-6 z-50 shadow-2xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border dark:border-gray-700 md:rounded-2xl">
        <CardHeader className="flex-shrink-0 border-b dark:border-gray-700 md:rounded-t-2xl bg-white/50 dark:bg-gray-900/50 px-4 pt-4 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                AI Assistant
              </CardTitle>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 rounded-full text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
              aria-label="Close"
            >
              x
            </Button>
          </div>
          {subject && (
            <Badge variant="secondary" className="mt-2 ml-12 w-fit">
              {subject} {lesson && `• ${lesson}`}
            </Badge>
          )}
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-end gap-2 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] p-3 rounded-lg text-sm ${
                    message.role === "user"
                      ? "bg-blue-600 dark:bg-blue-700 text-white dark:text-gray-100 rounded-br-none"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-100 border dark:border-gray-700 rounded-bl-none"
                  }`}
                >
                  {message.role === "user" ? (
                    message.content
                  ) : (
                    <MarkdownViewer markdown={message.content} />
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-end gap-2 justify-start">
                <div className="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-800 border dark:border-gray-700 p-3 rounded-lg rounded-bl-none">
                  <div className="flex space-x-1.5">
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse"
                      style={{ animationDelay: "0.4s" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="flex-shrink-0 border-t dark:border-gray-700 md:rounded-b-2xl bg-white/50 dark:bg-gray-900/50 p-3">
            {/* Quick Actions */}
            <div className="flex gap-2 mb-2 overflow-x-auto pb-2">
              {quickActions.map((action, index) => {
                const Icon = action.icon; // FIX: Assign component to capitalized variable
                return (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickAction(action.action)}
                    className="flex-shrink-0 text-xs h-8 bg-white dark:bg-gray-800"
                  >
                    <Icon className="h-3.5 w-3.5 mr-1.5" />
                    {action.label}
                  </Button>
                );
              })}
            </div>

            {/* Input */}
            <div className="flex items-center  gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything..."
                onKeyPress={(e) =>
                  e.key === "Enter" && !isLoading && handleSend()
                }
                className="flex-1 bg-white dark:bg-gray-800"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="icon"
                className="rounded-full flex-shrink-0 w-9 h-9 bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-800"
                aria-label="Send message"
              >
                <Send className="h-4 w-4 text-white dark:text-gray-100" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
};
