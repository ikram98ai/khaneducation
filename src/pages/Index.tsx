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
        "EduAgent AI has transformed how I teach. Creating personalized lessons takes minutes instead of hours!",
      author: "Dr. Sarah Johnson",
      role: "Mathematics Instructor",
    },
    {
      quote:
        "I've improved my grades in math by 30% since using EduAgent. The AI tutor explains concepts in a way I actually understand.",
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
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-50">
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
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              Transform Education with{" "}
              <span className="text-indigo-600">AI-Powered</span> Learning
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-2xl">
              EduAgent AI revolutionizes the classroom experience with
              personalized lessons, intelligent tutoring, and actionable
              insights for students and educators.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                to="/login"
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                Get Started Free
              </Link>
              <button
                onClick={() =>
                  document
                    .getElementById("features")
                    .scrollIntoView({ behavior: "smooth" })
                }
                className="bg-white hover:bg-gray-50 text-gray-800 font-semibold py-3 px-8 rounded-xl border border-gray-200 transition-all duration-300 shadow-md hover:shadow-lg"
              >
                Explore Features
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="relative"
          >
            <div className="bg-white/80 backdrop-blur-xl border border-white/40 rounded-3xl shadow-xl p-8">
              <div className="flex gap-2 mb-6">
                <div className="bg-indigo-600 w-3 h-3 rounded-full"></div>
                <div className="bg-gray-300 w-3 h-3 rounded-full"></div>
                <div className="bg-gray-300 w-3 h-3 rounded-full"></div>
              </div>

              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
                <h3 className="text-xl font-bold mb-2">Algebra Mastery</h3>
                <p className="text-indigo-100 mb-4">
                  Solving Quadratic Equations
                </p>

                <div className="bg-indigo-400/20 rounded-xl p-4 mb-4">
                  <p className="text-sm font-medium">Question 3 of 5</p>
                  <p className="mt-2">Solve for x: 2x² + 5x - 3 = 0</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/20 rounded-xl p-3 text-center cursor-pointer hover:bg-white/30 transition-colors">
                    x = 0.5, x = -3
                  </div>
                  <div className="bg-white/20 rounded-xl p-3 text-center cursor-pointer hover:bg-white/30 transition-colors">
                    x = -0.5, x = 3
                  </div>
                  <div className="bg-white/20 rounded-xl p-3 text-center cursor-pointer hover:bg-white/30 transition-colors">
                    x = 1.5, x = -1
                  </div>
                  <div className="bg-white/20 rounded-xl p-3 text-center cursor-pointer hover:bg-white/30 transition-colors">
                    x = -1.5, x = 1
                  </div>
                </div>

                <div className="mt-6 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-indigo-200">
                    <Bot size={18} />
                    <span>AI Tutor Available</span>
                  </div>
                  <button className="bg-white text-indigo-600 py-2 px-4 rounded-xl text-sm font-semibold hover:bg-gray-100 transition-colors">
                    Submit Answer
                  </button>
                </div>
              </div>
            </div>

            <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-yellow-400 rounded-full opacity-20 blur-3xl"></div>
            <div className="absolute -top-6 -right-6 w-32 h-32 bg-indigo-500 rounded-full opacity-20 blur-3xl"></div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-16 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Education
            </h2>
            <p className="text-xl text-gray-600">
              Whether you're a student or educator, EduAgent AI provides the
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
                className="bg-gradient-to-br from-white to-blue-50 border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="py-16 md:py-24 bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How EduAgent AI Works
            </h2>
            <p className="text-xl text-gray-600">
              Transforming education in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-white rounded-2xl p-6 shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-indigo-600 font-bold">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Create or Select Content
              </h3>
              <p className="text-gray-600 mb-4">
                Instructors generate AI-powered lessons or choose from our
                library. Students access curated content.
              </p>
              <div className="bg-gray-100 rounded-xl p-4 h-40 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <BookOpen className="text-indigo-600 mb-2" size={32} />
                  <p className="text-center text-sm">Mathematics • Grade 8</p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white rounded-2xl p-6 shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-indigo-600 font-bold">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Engage and Learn
              </h3>
              <p className="text-gray-600 mb-4">
                Students interact with lessons, complete practice tasks, and get
                real-time AI assistance.
              </p>
              <div className="bg-gray-100 rounded-xl p-4 h-40 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <Play className="text-indigo-600 mb-2" size={32} />
                  <p className="text-center text-sm">Interactive Learning</p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="bg-white rounded-2xl p-6 shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-indigo-600 font-bold">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Track and Improve
              </h3>
              <p className="text-gray-600 mb-4">
                Detailed analytics help students identify strengths and
                instructors optimize teaching strategies.
              </p>
              <div className="bg-gray-100 rounded-xl p-4 h-40 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <BarChart className="text-indigo-600 mb-2" size={32} />
                  <p className="text-center text-sm">Performance Dashboard</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="py-16 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Our Users Say
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands of educators and students transforming education
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-gradient-to-br from-white to-blue-50 border border-gray-100 rounded-2xl p-6 shadow-sm"
              >
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <CheckCircle
                      key={i}
                      className="text-yellow-400 fill-current"
                      size={20}
                    />
                  ))}
                </div>
                <p className="text-gray-600 italic mb-6">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mr-4">
                    <span className="text-indigo-600 font-bold">
                      {testimonial.author.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">
                      {testimonial.author}
                    </p>
                    <p className="text-gray-600 text-sm">{testimonial.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 md:py-24 bg-gradient-to-br from-indigo-600 to-purple-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Transform Learning?
            </h2>
            <p className="text-xl text-indigo-100 mb-10">
              Join thousands of educators and students already using EduAgent AI
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link
                to="/login"
                className="bg-white text-indigo-600 font-semibold py-3 px-8 rounded-xl hover:bg-gray-100 transition-colors shadow-lg"
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
