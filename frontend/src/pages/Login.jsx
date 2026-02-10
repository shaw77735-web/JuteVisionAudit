import { useState } from 'react'

export default function Login({ onLogin }) {
  const [userId, setUserId] = useState('')
  const [password, setPassword] = useState('')
  const [showConfirm, setShowConfirm] = useState(false)
  const [dontAskAgain, setDontAskAgain] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = () => {
    if (!userId.trim() || !password.trim()) {
      setError('Please enter User ID and Password')
      return
    }
    setError('')
    
    // Check localStorage for "don't ask again"
    const skipConfirm = localStorage.getItem('skipAuditConfirm')
    if (skipConfirm === 'true') {
      onLogin({ userId, password })
    } else {
      setShowConfirm(true)
    }
  }

  const handleConfirmProceed = () => {
    if (dontAskAgain) {
      localStorage.setItem('skipAuditConfirm', 'true')
    }
    onLogin({ userId, password })
    setShowConfirm(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleLogin()
    }
  }

  return (
    <div className="min-h-screen bg-charcoal flex flex-col items-center justify-center p-6">
      {/* Header */}
      <div className="text-center mb-12">
        <span className="text-emerald text-5xl mb-4 block drop-shadow-[0_0_8px_rgba(80,200,120,0.5)]">◆</span>
        <h1 className="text-white text-4xl font-bold mb-2">Hello, Inspector</h1>
        <p className="text-gray-400 text-lg">JuteVision Government Audit System</p>
      </div>

      {/* Login Card */}
      <div className="w-full max-w-sm rounded-[15px] border border-gray-700 bg-gray-900 p-8 shadow-2xl">
        <h2 className="text-white text-2xl font-semibold mb-6">Secure Login</h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* User ID Field */}
        <div className="mb-5">
          <label className="block text-white text-sm font-medium mb-2">User ID</label>
          <input
            type="text"
            value={userId}
            onChange={(e) => {
              setUserId(e.target.value)
              setError('')
            }}
            onKeyDown={handleKeyDown}
            placeholder="Enter your User ID"
            className="w-full px-4 py-3 rounded-[12px] bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-emerald/50 transition"
            autoFocus
          />
        </div>

        {/* Password Field */}
        <div className="mb-6">
          <label className="block text-white text-sm font-medium mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              setError('')
            }}
            onKeyDown={handleKeyDown}
            placeholder="Enter your password"
            className="w-full px-4 py-3 rounded-[12px] bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-emerald/50 transition"
          />
        </div>

        {/* Login Button */}
        <button
          onClick={handleLogin}
          className="w-full py-3 rounded-[12px] bg-emerald text-charcoal font-bold text-lg hover:bg-emerald/90 active:scale-[0.98] transition touch-manipulation"
        >
          Login
        </button>

        <p className="text-center text-gray-500 text-xs mt-6">
          Authorized government personnel only
        </p>
      </div>

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={() => setShowConfirm(false)}>
          <div
            className="w-full max-w-sm rounded-[15px] border border-gray-700 bg-gray-900 p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-white text-lg font-semibold mb-3">Proceed to Live Audit?</h3>
            <p className="text-gray-400 text-sm mb-6">You are about to start a live audit session with camera access.</p>

            {/* Checkbox */}
            <label className="flex items-center mb-6 cursor-pointer">
              <input
                type="checkbox"
                checked={dontAskAgain}
                onChange={(e) => setDontAskAgain(e.target.checked)}
                className="w-4 h-4 rounded accent-emerald"
              />
              <span className="text-gray-400 text-sm ml-2">Don't ask again</span>
            </label>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 py-2.5 rounded-[12px] border border-gray-700 text-gray-300 font-medium hover:bg-gray-800 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmProceed}
                className="flex-1 py-2.5 rounded-[12px] bg-emerald text-charcoal font-bold hover:bg-emerald/90 transition"
              >
                Proceed
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
