import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../contexts/CartContext";
import ShoppingCart from "../components/ShoppingCart";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

const Products = () => {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isLoaded, setIsLoaded] = useState(false);
  const [visibleSections, setVisibleSections] = useState(new Set());
  const [isCartOpen, setIsCartOpen] = useState(false);
  const { addToCart, getCartCount } = useCart();

  useEffect(() => {
    setTimeout(() => setIsLoaded(true), 300);

    // Intersection Observer for section animations
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisibleSections(prev => new Set([...prev, entry.target.id]));
          }
        });
      },
      { threshold: 0.2 }
    );

    // Observe all sections
    document.querySelectorAll('section[id]').forEach(section => {
      observer.observe(section);
    });

    return () => observer.disconnect();
  }, []);

  // Static product data with updated structure for cart integration
  const staticProducts = [
    {
      id: "nite_putter_complete",
      name: "Nite Putter Pro Complete System",
      category: "systems",
      price: 299.00,
      image: "https://niteputterpro.com/wp-content/uploads/2024/07/image0.png",
      description: "Complete illuminated golf cup system with patented POLY LIGHT CASING technology",
      specs: ["Patented POLY LIGHT CASING", "Multi-level drainage", "Hardwired 12v system", "Professional installation"]
    },
    {
      id: "smart_bulb_system",
      name: "Smart Life Bulb System",
      category: "components",
      price: 89.00,
      image: "https://niteputterpro.com/wp-content/uploads/2024/07/PIC-1.jpg",
      description: "Bluetooth-enabled MR16 bulb with color customization capabilities",
      specs: ["Bluetooth connectivity", "Color customization", "Smart Life app control", "Easy installation"]
    },
    {
      id: "installation_service",
      name: "Professional Installation Service",
      category: "services",
      price: 150.00,
      image: "https://niteputterpro.com/wp-content/uploads/2024/07/pic-3-1.jpg",
      description: "Expert installation by our veteran-owned team with ongoing support",
      specs: ["Professional setup", "System testing", "Training included", "Ongoing support"]
    },
    {
      id: "custom_course",
      name: "Custom Course Integration",
      category: "services",
      price: 500.00,
      image: "https://images.unsplash.com/photo-1699058455528-a603ab53c041?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxuaWdodCUyMGdvbGZ8ZW58MHx8fHwxNzU1OTc0MTI1fDA&ixlib=rb-4.1.0&q=85",
      description: "Complete golf course lighting solutions for professional installations",
      specs: ["Multi-hole systems", "Landscape integration", "Control systems", "Maintenance plans"]
    }
  ];

  const categories = [
    { id: "all", name: "All Products" },
    { id: "systems", name: "Complete Systems" },
    { id: "components", name: "Components" },
    { id: "services", name: "Services" }
  ];

  const filteredProducts = selectedCategory === "all" 
    ? staticProducts 
    : staticProducts.filter(product => product.category === selectedCategory);

  return (
    <div style={{ backgroundColor: '#0a0a0a', color: '#ffffff', minHeight: '100vh' }}>
      {/* Navigation */}
      <Navbar />

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

      {/* Loading Animation */}
      <div style={{
        position: 'fixed',
        top: '140px',
        left: '2rem',
        fontSize: '0.75rem',
        color: '#888888',
        fontFamily: 'monospace',
        opacity: isLoaded ? 0 : 1,
        transition: 'opacity 2s ease',
        pointerEvents: 'none'
      }}>
        <div>[01] Loading Product Catalog...</div>
        <div style={{ marginLeft: '1rem' }}>// Verifying System Specifications</div>
        <div style={{ marginLeft: '1rem' }}>{'>> Patented POLY LIGHT CASING'}</div>
        <div style={{ marginLeft: '1rem' }}>{'>> Multi-Level Drainage Technology'}</div>
        <div style={{ marginTop: '0.5rem' }}>Catalog loaded --{'>'}</div>
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
              PRODUCTS
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
              professional illuminated golf technology<br />
              engineered for premium installations
            </div>
          </div>
        </div>
      </section>

      {/* Category Filter */}
      <section id="filter" className="section section-dark">
        <div className="container">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: '2rem', 
            flexWrap: 'wrap',
            marginBottom: '4rem',
            transform: visibleSections.has('filter') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('filter') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            {categories.map((category, index) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: selectedCategory === category.id ? 'rgba(0,255,136,0.1)' : 'transparent',
                  border: `1px solid ${selectedCategory === category.id ? '#00ff88' : 'rgba(255,255,255,0.2)'}`,
                  borderRadius: '4px',
                  color: selectedCategory === category.id ? '#00ff88' : '#cccccc',
                  fontSize: '0.875rem',
                  fontWeight: 300,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  if (selectedCategory !== category.id) {
                    e.target.style.borderColor = '#00ff88';
                    e.target.style.color = '#ffffff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedCategory !== category.id) {
                    e.target.style.borderColor = 'rgba(255,255,255,0.2)';
                    e.target.style.color = '#cccccc';
                  }
                }}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section id="products" className="section">
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
            gap: '3rem'
          }}>
            {filteredProducts.map((product, index) => (
              <div 
                key={product.id}
                style={{ 
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  transform: visibleSections.has('products') ? 'translateY(0)' : 'translateY(50px)',
                  opacity: visibleSections.has('products') ? 1 : 0,
                  transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`,
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.borderColor = 'rgba(0,255,136,0.5)';
                  e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,255,136,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ 
                  height: '250px', 
                  overflow: 'hidden',
                  position: 'relative'
                }}>
                  <img 
                    src={product.image}
                    alt={product.name}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      filter: 'grayscale(60%)',
                      transition: 'all 0.5s ease'
                    }}
                    onError={(e) => {
                      e.target.src = "https://images.unsplash.com/photo-1699058455528-a603ab53c041?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxuaWdodCUyMGdvbGZ8ZW58MHx8fHwxNzU1OTc0MTI1fDA&ixlib=rb-4.1.0&q=85";
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.filter = 'grayscale(0%) brightness(1.1)';
                      e.target.style.transform = 'scale(1.05)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.filter = 'grayscale(60%)';
                      e.target.style.transform = 'scale(1)';
                    }}
                  />
                  <div style={{
                    position: 'absolute',
                    top: '1rem',
                    right: '1rem',
                    background: 'rgba(0,0,0,0.8)',
                    padding: '0.5rem 1rem',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    color: '#00ff88'
                  }}>
                    {product.price}
                  </div>
                </div>
                
                <div style={{ padding: '2rem' }}>
                  <h3 style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: 500, 
                    marginBottom: '1rem' 
                  }}>
                    {product.name}
                  </h3>
                  
                  <p style={{ 
                    color: '#cccccc', 
                    fontWeight: 300, 
                    lineHeight: 1.6,
                    marginBottom: '1.5rem'
                  }}>
                    {product.description}
                  </p>
                  
                  <div style={{ 
                    display: 'grid', 
                    gap: '0.5rem',
                    marginBottom: '2rem'
                  }}>
                    {product.specs.map((spec, specIndex) => (
                      <div 
                        key={specIndex}
                        style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '0.5rem',
                          fontSize: '0.875rem',
                          color: '#888888'
                        }}
                      >
                        <div style={{ 
                          width: '4px', 
                          height: '4px', 
                          background: '#00ff88', 
                          borderRadius: '50%'
                        }} />
                        {spec}
                      </div>
                    ))}
                  </div>
                  
                  <button
                    onClick={() => addToCart(product)}
                    className="btn btn-accent"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      fontSize: '0.875rem',
                      fontWeight: 500,
                      letterSpacing: '0.05em'
                    }}
                  >
                    ADD TO CART - ${product.price.toFixed(2)}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Installation Guide Section */}
      <section id="installation" className="section section-dark">
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
            gap: '4rem', 
            alignItems: 'center' 
          }}>
            <div style={{
              transform: visibleSections.has('installation') ? 'translateX(0)' : 'translateX(-50px)',
              opacity: visibleSections.has('installation') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <h2 style={{ 
                fontSize: 'clamp(2rem, 5vw, 4rem)',
                fontWeight: 500,
                lineHeight: 1.1,
                letterSpacing: '-0.01em',
                marginBottom: '2rem'
              }}>
                Installation<br />
                <span style={{ color: '#cccccc' }}>Guide</span>
              </h2>
              <p style={{ 
                fontSize: '1.125rem',
                color: '#cccccc',
                fontWeight: 300,
                lineHeight: 1.6,
                marginBottom: '3rem'
              }}>
                professional installation process<br />
                engineered for reliability and performance
              </p>
              
              <div style={{ display: 'grid', gap: '2rem' }}>
                {[
                  {
                    step: '01',
                    title: 'Site Assessment',
                    desc: 'comprehensive evaluation of installation requirements'
                  },
                  {
                    step: '02', 
                    title: 'System Design',
                    desc: 'custom configuration for optimal performance'
                  },
                  {
                    step: '03',
                    title: 'Professional Installation',
                    desc: 'expert setup with veteran-owned team'
                  }
                ].map((item, index) => (
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
                    <div style={{ 
                      fontSize: '0.75rem',
                      color: '#00ff88',
                      fontWeight: 500,
                      letterSpacing: '0.1em',
                      marginBottom: '0.5rem'
                    }}>
                      STEP {item.step}
                    </div>
                    <h3 style={{ 
                      fontSize: '1.125rem', 
                      fontWeight: 500, 
                      marginBottom: '0.5rem' 
                    }}>
                      {item.title}
                    </h3>
                    <p style={{ color: '#cccccc', fontWeight: 300, fontSize: '0.875rem' }}>
                      {item.desc}
                    </p>
                  </div>
                ))}
              </div>
            </div>
            
            <div style={{
              transform: visibleSections.has('installation') ? 'translateX(0)' : 'translateX(50px)',
              opacity: visibleSections.has('installation') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.2s'
            }}>
              <img 
                src="https://niteputterpro.com/wp-content/uploads/2024/07/pic-3-1.jpg"
                alt="Professional Installation"
                style={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: '8px',
                  filter: 'grayscale(60%)',
                  transition: 'filter 0.5s ease'
                }}
                onError={(e) => {
                  e.target.src = "https://images.unsplash.com/photo-1660165458059-57cfb6cc87e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwzfHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85";
                }}
                onMouseEnter={(e) => {
                  e.target.style.filter = 'grayscale(0%)  brightness(1.1)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.filter = 'grayscale(60%)';
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section">
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '2rem'
          }}>
            Ready to<br />
            <span style={{ color: '#cccccc' }}>Transform?</span>
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
            get professional consultation<br />
            for your golf lighting needs
          </p>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            gap: '2rem', 
            flexWrap: 'wrap'
          }}>
            <Link 
              to="/contact" 
              className="btn"
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 500,
                letterSpacing: '0.05em'
              }}
            >
              GET CONSULTATION
            </Link>
            <a 
              href="tel:469-642-7171"
              className="btn btn-accent"
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 500,
                letterSpacing: '0.05em'
              }}
            >
              CALL: (469) 642-7171
            </a>
          </div>
        </div>
      </section>
      
      {/* Spacer for proper footer separation */}
      <div style={{ height: '4rem' }}></div>
      
      {/* Footer */}
      <Footer />

      {/* Shopping Cart Sidebar */}
      <ShoppingCart isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </div>
  );
};

export default Products;