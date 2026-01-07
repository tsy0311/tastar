// Main Application Logic
// APIClient is defined in api.js
let api;

// Application State
let currentUser = null;
let currentPage = 'dashboard';

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Initialize API client
    api = new APIClient();
    checkAuth();
    setupEventListeners();
});

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
    // Login form
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        errorDiv.style.display = 'none';
        const response = await api.login(email, password);
        currentUser = response.user;
        showMainApp();
        loadDashboard();
    } catch (error) {
        errorDiv.textContent = error.message || 'Login failed. Please check your credentials.';
        errorDiv.style.display = 'block';
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
        const [companies, customers, invoices, payments] = await Promise.all([
            api.getCompanies().catch(() => []),
            api.getCustomers().catch(() => []),
            api.getInvoices().catch(() => []),
            api.getPayments().catch(() => [])
        ]);

        document.getElementById('stat-companies').textContent = companies.length || 0;
        document.getElementById('stat-customers').textContent = customers.length || 0;
        document.getElementById('stat-invoices').textContent = invoices.length || 0;
        document.getElementById('stat-payments').textContent = payments.length || 0;
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// Load companies
async function loadCompanies() {
    try {
        const companies = await api.getCompanies();
        const listDiv = document.getElementById('companies-list');
        listDiv.innerHTML = companies.length > 0 
            ? companies.map(c => `
                <div class="list-item">
                    <div>
                        <strong>${c.name}</strong>
                        <p>${c.email || ''} | ${c.country || ''}</p>
                    </div>
                </div>
            `).join('')
            : '<p class="empty-state">No companies found</p>';
    } catch (error) {
        document.getElementById('companies-list').innerHTML = 
            `<p class="error">Error loading companies: ${error.message}</p>`;
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

