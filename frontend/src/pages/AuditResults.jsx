import { useState, useEffect, useRef } from 'react'

const API = ''
const VIDEO_URL = typeof window !== 'undefined' && window.location.port === '5173'
  ? 'http://localhost:8000/video_feed'
  : '/video_feed'

export default function AuditResults({ user, onBackClick, metrics, onStartAudit, onUploadImage, onSaveImage, isScanning, settings }) {
  const [compliance, setCompliance] = useState('COMPLIANT')
  const [grade, setGrade] = useState('A')
  const fileInputRef = useRef(null)

  // Compliance Logic: Based on weight, detection count, and confidence
  useEffect(() => {
    const weight = metrics.estimated_weight_kg || 0
    const confidence = (metrics.confidence || 0) * 100
    const detections = metrics.detection_count || 0

    let status = 'COMPLIANT'
    let grade_val = 'A'

    // Government jute standards
    if (weight < 5 || confidence < 60 || detections < 2) {
      status = 'NON-COMPLIANT'
      grade_val = 'F'
    } else if (weight < 10 || confidence < 75 || detections < 5) {
      status = 'COMPLIANT'
      grade_val = 'C'
    } else if (weight < 20 || confidence < 85) {
      status = 'COMPLIANT'
      grade_val = 'B'
    } else {
      status = 'COMPLIANT'
      grade_val = 'A'
    }

    setCompliance(status)
    setGrade(grade_val)
  }, [metrics])

  const handleExport = () => {
    const data = {
      inspector: user.userId,
      timestamp: new Date().toISOString(),
      ...metrics,
      compliance,
      grade,
    }
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleUpload = async (e) => {
    const file = e?.target?.files?.[0]
    if (!file) return
    onUploadImage(file)
  }

  return (
    <div className="min-h-screen bg-charcoal text-white flex flex-col safe-area">
      {/* Header with Back Button */}
      <header className="border-b border-gray-700 bg-gray-900/80 backdrop-blur-sm px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <button
            onClick={onBackClick}
            className="flex items-center gap-2 px-4 py-2 rounded-[10px] border border-gray-700 text-gray-300 hover:text-emerald hover:border-emerald/50 transition"
          >
            ← Back
          </button>
          <h1 className="text-xl font-semibold">Audit Results</h1>
          <div className="w-20" />
        </div>
      </header>

      {/* Live Feed Section */}
      <div className="border-b border-gray-700 bg-gray-900/50 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Live Audit Feed</p>
          <div className="w-full h-64 sm:h-80 rounded-[15px] overflow-hidden border border-gray-700 bg-black">
            <img src={VIDEO_URL} alt="Live feed" className="w-full h-full object-contain" />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 p-6 overflow-auto">
        <div className="max-w-7xl mx-auto">
          {/* Compliance Badge - Large */}
          <div className="mb-8 text-center">
            <div
              className={`inline-flex items-center justify-center px-8 py-6 rounded-[15px] border-2 font-bold text-2xl ${
                compliance === 'COMPLIANT'
                  ? 'bg-emerald/20 border-emerald text-emerald'
                  : 'bg-red-500/20 border-red-500 text-red-400'
              }`}
            >
              {compliance === 'COMPLIANT' ? '✓' : '✗'} {compliance}
            </div>
          </div>

          {/* 2x2 Grid */}
          <div className="grid grid-cols-2 gap-6 mb-8">
            {/* Grade */}
            <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-6">
              <span className="block text-sm text-gray-500 uppercase tracking-wider mb-2">Grade</span>
              <span className="block text-5xl font-bold text-emerald">{grade}</span>
              <p className="text-xs text-gray-500 mt-2">Quality score</p>
            </div>

            {/* Weight */}
            <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-6">
              <span className="block text-sm text-gray-500 uppercase tracking-wider mb-2">Weight</span>
              <span className="block text-5xl font-bold text-white">{metrics.estimated_weight_kg || 0}</span>
              <p className="text-xs text-gray-500 mt-2">kg (estimated)</p>
            </div>

            {/* Confidence */}
            <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-6">
              <span className="block text-sm text-gray-500 uppercase tracking-wider mb-2">Confidence</span>
              <span className="block text-5xl font-bold text-white">{((metrics.confidence || 0) * 100).toFixed(0)}</span>
              <p className="text-xs text-gray-500 mt-2">% accuracy</p>
            </div>

            {/* Detections */}
            <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-6">
              <span className="block text-sm text-gray-500 uppercase tracking-wider mb-2">Detections</span>
              <span className="block text-5xl font-bold text-white">{metrics.detection_count || 0}</span>
              <p className="text-xs text-gray-500 mt-2">objects found</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            {/* Export Image */}
            <button
              onClick={handleExport}
              className="py-3 rounded-[12px] bg-gray-900 border border-gray-700 text-white font-medium hover:border-emerald/50 hover:text-emerald transition"
            >
              📥 Export Report
            </button>

            {/* Save Locally */}
            <button
              onClick={onSaveImage}
              className="py-3 rounded-[12px] bg-emerald/20 border border-emerald text-emerald font-medium hover:bg-emerald/30 transition"
            >
              💾 Save Locally
            </button>

            {/* Upload Image */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="py-3 rounded-[12px] bg-gray-900 border border-gray-700 text-white font-medium hover:border-emerald/50 hover:text-emerald transition"
            >
              📤 Upload New
            </button>
            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleUpload} />
          </div>

          {/* Additional Actions */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Start New Audit */}
            <button
              onClick={onStartAudit}
              className="py-3 rounded-[12px] bg-emerald text-charcoal font-bold hover:bg-emerald/90 transition active:scale-[0.98]"
            >
              🔄 New Audit
            </button>

            {/* Continue Scanning */}
            <button
              onClick={onStartAudit}
              className="py-3 rounded-[12px] bg-gray-900 border border-emerald text-emerald font-medium hover:bg-emerald/10 transition"
            >
              📷 Continue Scan
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
