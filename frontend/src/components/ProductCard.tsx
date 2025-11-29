import { Link } from 'react-router-dom';
import { Product } from '../types';
import './ProductCard.css';

interface Props {
  product: Product;
  compact?: boolean;
}

export function ProductCard({ product, compact }: Props) {
  const discount = product.compare_price 
    ? Math.round((1 - product.price / product.compare_price) * 100)
    : null;

  return (
    <Link to={`/product/${product.id}`} className={`product-card ${compact ? 'compact' : ''}`}>
      <div className="product-image-wrap">
        {product.image_url ? (
          <img src={product.image_url} alt={product.title} className="product-image" />
        ) : (
          <div className="product-image-placeholder">No Image</div>
        )}
        {discount && discount > 0 && (
          <span className="discount-badge">{discount}% OFF</span>
        )}
      </div>
      <div className="product-info">
        <h3 className="product-title">{product.title}</h3>
        {product.category && <span className="product-category">{product.category}</span>}
        <div className="product-price-row">
          <span className="product-price">₹{product.price}</span>
          {product.compare_price && product.compare_price > product.price && (
            <span className="product-compare-price">₹{product.compare_price}</span>
          )}
        </div>
      </div>
    </Link>
  );
}

