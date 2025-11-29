from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.rag_service import RAGService
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        rag_service = RAGService(db)
        
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in (request.conversation_history or [])
        ]
        
        response_text, products, needs_clarification = rag_service.generate_response(
            query=request.message,
            conversation_history=history
        )
        
        product_responses = [
            ProductResponse.model_validate(p) for p in products
        ]
        
        return ChatResponse(
            message=response_text,
            products=product_responses,
            needs_clarification=needs_clarification
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

