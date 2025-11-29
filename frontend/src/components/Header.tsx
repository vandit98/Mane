import { Link } from 'react-router-dom';
import './Header.css';

export function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          <span className="logo-icon">✦</span>
          <span className="logo-text">Mane</span>
        </Link>
        <nav className="nav">
          <Link to="/" className="nav-link">Shop</Link>
        </nav>
      </div>
    </header>
  );
}
