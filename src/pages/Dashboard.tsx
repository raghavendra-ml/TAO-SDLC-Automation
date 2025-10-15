import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, FolderOpen, Activity, Trash2, Download, Settings, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import { getProjects, deleteProject } from '../services/api'
import { useProjectStore } from '../store/projectStore'
import CreateProjectModal from '../components/modals/CreateProjectModal'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showJiraModal, setShowJiraModal] = useState(false)
  const [jiraConnected, setJiraConnected] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const { projects, setProjects } = useProjectStore()
  
  const [jiraConfig, setJiraConfig] = useState({
    url: '',
    email: '',
    apiToken: '',
    projectKey: ''
  })
  
  const [jiraStats, setJiraStats] = useState({
    projects: 0,
    issues: 0,
    inProgress: 0,
    completed: 0
  })
  
  const loadProjects = () => {
    setLoading(true)
    console.log('📊 Loading projects...')
    getProjects()
      .then((res) => {
        console.log('✅ Projects loaded:', res.data)
        setProjects(res.data)
        setLoading(false)
      })
      .catch((error) => {
        console.error('❌ Error loading projects:', error)
        toast.error('Failed to load projects')
        setLoading(false)
      })
  }
  
  const handleDeleteProject = async (e: React.MouseEvent, projectId: number, projectName: string) => {
    e.preventDefault() // Prevent navigation to project
    e.stopPropagation()
    
    if (!confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      return
    }
    
    try {
      await deleteProject(projectId)
      toast.success('Project deleted successfully')
      loadProjects() // Reload projects list
    } catch (error) {
      console.error('Error deleting project:', error)
      toast.error('Failed to delete project')
    }
  }

  useEffect(() => {
    loadProjects()
    // Load JIRA config from localStorage
    const savedJiraConfig = localStorage.getItem('jira_config')
    if (savedJiraConfig) {
      const config = JSON.parse(savedJiraConfig)
      setJiraConfig(config)
      setJiraConnected(true)
    }
    
    // Load JIRA stats from localStorage
    const savedJiraStats = localStorage.getItem('jira_stats')
    if (savedJiraStats) {
      const stats = JSON.parse(savedJiraStats)
      setJiraStats(stats)
    }
  }, [])
  
  const handleConnectJira = async () => {
    if (!jiraConfig.url || !jiraConfig.email || !jiraConfig.apiToken) {
      toast.error('Please fill in all JIRA credentials')
      return
    }
    
    try {
      // Dummy JIRA connection - will be replaced with real API later
      toast.success('🔄 Connecting to JIRA...', { duration: 2000 })
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Save config (without sensitive token in production)
      localStorage.setItem('jira_config', JSON.stringify(jiraConfig))
      setJiraConnected(true)
      setShowJiraModal(false)
      
      toast.success('✅ Connected to JIRA successfully!')
      
      // Auto-fetch data after connection
      await handleSyncJira()
    } catch (error) {
      toast.error('Failed to connect to JIRA. Please check your credentials.')
    }
  }
  
  const handleSyncJira = async () => {
    if (!jiraConnected) {
      toast.error('Please connect to JIRA first')
      return
    }
    
    setIsSyncing(true)
    try {
      toast.success('🔄 Syncing with JIRA...', { duration: 2000 })
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Dummy JIRA data - will be replaced with real API call
      const dummyStats = {
        projects: Math.floor(Math.random() * 10) + 5,
        issues: Math.floor(Math.random() * 100) + 50,
        inProgress: Math.floor(Math.random() * 30) + 20,
        completed: Math.floor(Math.random() * 50) + 40
      }
      
      setJiraStats(dummyStats)
      localStorage.setItem('jira_stats', JSON.stringify(dummyStats))
      
      toast.success(`✅ Synced: ${dummyStats.projects} projects, ${dummyStats.issues} issues`)
    } catch (error) {
      toast.error('Failed to sync with JIRA')
    } finally {
      setIsSyncing(false)
    }
  }
  
  const handleDisconnectJira = () => {
    if (confirm('Are you sure you want to disconnect from JIRA?')) {
      localStorage.removeItem('jira_config')
      localStorage.removeItem('jira_stats')
      setJiraConnected(false)
      setJiraConfig({ url: '', email: '', apiToken: '', projectKey: '' })
      setJiraStats({ projects: 0, issues: 0, inProgress: 0, completed: 0 })
      toast.success('Disconnected from JIRA')
    }
  }
  
  const getPhaseColor = (phase: number) => {
    const colors = ['bg-blue-500', 'bg-purple-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500']
    return colors[phase - 1] || 'bg-gray-500'
  }
  
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Manage your SDLC projects with AI assistance</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>New Project</span>
        </button>
      </div>

      <CreateProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadProjects}
      />
      
      {/* JIRA Integration Section */}
      <div className="mb-6 card bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
              <Download className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">JIRA Integration</h2>
              <div className="flex items-center space-x-2 mt-1">
                {jiraConnected ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">Connected</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-500">Not connected</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {jiraConnected ? (
              <>
                <button
                  onClick={handleSyncJira}
                  disabled={isSyncing}
                  className="btn-secondary flex items-center space-x-2 disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
                  <span>{isSyncing ? 'Syncing...' : 'Sync JIRA Data'}</span>
                </button>
                <button
                  onClick={handleDisconnectJira}
                  className="text-sm text-red-600 hover:text-red-700 px-3 py-2"
                >
                  Disconnect
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowJiraModal(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Connect to JIRA</span>
              </button>
            )}
          </div>
        </div>
        
        {/* JIRA Stats */}
        {jiraConnected && jiraStats.projects > 0 && (
          <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{jiraStats.projects}</p>
              <p className="text-xs text-gray-600 mt-1">JIRA Projects</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{jiraStats.issues}</p>
              <p className="text-xs text-gray-600 mt-1">Total Issues</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{jiraStats.inProgress}</p>
              <p className="text-xs text-gray-600 mt-1">In Progress</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{jiraStats.completed}</p>
              <p className="text-xs text-gray-600 mt-1">Completed</p>
            </div>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <>
            {[1, 2, 3].map((i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </>
        ) : projects.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No projects yet. Create your first project to get started.</p>
          </div>
        ) : (
          projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="card group cursor-pointer relative"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{project.description}</p>
                </div>
                <button
                  onClick={(e) => handleDeleteProject(e, project.id, project.name)}
                  className="ml-2 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete project"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-gray-400" />
                  <span className="text-xs text-gray-500">Phase {project.current_phase} of 5</span>
                </div>
                <div className={`${getPhaseColor(project.current_phase)} w-2 h-2 rounded-full`}></div>
              </div>
              
              <div className="mt-4 bg-gray-100 rounded-full h-2">
                <div
                  className={`${getPhaseColor(project.current_phase)} h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${(project.current_phase / 5) * 100}%` }}
                />
              </div>
            </Link>
          ))
        )}
      </div>
      
      {/* JIRA Configuration Modal */}
      {showJiraModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold">Connect to JIRA</h3>
              </div>
              <button onClick={() => setShowJiraModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <p className="text-sm text-gray-600 mb-4">
              Connect your JIRA workspace to sync projects, issues, and track progress across platforms.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">JIRA URL</label>
                <input
                  type="text"
                  className="input"
                  placeholder="https://your-domain.atlassian.net"
                  value={jiraConfig.url}
                  onChange={(e) => setJiraConfig({...jiraConfig, url: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  className="input"
                  placeholder="your-email@company.com"
                  value={jiraConfig.email}
                  onChange={(e) => setJiraConfig({...jiraConfig, email: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">API Token</label>
                <input
                  type="password"
                  className="input"
                  placeholder="Your JIRA API token"
                  value={jiraConfig.apiToken}
                  onChange={(e) => setJiraConfig({...jiraConfig, apiToken: e.target.value})}
                />
                <p className="text-xs text-gray-500 mt-1">
                  <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                    Generate API token →
                  </a>
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Key <span className="text-gray-400">(Optional)</span>
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="PROJ"
                  value={jiraConfig.projectKey}
                  onChange={(e) => setJiraConfig({...jiraConfig, projectKey: e.target.value})}
                />
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-xs text-blue-800">
                  <strong>Note:</strong> This is a demo integration. Your credentials are stored locally for demonstration purposes. In production, they will be securely encrypted and stored server-side.
                </p>
              </div>
              
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => setShowJiraModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConnectJira}
                  className="btn-primary flex-1"
                >
                  <Download className="w-4 h-4 mr-2 inline" />
                  Connect
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard

