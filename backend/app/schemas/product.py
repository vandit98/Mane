from pydantic import BaseModel
from typing import Optional, List


class ProductBase(BaseModel):
    title: str
    price: float
    compare_price: Optional[float] = None
    description: Optional[str] = None
    features: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    category: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[List[str]] = None
    url: Optional[str] = None


class ProductCreate(ProductBase):
    external_id: str


class ProductResponse(ProductBase):
    id: int
    external_id: str

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int

