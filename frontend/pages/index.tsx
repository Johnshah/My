import { useState } from 'react'
import Head from 'next/head'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type AppType = 'basic' | 'standard' | 'advanced'
type InputMethod = 'github' | 'upload' | 'prompt'

interface AppTypeDetails {
  name: string
  description: string
  features: string[]
  techStack: string[]
  estimatedTime: string
  color: string
}

const appTypes: Record<AppType, AppTypeDetails> = {
  basic: {
    name: 'Basic',
    description: 'Simple apps with essential features',
    features: [
      'Clean UI with modern design',
      'Basic CRUD operations',
      'Simple authentication',
      'SQLite database',
      'Responsive design',
      'Basic error handling'
    ],
    techStack: ['React', 'FastAPI', 'SQLite', 'TailwindCSS'],
    estimatedTime: '2-5 minutes',
    color: 'green'
  },
  standard: {
    name: 'Standard',
    description: 'Full-featured apps with advanced capabilities',
    features: [
      'Advanced UI with animations',
      'Complete CRUD with relations',
      'JWT authentication & authorization',
      'PostgreSQL/MySQL database',
      'API rate limiting',
      'Comprehensive error handling',
      'File uploads',
      'Email notifications',
      'Search & filtering',
      'Data validation'
    ],
    techStack: ['React', 'Next.js', 'FastAPI', 'PostgreSQL', 'Redis', 'TailwindCSS'],
    estimatedTime: '5-10 minutes',
    color: 'blue'
  },
  advanced: {
    name: 'Advanced (Deep Mode)',
    description: 'Production-ready apps with enterprise features',
    features: [
      'Premium UI with micro-interactions',
      'Complex business logic',
      'Multi-role authentication',
      'Scalable database architecture',
      'Caching layer (Redis)',
      'Real-time features (WebSocket)',
      'Advanced error tracking',
      'File processing & storage',
      'Email & SMS notifications',
      'Advanced search (Elasticsearch)',
      'API versioning',
      'Rate limiting & throttling',
      'Comprehensive logging',
      'Security audits',
      'Performance optimization',
      'Complete test suite',
      'CI/CD pipeline',
      'Docker deployment',
      'Monitoring & analytics'
    ],
    techStack: [
      'React', 'Next.js', 'TypeScript', 'FastAPI', 'PostgreSQL', 
      'Redis', 'Elasticsearch', 'Docker', 'TailwindCSS', 'WebSocket'
    ],
    estimatedTime: '10-20 minutes',
    color: 'purple'
  }
}

