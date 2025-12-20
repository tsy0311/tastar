// Preload script - runs in isolated context
// Provides secure bridge between renderer and main process

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process
// to use the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any Electron APIs you need here
  platform: process.platform,
  versions: process.versions
});

