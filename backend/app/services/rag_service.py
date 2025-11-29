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
    
    def retrieve_relevant_products(self, query: str, top_k: int = 5) -> List[Product]:
        """Retrieve relevant products using vector similarity search"""
        query_embedding = self.embedding_service.generate_query_embedding(query)
        
        sql = text("""
            SELECT id, title, price, compare_price, description, features, 
                   image_url, images, category, vendor, product_type, tags, url, external_id,
                   embedding <=> :embedding AS distance
            FROM products
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """)
        
        result = self.db.execute(sql, {"embedding": str(query_embedding), "limit": top_k})
        rows = result.fetchall()
        
        products = []
        for row in rows:
            product = Product(
                id=row[0], title=row[1], price=row[2], compare_price=row[3],
                description=row[4], features=row[5], image_url=row[6],
                images=row[7], category=row[8], vendor=row[9],
                product_type=row[10], tags=row[11], url=row[12], external_id=row[13]
            )
            products.append(product)
        
        return products

    def build_context(self, products: List[Product]) -> str:
        """Build context from retrieved products for the LLM"""
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
