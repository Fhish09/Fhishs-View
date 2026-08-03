import { motion } from 'framer-motion'

interface IslandProps {
  onClick: () => void
}

export function Island({ onClick }: IslandProps) {
  return (
    <motion.div
      initial={{ scale: 0.6, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.6, opacity: 0 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      onClick={onClick}
      className="
        cursor-pointer
        bg-black/80
        backdrop-blur-island
        rounded-full
        h-9
        w-[180px]
        flex items-center justify-center
        shadow-island
        border border-white/10
        hover:border-white/20
        transition-colors
        select-none
      "
      style={{
        WebkitAppRegion: 'drag',
      } as React.CSSProperties}
    >
      <div className="flex items-center gap-2 pointer-events-none">
        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-[10px] font-bold text-white shadow-sm">
          F
        </div>
        <span className="text-white/70 text-xs font-medium tracking-wide">
          Fhish's View
        </span>
      </div>
    </motion.div>
  )
}
