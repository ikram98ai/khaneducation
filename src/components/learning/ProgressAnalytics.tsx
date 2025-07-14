import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Clock, Target, Award, Calendar, Zap } from "lucide-react";

import { User, Enrollment } from "@/types/api";

interface ProgressAnalyticsProps {
  user?: User;
  enrollments?: Enrollment[];
}

export const ProgressAnalytics = ({ user, enrollments = [] }: ProgressAnalyticsProps) => {
  const mockAnalytics = {
    weeklyProgress: 85,
    averageSessionTime: "25 min",
    streak: 7,
    completionRate: 92,
    totalLessonsCompleted: 23,
    weeklyGoal: 5,
    lessonsTisWeek: 4,
    bestSubject: "Mathematics",
    improvementArea: "Science",
    upcomingDeadlines: 2
  };

  const weeklyActivity = [
    { day: "Mon", lessons: 2, time: 45 },
    { day: "Tue", lessons: 1, time: 30 },
    { day: "Wed", lessons: 3, time: 60 },
    { day: "Thu", lessons: 0, time: 0 },
    { day: "Fri", lessons: 2, time: 40 },
    { day: "Sat", lessons: 1, time: 25 },
    { day: "Sun", lessons: 1, time: 20 }
  ];

  const achievements = [
    { title: "Quick Learner", description: "Complete 5 lessons in one day", earned: true },
    { title: "Consistent Student", description: "7-day learning streak", earned: true },
    { title: "Math Wizard", description: "Score 90%+ on all math quizzes", earned: false },
    { title: "Early Bird", description: "Study before 8 AM for 5 days", earned: false }
  ];

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="elevated" className="animate-spring-in">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Weekly Progress</p>
                <p className="text-2xl font-bold text-success">{mockAnalytics.weeklyProgress}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-success animate-float" />
            </div>
            <Progress value={mockAnalytics.weeklyProgress} className="mt-2" />
          </CardContent>
        </Card>

        <Card variant="elevated" className="animate-spring-in" style={{ animationDelay: '0.1s' }}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Session</p>
                <p className="text-2xl font-bold">{mockAnalytics.averageSessionTime}</p>
              </div>
              <Clock className="h-8 w-8 text-info animate-float" style={{ animationDelay: '0.3s' }} />
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="animate-spring-in" style={{ animationDelay: '0.2s' }}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Current Streak</p>
                <p className="text-2xl font-bold text-warning">{mockAnalytics.streak} days</p>
              </div>
              <Zap className="h-8 w-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="animate-spring-in" style={{ animationDelay: '0.3s' }}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completion Rate</p>
                <p className="text-2xl font-bold text-primary">{mockAnalytics.completionRate}%</p>
              </div>
              <Target className="h-8 w-8 text-primary animate-float" style={{ animationDelay: '0.6s' }} />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity */}
        <Card variant="glass" className="animate-slide-up-fade">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Weekly Activity
            </CardTitle>
            <CardDescription>Your learning activity this week</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {weeklyActivity.map((day, index) => (
                <div key={day.day} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 text-sm font-medium">{day.day}</div>
                    <div className="flex-1 bg-muted rounded-full h-2 w-24">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-500"
                        style={{ 
                          width: `${Math.min((day.lessons / 3) * 100, 100)}%`,
                          animationDelay: `${index * 0.1}s`
                        }}
                      />
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {day.lessons} lessons • {day.time}min
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 p-3 bg-surface-elevated rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span>Weekly Goal Progress</span>
                <span className="font-medium">{mockAnalytics.lessonsTisWeek}/{mockAnalytics.weeklyGoal} lessons</span>
              </div>
              <Progress 
                value={(mockAnalytics.lessonsTisWeek / mockAnalytics.weeklyGoal) * 100} 
                className="mt-2" 
              />
            </div>
          </CardContent>
        </Card>

        {/* Achievements */}
        <Card variant="glass" className="animate-slide-up-fade" style={{ animationDelay: '0.2s' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Achievements
            </CardTitle>
            <CardDescription>Your learning milestones</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {achievements.map((achievement, index) => (
                <div 
                  key={index}
                  className={`p-3 rounded-lg border ${
                    achievement.earned 
                      ? 'bg-success/10 border-success/30' 
                      : 'bg-muted/30 border-muted'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className={`font-medium ${achievement.earned ? 'text-success' : 'text-muted-foreground'}`}>
                          {achievement.title}
                        </h4>
                        {achievement.earned && (
                          <Badge variant="secondary" className="text-xs">Earned</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {achievement.description}
                      </p>
                    </div>
                    <div className={`text-2xl ${achievement.earned ? 'animate-bounce' : 'opacity-50'}`}>
                      {achievement.earned ? '🏆' : '🔒'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card variant="floating" className="animate-slide-up-fade" style={{ animationDelay: '0.4s' }}>
        <CardHeader>
          <CardTitle>Learning Insights</CardTitle>
          <CardDescription>Personalized recommendations based on your progress</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-success/10 rounded-lg border border-success/30">
              <h4 className="font-medium text-success mb-1">Strong Performance</h4>
              <p className="text-sm text-muted-foreground">
                Excellent progress in {mockAnalytics.bestSubject}. Keep up the great work!
              </p>
            </div>
            
            <div className="p-4 bg-warning/10 rounded-lg border border-warning/30">
              <h4 className="font-medium text-warning mb-1">Focus Area</h4>
              <p className="text-sm text-muted-foreground">
                Consider spending more time on {mockAnalytics.improvementArea} topics.
              </p>
            </div>
            
            <div className="p-4 bg-info/10 rounded-lg border border-info/30">
              <h4 className="font-medium text-info mb-1">Upcoming</h4>
              <p className="text-sm text-muted-foreground">
                {mockAnalytics.upcomingDeadlines} assignment deadlines this week.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};