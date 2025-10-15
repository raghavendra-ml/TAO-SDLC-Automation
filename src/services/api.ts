import axios from 'axios'
import { Project, Phase, Approval, AIQuery, AIResponse } from '../types'

// Read the VITE_API_BASE_URL env var exposed by Vite (must be prefixed with VITE_)
// Normalize it so that the final baseURL points to the backend's '/api' root
// - If VITE_API_BASE_URL is empty, use '/api' (dev-server proxy)
// - If VITE_API_BASE_URL is provided (e.g. https://abcd.ngrok-free.dev),
//   ensure the URL ends with '/api' so requests to '/ai/...' become 'https://.../api/ai/...'
const rawBase = (import.meta.env.VITE_API_BASE_URL as string) || ''
let clientBase: string
if (rawBase && rawBase.trim().length > 0) {
  const noTrailing = rawBase.replace(/\/+$/, '')
  clientBase = noTrailing.endsWith('/api') ? noTrailing : `${noTrailing}/api`
} else {
  clientBase = '/api'
}

const api = axios.create({
  baseURL: clientBase,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Projects
export const getProjects = () => api.get<Project[]>('/projects/')
export const getProject = (id: number) => api.get<Project>(`/projects/${id}`)
export const createProject = (data: { name: string; description: string }) => 
  api.post<Project>('/projects/', data)
export const deleteProject = (id: number) => api.delete(`/projects/${id}`)

// Phases
export const getProjectPhases = (projectId: number) => 
  api.get<Phase[]>(`/phases/project/${projectId}`)
export const getPhase = (phaseId: number) => api.get<Phase>(`/phases/${phaseId}`)
export const updatePhase = (phaseId: number, data: Partial<Phase>) => 
  api.put<Phase>(`/phases/${phaseId}`, data)

// Approvals
export const getPhaseApprovals = (phaseId: number) => 
  api.get<Approval[]>(`/approvals/phase/${phaseId}`)
export const getPendingApprovals = (userId: number) => 
  api.get<Approval[]>(`/approvals/pending/${userId}`)
export const updateApproval = (approvalId: number, data: { status: string; comments?: string }) => 
  api.put<Approval>(`/approvals/${approvalId}`, data)

// AI Copilot
export const queryAI = (data: AIQuery) => api.post<AIResponse>('/ai/query', data)
export const generateContent = (phaseId: number, contentType: string, additionalData?: any) => 
  api.post(`/ai/generate/${phaseId}`, { content_type: contentType, ...additionalData })
export const analyzeRisks = (phaseId: number) => 
  api.post(`/ai/analyze-risks/${phaseId}`)
export const chatWithAI = (data: {
  query: string
  context_type: string
  project_id?: number
  phase_id?: number
}) => api.post<AIResponse>('/chat/query', data)

// Authentication
export const login = (username: string, password: string) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const signup = (data: {
  username: string
  email: string
  full_name: string
  password: string
  role?: string
}) => api.post('/auth/signup', data)

export const demoLogin = () => api.post('/auth/demo')

export const getCurrentUser = () => api.get('/auth/me')

export const logout = () => api.post('/auth/logout')

export default api

