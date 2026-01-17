import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import DashboardLayout from '../components/DashboardLayout'
import {
  ChartBarIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  UserGroupIcon,
  DocumentIcon
} from '@heroicons/react/24/outline'

interface Project {
  id: string
  name: string
  description: string
  status: 'active' | 'building' | 'failed' | 'completed'
  repository: string
  lastBuild: string
  buildTime: number
  coverage: number
  team: string[]
}

interface Metric {
  label: string
  value: string | number
  change?: number
  trend?: 'up' | 'down' | 'neutral'
}

export default function DashboardPage() {
  const { state } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate fetching data
    const fetchDashboardData = async () => {
      try {
        // In real app, these would be API calls
        const mockProjects: Project[] = [
          {
            id: '1',
            name: 'E-commerce Platform',
            description: 'AI-powered e-commerce platform with React and Node.js',
            status: 'active',
            repository: 'github.com/company/ecommerce-platform',
            lastBuild: '2024-01-16T22:00:00Z',
            buildTime: 120,
            coverage: 85,
            team: ['Alice Chen', 'Bob Smith', 'Carol Davis']
          },
          {
            id: '2',
            name: 'Mobile App Backend',
            description: 'Flutter mobile app backend with Firebase integration',
            status: 'building',
            repository: 'github.com/company/mobile-app',
            lastBuild: '2024-01-16T20:00:00Z',
            buildTime: 180,
            coverage: 72,
            team: ['David Wilson', 'Eve Brown']
          },
          {
            id: '3',
            name: 'Data Analytics Pipeline',
            description: 'ETL pipeline for real-time data processing',
            status: 'completed',
            repository: 'github.com/company/analytics',
            lastBuild: '2024-01-15T18:00:00Z',
            buildTime: 90,
            coverage: 92,
            team: ['Frank Miller', 'Grace Lee']
          }
        ]

        const mockMetrics: Metric[] = [
          {
            label: 'Total Projects',
            value: 12,
            change: 2,
            trend: 'up'
          },
          {
            label: 'Active Builds',
            value: 3,
            change: -1,
            trend: 'down'
          },
          {
            label: 'Avg Coverage',
            value: '83%',
            change: 5,
            trend: 'up'
          },
          {
            label: 'Team Members',
            value: 8,
            trend: 'neutral'
          }
        ]

        setProjects(mockProjects)
        setMetrics(mockMetrics)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const getStatusIcon = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'building':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'text-green-700 bg-green-100 dark:text-green-300 dark:bg-green-900'
      case 'building':
        return 'text-yellow-700 bg-yellow-100 dark:text-yellow-300 dark:bg-yellow-900'
      case 'failed':
        return 'text-red-700 bg-red-100 dark:text-red-300 dark:bg-red-900'
      case 'completed':
        return 'text-blue-700 bg-blue-100 dark:text-blue-300 dark:bg-blue-900'
      default:
        return 'text-gray-700 bg-gray-100 dark:text-gray-300 dark:bg-gray-900'
    }
  }

  const getTrendIcon = (trend?: Metric['trend']) => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {state.user?.name?.split(' ')[0] || 'User'}!
          </h1>
          <p className="mt-2 text-lg text-gray-600 dark:text-gray-300">
            Here's what's happening with your projects today.
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <ChartBarIcon className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {metric.value}
                    </p>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
                      {metric.label}
                    </p>
                  </div>
                  {metric.trend && (
                    <div className="flex items-center ml-2">
                      {getTrendIcon(metric.trend)}
                      <span className={`text-sm font-medium ${
                        metric.trend === 'up' ? 'text-green-600' : 
                        metric.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {Math.abs(metric.change || 0)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Projects Overview */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Active Projects
            </h2>
            <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              <FolderIcon className="h-5 w-5 mr-2" />
              New Project
            </button>
          </div>

          {/* Projects Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div key={project.id} className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      {getStatusIcon(project.status)}
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                        {project.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex space-x-2">
                      <button className="text-gray-400 hover:text-gray-600">
                        <DocumentIcon className="h-5 w-5" />
                      </button>
                      <button className="text-gray-400 hover:text-gray-600">
                        <UserGroupIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>

                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                    {project.description}
                  </p>

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Repository:</span>
                      <a 
                        href={`https://github.com/${project.repository}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        {project.repository}
                      </a>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Coverage:</span>
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${project.coverage}%` }}
                          />
                        </div>
                        <span className="ml-2 text-sm font-medium text-gray-900 dark:text-white">
                          {project.coverage}%
                        </span>
                      </div>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Build Time:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {project.buildTime}s
                      </span>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Team:</span>
                      <div className="flex items-center">
                        {project.team.slice(0, 2).map((member, index) => (
                          <div key={index} className="w-6 h-6 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center -ml-2 first:ml-0">
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                              {member.split(' ').map(n => n[0]).join('').toUpperCase()}
                            </span>
                          </div>
                        ))}
                        {project.team.length > 2 && (
                          <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                              +{project.team.length - 2}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
