import { useState } from 'react'
import { Send, Sparkles, ThumbsUp, ThumbsDown, RotateCw } from 'lucide-react'
import { queryAI } from '../../services/api'
import { AIResponse } from '../../types'

const AICopilot = () => {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<AIResponse | null>(null)
  const [loading, setLoading] = useState(false)
  
  const handleQuery = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    try {
      const result = await queryAI({
        project_id: 1, // TODO: Get from context
        phase_id: 1,
        query,
        context: {}
      })
      setResponse(result.data)
    } catch (error) {
      console.error('AI query failed:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <aside className="fixed right-0 top-16 h-[calc(100vh-4rem)] w-80 bg-white border-l border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-primary-600" />
          <h3 className="font-semibold text-gray-900">AI Copilot</h3>
        </div>
        <p className="text-xs text-gray-500 mt-1">Ask me anything about your project</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {response && (
          <div className="space-y-3">
            <div className="bg-primary-50 rounded-lg p-4">
              <p className="text-sm text-gray-800">{response.response}</p>
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Confidence:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 w-20">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${response.confidence_score}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-700">{response.confidence_score}%</span>
                </div>
              </div>
            </div>
            
            {response.explanation && (
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">{response.explanation}</p>
              </div>
            )}
            
            {response.alternatives && response.alternatives.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-700">Alternatives:</p>
                {response.alternatives.map((alt, i) => (
                  <div key={i} className="bg-gray-50 rounded p-2">
                    <p className="text-xs text-gray-600">{alt}</p>
                  </div>
                ))}
              </div>
            )}
            
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center space-x-2">
                <button className="p-1.5 hover:bg-gray-100 rounded transition-colors">
                  <ThumbsUp className="w-4 h-4 text-gray-600" />
                </button>
                <button className="p-1.5 hover:bg-gray-100 rounded transition-colors">
                  <ThumbsDown className="w-4 h-4 text-gray-600" />
                </button>
                <button className="p-1.5 hover:bg-gray-100 rounded transition-colors">
                  <RotateCw className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
            placeholder="Ask AI copilot..."
            className="flex-1 input text-sm"
            disabled={loading}
          />
          <button
            onClick={handleQuery}
            disabled={loading}
            className="btn-primary px-3"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}

export default AICopilot

