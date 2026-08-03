import type { IslandMode } from '../../App'

interface MenuPanelProps {
  onSelect: (mode: IslandMode) => void
}

const items = [
  { id: 'music' as IslandMode, label: 'Music', desc: 'Now playing controls' },
  { id: 'search' as IslandMode, label: 'Search', desc: 'Apps, files, web' },
  { id: 'system' as IslandMode, label: 'System', desc: 'Wi-Fi, volume, focus' },
]

export function MenuPanel({ onSelect }: MenuPanelProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onSelect(item.id)}
          className="
            flex items-center gap-3 px-3 py-2.5 rounded-2xl
            bg-white/5 hover:bg-white/10
            transition-colors text-left
          "
        >
          <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-white/70 text-xs font-semibold">
            {item.label.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="text-white/90 text-sm font-medium">{item.label}</div>
            <div className="text-white/40 text-xs">{item.desc}</div>
          </div>
        </button>
      ))}

      <div className="mt-2 pt-2 border-t border-white/5 text-center">
        <p className="text-white/30 text-[11px]">Your Windows. Reimagined.</p>
      </div>
    </div>
  )
}
