import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Island } from './components/Island'
import { ExpandedPanel } from './components/ExpandedPanel'

declare global {
  interface Window {
    fhish: {
      resizeIsland: (width: number, height: number) => void
      onToggle: (callback: () => void) => void
    }
  }
}

export type IslandMode = 'collapsed' | 'music' | 'search' | 'system' | 'menu'

function App() {
  const [mode, setMode] = useState<IslandMode>('collapsed')
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    // Listen for global shortcut
    if (window.fhish) {
      window.fhish.onToggle(() => {
        setExpanded((prev) => !prev)
        setMode((prev) => (prev === 'collapsed' ? 'menu' : 'collapsed'))
      })
    }
  }, [])

  useEffect(() => {
    // Resize Electron window based on state
    if (!window.fhish) return

    if (mode === 'collapsed') {
      window.fhish.resizeIsland(180, 36)
    } else if (mode === 'music') {
      window.fhish.resizeIsland(360, 72)
    } else if (mode === 'menu' || mode === 'search' || mode === 'system') {
      window.fhish.resizeIsland(380, 320)
    }
  }, [mode])

  const handleClick = () => {
    if (mode === 'collapsed') {
      setMode('menu')
      setExpanded(true)
    }
  }

  const handleClose = () => {
    setMode('collapsed')
    setExpanded(false)
  }

  return (
    <div className="w-full h-full flex items-start justify-center pt-0">
      <AnimatePresence mode="wait">
        {mode === 'collapsed' && (
          <Island key="collapsed" onClick={handleClick} />
        )}
        {mode !== 'collapsed' && (
          <ExpandedPanel
            key="expanded"
            mode={mode}
            onClose={handleClose}
            onModeChange={setMode}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default App
