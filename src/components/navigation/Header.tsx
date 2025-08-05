import { useAuthStore } from '@/stores/authStore';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

export default function Header() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4 md:py-6">
          <Link to="/" className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 cursor-pointer">
              <img src="/logo.png" alt="khan education logo" className='w-16 h-16' />
              <span className="text-xl font-bold text-gray-900">Khan Education</span>
            </div>
          </Link>

          <nav className="hidden md:flex space-x-10">
            <button onClick={() => scrollToSection('features')} className="text-gray-600 hover:text-indigo-600 font-medium">Features</button>
            <button onClick={() => scrollToSection('how-it-works')} className="text-gray-600 hover:text-indigo-600 font-medium">How It Works</button>
            <button onClick={() => scrollToSection('testimonials')} className="text-gray-600 hover:text-indigo-600 font-medium">Testimonials</button>
            <button onClick={() => scrollToSection('pricing')} className="text-gray-600 hover:text-indigo-600 font-medium">Pricing</button>
          </nav>

          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-4">
              {!isLoading && (isAuthenticated ? (
                  <>
                  <button
                    onClick={useAuthStore.getState().clearAuth}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors"
                  >
                    Logout
                  </button>

                  <Link 
                    to='/dashboard'
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors"
                  >
                    Go to Dashboard
                  </Link>
                  </>
              ) : (
                <>
        
                  <Link 
                    to='/login'
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors"
                  >
                    Get Started
                  </Link>
                </>
              ))}
            </div>
            <div className="md:hidden">
              <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>
        {isMenuOpen && (
          <div className="md:hidden">
            <nav className="flex flex-col space-y-4 pb-4">
              <button onClick={() => {scrollToSection('features'); setIsMenuOpen(false);}} className="text-gray-600 hover:text-indigo-600 font-medium">Features</button>
              <button onClick={() => {scrollToSection('how-it-works'); setIsMenuOpen(false);}} className="text-gray-600 hover:text-indigo-600 font-medium">How It Works</button>
              <button onClick={() => {scrollToSection('testimonials'); setIsMenuOpen(false);}} className="text-gray-600 hover:text-indigo-600 font-medium">Testimonials</button>
              <button onClick={() => {scrollToSection('pricing'); setIsMenuOpen(false);}} className="text-gray-600 hover:text-indigo-600 font-medium">Pricing</button>
              {!isLoading && (isAuthenticated ? (
                  <>
                  <button
                    onClick={useAuthStore.getState().clearAuth}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors"
                  >
                    Logout
                  </button>

                  <Link 
                    to='/dashboard'
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors text-center"
                  >
                    Go to Dashboard
                  </Link>
                  </>
              ) : (
                <>
        
                  <Link 
                    to='/login'
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors text-center"
                  >
                    Get Started
                  </Link>
                </>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
