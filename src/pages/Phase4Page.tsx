import { Code, Database, Layout, Palette } from 'lucide-react'

const Phase4Page = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Phase 4: Detailed Design & Development</h1>
        <p className="text-gray-500 mt-2">Database design, service design, UX/UI design, and implementation</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Backend Track */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Backend Development</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Database Schema Design</h3>
              <div className="bg-white p-3 rounded border border-gray-200 font-mono text-xs overflow-x-auto">
                <pre>{`CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  username VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);`}</pre>
              </div>
              <button className="btn-secondary w-full mt-2">Generate Schema with AI</button>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Service Design</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-white rounded">
                  <span className="text-sm text-gray-700">User Service</span>
                  <span className="text-xs text-green-600">✓ Complete</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded">
                  <span className="text-sm text-gray-700">Project Service</span>
                  <span className="text-xs text-blue-600">In Progress</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded">
                  <span className="text-sm text-gray-700">AI Service</span>
                  <span className="text-xs text-gray-500">Pending</span>
                </div>
              </div>
              <button className="btn-secondary w-full mt-2">Generate Service Code</button>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Unit Tests</h3>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Code Coverage</span>
                <span className="text-lg font-bold text-green-600">87%</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '87%' }}></div>
              </div>
              <button className="btn-secondary w-full mt-2">Generate Unit Tests</button>
            </div>
          </div>
        </div>
        
        {/* Frontend Track */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Layout className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Frontend Development</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">UX Design & Wireframes</h3>
              <div className="bg-white rounded-lg h-32 flex items-center justify-center border-2 border-dashed border-gray-300">
                <p className="text-gray-400 text-sm">Wireframe Preview</p>
              </div>
              <button className="btn-secondary w-full mt-2">Generate Wireframes with AI</button>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">UI Component Design</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-white rounded">
                  <div className="flex items-center space-x-2">
                    <Palette className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-700">Design System</span>
                  </div>
                  <span className="text-xs text-green-600">✓ Complete</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded">
                  <div className="flex items-center space-x-2">
                    <Code className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-700">React Components</span>
                  </div>
                  <span className="text-xs text-blue-600">In Progress</span>
                </div>
              </div>
              <button className="btn-secondary w-full mt-2">Generate UI Components</button>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Component Testing</h3>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Test Coverage</span>
                <span className="text-lg font-bold text-green-600">92%</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '92%' }}></div>
              </div>
              <button className="btn-secondary w-full mt-2">Generate Component Tests</button>
            </div>
          </div>
        </div>
        
        {/* Code Review Section */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Code className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">Code Review & Quality</h2>
            </div>
            <button className="btn-primary">Request Code Review</button>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-green-600">156</p>
              <p className="text-sm text-gray-600 mt-1">Files</p>
            </div>
            
            <div className="p-4 bg-blue-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-blue-600">12,450</p>
              <p className="text-sm text-gray-600 mt-1">Lines of Code</p>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-purple-600">89%</p>
              <p className="text-sm text-gray-600 mt-1">Test Coverage</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6 flex justify-end space-x-4">
        <button className="btn-secondary">Save Progress</button>
        <button className="btn-primary">Submit for Code Review</button>
      </div>
    </div>
  )
}

export default Phase4Page

