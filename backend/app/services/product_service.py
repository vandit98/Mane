from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.services.embedding_service import EmbeddingService


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_external_id(self, external_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.external_id == external_id).first()

    def search_products(self, query: str, limit: int = 20) -> List[Product]:
        search_term = f"%{query}%"
        return self.db.query(Product).filter(
            or_(
                Product.title.ilike(search_term),
                Product.description.ilike(search_term),
                Product.category.ilike(search_term)
            )
        ).limit(limit).all()

    def create_product(self, product_data: ProductCreate) -> Product:
        existing = self.get_product_by_external_id(product_data.external_id)
        if existing:
            for key, value in product_data.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        product = Product(**product_data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def generate_and_store_embedding(self, product: Product) -> Product:
        product_text = self.embedding_service.create_product_text(product.to_dict())
        embedding = self.embedding_service.generate_embedding(product_text)
        product.embedding = embedding
        self.db.commit()
        self.db.refresh(product)
        return product

    def generate_embeddings_for_all(self) -> int:
        products = self.db.query(Product).filter(Product.embedding == None).all()
        count = 0
        for product in products:
            try:
                self.generate_and_store_embedding(product)
                count += 1
            except Exception as e:
                print(f"Error generating embedding for product {product.id}: {e}")
        return count

    def get_products_count(self) -> int:
        return self.db.query(Product).count()

