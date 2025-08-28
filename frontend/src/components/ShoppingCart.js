import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { Link } from 'react-router-dom';

const ShoppingCart = ({ isOpen, onClose }) => {
  const { cart, removeFromCart, updateQuantity, getCartTotal, getCartCount, clearCart } = useCart();
  const [isCheckingOut, setIsCheckingOut] = useState(false);

  const handleCheckout = async () => {
    if (cart.length === 0) return;

    setIsCheckingOut(true);
    
    try {
      // For multiple items, we'll process them one by one
      // In a more advanced setup, you might want to combine them into a single checkout
      const originUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      
      if (cart.length === 1) {
        // Single item checkout
        const item = cart[0];
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/checkout/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            package_id: item.id,
            quantity: item.quantity,
            origin_url: originUrl,
            customer_info: {}
          })
        });

        if (!response.ok) {
          throw new Error('Failed to create checkout session');
        }

        const data = await response.json();
        
        // Redirect to Stripe Checkout
        window.location.href = data.url;
      } else {
        // Multiple items - redirect to custom checkout page
        // Store cart in session storage for checkout page
        sessionStorage.setItem('checkout_cart', JSON.stringify(cart));
        window.location.href = '/checkout';
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to start checkout. Please try again.');
    } finally {
      setIsCheckingOut(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: 'min(400px, 90vw)',
      height: '100vh',
      background: 'rgba(10, 10, 10, 0.98)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRight: 'none',
      zIndex: 2000,
      transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
      transition: 'transform 0.3s ease',
      display: 'flex',
      flexDirection: 'column',
      color: '#ffffff',
      boxShadow: '-4px 0 20px rgba(0,0,0,0.5)'
    }}>
      {/* Header */}
      <div style={{
        padding: '1.5rem 2rem',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255,255,255,0.02)'
      }}>
        <h2 style={{
          fontSize: '1.25rem',
          fontWeight: 600,
          margin: 0,
          letterSpacing: '0.02em'
        }}>
          Shopping Cart ({getCartCount()})
        </h2>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '4px',
            color: '#ffffff',
            padding: '0.5rem',
            cursor: 'pointer',
            fontSize: '1.2rem',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = '#00ff88';
            e.target.style.color = '#00ff88';
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = 'rgba(255,255,255,0.2)';
            e.target.style.color = '#ffffff';
          }}
        >
          ×
        </button>
      </div>

      {/* Cart Items */}
      <div style={{
        flex: 1,
        padding: '1rem',
        overflowY: 'auto'
      }}>
        {cart.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem 1rem',
            color: '#888888'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🛒</div>
            <p>Your cart is empty</p>
            <Link
              to="/products"
              onClick={onClose}
              style={{
                display: 'inline-block',
                marginTop: '1rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(0,255,136,0.1)',
                border: '1px solid #00ff88',
                borderRadius: '4px',
                color: '#00ff88',
                textDecoration: 'none',
                fontSize: '0.875rem',
                fontWeight: 500,
                letterSpacing: '0.05em',
                transition: 'all 0.3s ease'
              }}
            >
              BROWSE PRODUCTS
            </Link>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {cart.map((item) => (
              <div
                key={item.id}
                style={{
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  padding: '1.25rem',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(0,255,136,0.3)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '1rem'
                }}>
                  <h4 style={{
                    fontSize: '1rem',
                    fontWeight: 600,
                    margin: 0,
                    lineHeight: 1.4,
                    flex: 1,
                    color: '#ffffff'
                  }}>
                    {item.name}
                  </h4>
                  <button
                    onClick={() => removeFromCart(item.id)}
                    style={{
                      background: 'rgba(255,68,68,0.1)',
                      border: '1px solid rgba(255,68,68,0.3)',
                      borderRadius: '6px',
                      color: '#ff4444',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      padding: '0.375rem 0.5rem',
                      marginLeft: '0.75rem',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255,68,68,0.2)';
                      e.target.style.borderColor = '#ff4444';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'rgba(255,68,68,0.1)';
                      e.target.style.borderColor = 'rgba(255,68,68,0.3)';
                    }}
                  >
                    ×
                  </button>
                </div>
                
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '0.75rem'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '8px',
                    padding: '0.5rem'
                  }}>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      style={{
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '6px',
                        color: '#ffffff',
                        width: '32px',
                        height: '32px',
                        cursor: 'pointer',
                        fontSize: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(255,255,255,0.2)';
                        e.target.style.borderColor = 'rgba(255,255,255,0.4)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(255,255,255,0.1)';
                        e.target.style.borderColor = 'rgba(255,255,255,0.2)';
                      }}
                    >
                      -
                    </button>
                    <span style={{
                      fontSize: '1rem',
                      fontWeight: 600,
                      minWidth: '24px',
                      textAlign: 'center',
                      color: '#ffffff'
                    }}>
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      style={{
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '6px',
                        color: '#ffffff',
                        width: '32px',
                        height: '32px',
                        cursor: 'pointer',
                        fontSize: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(255,255,255,0.2)';
                        e.target.style.borderColor = 'rgba(255,255,255,0.4)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(255,255,255,0.1)';
                        e.target.style.borderColor = 'rgba(255,255,255,0.2)';
                      }}
                    >
                      +
                    </button>
                  </div>
                  
                  <div style={{
                    fontSize: '1.125rem',
                    fontWeight: 700,
                    color: '#00ff88',
                    textAlign: 'right'
                  }}>
                    ${(item.price * item.quantity).toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {cart.length > 0 && (
        <div style={{
          padding: '1.5rem 2rem 2rem',
          borderTop: '1px solid rgba(255,255,255,0.1)',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem',
            fontSize: '1.25rem',
            fontWeight: 600,
            padding: '1rem',
            background: 'rgba(0,255,136,0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(0,255,136,0.2)'
          }}>
            <span>Total:</span>
            <span style={{ color: '#00ff88', fontSize: '1.375rem' }}>
              ${getCartTotal().toFixed(2)}
            </span>
          </div>
          
          <div style={{ display: 'grid', gap: '1rem' }}>
            <button
              onClick={handleCheckout}
              disabled={isCheckingOut}
              style={{
                width: '100%',
                padding: '1.125rem',
                background: isCheckingOut ? 'rgba(0,255,136,0.5)' : 'linear-gradient(135deg, #00ff88, #00cc6a)',
                border: 'none',
                borderRadius: '8px',
                color: isCheckingOut ? '#ffffff' : '#000000',
                fontSize: '1rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                cursor: isCheckingOut ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                textTransform: 'uppercase',
                boxShadow: isCheckingOut ? 'none' : '0 4px 12px rgba(0,255,136,0.3)'
              }}
              onMouseEnter={(e) => {
                if (!isCheckingOut) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 6px 20px rgba(0,255,136,0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isCheckingOut) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,255,136,0.3)';
                }
              }}
            >
              {isCheckingOut ? 'PROCESSING...' : 'PROCEED TO CHECKOUT'}
            </button>
            
            <button
              onClick={clearCart}
              style={{
                width: '100%',
                padding: '0.875rem',
                background: 'transparent',
                border: '1px solid rgba(255,68,68,0.3)',
                borderRadius: '8px',
                color: '#ff4444',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                textTransform: 'uppercase',
                letterSpacing: '0.02em'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(255,68,68,0.1)';
                e.target.style.borderColor = '#ff4444';
                e.target.style.color = '#ff6666';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'transparent';
                e.target.style.borderColor = 'rgba(255,68,68,0.3)';
                e.target.style.color = '#ff4444';
              }}
            >
              Clear Cart
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShoppingCart;