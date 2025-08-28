import React from 'react';
import { Link } from 'react-router-dom';

const CheckoutCancel = () => {
  return (
    <div style={{ backgroundColor: '#0a0a0a', color: '#ffffff', minHeight: '100vh' }}>
      {/* Fixed Navigation */}
      <nav className="nav" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: 'rgba(10, 10, 10, 0.95)',
        backdropFilter: 'blur(10px)'
      }}>
        <div className="container nav-container">
          <Link to="/" className="nav-logo">
            NITE PUTTER PRO
          </Link>
          <ul className="nav-links">
            <li><Link to="/products" className="nav-link">PRODUCTS</Link></li>
            <li><Link to="/technology" className="nav-link">TECHNOLOGY</Link></li>
            <li><Link to="/about" className="nav-link">ABOUT</Link></li>
            <li><Link to="/contact" className="nav-link">CONTACT</Link></li>
            <li><Link to="/shop" className="nav-link nav-cta">SHOP</Link></li>
          </ul>
          <button className="mobile-menu-btn">☰</button>
        </div>
      </nav>

      {/* Main Content */}
      <section className="section" style={{ 
        paddingTop: '12rem', 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div className="container" style={{ 
          textAlign: 'center',
          maxWidth: '600px'
        }}>
          <div style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            padding: '4rem 2rem'
          }}>
            <div style={{
              fontSize: '4rem',
              marginBottom: '2rem'
            }}>
              😔
            </div>
            
            <h1 style={{
              fontSize: 'clamp(2rem, 5vw, 3rem)',
              fontWeight: 500,
              lineHeight: 1.2,
              marginBottom: '1rem',
              color: '#ffaa00'
            }}>
              Checkout Cancelled
            </h1>
            
            <p style={{
              fontSize: '1.125rem',
              color: '#cccccc',
              fontWeight: 300,
              lineHeight: 1.6,
              marginBottom: '3rem'
            }}>
              Your payment was cancelled. No charges were made to your account.
              <br />
              Your items are still in your cart if you'd like to try again.
            </p>

            {/* Action Buttons */}
            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              <Link
                to="/products"
                className="btn"
                style={{
                  padding: '1rem 2rem',
                  fontSize: '1rem',
                  fontWeight: 500,
                  letterSpacing: '0.05em'
                }}
              >
                CONTINUE SHOPPING
              </Link>
              
              <Link
                to="/contact"
                className="btn btn-accent"
                style={{
                  padding: '1rem 2rem',
                  fontSize: '1rem',
                  fontWeight: 500,
                  letterSpacing: '0.05em'
                }}
              >
                NEED HELP?
              </Link>
            </div>
          </div>

          {/* Additional Info */}
          <div style={{
            fontSize: '0.875rem',
            color: '#888888',
            lineHeight: 1.6,
            marginTop: '2rem'
          }}>
            <p>
              If you encountered any issues during checkout or have questions about our products,
              please don't hesitate to contact us at{' '}
              <a 
                href="mailto:niteputterpro@gmail.com"
                style={{ color: '#00ff88', textDecoration: 'none' }}
              >
                niteputterpro@gmail.com
              </a>
              {' '}or call{' '}
              <a 
                href="tel:469-642-7171"
                style={{ color: '#00ff88', textDecoration: 'none' }}
              >
                (469) 642-7171
              </a>.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CheckoutCancel;