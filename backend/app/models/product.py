from sqlalchemy import Column, Integer, String, Float, Text, ARRAY
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True)
    title = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    compare_price = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    images = Column(ARRAY(String), nullable=True)
    category = Column(String(200), nullable=True)
    vendor = Column(String(200), nullable=True)
    product_type = Column(String(200), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    url = Column(String(1000), nullable=True)
    embedding = Column(Vector(384), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "price": self.price,
            "compare_price": self.compare_price,
            "description": self.description,
            "features": self.features,
            "image_url": self.image_url,
            "images": self.images,
            "category": self.category,
            "vendor": self.vendor,
            "product_type": self.product_type,
            "tags": self.tags,
            "url": self.url
        }
