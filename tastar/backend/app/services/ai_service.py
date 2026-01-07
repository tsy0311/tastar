"""
AI Service for ML/AI operations
Ready for integration with OpenAI, Anthropic, and custom ML models
"""
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logging import logger

class AIService:
    """AI Service for handling ML/AI operations"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
    
    async def chat(self, message: str, session_id: str = "default", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Chat with AI assistant"""
        try:
            # Initialize conversation history if needed
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Add user message to history
            self.conversation_history[session_id].append({"role": "user", "content": message})
            
            # Generate response
            response = await self._generate_chat_response(message, context)
            
            # Add assistant response to history
            self.conversation_history[session_id].append({"role": "assistant", "content": response})
            
            return {
                "response": response,
                "session_id": session_id,
                "conversation_length": len(self.conversation_history[session_id])
            }
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "error": str(e)
            }
    
    async def _generate_chat_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate chat response based on message and context"""
        message_lower = message.lower()
        
        # Business-specific responses
        if any(word in message_lower for word in ["invoice", "billing", "payment"]):
            return """I can help you with invoices and payments. I can:
- Process invoice documents
- Track payment status
- Generate invoices
- Manage accounts receivable

Would you like me to help with any of these?"""
        
        elif any(word in message_lower for word in ["customer", "client", "contact"]):
            return """I can assist with customer management:
- Add new customers
- View customer information
- Track customer orders
- Manage customer relationships

What would you like to do?"""
        
        elif any(word in message_lower for word in ["order", "purchase", "po"]):
            return """I can help with purchase orders:
- Create purchase orders
- Track order status
- Manage suppliers
- Forecast demand

How can I assist you?"""
        
        elif any(word in message_lower for word in ["inventory", "stock", "material"]):
            return """I can help with inventory management:
- Check stock levels
- Set reorder points
- Track inventory movements
- Generate inventory reports

What do you need?"""
        
        elif any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return """Hello! I'm your AI Business Assistant. I can help you with:
- Document processing and OCR
- Invoice and payment management
- Customer and supplier management
- Inventory tracking
- Sales and quotations
- Financial reporting

What would you like to do today?"""
        
        elif any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
            return """I'm an AI Business Assistant for CNC Factory Operations. I can:

📄 **Document Processing:**
- Upload and process invoices, receipts, POs
- Extract data using OCR
- Classify documents automatically

💰 **Accounting:**
- Generate invoices
- Track payments
- Manage accounts receivable/payable
- Financial reporting

👥 **Customer Management:**
- Add/view customers
- Track customer orders
- Customer analytics

📦 **Inventory & Purchasing:**
- Inventory tracking
- Purchase order management
- Supplier management
- Demand forecasting

💬 **Communication:**
- Answer questions
- Provide business insights
- Generate reports

How can I help you today?"""
        
        else:
            # Generic helpful response
            return f"""I understand you're asking about: "{message}"

I'm an AI Business Assistant designed to help with CNC factory operations. I can assist with:
- Processing business documents
- Managing invoices and payments
- Tracking customers and suppliers
- Inventory management
- Sales and quotations

Could you be more specific about what you need? For example:
- "Upload an invoice"
- "Show me customer list"
- "Create a quotation"
- "Check inventory levels"

Or ask me "help" to see all my capabilities."""
    
    async def generate_text(self, prompt: str, model: str = "gpt-4") -> str:
        """Generate text using AI model"""
        # Try OpenAI if API key is available
        if self.openai_api_key and self.openai_api_key != "your-openai-api-key":
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model=model if model != "gpt-4" else "gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API error: {e}, using fallback")
        
        # Fallback to rule-based response
        logger.info(f"Generating text with {model} (fallback mode)")
        return await self._generate_chat_response(prompt)
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        # Simple rule-based sentiment analysis
        positive_words = ["good", "great", "excellent", "happy", "satisfied", "thanks", "thank you"]
        negative_words = ["bad", "terrible", "angry", "disappointed", "problem", "issue", "error"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.5 + (positive_count * 0.15), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(0.5 - (negative_count * 0.15), 0.0)
        else:
            sentiment = "neutral"
            score = 0.5
        
        logger.info(f"Analyzing sentiment: {sentiment} ({score})")
        return {"sentiment": sentiment, "score": score}
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        import re
        
        entities = {
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            "phone_numbers": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
            "amounts": re.findall(r'\$\d+\.?\d*', text),
            "dates": re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text),
        }
        
        logger.info("Extracting entities")
        return {"entities": entities}

# Global AI service instance
ai_service = AIService()






