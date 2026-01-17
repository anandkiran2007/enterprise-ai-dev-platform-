import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function AuthCallback() {
  const router = useRouter()

  useEffect(() => {
    const { token } = router.query
    
    if (token && typeof token === 'string') {
      // Store token in localStorage
      localStorage.setItem('auth_token', token)
      
      // Redirect to dashboard
      router.push('/dashboard')
    } else {
      // No token found, redirect to login
      router.push('/')
    }
  }, [router.query, router])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing authentication...</p>
      </div>
    </div>
  )
}
