"""
AI Assistant Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.core.dependencies import get_current_active_user
from app.database.models import User
from app.services.ai_service import ai_service
from app.core.logging import logger

router = APIRouter()

class ChatMessage(BaseModel):
    message: str = Field(..., description="User message to the AI assistant")
    session_id: Optional[str] = Field(None, description="Session ID for conversation history")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the AI")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    conversation_length: int

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with the AI assistant
    
    The AI can help with:
    - Document processing questions
    - Invoice and payment management
    - Customer and supplier information
    - Inventory queries
    - Business insights and reports
    """
    try:
        session_id = chat_message.session_id or f"user_{current_user.id}"
        
        result = await ai_service.chat(
            message=chat_message.message,
            session_id=session_id,
            context=chat_message.context
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            conversation_length=result["conversation_length"]
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/chat/history")
async def get_chat_history(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get conversation history for a session
    """
    try:
        session_id = session_id or f"user_{current_user.id}"
        history = ai_service.conversation_history.get(session_id, [])
        
        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/history")
async def clear_chat_history(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Clear conversation history for a session
    """
    try:
        session_id = session_id or f"user_{current_user.id}"
        
        if session_id in ai_service.conversation_history:
            del ai_service.conversation_history[session_id]
        
        return {
            "success": True,
            "message": f"Chat history cleared for session: {session_id}"
        }
    
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/sentiment")
async def analyze_sentiment(
    text: str = Body(..., description="Text to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze sentiment of text
    """
    try:
        result = await ai_service.analyze_sentiment(text)
        return {
            "success": True,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": result["sentiment"],
            "score": result["score"]
        }
    
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract/entities")
async def extract_entities(
    text: str = Body(..., description="Text to extract entities from"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Extract entities (emails, phone numbers, amounts, dates) from text
    """
    try:
        result = await ai_service.extract_entities(text)
        return {
            "success": True,
            "text": text[:200] + "..." if len(text) > 200 else text,
            "entities": result["entities"]
        }
    
    except Exception as e:
        logger.error(f"Entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

