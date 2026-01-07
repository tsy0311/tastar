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
    // Check if venv exists first
    if (!fs.existsSync(venvPath)) {
        console.error('❌ Virtual environment not found at:', venvPath);
        console.log('💡 Attempting to retry installation check...');
        
        // Retry checking after a delay
        setTimeout(() => {
            if (fs.existsSync(venvPath)) {
                console.log('✅ Virtual environment found on retry, starting backend...');
                startBackend();
            } else {
                console.error('❌ Virtual environment still not found after retry');
                if (mainWindow && mainWindow.webContents) {
                    mainWindow.webContents.send('backend-error', 'Backend installation incomplete. Please restart the application.');
                }
            }
        }, 5000);
        return;
    }

    // Try to find Python in venv - check multiple possible paths
    let pythonPath = null;
    const possiblePythonPaths = process.platform === 'win32'
        ? [
            path.join(venvPath, 'Scripts', 'python.exe'),
            path.join(venvPath, 'Scripts', 'python3.exe'),
        ]
        : [
            path.join(venvPath, 'bin', 'python'),
            path.join(venvPath, 'bin', 'python3'),
            path.join(venvPath, 'bin', 'python3.12'),
            path.join(venvPath, 'bin', 'python3.11'),
            path.join(venvPath, 'bin', 'python3.10'),
        ];
    
    for (const possiblePath of possiblePythonPaths) {
        if (fs.existsSync(possiblePath)) {
            pythonPath = possiblePath;
            console.log('✅ Found Python at:', pythonPath);
            break;
        }
    }

    if (!pythonPath) {
        console.error('❌ Python not found in virtual environment');
        console.log('💡 Searched paths:', possiblePythonPaths);
        if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('backend-error', 'Python interpreter not found in virtual environment');
        }
        return;
    }

    const runPy = path.join(backendPath, 'run.py');

    if (!fs.existsSync(runPy)) {
        console.error('❌ Backend run.py not found at:', runPy);
        if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('backend-error', 'Backend files not found');
        }
        return;
    }

    console.log('🚀 Starting backend server...');
    console.log('Python path:', pythonPath);
    console.log('Backend path:', backendPath);
    
    backendProcess = spawn(pythonPath, [runPy], {
        cwd: backendPath,
        stdio: 'pipe',
        env: {
            ...process.env,
            PYTHONUNBUFFERED: '1', // Ensure output is not buffered
            DEBUG: '' // Clear DEBUG env var if set
        }
    });

    let startupLog = '';

    backendProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`[Backend] ${output}`);
        startupLog += output;
        
        // Check if backend started successfully
        if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
            console.log('✅ Backend started successfully');
            if (mainWindow && mainWindow.webContents) {
                mainWindow.webContents.send('backend-ready');
            }
        }
    });

    backendProcess.stderr.on('data', (data) => {
        const output = data.toString();
        console.error(`[Backend Error] ${output}`);
        
        // Check for specific errors
        if (output.includes('Address already in use')) {
            console.log('ℹ️  Backend port already in use, assuming it\'s running');
            if (mainWindow && mainWindow.webContents) {
                mainWindow.webContents.send('backend-ready');
            }
        }
    });

    backendProcess.on('error', (error) => {
        console.error('❌ Failed to start backend process:', error);
        if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('backend-error', error.message);
        }
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
        if (code !== 0 && code !== null) {
            console.error('Backend exited unexpectedly');
            if (mainWindow && mainWindow.webContents) {
                mainWindow.webContents.send('backend-error', `Backend exited with code ${code}`);
            }
        }
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
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: true, // Enable web security for production
            allowRunningInsecureContent: false
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        show: false
    });
    
    // Open DevTools in development mode for debugging
    if (isDev || process.env.ELECTRON_IS_DEV) {
        mainWindow.webContents.openDevTools();
    }

    // Load local HTML file (frontend bundled)
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
    
    // Show window as soon as it's ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        console.log('✅ Window is ready');
    });
    
    // Wait for backend to be ready in background
    waitForBackend().then((ready) => {
        if (ready) {
            console.log('✅ Backend is ready and window is shown');
            // Send message to renderer that backend is ready
            if (mainWindow && mainWindow.webContents) {
                mainWindow.webContents.send('backend-ready');
            }
        } else {
            console.warn('⚠️  Backend is not ready, but showing window anyway');
            if (mainWindow && mainWindow.webContents) {
                mainWindow.webContents.send('backend-not-ready');
            }
        }
    }).catch((error) => {
        console.error('Backend startup error:', error);
        if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('backend-error', error.message);
        }
    });
    
    // Handle console messages from renderer for debugging
    mainWindow.webContents.on('console-message', (event, level, message) => {
        console.log(`[Renderer ${level}]: ${message}`);
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

async function waitForBackend(maxAttempts = 30) {
    // Use Node's https/http instead of fetch in main process
    const http = require('http');
    
    // First check if backend is already running
    try {
        const response = await new Promise((resolve, reject) => {
            const req = http.get(`${BACKEND_URL}/health`, (res) => {
                resolve(res);
            });
            req.on('error', reject);
            req.setTimeout(2000, () => {
                req.destroy();
                reject(new Error('Timeout'));
            });
        });
        
        if (response.statusCode === 200) {
            console.log('✅ Backend is already running');
            return true;
        }
    } catch (error) {
        // Backend not running yet, continue to wait
    }
    
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await new Promise((resolve, reject) => {
                const req = http.get(`${BACKEND_URL}/health`, (res) => {
                    resolve(res);
                });
                req.on('error', reject);
                req.setTimeout(2000, () => {
                    req.destroy();
                    reject(new Error('Timeout'));
                });
            });
            
            if (response.statusCode === 200) {
                console.log('✅ Backend is ready');
                return true;
            }
        } catch (error) {
            // Backend not ready yet
            if (i % 5 === 0) {
                console.log(`Waiting for backend... (${i + 1}/${maxAttempts})`);
            }
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    console.warn('⚠️  Backend failed to start within timeout, continuing anyway...');
    return false; // Don't throw, just return false
}

app.whenReady().then(async () => {
    // Always create window - installation will happen in background if needed
    createWindow();
    
    // Try to ensure backend is ready
    const backendReady = await ensureBackend();
    
    // Wait for backend to be fully installed before starting
    await waitForBackendInstallation();
    
    // Now start the backend server
    startBackend();
});

// Wait for backend installation to complete
async function waitForBackendInstallation(maxAttempts = 60) {
    console.log('⏳ Waiting for backend installation to complete...');
    
    // First check if backend is already running (from external process)
    const http = require('http');
    try {
        const response = await new Promise((resolve, reject) => {
            const req = http.get(`${BACKEND_URL}/health`, (res) => {
                resolve(res);
            });
            req.on('error', reject);
            req.setTimeout(1000, () => {
                req.destroy();
                reject(new Error('Timeout'));
            });
        });
        
        if (response.statusCode === 200) {
            console.log('✅ Backend is already running externally, skipping installation wait');
            return true;
        }
    } catch (error) {
        // Backend not running externally, continue checking installation
    }
    
    for (let i = 0; i < maxAttempts; i++) {
        // Check if venv exists and Python is available
        if (fs.existsSync(venvPath)) {
            // Try to find Python
            const possiblePythonPaths = process.platform === 'win32'
                ? [
                    path.join(venvPath, 'Scripts', 'python.exe'),
                    path.join(venvPath, 'Scripts', 'python3.exe'),
                ]
                : [
                    path.join(venvPath, 'bin', 'python'),
                    path.join(venvPath, 'bin', 'python3'),
                    path.join(venvPath, 'bin', 'python3.12'),
                    path.join(venvPath, 'bin', 'python3.11'),
                    path.join(venvPath, 'bin', 'python3.10'),
                ];
            
            for (const pythonPath of possiblePythonPaths) {
                if (fs.existsSync(pythonPath)) {
                    // Check if run.py exists
                    const runPy = path.join(backendPath, 'run.py');
                    if (fs.existsSync(runPy)) {
                        console.log('✅ Backend installation complete');
                        return true;
                    }
                }
            }
        }
        
        // Wait 1 second before checking again
        if (i % 5 === 0 && i > 0) {
            console.log(`⏳ Still waiting for backend installation... (${i}s)`);
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.warn('⚠️  Backend installation timeout, but continuing anyway...');
    return false;
}

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

