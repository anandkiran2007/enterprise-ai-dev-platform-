import React from 'react'
import DashboardLayout from '../components/DashboardLayout'

export default function AgentsPage() {
  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agents</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            Monitor agent runs, queues, and execution health.
          </p>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Agent monitoring</h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            Next step: connect this page to the Agents API for real-time status.
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}
