import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'

interface User {
  id: string
  email: string
  name: string
  username?: string
  avatar_url?: string
  github_id: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
}

interface AuthContextType {
  state: AuthState
  login: (token: string) => Promise<void>
  logout: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }

const initialState: AuthState = {
  user: null,
  token: null,
  isLoading: false,
  error: null,
}

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null }
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        error: null,
      }
    case 'LOGIN_ERROR':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        error: action.payload,
      }
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        error: null,
      }
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    default:
      return state
  }
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    const user = localStorage.getItem('auth_user')
    
    if (token && user) {
      try {
        const parsedUser = JSON.parse(user)
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user: parsedUser, token }
        })
      } catch (error) {
        console.error('Failed to parse stored user data:', error)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
      }
    }
  }, [])

  const login = async (token: string) => {
    try {
      setLoading(true)
      
      // Decode JWT token to get user info (you might want to do this server-side)
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.ok) {
        const userData = await response.json()
        localStorage.setItem('auth_token', token)
        localStorage.setItem('auth_user', JSON.stringify(userData))
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user: userData, token }
        })
      } else {
        throw new Error('Authentication failed')
      }
    } catch (error: any) {
      dispatch({ type: 'LOGIN_ERROR', payload: error.message })
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    dispatch({ type: 'LOGOUT' })
  }

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading })
  }

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error })
  }

  const value: AuthContextType = {
    state,
    login,
    logout,
    setLoading,
    setError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
