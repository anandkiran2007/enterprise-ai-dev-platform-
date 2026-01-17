import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useAuth } from '../contexts/AuthContext'
import {
  ChartBarIcon,
  CogIcon,
  DocumentTextIcon,
  FolderIcon,
  UserGroupIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  BellIcon,
  MagnifyingGlassIcon,
  CpuChipIcon,
  HomeIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

interface SidebarItem {
  name: string
  href: string
  icon: React.ComponentType<any>
  current?: boolean
  children?: SidebarItem[]
}

const sidebarItems: SidebarItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderIcon
  },
  {
    name: 'Repositories',
    href: '/repositories',
    icon: DocumentTextIcon
  },
  {
    name: 'Organizations',
    href: '/organizations',
    icon: UserGroupIcon
  },
  {
    name: 'Agents',
    href: '/agents',
    icon: CpuChipIcon
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: CogIcon
  }
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { state, logout } = useAuth()
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showNotifications, setShowNotifications] = useState(false)

  useEffect(() => {
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!state.token && !storedToken) {
      router.replace('/')
    }
  }, [state.token, router])

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle('dark')
  }

  const currentPath = router.pathname
  const currentSidebarItem = sidebarItems.find(item => item.href === currentPath)

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600/80 backdrop-blur-xs lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={clsx(
        "fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center px-6 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center space-x-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-sm">
                <span className="text-sm font-bold">AI</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Enterprise AI</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">Development Platform</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            <div className="space-y-1">
              {sidebarItems.map((item) => {
                const Icon = item.icon
                const isActive = currentPath === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={clsx(
                      "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                      isActive
                        ? "bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300"
                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    )}
                  >
                    <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                    {item.name}
                    {isActive && (
                      <div className="ml-auto h-2 w-2 rounded-full bg-primary-600" />
                    )}
                  </Link>
                )
              })}
            </div>

            {/* User Section */}
            <div className="border-t border-gray-200 dark:border-gray-800 pt-4 mt-4">
              <div className="px-3 py-2">
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                      {state.user?.name?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {state.user?.name || 'Unknown User'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {state.user?.email || 'user@example.com'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="mt-3 w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors duration-200"
                >
                  <ArrowRightOnRectangleIcon className="mr-2 h-4 w-4" />
                  Sign Out
                </button>
              </div>
            </div>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-72">
        {/* Top Bar */}
        <div className="sticky top-0 z-30 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            {/* Left side - Mobile menu button and breadcrumbs */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 lg:hidden"
              >
                <Bars3Icon className="h-5 w-5" />
              </button>
              
              {currentSidebarItem && (
                <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                  <span>Enterprise AI</span>
                  <ChevronDownIcon className="h-4 w-4" />
                  <span className="font-medium text-gray-900 dark:text-white">
                    {currentSidebarItem.name}
                  </span>
                </div>
              )}
            </div>

            {/* Right side - Search, notifications, theme toggle */}
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="hidden md:block">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search..."
                    className="w-64 pl-10 pr-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors duration-200"
                  />
                </div>
              </div>

              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 relative"
                >
                  <BellIcon className="h-5 w-5" />
                  <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
                </button>
                
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2">
                    <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">Notifications</h3>
                    </div>
                    <div className="py-2">
                      <div className="px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                        <p className="text-sm text-gray-900 dark:text-white">New repository added</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">2 minutes ago</p>
                      </div>
                      <div className="px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                        <p className="text-sm text-gray-900 dark:text-white">Agent completed task</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">5 minutes ago</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Dark Mode Toggle */}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800"
              >
                {darkMode ? (
                  <SunIcon className="h-5 w-5" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="relative">
          <div className="py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
