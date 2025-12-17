// API Client for connecting to FastAPI backend
// In Electron app, backend runs on localhost
// In development, use localhost:8000
const API_BASE_URL = window.electronAPI 
    ? 'http://localhost:8000/api/v1'  // Electron app
    : 'http://localhost:8000/api/v1'; // Development

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token') || null;
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        this.setToken(data.access_token);
        return data;
    }

    async logout() {
        this.setToken(null);
    }

    // Companies
    async getCompanies() {
        return this.request('/companies');
    }

    async getCompany(id) {
        return this.request(`/companies/${id}`);
    }

    async createCompany(data) {
        return this.request('/companies', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Customers
    async getCustomers() {
        return this.request('/customers');
    }

    async getCustomer(id) {
        return this.request(`/customers/${id}`);
    }

    async createCustomer(data) {
        return this.request('/customers', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Invoices
    async getInvoices() {
        return this.request('/invoices');
    }

    async getInvoice(id) {
        return this.request(`/invoices/${id}`);
    }

    async createInvoice(data) {
        return this.request('/invoices', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Payments
    async getPayments() {
        return this.request('/payments');
    }

    async getPayment(id) {
        return this.request(`/payments/${id}`);
    }

    async createPayment(data) {
        return this.request('/payments', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// Export singleton instance
const api = new APIClient();

