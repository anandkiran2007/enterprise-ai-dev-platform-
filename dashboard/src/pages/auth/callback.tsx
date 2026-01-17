import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '../../contexts/AuthContext'

export default function AuthCallback() {
  const router = useRouter()
  const { login } = useAuth()

  useEffect(() => {
    const { token, error, message } = router.query
    
    if (token && typeof token === 'string') {
      login(token)
      router.push('/dashboard')
      return
    }

    if (error) {
      const errMsg = typeof message === 'string' ? message : 'Authentication failed'
      router.push(`/?error=${encodeURIComponent(String(error))}&message=${encodeURIComponent(errMsg)}`)
      return
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
