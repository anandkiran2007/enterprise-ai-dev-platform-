import React, { useState } from 'react'
import DashboardLayout from '../components/DashboardLayout'
import { useAuth } from '../contexts/AuthContext'
import {
  FolderIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowPathIcon,
  EyeIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  EllipsisHorizontalIcon
} from '@heroicons/react/24/outline'
import { repositoriesService } from '../services/repositories.service'
import { Repository, DiscoveryReport } from '../types'
import { useApi, useMutation } from '../hooks/useApi'

export default function RepositoriesPage() {
  const { state } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedOrg, setSelectedOrg] = useState<string>('all')
  const [selectedProject, setSelectedProject] = useState<string>('all')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showDiscoveryModal, setShowDiscoveryModal] = useState<string | null>(null)

  // Fetch repositories using BFF service
  const {
    data: repositoriesData,
    loading,
    error,
    refetch
  } = useApi(() => repositoriesService.getRepositories({
    query: searchQuery || undefined,
    organization_id: selectedOrg !== 'all' ? selectedOrg : undefined,
    project_id: selectedProject !== 'all' ? selectedProject : undefined
  }), {
    immediate: true
  })

  // Sync repository mutation
  const { mutate: syncRepository } = useMutation(
    (repoId: string) => repositoriesService.syncRepository(repoId),
    {
      onSuccess: () => {
        refetch()
      }
    }
  )

  // Discovery mutation
  const { mutate: startDiscovery } = useMutation(
    (repoId: string) => repositoriesService.startDiscovery(repoId),
    {
      onSuccess: (report) => {
        // Show discovery modal with the report
        setShowDiscoveryModal(report.repository_id)
      }
    }
  )

  // Get discovery report
  const {
    data: discoveryReport,
    loading: discoveryLoading
  } = useApi(
    () => showDiscoveryModal ? repositoriesService.getDiscoveryReport(showDiscoveryModal) : Promise.reject(new Error('No repo selected')),
    {
      immediate: false
    }
  )

  const repositories = repositoriesData?.data || []

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'synced':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'syncing':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      synced: 'badge-success',
      syncing: 'badge-warning',
      error: 'badge-error',
      pending: 'badge-gray'
    }
    return <span className={`badge ${styles[status as keyof typeof styles] || 'badge-gray'}`}>{status}</span>
  }

  const handleSync = async (repoId: string) => {
    try {
      await syncRepository(repoId)
    } catch (error) {
      console.error('Failed to sync repository:', error)
    }
  }

  const handleDiscovery = async (repoId: string) => {
    try {
      await startDiscovery(repoId)
    } catch (error) {
      console.error('Failed to start discovery:', error)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="animate-pulse">
          <div className="flex justify-between items-center mb-6">
            <div className="skeleton h-8 w-32" />
            <div className="skeleton h-10 w-32" />
          </div>
          <div className="card">
            <div className="card-header">
              <div className="skeleton h-6 w-24" />
            </div>
            <div className="card-body">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton h-16 w-full mb-3" />
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="text-red-500 mb-4">
              <ExclamationTriangleIcon className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Failed to load repositories
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {error.message}
            </p>
            <button onClick={refetch} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Repositories</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Manage and monitor your code repositories
            </p>
          </div>
          <button 
            onClick={() => setShowAddModal(true)}
            className="btn btn-primary"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Repository
          </button>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search repositories..."
                    className="input pl-10"
                  />
                </div>
              </div>

              {/* Organization Filter */}
              <div className="w-full lg:w-48">
                <select 
                  value={selectedOrg}
                  onChange={(e) => setSelectedOrg(e.target.value)}
                  className="select"
                >
                  <option value="all">All Organizations</option>
                  {/* TODO: Fetch organizations from service */}
                </select>
              </div>

              {/* Project Filter */}
              <div className="w-full lg:w-48">
                <select 
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="select"
                >
                  <option value="all">All Projects</option>
                  {/* TODO: Fetch projects from service */}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Repositories Table */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                All Repositories ({repositories.length})
              </h2>
              <button className="btn btn-ghost btn-sm">
                <FunnelIcon className="h-4 w-4 mr-1" />
                Filters
              </button>
            </div>
          </div>
          <div className="card-body p-0">
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th className="table-header text-left">Repository</th>
                    <th className="table-header text-left">Branch</th>
                    <th className="table-header text-left">Sync Status</th>
                    <th className="table-header text-left">Last Synced</th>
                    <th className="table-header text-left">Discovery</th>
                    <th className="table-header text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {repositories.map((repo) => (
                    <tr key={repo.id} className="table-row">
                      <td className="table-cell">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <FolderIcon className="h-5 w-5 text-gray-400" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {repo.name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {repo.full_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="badge badge-gray">{repo.branch}</span>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(repo.sync_status)}
                          {getStatusBadge(repo.sync_status)}
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {repo.last_synced_at ? new Date(repo.last_synced_at).toLocaleDateString() : 'Never'}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-2">
                          {repo.discovery_status === 'completed' && (
                            <CheckCircleIcon className="h-4 w-4 text-green-500" />
                          )}
                          {repo.discovery_status === 'in_progress' && (
                            <ClockIcon className="h-4 w-4 text-yellow-500" />
                          )}
                          {repo.discovery_status === 'failed' && (
                            <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                          )}
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {repo.discovery_status || 'not started'}
                          </span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleSync(repo.id)}
                            className="btn btn-ghost btn-sm"
                            disabled={repo.sync_status === 'syncing'}
                          >
                            <ArrowPathIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDiscovery(repo.id)}
                            className="btn btn-ghost btn-sm"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          <div className="relative">
                            <button className="btn btn-ghost btn-sm">
                              <EllipsisHorizontalIcon className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Discovery Modal */}
        {showDiscoveryModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Discovery Report
                  </h3>
                  <button
                    onClick={() => setShowDiscoveryModal(null)}
                    className="btn btn-ghost btn-sm"
                  >
                    ×
                  </button>
                </div>
              </div>
              <div className="card-body">
                {discoveryLoading ? (
                  <div className="text-center py-8">
                    <div className="spinner h-8 w-8 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">Running discovery analysis...</p>
                  </div>
                ) : discoveryReport ? (
                  <div className="space-y-6">
                    {/* Detected Stack */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Detected Stack</h4>
                      <div className="space-y-2">
                        {Object.entries(discoveryReport.detected_stack).map(([tech, files]) => (
                          <div key={tech} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                            <span className="text-sm font-medium">{tech}</span>
                            <span className="text-xs text-gray-500">{Array.isArray(files) ? files.length : 1} files</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* File Index Summary */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">File Index Summary</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
                          <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {discoveryReport.file_index_summary.total_files}
                          </div>
                          <div className="text-xs text-gray-500">Total Files</div>
                        </div>
                        <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
                          <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {discoveryReport.file_index_summary.indexed_files}
                          </div>
                          <div className="text-xs text-gray-500">Indexed Files</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