export default function Home() {
  const [inputMethod, setInputMethod] = useState<InputMethod>('prompt')
  const [appType, setAppType] = useState<AppType>('standard')
  const [githubUrl, setGithubUrl] = useState('')
  const [prompt, setPrompt] = useState('')
  const [platforms, setPlatforms] = useState<string[]>(['web'])
  const [loading, setLoading] = useState(false)
  const [projectId, setProjectId] = useState('')
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    setMessage('')
    setProgress(0)

    try {
      if (inputMethod === 'github') {
        if (!githubUrl) {
          setError('Please enter a GitHub repository URL')
          setLoading(false)
          return
        }

        // Analyze GitHub repo first
        setMessage('Analyzing GitHub repository...')
        const analyzeResponse = await axios.post(`${API_URL}/api/v1/analyze/github`, {
          repo_url: githubUrl,
          branch: 'main',
          include_analysis: true
        })

        const projectId = analyzeResponse.data.project_id
        setProjectId(projectId)

        // Poll for analysis completion
        let analysisComplete = false
        while (!analysisComplete) {
          await new Promise(resolve => setTimeout(resolve, 2000))
          const statusResponse = await axios.get(`${API_URL}/api/v1/projects/${projectId}`)
          
          if (statusResponse.data.status === 'analyzed') {
            analysisComplete = true
            setMessage('Analysis complete! Generating app from repository...')
            
            // Now generate app based on analyzed repo
            const generateResponse = await axios.post(
              `${API_URL}/api/v1/generate/${appType === 'advanced' ? 'deep-mode' : 'prompt'}`,
              {
                prompt: `Create an app based on the analyzed repository with ${appType} level features and capabilities`,
                app_type: 'full-stack',
                platform: platforms,
                source_repo: githubUrl,
                source_project_id: projectId,
                app_complexity: appType
              }
            )
            
            setProjectId(generateResponse.data.project_id)
            setMessage(generateResponse.data.message)
            pollProgress(generateResponse.data.project_id)
          } else if (statusResponse.data.status === 'error') {
            throw new Error(statusResponse.data.error)
          }
        }
      } else if (inputMethod === 'prompt') {
        if (!prompt) {
          setError('Please describe the app you want to create')
          setLoading(false)
          return
        }

        const endpoint = appType === 'advanced' 
          ? '/api/v1/generate/deep-mode' 
          : '/api/v1/generate/prompt'

        const response = await axios.post(`${API_URL}${endpoint}`, {
          prompt: `${prompt}\n\nApp Complexity: ${appType}\nFeatures: ${appTypes[appType].features.join(', ')}`,
          app_type: 'full-stack',
          platform: platforms
        })

        setProjectId(response.data.project_id)
        setMessage(response.data.message)
        pollProgress(response.data.project_id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred')
      setLoading(false)
    }
  }

  const pollProgress = async (projectId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/projects/${projectId}`)
        const project = response.data

        if (project.progress !== undefined) {
          setProgress(project.progress)
          setMessage(project.progress_message || '')
        }

        if (project.status === 'ready' || project.status === 'completed') {
          clearInterval(interval)
          setLoading(false)
          setProgress(100)
          setMessage('✅ App generated successfully! Ready to download.')
        } else if (project.status === 'error') {
          clearInterval(interval)
          setLoading(false)
          setError(project.error || 'Generation failed')
        }
      } catch (err) {
        console.error('Error polling progress:', err)
      }
    }, 2000)
  }

  const togglePlatform = (platform: string) => {
    if (platforms.includes(platform)) {
      setPlatforms(platforms.filter(p => p !== platform))
    } else {
      setPlatforms([...platforms, platform])
    }
  }

  return (
    <>
      <Head>
        <title>My - Universal AI App Generator</title>
        <meta name="description" content="Generate real, working apps with AI - Completely FREE!" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">My</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">My</h1>
                  <p className="text-xs text-gray-500">Universal AI App Generator</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">100% Free</span>
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">
                  Online
                </span>
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h2 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-4">
              Build Apps with AI
            </h2>
            <p className="text-xl text-gray-600 mb-2">
              Generate real, working, professional applications in minutes
            </p>
            <p className="text-sm text-gray-500">
              From GitHub repos, uploads, or text descriptions • Multi-platform • Completely Free
            </p>
          </div>

          {/* Input Method Selection */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">How do you want to create your app?</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <button
                  onClick={() => setInputMethod('github')}
                  className={`p-4 border-2 rounded-xl transition-all ${
                    inputMethod === 'github'
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="text-3xl mb-2">🔗</div>
                  <div className="font-semibold text-gray-900">GitHub Repository</div>
                  <div className="text-sm text-gray-500 mt-1">
                    Analyze & recreate from repo
                  </div>
                </button>

                <button
                  onClick={() => setInputMethod('upload')}
                  className={`p-4 border-2 rounded-xl transition-all ${
                    inputMethod === 'upload'
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="text-3xl mb-2">📁</div>
                  <div className="font-semibold text-gray-900">Upload Project</div>
                  <div className="text-sm text-gray-500 mt-1">
                    Upload ZIP or folder
                  </div>
                </button>

                <button
                  onClick={() => setInputMethod('prompt')}
                  className={`p-4 border-2 rounded-xl transition-all ${
                    inputMethod === 'prompt'
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="text-3xl mb-2">💬</div>
                  <div className="font-semibold text-gray-900">Describe It</div>
                  <div className="text-sm text-gray-500 mt-1">
                    Tell AI what to build
                  </div>
                </button>
              </div>

              {/* Input Fields */}
              {inputMethod === 'github' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      GitHub Repository URL
                    </label>
                    <input
                      type="url"
                      value={githubUrl}
                      onChange={(e) => setGithubUrl(e.target.value)}
                      placeholder="https://github.com/username/repository"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 mt-2">
                      💡 My will analyze the repo, understand its structure, and generate an improved version
                    </p>
                  </div>
                </div>
              )}

              {inputMethod === 'upload' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Project File
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors cursor-pointer">
                    <div className="text-4xl mb-2">📦</div>
                    <div className="text-gray-600">
                      Drag & drop or click to upload
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      ZIP, TAR, or folder
                    </div>
                  </div>
                </div>
              )}

              {inputMethod === 'prompt' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Describe Your App
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Example: Create a todo list app with user authentication, ability to add/edit/delete tasks, mark tasks as complete, filter by status, and a beautiful dark mode UI with smooth animations..."
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    💡 Be specific! Include features, design preferences, and any special requirements
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* App Type Selection */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Select App Complexity</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(appTypes).map(([key, details]) => (
                  <button
                    key={key}
                    onClick={() => setAppType(key as AppType)}
                    className={`text-left p-4 border-2 rounded-xl transition-all ${
                      appType === key
                        ? `border-${details.color}-600 bg-${details.color}-50`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-lg text-gray-900">{details.name}</span>
                      {appType === key && (
                        <span className="text-2xl">✓</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{details.description}</p>
                    <div className="text-xs text-gray-500 mb-2">
                      ⏱️ {details.estimatedTime}
                    </div>
                    <div className="space-y-1">
                      {details.features.slice(0, 3).map((feature, idx) => (
                        <div key={idx} className="text-xs text-gray-600 flex items-start">
                          <span className="mr-1">•</span>
                          <span>{feature}</span>
                        </div>
                      ))}
                      {details.features.length > 3 && (
                        <div className="text-xs text-gray-500 italic">
                          +{details.features.length - 3} more features
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {/* Selected App Type Details */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {appTypes[appType].name} - Complete Feature List:
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {appTypes[appType].features.map((feature, idx) => (
                    <div key={idx} className="text-sm text-gray-600 flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Tech Stack:</h5>
                  <div className="flex flex-wrap gap-2">
                    {appTypes[appType].techStack.map((tech, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-white border border-gray-300 rounded text-xs text-gray-700"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Platform Selection */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Target Platforms</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { id: 'web', name: 'Web', icon: '🌐' },
                  { id: 'android', name: 'Android', icon: '📱' },
                  { id: 'ios', name: 'iOS', icon: '🍎' },
                  { id: 'desktop', name: 'Desktop', icon: '💻' }
                ].map((platform) => (
                  <button
                    key={platform.id}
                    onClick={() => togglePlatform(platform.id)}
                    className={`p-4 border-2 rounded-xl transition-all ${
                      platforms.includes(platform.id)
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    <div className="text-3xl mb-2">{platform.icon}</div>
                    <div className="font-semibold text-gray-900">{platform.name}</div>
                    {platforms.includes(platform.id) && (
                      <div className="text-xs text-indigo-600 mt-1">✓ Selected</div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <div className="max-w-4xl mx-auto mb-8">
            <button
              onClick={handleGenerate}
              disabled={loading || platforms.length === 0}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
                loading || platforms.length === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating... {progress}%
                </span>
              ) : (
                `🚀 Generate ${appTypes[appType].name} App`
              )}
            </button>
            
            {platforms.length === 0 && (
              <p className="text-center text-sm text-red-500 mt-2">
                Please select at least one platform
              </p>
            )}
          </div>

          {/* Progress Display */}
          {loading && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Generation Progress</h3>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>{message}</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 h-full transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

                {appType === 'advanced' && (
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>🔥 Deep Mode Active - Generating high-quality code...</p>
                    <p>⚡ This may take 10-20 minutes for maximum quality</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-start">
                  <span className="text-2xl mr-3">❌</span>
                  <div>
                    <h4 className="font-semibold text-red-900">Error</h4>
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Success Display */}
          {projectId && !loading && !error && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                <div className="flex items-start mb-4">
                  <span className="text-3xl mr-3">✅</span>
                  <div className="flex-1">
                    <h4 className="font-bold text-green-900 text-lg">App Generated Successfully!</h4>
                    <p className="text-sm text-green-700 mt-1">{message}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="bg-white border-2 border-green-600 text-green-700 px-4 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors">
                    📥 Download Code
                  </button>
                  <button className="bg-white border-2 border-blue-600 text-blue-700 px-4 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                    👁️ Preview App
                  </button>
                  <button className="bg-white border-2 border-purple-600 text-purple-700 px-4 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
                    🔨 Build APK
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-16">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center text-gray-600 text-sm">
              <p className="mb-2">
                Made with ❤️ by My - Universal AI App Generator
              </p>
              <p className="text-xs text-gray-500">
                100% Free Forever • Open Source • No Limits
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  )
}
