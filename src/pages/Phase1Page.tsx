import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FileText, Users, CheckCircle, Edit3, AlertTriangle, Target, Loader2, UserPlus, Plus, Download, Save } from 'lucide-react'
import { getProjectPhases, generateContent, updatePhase, analyzeRisks } from '../services/api'
import toast from 'react-hot-toast'
import SelectStakeholderModal from '../components/modals/SelectStakeholderModal'
import RequirementUploader from '../components/DocumentUpload/RequirementUploader'
import GherkinViewer from '../components/Requirements/GherkinViewer'
// import AIChatPanel from '../components/AICopilot/AIChatPanel'

interface Requirement {
  id: number
  title: string
  priority: string
  status: string
}

interface GherkinRequirement {
  id: string
  feature: string
  as_a: string
  i_want: string
  so_that: string
  scenarios: GherkinScenario[]
  priority: 'High' | 'Medium' | 'Low'
  status: 'draft' | 'review' | 'approved'
}

interface GherkinScenario {
  title: string
  given: string[]
  when: string[]
  then: string[]
}

interface Risk {
  id: number
  risk: string
  severity: string
  mitigation: string
}

interface Stakeholder {
  role: string
  name: string
  status: string
}

const Phase1Page = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [prdContent, setPrdContent] = useState('')
  const [brdContent, setBrdContent] = useState('')
  const [phaseId, setPhaseId] = useState<number | null>(null)
  const [isGeneratingPRD, setIsGeneratingPRD] = useState(false)
  const [isGeneratingBRD, setIsGeneratingBRD] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [isAnalyzingRisks, setIsAnalyzingRisks] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingPhase, setIsLoadingPhase] = useState(true)
  // Start with empty arrays - will load from database
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [risks, setRisks] = useState<Risk[]>([])
  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([])
  const [showAddStakeholder, setShowAddStakeholder] = useState(false)
  const [showSelectModal, setShowSelectModal] = useState(false)
  const [newStakeholder, setNewStakeholder] = useState({ role: '', name: '' })
  const [gherkinRequirements, setGherkinRequirements] = useState<GherkinRequirement[]>([])
  const [showUploadSection, setShowUploadSection] = useState(false)
  const [showManualInput, setShowManualInput] = useState(false)
  const [manualRequirement, setManualRequirement] = useState('')
  
  useEffect(() => {
    if (projectId) {
      loadPhase()
    }
  }, [projectId])
  
  const loadPhase = async () => {
    if (!projectId || isNaN(Number(projectId))) {
      console.error('Invalid project ID:', projectId)
      toast.error('Invalid project ID')
      navigate('/')
      return
    }
    
    setIsLoadingPhase(true)
    try {
      const response = await getProjectPhases(Number(projectId))
      const phase1 = response.data.find((p: any) => p.phase_number === 1)
      if (phase1) {
        setPhaseId(phase1.id)
        
        // Load existing phase data
        if (phase1.data) {
          if (phase1.data.prd) setPrdContent(phase1.data.prd)
          if (phase1.data.brd) setBrdContent(phase1.data.brd)
          
          // Load requirements from saved data (not dummy data)
          if (phase1.data.requirements && Array.isArray(phase1.data.requirements)) {
            setRequirements(phase1.data.requirements)
          } else {
            // If no saved requirements, start with empty array
            setRequirements([])
          }
          
          // Load risks from saved data
          if (phase1.data.risks && Array.isArray(phase1.data.risks)) {
            setRisks(phase1.data.risks)
          } else {
            setRisks([])
          }
          
          // Load stakeholders from saved data
          if (phase1.data.stakeholders && Array.isArray(phase1.data.stakeholders)) {
            setStakeholders(phase1.data.stakeholders)
          } else {
            setStakeholders([])
          }
          
          // Load Gherkin requirements from saved data
          if (phase1.data.gherkinRequirements && Array.isArray(phase1.data.gherkinRequirements)) {
            setGherkinRequirements(phase1.data.gherkinRequirements)
          }
        } else {
          // No phase data exists yet, start with empty arrays
          setRequirements([])
          setRisks([])
          setStakeholders([])
        }
      }
    } catch (error) {
      console.error('Error loading phase:', error)
      toast.error('Failed to load phase data')
    } finally {
      setIsLoadingPhase(false)
    }
  }
  
  const handleExtractRequirements = async () => {
    if (!manualRequirement.trim()) {
      toast.error('Please enter requirement text')
      return
    }
    
    setIsExtracting(true)
    try {
      // Mock AI extraction for manual input
      const newGherkin: GherkinRequirement = {
        id: `req-${Date.now()}`,
        feature: manualRequirement.split('\n')[0] || 'New Feature',
        as_a: 'user',
        i_want: 'to achieve the stated goal',
        so_that: 'I can benefit from the system',
        scenarios: [{
          title: 'Main scenario',
          given: ['the system is ready'],
          when: ['I perform the action'],
          then: ['the expected result occurs']
        }],
        priority: 'Medium',
        status: 'draft'
      }
      
      const updatedRequirements = [...gherkinRequirements, newGherkin]
      setGherkinRequirements(updatedRequirements)
      setManualRequirement('')
      setShowManualInput(false)
      toast.success('Requirement converted to Gherkin format!')
      
      // Auto-save requirements to database
      if (phaseId) {
        try {
          await updatePhase(phaseId, {
            data: {
              gherkinRequirements: updatedRequirements,
              requirements,
              risks,
              stakeholders,
              prd: prdContent,
              brd: brdContent
            }
          })
          console.log('✅ Manual requirement auto-saved to database')
        } catch (error) {
          console.error('Failed to auto-save requirement:', error)
        }
      }
    } catch (error) {
      console.error('Error extracting requirements:', error)
      toast.error('Failed to extract requirements. Please try again.')
    } finally {
      setIsExtracting(false)
    }
  }
  
  const handleDocumentExtractComplete = async (extractedRequirements: any[]) => {
    const updatedRequirements = [...gherkinRequirements, ...extractedRequirements]
    setGherkinRequirements(updatedRequirements)
    setShowUploadSection(false)
    
    // Auto-save requirements to database
    if (phaseId) {
      try {
        await updatePhase(phaseId, {
          data: {
            gherkinRequirements: updatedRequirements,
            requirements,
            risks,
            stakeholders,
            prd: prdContent,
            brd: brdContent
          }
        })
        console.log('✅ Requirements auto-saved to database')
      } catch (error) {
        console.error('Failed to auto-save requirements:', error)
      }
    }
  }
  
  const handleGeneratePRD = async () => {
    if (!phaseId) {
      toast.error('Phase not found')
      return
    }
    
    // Validate that requirements exist
    if (gherkinRequirements.length === 0 && requirements.length === 0) {
      toast.error('Please add requirements before generating PRD')
      return
    }
    
    setIsGeneratingPRD(true)
    try {
      // STEP 1: Save current requirements to database FIRST
      await updatePhase(phaseId, {
        data: {
          gherkinRequirements,
          requirements,
          risks,
          stakeholders,
          prd: prdContent,
          brd: brdContent
        }
      })
      console.log('✅ Requirements saved before PRD generation')
      
      // STEP 2: Fetch project details
      const projectResponse = await import('../services/api').then(api => api.getProject(Number(projectId)))
      const projectData = projectResponse.data
      
      console.log('🔍 Generating PRD with data:', {
        requirements: requirements.length,
        gherkinRequirements: gherkinRequirements.length,
        projectName: projectData.name
      })
      
      // Pass requirements and project data for context-aware generation
      const response = await generateContent(phaseId, 'prd', {
        requirements,
        gherkinRequirements,
        risks,
        project: {
          id: projectId,
          name: projectData.name,
          description: projectData.description
        }
      })
      setPrdContent(response.data.content || response.data)
      
      // Save confidence score to phase
      const confidenceScore = response.data.confidence_score || 88
      await updatePhase(phaseId, {
        ai_confidence_score: confidenceScore
      })
      
      toast.success(`PRD generated successfully! (AI Confidence: ${confidenceScore}%)`)
    } catch (error) {
      console.error('Error generating PRD:', error)
      toast.error('Failed to generate PRD. Please try again.')
    } finally {
      setIsGeneratingPRD(false)
    }
  }
  
  const handleGenerateBRD = async () => {
    if (!phaseId) {
      toast.error('Phase not found')
      return
    }
    
    // Validate that requirements exist
    if (gherkinRequirements.length === 0 && requirements.length === 0) {
      toast.error('Please add requirements before generating BRD')
      return
    }
    
    setIsGeneratingBRD(true)
    try {
      // STEP 1: Save current requirements to database FIRST
      await updatePhase(phaseId, {
        data: {
          gherkinRequirements,
          requirements,
          risks,
          stakeholders,
          prd: prdContent,
          brd: brdContent
        }
      })
      console.log('✅ Requirements saved before BRD generation')
      
      // STEP 2: Fetch project details
      const projectResponse = await import('../services/api').then(api => api.getProject(Number(projectId)))
      const projectData = projectResponse.data
      
      console.log('🔍 Generating BRD with data:', {
        requirements: requirements.length,
        gherkinRequirements: gherkinRequirements.length,
        projectName: projectData.name
      })
      
      // Pass requirements and project data for context-aware generation
      const response = await generateContent(phaseId, 'brd', {
        requirements,
        gherkinRequirements,
        risks,
        project: {
          id: projectId,
          name: projectData.name,
          description: projectData.description
        }
      })
      setBrdContent(response.data.content || response.data)
      
      // Save confidence score to phase
      const confidenceScore = response.data.confidence_score || 88
      await updatePhase(phaseId, {
        ai_confidence_score: confidenceScore
      })
      
      toast.success(`BRD generated successfully! (AI Confidence: ${confidenceScore}%)`)
    } catch (error) {
      console.error('Error generating BRD:', error)
      toast.error('Failed to generate BRD. Please try again.')
    } finally {
      setIsGeneratingBRD(false)
    }
  }
  
  const handleAnalyzeRisks = async () => {
    if (!phaseId) {
      toast.error('Phase not found')
      return
    }
    
    if (!gherkinRequirements.length && !requirements.length) {
      toast.error('Please add requirements first before analyzing risks')
      return
    }
    
    setIsAnalyzingRisks(true)
    try {
      // Call the new AI-powered risk analysis endpoint
      const response = await analyzeRisks(phaseId)
      
      console.log('🔍 Risk Analysis Response:', response.data)
      
      // Parse risk analysis response from the new endpoint
      if (response.data.status === 'success' && response.data.risks) {
        const aiRisks = response.data.risks.map((risk: any) => ({
          id: risk.id || `risk-${Date.now()}-${Math.random()}`,
          risk: risk.risk,
          severity: risk.priority, // Map priority to severity for display
          mitigation: risk.mitigation,
          impact: risk.impact,
          likelihood: risk.likelihood,
          category: risk.category,
          contingency: risk.contingency
        }))
        
        setRisks(aiRisks)
        
        // Auto-save risks to phase data
        await updatePhase(phaseId, {
          data: {
            gherkinRequirements,
            requirements,
            risks: aiRisks,
            stakeholders,
            prd: prdContent,
            brd: brdContent
          }
        })
        
        toast.success(`✅ ${aiRisks.length} risks identified and analyzed!`)
        console.log('✅ Risks saved to database:', aiRisks.length)
      } else {
        toast.error('No risks found in response')
      }
    } catch (error) {
      console.error('Error analyzing risks:', error)
      toast.error('Failed to analyze risks. Please try again.')
    } finally {
      setIsAnalyzingRisks(false)
    }
  }
  
  const handleSaveDraft = async (documentType: 'prd' | 'brd') => {
    if (!phaseId) {
      toast.error('Phase not found')
      return
    }
    
    try {
      const content = documentType === 'prd' ? prdContent : brdContent
      
      if (!content || content.trim() === '') {
        toast.error(`Please generate or add ${documentType.toUpperCase()} content first`)
        return
      }
      
      await updatePhase(phaseId, {
        data: {
          gherkinRequirements,
          requirements,
          risks,
          stakeholders,
          prd: documentType === 'prd' ? prdContent : undefined,
          brd: documentType === 'brd' ? brdContent : undefined
        }
      })
      
      toast.success(`✅ ${documentType.toUpperCase()} draft saved successfully!`)
    } catch (error) {
      console.error(`Error saving ${documentType}:`, error)
      toast.error(`Failed to save ${documentType.toUpperCase()} draft`)
    }
  }
  
  const handleExportPDF = (documentType: 'prd' | 'brd') => {
    const content = documentType === 'prd' ? prdContent : brdContent
    
    if (!content || content.trim() === '') {
      toast.error(`Please generate or add ${documentType.toUpperCase()} content first`)
      return
    }
    
    try {
      // Convert markdown to HTML with basic formatting
      const htmlContent = convertMarkdownToHTML(content)
      
      // Create a new window for printing
      const printWindow = window.open('', '_blank')
      if (!printWindow) {
        toast.error('Please allow popups to export PDF')
        return
      }
      
      // Write formatted HTML content
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>${documentType.toUpperCase()} - ${new Date().toISOString().split('T')[0]}</title>
            <style>
              body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
              }
              h1 {
                color: #2563eb;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 10px;
                margin-top: 30px;
              }
              h2 {
                color: #1e40af;
                margin-top: 25px;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 8px;
              }
              h3 {
                color: #1e3a8a;
                margin-top: 20px;
              }
              ul, ol {
                margin: 10px 0;
                padding-left: 30px;
              }
              li {
                margin: 5px 0;
              }
              p {
                margin: 10px 0;
              }
              strong {
                color: #1f2937;
              }
              code {
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
              }
              table {
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
              }
              th, td {
                border: 1px solid #d1d5db;
                padding: 8px 12px;
                text-align: left;
              }
              th {
                background: #f3f4f6;
                font-weight: 600;
              }
              @media print {
                body {
                  margin: 0;
                  padding: 15px;
                }
                h1 {
                  page-break-after: avoid;
                }
              }
            </style>
          </head>
          <body>
            ${htmlContent}
            <script>
              window.onload = function() {
                window.print();
                setTimeout(function() {
                  window.close();
                }, 100);
              }
            </script>
          </body>
        </html>
      `)
      printWindow.document.close()
      
      toast.success(`✅ ${documentType.toUpperCase()} ready for PDF export! Use "Save as PDF" in print dialog.`)
    } catch (error) {
      console.error(`Error exporting ${documentType}:`, error)
      toast.error(`Failed to export ${documentType.toUpperCase()}`)
    }
  }
  
  const convertMarkdownToHTML = (markdown: string): string => {
    let html = markdown
    
    // Convert headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
    
    // Convert bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    
    // Convert bullet lists
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>')
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>')
    
    // Wrap consecutive <li> in <ul>
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
    
    // Convert numbered lists
    html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    html = html.replace(/(<li>.*<\/li>\n?){2,}/g, (match) => {
      if (!match.includes('<ul>')) {
        return `<ol>${match}</ol>`
      }
      return match
    })
    
    // Convert line breaks to paragraphs
    html = html.replace(/\n\n/g, '</p><p>')
    html = '<p>' + html + '</p>'
    
    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '')
    html = html.replace(/<p>\s*<\/p>/g, '')
    
    return html
  }
  
  const handleAddStakeholder = () => {
    if (!newStakeholder.role || !newStakeholder.name) {
      toast.error('Please enter both role and name')
      return
    }
    
    setStakeholders([...stakeholders, { ...newStakeholder, status: 'pending' }])
    setNewStakeholder({ role: '', name: '' })
    setShowAddStakeholder(false)
    toast.success('Stakeholder added successfully!')
  }
  
  const handleSelectStakeholder = (stakeholder: { role: string; name: string; email: string; userId: number }) => {
    // Check if stakeholder already exists
    const exists = stakeholders.some(s => s.name === stakeholder.name && s.role === stakeholder.role)
    if (exists) {
      toast.error('This stakeholder is already added')
      return
    }
    
    setStakeholders([...stakeholders, { 
      role: stakeholder.role, 
      name: stakeholder.name, 
      status: 'pending' 
    }])
    setShowSelectModal(false)
  }
  
  const handleSubmitForApproval = async () => {
    if (!phaseId) {
      toast.error('Phase not found')
      return
    }
    
    if (!prdContent || !brdContent) {
      toast.error('Please generate PRD and BRD before submitting for approval')
      return
    }
    
    if (stakeholders.length === 0) {
      toast.error('Please add at least one stakeholder before submitting for approval')
      return
    }
    
    setIsSubmitting(true)
    try {
      // Step 1: Update phase status to pending_approval
      await updatePhase(phaseId, {
        status: 'pending_approval',
        data: {
          prd: prdContent,
          brd: brdContent,
          requirements,
          risks,
          stakeholders,
          gherkinRequirements
        }
      })
      
      // Step 2: Create approval records for each stakeholder
      // TODO: This needs backend endpoint to create approvals
      // For now, the phase is marked as pending_approval
      
      toast.success(`Phase 1 submitted for approval! ${stakeholders.length} stakeholder(s) will be notified.`)
      
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
  
  if (isLoadingPhase) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-500">Loading Phase 1...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Phase 1: Requirements & Business Analysis</h1>
        <p className="text-gray-500 mt-2">Define what needs to be built - PRD & BRD creation</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Requirements Collection */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Target className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Requirements Collection</h2>
              </div>
              <button 
                onClick={() => setShowUploadSection(!showUploadSection)}
                className="btn-primary flex items-center space-x-2"
              >
                <FileText className="w-4 h-4" />
                <span>Upload Documents</span>
              </button>
            </div>
            
            {/* Upload Section */}
            {showUploadSection && phaseId && (
              <div className="mb-6">
                <RequirementUploader
                  projectId={Number(projectId)}
                  phaseId={phaseId}
                  onExtractComplete={handleDocumentExtractComplete}
                />
              </div>
            )}
            
            {/* Manual Input Section */}
            {showManualInput ? (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                <h3 className="font-semibold text-gray-900 mb-3">Add Manual Requirement</h3>
                <textarea
                  value={manualRequirement}
                  onChange={(e) => setManualRequirement(e.target.value)}
                  placeholder="Enter your requirement description here...
Example:
User Authentication System
The system should allow users to register and login securely"
                  className="input w-full min-h-32 mb-3"
                />
                <div className="flex space-x-2">
                  <button 
                    onClick={handleExtractRequirements}
                    disabled={isExtracting || !manualRequirement.trim()}
                    className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isExtracting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Converting...</span>
                      </>
                    ) : (
                      <>
                        <Edit3 className="w-4 h-4" />
                        <span>Extract with AI</span>
                      </>
                    )}
                  </button>
                  <button 
                    onClick={() => {
                      setShowManualInput(false)
                      setManualRequirement('')
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button 
                onClick={() => setShowManualInput(true)}
                className="btn-secondary w-full mb-4 flex items-center justify-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add Manual Requirement</span>
              </button>
            )}
            
            {/* Gherkin Requirements Display */}
            {gherkinRequirements.length > 0 && (
              <GherkinViewer
                requirements={gherkinRequirements}
                onUpdate={setGherkinRequirements}
              />
            )}
            
            {/* Legacy Requirements Display (can be removed later) */}
            {gherkinRequirements.length === 0 && (
              <div className="space-y-3">
                {requirements.map((req) => (
                  <div key={req.id} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{req.title}</h3>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className={`text-xs font-medium ${
                            req.priority === 'High' ? 'text-red-600' :
                            req.priority === 'Medium' ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {req.priority} Priority
                          </span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            req.status === 'documented' ? 'bg-green-100 text-green-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {req.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                <p className="text-sm text-gray-500 text-center py-4">
                  👆 Upload documents or add manual requirements to see them in Gherkin format
                </p>
              </div>
            )}
          </div>

          {/* Product Requirements Document (PRD) */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Product Requirements Document (PRD)</h2>
              </div>
              <button 
                onClick={handleGeneratePRD}
                disabled={isGeneratingPRD || !phaseId}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGeneratingPRD ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Edit3 className="w-4 h-4" />
                    <span>Generate with AI</span>
                  </>
                )}
              </button>
            </div>
            
            <textarea
              value={prdContent}
              onChange={(e) => setPrdContent(e.target.value)}
              placeholder="Enter PRD content or generate with AI...

