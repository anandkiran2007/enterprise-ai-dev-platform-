import React from 'react'
import DashboardLayout from '../components/DashboardLayout'

export default function ProjectsPage() {
  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Projects</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            Create and manage projects across repositories.
          </p>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">No projects yet</h2>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                Create your first project to start tracking builds, coverage, and agents.
              </p>
            </div>
            <button className="btn btn-primary">New Project</button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
