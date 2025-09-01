import { Link } from 'react-router-dom'
import { ArrowRight, Brain, Target, TrendingUp, Shield } from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning algorithms analyze founder materials and market data to provide deep insights.'
    },
    {
      icon: Target,
      title: 'Investment Focus',
      description: 'Get clear, actionable investment recommendations based on comprehensive startup evaluation.'
    },
    {
      icon: TrendingUp,
      title: 'Market Intelligence',
      description: 'Leverage public data and market trends to understand startup positioning and potential.'
    },
    {
      icon: Shield,
      title: 'Risk Assessment',
      description: 'Comprehensive risk analysis helps you make informed investment decisions with confidence.'
    }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900">
            AI-Powered Startup
            <span className="text-primary-600 block">Analysis Platform</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Liora synthesizes founder materials and public data to generate concise, 
            actionable investment insights for smarter startup evaluation.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/analysis"
            className="inline-flex items-center px-6 py-3 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors"
          >
            Start Analysis
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
          <button className="inline-flex items-center px-6 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
            Watch Demo
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-gray-900">
            Why Choose Liora?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our platform combines cutting-edge AI with comprehensive market data 
            to deliver unparalleled startup analysis capabilities.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 rounded-2xl p-8 md:p-12 text-center text-white">
        <div className="space-y-4">
          <h2 className="text-3xl font-bold">
            Ready to Transform Your Investment Process?
          </h2>
          <p className="text-primary-100 text-lg max-w-2xl mx-auto">
            Join forward-thinking investors who use Liora to make data-driven 
            decisions and identify the next generation of successful startups.
          </p>
          <Link
            to="/analysis"
            className="inline-flex items-center px-8 py-4 rounded-lg bg-white text-primary-600 font-semibold hover:bg-gray-50 transition-colors"
          >
            Get Started Now
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home