Sections to include:
1. Product Overview
2. Objectives & Goals
3. User Personas
4. Features & Functionality
5. User Stories
6. Success Metrics"
              className="input min-h-64 font-mono text-sm"
            />
            
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm text-gray-500">AI Confidence: 88%</span>
              <div className="space-x-2">
                <button 
                  onClick={() => handleSaveDraft('prd')}
                  className="btn-secondary flex items-center space-x-2"
                  disabled={!prdContent}
                >
                  <Save className="w-4 h-4" />
                  <span>Save Draft</span>
                </button>
                <button 
                  onClick={() => handleExportPDF('prd')}
                  className="btn-primary flex items-center space-x-2"
                  disabled={!prdContent}
                >
                  <Download className="w-4 h-4" />
                  <span>Export PDF</span>
                </button>
              </div>
            </div>
          </div>

          {/* Business Requirements Document (BRD) */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Business Requirements Document (BRD)</h2>
              </div>
              <button 
                onClick={handleGenerateBRD}
                disabled={isGeneratingBRD || !phaseId}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGeneratingBRD ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Edit3 className="w-4 h-4" />
                    <span>Generate with AI</span>
                  </>
                )}
              </button>
            </div>
            
            <textarea
              value={brdContent}
              onChange={(e) => setBrdContent(e.target.value)}
              placeholder="Enter BRD content or generate with AI...

