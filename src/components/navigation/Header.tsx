import { useAuthStore } from '@/stores/authStore';
import { Link } from 'react-router-dom';

export default function Header() {
  const { isAuthenticated, isLoading } = useAuthStore();
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
            <button className="text-gray-600 hover:text-indigo-600 font-medium">Features</button>
            <button className="text-gray-600 hover:text-indigo-600 font-medium">How It Works</button>
            <button className="text-gray-600 hover:text-indigo-600 font-medium">Testimonials</button>
            <button className="text-gray-600 hover:text-indigo-600 font-medium">Pricing</button>
          </nav>
          
          <div className="flex items-center space-x-4">
            {!isLoading && (isAuthenticated ? (
                <>
                <button
                  onClick={useAuthStore.getState().clearAuth}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors"
                >
                  Logout
                </button>

                {/* <Link 
                  to='/dashboard'
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-xl transition-colors"
                >
                  Go to Dashboard
                </Link> */}
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
        </div>
      </div>
    </header>
  );
}
