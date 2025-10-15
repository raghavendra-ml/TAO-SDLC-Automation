import { Rocket, Server, Activity, FileText, AlertCircle, CheckCircle2, Play } from 'lucide-react'

const Phase6Page = () => {
  const deploymentStages = [
    { name: 'Staging', status: 'completed', url: 'https://staging.example.com' },
    { name: 'Production', status: 'pending', url: 'https://example.com' },
  ]

  const monitoringMetrics = [
    { name: 'Uptime', value: '99.9%', status: 'good', icon: Activity },
    { name: 'Response Time', value: '145ms', status: 'good', icon: Activity },
    { name: 'Error Rate', value: '0.02%', status: 'good', icon: AlertCircle },
    { name: 'CPU Usage', value: '45%', status: 'warning', icon: Server },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Phase 6: Deployment, Release & Operations</h1>
        <p className="text-gray-500 mt-2">Release to production and monitor system performance</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Deployment Pipeline */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Rocket className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Deployment Pipeline</h2>
              </div>
              <button className="btn-primary flex items-center space-x-2">
                <Play className="w-4 h-4" />
                <span>Deploy to Production</span>
              </button>
            </div>

            <div className="space-y-4">
              {deploymentStages.map((stage, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    stage.status === 'completed'
                      ? 'border-green-500 bg-green-50'
                      : stage.status === 'in_progress'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{stage.name} Environment</h3>
                      <p className="text-sm text-gray-600 mt-1">{stage.url}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      {stage.status === 'completed' && (
                        <CheckCircle2 className="w-6 h-6 text-green-600" />
                      )}
                      {stage.status === 'pending' && (
                        <button className="btn-primary text-sm">Deploy</button>
                      )}
                    </div>
                  </div>

                  {stage.status === 'completed' && (
                    <div className="mt-3 grid grid-cols-3 gap-3 pt-3 border-t border-green-200">
                      <div className="text-center">
                        <p className="text-xs text-gray-600">Deployed</p>
                        <p className="text-sm font-medium text-gray-900">2 hours ago</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-600">Build</p>
                        <p className="text-sm font-medium text-gray-900">#245</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-600">Version</p>
                        <p className="text-sm font-medium text-gray-900">v1.2.3</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* CI/CD Integration */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Server className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">CI/CD Pipeline</h2>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium text-gray-900">Build #245</p>
                    <p className="text-xs text-gray-500">main branch • 2 hours ago</p>
                  </div>
                </div>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded font-medium">
                  Passed
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <div>
                    <p className="font-medium text-gray-900">Build #246</p>
                    <p className="text-xs text-gray-500">develop branch • Running...</p>
                  </div>
                </div>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded font-medium">
                  In Progress
                </span>
              </div>
            </div>

            <button className="btn-secondary w-full mt-4">View Pipeline History</button>
          </div>

          {/* Monitoring Dashboard */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Activity className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">System Monitoring</h2>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {monitoringMetrics.map((metric, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <metric.icon className="w-5 h-5 text-gray-600" />
                    <span
                      className={`text-xs font-medium px-2 py-1 rounded ${
                        metric.status === 'good'
                          ? 'bg-green-100 text-green-800'
                          : metric.status === 'warning'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {metric.status}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  <p className="text-sm text-gray-600">{metric.name}</p>
                </div>
              ))}
            </div>

            <button className="btn-primary w-full mt-4">Open Full Dashboard</button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Deployment Checklist */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <FileText className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Deployment Checklist</h2>
            </div>

            <div className="space-y-2">
              {[
                { item: 'Run all tests', done: true },
                { item: 'Update documentation', done: true },
                { item: 'Database backup', done: true },
                { item: 'Notify stakeholders', done: false },
                { item: 'Monitor for 1 hour', done: false },
              ].map((task, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={task.done}
                    className="w-4 h-4 text-primary-600 rounded"
                    readOnly
                  />
                  <span className={`text-sm ${task.done ? 'line-through text-gray-500' : 'text-gray-700'}`}>
                    {task.item}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Rollback Plan */}
          <div className="card bg-yellow-50">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Rollback Plan</h2>
            <p className="text-sm text-gray-600 mb-4">
              If issues are detected, the system can automatically rollback to the previous stable version.
            </p>
            <button className="btn-secondary w-full text-red-600 border-red-300 hover:bg-red-50">
              Initiate Rollback
            </button>
          </div>

          {/* Documentation */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Documentation</h2>
            <div className="space-y-2">
              <button className="w-full text-left p-2 hover:bg-gray-50 rounded text-sm">
                📄 Release Notes v1.2.3
              </button>
              <button className="w-full text-left p-2 hover:bg-gray-50 rounded text-sm">
                📘 User Guide
              </button>
              <button className="w-full text-left p-2 hover:bg-gray-50 rounded text-sm">
                🔧 Admin Manual
              </button>
              <button className="w-full text-left p-2 hover:bg-gray-50 rounded text-sm">
                🚨 Runbook
              </button>
            </div>
            <button className="btn-primary w-full mt-4">Generate Documentation</button>
          </div>

          {/* Integrations */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Tool Integrations</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">GitHub</span>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Jira</span>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Confluence</span>
                <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not Connected</span>
              </div>
            </div>
            <button className="btn-secondary w-full mt-4">Manage Integrations</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Phase6Page

