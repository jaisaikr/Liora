import { Link, useLocation } from 'react-router-dom'
import { Brain, BarChart3, Settings } from 'lucide-react'

const Header = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Home', icon: Brain },
    { path: '/analysis', label: 'Analysis', icon: BarChart3 },
  ]

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">Liora</span>
            </Link>
          </div>

          <nav className="hidden md:flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="flex items-center space-x-4">
            <button className="text-gray-400 hover:text-gray-500">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header