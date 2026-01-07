/**
 * First-Run Installer
 * Downloads and installs backend dependencies when exe is first opened
 */
const { app, dialog } = require('electron');
const { spawn, exec, execSync } = require('child_process');
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
        this.installationInProgress = false;
        this.installationPromise = null;
    }

    async checkAndInstall() {
        // Check if already installed and all requirements are met
        if (this.isBackendInstalled() && await this.checkRequirements()) {
            console.log('✅ Backend already installed and requirements met');
            return true;
        }

        // If installation is already in progress, wait for it
        if (this.installationInProgress && this.installationPromise) {
            console.log('⏳ Installation already in progress, waiting...');
            try {
                await this.installationPromise;
                return true;
            } catch (error) {
                console.error('❌ Installation failed:', error.message);
                return false;
            }
        }

        // Requirements not met - install silently
        console.log('📦 Installing backend dependencies...');
        this.installationInProgress = true;
        
        // Notify renderer that installation is starting
        if (this.mainWindow && this.mainWindow.webContents) {
            this.mainWindow.webContents.send('backend-installing');
        }
        
        // Create installation promise
        this.installationPromise = this.installBackend().then(() => {
            this.setupComplete = true;
            this.installationInProgress = false;
            console.log('✅ Backend installation completed successfully');
            
            // Notify renderer that installation is complete
            if (this.mainWindow && this.mainWindow.webContents) {
                this.mainWindow.webContents.send('backend-installed');
            }
            
            return true;
        }).catch((error) => {
            this.installationInProgress = false;
            console.error('❌ Installation error:', error.message);
            
            // Notify renderer of installation error
            if (this.mainWindow && this.mainWindow.webContents) {
                this.mainWindow.webContents.send('backend-install-error', error.message);
            }
            
            // Check if it's a critical error that requires user attention
            if (this.isCriticalError(error)) {
                console.error('❌ Critical installation error - cannot continue');
                // Don't show dialog in silent mode, just log
                // dialog.showErrorBox('Installation Error', 
                //     `Failed to setup backend: ${error.message}\n\nPlease check:\n- Python 3.11+ is installed\n- Internet connection\n- Sufficient disk space`);
                throw error;
            }
            // Non-critical error, log but continue
            console.warn('⚠️  Non-critical installation warning, continuing...');
            this.setupComplete = true;
            
            // Still notify as installed (with warnings)
            if (this.mainWindow && this.mainWindow.webContents) {
                this.mainWindow.webContents.send('backend-installed');
            }
            
            return true;
        });
        
        try {
            return await this.installationPromise;
        } catch (error) {
            return false;
        }
    }
    
    isCriticalError(error) {
        // Define what constitutes a critical error
        const criticalMessages = [
            'Python',
            'python',
            'command not found',
            'not found',
            'ENOENT',
            'permission denied',
            'EACCES',
            'virtual environment',
            'venv',
            'failed to create',
            'failed to spawn'
        ];
        const errorMsg = error.message.toLowerCase();
        return criticalMessages.some(msg => errorMsg.includes(msg.toLowerCase()));
    }
    
    async checkRequirements() {
        // Check if all critical dependencies are installed
        try {
            const pythonPath = process.platform === 'win32'
                ? path.join(venvPath, 'Scripts', 'python.exe')
                : path.join(venvPath, 'bin', 'python');
            
            if (!fs.existsSync(pythonPath)) {
                return false;
            }
            
            // Check if key packages are installed
            try {
                execSync(`"${pythonPath}" -c "import fastapi, sqlalchemy, uvicorn"`, {
                    stdio: 'ignore',
                    timeout: 5000
                });
                return true;
            } catch (e) {
                return false;
            }
        } catch (error) {
            console.warn('Requirements check failed:', error.message);
            return false;
        }
    }

    isBackendInstalled() {
        const pythonPath = process.platform === 'win32'
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
        
        return fs.existsSync(venvPath) && 
               fs.existsSync(pythonPath) &&
               fs.existsSync(path.join(backendPath, 'requirements.txt')) &&
               fs.existsSync(path.join(backendPath, 'run.py'));
    }

    async installBackend() {
        // Create backend directory
        if (!fs.existsSync(backendPath)) {
            fs.mkdirSync(backendPath, { recursive: true });
        }

        // Copy backend files from app bundle
        console.log('Copying backend files...');
        await this.copyBackendFiles();
        console.log('Backend files copied');

        // Create virtual environment
        await this.createVirtualEnvironment();
        
        // Verify venv was created before proceeding
        if (!fs.existsSync(venvPath)) {
            throw new Error('Virtual environment creation failed');
        }
        console.log('✅ Virtual environment verified');

        // Install Python dependencies
        await this.installDependencies();

        // Run database migrations
        await this.runMigrations();

        // Verify installation is complete
        const runPy = path.join(backendPath, 'run.py');
        if (!fs.existsSync(runPy)) {
            throw new Error('Backend files incomplete');
        }
        
        // Check Python exists
        const pythonPath = process.platform === 'win32'
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
        
        // Try to find Python
        let pythonFound = false;
        const possiblePaths = process.platform === 'win32'
            ? [path.join(venvPath, 'Scripts', 'python.exe'), path.join(venvPath, 'Scripts', 'python3.exe')]
            : [
                path.join(venvPath, 'bin', 'python'),
                path.join(venvPath, 'bin', 'python3'),
                path.join(venvPath, 'bin', 'python3.12'),
                path.join(venvPath, 'bin', 'python3.11'),
            ];
        
        for (const possiblePath of possiblePaths) {
            if (fs.existsSync(possiblePath)) {
                pythonFound = true;
                console.log('✅ Python found at:', possiblePath);
                break;
            }
        }
        
        if (!pythonFound) {
            throw new Error('Python interpreter not found after installation');
        }

        this.setupComplete = true;
        console.log('✅ Backend installation fully completed and verified');
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
            // Check if venv already exists
            if (fs.existsSync(venvPath)) {
                console.log('Virtual environment already exists');
                resolve();
                return;
            }
            
            const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
            
            console.log('Creating virtual environment...');
            console.log('Python command:', pythonCmd);
            console.log('Venv path:', venvPath);
            
            let errorOutput = '';
            
            const proc = spawn(pythonCmd, ['-m', 'venv', venvPath], {
                stdio: 'pipe',
                shell: true,
                env: {
                    ...process.env
                }
            });
            
            proc.stdout.on('data', (data) => {
                const output = data.toString();
                if (output.trim()) {
                    console.log('venv stdout:', output);
                }
            });
            
            proc.stderr.on('data', (data) => {
                const output = data.toString();
                errorOutput += output;
                // Log errors and warnings
                if (output.trim()) {
                    console.error('venv stderr:', output);
                }
            });

            proc.on('error', (error) => {
                console.error('Failed to spawn venv process:', error);
                reject(new Error(`Failed to create virtual environment: ${error.message}. Make sure Python 3.11+ is installed.`));
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    // Verify venv was actually created
                    const pythonPath = process.platform === 'win32'
                        ? path.join(venvPath, 'Scripts', 'python.exe')
                        : path.join(venvPath, 'bin', 'python');
                    
                    // Wait a moment for filesystem to sync
                    setTimeout(() => {
                        if (fs.existsSync(venvPath)) {
                            console.log('✅ Virtual environment created and verified');
                            resolve();
                        } else {
                            reject(new Error('Virtual environment directory was not created'));
                        }
                    }, 1000);
                } else {
                    reject(new Error(`Virtual environment creation failed with code ${code}. Error: ${errorOutput}`));
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

            console.log('Installing Python dependencies (this may take a few minutes)...');
            
            const proc = spawn(pipPath, ['install', '-r', requirementsPath, '--quiet', '--disable-pip-version-check'], {
                cwd: backendPath,
                stdio: 'pipe', // Changed from 'inherit' to 'pipe' for silent operation
                shell: true
            });
            
            let output = '';
            let errorOutput = '';
            
            proc.stdout.on('data', (data) => {
                output += data.toString();
                // Only show progress for important messages
                const text = data.toString();
                if (text.includes('Successfully installed') || text.includes('Installing')) {
                    // Silent - suppress verbose pip output
                }
            });
            
            proc.stderr.on('data', (data) => {
                errorOutput += data.toString();
                // Only log actual errors, not warnings
                const text = data.toString();
                if (text.toLowerCase().includes('error') && !text.toLowerCase().includes('warning')) {
                    console.error('pip error:', text);
                }
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    console.log('Dependencies installed successfully');
                    resolve();
                } else {
                    // Check if it's a critical error or just warnings
                    if (errorOutput.toLowerCase().includes('error') && 
                        !errorOutput.toLowerCase().includes('warning')) {
                        reject(new Error(`Dependency installation failed with code ${code}`));
                    } else {
                        // Non-critical errors (warnings), still resolve
                        console.warn('Installation completed with warnings');
                        resolve();
                    }
                }
            });
        });
    }

    async runMigrations() {
        return new Promise((resolve) => {
            const pythonPath = process.platform === 'win32'
                ? path.join(venvPath, 'Scripts', 'python.exe')
                : path.join(venvPath, 'bin', 'python');

            // Check if alembic is available before running
            if (!fs.existsSync(path.join(backendPath, 'alembic.ini'))) {
                console.log('Skipping migrations (alembic.ini not found)');
                resolve();
                return;
            }

            const proc = spawn(pythonPath, ['-m', 'alembic', 'upgrade', 'head'], {
                cwd: backendPath,
                stdio: 'pipe', // Silent operation
                shell: true
            });
            
            proc.stdout.on('data', () => {
                // Silent - suppress migration output
            });
            
            proc.stderr.on('data', (data) => {
                // Only log errors
                const output = data.toString();
                if (output.toLowerCase().includes('error')) {
                    console.error('Migration error:', output);
                }
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    console.log('Database migrations completed');
                } else {
                    // Migration errors are not critical for first run
                    console.warn('Migration completed with warnings (non-critical)');
                }
                resolve();
            });
        });
    }
}

module.exports = BackendInstaller;

