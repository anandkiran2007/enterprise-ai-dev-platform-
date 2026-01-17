// Common Types
export interface BaseEntity {
  id: string
  created_at: string
  updated_at?: string
}

// User Types
export interface User extends BaseEntity {
  email: string
  name: string
  username?: string
  avatar_url?: string
  github_id: string
}

// Organization Types
export interface Organization extends BaseEntity {
  name: string
  slug: string
  member_count?: number
  repository_count?: number
  description?: string
}

export interface OrganizationMember extends BaseEntity {
  username: string
  email: string
  role: 'admin' | 'maintainer' | 'member'
  joined_at: string
  user_id?: string
}

export interface CreateOrganizationRequest {
  name: string
  slug?: string
  description?: string
}

export interface InviteMemberRequest {
  email: string
  role: 'admin' | 'maintainer' | 'member'
}

// Project Types
export interface Project extends BaseEntity {
  name: string
  description?: string
  status: 'active' | 'archived' | 'deleted'
  repository_count?: number
  last_activity?: string
  organization_id?: string
}

// Repository Types
export interface Repository extends BaseEntity {
  name: string
  full_name: string
  clone_url: string
  branch: string
  sync_status: 'synced' | 'syncing' | 'error' | 'pending'
  last_synced_at?: string
  discovery_status?: 'completed' | 'in_progress' | 'failed' | 'not_started'
  detected_stack?: Record<string, any>
  project_id?: string
  organization_id?: string
}

export interface CreateRepositoryRequest {
  name: string
  full_name: string
  clone_url: string
  branch: string
  project_id?: string
  organization_id?: string
}

// Agent Types
export interface Agent extends BaseEntity {
  name: string
  type: string
  status: 'active' | 'inactive' | 'error' | 'starting' | 'stopping'
  config: Record<string, any>
  last_activity?: string
  metrics?: AgentMetrics
}

export interface AgentMetrics {
  tasks_completed: number
  tasks_failed: number
  average_response_time: number
  uptime_percentage: number
}

export interface AgentTask extends BaseEntity {
  agent_id: string
  type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  started_at?: string
  completed_at?: string
}

export interface CreateAgentRequest {
  name: string
  type: string
  config: Record<string, any>
}

// Settings Types
export interface UserSettings extends BaseEntity {
  user_id: string
  theme: 'light' | 'dark' | 'system'
  language: string
  timezone: string
  notifications: NotificationSettings
  integrations: IntegrationSettings
}

export interface NotificationSettings {
  email: boolean
  push: boolean
  task_completion: boolean
  error_alerts: boolean
  system_updates: boolean
}

export interface IntegrationSettings {
  github: {
    connected: boolean
    username?: string
    token_expires_at?: string
  }
  slack: {
    connected: boolean
    webhook_url?: string
    channel?: string
  }
  discord: {
    connected: boolean
    webhook_url?: string
    channel?: string
  }
}

// Dashboard Types
export interface DashboardMetric {
  title: string
  value: string | number
  change?: {
    value: string
    trend: 'up' | 'down' | 'neutral'
  }
  icon?: string
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}

export interface DashboardActivity {
  id: string
  type: 'build' | 'deploy' | 'commit' | 'error' | 'agent_task'
  message: string
  timestamp: string
  user?: string
  metadata?: Record<string, any>
}

// Discovery Types
export interface DiscoveryReport extends BaseEntity {
  repository_id: string
  detected_stack: Record<string, string[]>
  service_boundaries: Array<{ name: string; files: string[] }>
  dependency_graph: { nodes: string[]; edges: string[][] }
  risk_hotspots: Array<{ file: string; risk: string; reason: string }>
  file_index_summary: {
    total_files: number
    indexed_files: number
    languages: Record<string, number>
  }
}

// API Response Types
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}

export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
}

// Filter and Search Types
export interface SearchFilters {
  query?: string
  organization_id?: string
  project_id?: string
  status?: string
  date_range?: {
    start: string
    end: string
  }
}

export interface PaginationParams {
  page?: number
  limit?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}
