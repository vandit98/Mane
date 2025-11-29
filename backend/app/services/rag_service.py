import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Tuple
from app.core.config import get_settings
from app.models.product import Product
from app.services.embedding_service import EmbeddingService

settings = get_settings()


class RAGService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.chat_model)
    
    def retrieve_by_text_search(self, query: str, top_k: int = 5) -> List[Product]:
        """Retrieve products using text search"""
        keywords = query.lower().split()
        products = self.db.query(Product).all()
        
        scored_products = []
        for product in products:
            score = 0
            searchable = f"{product.title} {product.description or ''} {product.features or ''} {' '.join(product.tags or [])}".lower()
            
            for keyword in keywords:
                if len(keyword) > 2 and keyword in searchable:
                    score += searchable.count(keyword)
            
            if score > 0:
                scored_products.append((score, product))
        
        scored_products.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_products:
            return self.db.query(Product).limit(top_k).all()
        
        return [p for _, p in scored_products[:top_k]]
    
    def retrieve_relevant_products(self, query: str, top_k: int = 5) -> List[Product]:
        """Retrieve relevant products - uses text search (memory efficient)"""
        return self.retrieve_by_text_search(query, top_k)

    def build_context(self, products: List[Product]) -> str:
        if not products:
            return "No products found in the database."
        
        context_parts = ["Here are the relevant products from our catalog:\n"]
        
        for i, product in enumerate(products, 1):
            context_parts.append(f"""
Product {i}:
- Name: {product.title}
- Price: ₹{product.price}
- Category: {product.category or 'Hair Care'}
- Description: {(product.description or '')[:300]}
- Features: {product.features or 'N/A'}
- Tags: {', '.join(product.tags[:5]) if product.tags else 'N/A'}
""")
        
        return "\n".join(context_parts)

    def generate_response(
        self, 
        query: str, 
        conversation_history: List[dict] = None
    ) -> Tuple[str, List[Product], bool]:
        """Generate a response using RAG"""
        
        relevant_products = self.retrieve_relevant_products(query, top_k=5)
        context = self.build_context(relevant_products)
        
        system_prompt = """You are a helpful shopping assistant for Mane, a hair care brand. Your role is to:

1. Help customers find the right products for their hair concerns
2. Provide personalized recommendations based on their specific needs
3. Ask clarifying questions when the query is vague
4. Explain why you're recommending specific products

Guidelines:
- Be conversational and friendly
- If the user's query is unclear, ask ONE specific clarifying question
- When recommending products, explain how they address the user's concern
- Always base recommendations on the products in the provided context
- Keep responses concise but informative

Product Context:
{context}
"""
        
        messages = []
        
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "user" if msg.get("role") == "user" else "model"
                messages.append({"role": role, "parts": [msg.get("content", "")]})
        
        messages.append({"role": "user", "parts": [query]})
        
        chat = self.model.start_chat(history=messages[:-1] if len(messages) > 1 else [])
        
        full_prompt = f"{system_prompt.format(context=context)}\n\nUser Query: {query}"
        response = chat.send_message(full_prompt)
        
        response_text = response.text
        
        needs_clarification = any(phrase in response_text.lower() for phrase in [
            "could you tell me more", "what type of", "can you specify",
            "would you like", "do you prefer", "what is your", "could you clarify"
        ])
        
        return response_text, relevant_products, needs_clarification
