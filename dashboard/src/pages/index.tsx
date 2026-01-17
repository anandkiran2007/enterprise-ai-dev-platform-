import { useState, useEffect } from 'react'

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('auth_token')
    if (token) {
      setIsAuthenticated(true)
      // Redirect to dashboard if already logged in
      window.location.href = '/dashboard'
    }
  }, [])

  const handleLogin = async () => {
    setIsLoading(true)
    // Redirect to GitHub OAuth authorize endpoint
    window.location.href = '/api/auth/github/authorize'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex min-h-screen">
        <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
          <div className="mx-auto w-full max-w-sm lg:w-96">
            <div>
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                Enterprise AI Platform
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                Sign in to access your AI development dashboard
              </p>
            </div>

            <div className="mt-8">
              {isAuthenticated ? (
                <div className="text-center">
                  <h3 className="text-lg font-medium text-gray-900">
                    Welcome back!
                  </h3>
                  <p className="mt-2 text-sm text-gray-600">
                    You are now signed in to Enterprise AI Platform.
                  </p>
                  <button
                    onClick={() => window.location.href = '/dashboard'}
                    className="mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Go to Dashboard
                  </button>
                </div>
              ) : (
                <div>
                  <button
                    onClick={handleLogin}
                    disabled={isLoading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                  >
                    {isLoading ? 'Signing in...' : 'Sign in with GitHub'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="hidden lg:block relative w-0 flex-1">
          <div className="absolute inset-0 bg-primary-600">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-primary-700 opacity-90" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <h1 className="text-4xl font-bold mb-4">
                  Enterprise AI Development Platform
                </h1>
                <p className="text-xl mb-8">
                  Build, deploy, and manage AI-powered applications with ease
                </p>
                <div className="grid grid-cols-2 gap-8 max-w-2xl mx-auto">
                  <div className="text-center">
                    <div className="text-3xl font-bold mb-2">10+</div>
                    <div className="text-sm">AI Agents</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold mb-2">100%</div>
                    <div className="text-sm">Automation</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold mb-2">24/7</div>
                    <div className="text-sm">Monitoring</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold mb-2">Enterprise</div>
                    <div className="text-sm">Security</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
