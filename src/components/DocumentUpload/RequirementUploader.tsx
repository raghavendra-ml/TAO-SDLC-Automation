import { useState, useCallback } from 'react'
import { Upload, FileText, FileSpreadsheet, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

interface RequirementUploaderProps {
  projectId: number
  phaseId: number
  onExtractComplete: (gherkinRequirements: any[]) => void
}

interface UploadedFile {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  message?: string
}

const RequirementUploader = ({ projectId, phaseId, onExtractComplete }: RequirementUploaderProps) => {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  }

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    if (ext === 'xlsx' || ext === 'xls' || ext === 'csv') {
      return <FileSpreadsheet className="w-8 h-8 text-green-600" />
    }
    return <FileText className="w-8 h-8 text-blue-600" />
  }

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }
  }

  const handleFiles = (selectedFiles: File[]) => {
    const validFiles = selectedFiles.filter(file => {
      const ext = file.name.split('.').pop()?.toLowerCase()
      return ['xlsx', 'xls', 'docx', 'doc', 'txt', 'csv'].includes(ext || '')
    })

    if (validFiles.length !== selectedFiles.length) {
      toast.error('Some files were skipped. Only Excel, Word, and Text files are supported.')
    }

    const newFiles: UploadedFile[] = validFiles.map(file => ({
      file,
      status: 'pending',
      progress: 0
    }))

    setFiles(prev => [...prev, ...newFiles])
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleExtract = async () => {
    if (files.length === 0) {
      toast.error('Please upload at least one document')
      return
    }

    setIsExtracting(true)

    try {
      const formData = new FormData()
      files.forEach(({ file }) => {
        formData.append('files', file)
      })
      formData.append('project_id', projectId.toString())
      formData.append('phase_id', phaseId.toString())

      // Update file status to uploading
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const, progress: 50 })))

      const response = await axios.post(
        'http://localhost:8000/api/ai/extract-requirements',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0
            setFiles(prev => prev.map(f => ({ ...f, progress })))
          }
        }
      )

      // Update file status to success
      setFiles(prev => prev.map(f => ({ 
        ...f, 
        status: 'success' as const, 
        progress: 100,
        message: 'Extracted successfully'
      })))

      toast.success(`Successfully extracted ${response.data.requirements.length} requirements!`)
      onExtractComplete(response.data.requirements)

    } catch (error) {
      console.error('Error extracting requirements:', error)
      setFiles(prev => prev.map(f => ({ 
        ...f, 
        status: 'error' as const,
        message: 'Extraction failed'
      })))
      toast.error('Failed to extract requirements. Please try again.')
    } finally {
      setIsExtracting(false)
    }
  }

  const clearAll = () => {
    setFiles([])
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <input
          type="file"
          id="file-upload"
          multiple
          accept=".xlsx,.xls,.docx,.doc,.txt,.csv"
          onChange={handleFileInput}
          className="hidden"
        />
        
        <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-primary-600' : 'text-gray-400'}`} />
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Upload Requirement Documents
        </h3>
        
        <p className="text-sm text-gray-500 mb-4">
          Drag and drop files here, or click to browse
        </p>
        
        <label
          htmlFor="file-upload"
          className="btn-primary cursor-pointer inline-flex items-center space-x-2"
        >
          <Upload className="w-4 h-4" />
          <span>Choose Files</span>
        </label>
        
        <p className="text-xs text-gray-400 mt-4">
          Supported formats: Excel (.xlsx, .xls), Word (.docx, .doc), Text (.txt), CSV (.csv)
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-gray-900">
              Uploaded Files ({files.length})
            </h4>
            <button onClick={clearAll} className="text-sm text-red-600 hover:text-red-700">
              Clear All
            </button>
          </div>

          <div className="space-y-2">
            {files.map((uploadedFile, index) => (
              <div
                key={index}
                className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                {getFileIcon(uploadedFile.file.name)}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadedFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(uploadedFile.file.size / 1024).toFixed(2)} KB
                  </p>
                  
                  {/* Progress Bar */}
                  {uploadedFile.status === 'uploading' && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${uploadedFile.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {uploadedFile.message && (
                    <p className={`text-xs mt-1 ${
                      uploadedFile.status === 'success' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {uploadedFile.message}
                    </p>
                  )}
                </div>

                {/* Status Icon */}
                {uploadedFile.status === 'uploading' && (
                  <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                )}
                {uploadedFile.status === 'success' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
                {uploadedFile.status === 'error' && (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
                {uploadedFile.status === 'pending' && (
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extract Button */}
      {files.length > 0 && (
        <button
          onClick={handleExtract}
          disabled={isExtracting || files.some(f => f.status === 'uploading')}
          className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50"
        >
          {isExtracting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Extracting with AI...</span>
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              <span>Extract Requirements with AI</span>
            </>
          )}
        </button>
      )}
    </div>
  )
}

export default RequirementUploader