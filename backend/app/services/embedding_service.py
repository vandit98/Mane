from sentence_transformers import SentenceTransformer
from typing import List

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model


class EmbeddingService:
    def __init__(self):
        self.model = get_model()
    
    def create_product_text(self, product: dict) -> str:
        parts = [
            f"Product: {product.get('title', '')}",
            f"Category: {product.get('category', 'Hair Care')}",
            f"Type: {product.get('product_type', '')}",
            f"Price: ₹{product.get('price', 0)}",
        ]
        
        if product.get('description'):
            parts.append(f"Description: {product['description'][:500]}")
        
        if product.get('features'):
            parts.append(f"Features: {product['features']}")
        
        if product.get('tags'):
            tags = product['tags'] if isinstance(product['tags'], list) else []
            if tags:
                parts.append(f"Tags: {', '.join(tags[:10])}")
        
        return " | ".join(parts)

    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()

    def generate_query_embedding(self, query: str) -> List[float]:
        embedding = self.model.encode(query)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return [e.tolist() for e in embeddings]
