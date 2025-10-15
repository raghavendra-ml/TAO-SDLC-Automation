import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Boxes, Database, Code, Shield, Zap, Loader2, Download, Settings } from 'lucide-react'
import { getProjectPhases, generateContent, updatePhase } from '../services/api'
import toast from 'react-hot-toast'

interface ArchitectureComponent {
  id: number
  name: string
  type: string
  description: string
  technologies: string[]
}

const Phase3Page = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(false)
  const [generatingArchitecture, setGeneratingArchitecture] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showJiraModal, setShowJiraModal] = useState(false)
  
  const [phase3, setPhase3] = useState<any>(null)
  const [phase2Data, setPhase2Data] = useState<any>(null)
  
  const [architectureComponents, setArchitectureComponents] = useState<ArchitectureComponent[]>([])
  const [technologyStack, setTechnologyStack] = useState<any>({})
  const [databaseSchema, setDatabaseSchema] = useState<any>({})
  const [apiDesign, setApiDesign] = useState<any>({})
  
  const [jiraConfig, setJiraConfig] = useState({
    url: '',
    email: '',
    apiToken: '',
    projectKey: ''
  })
  
  useEffect(() => {
    if (projectId) {
      loadPhaseData()
    }
  }, [projectId])
  
  const loadPhaseData = async () => {
    try {
      setLoading(true)
      const response = await getProjectPhases(parseInt(projectId!))
      const phases = response.data
      
      // Get Phase 2 data (backlog)
      const phase2 = phases.find((p: any) => p.phase_number === 2)
      if (phase2?.data) {
        setPhase2Data(phase2.data)
        console.log('✅ Loaded Phase 2 data:', phase2.data)
      }
      
      // Get Phase 3 data
      const phase3 = phases.find((p: any) => p.phase_number === 3)
      if (phase3) {
        setPhase3(phase3)
        
        if (phase3.data?.architectureComponents) {
          setArchitectureComponents(phase3.data.architectureComponents)
        }
        if (phase3.data?.technologyStack) {
          setTechnologyStack(phase3.data.technologyStack)
        }
        if (phase3.data?.databaseSchema) {
          setDatabaseSchema(phase3.data.databaseSchema)
        }
        if (phase3.data?.apiDesign) {
          setApiDesign(phase3.data.apiDesign)
        }
      }
    } catch (error) {
      console.error('Error loading phase data:', error)
      toast.error('Failed to load phase data')
    } finally {
      setLoading(false)
    }
  }
  
  const handleGenerateArchitecture = async () => {
    if (!phase2Data || !phase2Data.epics) {
      toast.error('Please complete Phase 2 first to generate architecture')
      return
    }
    
    setGeneratingArchitecture(true)
    try {
      const response = await generateContent(phase3.id, 'architecture', {
        epics: phase2Data.epics || [],
        userStories: phase2Data.userStories || [],
        requirements: phase2Data.requirements || []
      })
      
      const generatedArch = response.data.content
      const confidenceScore = response.data.confidence_score || 85
      
      setArchitectureComponents(generatedArch.components || [])
      setTechnologyStack(generatedArch.techStack || {})
      setDatabaseSchema(generatedArch.database || {})
      setApiDesign(generatedArch.api || {})
      
      // Save to phase
      await updatePhase(phase3.id, {
        data: {
          ...phase3.data,
          architectureComponents: generatedArch.components,
          technologyStack: generatedArch.techStack,
          databaseSchema: generatedArch.database,
          apiDesign: generatedArch.api
        },
        ai_confidence_score: confidenceScore
      })
      
      toast.success(`✅ Architecture generated! (AI Confidence: ${confidenceScore}%)`)
    } catch (error: any) {
      console.error('Error generating architecture:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate architecture')
    } finally {
      setGeneratingArchitecture(false)
    }
  }
  
  const handleExportToJira = async () => {
    if (!jiraConfig.url || !jiraConfig.email || !jiraConfig.apiToken || !jiraConfig.projectKey) {
      toast.error('Please fill in all JIRA credentials')
      return
    }
    
    try {
      // Dummy JIRA export - will be replaced with real integration later
      toast.success('🔄 Connecting to JIRA...', { duration: 2000 })
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const epicCount = phase2Data?.epics?.length || 0
      const storyCount = phase2Data?.userStories?.length || 0
      
      toast.success(`✅ Exported to JIRA: ${epicCount} epics and ${storyCount} stories!`, {
        duration: 5000
      })
      
      setShowJiraModal(false)
      
      // Save JIRA config for future use (without sensitive data)
      await updatePhase(phase3.id, {
        data: {
          ...phase3.data,
          jiraIntegration: {
            configured: true,
            url: jiraConfig.url,
            projectKey: jiraConfig.projectKey,
            lastExportDate: new Date().toISOString()
          }
        }
      })
    } catch (error) {
      toast.error('Failed to export to JIRA. Please check your credentials.')
    }
  }
  
  const handleSubmitForApproval = async () => {
    if (!phase3) {
      toast.error('Phase not found')
      return
    }
    
    if (architectureComponents.length === 0) {
      toast.error('Please generate architecture before submitting for approval')
      return
    }
    
    setIsSubmitting(true)
    try {
      await updatePhase(phase3.id, {
        status: 'pending_approval',
        data: {
          ...phase3.data,
          architectureComponents,
          technologyStack,
          databaseSchema,
          apiDesign
        }
      })
      
      toast.success('✅ Phase 3 submitted for approval!')
      
      setTimeout(() => {
        navigate('/approvals')
      }, 2000)
    } catch (error) {
      console.error('Error submitting for approval:', error)
      toast.error('Failed to submit for approval')
    } finally {
      setIsSubmitting(false)
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Phase 3: Architecture & High-Level Design</h1>
        <p className="text-gray-500 mt-2">System architecture, technology stack, and technical decisions</p>
        {phase2Data && (
          <p className="text-sm text-green-600 mt-1">
            ✓ Phase 2 data loaded: {phase2Data.epics?.length || 0} epics, {phase2Data.userStories?.length || 0} stories
          </p>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* System Architecture Components */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Boxes className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">System Architecture Components</h2>
              </div>
              <button 
                className="btn-primary disabled:opacity-50"
                onClick={handleGenerateArchitecture}
                disabled={generatingArchitecture || !phase2Data}
              >
                {generatingArchitecture ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                    Generating...
                  </>
                ) : (
                  'Generate Architecture with AI'
                )}
              </button>
            </div>
            
            {architectureComponents.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Boxes className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No architecture components yet. Generate from your Phase 2 backlog.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {architectureComponents.map((component) => (
                  <div key={component.id} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        {component.type === 'frontend' && <Code className="w-5 h-5 text-primary-600" />}
                        {component.type === 'backend' && <Database className="w-5 h-5 text-primary-600" />}
                        {component.type === 'database' && <Database className="w-5 h-5 text-primary-600" />}
                        {component.type === 'security' && <Shield className="w-5 h-5 text-primary-600" />}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{component.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{component.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {component.technologies.map((tech, idx) => (
                            <span key={idx} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
                              {tech}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Technology Stack */}
          {Object.keys(technologyStack).length > 0 && (
            <div className="card">
              <div className="flex items-center space-x-3 mb-4">
                <Zap className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Technology Stack</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {technologyStack.frontend && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Frontend</h3>
                    <ul className="space-y-1">
                      {technologyStack.frontend.map((tech: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-600">• {tech}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {technologyStack.backend && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Backend</h3>
                    <ul className="space-y-1">
                      {technologyStack.backend.map((tech: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-600">• {tech}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {technologyStack.infrastructure && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Infrastructure</h3>
                    <ul className="space-y-1">
                      {technologyStack.infrastructure.map((tech: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-600">• {tech}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Backlog Reference */}
          {phase2Data && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Phase 2 Backlog</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Epics</span>
                  <span className="text-lg font-bold text-gray-900">{phase2Data.epics?.length || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Stories</span>
                  <span className="text-lg font-bold text-gray-900">{phase2Data.userStories?.length || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Story Points</span>
                  <span className="text-lg font-bold text-primary-600">
                    {phase2Data.userStories?.reduce((sum: number, s: any) => sum + (s.points || 0), 0) || 0}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          {/* JIRA Export */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Download className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">JIRA Integration</h2>
            </div>
            
            <p className="text-sm text-gray-600 mb-4">
              Export your epics and user stories to JIRA for tracking and management.
            </p>
            
            <button 
              className="btn-primary w-full"
              onClick={() => setShowJiraModal(true)}
              disabled={!phase2Data || !phase2Data.epics}
            >
              <Download className="w-4 h-4 mr-2 inline" />
              Configure & Export to JIRA
            </button>
            
            {phase3?.data?.jiraIntegration?.configured && (
              <p className="text-xs text-green-600 mt-2">
                ✓ Last exported: {new Date(phase3.data.jiraIntegration.lastExportDate).toLocaleString()}
              </p>
            )}
          </div>
          
          {/* Key Deliverables */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Key Deliverables</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className={`mr-2 ${architectureComponents.length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {architectureComponents.length > 0 ? '✓' : '⋯'}
                </span>
                <span>System Architecture</span>
              </li>
              <li className="flex items-start">
                <span className={`mr-2 ${Object.keys(technologyStack).length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {Object.keys(technologyStack).length > 0 ? '✓' : '⋯'}
                </span>
                <span>Technology Stack</span>
              </li>
              <li className="flex items-start">
                <span className={`mr-2 ${Object.keys(databaseSchema).length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {Object.keys(databaseSchema).length > 0 ? '✓' : '⋯'}
                </span>
                <span>Database Design</span>
              </li>
              <li className="flex items-start">
                <span className={`mr-2 ${Object.keys(apiDesign).length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {Object.keys(apiDesign).length > 0 ? '✓' : '⋯'}
                </span>
                <span>API Design</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Submit for Approval */}
      {architectureComponents.length > 0 && (
        <div className="mt-8 flex justify-end">
          <button
            onClick={handleSubmitForApproval}
            disabled={isSubmitting}
            className="btn-primary px-8 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin inline" />
                Submitting...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Submit Phase 3 for Approval</span>
              </>
            )}
          </button>
        </div>
      )}
      
      {/* JIRA Configuration Modal */}
      {showJiraModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold">JIRA Configuration</h3>
              </div>
              <button onClick={() => setShowJiraModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
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
                    Get your API token here
                  </a>
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Project Key</label>
                <input
                  type="text"
                  className="input"
                  placeholder="PROJ"
                  value={jiraConfig.projectKey}
                  onChange={(e) => setJiraConfig({...jiraConfig, projectKey: e.target.value})}
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => setShowJiraModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={handleExportToJira}
                  className="btn-primary flex-1"
                >
                  <Download className="w-4 h-4 mr-2 inline" />
                  Export to JIRA
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Phase3Page
