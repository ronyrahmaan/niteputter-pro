import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Footer from "../components/Footer";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    company: "",
    subject: "",
    message: "",
    inquiryType: "general"
  });
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setTimeout(() => setIsLoaded(true), 300);
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form submitted:", formData);
    alert("Thank you for your message! We'll get back to you soon.");
    setFormData({
      name: "",
      email: "",
      phone: "",
      company: "",
      subject: "",
      message: "",
      inquiryType: "general"
    });
  };

  const contactInfo = [
    {
      title: "General Inquiries",
      icon: "📧",
      details: [
        "Phone: (469) 642-7171",
        "Email: niteputterpro@gmail.com",
        "Hours: Mon-Fri 9AM-6PM CST"
      ]
    },
    {
      title: "Bucky Thrash",
      icon: "👨‍💼",
      details: [
        "Co-Founder & CEO",
        "Email: buckythrash@gmail.com",
        "Direct business inquiries"
      ]
    },
    {
      title: "Dusty Thrash",
      icon: "🔧",
      details: [
        "Co-Founder & Operations",
        "Email: dustythrash@yahoo.com",
        "Technical & installation support"
      ]
    },
    {
      title: "Texas Headquarters",
      icon: "🏢",
      details: [
        "842 Faith Trail",
        "Heath, TX 75032",
        "United States"
      ]
    }
  ];

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
            <li><Link to="/contact" className="nav-link nav-active">CONTACT</Link></li>
            <li><Link to="/shop" className="nav-link nav-cta">SHOP</Link></li>
          </ul>
          <button className="mobile-menu-btn">☰</button>
        </div>
      </nav>

      {/* Back Button */}
      <div style={{
        position: 'fixed',
        top: '100px',
        left: '2rem',
        zIndex: 100,
        opacity: isLoaded ? 1 : 0,
        transition: 'opacity 0.5s ease'
      }}>
        <Link 
          to="/" 
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1rem',
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '4px',
            color: '#ffffff',
            textDecoration: 'none',
            fontSize: '0.875rem',
            fontWeight: 300,
            letterSpacing: '0.05em',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(0,255,136,0.1)';
            e.target.style.borderColor = '#00ff88';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'rgba(255,255,255,0.1)';
            e.target.style.borderColor = 'rgba(255,255,255,0.2)';
          }}
        >
          <span>←</span>
          <span>BACK TO HOME</span>
        </Link>
      </div>

      {/* Hero Section */}
      <section className="section" style={{ 
        paddingTop: '12rem', 
        minHeight: '70vh', 
        display: 'flex', 
        alignItems: 'center',
        position: 'relative'
      }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <div style={{ 
            opacity: isLoaded ? 1 : 0, 
            transform: `translateY(${isLoaded ? 0 : 50}px)`,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)' 
          }}>
            <h1 style={{ 
              fontSize: 'clamp(3rem, 8vw, 6rem)',
              fontWeight: 700,
              lineHeight: 0.9,
              letterSpacing: '-0.02em',
              marginBottom: '2rem'
            }}>
              CONTACT<br />
              <span style={{ 
                color: '#cccccc',
                fontSize: '0.7em'
              }}>
                US
              </span>
            </h1>
            
            <div style={{ 
              fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
              color: '#cccccc',
              fontWeight: 300,
              lineHeight: 1.5,
              marginBottom: '3rem',
              maxWidth: '600px',
              margin: '0 auto 3rem'
            }}>
              veteran-owned team<br />
              ready to transform your golf experience
            </div>
          </div>
        </div>
      </section>

      {/* Contact Form and Info Section */}
      <section className="section section-dark">
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
            gap: '4rem', 
            alignItems: 'start' 
          }}>
            {/* Contact Form */}
            <div style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '3rem'
            }}>
              <h2 style={{ 
                fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                fontWeight: 500,
                lineHeight: 1.2,
                marginBottom: '2rem'
              }}>
                Send Message
              </h2>
              
              <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="Full Name *"
                    style={{
                      padding: '1rem',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '4px',
                      color: '#ffffff',
                      fontSize: '1rem'
                    }}
                  />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="Email Address *"
                    style={{
                      padding: '1rem',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '4px',
                      color: '#ffffff',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="Phone Number"
                    style={{
                      padding: '1rem',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '4px',
                      color: '#ffffff',
                      fontSize: '1rem'
                    }}
                  />
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleChange}
                    placeholder="Company/Organization"
                    style={{
                      padding: '1rem',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '4px',
                      color: '#ffffff',
                      fontSize: '1rem'
                    }}
                  />
                </div>

                <select
                  name="inquiryType"
                  value={formData.inquiryType}
                  onChange={handleChange}
                  style={{
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '4px',
                    color: '#ffffff',
                    fontSize: '1rem'
                  }}
                >
                  <option value="general">General Inquiry</option>
                  <option value="sales">Sales & Pricing</option>
                  <option value="installation">Installation Support</option>
                  <option value="technical">Technical Support</option>
                  <option value="partnership">Partnership</option>
                </select>

                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  placeholder="Subject *"
                  style={{
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '4px',
                    color: '#ffffff',
                    fontSize: '1rem'
                  }}
                />
                
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={6}
                  placeholder="Message *"
                  style={{
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '4px',
                    color: '#ffffff',
                    fontSize: '1rem',
                    resize: 'vertical'
                  }}
                />
                
                <button
                  type="submit"
                  className="btn btn-accent"
                  style={{
                    padding: '1rem 2rem',
                    fontSize: '1rem',
                    fontWeight: 500,
                    letterSpacing: '0.05em'
                  }}
                >
                  SEND MESSAGE
                </button>
              </form>
            </div>

            {/* Contact Information */}
            <div>
              <h2 style={{ 
                fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                fontWeight: 500,
                lineHeight: 1.2,
                marginBottom: '2rem'
              }}>
                Get In<br />
                <span style={{ color: '#cccccc' }}>Touch</span>
              </h2>
              <p style={{ 
                fontSize: '1.125rem',
                color: '#cccccc',
                fontWeight: 300,
                lineHeight: 1.5,
                marginBottom: '3rem'
              }}>
                veteran-owned team ready to help<br />
                with installations and custom solutions
              </p>

              <div style={{ display: 'grid', gap: '2rem' }}>
                {contactInfo.map((info, index) => (
                  <div 
                    key={index} 
                    style={{ 
                      borderLeft: '1px solid #2a2a2a', 
                      paddingLeft: '2rem',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderLeftColor = '#00ff88';
                      e.currentTarget.style.transform = 'translateX(5px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderLeftColor = '#2a2a2a';
                      e.currentTarget.style.transform = 'translateX(0)';
                    }}
                  >
                    <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{info.icon}</div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 500, marginBottom: '0.5rem' }}>
                      {info.title}
                    </h3>
                    <div style={{ color: '#cccccc', fontSize: '0.875rem' }}>
                      {info.details.map((detail, detailIndex) => (
                        <div key={detailIndex} style={{ marginBottom: '0.25rem' }}>{detail}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Location Section */}
      <section className="section">
        <div className="container">
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '2rem',
            textAlign: 'center'
          }}>
            Heath<br />
            <span style={{ color: '#cccccc' }}>Texas</span>
          </h2>
          <p style={{ 
            fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
            color: '#cccccc',
            fontWeight: 300,
            lineHeight: 1.5,
            textAlign: 'center',
            marginBottom: '4rem',
            maxWidth: '600px',
            margin: '0 auto 4rem'
          }}>
            veteran-owned operations<br />
            842 Faith Trail, Heath, TX 75032
          </p>
          
          <div style={{ 
            maxWidth: '800px', 
            margin: '0 auto',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
            overflow: 'hidden'
          }}>
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3337.1234567890123!2d-96.4566789!3d32.8123456!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzLCsDQ4JzQ0LjQiTiA5NsKwMjcnMjQiVw!5e0!3m2!1sen!2sus!4v1234567890123!5m2!1sen!2sus"
              width="100%"
              height="400"
              style={{ border: 0 }}
              allowFullScreen=""
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="Nite Putter Pro Headquarters Location"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section section-dark">
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '2rem'
          }}>
            Ready to<br />
            <span style={{ color: '#cccccc' }}>Get Started?</span>
          </h2>
          <p style={{ 
            fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
            color: '#cccccc',
            fontWeight: 300,
            lineHeight: 1.5,
            marginBottom: '3rem',
            maxWidth: '600px',
            margin: '0 auto 3rem'
          }}>
            transform your backyard putting experience<br />
            with our veteran team
          </p>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            gap: '2rem', 
            flexWrap: 'wrap'
          }}>
            <a 
              href="tel:469-642-7171" 
              className="btn"
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 500,
                letterSpacing: '0.05em'
              }}
            >
              CALL: (469) 642-7171
            </a>
            <a 
              href="mailto:niteputterpro@gmail.com"
              className="btn btn-accent"
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 500,
                letterSpacing: '0.05em'
              }}
            >
              EMAIL US
            </a>
          </div>
        </div>
      </section>

      {/* Add CSS for form styling */}
      <style jsx>{`
        input::placeholder,
        textarea::placeholder {
          color: rgba(255,255,255,0.5);
        }
        
        input:focus,
        textarea:focus,
        select:focus {
          outline: none;
          border-color: #00ff88;
        }
        
        select option {
          background: #1a1a1a;
          color: #ffffff;
        }
      `}</style>
      
      {/* Spacer for proper footer separation */}
      <div style={{ height: '4rem' }}></div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Contact;