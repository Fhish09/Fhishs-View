import { app, BrowserWindow, screen, globalShortcut, ipcMain } from 'electron'
import path from 'path'

let mainWindow: BrowserWindow | null = null

const isDev = !app.isPackaged

function createWindow() {
  const { width } = screen.getPrimaryDisplay().workAreaSize

  mainWindow = new BrowserWindow({
    width: 420,
    height: 64,
    x: Math.round((width - 420) / 2),
    y: 12,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    hasShadow: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // Make window click-through when not interacting (can be toggled later)
  mainWindow.setIgnoreMouseEvents(false)

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // Global shortcut to toggle / expand (Ctrl+Shift+Space)
  globalShortcut.register('CommandOrControl+Shift+Space', () => {
    if (mainWindow) {
      mainWindow.webContents.send('toggle-island')
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// Resize the island window from renderer
ipcMain.on('resize-island', (_event, { width, height }: { width: number; height: number }) => {
  if (!mainWindow) return
  const { width: screenWidth } = screen.getPrimaryDisplay().workAreaSize
  const x = Math.round((screenWidth - width) / 2)
  mainWindow.setBounds({ x, y: 12, width, height }, true)
})

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  globalShortcut.unregisterAll()
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
