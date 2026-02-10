import { useState, useEffect, useCallback, useRef } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import AuditResults from './pages/AuditResults'

const API = ''
const VIDEO_URL = typeof window !== 'undefined' && window.location.port === '5173'
  ? 'http://localhost:8000/video_feed'
  : '/video_feed'

// --- Confirm Modal ---
function ConfirmModal({ show, title, message, confirmLabel, onConfirm, onCancel, danger }) {
  if (!show) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={onCancel}>
      <div className="w-full max-w-sm rounded-xl border border-obsidian-border bg-obsidian-card p-6 shadow-xl" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-gray-200 mb-2">{title}</h3>
        <p className="text-sm text-obsidian-muted mb-6">{message}</p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="flex-1 py-2.5 rounded-lg border border-obsidian-border text-gray-300 font-medium hover:bg-obsidian-border/50 transition">
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`flex-1 py-2.5 rounded-lg font-medium transition ${danger ? 'bg-red-500/20 text-red-400 border border-red-500/40 hover:bg-red-500/30' : 'bg-emerald/20 text-emerald-bright border border-emerald/40 hover:bg-emerald/30'}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

// --- PIN Lock Screen ---
function PinLock({ onUnlock, type }) {
  const [pin, setPin] = useState('')
  const [error, setError] = useState('')

  const submit = async () => {
    try {
      const fd = new FormData()
      fd.append('pin_type', type)
      fd.append('pin', pin)
      const res = await fetch(`${API}/api/verify_pin`, { method: 'POST', body: fd })
      const data = await res.json()
      if (data.valid) {
        onUnlock()
      } else {
        setError('Invalid PIN')
      }
    } catch (e) {
      setError('Error verifying')
    }
  }

  return (
    <div className="min-h-screen bg-obsidian-bg flex flex-col items-center justify-center p-6">
      <span className="text-emerald text-4xl mb-4">◆</span>
      <h1 className="text-xl font-semibold mb-1">JuteVision</h1>
      <p className="text-sm text-obsidian-muted mb-6">Enter {type === 'app' ? 'App' : 'File'} PIN</p>
      <input
        type="password"
        inputMode="numeric"
        maxLength={8}
        value={pin}
        onChange={e => { setPin(e.target.value); setError('') }}
        onKeyDown={e => e.key === 'Enter' && submit()}
        placeholder="••••"
        className="w-full max-w-[200px] px-4 py-3 rounded-lg bg-obsidian-card border border-obsidian-border text-center text-lg tracking-widest focus:outline-none focus:border-emerald/50"
        autoFocus
      />
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      <button onClick={submit} className="mt-6 px-8 py-2.5 rounded-lg bg-emerald/20 text-emerald-bright font-medium border border-emerald/40 hover:bg-emerald/30 transition">
        Unlock
      </button>
    </div>
  )
}

// --- Settings Modal ---
function SettingsModal({ show, onClose, settings, onRefresh }) {
  const [appPinEnabled, setAppPinEnabled] = useState(settings.app_pin_enabled)
  const [filePinEnabled, setFilePinEnabled] = useState(settings.file_pin_enabled)
  const [appPin, setAppPin] = useState('')
  const [filePin, setFilePin] = useState('')
  const [toast, setToast] = useState('')

  const saveAppPin = async () => {
    if (appPinEnabled && !appPin) { setToast('Enter PIN'); return }
    try {
      const fd = new FormData()
      fd.append('enabled', appPinEnabled)
      fd.append('pin', appPin)
      await fetch(`${API}/api/settings/app_pin`, { method: 'POST', body: fd })
      setToast('App PIN saved')
      setAppPin('')
      onRefresh()
    } catch (e) { setToast('Failed') }
  }

  const saveFilePin = async () => {
    if (filePinEnabled && !filePin) { setToast('Enter PIN'); return }
    try {
      const fd = new FormData()
      fd.append('enabled', filePinEnabled)
      fd.append('pin', filePin)
      await fetch(`${API}/api/settings/file_pin`, { method: 'POST', body: fd })
      setToast('File PIN saved')
      setFilePin('')
      onRefresh()
    } catch (e) { setToast('Failed') }
  }

  useEffect(() => { if (toast) setTimeout(() => setToast(''), 2000) }, [toast])

  if (!show) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={onClose}>
      <div className="w-full max-w-md rounded-xl border border-obsidian-border bg-obsidian-card p-6 shadow-xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold">Settings & Safety</h2>
          <button onClick={onClose} className="text-obsidian-muted hover:text-gray-300">✕</button>
        </div>

        {/* App PIN */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">App PIN</span>
            <label className="flex items-center gap-2">
              <span className="text-xs text-obsidian-muted">Enable</span>
              <input type="checkbox" checked={appPinEnabled} onChange={e => setAppPinEnabled(e.target.checked)} className="rounded" />
            </label>
          </div>
          {appPinEnabled && (
            <div className="flex gap-2 mt-2">
              <input type="password" inputMode="numeric" placeholder="Set PIN" value={appPin} onChange={e => setAppPin(e.target.value)} className="flex-1 px-3 py-2 rounded-lg bg-obsidian-bg border border-obsidian-border text-sm focus:outline-none focus:border-emerald/50" />
              <button onClick={saveAppPin} className="px-4 py-2 rounded-lg bg-emerald/20 text-emerald-bright text-sm font-medium">Save</button>
            </div>
          )}
        </div>

        {/* File PIN */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">File Access PIN</span>
            <label className="flex items-center gap-2">
              <span className="text-xs text-obsidian-muted">Enable</span>
              <input type="checkbox" checked={filePinEnabled} onChange={e => setFilePinEnabled(e.target.checked)} className="rounded" />
            </label>
          </div>
          {filePinEnabled && (
            <div className="flex gap-2 mt-2">
              <input type="password" inputMode="numeric" placeholder="Set PIN" value={filePin} onChange={e => setFilePin(e.target.value)} className="flex-1 px-3 py-2 rounded-lg bg-obsidian-bg border border-obsidian-border text-sm focus:outline-none focus:border-emerald/50" />
              <button onClick={saveFilePin} className="px-4 py-2 rounded-lg bg-emerald/20 text-emerald-bright text-sm font-medium">Save</button>
            </div>
          )}
          <p className="text-xs text-obsidian-muted mt-1">Required for Save & Saved Images</p>
        </div>

        {toast && <p className="text-sm text-emerald-bright">{toast}</p>}
      </div>
    </div>
  )
}

// --- Saved Images Modal ---
function SavedImagesModal({ show, onClose, filePinEnabled }) {
  const [files, setFiles] = useState([])
  const [pin, setPin] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (show) load()
  }, [show])

  const load = async () => {
    try {
      const url = filePinEnabled ? `${API}/api/saved?file_pin=${encodeURIComponent(pin)}` : `${API}/api/saved`
      const res = await fetch(url)
      if (res.status === 403) { setError('Invalid PIN'); return }
      const data = await res.json()
      setFiles(data.files || [])
      setError('')
    } catch (e) { setError('Failed to load') }
  }

  const getUrl = f => filePinEnabled ? `${API}/api/saved/${f}?file_pin=${encodeURIComponent(pin)}` : `${API}/api/saved/${f}`

  if (!show) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl border border-obsidian-border bg-obsidian-card p-6 shadow-xl max-h-[85vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Saved Images</h2>
          <button onClick={onClose} className="text-obsidian-muted hover:text-gray-300">✕</button>
        </div>
        {filePinEnabled && (
          <div className="flex gap-2 mb-4">
            <input type="password" inputMode="numeric" placeholder="File PIN" value={pin} onChange={e => { setPin(e.target.value); setError('') }} className="flex-1 px-3 py-2 rounded-lg bg-obsidian-bg border border-obsidian-border text-sm focus:outline-none" />
            <button onClick={load} className="px-4 py-2 rounded-lg bg-emerald/20 text-emerald-bright text-sm font-medium">Load</button>
          </div>
        )}
        {error && <p className="text-sm text-red-400 mb-2">{error}</p>}
        <div className="flex-1 overflow-y-auto grid grid-cols-2 sm:grid-cols-3 gap-2">
          {files.map(f => (
            <a key={f} href={getUrl(f)} target="_blank" rel="noopener noreferrer" className="block rounded-lg overflow-hidden border border-obsidian-border hover:border-emerald/40 transition">
              <img src={getUrl(f)} alt={f} className="w-full aspect-square object-cover" />
            </a>
          ))}
        </div>
        {files.length === 0 && !error && <p className="text-sm text-obsidian-muted py-8 text-center">No saved images</p>}
      </div>
    </div>
  )
}

// --- Scan View (the old main UI) ---
function ScanView({ metrics, settings, onMetricsUpdate, onBack, onViewResults }) {
  const [loading, setLoading] = useState(null)
  const [toast, setToast] = useState('')
  const [confirm, setConfirm] = useState(null)
  const [showSettings, setShowSettings] = useState(false)
  const [showSaved, setShowSaved] = useState(false)
  const [showUploadResult, setShowUploadResult] = useState(null)
  const [feedError, setFeedError] = useState(false)
  const fileInputRef = useRef(null)

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/metrics`)
      onMetricsUpdate(await res.json())
    } catch (e) {}
  }, [onMetricsUpdate])

  const fetchSettings = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/settings`)
      return await res.json()
    } catch (e) {}
  }, [])

  useEffect(() => {
    fetchMetrics()
    const id = setInterval(fetchMetrics, 1500)
    return () => clearInterval(id)
  }, [fetchMetrics])

  useEffect(() => { if (toast) setTimeout(() => setToast(''), 2500) }, [toast])

  const call = async (endpoint, method = 'POST') => {
    setLoading(endpoint)
    try {
      const res = await fetch(`${API}${endpoint}`, { method })
      const data = await res.json().catch(() => ({}))
      await fetchMetrics()
      return data
    } finally { setLoading(null) }
  }

  const confirmAction = (title, message, onConfirm, danger) => {
    setConfirm({ title, message, onConfirm, danger })
  }

  const handleStop = () => confirmAction('Stop Audit', 'End the current scan and mark as complete?', () => call('/api/audit/stop').then(() => {
    setToast('Audit stopped')
    onViewResults()
  }))
  const handleReset = () => confirmAction('Reset Session', 'Clear total and reset to idle?', () => call('/api/audit/reset').then(() => setToast('Session reset')), true)

  const handleSaveImage = () => {
    const needsPin = settings.file_pin_enabled
    if (needsPin) {
      const pin = prompt('Enter File PIN:')
      if (!pin) return
      saveCapture(pin)
    } else saveCapture('')
  }

  const saveCapture = async (filePin) => {
    setLoading('save')
    try {
      const fd = new FormData()
      fd.append('file_pin', filePin)
      const res = await fetch(`${API}/api/capture`, { method: 'POST', body: fd })
      const data = await res.json()
      if (res.ok) setToast('Image saved')
      else setToast(data.detail || 'Failed')
    } catch (e) { setToast('Failed') }
    finally { setLoading(null) }
  }

  const handleUpload = async (e) => {
    const file = e?.target?.files?.[0]
    if (!file) return
    setLoading('upload')
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('save', 'true')
      if (settings.file_pin_enabled) fd.append('file_pin', prompt('Enter File PIN:') || '')
      const res = await fetch(`${API}/api/upload`, { method: 'POST', body: fd })
      const data = await res.json()
      if (res.ok) setShowUploadResult(data)
      else setToast(data.detail || 'Upload failed')
    } catch (e) { setToast('Failed') }
    finally { setLoading(null); e.target.value = '' }
  }

  const statusLabel = { idle: 'Idle', scanning: 'Scanning', analyzing: 'Analyzing', complete: 'Complete', error: 'Error' }[metrics.audit_status] || metrics.audit_status
  const isScanning = metrics.audit_status === 'scanning' || metrics.audit_status === 'analyzing'

  return (
    <div className="min-h-screen bg-charcoal text-white flex flex-col safe-area">
      <header className="flex-shrink-0 border-b border-gray-700 bg-gray-900/80 backdrop-blur-sm px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-4 py-2 rounded-[10px] border border-gray-700 text-gray-300 hover:text-emerald hover:border-emerald/50 transition"
          >
            ← Back
          </button>
          <div className="flex items-center gap-3">
            <span className="text-emerald text-xl sm:text-2xl drop-shadow-[0_0_8px_rgba(80,200,120,0.5)]">◆</span>
            <div>
              <h1 className="text-lg sm:text-xl font-semibold">JuteVision</h1>
              <p className="text-xs text-gray-400 hidden sm:block">Live Audit Scanner</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setShowSaved(true)} className="p-2 rounded-[10px] text-gray-400 hover:text-emerald hover:bg-emerald/10 transition" title="Saved Images">📁</button>
            <button onClick={() => { setShowSettings(true); fetchSettings() }} className="p-2 rounded-[10px] text-gray-400 hover:text-emerald hover:bg-emerald/10 transition" title="Settings">⚙</button>
            <div className={`text-xs font-medium px-2 py-1 rounded-[8px] ${isScanning ? 'text-emerald bg-emerald/10' : 'text-gray-400'}`}>{statusLabel}</div>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col lg:grid lg:grid-cols-[1fr_340px] gap-4 sm:gap-6 p-4 sm:p-6 overflow-auto max-h-[calc(100vh-120px)]">
        <section className="flex flex-col min-h-0 order-1">
          <div className="flex-1 min-h-[280px] sm:min-h-[360px] relative rounded-[15px] overflow-hidden border border-gray-700 bg-gray-900 shadow-lg">
            <div className="absolute inset-0 flex items-center justify-center">
              <img src={VIDEO_URL} alt="Live feed" className="w-full h-full object-contain" onError={() => setFeedError(true)} onLoad={() => setFeedError(false)} />
              {feedError && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-gray-900 text-gray-400 p-4 text-center">
                  <p className="font-medium">Camera feed unavailable</p>
                  <p className="text-sm">Connect to the same network and open from server.</p>
                </div>
              )}
            </div>
            <div className="absolute bottom-3 left-3 text-xs font-medium text-emerald uppercase tracking-wider">Live Audit Feed</div>
          </div>
        </section>

        <aside className="flex flex-col gap-4 order-2">
          <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-4 shadow-lg">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Actions</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <button onClick={() => call('/api/audit/start')} disabled={loading || isScanning} className="min-h-[44px] px-3 py-2.5 rounded-[12px] bg-emerald/20 text-emerald font-medium text-sm border border-emerald/40 hover:bg-emerald/30 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition touch-manipulation">
                {loading === '/api/audit/start' ? '…' : 'Scan'}
              </button>
              <button onClick={handleStop} disabled={loading || !isScanning} className="min-h-[44px] px-3 py-2.5 rounded-[12px] bg-gray-800 text-gray-300 font-medium text-sm border border-gray-700 hover:bg-gray-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition touch-manipulation">
                {loading === '/api/audit/stop' ? '…' : 'Stop'}
              </button>
              <button onClick={handleReset} disabled={loading} className="min-h-[44px] px-3 py-2.5 rounded-[12px] bg-gray-800 text-gray-400 font-medium text-sm border border-gray-700 hover:text-gray-300 active:scale-[0.98] disabled:opacity-50 transition touch-manipulation">
                {loading === '/api/audit/reset' ? '…' : 'Reset'}
              </button>
              <button onClick={() => fileInputRef.current?.click()} disabled={loading} className="min-h-[44px] px-3 py-2.5 rounded-[12px] bg-gray-800 text-gray-300 font-medium text-sm border border-gray-700 hover:bg-gray-700 active:scale-[0.98] disabled:opacity-50 transition touch-manipulation col-span-2 sm:col-span-1">
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleUpload} />
                {loading === 'upload' ? '…' : 'Upload Image'}
              </button>
              <button onClick={() => confirmAction('Save Image', 'Capture and save current frame?', handleSaveImage)} disabled={loading} className="min-h-[44px] px-3 py-2.5 rounded-[12px] bg-emerald/20 text-emerald font-medium text-sm border border-emerald/40 hover:bg-emerald/30 active:scale-[0.98] disabled:opacity-50 transition touch-manipulation">
                {loading === 'save' ? '…' : 'Save Image'}
              </button>
            </div>
          </div>

          <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-5 shadow-lg">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Estimated Jute Weight</h3>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl sm:text-4xl font-bold text-emerald drop-shadow-[0_0_16px_rgba(80,200,120,0.35)]">{metrics.estimated_weight_kg ?? 0}</span>
              <span className="text-base text-gray-400">kg</span>
            </div>
            <p className="mt-1.5 text-sm text-gray-500">{((metrics.confidence ?? 0) * 100).toFixed(0)}% confidence · {metrics.detection_count ?? 0} detections</p>
          </div>

          <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-5 shadow-lg">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Audit Status</h3>
            <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-[10px] font-medium text-sm ${isScanning ? 'text-emerald border border-emerald/40 bg-emerald/10' : 'text-gray-400 border border-gray-700'}`}>
              <span className={`w-2 h-2 rounded-full ${isScanning ? 'bg-emerald animate-pulse' : 'bg-gray-600'}`} />
              {statusLabel}
            </div>
          </div>

          <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-5 shadow-lg">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Audit Progress</h3>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-emerald font-medium">{metrics.audit_progress ?? 0}%</span>
              <span className="text-gray-500">Complete</span>
            </div>
            <div className="h-2.5 rounded-full bg-gray-800 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-emerald/50 to-emerald transition-all duration-500" style={{ width: `${metrics.audit_progress ?? 0}%` }} />
            </div>
          </div>

          <div className="rounded-[15px] border border-gray-700 bg-gray-900 p-5 shadow-lg">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Total Jute Scanned</h3>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl sm:text-4xl font-bold text-emerald drop-shadow-[0_0_16px_rgba(80,200,120,0.35)]">{metrics.total_jute_scanned_kg ?? 0}</span>
              <span className="text-base text-gray-400">kg</span>
            </div>
            <p className="mt-1.5 text-sm text-gray-500">Cumulative this session</p>
          </div>

          <div className="h-1 rounded-full bg-gradient-to-r from-transparent via-emerald/50 to-transparent" />
        </aside>
      </main>

      {toast && <div className="fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 rounded-[12px] bg-emerald/20 text-emerald text-sm font-medium border border-emerald/40 shadow-lg z-40">{toast}</div>}

      <ConfirmModal
        show={!!confirm}
        title={confirm?.title}
        message={confirm?.message}
        confirmLabel="Confirm"
        danger={confirm?.danger}
        onConfirm={() => { confirm?.onConfirm?.(); setConfirm(null) }}
        onCancel={() => setConfirm(null)}
      />

      <SettingsModal show={showSettings} onClose={() => setShowSettings(false)} settings={settings} onRefresh={fetchSettings} />

      <SavedImagesModal show={showSaved} onClose={() => setShowSaved(false)} filePinEnabled={settings.file_pin_enabled} />

      {showUploadResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={() => setShowUploadResult(null)}>
          <div className="max-w-md w-full rounded-[15px] border border-gray-700 bg-gray-900 p-6 shadow-xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-white mb-4">Upload Result</h3>
            {showUploadResult.annotated_base64 && <img src={`data:image/jpeg;base64,${showUploadResult.annotated_base64}`} alt="Result" className="w-full rounded-[12px] mb-4" />}
            <p className="text-sm text-gray-400">{showUploadResult.metrics?.weight_kg} kg · {showUploadResult.metrics?.detection_count} detections</p>
            {showUploadResult.saved_as && <p className="text-xs text-emerald mt-1">Saved as {showUploadResult.saved_as}</p>}
            <button onClick={() => setShowUploadResult(null)} className="mt-4 w-full py-2 rounded-[12px] bg-emerald/20 text-emerald font-medium">Close</button>
          </div>
        </div>
      )}
    </div>
  )
}

