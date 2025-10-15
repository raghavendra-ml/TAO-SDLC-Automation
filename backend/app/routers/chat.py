"""
AI Copilot Chat Router
Handles RAG-based chat queries with context awareness
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.database import get_db
from app.services.rag_chat_service import RAGChatService

router = APIRouter()
chat_service = RAGChatService()

class ChatQuery(BaseModel):
    query: str
    context_type: str  # "dashboard" or "project"
    project_id: Optional[int] = None
    phase_id: Optional[int] = None
    conversation_history: Optional[List[Dict[str, Any]]] = []

class ChatResponse(BaseModel):
    response: str
    confidence_score: int
    sources: list
    context_type: str

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    chat_query: ChatQuery,
    db: Session = Depends(get_db)
):
    """
    Process AI Copilot chat query with RAG
    
    Context-aware routing:
    - Dashboard context: Global view of all projects
    - Project context: Project-specific guidance
    """
    try:
        response = await chat_service.process_chat_query(
            query=chat_query.query,
            context_type=chat_query.context_type,
            project_id=chat_query.project_id,
            phase_id=chat_query.phase_id,
            conversation_history=chat_query.conversation_history,
            db=db
        )
        
        return ChatResponse(**response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )

@router.get("/health")
async def chat_health():
    """Check if chat service is healthy"""
    return {
        "status": "healthy",
        "service": "AI Copilot Chat",
        "rag_enabled": True,
        "vector_db": "pgvector",
        "sql_db": "postgresql"
    }