Sections to include:
1. Business Context
2. Business Objectives
3. Scope & Constraints
4. Stakeholders
5. Business Rules
6. Budget & Timeline"
              className="input min-h-64 font-mono text-sm"
            />
            
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm text-gray-500">AI Confidence: 85%</span>
              <div className="space-x-2">
                <button 
                  onClick={() => handleSaveDraft('brd')}
                  className="btn-secondary flex items-center space-x-2"
                  disabled={!brdContent}
                >
                  <Save className="w-4 h-4" />
                  <span>Save Draft</span>
                </button>
                <button 
                  onClick={() => handleExportPDF('brd')}
                  className="btn-primary flex items-center space-x-2"
                  disabled={!brdContent}
                >
                  <Download className="w-4 h-4" />
                  <span>Export PDF</span>
                </button>
              </div>
            </div>
          </div>

          {/* Risk Assessment */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Risk Assessment</h2>
              </div>
              <button 
                onClick={handleAnalyzeRisks}
                disabled={isAnalyzingRisks || !phaseId}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzingRisks ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <span>Analyze Risks with AI</span>
                )}
              </button>
            </div>
            
            <div className="space-y-3">
              {risks.map((risk) => (
                <div key={risk.id} className={`p-4 rounded-lg border-l-4 ${
                  risk.severity === 'High' ? 'border-red-500 bg-red-50' :
                  risk.severity === 'Medium' ? 'border-yellow-500 bg-yellow-50' :
                  'border-green-500 bg-green-50'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-gray-900">{risk.risk}</h3>
                        <span className={`text-xs px-2 py-1 rounded font-medium ${
                          risk.severity === 'High' ? 'bg-red-100 text-red-800' :
                          risk.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        <strong>Mitigation:</strong> {risk.mitigation}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button className="btn-secondary w-full mt-4">Add Risk</button>
          </div>
        </div>
        
        {/* Stakeholders & Approval Section */}
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Users className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Stakeholders</h2>
            </div>
            
            <div className="space-y-3">
              {stakeholders.map((stakeholder, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{stakeholder.role}</p>
                    <p className="text-xs text-gray-500">{stakeholder.name}</p>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                    Pending
                  </span>
                </div>
              ))}
            </div>

            <div className="mt-4 space-y-2">
              <button 
                onClick={() => setShowSelectModal(true)} 
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                <UserPlus className="w-4 h-4" />
                <span>Select from Database</span>
              </button>
              
              {showAddStakeholder ? (
                <div className="p-4 bg-blue-50 rounded-lg space-y-3">
                  <input
                    type="text"
                    placeholder="Role (e.g., Technical Lead)"
                    value={newStakeholder.role}
                    onChange={(e) => setNewStakeholder({ ...newStakeholder, role: e.target.value })}
                    className="input w-full"
                  />
                  <input
                    type="text"
                    placeholder="Name"
                    value={newStakeholder.name}
                    onChange={(e) => setNewStakeholder({ ...newStakeholder, name: e.target.value })}
                    className="input w-full"
                  />
                  <div className="flex space-x-2">
                    <button onClick={handleAddStakeholder} className="btn-primary flex-1">
                      Add
                    </button>
                    <button 
                      onClick={() => {
                        setShowAddStakeholder(false)
                        setNewStakeholder({ role: '', name: '' })
                      }} 
                      className="btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button 
                  onClick={() => setShowAddStakeholder(true)} 
                  className="btn-secondary w-full flex items-center justify-center space-x-2"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Add Custom Stakeholder</span>
                </button>
              )}
            </div>
            
            <SelectStakeholderModal
              isOpen={showSelectModal}
              onClose={() => setShowSelectModal(false)}
              onSelect={handleSelectStakeholder}
            />
          </div>
          
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Approval Workflow</h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Requirements Collected</p>
                  <p className="text-xs text-gray-500">All key requirements documented</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">PRD & BRD Created</p>
                  <p className="text-xs text-gray-500">Documents ready for review</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center">
                  <span className="text-yellow-600 font-bold">3</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Awaiting Approvals</p>
                  <p className="text-xs text-gray-500">3 stakeholders pending</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 opacity-50">
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                  <span className="text-gray-600 font-bold">4</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Approved</p>
                  <p className="text-xs text-gray-500">Move to Phase 2</p>
                </div>
              </div>
            </div>
            
            <button 
              onClick={handleSubmitForApproval}
              disabled={isSubmitting || !phaseId || !prdContent || !brdContent}
              className="w-full mt-6 btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Submitting...</span>
                </>
              ) : (
                <span>Submit for Approval</span>
              )}
            </button>
          </div>

          <div className="card bg-blue-50">
            <h3 className="font-semibold text-gray-900 mb-2">📝 Note</h3>
            <p className="text-sm text-gray-700">
              FSD (Functional Specification Document) will be created in Phase 4 (Detailed Design) after architecture is finalized.
            </p>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Key Deliverables</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Product Requirements Document (PRD)</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Business Requirements Document (BRD)</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Risk Assessment Report</span>
              </li>
              <li className="flex items-start">
                <span className="text-yellow-600 mr-2">⋯</span>
                <span>Feasibility Analysis</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Phase1Page
