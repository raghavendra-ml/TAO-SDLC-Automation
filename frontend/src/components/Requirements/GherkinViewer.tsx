import { useState } from 'react'
import { Check, X, Edit3, Trash2, Copy, Download } from 'lucide-react'
import toast from 'react-hot-toast'

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

interface GherkinViewerProps {
  requirements: GherkinRequirement[]
  onUpdate: (requirements: GherkinRequirement[]) => void
}

const GherkinViewer = ({ requirements, onUpdate }: GherkinViewerProps) => {
  const [expandedRequirements, setExpandedRequirements] = useState<Set<string>>(new Set())

  const toggleRequirement = (id: string) => {
    const newExpanded = new Set(expandedRequirements)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedRequirements(newExpanded)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'Low':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'review':
        return 'bg-yellow-100 text-yellow-800'
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const updateRequirementStatus = (id: string, status: GherkinRequirement['status']) => {
    const updated = requirements.map(req =>
      req.id === id ? { ...req, status } : req
    )
    onUpdate(updated)
    toast.success(`Requirement ${status}`)
  }

  const deleteRequirement = (id: string) => {
    const updated = requirements.filter(req => req.id !== id)
    onUpdate(updated)
    toast.success('Requirement deleted')
  }

  const copyToClipboard = (requirement: GherkinRequirement) => {
    const gherkinText = `Feature: ${requirement.feature}
  As a ${requirement.as_a}
  I want ${requirement.i_want}
  So that ${requirement.so_that}

${requirement.scenarios.map((scenario, idx) => `  Scenario ${idx + 1}: ${scenario.title}
${scenario.given.map(g => `    Given ${g}`).join('\n')}
${scenario.when.map(w => `    When ${w}`).join('\n')}
${scenario.then.map(t => `    Then ${t}`).join('\n')}`).join('\n\n')}`

    navigator.clipboard.writeText(gherkinText)
    toast.success('Copied to clipboard!')
  }

  const exportAllAsGherkin = () => {
    const allGherkin = requirements.map(req => {
      return `Feature: ${req.feature}
  As a ${req.as_a}
  I want ${req.i_want}
  So that ${req.so_that}

${req.scenarios.map((scenario, idx) => `  Scenario ${idx + 1}: ${scenario.title}
${scenario.given.map(g => `    Given ${g}`).join('\n')}
${scenario.when.map(w => `    When ${w}`).join('\n')}
${scenario.then.map(t => `    Then ${t}`).join('\n')}`).join('\n\n')}`
    }).join('\n\n' + '='.repeat(80) + '\n\n')

    const blob = new Blob([allGherkin], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'requirements-gherkin.feature'
    a.click()
    toast.success('Gherkin file downloaded!')
  }

  if (requirements.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <p className="text-gray-500">No requirements extracted yet. Upload documents to get started.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Extracted Requirements ({requirements.length})
        </h3>
        <button
          onClick={exportAllAsGherkin}
          className="btn-secondary flex items-center space-x-2"
        >
          <Download className="w-4 h-4" />
          <span>Export All as .feature</span>
        </button>
      </div>

      {requirements.map((requirement) => (
        <div
          key={requirement.id}
          className="border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow"
        >
          {/* Header */}
          <div
            className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 cursor-pointer"
            onClick={() => toggleRequirement(requirement.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded border ${getPriorityColor(requirement.priority)}`}>
                    {requirement.priority}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(requirement.status)}`}>
                    {requirement.status}
                  </span>
                </div>
                <h4 className="text-lg font-bold text-gray-900 mb-2">
                  Feature: {requirement.feature}
                </h4>
                <div className="text-sm text-gray-700 space-y-1">
                  <p><span className="font-semibold">As a</span> {requirement.as_a}</p>
                  <p><span className="font-semibold">I want</span> {requirement.i_want}</p>
                  <p><span className="font-semibold">So that</span> {requirement.so_that}</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    copyToClipboard(requirement)
                  }}
                  className="p-2 text-gray-500 hover:text-primary-600 hover:bg-white rounded transition-colors"
                  title="Copy as Gherkin"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    updateRequirementStatus(requirement.id, 'approved')
                  }}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-white rounded transition-colors"
                  title="Approve"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteRequirement(requirement.id)
                  }}
                  className="p-2 text-gray-500 hover:text-red-600 hover:bg-white rounded transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Scenarios (Expandable) */}
          {expandedRequirements.has(requirement.id) && (
            <div className="p-4 bg-gray-50 border-t border-gray-200">
              <h5 className="font-semibold text-gray-900 mb-3">
                Scenarios ({requirement.scenarios.length})
              </h5>
              <div className="space-y-4">
                {requirement.scenarios.map((scenario, idx) => (
                  <div
                    key={idx}
                    className="bg-white p-4 rounded-lg border border-gray-200"
                  >
                    <h6 className="font-semibold text-gray-900 mb-3">
                      Scenario {idx + 1}: {scenario.title}
                    </h6>
                    
                    <div className="space-y-2 font-mono text-sm">
                      {scenario.given.map((given, gIdx) => (
                        <div key={`g-${gIdx}`} className="flex items-start">
                          <span className="text-blue-600 font-semibold mr-2">Given</span>
                          <span className="text-gray-700">{given}</span>
                        </div>
                      ))}
                      {scenario.when.map((when, wIdx) => (
                        <div key={`w-${wIdx}`} className="flex items-start">
                          <span className="text-green-600 font-semibold mr-2">When</span>
                          <span className="text-gray-700">{when}</span>
                        </div>
                      ))}
                      {scenario.then.map((then, tIdx) => (
                        <div key={`t-${tIdx}`} className="flex items-start">
                          <span className="text-purple-600 font-semibold mr-2">Then</span>
                          <span className="text-gray-700">{then}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default GherkinViewer

