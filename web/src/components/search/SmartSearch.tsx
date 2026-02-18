import { useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, BookOpen, Play, CheckCircle, Clock } from "lucide-react";

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'lesson' | 'subject' | 'quiz' | 'practice';
  subject: string;
  progress?: number;
  duration?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
}

interface SmartSearchProps {
  onSelectResult?: (result: SearchResult) => void;
  placeholder?: string;
}

export const SmartSearch = ({ onSelectResult, placeholder = "Search lessons, subjects, or topics..." }: SmartSearchProps) => {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);

  const mockResults: SearchResult[] = [
    {
      id: '1',
      title: 'Linear Equations',
      description: 'Learn to solve linear equations step by step',
      type: 'lesson',
      subject: 'Mathematics',
      progress: 75,
      duration: '20 min',
      difficulty: 'beginner'
    },
    {
      id: '2',
      title: 'Chemical Reactions',
      description: 'Understanding chemical bonds and reactions',
      type: 'lesson',
      subject: 'Science',
      progress: 0,
      duration: '25 min',
      difficulty: 'intermediate'
    },
    {
      id: '3',
      title: 'Mathematics',
      description: 'Complete mathematics curriculum',
      type: 'subject',
      subject: 'Mathematics',
      progress: 60,
      duration: '2.5 hours',
      difficulty: 'beginner'
    },
    {
      id: '4',
      title: 'Algebra Quiz',
      description: 'Test your algebraic skills',
      type: 'quiz',
      subject: 'Mathematics',
      duration: '10 min',
      difficulty: 'intermediate'
    },
    {
      id: '5',
      title: 'Practice Problems',
      description: 'Solve linear equation practice problems',
      type: 'practice',
      subject: 'Mathematics',
      duration: '15 min',
      difficulty: 'beginner'
    }
  ];

  const filters = [
    { id: 'lesson', label: 'Lessons', icon: BookOpen },
    { id: 'subject', label: 'Subjects', icon: BookOpen },
    { id: 'quiz', label: 'Quizzes', icon: CheckCircle },
    { id: 'practice', label: 'Practice', icon: Play }
  ];

  const filteredResults = useMemo(() => {
    let results = mockResults;

    if (query.trim()) {
      results = results.filter(result =>
        result.title.toLowerCase().includes(query.toLowerCase()) ||
        result.description.toLowerCase().includes(query.toLowerCase()) ||
        result.subject.toLowerCase().includes(query.toLowerCase())
      );
    }

    if (selectedFilters.length > 0) {
      results = results.filter(result => selectedFilters.includes(result.type));
    }

    return results;
  }, [query, selectedFilters]);

  const toggleFilter = (filterId: string) => {
    setSelectedFilters(prev =>
      prev.includes(filterId)
        ? prev.filter(id => id !== filterId)
        : [...prev, filterId]
    );
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'lesson': return BookOpen;
      case 'subject': return BookOpen;
      case 'quiz': return CheckCircle;
      case 'practice': return Play;
      default: return BookOpen;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'lesson': return 'bg-primary/10 text-primary border-primary/30';
      case 'subject': return 'bg-success/10 text-success border-success/30';
      case 'quiz': return 'bg-warning/10 text-warning border-warning/30';
      case 'practice': return 'bg-info/10 text-info border-info/30';
      default: return 'bg-muted/10 text-muted-foreground border-muted/30';
    }
  };

  return (
    <div className="relative w-full max-w-2xl">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="pl-10 pr-4 h-12 text-base"
        />
      </div>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Results Panel */}
          <Card className="absolute top-full left-0 right-0 mt-2 z-50 shadow-floating border-glass backdrop-blur-glass animate-spring-in">
            <CardContent className="p-4">
              {/* Filters */}
              <div className="flex items-center gap-2 mb-4 pb-3 border-b overflow-x-auto">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground mr-2">Filter by:</span>
                {filters.map((filter) => (
                  <Button
                    key={filter.id}
                    variant={selectedFilters.includes(filter.id) ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleFilter(filter.id)}
                    className="text-xs"
                  >
                    <filter.icon className="h-3 w-3 mr-1" />
                    {filter.label}
                  </Button>
                ))}
              </div>

              {/* Results */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredResults.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No results found</p>
                    <p className="text-sm">Try adjusting your search or filters</p>
                  </div>
                ) : (
                  filteredResults.map((result, index) => {
                    const TypeIcon = getTypeIcon(result.type);
                    return (
                      <div
                        key={result.id}
                        onClick={() => {
                          onSelectResult?.(result);
                          setIsOpen(false);
                        }}
                        className="p-3 rounded-lg border hover:bg-surface-hover cursor-pointer transition-all duration-200 hover:scale-[1.01] animate-spring-in"
                        style={{ animationDelay: `${index * 0.05}s` }}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${getTypeColor(result.type)}`}>
                            <TypeIcon className="h-4 w-4" />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium truncate">{result.title}</h4>
                              <Badge variant="outline" className="text-xs">
                                {result.type}
                              </Badge>
                            </div>
                            
                            <p className="text-sm text-muted-foreground mb-2">
                              {result.description}
                            </p>
                            
                            <div className="flex items-center gap-3 text-xs text-muted-foreground">
                              <span>{result.subject}</span>
                              {result.duration && (
                                <>
                                  <span>•</span>
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    {result.duration}
                                  </div>
                                </>
                              )}
                              {result.progress !== undefined && (
                                <>
                                  <span>•</span>
                                  <span>{result.progress}% complete</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};