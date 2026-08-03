import { motion } from 'framer-motion'
import type { IslandMode } from '../App'
import { MusicPanel } from './panels/MusicPanel'
import { MenuPanel } from './panels/MenuPanel'
import { SearchPanel } from './panels/SearchPanel'
import { SystemPanel } from './panels/SystemPanel'

interface ExpandedPanelProps {
  mode: IslandMode
  onClose: () => void
  onModeChange: (mode: IslandMode) => void
}

export function ExpandedPanel({ mode, onClose, onModeChange }: ExpandedPanelProps) {
  return (
    <motion.div
      initial={{ scale: 0.7, opacity: 0, borderRadius: '50%' }}
      animate={{ scale: 1, opacity: 1, borderRadius: '32px' }}
      exit={{ scale: 0.7, opacity: 0, borderRadius: '50%' }}
      transition={{ type: 'spring', stiffness: 350, damping: 28 }}
      className="
        bg-black/85
        backdrop-blur-island
        shadow-island
        border border-white/10
        overflow-hidden
        w-full
        max-w-[380px]
      "
      style={{
        WebkitAppRegion: 'no-drag',
      } as React.CSSProperties}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-[11px] font-bold text-white">
            F
          </div>
          <span className="text-white/80 text-sm font-medium">Fhish's View</span>
        </div>
        <button
          onClick={onClose}
          className="w-6 h-6 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/60 text-xs transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div className="p-3">
        {mode === 'menu' && <MenuPanel onSelect={onModeChange} />}
        {mode === 'music' && <MusicPanel />}
        {mode === 'search' && <SearchPanel />}
        {mode === 'system' && <SystemPanel />}
      </div>
    </motion.div>
  )
}
