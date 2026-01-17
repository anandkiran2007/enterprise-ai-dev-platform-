import React from 'react'
import DashboardLayout from '../components/DashboardLayout'

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            Configure integrations, tokens, and environment preferences.
          </p>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">General</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">API Base URL</label>
              <input className="input mt-1 dark:bg-gray-900 dark:border-gray-700 dark:text-white" placeholder="http://localhost" disabled />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Environment</label>
              <input className="input mt-1 dark:bg-gray-900 dark:border-gray-700 dark:text-white" placeholder="development" disabled />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
