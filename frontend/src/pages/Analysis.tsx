import { useState } from 'react'
import { Upload, FileText, Globe, BarChart3, TrendingUp, AlertCircle } from 'lucide-react'

const Analysis = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'results'>('upload')
  const [files, setFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files))
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      const fileInput = event.currentTarget.querySelector('input[type="file"]') as HTMLInputElement
      fileInput?.click()
    }
  }

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    // Simulate analysis delay
    setTimeout(() => {
      setIsAnalyzing(false)
      setActiveTab('results')
    }, 3000)
  }

  const mockResults = {
    overallScore: 8.2,
    recommendation: 'Strong Investment Opportunity',
    keyMetrics: [
      { label: 'Market Potential', value: '9.1', color: 'text-green-600' },
      { label: 'Team Strength', value: '8.7', color: 'text-green-600' },
      { label: 'Product Viability', value: '7.8', color: 'text-yellow-600' },
      { label: 'Financial Health', value: '7.5', color: 'text-yellow-600' },
    ],
    insights: [
      'Strong founding team with relevant industry experience',
      'Large addressable market with growing demand',
      'Competitive product differentiation identified',
      'Revenue growth trajectory shows positive momentum'
    ],
    risks: [
      'High competition in target market segment',
      'Dependency on key partnerships for distribution',
      'Limited runway based on current burn rate'
    ]
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Startup Analysis</h1>
        <p className="text-lg text-gray-600">
          Upload founder materials and company data to generate comprehensive investment insights
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
            activeTab === 'upload'
              ? 'bg-white text-primary-600 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Upload Materials
        </button>
        <button
          onClick={() => setActiveTab('results')}
          className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
            activeTab === 'results'
              ? 'bg-white text-primary-600 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Analysis Results
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Upload Founder Materials
            </h2>
            
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors"
              tabIndex={0}
              onKeyDown={handleKeyDown}
              role="button"
              aria-describedby="file-upload-description"
            >
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-2" id="file-upload-description">
                <p className="text-lg font-medium text-gray-900">
                  Drop files here or click to browse
                </p>
                <p className="text-gray-500">
                  Supported formats: PDF, DOC, PPT, XLS, TXT
                </p>
              </div>
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt"
                aria-label="Upload founder materials - supported formats: PDF, DOC, PPT, XLS, TXT"
              />
            </div>

            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                <h3 className="font-medium text-gray-900">Uploaded Files:</h3>
                {files.map((file, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                    <FileText className="h-4 w-4" />
                    <span>{file.name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Company Information
            </h2>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter company name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., SaaS, Fintech, Healthcare"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Website
                </label>
                <input
                  type="url"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  placeholder="https://company.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Funding Stage
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500">
                  <option>Pre-seed</option>
                  <option>Seed</option>
                  <option>Series A</option>
                  <option>Series B</option>
                  <option>Series C+</option>
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={files.length === 0 || isAnalyzing}
            className="w-full py-3 px-6 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
          </button>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-primary-100 rounded-full mb-4">
              <span className="text-3xl font-bold text-primary-600">
                {mockResults.overallScore}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {mockResults.recommendation}
            </h2>
            <p className="text-gray-600">
              Based on comprehensive analysis of founder materials and market data
            </p>
          </div>

          {/* Key Metrics */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Key Metrics
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {mockResults.keyMetrics.map((metric, index) => (
                <div key={index} className="flex justify-between items-center py-2">
                  <span className="text-gray-700">{metric.label}</span>
                  <span className={`font-bold ${metric.color}`}>
                    {metric.value}/10
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Insights & Risks */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Key Insights
              </h3>
              <ul className="space-y-2">
                {mockResults.insights.map((insight, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 text-yellow-600" />
                Risk Factors
              </h3>
              <ul className="space-y-2">
                {mockResults.risks.map((risk, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-gray-700">{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="flex space-x-4">
            <button className="flex-1 py-3 px-6 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors">
              Download Report
            </button>
            <button className="flex-1 py-3 px-6 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors">
              Share Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Analysis