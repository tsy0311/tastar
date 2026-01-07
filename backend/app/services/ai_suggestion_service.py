"""
AI Suggestion Service for Autofill and Smart Suggestions
"""
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logging import logger
import openai
from openai import AsyncOpenAI
import anthropic

class AISuggestionService:
    """Service for generating AI-powered field suggestions and autofill"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_field_suggestion(
        self,
        field_label: str,
        field_type: str,
        partial_value: str = "",
        context: Dict[str, Any] = None,
        existing_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate AI suggestion for a field based on context
        
        Args:
            field_label: Label of the field (e.g., "Company Name")
            field_type: Type of field (text, email, phone, etc.)
            partial_value: What user has typed so far
            context: Additional context about the entity
            existing_data: Other fields already filled in
        
        Returns:
            {
                "suggestion": "suggested value",
                "confidence": 0.85,
                "alternatives": ["alt1", "alt2"]
            }
        """
        try:
            # Build context prompt
            prompt = self._build_suggestion_prompt(
                field_label, field_type, partial_value, context, existing_data
            )
            
            # Use OpenAI if available, fallback to Anthropic
            if self.openai_client:
                response = await self._get_openai_suggestion(prompt, field_type)
            elif self.anthropic_client:
                response = await self._get_anthropic_suggestion(prompt, field_type)
            else:
                # Fallback to pattern-based suggestions
                response = await self._get_pattern_suggestion(
                    field_label, field_type, partial_value, existing_data
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI suggestion: {e}")
            return {
                "suggestion": "",
                "confidence": 0.0,
                "alternatives": []
            }
    
    def _build_suggestion_prompt(
        self,
        field_label: str,
        field_type: str,
        partial_value: str,
        context: Dict[str, Any],
        existing_data: Dict[str, Any]
    ) -> str:
        """Build prompt for AI suggestion"""
        
        prompt = f"""You are helping a user fill out a form field in a business management system.

Field Label: {field_label}
Field Type: {field_type}
Partial Input: "{partial_value}"

"""
        
        if existing_data:
            prompt += "Other fields already filled:\n"
            for key, value in existing_data.items():
                if value:
                    prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += f"""Based on the field label, type, partial input, and context, suggest the most likely complete value.
Return only the suggested value, nothing else. If the partial input seems complete, return it as-is.
For business data, be realistic and professional."""

        return prompt
    
    async def _get_openai_suggestion(self, prompt: str, field_type: str) -> Dict[str, Any]:
        """Get suggestion from OpenAI"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cheaper model for suggestions
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests form field values based on context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3  # Lower temperature for more consistent suggestions
            )
            
            suggestion = response.choices[0].message.content.strip()
            
            # Generate alternatives
            alternatives = await self._get_alternatives(suggestion, field_type)
            
            return {
                "suggestion": suggestion,
                "confidence": 0.85,
                "alternatives": alternatives[:3]  # Top 3 alternatives
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _get_anthropic_suggestion(self, prompt: str, field_type: str) -> Dict[str, Any]:
        """Get suggestion from Anthropic Claude"""
        try:
            message = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cheap for suggestions
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            suggestion = message.content[0].text.strip()
            
            alternatives = await self._get_alternatives(suggestion, field_type)
            
            return {
                "suggestion": suggestion,
                "confidence": 0.80,
                "alternatives": alternatives[:3]
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def _get_pattern_suggestion(
        self,
        field_label: str,
        field_type: str,
        partial_value: str,
        existing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback pattern-based suggestions when AI is not available"""
        
        suggestion = partial_value
        confidence = 0.5
        
        # Pattern matching for common fields
        field_lower = field_label.lower()
        
        if field_type == "email":
            if "@" not in partial_value and existing_data.get("name"):
                # Suggest email from name
                name = existing_data.get("name", "").lower().replace(" ", ".")
                suggestion = f"{name}@example.com"
        
        elif field_type == "phone":
            # Format phone number
            digits = ''.join(filter(str.isdigit, partial_value))
            if len(digits) == 10:
                suggestion = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        elif "name" in field_lower and existing_data.get("email"):
            # Extract name from email
            email = existing_data.get("email", "")
            if "@" in email:
                name_part = email.split("@")[0].replace(".", " ").title()
                suggestion = name_part if not partial_value else partial_value
        
        return {
            "suggestion": suggestion,
            "confidence": confidence,
            "alternatives": []
        }
    
    async def _get_alternatives(self, suggestion: str, field_type: str) -> List[str]:
        """Generate alternative suggestions"""
        # Simple alternatives - can be enhanced
        alternatives = []
        
        if field_type == "email" and "@" in suggestion:
            # Suggest variations
            base = suggestion.split("@")[0]
            domain = suggestion.split("@")[1]
            alternatives = [
                f"{base}1@{domain}",
                f"{base}.alt@{domain}"
            ]
        
        return alternatives
    
    async def autofill_entity(
        self,
        entity_type: str,
        partial_data: Dict[str, Any],
        field_definitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Autofill multiple fields at once based on partial data
        
        Args:
            entity_type: Type of entity (company, customer, etc.)
            partial_data: Fields user has already filled
            field_definitions: List of field definitions
        
        Returns:
            Dictionary of field_key -> suggested_value
        """
        suggestions = {}
        
        for field_def in field_definitions:
            field_key = field_def.get("field_key")
            field_label = field_def.get("field_label")
            field_type = field_def.get("field_type")
            
            # Skip if already has value
            if field_key in partial_data and partial_data[field_key]:
                continue
            
            # Generate suggestion
            suggestion_data = await self.generate_field_suggestion(
                field_label=field_label,
                field_type=field_type,
                partial_value="",
                context={"entity_type": entity_type},
                existing_data=partial_data
            )
            
            if suggestion_data.get("suggestion"):
                suggestions[field_key] = suggestion_data
        
        return suggestions

# Global instance
ai_suggestion_service = AISuggestionService()

