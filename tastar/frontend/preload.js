// Preload script - runs in isolated context
// Provides secure bridge between renderer and main process

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process
// to use the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any Electron APIs you need here
  platform: process.platform,
  versions: process.versions,
  
  // Backend status events
  onBackendReady: (callback) => {
    ipcRenderer.on('backend-ready', callback);
  },
  onBackendNotReady: (callback) => {
    ipcRenderer.on('backend-not-ready', callback);
  },
  onBackendError: (callback) => {
    ipcRenderer.on('backend-error', (event, message) => callback(message));
  },
  onBackendInstalling: (callback) => {
    ipcRenderer.on('backend-installing', callback);
  },
  onBackendInstalled: (callback) => {
    ipcRenderer.on('backend-installed', callback);
  },
  onBackendInstallError: (callback) => {
    ipcRenderer.on('backend-install-error', (event, message) => callback(message));
  },
  
  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

