const controls = [
  { label: 'Wi-Fi', active: true },
  { label: 'Bluetooth', active: false },
  { label: 'Focus', active: false },
  { label: 'Night Light', active: false },
]

export function SystemPanel() {
  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-2">
        {controls.map((c) => (
          <button
            key={c.label}
            className={`
              px-3 py-3 rounded-2xl text-left transition-colors
              ${
                c.active
                  ? 'bg-blue-500/30 border border-blue-400/30'
                  : 'bg-white/5 border border-white/5 hover:bg-white/10'
              }
            `}
          >
            <div className="text-white/90 text-sm font-medium">{c.label}</div>
            <div className="text-white/40 text-xs">{c.active ? 'On' : 'Off'}</div>
          </button>
        ))}
      </div>

      {/* Volume */}
      <div className="px-1">
        <div className="text-white/40 text-xs mb-1.5">Volume</div>
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full w-2/3 bg-white/50 rounded-full" />
        </div>
      </div>

      {/* Brightness */}
      <div className="px-1">
        <div className="text-white/40 text-xs mb-1.5">Brightness</div>
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full w-1/2 bg-white/50 rounded-full" />
        </div>
      </div>
    </div>
  )
}
