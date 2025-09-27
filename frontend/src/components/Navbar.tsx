import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav style={{ backgroundColor: '#f8f9fa', padding: '1rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '1rem' }}>
        <Link to="/" style={{ textDecoration: 'none', color: '#007bff' }}>
          Home
        </Link>
        <Link to="/about" style={{ textDecoration: 'none', color: '#007bff' }}>
          About
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;