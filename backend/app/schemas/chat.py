from pydantic import BaseModel
from typing import Optional, List
from app.schemas.product import ProductResponse


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    message: str
    products: Optional[List[ProductResponse]] = []
    needs_clarification: bool = False

