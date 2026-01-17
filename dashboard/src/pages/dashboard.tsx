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
  DocumentIcon,
  EllipsisHorizontalIcon,
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

type ActivityType = 'build' | 'deploy' | 'commit' | 'error'

interface Activity {
  id: string
  type: ActivityType
  message: string
  timestamp: string
  user: string
}

type MetricTrend = 'up' | 'down' | 'neutral'
type MetricColor = 'blue' | 'green' | 'yellow' | 'red' | 'purple'

interface MetricChange {
  value: string
  trend: MetricTrend
}

interface Metric {
  label: string
  value: string | number
  title: string
  color: MetricColor
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  change?: MetricChange
}

export default function DashboardPage() {
  const { state } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      // Mock projects with full Project shape
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
          team: ['Alice Chen', 'Bob Smith', 'Carol Davis'],
        },
        {
          id: '2',
          name: 'Mobile App API',
          description: 'Backend API for mobile clients',
          status: 'building',
          repository: 'github.com/company/mobile-api',
          lastBuild: '2024-01-16T21:30:00Z',
          buildTime: 95,
          coverage: 78,
          team: ['John Doe', 'Eve Martinez'],
        },
        {
          id: '3',
          name: 'Data Analytics Dashboard',
          description: 'Analytics dashboard for business metrics',
          status: 'completed',
          repository: 'github.com/company/analytics-dashboard',
          lastBuild: '2024-01-15T18:00:00Z',
          buildTime: 110,
          coverage: 92,
          team: ['Mike Johnson', 'Sarah Wilson'],
        },
        {
          id: '4',
          name: 'AI Content Generator',
          description: 'AI-based content generation tool',
          status: 'failed',
          repository: 'github.com/company/ai-content',
          lastBuild: '2024-01-16T20:10:00Z',
          buildTime: 60,
          coverage: 65,
          team: ['Jane Smith', 'Tom Lee'],
        },
      ]

      const mockMetrics: Metric[] = [
        {
          label: 'Active Projects',
          title: 'Projects currently in progress',
          value: 3,
          color: 'blue',
          icon: FolderIcon,
          change: { value: '+1 this week', trend: 'up' },
        },
        {
          label: 'Build Success Rate',
          title: 'Successful builds in the last 24h',
          value: '92%',
          color: 'green',
          icon: CheckCircleIcon,
          change: { value: '+4%', trend: 'up' },
        },
        {
          label: 'Mean Build Time',
          title: 'Average build duration',
          value: '104s',
          color: 'yellow',
          icon: ClockIcon,
          change: { value: '-8s', trend: 'down' },
        },
        {
          label: 'Open Incidents',
          title: 'Current build/ deploy incidents',
          value: 2,
          color: 'red',
          icon: ExclamationTriangleIcon,
          change: { value: '+1', trend: 'up' },
        },
      ]

      const mockActivities: Activity[] = [
        {
          id: '1',
          type: 'build',
          message: 'Mobile App API build completed successfully',
          timestamp: '5 minutes ago',
          user: 'John Doe',
        },
        {
          id: '2',
          type: 'commit',
          message: 'New features pushed to e-commerce-frontend',
          timestamp: '1 hour ago',
          user: 'Jane Smith',
        },
        {
          id: '3',
          type: 'deploy',
          message: 'Analytics dashboard deployed to production',
          timestamp: '2 hours ago',
          user: 'Mike Johnson',
        },
        {
          id: '4',
          type: 'error',
          message: 'AI Content Generator build failed',
          timestamp: '3 hours ago',
          user: 'Sarah Wilson',
        },
      ]

      setProjects(mockProjects)
      setMetrics(mockMetrics)
      setActivities(mockActivities)
      setIsLoading(false)
    }

    loadData()
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

  const getStatusBadge = (status: Project['status']) => {
    const styles: Record<Project['status'], string> = {
      active: 'badge-success',
      building: 'badge-warning',
      failed: 'badge-error',
      completed: 'badge-primary',
    }
    return <span className={`badge ${styles[status]}`}>{status}</span>
  }

  const getActivityIcon = (type: ActivityType) => {
    switch (type) {
      case 'build':
        return <ChartBarIcon className="h-4 w-4 text-blue-500" />
      case 'deploy':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
      case 'commit':
        return <DocumentIcon className="h-4 w-4 text-purple-500" />
      case 'error':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
      default:
        return <DocumentIcon className="h-4 w-4 text-gray-500" />
    }
  }

  const getMetricColor = (color: MetricColor) => {
    const colors: Record<MetricColor, string> = {
      blue: 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300',
      green:
        'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300',
      yellow:
        'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300',
      red: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
      purple:
        'bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300',
    }
    return colors[color]
  }

  const getTrendIcon = (trend?: MetricTrend) => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card p-6">
                <div className="skeleton h-8 w-20 mb-2" />
                <div className="skeleton h-12 w-16 mb-4" />
                <div className="skeleton h-4 w-24" />
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 card p-6">
              <div className="skeleton h-6 w-32 mb-4" />
              {[...Array(4)].map((_, i) => (
                <div key={i} className="skeleton h-16 w-full mb-3" />
              ))}
            </div>
            <div className="card p-6">
              <div className="skeleton h-6 w-24 mb-4" />
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton h-12 w-full mb-2" />
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Welcome back! Here&apos;s what&apos;s happening with your projects
            today.
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric, index) => {
            const Icon = metric.icon
            return (
              <div key={index} className="card-hover p-6">
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-lg ${getMetricColor(metric.color)}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <button className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                    <EllipsisHorizontalIcon className="h-5 w-5 text-gray-400" />
                  </button>
                </div>
                <div className="mt-4">
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {metric.value}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {metric.title}
                  </p>
                  {metric.change && (
                    <div className="flex items-center mt-2">
                      {getTrendIcon(metric.change.trend)}
                      <span
                        className={`text-sm ml-1 ${
                          metric.change.trend === 'up'
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}
                      >
                        {metric.change.value}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Projects & Activity sections would go here, using projects and activities state */}
        {/* Example: map over projects and render cards, using getStatusIcon/getStatusBadge and coverage/team UI you had */}
      </div>
    </DashboardLayout>
  )
}
