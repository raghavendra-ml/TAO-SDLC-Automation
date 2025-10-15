import { TestTube, CheckCircle, XCircle, Shield, Zap } from 'lucide-react'

const Phase5Page = () => {
  const testSuites = [
    { name: 'Integration Tests', total: 45, passed: 43, failed: 2, status: 'warning' },
    { name: 'Functional Tests', total: 68, passed: 68, failed: 0, status: 'success' },
    { name: 'Security Tests', total: 32, passed: 30, failed: 2, status: 'warning' },
    { name: 'Performance Tests', total: 15, passed: 14, failed: 1, status: 'warning' },
  ]
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Phase 5: QA & Testing</h1>
        <p className="text-gray-500 mt-2">Comprehensive testing and quality assurance</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <TestTube className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Test Suites</h2>
              </div>
              <button className="btn-primary">Generate Tests with AI</button>
            </div>
            
            <div className="space-y-4">
              {testSuites.map((suite, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{suite.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      suite.status === 'success' ? 'bg-green-100 text-green-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {suite.passed}/{suite.total} Passed
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-1 text-green-600">
                      <CheckCircle className="w-4 h-4" />
                      <span>{suite.passed} passed</span>
                    </div>
                    {suite.failed > 0 && (
                      <div className="flex items-center space-x-1 text-red-600">
                        <XCircle className="w-4 h-4" />
                        <span>{suite.failed} failed</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-3 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        suite.status === 'success' ? 'bg-green-500' : 'bg-yellow-500'
                      }`}
                      style={{ width: `${(suite.passed / suite.total) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">Security Testing</h2>
            </div>
            
            <div className="space-y-3">
              <div className="p-3 bg-green-50 rounded-lg flex items-center justify-between">
                <span className="text-sm text-gray-700">SQL Injection</span>
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              
              <div className="p-3 bg-green-50 rounded-lg flex items-center justify-between">
                <span className="text-sm text-gray-700">XSS Vulnerabilities</span>
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              
              <div className="p-3 bg-yellow-50 rounded-lg flex items-center justify-between">
                <span className="text-sm text-gray-700">CSRF Protection</span>
                <span className="text-xs text-yellow-700">1 Warning</span>
              </div>
              
              <div className="p-3 bg-green-50 rounded-lg flex items-center justify-between">
                <span className="text-sm text-gray-700">Authentication</span>
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
            </div>
            
            <button className="btn-secondary w-full mt-4">Run Security Scan</button>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Zap className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Performance</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600">API Response Time</span>
                  <span className="text-sm font-medium text-green-600">125ms</span>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600">Page Load Time</span>
                  <span className="text-sm font-medium text-green-600">1.2s</span>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '90%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600">Memory Usage</span>
                  <span className="text-sm font-medium text-yellow-600">245MB</span>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
            </div>
            
            <button className="btn-secondary w-full mt-4">Run Load Test</button>
          </div>
          
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Coverage</h2>
            
            <div className="text-center mb-4">
              <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-green-50">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">91%</p>
                  <p className="text-xs text-gray-500">Coverage</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Backend</span>
                <span className="font-medium text-gray-900">87%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Frontend</span>
                <span className="font-medium text-gray-900">92%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Integration</span>
                <span className="font-medium text-gray-900">95%</span>
              </div>
            </div>
          </div>
          
          <div className="card bg-green-50">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">QA Sign-off</h2>
            <p className="text-sm text-gray-600 mb-4">All tests passed. Ready for production deployment.</p>
            <button className="btn-primary w-full">Submit for UAT</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Phase5Page

