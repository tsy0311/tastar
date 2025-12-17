// AI Autofill Component with Tab-to-Accept
class AIAutofillInput {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            apiBaseUrl: options.apiBaseUrl || 'http://localhost:8000/api/v1',
            fieldDefinitionId: options.fieldDefinitionId,
            entityType: options.entityType || 'customer',
            entityId: options.entityId,
            debounceMs: options.debounceMs || 500,
            minChars: options.minChars || 2,
            ...options
        };
        
        this.suggestion = null;
        this.suggestionElement = null;
        this.debounceTimer = null;
        this.isSuggestionVisible = false;
        this.apiToken = localStorage.getItem('auth_token');
        
        this.init();
    }
    
    init() {
        // Create suggestion display element
        this.createSuggestionElement();
        
        // Setup event listeners
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.input.addEventListener('blur', () => this.hideSuggestion());
        this.input.addEventListener('focus', () => {
            if (this.suggestion) {
                this.showSuggestion();
            }
        });
    }
    
    createSuggestionElement() {
        // Create suggestion container
        const container = document.createElement('div');
        container.className = 'ai-suggestion-container';
        container.style.cssText = `
            position: absolute;
            background: #f0f7ff;
            border: 2px solid #4a90e2;
            border-radius: 4px;
            padding: 8px 12px;
            margin-top: 2px;
            font-size: 14px;
            color: #333;
            display: none;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        `;
        
        const suggestionText = document.createElement('span');
        suggestionText.className = 'ai-suggestion-text';
        suggestionText.style.cssText = 'color: #666;';
        
        const suggestionValue = document.createElement('span');
        suggestionValue.className = 'ai-suggestion-value';
        suggestionValue.style.cssText = 'color: #4a90e2; font-weight: 600;';
        
        const hint = document.createElement('span');
        hint.className = 'ai-suggestion-hint';
        hint.textContent = ' (Press Tab to accept)';
        hint.style.cssText = 'color: #999; font-size: 12px; margin-left: 8px;';
        
        container.appendChild(suggestionText);
        container.appendChild(suggestionValue);
        container.appendChild(hint);
        
        // Insert after input
        this.input.parentNode.style.position = 'relative';
        this.input.parentNode.appendChild(container);
        this.suggestionElement = container;
        this.suggestionText = suggestionText;
        this.suggestionValue = suggestionValue;
    }
    
    async handleInput(e) {
        const value = e.target.value;
        
        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Hide suggestion if input is cleared
        if (!value) {
            this.hideSuggestion();
            return;
        }
        
        // Debounce API call
        this.debounceTimer = setTimeout(async () => {
            if (value.length >= this.options.minChars) {
                await this.fetchSuggestion(value);
            } else {
                this.hideSuggestion();
            }
        }, this.options.debounceMs);
    }
    
    async fetchSuggestion(partialValue) {
        if (!this.options.fieldDefinitionId) {
            return;
        }
        
        try {
            // Get existing form data for context
            const existingData = this.getFormData();
            
            const response = await fetch(
                `${this.options.apiBaseUrl}/cms/ai/suggest`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.apiToken}`
                    },
                    body: JSON.stringify({
                        field_definition_id: this.options.fieldDefinitionId,
                        entity_type: this.options.entityType,
                        entity_id: this.options.entityId,
                        partial_value: partialValue,
                        existing_data: existingData
                    })
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to get suggestion');
            }
            
            const data = await response.json();
            
            if (data.suggestion && data.suggestion !== partialValue) {
                this.suggestion = data.suggestion;
                this.showSuggestion(partialValue);
            } else {
                this.hideSuggestion();
            }
        } catch (error) {
            console.error('AI suggestion error:', error);
            this.hideSuggestion();
        }
    }
    
    getFormData() {
        // Get all form data from parent form
        const form = this.input.closest('form');
        if (!form) return {};
        
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            if (value && key !== this.input.name) {
                data[key] = value;
            }
        }
        
        return data;
    }
    
    showSuggestion(partialValue = '') {
        if (!this.suggestion) return;
        
        // Extract the new part of suggestion
        const newPart = this.suggestion.substring(partialValue.length);
        
        this.suggestionText.textContent = partialValue;
        this.suggestionValue.textContent = newPart;
        
        this.suggestionElement.style.display = 'block';
        this.isSuggestionVisible = true;
    }
    
    hideSuggestion() {
        this.suggestionElement.style.display = 'none';
        this.isSuggestionVisible = false;
    }
    
    acceptSuggestion() {
        if (this.suggestion) {
            this.input.value = this.suggestion;
            this.input.dispatchEvent(new Event('input', { bubbles: true }));
            this.hideSuggestion();
            this.suggestion = null;
            return true;
        }
        return false;
    }
    
    handleKeyDown(e) {
        // Tab to accept suggestion
        if (e.key === 'Tab' && this.isSuggestionVisible && this.suggestion) {
            e.preventDefault();
            this.acceptSuggestion();
            return;
        }
        
        // Escape to dismiss
        if (e.key === 'Escape' && this.isSuggestionVisible) {
            this.hideSuggestion();
            return;
        }
        
        // Arrow right to accept
        if (e.key === 'ArrowRight' && this.isSuggestionVisible && this.suggestion) {
            e.preventDefault();
            this.acceptSuggestion();
            return;
        }
    }
}

// Auto-initialize AI autofill on inputs with data-ai-autofill attribute
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-ai-autofill]').forEach(input => {
        const fieldDefId = input.getAttribute('data-ai-autofill');
        const entityType = input.getAttribute('data-entity-type') || 'customer';
        const entityId = input.getAttribute('data-entity-id');
        
        new AIAutofillInput(input, {
            fieldDefinitionId: fieldDefId,
            entityType: entityType,
            entityId: entityId
        });
    });
});

// Export for manual initialization
window.AIAutofillInput = AIAutofillInput;

