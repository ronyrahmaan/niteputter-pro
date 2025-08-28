import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';

const CheckoutSuccess = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [paymentStatus, setPaymentStatus] = useState('checking');
  const [orderDetails, setOrderDetails] = useState(null);
  const { clearCart } = useCart();

  // Function to poll payment status
  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/checkout/status/${sessionId}`);
      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      const data = await response.json();
      
      if (data.payment_status === 'paid') {
        setPaymentStatus('success');
        setOrderDetails(data);
        // Clear cart after successful payment
        clearCart();
        return;
      } else if (data.status === 'expired') {
        setPaymentStatus('expired');
        return;
      }

      // If payment is still pending, continue polling
      setPaymentStatus('processing');
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setPaymentStatus('error');
    }
  };

  useEffect(() => {
    if (sessionId) {
      pollPaymentStatus(sessionId);
    } else {
      setPaymentStatus('no_session');
    }
  }, [sessionId]);

  const getStatusMessage = () => {
    switch (paymentStatus) {
      case 'checking':
        return {
          title: 'Verifying Payment...',
          message: 'Please wait while we confirm your payment.',
          icon: '⏳',
          color: '#00ff88'
        };
      case 'processing':
        return {
          title: 'Processing Payment...',
          message: 'Your payment is being processed. This may take a few moments.',
          icon: '🔄',
          color: '#00ff88'
        };
      case 'success':
        return {
          title: 'Payment Successful!',
          message: 'Thank you for your purchase. You will receive a confirmation email shortly.',
          icon: '✅',
          color: '#00ff88'
        };
      case 'expired':
        return {
          title: 'Payment Session Expired',
          message: 'Your payment session has expired. Please try again.',
          icon: '❌',
          color: '#ff4444'
        };
      case 'timeout':
        return {
          title: 'Payment Verification Timeout',
          message: 'We couldn\'t verify your payment status. Please check your email for confirmation or contact support.',
          icon: '⚠️',
          color: '#ffaa00'
        };
      case 'error':
        return {
          title: 'Payment Verification Error',
          message: 'There was an error verifying your payment. Please contact support if you were charged.',
          icon: '❌',
          color: '#ff4444'
        };
      case 'no_session':
        return {
          title: 'Invalid Payment Session',
          message: 'No valid payment session found. Please start checkout again.',
          icon: '❌',
          color: '#ff4444'
        };
      default:
        return {
          title: 'Unknown Status',
          message: 'Unknown payment status.',
          icon: '❓',
          color: '#888888'
        };
    }
  };

  const status = getStatusMessage();

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
            padding: '4rem 2rem',
            marginBottom: '2rem'
          }}>
            <div style={{
              fontSize: '4rem',
              marginBottom: '2rem'
            }}>
              {status.icon}
            </div>
            
            <h1 style={{
              fontSize: 'clamp(2rem, 5vw, 3rem)',
              fontWeight: 500,
              lineHeight: 1.2,
              marginBottom: '1rem',
              color: status.color
            }}>
              {status.title}
            </h1>
            
            <p style={{
              fontSize: '1.125rem',
              color: '#cccccc',
              fontWeight: 300,
              lineHeight: 1.6,
              marginBottom: '3rem'
            }}>
              {status.message}
            </p>

            {/* Order Details */}
            {paymentStatus === 'success' && orderDetails && (
              <div style={{
                background: 'rgba(0,255,136,0.1)',
                border: '1px solid rgba(0,255,136,0.3)',
                borderRadius: '8px',
                padding: '2rem',
                marginBottom: '3rem',
                textAlign: 'left'
              }}>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 500,
                  marginBottom: '1rem',
                  color: '#00ff88'
                }}>
                  Order Details
                </h3>
                <div style={{ display: 'grid', gap: '0.5rem', fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Order ID:</span>
                    <span style={{ fontFamily: 'monospace' }}>{sessionId}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Amount:</span>
                    <span>${(orderDetails.amount_total / 100).toFixed(2)} {orderDetails.currency.toUpperCase()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Status:</span>
                    <span style={{ color: '#00ff88', textTransform: 'capitalize' }}>
                      {orderDetails.payment_status}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              <Link
                to="/"
                className="btn"
                style={{
                  padding: '1rem 2rem',
                  fontSize: '1rem',
                  fontWeight: 500,
                  letterSpacing: '0.05em'
                }}
              >
                BACK TO HOME
              </Link>
              
              {paymentStatus === 'success' ? (
                <Link
                  to="/products"
                  className="btn btn-accent"
                  style={{
                    padding: '1rem 2rem',
                    fontSize: '1rem',
                    fontWeight: 500,
                    letterSpacing: '0.05em'
                  }}
                >
                  SHOP MORE
                </Link>
              ) : (
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
                  CONTACT SUPPORT
                </Link>
              )}
            </div>
          </div>

          {/* Additional Info */}
          {paymentStatus === 'success' && (
            <div style={{
              fontSize: '0.875rem',
              color: '#888888',
              lineHeight: 1.6
            }}>
              <p>
                A confirmation email has been sent to your email address. 
                If you have any questions about your order, please contact us at{' '}
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
          )}
        </div>
      </section>
    </div>
  );
};

export default CheckoutSuccess;