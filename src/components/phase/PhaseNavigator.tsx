import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useProjectStore } from '../../store/projectStore'
import { getProjectPhases } from '../../services/api'
import { Check, Circle, Lock } from 'lucide-react'

const PhaseNavigator = () => {
  const { projectId } = useParams()
  const { phases, setPhases } = useProjectStore()
  
  useEffect(() => {
    if (projectId) {
      getProjectPhases(Number(projectId)).then((res) => setPhases(res.data))
    }
  }, [projectId])
  
  const getPhaseIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <Check className="w-5 h-5 text-green-500" />
      case 'in_progress':
        return <Circle className="w-5 h-5 text-blue-500 fill-blue-500" />
      case 'pending_approval':
        return <Circle className="w-5 h-5 text-yellow-500" />
      default:
        return <Lock className="w-5 h-5 text-gray-400" />
    }
  }
  
  return (
    <div className="p-4">
      <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4">Phase Progress</h3>
      <div className="space-y-2">
        {phases.map((phase) => (
          <Link
            key={phase.id}
            to={`/projects/${projectId}/phase${phase.phase_number}`}
            className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="flex-shrink-0 mt-0.5">
              {getPhaseIcon(phase.status)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                Phase {phase.phase_number}
              </p>
              <p className="text-xs text-gray-500 truncate">{phase.phase_name}</p>
              <div className="mt-1 flex items-center space-x-1">
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${
                      phase.status === 'approved' ? 'bg-green-500' :
                      phase.status === 'in_progress' ? 'bg-blue-500' :
                      'bg-gray-300'
                    }`}
                    style={{ width: phase.status === 'approved' ? '100%' : phase.status === 'in_progress' ? '50%' : '0%' }}
                  />
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default PhaseNavigator

