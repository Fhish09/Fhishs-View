export function MusicPanel() {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="text-white/90 text-sm font-medium truncate">No media playing</div>
          <div className="text-white/40 text-xs truncate">Open Spotify, YouTube, or VLC</div>
        </div>
      </div>

      {/* Progress */}
      <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
        <div className="h-full w-0 bg-white/50 rounded-full" />
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-6">
        <button className="text-white/50 hover:text-white/80 transition-colors text-sm">Prev</button>
        <button className="w-10 h-10 rounded-full bg-white/15 hover:bg-white/25 flex items-center justify-center text-white text-sm font-medium transition-colors">
          Play
        </button>
        <button className="text-white/50 hover:text-white/80 transition-colors text-sm">Next</button>
      </div>
    </div>
  )
}
