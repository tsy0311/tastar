// Dynamic Form Builder with CMS Field Support
class DynamicFormBuilder {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            apiBaseUrl: options.apiBaseUrl || 'http://localhost:8000/api/v1',
            entityType: options.entityType || 'customer',
            entityId: options.entityId,
            onSubmit: options.onSubmit || (() => {}),
            ...options
        };
        
        this.fields = [];
        this.apiToken = localStorage.getItem('auth_token');
    }
    
    async loadFields() {
        try {
            const response = await fetch(
                `${this.options.apiBaseUrl}/cms/fields?entity_type=${this.options.entityType}`,
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiToken}`
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to load fields');
            }
            
            this.fields = await response.json();
            return this.fields;
        } catch (error) {
            console.error('Error loading fields:', error);
            return [];
        }
    }
    
    async render() {
        await this.loadFields();
        
        const form = document.createElement('form');
        form.className = 'dynamic-form';
        form.id = `form-${this.options.entityType}`;
        
        // Render each field
        for (const field of this.fields) {
            if (!field.is_visible) continue;
            
            const fieldElement = this.createFieldElement(field);
            form.appendChild(fieldElement);
        }
        
        // Add submit button
        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn btn-primary';
        submitBtn.textContent = 'Save';
        form.appendChild(submitBtn);
        
        // Handle form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = this.getFormData(form);
            await this.options.onSubmit(formData);
        });
        
        this.container.innerHTML = '';
        this.container.appendChild(form);
        
        // Initialize AI autofill for fields that support it
        this.initializeAIAutofill(form);
    }
    
    createFieldElement(field) {
        const fieldGroup = document.createElement('div');
        fieldGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.textContent = field.field_label;
        label.setAttribute('for', field.field_key);
        if (field.is_required) {
            label.innerHTML += ' <span style="color: red;">*</span>';
        }
        
        let input;
        
        switch (field.field_type) {
            case 'text':
            case 'email':
            case 'phone':
            case 'url':
                input = document.createElement('input');
                input.type = field.field_type === 'email' ? 'email' : 
                            field.field_type === 'url' ? 'url' : 'text';
                break;
                
            case 'number':
            case 'currency':
            case 'percentage':
                input = document.createElement('input');
                input.type = 'number';
                if (field.field_type === 'currency') {
                    input.step = '0.01';
                }
                break;
                
            case 'date':
                input = document.createElement('input');
                input.type = 'date';
                break;
                
            case 'datetime':
                input = document.createElement('input');
                input.type = 'datetime-local';
                break;
                
            case 'boolean':
                input = document.createElement('input');
                input.type = 'checkbox';
                break;
                
            case 'textarea':
                input = document.createElement('textarea');
                input.rows = 4;
                break;
                
            case 'select':
                input = document.createElement('select');
                if (field.options) {
                    field.options.forEach(option => {
                        const optionEl = document.createElement('option');
                        optionEl.value = option;
                        optionEl.textContent = option;
                        input.appendChild(optionEl);
                    });
                }
                break;
                
            case 'multi_select':
                // Create checkbox group
                const container = document.createElement('div');
                if (field.options) {
                    field.options.forEach(option => {
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.value = option;
                        checkbox.name = `${field.field_key}[]`;
                        checkbox.id = `${field.field_key}-${option}`;
                        
                        const checkboxLabel = document.createElement('label');
                        checkboxLabel.setAttribute('for', `${field.field_key}-${option}`);
                        checkboxLabel.textContent = option;
                        
                        container.appendChild(checkbox);
                        container.appendChild(checkboxLabel);
                        container.appendChild(document.createElement('br'));
                    });
                }
                fieldGroup.appendChild(label);
                fieldGroup.appendChild(container);
                return fieldGroup;
                
            default:
                input = document.createElement('input');
                input.type = 'text';
        }
        
        input.id = field.field_key;
        input.name = field.field_key;
        input.required = field.is_required;
        
        if (field.default_value) {
            input.value = field.default_value;
        }
        
        // Add AI autofill if enabled
        if (field.ai_enabled) {
            input.setAttribute('data-ai-autofill', field.id);
            input.setAttribute('data-entity-type', this.options.entityType);
            if (this.options.entityId) {
                input.setAttribute('data-entity-id', this.options.entityId);
            }
        }
        
        // Add placeholder
        if (field.ai_enabled) {
            input.placeholder = `Type to get AI suggestions...`;
        }
        
        fieldGroup.appendChild(label);
        fieldGroup.appendChild(input);
        
        return fieldGroup;
    }
    
    initializeAIAutofill(form) {
        // Initialize AI autofill for all fields with the attribute
        form.querySelectorAll('[data-ai-autofill]').forEach(input => {
            const fieldDefId = input.getAttribute('data-ai-autofill');
            const entityType = input.getAttribute('data-entity-type');
            const entityId = input.getAttribute('data-entity-id');
            
            if (window.AIAutofillInput) {
                new window.AIAutofillInput(input, {
                    fieldDefinitionId: fieldDefId,
                    entityType: entityType,
                    entityId: entityId
                });
            }
        });
    }
    
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            if (key.endsWith('[]')) {
                // Handle multi-select
                const baseKey = key.replace('[]', '');
                if (!data[baseKey]) {
                    data[baseKey] = [];
                }
                data[baseKey].push(value);
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }
    
    async autofillAll() {
        try {
            const form = document.getElementById(`form-${this.options.entityType}`);
            if (!form) return;
            
            const partialData = this.getFormData(form);
            
            const response = await fetch(
                `${this.options.apiBaseUrl}/cms/ai/autofill`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.apiToken}`
                    },
                    body: JSON.stringify({
                        entity_type: this.options.entityType,
                        partial_data: partialData
                    })
                }
            );
            
            if (!response.ok) {
                throw new Error('Autofill failed');
            }
            
            const data = await response.json();
            
            // Apply suggestions
            for (const [fieldKey, suggestionData] of Object.entries(data.suggestions)) {
                const input = form.querySelector(`[name="${fieldKey}"]`);
                if (input && !input.value && suggestionData.suggestion) {
                    input.value = suggestionData.suggestion;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            
            return data;
        } catch (error) {
            console.error('Autofill error:', error);
        }
    }
}

// Export
window.DynamicFormBuilder = DynamicFormBuilder;

