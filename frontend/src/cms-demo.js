// Demo: How to use CMS and AI Autofill in your forms

// Example 1: Simple form with AI autofill
function createCustomerFormWithAI() {
    const form = document.createElement('form');
    form.id = 'customer-form';
    
    // Name field with AI autofill
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.name = 'name';
    nameInput.placeholder = 'Customer Name';
    nameInput.setAttribute('data-ai-autofill', 'field-def-id-here');
    nameInput.setAttribute('data-entity-type', 'customer');
    
    // Email field with AI autofill
    const emailInput = document.createElement('input');
    emailInput.type = 'email';
    emailInput.name = 'email';
    emailInput.placeholder = 'Email';
    emailInput.setAttribute('data-ai-autofill', 'field-def-id-email');
    emailInput.setAttribute('data-entity-type', 'customer');
    
    form.appendChild(nameInput);
    form.appendChild(emailInput);
    
    // Initialize AI autofill after adding to DOM
    document.body.appendChild(form);
    
    // AI autofill will auto-initialize via DOMContentLoaded listener
    // Or manually:
    if (window.AIAutofillInput) {
        new window.AIAutofillInput(nameInput, {
            fieldDefinitionId: 'field-def-id-here',
            entityType: 'customer'
        });
    }
}

// Example 2: Dynamic form with all custom fields
async function createDynamicCustomerForm() {
    const container = document.getElementById('form-container');
    
    const formBuilder = new DynamicFormBuilder('form-container', {
        entityType: 'customer',
        entityId: null, // or existing customer ID
        onSubmit: async (data) => {
            console.log('Form data:', data);
            // Save to API
            try {
                const response = await api.createCustomer(data);
                alert('Customer created!');
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    });
    
    // Render form with all fields (default + custom)
    await formBuilder.render();
    
    // Add "Autofill All" button
    const autofillBtn = document.createElement('button');
    autofillBtn.type = 'button';
    autofillBtn.textContent = '🤖 Autofill All (AI)';
    autofillBtn.className = 'btn btn-secondary';
    autofillBtn.onclick = async () => {
        await formBuilder.autofillAll();
    };
    
    const form = document.getElementById('form-customer');
    if (form) {
        form.insertBefore(autofillBtn, form.lastChild);
    }
}

// Example 3: Add custom field and use it
async function addCustomFieldExample() {
    const token = localStorage.getItem('auth_token');
    
    // Create a custom field
    const response = await fetch('http://localhost:8000/api/v1/cms/fields', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            entity_type: 'customer',
            field_key: 'industry_segment',
            field_label: 'Industry Segment',
            field_type: 'select',
            options: ['Manufacturing', 'Retail', 'Services', 'Technology'],
            ai_enabled: false,
            field_order: 5
        })
    });
    
    const field = await response.json();
    console.log('Created field:', field);
    
    // Now this field will appear in dynamic forms!
}

// Export for use
window.createCustomerFormWithAI = createCustomerFormWithAI;
window.createDynamicCustomerForm = createDynamicCustomerForm;
window.addCustomFieldExample = addCustomFieldExample;

