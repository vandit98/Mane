from typing import List, Optional
import os

_model = None
_model_failed = False


def get_model():
    global _model, _model_failed
    if _model_failed:
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            _model_failed = True
            return None
    return _model


class EmbeddingService:
    def __init__(self):
        pass
    
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

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        model = get_model()
        if model is None:
            return None
        embedding = model.encode(text)
        return embedding.tolist()

    def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        model = get_model()
        if model is None:
            return None
        embedding = model.encode(query)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        model = get_model()
        if model is None:
            return []
        embeddings = model.encode(texts)
        return [e.tolist() for e in embeddings]
