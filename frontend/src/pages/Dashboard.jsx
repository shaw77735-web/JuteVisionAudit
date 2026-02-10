import { useState, useEffect } from 'react'

export default function Dashboard({ user, onLogout, onStartAudit }) {
  const [gps, setGps] = useState({ lat: null, lng: null })
  const [timestamp, setTimestamp] = useState(new Date())

  useEffect(() => {
    // Update timestamp every second
    const timer = setInterval(() => setTimestamp(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    // Get GPS location if available
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setGps({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => setGps({ lat: null, lng: null })
      )
    }
  }, [])

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true })
  }

  const [showProfileMenu, setShowProfileMenu] = useState(false)

  return (
    <div className="min-h-screen bg-charcoal text-white flex flex-col safe-area">
      {/* Header */}
      <header className="border-b border-gray-700 bg-gray-900/80 backdrop-blur-sm px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <span className="text-emerald text-2xl drop-shadow-[0_0_8px_rgba(80,200,120,0.5)]">◆</span>
            <div>
              <h1 className="text-xl font-semibold">JuteVision Auditor</h1>
              <p className="text-xs text-gray-400">Inspector Dashboard</p>
            </div>
          </div>

          {/* Profile Menu */}
          <div className="relative">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="p-2 rounded-[10px] text-gray-400 hover:text-emerald hover:bg-emerald/10 transition"
              title="Profile"
            >
              👤
            </button>
            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-48 rounded-[12px] border border-gray-700 bg-gray-900 shadow-lg z-40">
                <div className="p-3 border-b border-gray-700">
                  <p className="text-sm text-gray-400">Signed in as</p>
                  <p className="text-white font-medium">{user.userId}</p>
                </div>
                <button
                  onClick={() => {
                    setShowProfileMenu(false)
                    onLogout()
                  }}
                  className="w-full px-4 py-2 text-left text-red-400 hover:bg-red-500/10 transition text-sm font-medium"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Metadata Section */}
      <div className="border-b border-gray-700 bg-gray-900/50 px-6 py-4">
        <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Inspector ID */}
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 uppercase tracking-wider">Inspector ID</span>
            <span className="text-lg font-semibold text-emerald">{user.userId}</span>
          </div>

          {/* GPS Location */}
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 uppercase tracking-wider">📍 Live GPS</span>
            <span className="text-lg font-semibold text-white">
              {gps.lat ? `${gps.lat.toFixed(4)}°, ${gps.lng.toFixed(4)}°` : 'N/A'}
            </span>
          </div>

          {/* Timestamp */}
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 uppercase tracking-wider">⏰ Timestamp</span>
            <span className="text-lg font-semibold text-white">{formatTime(timestamp)}</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 gap-8">
        <h2 className="text-3xl font-semibold text-white text-center">Select an Action</h2>

        {/* Action Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 w-full max-w-2xl">
          {/* CLICK TO SCAN Card */}
          <button
            onClick={onStartAudit}
            className="h-48 rounded-[15px] border-2 border-emerald bg-gradient-to-br from-emerald/20 to-emerald/5 hover:from-emerald/30 hover:to-emerald/10 hover:border-emerald/80 flex flex-col items-center justify-center gap-4 transition active:scale-[0.98] group"
          >
            <span className="text-6xl group-hover:scale-110 transition">📷</span>
            <span className="text-2xl font-bold text-emerald group-hover:text-emerald/90">CLICK TO SCAN</span>
          </button>

          {/* UPLOAD IMAGE Card */}
          <button
            onClick={onStartAudit}
            className="h-48 rounded-[15px] border-2 border-emerald bg-gradient-to-br from-emerald/20 to-emerald/5 hover:from-emerald/30 hover:to-emerald/10 hover:border-emerald/80 flex flex-col items-center justify-center gap-4 transition active:scale-[0.98] group"
          >
            <span className="text-6xl group-hover:scale-110 transition">📤</span>
            <span className="text-2xl font-bold text-emerald group-hover:text-emerald/90">UPLOAD IMAGE</span>
          </button>
        </div>

        <p className="text-gray-500 text-sm text-center">
          Ensure proper lighting and jute placement for accurate detection
        </p>
      </main>
    </div>
  )
}
