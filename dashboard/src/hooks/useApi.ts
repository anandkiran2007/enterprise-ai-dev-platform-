import { useState, useEffect, useCallback, useRef } from 'react'
import { ApiError } from '../lib/api-client'

// Generic hook state
interface ApiState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
  lastFetched: number | null
}

// Generic hook options
interface UseApiOptions<T> {
  immediate?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: ApiError) => void
  retryCount?: number
  retryDelay?: number
}

// Generic API hook
export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions<T> = {}
) {
  const {
    immediate = true,
    onSuccess,
    onError,
    retryCount = 3,
    retryDelay = 1000
  } = options

  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
    lastFetched: null
  })

  const retryTimeoutRef = useRef<NodeJS.Timeout>()
  const retryCountRef = useRef(0)

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const data = await apiCall()
      setState({
        data,
        loading: false,
        error: null,
        lastFetched: Date.now()
      })
      onSuccess?.(data)
      retryCountRef.current = 0
      return data
    } catch (error) {
      const apiError = error as ApiError
      
      // Retry logic for network errors
      if (retryCountRef.current < retryCount && apiError.status >= 500) {
        retryCountRef.current++
        retryTimeoutRef.current = setTimeout(() => {
          execute()
        }, retryDelay * Math.pow(2, retryCountRef.current - 1))
        return
      }

      setState(prev => ({
        ...prev,
        loading: false,
        error: apiError
      }))
      onError?.(apiError)
      throw apiError
    }
  }, [apiCall, onSuccess, onError, retryCount, retryDelay])

  const reset = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current)
    }
    setState({
      data: null,
      loading: false,
      error: null,
      lastFetched: null
    })
    retryCountRef.current = 0
  }, [])

  const refetch = useCallback(() => {
    return execute()
  }, [execute])

  useEffect(() => {
    if (immediate) {
      execute()
    }

    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [immediate, execute])

  return {
    ...state,
    execute,
    refetch,
    reset
  }
}

// Hook for paginated data
export function usePaginatedApi<T>(
  apiCall: (page: number, limit: number) => Promise<{ data: T[]; total: number; hasMore: boolean }>,
  initialLimit: number = 20
) {
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(initialLimit)
  const [allData, setAllData] = useState<T[]>([])
  const [hasMore, setHasMore] = useState(true)
  const [total, setTotal] = useState(0)

  const {
    data: currentPageData,
    loading,
    error,
    execute,
    refetch
  } = useApi(() => apiCall(page, limit), {
    immediate: true
  })

  useEffect(() => {
    if (currentPageData) {
      setAllData(prev => {
        if (page === 1) {
          return currentPageData.data
        }
        return [...prev, ...currentPageData.data]
      })
      setHasMore(currentPageData.hasMore)
      setTotal(currentPageData.total)
    }
  }, [currentPageData, page])

  const loadMore = useCallback(() => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1)
    }
  }, [loading, hasMore])

  const reset = useCallback(() => {
    setPage(1)
    setAllData([])
    setHasMore(true)
    setTotal(0)
  }, [])

  return {
    data: allData,
    currentPageData,
    loading,
    error,
    hasMore,
    total,
    page,
    limit,
    setPage,
    setLimit,
    loadMore,
    refetch,
    reset
  }
}

// Hook for mutations (POST, PUT, DELETE)
export function useMutation<T, P = any>(
  apiCall: (params: P) => Promise<T>,
  options: {
    onSuccess?: (data: T) => void
    onError?: (error: ApiError) => void
    onSettled?: () => void
  } = {}
) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [data, setData] = useState<T | null>(null)

  const mutate = useCallback(async (params: P) => {
    setLoading(true)
    setError(null)

    try {
      const result = await apiCall(params)
      setData(result)
      options.onSuccess?.(result)
      return result
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError)
      options.onError?.(apiError)
      throw apiError
    } finally {
      setLoading(false)
      options.onSettled?.()
    }
  }, [apiCall, options])

  const reset = useCallback(() => {
    setLoading(false)
    setError(null)
    setData(null)
  }, [])

  return {
    mutate,
    loading,
    error,
    data,
    reset
  }
}

// Hook for real-time data (polling)
export function useRealTimeApi<T>(
  apiCall: () => Promise<T>,
  interval: number = 30000,
  options: UseApiOptions<T> = {}
) {
  const intervalRef = useRef<NodeJS.Timeout>()

  const {
    data,
    loading,
    error,
    refetch
  } = useApi(apiCall, options)

  useEffect(() => {
    if (interval > 0) {
      intervalRef.current = setInterval(() => {
        refetch()
      }, interval)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [interval, refetch])

  return {
    data,
    loading,
    error,
    refetch
  }
}

// Hook for cached data
export function useCachedApi<T>(
  key: string,
  apiCall: () => Promise<T>,
  ttl: number = 300000 // 5 minutes default
) {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
    lastFetched: null
  })

  const getCachedData = useCallback(() => {
    if (typeof window === 'undefined') return null
    
    try {
      const cached = localStorage.getItem(`api_cache_${key}`)
      if (!cached) return null

      const { data, timestamp } = JSON.parse(cached)
      const isExpired = Date.now() - timestamp > ttl

      if (isExpired) {
        localStorage.removeItem(`api_cache_${key}`)
        return null
      }

      return data
    } catch {
      return null
    }
  }, [key, ttl])

  const setCachedData = useCallback((data: T) => {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem(`api_cache_${key}`, JSON.stringify({
        data,
        timestamp: Date.now()
      }))
    } catch {
      // Ignore localStorage errors
    }
  }, [key])

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const data = await apiCall()
      setState({
        data,
        loading: false,
        error: null,
        lastFetched: Date.now()
      })
      setCachedData(data)
      return data
    } catch (error) {
      const apiError = error as ApiError
      setState(prev => ({
        ...prev,
        loading: false,
        error: apiError
      }))
      throw apiError
    }
  }, [apiCall, setCachedData])

  useEffect(() => {
    const cachedData = getCachedData()
    if (cachedData) {
      setState({
        data: cachedData,
        loading: false,
        error: null,
        lastFetched: Date.now()
      })
    } else {
      execute()
    }
  }, [getCachedData, execute])

  return {
    ...state,
    execute,
    refetch: execute
  }
}
