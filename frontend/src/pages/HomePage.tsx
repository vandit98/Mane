import { useState, useEffect } from 'react';
import { Product } from '../types';
import { getProducts } from '../services/api';
import { ProductCard } from '../components/ProductCard';
import './HomePage.css';

export function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProducts() {
      try {
        const data = await getProducts(0, 50);
        setProducts(data.products);
      } catch {
        setError('Failed to load products. Make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    }
    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="home-loading">
        <div className="spinner"></div>
        <p>Loading products...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-error">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="home-page">
      <section className="hero">
        <h1>Your Hair, Your Way</h1>
        <p>Discover science-backed hair care solutions tailored to your needs</p>
      </section>

      <section className="products-section">
        <div className="section-header">
          <h2>All Products</h2>
          <span className="product-count">{products.length} products</span>
        </div>

        {products.length === 0 ? (
          <div className="no-products">
            <p>No products found. Run the scraper to populate the database.</p>
            <code>POST /api/scraper/run</code>
          </div>
        ) : (
          <div className="products-grid">
            {products.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
