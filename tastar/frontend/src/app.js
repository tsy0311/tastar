// Main Application Logic
// APIClient is defined in api.js
// Use the singleton instance from api.js, or create a new one
let api = window.apiClientInstance || null;

// Application State
let currentUser = null;
let currentPage = 'dashboard';

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    console.log('App initializing...');
    console.log('Is Electron?', typeof window.electronAPI !== 'undefined');
    console.log('API Base URL:', typeof APIClient !== 'undefined' ? 'http://localhost:8000/api/v1' : 'N/A');
    
    try {
        // Initialize API client (use existing instance or create new one)
        if (!api) {
            if (typeof APIClient !== 'undefined') {
                api = window.apiClientInstance || new APIClient();
            } else {
                console.error('APIClient class not found!');
            }
        }
        console.log('API client initialized:', api ? 'success' : 'failed');
        
        // Listen for backend status in Electron
        if (window.electronAPI) {
            window.electronAPI.onBackendReady(() => {
                console.log('✅ Backend is ready (from Electron)');
                hideBackendStatus();
            });
            
            window.electronAPI.onBackendNotReady(() => {
                console.warn('⚠️  Backend is not ready (from Electron)');
                showBackendWarning();
            });
            
            window.electronAPI.onBackendError((message) => {
                console.error('❌ Backend error (from Electron):', message);
                showBackendError(message);
            });
            
            window.electronAPI.onBackendInstalling(() => {
                console.log('📦 Backend installation in progress...');
                showBackendInstalling();
            });
            
            window.electronAPI.onBackendInstalled(() => {
                console.log('✅ Backend installation completed');
                hideBackendStatus();
            });
            
            window.electronAPI.onBackendInstallError((message) => {
                console.error('❌ Backend installation error:', message);
                showBackendError('Installation error: ' + message);
            });
        }
        
        checkAuth();
        setupEventListeners();
        console.log('Event listeners setup complete');
        
        // Test backend connection
        testBackendConnection();
    } catch (error) {
        console.error('Error during app initialization:', error);
        alert('Failed to initialize app: ' + error.message);
    }
});

// Test backend connection on startup
async function testBackendConnection() {
    try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
            console.log('✅ Backend is accessible');
        } else {
            console.warn('⚠️  Backend health check returned:', response.status);
        }
    } catch (error) {
        console.error('❌ Backend connection test failed:', error.message);
        if (window.electronAPI) {
            showBackendWarning();
        }
    }
}

function showBackendWarning() {
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
        errorDiv.textContent = 'Backend is starting up. Please wait a moment and try again.';
        errorDiv.style.display = 'block';
        errorDiv.style.background = '#fff3cd';
        errorDiv.style.color = '#856404';
        errorDiv.style.border = '1px solid #ffc107';
        errorDiv.style.whiteSpace = 'pre-line';
    }
}

function showBackendInstalling() {
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
        errorDiv.textContent = 'Installing backend dependencies...\nThis may take a few minutes.\nPlease wait.';
        errorDiv.style.display = 'block';
        errorDiv.style.background = '#d1ecf1';
        errorDiv.style.color = '#0c5460';
        errorDiv.style.border = '1px solid #bee5eb';
        errorDiv.style.whiteSpace = 'pre-line';
    }
}

function hideBackendStatus() {
    const errorDiv = document.getElementById('login-error');
    if (errorDiv && errorDiv.style.display !== 'none') {
        // Only hide if it's a status message, not an error
        if (errorDiv.style.background.includes('d1ecf1') || errorDiv.style.background.includes('fff3cd')) {
            errorDiv.style.display = 'none';
        }
    }
}

function showBackendError(message) {
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
        errorDiv.textContent = `Backend error: ${message}`;
        errorDiv.style.display = 'block';
        errorDiv.style.background = '#fee';
        errorDiv.style.color = '#c33';
        errorDiv.style.border = '1px solid #fcc';
        errorDiv.style.whiteSpace = 'pre-line';
    }
}

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    if (token) {
        showMainApp();
        loadDashboard();
    } else {
        showLogin();
    }
}

// Show login screen
function showLogin() {
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('main-app').classList.remove('active');
}

// Show main application
function showMainApp() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('main-app').classList.add('active');
}

// Setup event listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        console.log('Login form found, adding submit listener');
        loginForm.addEventListener('submit', handleLogin);
    } else {
        console.error('Login form not found!');
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });
    
    console.log('Event listeners setup complete');
}

// Handle login
async function handleLogin(e) {
    console.log('Login form submitted');
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');
    
    // Find submit button - try multiple ways
    let submitBtn = e.target.querySelector('button[type="submit"]');
    if (!submitBtn) {
        submitBtn = document.querySelector('#login-form button[type="submit"]');
    }

    try {
        console.log('Attempting login for:', email);
        console.log('API Base URL:', 'http://localhost:8000/api/v1');
        errorDiv.style.display = 'none';
        
        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';
        }
        
        // Test backend connection first
        try {
            const healthCheck = await fetch('http://localhost:8000/health');
            if (!healthCheck.ok) {
                throw new Error('Backend health check failed');
            }
            console.log('✅ Backend health check passed');
        } catch (healthError) {
            console.error('❌ Backend health check failed:', healthError);
            throw new Error('Cannot connect to backend server. Please ensure the backend is running.');
        }
        
        console.log('Calling API login...');
        const response = await api.login(email, password);
        console.log('Login successful:', response);
        currentUser = response.user;
        showMainApp();
        loadDashboard();
    } catch (error) {
        console.error('Login error:', error);
        console.error('Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        let errorMessage = error.message || 'Login failed. Please check your credentials.';
        
        // Provide more specific guidance
        if (errorMessage.includes('database') || errorMessage.includes('Database') || errorMessage.includes('Server error')) {
            errorMessage = 'Server error: Database connection issue.\n\nTo fix:\n1. Start Docker Desktop\n2. Run: cd tastar && docker-compose up -d\n3. Run: cd backend && python scripts/seed_db.py';
        } else if (errorMessage.includes('connect') || errorMessage.includes('Cannot connect') || errorMessage.includes('Failed to fetch')) {
            errorMessage = 'Cannot connect to backend server.\n\nPlease ensure:\n1. Backend server is running on http://localhost:8000\n2. Check Electron console for backend status';
        } else if (errorMessage.includes('Internal Server Error')) {
            errorMessage = 'Server error occurred. Please check:\n1. Backend server is running\n2. Database is connected\n3. Check console for details';
        }
        
        errorDiv.textContent = errorMessage;
        errorDiv.style.display = 'block';
        errorDiv.style.whiteSpace = 'pre-line'; // Allow line breaks
        errorDiv.style.background = '#fee';
        errorDiv.style.color = '#c33';
        errorDiv.style.border = '1px solid #fcc';
    } finally {
        // Restore button state
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In';
        }
    }
}

// Handle logout
function handleLogout() {
    api.logout();
    currentUser = null;
    showLogin();
}

// Navigate to page
function navigateToPage(page) {
    currentPage = page;
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    
    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        companies: 'Companies',
        customers: 'Customers',
        invoices: 'Invoices',
        payments: 'Payments'
    };
    document.getElementById('page-title').textContent = titles[page] || 'Dashboard';
    
    // Show/hide pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });
    
    // Load page data
    loadPageData(page);
}

// Load page data
async function loadPageData(page) {
    try {
        switch(page) {
            case 'dashboard':
                await loadDashboard();
                break;
            case 'companies':
                await loadCompanies();
                break;
            case 'customers':
                await loadCustomers();
                break;
            case 'invoices':
                await loadInvoices();
                break;
            case 'payments':
                await loadPayments();
                break;
        }
    } catch (error) {
        console.error('Error loading page data:', error);
        showError(`Failed to load ${page} data: ${error.message}`);
    }
}

