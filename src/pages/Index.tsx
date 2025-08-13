import { motion } from "framer-motion";
import {
  BookOpen,
  Bot,
  Award,
  Users,
  BarChart,
  Play,
  CheckCircle,
} from "lucide-react";
import Header from "@/components/navigation/Header";
import Footer from "@/components/navigation/Footer";
import { Link } from "react-router-dom";
import AITutorQuiz from '@/components/quiz/AITutorQuiz';

export default function Index() {
  const features = [
    {
      icon: <Bot size={40} className="text-indigo-600" />,
      title: "AI-Powered Lessons",
      description:
        "Generate personalized lesson content tailored to each student's learning style and pace.",
    },
    {
      icon: <BookOpen size={40} className="text-indigo-600" />,
      title: "Interactive Content",
      description:
        "Engaging multimedia lessons with embedded quizzes and practice exercises.",
    },
    {
      icon: <Award size={40} className="text-indigo-600" />,
      title: "Progress Tracking",
      description:
        "Monitor student performance with detailed analytics and progress reports.",
    },
    {
      icon: <Users size={40} className="text-indigo-600" />,
      title: "Collaborative Learning",
      description:
        "Connect students and teachers in a supportive learning environment.",
    },
  ];

  const testimonials = [
    {
      quote:
        "Khan Education has transformed how I teach. Creating personalized lessons takes minutes instead of hours!",
      author: "Dr. Sarah Johnson",
      role: "Mathematics Instructor",
    },
    {
      quote:
        "I've improved my grades in math by 30% since using Khan Education. The AI tutor explains concepts in a way I actually understand.",
      author: "Alex Martinez",
      role: "Grade 10 Student",
    },
    {
      quote:
        "The analytics dashboard helps me identify exactly where students are struggling so I can provide targeted support.",
      author: "Michael Thompson",
      role: "Science Department Head",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 dark:from-gray-950 to-indigo-50 dark:to-gray-900">
      {/* Header */}
      <Header />

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
              Transform Education with{" "}
              <span className="text-indigo-600 dark:text-indigo-400">AI-Powered</span> Learning
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-gray-600 dark:text-gray-300 max-w-2xl">
              Khan Education revolutionizes the classroom experience with
              personalized lessons, intelligent tutoring, and actionable
              insights for students and educators.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row sm:flex-wrap gap-4">
              <Link
                to="/login"
                className="bg-indigo-600 dark:bg-indigo-700 hover:bg-indigo-700 dark:hover:bg-indigo-800 text-white dark:text-gray-100 font-semibold py-3 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl w-full sm:w-auto text-center"
              >
                Get Started Free
              </Link>
              <button
                onClick={() =>
                  document
                    .getElementById("features")
                    .scrollIntoView({ behavior: "smooth" })
                }
                className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100 font-semibold py-3 px-8 rounded-xl border border-gray-200 dark:border-gray-700 transition-all duration-300 shadow-md hover:shadow-lg w-full sm:w-auto text-center"
              >
                Explore Features
              </button>
            </div>
          </motion.div>

          <AITutorQuiz />
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-16 md:py-24 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Powerful Features for Modern Education
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Whether you're a student or educator, Khan Education provides the
              tools you need to succeed
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-gradient-to-br from-white dark:from-gray-900 to-blue-50 dark:to-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div id="how-it-works" className="py-16 md:py-24 bg-gradient-to-br from-indigo-50 dark:from-gray-950 to-purple-50 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              How Khan Education Works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Transforming education in three simple steps
            </p>
          </div>

          <div className="flex flex-col md:grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/20 rounded-full flex items-center justify-center mb-4">
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                Create or Select Content
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Instructors generate AI-powered lessons or choose from our
                library. Students access curated content.
              </p>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 h-40 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <BookOpen className="text-indigo-600 dark:text-indigo-400 mb-2" size={32} />
                  <p className="text-center text-sm">Mathematics • Grade 8</p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/20 rounded-full flex items-center justify-center mb-4">
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                Engage and Learn
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Students interact with lessons, complete practice tasks, and get
                real-time AI assistance.
              </p>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 h-40 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <Play className="text-indigo-600 dark:text-indigo-400 mb-2" size={32} />
                  <p className="text-center text-sm">Interactive Learning</p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/20 rounded-full flex items-center justify-center mb-4">
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                Track and Improve
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Detailed analytics help students identify strengths and
                instructors optimize teaching strategies.
              </p>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 h-40 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <BarChart className="text-indigo-600 dark:text-indigo-400 mb-2" size={32} />
                  <p className="text-center text-sm">Performance Dashboard</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div id="testimonials" className="py-16 md:py-24 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              What Our Users Say
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Join thousands of educators and students transforming education
            </p>
          </div>

          <div className="flex flex-col md:grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-gradient-to-br from-white dark:from-gray-900 to-blue-50 dark:to-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl p-6 shadow-sm"
              >
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <CheckCircle
                      key={i}
                      className="text-yellow-400 dark:text-yellow-500 fill-current"
                      size={20}
                    />
                  ))}
                </div>
                <p className="text-gray-600 dark:text-gray-300 italic mb-6">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/20 rounded-full flex items-center justify-center mr-4">
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                      {testimonial.author.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="font-bold text-gray-900 dark:text-gray-100">
                      {testimonial.author}
                    </p>
                    <p className="text-gray-600 dark:text-gray-300 text-sm">{testimonial.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div id="pricing" className="py-16 md:py-24 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Affordable pricing for individuals and institutions.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Pricing plans would go here */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm text-center">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">Free</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">Basic features for individual students.</p>
              <p className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-6">$0</p>
              <button className="bg-indigo-600 dark:bg-indigo-700 hover:bg-indigo-700 dark:hover:bg-indigo-800 text-white dark:text-gray-100 font-semibold py-3 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl">
                Get Started
              </button>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm text-center">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">Pro</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">Advanced features for dedicated learners.</p>
              <p className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-6">$15</p>
              <button className="bg-indigo-600 dark:bg-indigo-700 hover:bg-indigo-700 dark:hover:bg-indigo-800 text-white dark:text-gray-100 font-semibold py-3 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl">
                Choose Plan
              </button>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm text-center">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">Institution</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">Full suite of tools for schools and organizations.</p>
              <p className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-6">Contact Us</p>
              <button className="bg-indigo-600 dark:bg-indigo-700 hover:bg-indigo-700 dark:hover:bg-indigo-800 text-white dark:text-gray-100 font-semibold py-3 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 md:py-24 bg-gradient-to-br from-indigo-600 dark:from-indigo-700 to-purple-700 dark:to-purple-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white dark:text-gray-100 mb-6">
              Ready to Transform Learning?
            </h2>
            <p className="text-xl text-indigo-100 dark:text-indigo-200 mb-10">
              Join thousands of educators and students already using Khan Education
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link
                to="/login"
                className="bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 font-semibold py-3 px-8 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors shadow-lg"
              >
                Get Started Free
              </Link>
              {/* <Link
                to="/login"
                className="bg-transparent border-2 border-white text-white font-semibold py-3 px-8 rounded-xl hover:bg-white/10 transition-colors"
              >
                Sign In
              </Link> */}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}
