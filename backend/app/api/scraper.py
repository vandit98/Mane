from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time
from app.core.database import get_db
from app.scraper.traya_scraper import TrayaScraper
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run")
def trigger_scraper(db: Session = Depends(get_db)):
    """Trigger the scraper to fetch products from Traya.health (without embeddings)"""
    scraper = TrayaScraper()
    try:
        products = scraper.scrape_products(min_products=30)
        service = ProductService(db)
        
        created_count = 0
        for product_data in products:
            product_create = ProductCreate(**product_data)
            service.create_product(product_create)
            created_count += 1
        
        return {
            "status": "success",
            "message": f"Scraped and stored {created_count} products (embeddings pending)",
            "products_count": created_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        scraper.close()


@router.post("/generate-embeddings")
def generate_embeddings(db: Session = Depends(get_db)):
    """Generate embeddings for products that don't have them (with rate limiting)"""
    service = ProductService(db)
    count = 0
    errors = 0
    
    products = db.query(service.db.query.__self__.query(
        __import__('app.models.product', fromlist=['Product']).Product
    ).filter_by(embedding=None)).all() if False else []
    
    from app.models.product import Product
    products = db.query(Product).filter(Product.embedding == None).limit(10).all()
    
    for product in products:
        try:
            service.generate_and_store_embedding(product)
            count += 1
            time.sleep(2)  # Rate limit: 1 request per 2 seconds
        except Exception as e:
            errors += 1
            print(f"Error generating embedding for product {product.id}: {e}")
            time.sleep(5)  # Wait longer on error
    
    return {
        "status": "success", 
        "embeddings_generated": count,
        "errors": errors,
        "remaining": db.query(Product).filter(Product.embedding == None).count()
    }
