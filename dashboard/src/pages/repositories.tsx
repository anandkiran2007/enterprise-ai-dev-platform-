import React from 'react'
import DashboardLayout from '../components/DashboardLayout'

export default function RepositoriesPage() {
  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Repositories</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            Connect repositories and manage indexing, webhooks, and analysis.
          </p>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">No repositories connected</h2>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                Connect a GitHub repository to start tracking commits, PRs, and AI insights.
              </p>
            </div>
            <button className="btn btn-primary">Connect Repo</button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