// Load dashboard
async function loadDashboard() {
    try {
        console.log('Loading dashboard data...');
        
        // Load all stats with better error handling
        const [companiesResult, customersResult, invoicesResult, paymentsResult] = await Promise.allSettled([
            api.getCompanies().catch(err => {
                console.warn('Companies load error:', err);
                return [];
            }),
            api.getCustomers().catch(err => {
                console.warn('Customers load error:', err);
                return [];
            }),
            api.getInvoices().catch(err => {
                console.warn('Invoices load error:', err);
                return [];
            }),
            api.getPayments().catch(err => {
                console.warn('Payments load error:', err);
                return [];
            })
        ]);

        const companies = companiesResult.status === 'fulfilled' ? companiesResult.value : [];
        const customers = customersResult.status === 'fulfilled' ? customersResult.value : [];
        const invoices = invoicesResult.status === 'fulfilled' ? invoicesResult.value : [];
        const payments = paymentsResult.status === 'fulfilled' ? paymentsResult.value : [];

        // Update stats
        const statCompanies = document.getElementById('stat-companies');
        const statCustomers = document.getElementById('stat-customers');
        const statInvoices = document.getElementById('stat-invoices');
        const statPayments = document.getElementById('stat-payments');
        
        if (statCompanies) statCompanies.textContent = Array.isArray(companies) ? companies.length : 0;
        if (statCustomers) statCustomers.textContent = Array.isArray(customers) ? customers.length : 0;
        if (statInvoices) statInvoices.textContent = Array.isArray(invoices) ? invoices.length : 0;
        if (statPayments) statPayments.textContent = Array.isArray(payments) ? payments.length : 0;
        
        console.log('Dashboard loaded:', {
            companies: Array.isArray(companies) ? companies.length : 0,
            customers: Array.isArray(customers) ? customers.length : 0,
            invoices: Array.isArray(invoices) ? invoices.length : 0,
            payments: Array.isArray(payments) ? payments.length : 0
        });
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// Load companies
async function loadCompanies() {
    try {
        console.log('Loading companies...');
        const companies = await api.getCompanies();
        console.log('Companies loaded:', companies);
        
        const listDiv = document.getElementById('companies-list');
        
        if (!listDiv) {
            console.error('Companies list div not found');
            return;
        }
        
        listDiv.innerHTML = companies && companies.length > 0 
            ? companies.map(c => `
                <div class="list-item">
                    <div>
                        <strong>${c.name || c.legal_name || 'Unnamed Company'}</strong>
                        <p>${c.country || ''} | ${c.currency_code || ''} | ${c.tax_id || ''}</p>
                    </div>
                </div>
            `).join('')
            : '<p class="empty-state">No companies found</p>';
    } catch (error) {
        console.error('Error loading companies:', error);
        const listDiv = document.getElementById('companies-list');
        if (listDiv) {
            listDiv.innerHTML = 
                `<p class="error">Error loading companies: ${error.message}</p>`;
        }
    }
}

// Load customers
async function loadCustomers() {
    try {
        const customers = await api.getCustomers();
        const listDiv = document.getElementById('customers-list');
        listDiv.innerHTML = customers.length > 0
            ? customers.map(c => `
                <div class="list-item">
                    <div>
                        <strong>${c.name}</strong>
                        <p>${c.customer_code} | ${c.primary_email || ''}</p>
                    </div>
                </div>
            `).join('')
            : '<p class="empty-state">No customers found</p>';
    } catch (error) {
        document.getElementById('customers-list').innerHTML = 
            `<p class="error">Error loading customers: ${error.message}</p>`;
    }
}

// Load invoices
async function loadInvoices() {
    try {
        const invoices = await api.getInvoices();
        const listDiv = document.getElementById('invoices-list');
        listDiv.innerHTML = invoices.length > 0
            ? invoices.map(i => `
                <div class="list-item">
                    <div>
                        <strong>${i.invoice_number}</strong>
                        <p>$${i.total_amount} | ${i.status} | Due: ${i.due_date}</p>
                    </div>
                </div>
            `).join('')
            : '<p class="empty-state">No invoices found</p>';
    } catch (error) {
        document.getElementById('invoices-list').innerHTML = 
            `<p class="error">Error loading invoices: ${error.message}</p>`;
    }
}

// Load payments
async function loadPayments() {
    try {
        const payments = await api.getPayments();
        const listDiv = document.getElementById('payments-list');
        listDiv.innerHTML = payments.length > 0
            ? payments.map(p => `
                <div class="list-item">
                    <div>
                        <strong>${p.payment_number}</strong>
                        <p>$${p.amount} | ${p.status} | ${p.payment_date}</p>
                    </div>
                </div>
            `).join('')
            : '<p class="empty-state">No payments found</p>';
    } catch (error) {
        document.getElementById('payments-list').innerHTML = 
            `<p class="error">Error loading payments: ${error.message}</p>`;
    }
}

// Show error message
function showError(message) {
    // You can implement a toast notification here
    console.error(message);
    alert(message);
}

