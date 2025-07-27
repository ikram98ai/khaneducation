import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Send, Lightbulb, Brain, Target } from "lucide-react";

interface Message {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
}


export const AIAssistant = ({subject, lesson}:{subject:string, lesson?:string}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
        id: '1',
        content: `Hi! I'm your AI learning assistant. I'm here to help you understand ${subject || 'your lessons'} better. Feel free to ask me questions about the concepts, request explanations, or get study tips!`,
        type: 'assistant',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length, subject]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      type: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate AI response with contextual learning assistance
    setTimeout(() => {
      const responses = [
        "That's a great question! Let me break this down for you step by step...",
        "I can help you understand this concept better. Here's a simple way to think about it...",
        "This is a common area where students get confused. Let me clarify...",
        "Excellent! You're asking the right questions. Here's what you need to know...",
        "I can see you're thinking critically about this. Let me provide some additional insight..."
      ];

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responses[Math.floor(Math.random() * responses.length)],
        type: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000 + Math.random() * 1000);
  };

  const quickActions = [
    { icon: Lightbulb, label: "Explain concept", action: "Can you explain this concept in simpler terms?" },
    { icon: Brain, label: "Study tips", action: "What are some effective study strategies for this topic?" },
    { icon: Target, label: "Practice problems", action: "Can you give me some practice problems?" }
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
        className="fixed bottom-6 right-6 z-50 shadow-floating animate-float"
      >
        <Sparkles className="h-5 w-5 mr-2" />
        AI Assistant
      </Button>
    );
  }

  return (
    <Card className="fixed bottom-6 right-6 w-96 h-[500px] z-50 shadow-floating animate-spring-in  bg-white/80 backdrop-blur-xl border-b border-gray-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <CardTitle className="text-lg">AI Assistant</CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
            className="h-8 w-8 p-0"
          >
            ×
          </Button>
        </div>
        {subject && (
          <Badge variant="secondary" className="w-fit">
            {subject} {lesson && `• ${lesson}`}
          </Badge>
        )}
      </CardHeader>

      <CardContent className="flex flex-col h-[380px] p-4">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-3 rounded-lg text-sm ${
                  message.type === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-surface-elevated border'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-surface-elevated border p-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        <div className="flex gap-1 mb-3 overflow-x-auto">
          {quickActions.map((action, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              onClick={() => handleQuickAction(action.action)}
              className="flex-1 text-xs"
            >
              <action.icon className="h-3 w-3 mr-1" />
              {action.label}
            </Button>
          ))}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            size="sm"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};