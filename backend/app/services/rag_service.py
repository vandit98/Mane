import google.generativeai as genai
from sqlalchemy.orm import Session
from typing import List, Tuple
from app.core.config import get_settings
from app.models.product import Product

settings = get_settings()


class RAGService:
    def __init__(self, db: Session):
        self.db = db
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.chat_model)
    
    def retrieve_by_text_search(self, query: str, top_k: int = 5) -> List[Product]:
        """Retrieve products using improved text search"""
        query_lower = query.lower()
        
        keywords = [w for w in query_lower.split() if len(w) > 2]
        
        hair_keywords = {
            'dry': ['dry', 'moisture', 'hydrat', 'nourish', 'oil'],
            'scalp': ['scalp', 'oil', 'health', 'sooth'],
            'hair fall': ['fall', 'loss', 'minoxidil', 'growth', 'serum'],
            'hairfall': ['fall', 'loss', 'minoxidil', 'growth', 'serum'],
            'dandruff': ['dandruff', 'flak', 'itch', 'anti-dandruff'],
            'density': ['density', 'thick', 'volume', 'growth', 'biotin'],
            'thin': ['thin', 'volume', 'density', 'thick'],
            'oily': ['oily', 'oil control', 'shampoo'],
            'frizz': ['frizz', 'smooth', 'serum', 'conditioner'],
            'growth': ['growth', 'minoxidil', 'serum', 'biotin'],
        }
        
        expanded_keywords = set(keywords)
        for key, expansions in hair_keywords.items():
            if key in query_lower:
                expanded_keywords.update(expansions)
        
        products = self.db.query(Product).all()
        scored_products = []
        
        for product in products:
            score = 0
            title_lower = product.title.lower()
            desc_lower = (product.description or '').lower()
            features_lower = (product.features or '').lower()
            tags_text = ' '.join(product.tags or []).lower()
            
            all_text = f"{title_lower} {desc_lower} {features_lower} {tags_text}"
            
            for keyword in expanded_keywords:
                if keyword in title_lower:
                    score += 10
                if keyword in desc_lower:
                    score += 3
                if keyword in features_lower:
                    score += 2
                if keyword in tags_text:
                    score += 2
            
            if score > 0:
                scored_products.append((score, product))
        
        scored_products.sort(key=lambda x: x[0], reverse=True)
        
        if len(scored_products) < top_k:
            existing_ids = {p.id for _, p in scored_products}
            for product in products:
                if product.id not in existing_ids:
                    scored_products.append((0, product))
                if len(scored_products) >= top_k:
                    break
        
        return [p for _, p in scored_products[:top_k]]
    
    def retrieve_relevant_products(self, query: str, top_k: int = 5) -> List[Product]:
        return self.retrieve_by_text_search(query, top_k)

    def build_context(self, products: List[Product]) -> str:
        if not products:
            return "No products found."
        
        context_parts = ["Available products:\n"]
        
        for i, product in enumerate(products, 1):
            context_parts.append(f"""
Product {i}: {product.title}
- Price: ₹{product.price}
- Category: {product.category or 'Hair Care'}
- Description: {(product.description or '')[:250]}
- Key Benefits: {(product.features or '')[:150]}
""")
        
        return "\n".join(context_parts)

    def generate_response(
        self, 
        query: str, 
        conversation_history: List[dict] = None
    ) -> Tuple[str, List[Product], bool]:
        
        relevant_products = self.retrieve_relevant_products(query, top_k=5)
        context = self.build_context(relevant_products)
        
        system_prompt = """You are Mane's shopping assistant for hair care products.

IMPORTANT RULES:
1. ONLY recommend products from the list below - do not mention products not in the list
2. When recommending, use the EXACT product names from the list
3. Be helpful and explain why each product helps with the user's concern
4. If unsure what the user needs, ask ONE clarifying question
5. Keep responses concise (2-3 sentences per recommendation)

{context}

Based on the user's query, recommend the most relevant products from the list above."""

        messages = []
        if conversation_history:
            for msg in conversation_history[-4:]:
                role = "user" if msg.get("role") == "user" else "model"
                messages.append({"role": role, "parts": [msg.get("content", "")]})
        
        chat = self.model.start_chat(history=messages if messages else [])
        
        full_prompt = f"{system_prompt.format(context=context)}\n\nUser: {query}"
        response = chat.send_message(full_prompt)
        
        needs_clarification = any(phrase in response.text.lower() for phrase in [
            "could you", "what type", "can you specify", "would you like",
            "do you prefer", "what is your", "tell me more", "?"
        ])
        
        return response.text, relevant_products, needs_clarification
