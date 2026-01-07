/**
 * Electron Main Process - Bundles Backend + Frontend
 */
const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const BackendInstaller = require('./installer');

let mainWindow;
let backendProcess = null;
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

// Paths
const isDev = process.env.NODE_ENV === 'development';
const appPath = app.getAppPath();
const userDataPath = app.getPath('userData');
const backendPath = path.join(userDataPath, 'backend');
const venvPath = path.join(backendPath, 'venv');
const requirementsPath = path.join(backendPath, 'requirements.txt');

async function ensureBackend() {
    const installer = new BackendInstaller(mainWindow);
    return await installer.checkAndInstall();
}


function startBackend() {
    const pythonPath = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');

    const runPy = path.join(backendPath, 'run.py');

    if (!fs.existsSync(pythonPath) || !fs.existsSync(runPy)) {
        console.error('Backend not found');
        return;
    }

    backendProcess = spawn(pythonPath, [runPy], {
        cwd: backendPath,
        stdio: 'pipe'
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        show: false
    });

    // Load local HTML file (frontend bundled)
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
    
    // Wait for backend to be ready, then redirect to API
    waitForBackend().then(() => {
        // Backend is ready, frontend will connect to it
        mainWindow.once('ready-to-show', () => {
            mainWindow.show();
        });
    }).catch((error) => {
        console.error('Backend startup error:', error);
        // Still show window, user can configure backend manually
        mainWindow.once('ready-to-show', () => {
            mainWindow.show();
        });
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

async function waitForBackend(maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await fetch(`${BACKEND_URL}/health`);
            if (response.ok) {
                return true;
            }
        } catch (error) {
            // Backend not ready yet
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    throw new Error('Backend failed to start');
}

app.whenReady().then(async () => {
    const backendReady = await ensureBackend();
    if (backendReady) {
        startBackend();
        createWindow();
    }
});

app.on('window-all-closed', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('before-quit', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
});

