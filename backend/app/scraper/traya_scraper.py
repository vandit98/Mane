import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential


class TrayaScraper:
    BASE_URL = "https://traya.health"
    PRODUCTS_JSON_URL = f"{BASE_URL}/products.json"
    
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=30.0
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_products_json(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Fetch products from Shopify JSON API"""
        url = f"{self.PRODUCTS_JSON_URL}?page={page}&limit={limit}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean text"""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_features(self, description: str, tags: List[str]) -> str:
        """Extract key features from description and tags"""
        features = []
        if tags:
            features.extend([tag for tag in tags if tag])
        
        keywords = ["benefit", "feature", "contains", "ingredient", "helps", "reduces", "promotes"]
        if description:
            sentences = description.split('.')
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in keywords):
                    clean_sentence = sentence.strip()
                    if clean_sentence and len(clean_sentence) > 10:
                        features.append(clean_sentence)
        
        return " | ".join(features[:10]) if features else ""

    def parse_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a single product from Shopify JSON format"""
        variants = product_data.get("variants", [])
        first_variant = variants[0] if variants else {}
        
        price = float(first_variant.get("price", 0))
        compare_price = first_variant.get("compare_at_price")
        if compare_price:
            compare_price = float(compare_price)
        
        images = product_data.get("images", [])
        image_urls = [img.get("src", "") for img in images if img.get("src")]
        main_image = image_urls[0] if image_urls else None
        
        description_html = product_data.get("body_html", "")
        description = self.clean_html(description_html)
        
        tags = product_data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        
        features = self.extract_features(description, tags)
        
        product_type = product_data.get("product_type", "")
        vendor = product_data.get("vendor", "Traya")
        
        category = product_type if product_type else "Hair Care"
        
        return {
            "external_id": str(product_data.get("id", "")),
            "title": product_data.get("title", ""),
            "price": price,
            "compare_price": compare_price,
            "description": description[:2000] if description else None,
            "features": features[:1000] if features else None,
            "image_url": main_image,
            "images": image_urls[:5],
            "category": category,
            "vendor": vendor,
            "product_type": product_type,
            "tags": tags[:20] if tags else [],
            "url": f"{self.BASE_URL}/products/{product_data.get('handle', '')}"
        }

    def scrape_products(self, min_products: int = 25) -> List[Dict[str, Any]]:
        """Scrape products from Traya.health"""
        all_products = []
        page = 1
        
        while len(all_products) < min_products:
            try:
                data = self.fetch_products_json(page=page)
                products = data.get("products", [])
                
                if not products:
                    break
                
                for product in products:
                    parsed = self.parse_product(product)
                    if parsed["title"] and parsed["price"] > 0:
                        all_products.append(parsed)
                
                page += 1
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        return all_products[:max(min_products, len(all_products))]

    def close(self):
        self.client.close()

