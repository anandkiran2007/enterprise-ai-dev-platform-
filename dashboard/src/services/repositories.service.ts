import { apiClient, ApiError } from '../lib/api-client'
import { 
  Repository, 
  CreateRepositoryRequest, 
  DiscoveryReport,
  PaginatedResponse,
  SearchFilters,
  PaginationParams
} from '../types'

export class RepositoriesService {
  private static instance: RepositoriesService

  static getInstance(): RepositoriesService {
    if (!RepositoriesService.instance) {
      RepositoriesService.instance = new RepositoriesService()
    }
    return RepositoriesService.instance
  }

  // Get all repositories
  async getRepositories(filters?: SearchFilters, pagination?: PaginationParams): Promise<PaginatedResponse<Repository>> {
    try {
      const params = { ...filters, ...pagination }
      const response = await apiClient.get<PaginatedResponse<Repository>>('/repositories', params)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch repositories')
    }
  }

  // Get single repository
  async getRepository(id: string): Promise<Repository> {
    try {
      const response = await apiClient.get<Repository>(`/repositories/${id}`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch repository')
    }
  }

  // Create new repository
  async createRepository(data: CreateRepositoryRequest): Promise<Repository> {
    try {
      const response = await apiClient.post<Repository>('/repositories', data)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to create repository')
    }
  }

  // Update repository
  async updateRepository(id: string, data: Partial<Repository>): Promise<Repository> {
    try {
      const response = await apiClient.put<Repository>(`/repositories/${id}`, data)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to update repository')
    }
  }

  // Delete repository
  async deleteRepository(id: string): Promise<void> {
    try {
      await apiClient.delete(`/repositories/${id}`)
    } catch (error) {
      throw this.handleError(error, 'Failed to delete repository')
    }
  }

  // Sync repository
  async syncRepository(id: string): Promise<Repository> {
    try {
      const response = await apiClient.post<Repository>(`/repositories/${id}/sync`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to sync repository')
    }
  }

  // Get sync status
  async getSyncStatus(id: string): Promise<{
    status: 'synced' | 'syncing' | 'error' | 'pending'
    last_synced_at?: string
    error_message?: string
  }> {
    try {
      const response = await apiClient.get(`/repositories/${id}/sync-status`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to get sync status')
    }
  }

  // Start discovery analysis
  async startDiscovery(id: string): Promise<DiscoveryReport> {
    try {
      const response = await apiClient.post<DiscoveryReport>(`/repositories/${id}/discovery`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to start discovery')
    }
  }

  // Get discovery report
  async getDiscoveryReport(id: string): Promise<DiscoveryReport> {
    try {
      const response = await apiClient.get<DiscoveryReport>(`/repositories/${id}/discovery`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to get discovery report')
    }
  }

  // Get discovery status
  async getDiscoveryStatus(id: string): Promise<{
    status: 'completed' | 'in_progress' | 'failed' | 'not_started'
    progress?: number
    started_at?: string
    completed_at?: string
  }> {
    try {
      const response = await apiClient.get(`/repositories/${id}/discovery-status`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to get discovery status')
    }
  }

  // Get repository branches
  async getBranches(id: string): Promise<string[]> {
    try {
      const response = await apiClient.get<string[]>(`/repositories/${id}/branches`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch branches')
    }
  }

  // Change default branch
  async changeBranch(id: string, branch: string): Promise<Repository> {
    try {
      const response = await apiClient.patch<Repository>(`/repositories/${id}/branch`, { branch })
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to change branch')
    }
  }

  // Get repository statistics
  async getRepositoryStats(id: string): Promise<{
    total_commits: number
    total_branches: number
    total_contributors: number
    last_commit_at: string
    languages: Record<string, number>
    file_count: number
  }> {
    try {
      const response = await apiClient.get(`/repositories/${id}/stats`)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch repository statistics')
    }
  }

  // Search repositories
  async searchRepositories(query: string): Promise<Repository[]> {
    try {
      const response = await apiClient.get<Repository[]>('/repositories/search', { query })
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to search repositories')
    }
  }

  // Bulk sync multiple repositories
  async bulkSync(repositoryIds: string[]): Promise<{
    success: string[]
    failed: Array<{ id: string; error: string }>
  }> {
    try {
      const response = await apiClient.post('/repositories/bulk-sync', { repository_ids: repositoryIds })
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to bulk sync repositories')
    }
  }

  // Get repository activity
  async getActivity(id: string, pagination?: PaginationParams): Promise<PaginatedResponse<{
    type: string
    message: string
    timestamp: string
    user?: string
    metadata?: Record<string, any>
  }>> {
    try {
      const params = pagination || {}
      const response = await apiClient.get<PaginatedResponse<any>>(`/repositories/${id}/activity`, params)
      return response.data
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch repository activity')
    }
  }

  // Error handling helper
  private handleError(error: any, defaultMessage: string): ApiError {
    if (error instanceof ApiError) {
      return error
    }
    
    if (error.response?.status === 401) {
      return new ApiError('Authentication required. Please log in again.', 401, 'UNAUTHORIZED')
    }
    
    if (error.response?.status === 403) {
      return new ApiError('You do not have permission to perform this action.', 403, 'FORBIDDEN')
    }
    
    if (error.response?.status === 404) {
      return new ApiError('The requested repository was not found.', 404, 'NOT_FOUND')
    }
    
    if (error.response?.status === 422) {
      const validationErrors = error.response.data?.errors
      if (validationErrors) {
        const message = Object.values(validationErrors).flat().join(', ')
        return new ApiError(message, 422, 'VALIDATION_ERROR')
      }
    }
    
    return new ApiError(defaultMessage, error.response?.status, 'UNKNOWN_ERROR', error.response?.data)
  }
}

// Export singleton instance
export const repositoriesService = RepositoriesService.getInstance()
