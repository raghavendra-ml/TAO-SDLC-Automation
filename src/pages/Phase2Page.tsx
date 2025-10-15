import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Calendar, Target, Users, TrendingUp, ListChecks, Loader2, Plus, ChevronDown, ChevronUp } from 'lucide-react'
import { getProjectPhases, generateContent, updatePhase, getProject } from '../services/api'
import toast from 'react-hot-toast'
import { useProjectStore } from '../store/projectStore'

interface Epic {
  id: number
  title: string
  description?: string
  stories: number
  points: number
  priority: 'High' | 'Medium' | 'Low'
  requirements_mapped?: string[]
}

interface UserStory {
  id: number
  epic: string
  epic_id: number
  title: string
  description?: string
  acceptance_criteria?: string[]
  points: number
  priority: 'High' | 'Medium' | 'Low'
  sprint?: number | null
  status?: string
}

const Phase2Page = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { currentProject } = useProjectStore()
  
  const [epics, setEpics] = useState<Epic[]>([])
  const [userStories, setUserStories] = useState<UserStory[]>([])
  const [phase1Data, setPhase1Data] = useState<any>(null)
  const [phase2, setPhase2] = useState<any>(null)
  const [project, setProject] = useState<any>(null)
  
  const [loading, setLoading] = useState(false)
  const [generatingEpics, setGeneratingEpics] = useState(false)
  const [generatingStories, setGeneratingStories] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [capacityCalculated, setCapacityCalculated] = useState(false)
  
  const [teamSize, setTeamSize] = useState(3)
  const [sprintDuration, setSprintDuration] = useState('2 weeks')
  const [velocity, setVelocity] = useState(25)
  
  const [expandedStory, setExpandedStory] = useState<number | null>(null)

  useEffect(() => {
    if (projectId) {
      loadPhaseData()
      loadProjectData()
    }
  }, [projectId])

  const loadProjectData = async () => {
    try {
      const response = await getProject(parseInt(projectId!))
      setProject(response.data)
    } catch (error) {
      console.error('Error loading project:', error)
    }
  }

  const loadPhaseData = async () => {
    try {
      setLoading(true)
      const response = await getProjectPhases(parseInt(projectId!))
      const phases = response.data

      // Get Phase 1 data
      const phase1 = phases.find((p: any) => p.phase_number === 1)
      if (phase1?.data) {
        setPhase1Data(phase1.data)
        console.log('✅ Loaded Phase 1 data:', phase1.data)
      }

      // Get Phase 2 data
      const phase2 = phases.find((p: any) => p.phase_number === 2)
      if (phase2) {
        setPhase2(phase2)
        
        // Load existing epics and stories if available
        if (phase2.data?.epics) {
          setEpics(phase2.data.epics)
          console.log(`✅ Loaded ${phase2.data.epics.length} existing epics`)
        }
        
        if (phase2.data?.userStories) {
          setUserStories(phase2.data.userStories)
          console.log(`✅ Loaded ${phase2.data.userStories.length} existing user stories`)
        }
        
        // Load resource planning data
        if (phase2.data?.resource_planning) {
          setTeamSize(phase2.data.resource_planning.team_size || 3)
          setSprintDuration(phase2.data.resource_planning.sprint_duration || '2 weeks')
          setVelocity(phase2.data.resource_planning.velocity || 25)
        }
      }
    } catch (error) {
      console.error('Error loading phase data:', error)
      toast.error('Failed to load phase data')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateEpics = async () => {
    if (!phase1Data) {
      toast.error('Please complete Phase 1 first before generating epics')
      return
    }

    if (!phase1Data.requirements && !phase1Data.gherkinRequirements) {
      toast.error('No requirements found in Phase 1. Please add requirements first.')
      return
    }

    setGeneratingEpics(true)
    try {
      const response = await generateContent(phase2.id, 'epics', {
        requirements: phase1Data.requirements || [],
        gherkinRequirements: phase1Data.gherkinRequirements || [],
        prd: phase1Data.prd,
        brd: phase1Data.brd,
        project: project
      })

      const generatedEpics = response.data.content
      const confidenceScore = response.data.confidence_score || 88
      setEpics(generatedEpics)
      
      toast.success(`✅ Generated ${generatedEpics.length} epics! (AI Confidence: ${confidenceScore}%)`)
      
      // Save epics and confidence score to phase data
      await updatePhase(phase2.id, {
        data: { 
          ...phase2.data, 
          epics: generatedEpics 
        },
        ai_confidence_score: confidenceScore
      })
      
      console.log('✅ Epics generated and saved:', generatedEpics)
    } catch (error: any) {
      console.error('Error generating epics:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate epics')
    } finally {
      setGeneratingEpics(false)
    }
  }

  const handleGenerateUserStories = async () => {
    if (epics.length === 0) {
      toast.error('Please generate Epics first before creating user stories')
      return
    }

    setGeneratingStories(true)
    try {
      const response = await generateContent(phase2.id, 'user_stories', {
        epics: epics,
        gherkinRequirements: phase1Data?.gherkinRequirements || [],
        requirements: phase1Data?.requirements || [],
        project: project
      })

      const generatedStories = response.data.content
      const confidenceScore = response.data.confidence_score || 88
      setUserStories(generatedStories)
      
      toast.success(`✅ Generated ${generatedStories.length} user stories! (AI Confidence: ${confidenceScore}%)`)
      
      // Save stories and confidence score to phase data
      await updatePhase(phase2.id, {
        data: { 
          ...phase2.data, 
          epics: epics,
          userStories: generatedStories 
        },
        ai_confidence_score: confidenceScore
      })
      
      console.log('✅ User stories generated and saved:', generatedStories)
    } catch (error: any) {
      console.error('Error generating user stories:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate user stories')
    } finally {
      setGeneratingStories(false)
    }
  }

  const calculateCapacity = async () => {
    if (!teamSize || teamSize < 1) {
      toast.error('Please enter a valid team size')
      return
    }
    
    if (!velocity || velocity < 1) {
      toast.error('Please enter a valid team velocity')
      return
    }
    
    try {
      // Calculate detailed capacity metrics
      const hoursPerPerson = sprintDuration === '2 weeks' ? 80 : sprintDuration === '3 weeks' ? 120 : 160
      const totalHoursPerSprint = teamSize * hoursPerPerson
      const capacityUtilization = (velocity * 8) / totalHoursPerSprint * 100 // Assuming 8 hours per point
      
      const capacityMetrics = {
        team_size: teamSize,
        sprint_duration: sprintDuration,
        velocity: velocity,
        hours_per_sprint: totalHoursPerSprint,
        capacity_utilization: Math.round(capacityUtilization),
        sprints_needed: totalSprints,
        estimated_completion: `${totalTimeline.toFixed(1)} weeks`
      }
      
      // Save resource planning data with metrics
      await updatePhase(phase2.id, {
        data: {
          ...phase2.data,
          epics: epics,
          userStories: userStories,
          resource_planning: capacityMetrics
        }
      })
      
      setCapacityCalculated(true)
      toast.success(`✅ Capacity Calculated: ${totalHoursPerSprint}h per sprint, ${capacityUtilization.toFixed(0)}% utilization`, {
        duration: 5000
      })
    } catch (error) {
      toast.error('Failed to calculate capacity')
    }
  }

  const handleSubmitForApproval = async () => {
    if (!phase2) {
      toast.error('Phase not found')
      return
    }
    
    if (epics.length === 0) {
      toast.error('Please generate epics before submitting for approval')
      return
    }
    
    if (userStories.length === 0) {
      toast.error('Please generate user stories before submitting for approval')
      return
    }
    
    if (!capacityCalculated) {
      toast.error('Please calculate capacity before submitting for approval')
      return
    }
    
    setIsSubmitting(true)
    try {
      // Update phase status to pending_approval
      await updatePhase(phase2.id, {
        status: 'pending_approval',
        data: {
          ...phase2.data,
          epics: epics,
          userStories: userStories,
          resource_planning: {
            team_size: teamSize,
            sprint_duration: sprintDuration,
            velocity: velocity
          }
        }
      })
      
      toast.success(`✅ Phase 2 submitted for approval! Product backlog with ${epics.length} epics and ${userStories.length} stories.`)
      
      // Navigate to approvals page after a short delay
      setTimeout(() => {
        navigate('/approvals')
      }, 2000)
    } catch (error) {
      console.error('Error submitting for approval:', error)
      toast.error('Failed to submit for approval. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Calculate metrics
  const totalPoints = userStories.reduce((sum, story) => sum + story.points, 0)
  const estimatedHours = totalPoints * 8 // Rough estimate: 8 hours per point
  const weeksPerSprint = sprintDuration === '2 weeks' ? 2 : sprintDuration === '3 weeks' ? 3 : 4
  const totalSprints = Math.ceil(totalPoints / velocity)
  const estimatedWeeks = totalSprints * weeksPerSprint
  const bufferWeeks = estimatedWeeks * 0.2 // 20% buffer
  const totalTimeline = estimatedWeeks + bufferWeeks

  const highPriorityStories = userStories.filter(s => s.priority === 'High').length
  const mediumPriorityStories = userStories.filter(s => s.priority === 'Medium').length

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
        <h1 className="text-3xl font-bold text-gray-900">Phase 2: Planning & Product Backlog</h1>
        <p className="text-gray-500 mt-2">Plan effort, create backlog, and define sprint schedule</p>
        {phase1Data && (
          <p className="text-sm text-green-600 mt-1">
            ✓ Phase 1 data loaded: {phase1Data.gherkinRequirements?.length || phase1Data.requirements?.length || 0} requirements available
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Epics */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Target className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Epics</h2>
                {epics.length > 0 && (
                  <span className="text-sm text-gray-500">({epics.length})</span>
                )}
              </div>
              <button 
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleGenerateEpics}
                disabled={generatingEpics || !phase1Data}
              >
                {generatingEpics ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                    Generating...
                  </>
                ) : (
                  'Generate Epics with AI'
                )}
              </button>
            </div>

            {epics.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Target className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No epics yet. Generate epics from your Phase 1 requirements.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {epics.map((epic) => (
                  <div key={epic.id} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{epic.title}</h3>
                        {epic.description && (
                          <p className="text-sm text-gray-600 mt-1">{epic.description}</p>
                        )}
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                          <span>{epic.stories} stories</span>
                          <span>•</span>
                          <span>{epic.points} points</span>
                          <span>•</span>
                          <span className={`font-medium ${
                            epic.priority === 'High' ? 'text-red-600' : 
                            epic.priority === 'Medium' ? 'text-yellow-600' : 
                            'text-green-600'
                          }`}>{epic.priority}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {epics.length > 0 && (
              <button className="btn-secondary w-full mt-4">
                <Plus className="w-4 h-4 mr-2 inline" />
                Add Epic Manually
              </button>
            )}
          </div>

          {/* User Stories */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <ListChecks className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">User Stories</h2>
                {userStories.length > 0 && (
                  <span className="text-sm text-gray-500">({userStories.length})</span>
                )}
              </div>
              <button 
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleGenerateUserStories}
                disabled={generatingStories || epics.length === 0}
              >
                {generatingStories ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                    Generating...
                  </>
                ) : (
                  'Generate Stories with AI'
                )}
              </button>
            </div>

            {userStories.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <ListChecks className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No user stories yet. Generate stories from your epics.</p>
                {epics.length === 0 && (
                  <p className="text-sm mt-2">Tip: Generate epics first</p>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {userStories.map((story) => (
                  <div key={story.id} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded font-medium">
                          {story.epic}
                        </span>
                        <p className="text-gray-900 mt-2 font-medium">{story.title}</p>
                        {story.description && (
                          <p className="text-sm text-gray-600 mt-1">{story.description}</p>
                        )}
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-xs text-gray-500">Points: {story.points}</span>
                          <span className={`text-xs font-medium ${
                            story.priority === 'High' ? 'text-red-600' : 
                            story.priority === 'Medium' ? 'text-yellow-600' : 
                            'text-green-600'
                          }`}>{story.priority}</span>
                          {story.sprint && (
                            <span className="text-xs text-gray-500">Sprint {story.sprint}</span>
                          )}
                        </div>
                        
                        {/* Acceptance Criteria (expandable) */}
                        {story.acceptance_criteria && story.acceptance_criteria.length > 0 && (
                          <div className="mt-3">
                            <button
                              onClick={() => setExpandedStory(expandedStory === story.id ? null : story.id)}
                              className="text-xs text-primary-600 hover:text-primary-700 flex items-center"
                            >
                              {expandedStory === story.id ? (
                                <>
                                  <ChevronUp className="w-3 h-3 mr-1" />
                                  Hide Acceptance Criteria
                                </>
                              ) : (
                                <>
                                  <ChevronDown className="w-3 h-3 mr-1" />
                                  Show Acceptance Criteria ({story.acceptance_criteria.length})
                                </>
                              )}
                            </button>
                            
                            {expandedStory === story.id && (
                              <div className="mt-2 pl-4 border-l-2 border-primary-200">
                                {story.acceptance_criteria.map((criteria, idx) => (
                                  <div key={idx} className="text-xs text-gray-600 mb-2 whitespace-pre-line">
                                    {criteria}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {userStories.length > 0 && (
              <button className="btn-secondary w-full mt-4">
                <Plus className="w-4 h-4 mr-2 inline" />
                Add User Story Manually
              </button>
            )}
          </div>

          {/* Sprint Planning */}
          {userStories.length > 0 && (
            <div className="card">
              <div className="flex items-center space-x-3 mb-4">
                <Calendar className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Sprint Planning</h2>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-blue-50 rounded-lg text-center">
                  <p className="text-2xl font-bold text-blue-600">{totalSprints}</p>
                  <p className="text-sm text-gray-600 mt-1">Total Sprints</p>
                </div>

                <div className="p-4 bg-green-50 rounded-lg text-center">
                  <p className="text-2xl font-bold text-green-600">{totalPoints}</p>
                  <p className="text-sm text-gray-600 mt-1">Total Points</p>
                </div>

                <div className="p-4 bg-purple-50 rounded-lg text-center">
                  <p className="text-2xl font-bold text-purple-600">{velocity}</p>
                  <p className="text-sm text-gray-600 mt-1">Points/Sprint</p>
                </div>
              </div>

              <div className="space-y-3">
                {Array.from({ length: totalSprints }, (_, i) => i + 1).map((sprint) => (
                  <div key={sprint} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium text-gray-900">Sprint {sprint}</span>
                    <span className="text-sm text-gray-600">{velocity} points • {sprintDuration}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Resource Planning */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Users className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Resource Planning</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Team Size</label>
                <input 
                  type="number" 
                  className="input mt-1" 
                  value={teamSize}
                  onChange={(e) => setTeamSize(parseInt(e.target.value) || 0)}
                  min="1"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Sprint Duration</label>
                <select 
                  className="input mt-1"
                  value={sprintDuration}
                  onChange={(e) => setSprintDuration(e.target.value)}
                >
                  <option>2 weeks</option>
                  <option>3 weeks</option>
                  <option>4 weeks</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Team Velocity</label>
                <input 
                  type="number" 
                  className="input mt-1" 
                  placeholder="Story points per sprint" 
                  value={velocity}
                  onChange={(e) => setVelocity(parseInt(e.target.value) || 0)}
                  min="1"
                />
              </div>

              <button 
                className={`w-full py-3 rounded-lg font-medium transition-all ${
                  capacityCalculated 
                    ? 'bg-green-100 text-green-700 border-2 border-green-300' 
                    : 'bg-primary-600 text-white hover:bg-primary-700'
                }`}
                onClick={calculateCapacity}
              >
                {capacityCalculated ? (
                  <>
                    <svg className="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Capacity Calculated
                  </>
                ) : (
                  'Calculate Team Capacity'
                )}
              </button>
            </div>
          </div>

          {/* Effort Estimation */}
          {userStories.length > 0 && (
            <div className="card">
              <div className="flex items-center space-x-3 mb-4">
                <TrendingUp className="w-5 h-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-gray-900">Effort Estimation</h2>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Story Points</span>
                  <span className="text-lg font-bold text-gray-900">{totalPoints}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Estimated Hours</span>
                  <span className="text-lg font-bold text-gray-900">{estimatedHours}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Estimated Duration</span>
                  <span className="text-lg font-bold text-primary-600">{estimatedWeeks.toFixed(1)} weeks</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Buffer (20%)</span>
                  <span className="text-lg font-bold text-gray-900">{bufferWeeks.toFixed(1)} weeks</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Total Timeline</span>
                  <span className="text-xl font-bold text-green-600">{totalTimeline.toFixed(1)} weeks</span>
                </div>
              </div>
            </div>
          )}

          {/* Backlog Stats */}
          {(epics.length > 0 || userStories.length > 0) && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Backlog Statistics</h2>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Epics</span>
                  <span className="text-lg font-bold text-gray-900">{epics.length}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Stories</span>
                  <span className="text-lg font-bold text-gray-900">{userStories.length}</span>
                </div>

                {userStories.length > 0 && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">High Priority</span>
                      <span className="text-lg font-bold text-red-600">{highPriorityStories}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Medium Priority</span>
                      <span className="text-lg font-bold text-yellow-600">{mediumPriorityStories}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Key Deliverables */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Key Deliverables</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className={`mr-2 ${epics.length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {epics.length > 0 ? '✓' : '⋯'}
                </span>
                <span>Product Backlog</span>
              </li>
              <li className="flex items-start">
                <span className={`mr-2 ${userStories.length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {userStories.length > 0 ? '✓' : '⋯'}
                </span>
                <span>Sprint Plan</span>
              </li>
              <li className="flex items-start">
                <span className={`mr-2 ${totalSprints > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                  {totalSprints > 0 ? '✓' : '⋯'}
                </span>
                <span>Release Roadmap</span>
              </li>
              <li className="flex items-start">
                <span className="text-gray-400 mr-2">⋯</span>
                <span>Resource Allocation Plan</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Submit for Approval Section */}
      {epics.length > 0 && userStories.length > 0 && (
        <div className="mt-8 flex justify-end">
          <button
            onClick={handleSubmitForApproval}
            disabled={isSubmitting || !capacityCalculated}
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
                <span>Submit Phase 2 for Approval</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Helpful message */}
      {epics.length > 0 && userStories.length > 0 && !capacityCalculated && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            💡 <strong>Tip:</strong> Click "Calculate Capacity" to analyze your team's resource planning before submitting for approval.
          </p>
        </div>
      )}
    </div>
  )
}

export default Phase2Page
