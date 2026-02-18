import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin, useRegister } from "@/hooks/useApiQueries";
import { useAuthStore } from "@/stores/authStore";
import { useNavigate } from "react-router-dom";


export const AuthForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    first_name: '',
    last_name: ''
  });
  const [mode, setAuthMode] = useState('login')
  
  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const { isLoading, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);


  const toggleAuthMode = () => {
    setAuthMode(prev => prev === 'login' ? 'register' : 'login');
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (mode === 'login') {
        const result = await loginMutation.mutateAsync({
          email: formData.email,
          password: formData.password
        });
      } else {
        const result = await registerMutation.mutateAsync(formData);
      }
    } catch (error) {
      // Error handling is done in the mutations
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-accent/20 p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-large border-0">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4">
              <img src="/logo.png" alt="Khan Education Logo" className="w-16 h-16" />
            </div>
            <CardTitle className="text-2xl font-bold">
              {mode === 'login' ? 'Welcome Back' : 'Create Account'}
            </CardTitle>
            <CardDescription>
              {mode === 'login' 
                ? 'Sign in to continue your learning journey' 
                : 'Start your educational adventure today'
              }
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {mode === 'register' && (
                <>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="first_name">First Name</Label>
                      <Input
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleInputChange}
                        required
                        placeholder="John"
                      />
                    </div>
                    <div>
                      <Label htmlFor="last_name">Last Name</Label>
                      <Input
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleInputChange}
                        required
                        placeholder="Doe"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      required
                      placeholder="johndoe"
                    />
                  </div>
                </>
              )}
              
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  placeholder="john@example.com"
                />
              </div>
              
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  placeholder="•••"
                />
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <Button
                type="submit"
                variant="gradient"
                size="lg"
                className="w-full"
                disabled={isLoading || loginMutation.isPending || registerMutation.isPending}
              >
                {(isLoading || loginMutation.isPending || registerMutation.isPending) ? "Processing..." : mode === 'login' ? 'Sign In' : 'Sign Up'}
              </Button>
              
              <p className="text-sm text-muted-foreground">
                {mode === 'login' ? "Don't have an account?" : "Already have an account?"}
                <button
                  type="button"
                  onClick={toggleAuthMode}
                  className="ml-1 text-primary hover:underline font-medium"
                >
                  {mode === 'login' ? 'Sign up' : 'Sign in'}
                </button>
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
};