// --- Main App ---
function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('dashboard') // 'dashboard', 'scan', 'results'
  const [metrics, setMetrics] = useState({ audit_progress: 0, total_jute_scanned_kg: 0, estimated_weight_kg: 0, detection_count: 0, confidence: 0, audit_status: 'idle' })
  const [settings, setSettings] = useState({ app_pin_enabled: false, file_pin_enabled: false })
  const [unlocked, setUnlocked] = useState(false)

  const fetchSettings = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/settings`)
      setSettings(await res.json())
    } catch (e) {}
  }, [])

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  useEffect(() => {
    if (!settings.app_pin_enabled) setUnlocked(true)
  }, [settings.app_pin_enabled])

  const handleLogin = (userData) => {
    setUser(userData)
    setLoggedIn(true)
    setCurrentPage('dashboard')
  }

  const handleLogout = () => {
    setLoggedIn(false)
    setUser(null)
    setCurrentPage('login')
    setMetrics({ audit_progress: 0, total_jute_scanned_kg: 0, estimated_weight_kg: 0, detection_count: 0, confidence: 0, audit_status: 'idle' })
  }

  if (!loggedIn) {
    return <Login onLogin={handleLogin} />
  }

  if (settings.app_pin_enabled && !unlocked) {
    return <PinLock onUnlock={() => setUnlocked(true)} type="app" />
  }

  return (
    <>
      {currentPage === 'dashboard' && (
        <Dashboard
          user={user}
          onLogout={handleLogout}
          onStartAudit={() => setCurrentPage('scan')}
        />
      )}
      {currentPage === 'scan' && (
        <ScanView
          metrics={metrics}
          settings={settings}
          onMetricsUpdate={setMetrics}
          onBack={() => setCurrentPage('dashboard')}
          onViewResults={() => setCurrentPage('results')}
        />
      )}
      {currentPage === 'results' && (
        <AuditResults
          user={user}
          onBackClick={() => setCurrentPage('scan')}
          metrics={metrics}
          onStartAudit={() => setCurrentPage('scan')}
          onUploadImage={(file) => console.log('Upload:', file)}
          onSaveImage={() => console.log('Save image')}
          isScanning={metrics.audit_status === 'scanning'}
          settings={settings}
        />
      )}
    </>
  )
}

export default App
