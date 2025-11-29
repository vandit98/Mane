import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Product } from '../types';
import { getProduct } from '../services/api';
import './ProductPage.css';

export function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(0);

  useEffect(() => {
    async function fetchProduct() {
      if (!id) return;
      try {
        const data = await getProduct(parseInt(id));
        setProduct(data);
      } catch {
        setProduct(null);
      } finally {
        setLoading(false);
      }
    }
    fetchProduct();
  }, [id]);

  if (loading) {
    return (
      <div className="product-page-loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-not-found">
        <h2>Product not found</h2>
        <Link to="/" className="back-link">← Back to shop</Link>
      </div>
    );
  }

  const images = product.images?.length ? product.images : (product.image_url ? [product.image_url] : []);
  const discount = product.compare_price
    ? Math.round((1 - product.price / product.compare_price) * 100)
    : null;

  return (
    <div className="product-page">
      <Link to="/" className="back-link">← Back to shop</Link>

      <div className="product-detail">
        <div className="product-gallery">
          <div className="main-image">
            {images.length > 0 ? (
              <img src={images[selectedImage]} alt={product.title} />
            ) : (
              <div className="no-image">No Image</div>
            )}
          </div>
          {images.length > 1 && (
            <div className="thumbnail-row">
              {images.map((img, i) => (
                <button
                  key={i}
                  className={`thumbnail ${i === selectedImage ? 'active' : ''}`}
                  onClick={() => setSelectedImage(i)}
                >
                  <img src={img} alt="" />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="product-info">
          {product.category && <span className="product-category">{product.category}</span>}
          <h1 className="product-title">{product.title}</h1>

          <div className="price-section">
            <span className="price">₹{product.price}</span>
            {product.compare_price && product.compare_price > product.price && (
              <>
                <span className="compare-price">₹{product.compare_price}</span>
                <span className="discount">{discount}% OFF</span>
              </>
            )}
          </div>

          {product.description && (
            <div className="description">
              <h3>Description</h3>
              <p>{product.description}</p>
            </div>
          )}

          {product.features && (
            <div className="features">
              <h3>Features</h3>
              <p>{product.features}</p>
            </div>
          )}

          {product.tags && product.tags.length > 0 && (
            <div className="tags">
              {product.tags.map((tag, i) => (
                <span key={i} className="tag">{tag}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
