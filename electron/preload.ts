import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('fhish', {
  resizeIsland: (width: number, height: number) => {
    ipcRenderer.send('resize-island', { width, height })
  },
  onToggle: (callback: () => void) => {
    ipcRenderer.on('toggle-island', () => callback())
  },
})
