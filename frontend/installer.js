/**
 * First-Run Installer
 * Downloads and installs backend dependencies when exe is first opened
 */
const { app, dialog } = require('electron');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');

const userDataPath = app.getPath('userData');
const backendPath = path.join(userDataPath, 'backend');
const venvPath = path.join(backendPath, 'venv');

class BackendInstaller {
    constructor(mainWindow) {
        this.mainWindow = mainWindow;
        this.setupComplete = false;
    }

    async checkAndInstall() {
        // Check if already installed
        if (this.isBackendInstalled()) {
            console.log('✅ Backend already installed');
            return true;
        }

        // Show installation dialog
        const result = await dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'First Time Setup',
            message: 'Setting up application components...',
            detail: 'This will download and install required components. This may take a few minutes.\n\nPlease ensure you have:\n- Internet connection\n- Python 3.14+ installed\n- PostgreSQL and Redis (or Docker)',
            buttons: ['Continue', 'Cancel'],
            defaultId: 0
        });

        if (result.response === 1) {
            return false;
        }

        try {
            await this.installBackend();
            return true;
        } catch (error) {
            dialog.showErrorBox('Installation Error', `Failed to setup: ${error.message}`);
            return false;
        }
    }

    isBackendInstalled() {
        return fs.existsSync(venvPath) && 
               fs.existsSync(path.join(venvPath, 'bin', 'python')) &&
               fs.existsSync(path.join(backendPath, 'requirements.txt'));
    }

    async installBackend() {
        // Create backend directory
        if (!fs.existsSync(backendPath)) {
            fs.mkdirSync(backendPath, { recursive: true });
        }

        // Copy backend files from app bundle
        await this.copyBackendFiles();

        // Create virtual environment
        await this.createVirtualEnvironment();

        // Install Python dependencies
        await this.installDependencies();

        // Run database migrations
        await this.runMigrations();

        this.setupComplete = true;
    }

    async copyBackendFiles() {
        const appPath = app.getAppPath();
        const sourceBackend = path.join(appPath, 'resources', 'backend');
        
        if (fs.existsSync(sourceBackend)) {
            await this.copyDirectory(sourceBackend, backendPath);
        } else {
            // Fallback: use original backend path
            const originalBackend = path.join(appPath, '..', 'backend');
            if (fs.existsSync(originalBackend)) {
                await this.copyDirectory(originalBackend, backendPath);
            } else {
                throw new Error('Backend files not found');
            }
        }
    }

    async copyDirectory(src, dest) {
        return new Promise((resolve, reject) => {
            if (!fs.existsSync(dest)) {
                fs.mkdirSync(dest, { recursive: true });
            }

            const entries = fs.readdirSync(src, { withFileTypes: true });
            const promises = [];

            for (const entry of entries) {
                const srcPath = path.join(src, entry.name);
                const destPath = path.join(dest, entry.name);

                if (entry.isDirectory()) {
                    if (entry.name === 'venv' || entry.name === '__pycache__' || entry.name === '.pytest_cache') {
                        continue; // Skip these
                    }
                    promises.push(this.copyDirectory(srcPath, destPath));
                } else {
                    promises.push(
                        new Promise((res, rej) => {
                            fs.copyFile(srcPath, destPath, (err) => {
                                if (err) rej(err);
                                else res();
                            });
                        })
                    );
                }
            }

            Promise.all(promises).then(resolve).catch(reject);
        });
    }

    async createVirtualEnvironment() {
        return new Promise((resolve, reject) => {
            const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
            
            const proc = spawn(pythonCmd, ['-m', 'venv', venvPath], {
                stdio: 'inherit',
                shell: true
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Virtual environment creation failed with code ${code}`));
                }
            });
        });
    }

    async installDependencies() {
        return new Promise((resolve, reject) => {
            const pipPath = process.platform === 'win32'
                ? path.join(venvPath, 'Scripts', 'pip')
                : path.join(venvPath, 'bin', 'pip');

            const requirementsPath = path.join(backendPath, 'requirements.txt');

            if (!fs.existsSync(requirementsPath)) {
                reject(new Error('requirements.txt not found'));
                return;
            }

            const proc = spawn(pipPath, ['install', '-r', requirementsPath], {
                cwd: backendPath,
                stdio: 'inherit',
                shell: true
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Dependency installation failed with code ${code}`));
                }
            });
        });
    }

    async runMigrations() {
        return new Promise((resolve, reject) => {
            const pythonPath = process.platform === 'win32'
                ? path.join(venvPath, 'Scripts', 'python.exe')
                : path.join(venvPath, 'bin', 'python');

            const proc = spawn(pythonPath, ['-m', 'alembic', 'upgrade', 'head'], {
                cwd: backendPath,
                stdio: 'inherit',
                shell: true
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    // Migration errors are not critical for first run
                    console.warn('Migration warning (non-critical)');
                    resolve();
                }
            });
        });
    }
}

module.exports = BackendInstaller;

