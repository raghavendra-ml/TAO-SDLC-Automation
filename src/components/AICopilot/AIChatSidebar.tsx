import { useState, useEffect, useRef } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { Send, Loader2, Sparkles, Lightbulb } from 'lucide-react'
import { chatWithAI } from '../../services/api'
import toast from 'react-hot-toast'

interface ChatMessage {
  sender: 'user' | 'ai'
  message: string
  timestamp: string
  confidence?: number
  suggestedQuestions?: string[]
}

const AIChatSidebar = () => {
  const location = useLocation()
  const params = useParams<{ projectId?: string }>()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Determine context based on current route
  const projectId = params.projectId ? Number(params.projectId) : undefined
  const contextType = projectId ? 'project' : 'dashboard'
  
  // Extract phase ID from route if present
  const phaseMatch = location.pathname.match(/\/phase(\d+)/)
  const phaseNumber = phaseMatch ? Number(phaseMatch[1]) : undefined
  
  // Get phase ID from URL or state if available
  const phaseId = phaseNumber
  
  const contextLabel = projectId 
    ? `Project ${projectId}${phaseNumber ? ` / Phase ${phaseNumber}` : ''}`
    : 'Dashboard'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Clear messages when context changes
  useEffect(() => {
    setMessages([])
  }, [location.pathname])

  const handleSendMessage = async () => {
    if (input.trim() === '') return

    const userMessage: ChatMessage = {
      sender: 'user',
      message: input,
      timestamp: new Date().toLocaleTimeString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await chatWithAI({
        query: input,
        context_type: contextType,
        project_id: projectId,
        phase_id: phaseId,
      })

      const aiMessage: ChatMessage = {
        sender: 'ai',
        message: response.data.response,
        timestamp: new Date().toLocaleTimeString(),
        confidence: response.data.confidence_score,
        suggestedQuestions: response.data.alternatives,
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending chat message:', error)
      toast.error('Failed to get AI response')
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          message: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestedQuestionClick = (question: string) => {
    setInput(question)
  }

  const getSuggestedQuestions = () => {
    if (contextType === 'dashboard') {
      return [
        'How many projects are there?',
        'What approvals are pending?',
        'Show me active projects',
      ]
    } else if (phaseNumber === 1) {
      return [
        'What should I do in Phase 1?',
        'How do I upload requirements?',
        'Generate PRD for this project',
      ]
    } else if (phaseNumber === 2) {
      return [
        'How do I create effective epics?',
        'What is story point estimation?',
        'Help me with sprint planning',
      ]
    } else if (phaseNumber === 3) {
      return [
        'What is system architecture design?',
        'How do I create a high-level design?',
        'What are architecture best practices?',
      ]
    } else if (phaseNumber === 4) {
      return [
        'How do I design database schemas?',
        'What is detailed design specification?',
        'Help me with API design',
      ]
    } else if (phaseNumber === 5) {
      return [
        'What are development best practices?',
        'How do I write effective tests?',
        'What is code review checklist?',
      ]
    } else if (phaseNumber === 6) {
      return [
        'How do I deploy to production?',
        'What is CI/CD pipeline?',
        'Help me with monitoring setup',
      ]
    } else if (projectId) {
      return [
        'What is the current phase?',
        'Show me project insights',
        'What are the next steps?',
      ]
    } else {
      return [
        'How can you help me?',
        'What features do you have?',
        'Guide me through SDLC',
      ]
    }
  }

  return (
    <aside className="fixed right-0 top-16 h-[calc(100vh-4rem)] w-96 bg-white border-l border-gray-200 flex flex-col shadow-lg z-40">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="flex items-center space-x-2 mb-2">
          <Sparkles className="w-5 h-5" />
          <h3 className="text-lg font-semibold">AI Copilot</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-primary-100">{contextLabel}</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-gray-50">
        {messages.length === 0 && !isLoading && (
          <div className="text-center mt-8">
            <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary-300" />
            <p className="text-lg font-medium text-gray-700">
              {phaseNumber ? `Phase ${phaseNumber} Assistant` : 'Ask me anything!'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              {phaseNumber === 1 && 'I can help with requirements gathering, PRD creation, and business analysis.'}
              {phaseNumber === 2 && 'I can help with sprint planning, epics, user stories, and effort estimation.'}
              {phaseNumber === 3 && 'I can help with system architecture, high-level design, and technical decisions.'}
              {phaseNumber === 4 && 'I can help with detailed design, database schemas, and API specifications.'}
              {phaseNumber === 5 && 'I can help with development, testing, code review, and quality assurance.'}
              {phaseNumber === 6 && 'I can help with deployment, CI/CD, monitoring, and operations.'}
              {!phaseNumber && projectId && 'I can help you with this project and guide you through the SDLC phases.'}
              {!phaseNumber && !projectId && 'I can help you with project management, SDLC guidance, and more.'}
            </p>
            
            {/* Suggested Questions */}
            <div className="mt-6 space-y-2">
              <div className="flex items-center justify-center space-x-1 text-xs text-gray-500 mb-3">
                <Lightbulb className="w-3 h-3" />
                <span>Try asking:</span>
              </div>
              {getSuggestedQuestions().map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestedQuestionClick(question)}
                  className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] p-3 rounded-lg shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
              <p className={`text-xs mt-1 ${msg.sender === 'user' ? 'text-primary-100' : 'text-gray-500'}`}>
                {msg.timestamp}
              </p>
              {msg.sender === 'ai' && msg.confidence && (
                <p className="text-xs text-gray-600 mt-1">Confidence: {msg.confidence}%</p>
              )}
              {msg.sender === 'ai' && msg.suggestedQuestions && msg.suggestedQuestions.length > 0 && (
                <div className="mt-3 pt-2 border-t border-gray-200">
                  <p className="text-xs font-semibold text-gray-700 mb-2">Related questions:</p>
                  <div className="space-y-1">
                    {msg.suggestedQuestions.map((q, qIndex) => (
                      <button
                        key={qIndex}
                        onClick={() => handleSuggestedQuestionClick(q)}
                        className="w-full text-left text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 px-2 py-1 rounded transition-colors"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] p-3 rounded-lg shadow-sm bg-white border border-gray-200 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
              <p className="text-sm text-gray-600">Thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-end space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
            placeholder="Ask AI Copilot..."
            className="flex-1 input resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            className="btn-primary p-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading || input.trim() === ''}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </aside>
  )
}

export default AIChatSidebar
