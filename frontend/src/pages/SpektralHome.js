import React, { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import AnimatedCounter from "../components/AnimatedCounter";
import InteractiveImageGallery from "../components/InteractiveImageGallery";
import AnimatedVideoBackground from "../components/AnimatedVideoBackground";
import Navbar from "../components/Navbar";

const SpektralHome = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const heroRef = useRef(null);
  const [visibleSections, setVisibleSections] = useState(new Set());

  useEffect(() => {
    setTimeout(() => setIsLoaded(true), 500);
    
    // Scroll tracking for parallax
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    
    // Mouse tracking for interactive effects
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);

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

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
      observer.disconnect();
    };
  }, []);

  const services = [
    {
      icon: "⚡",
      title: "Concept Design",
      description: "Full-spectrum illuminated golf technology from concept to reality.",
      detail: "If traditional golf lighting doesn't exist, we engineer it. If it does, we perfect it.",
      delay: 0.1
    },
    {
      icon: "🔧",
      title: "System Production", 
      description: "From prototype to installation, systems engineered for premium golf experiences.",
      detail: "Built to spec. Delivered on time.",
      delay: 0.2
    },
    {
      icon: "🎯",
      title: "Integration Support",
      description: "Professional installation and ongoing technical support for golf facilities.",
      detail: "We respond like we're part of your team—because we are.",
      delay: 0.3
    }
  ];

  const clients = [
    "GOLF COURSES",
    "ENTERTAINMENT CENTERS", 
    "RESIDENTIAL PROPERTIES",
    "HOSPITALITY VENUES",
    "RECREATION FACILITIES",
    "SPORTS COMPLEXES",
    "PRIVATE CLUBS",
    "EVENT VENUES"
  ];

  const stats = [
    { number: 100, suffix: "+", label: "INSTALLATIONS COMPLETED" },
    { number: 5, suffix: " YEARS", label: "VETERAN-OWNED EXPERIENCE" },
    { number: 24, suffix: "/7", label: "TECHNICAL SUPPORT" },
    { number: 99, suffix: "%", label: "CUSTOMER SATISFACTION" }
  ];

  return (
    <div style={{ backgroundColor: '#0a0a0a', color: '#ffffff', minHeight: '100vh', overflow: 'hidden' }}>
      {/* Navigation */}
      <Navbar />

      {/* Enhanced Hero Section with Interactive Background */}
      <section 
        id="hero" 
        ref={heroRef}
        className="section" 
        style={{ 
          paddingTop: '12rem', 
          minHeight: '100vh', 
          display: 'flex', 
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <AnimatedVideoBackground />
        
        {/* Interactive cursor follower */}
        <div style={{
          position: 'absolute',
          left: mousePosition.x - 100,
          top: mousePosition.y - 100,
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(0,255,136,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          pointerEvents: 'none',
          transition: 'all 0.1s ease',
          zIndex: 2
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 3 }}>
          <div style={{ 
            textAlign: 'center', 
            opacity: isLoaded ? 1 : 0, 
            transform: `translateY(${isLoaded ? 0 : 50}px)`,
            transition: 'all 1.5s cubic-bezier(0.4, 0, 0.2, 1)' 
          }}>
            <div style={{ 
              overflow: 'hidden',
              marginBottom: '2rem'
            }}>
              <h1 style={{ 
                fontSize: 'clamp(3rem, 8vw, 8rem)',
                fontWeight: 700,
                lineHeight: 0.9,
                letterSpacing: '-0.02em',
                transform: `translateY(${isLoaded ? 0 : 100}px)`,
                transition: 'transform 1.2s cubic-bezier(0.4, 0, 0.2, 1)',
                textShadow: '0 0 30px rgba(0,255,136,0.3)'
              }}>
                <span style={{ 
                  display: 'inline-block',
                  transform: `translateY(${isLoaded ? 0 : 100}px)`,
                  transition: 'transform 1.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s'
                }}>
                  TURN NITE TIME
                </span>
                <br />
                <span style={{ 
                  display: 'inline-block',
                  transform: `translateY(${isLoaded ? 0 : 100}px)`,
                  transition: 'transform 1.4s cubic-bezier(0.4, 0, 0.2, 1) 0.2s',
                  background: 'linear-gradient(135deg, #00ff88, #ffffff)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  INTO TEE TIME
                </span>
              </h1>
            </div>
            
            <div style={{ 
              fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
              color: '#cccccc',
              fontWeight: 300,
              lineHeight: 1.5,
              marginBottom: '3rem',
              transform: `translateY(${isLoaded ? 0 : 30}px)`,
              opacity: isLoaded ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.5s'
            }}>
              veteran-owned golf technology<br />
              and precision lighting systems
            </div>
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              gap: '1.5rem', 
              flexWrap: 'wrap',
              transform: `translateY(${isLoaded ? 0 : 30}px)`,
              opacity: isLoaded ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.7s',
              margin: '0 auto',
              maxWidth: '500px'
            }}>
              <Link to="/products" className="btn" style={{
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 10px 30px rgba(0,255,136,0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = 'none';
              }}>
                VIEW PRODUCTS
              </Link>
              <Link to="/contact" className="btn btn-accent" style={{
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px) scale(1.05)';
                e.target.style.boxShadow = '0 15px 40px rgba(0,255,136,0.4)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0) scale(1)';
                e.target.style.boxShadow = 'none';
              }}>
                GET QUOTE
              </Link>
            </div>
          </div>
        </div>

        {/* Animated scroll indicator */}
        <div style={{
          position: 'absolute',
          bottom: '2rem',
          left: '50%',
          transform: 'translateX(-50%)',
          opacity: isLoaded ? 1 : 0,
          transition: 'opacity 1s ease 1.5s',
          zIndex: 3
        }}>
          <div style={{
            width: '2px',
            height: '30px',
            background: 'linear-gradient(to bottom, #00ff88, transparent)',
            margin: '0 auto 10px',
            animation: 'pulse 2s infinite'
          }} />
          <div style={{
            color: '#888888',
            fontSize: '0.75rem',
            letterSpacing: '0.1em',
            textTransform: 'uppercase'
          }}>SCROLL</div>
        </div>
      </section>

      {/* Interactive Services Section */}
      <section id="services" className="section section-dark" style={{ position: 'relative' }}>
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '4rem', 
            alignItems: 'start' 
          }}>
            <div style={{
              transform: visibleSections.has('services') ? 'translateX(0)' : 'translateX(-50px)',
              opacity: visibleSections.has('services') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <h2 style={{ 
                fontSize: 'clamp(2rem, 5vw, 4rem)',
                fontWeight: 500,
                lineHeight: 1.1,
                letterSpacing: '-0.01em',
                marginBottom: '2rem'
              }}>
                Integrated Golf<br />
                <span style={{ color: '#cccccc' }}>Lighting Development</span>
              </h2>
              <div style={{ fontSize: '1.125rem', color: '#cccccc', fontWeight: 300, lineHeight: 1.5, marginBottom: '2rem' }}>
                <div style={{ marginBottom: '2rem' }}>
                  <strong style={{ color: '#ffffff' }}>Professional Installations</strong><br />
                  golf courses and premium facilities
                </div>
                <div style={{ marginBottom: '2rem' }}>
                  <strong style={{ color: '#ffffff' }}>Entertainment Centers</strong><br />
                  immersive experiences and
                </div>
                <div style={{ marginBottom: '2rem' }}>
                  <strong style={{ color: '#ffffff' }}>Residential Properties</strong><br />
                  premium backyard putting and
                </div>
                <div>
                  <strong style={{ color: '#ffffff' }}>Custom Solutions</strong><br />
                  engineered for your vision
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gap: '3rem' }}>
              {services.map((service, index) => (
                <div 
                  key={index} 
                  style={{ 
                    borderLeft: '1px solid #2a2a2a', 
                    paddingLeft: '2rem', 
                    background: 'transparent',
                    transform: visibleSections.has('services') ? 'translateY(0)' : 'translateY(30px)',
                    opacity: visibleSections.has('services') ? 1 : 0,
                    transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${service.delay}s`,
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-5px) translateX(10px)';
                    e.currentTarget.style.borderLeftColor = '#00ff88';
                    e.currentTarget.style.background = 'rgba(0,255,136,0.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0) translateX(0)';
                    e.currentTarget.style.borderLeftColor = '#2a2a2a';
                    e.currentTarget.style.background = 'transparent';
                  }}
                >
                  <div style={{ 
                    fontSize: '2rem', 
                    marginBottom: '1rem',
                    transition: 'transform 0.3s ease'
                  }}>
                    {service.icon}
                  </div>
                  <h3 style={{ 
                    fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                    fontWeight: 500,
                    lineHeight: 1.2,
                    marginBottom: '1rem'
                  }}>
                    {service.title}
                  </h3>
                  <p style={{ color: '#cccccc', fontWeight: 300, marginBottom: '1rem', lineHeight: 1.6 }}>
                    {service.description}
                  </p>
                  <p style={{ fontSize: '0.875rem', color: '#888888', fontStyle: 'italic', fontWeight: 300 }}>
                    {service.detail}
                  </p>
                </div>
              ))}
              <Link to="/technology" style={{ 
                fontSize: '0.875rem',
                color: '#ffffff',
                fontWeight: 300,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                textDecoration: 'underline',
                transform: visibleSections.has('services') ? 'translateY(0)' : 'translateY(20px)',
                opacity: visibleSections.has('services') ? 1 : 0,
                transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.4s'
              }}>
                more
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Image Gallery Section */}
      <section id="gallery" className="section" style={{ position: 'relative' }}>
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '4rem', 
            alignItems: 'center' 
          }}>
            <div style={{
              transform: visibleSections.has('gallery') ? 'translateX(0)' : 'translateX(-50px)',
              opacity: visibleSections.has('gallery') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <h2 style={{ 
                fontSize: 'clamp(2rem, 5vw, 4rem)',
                fontWeight: 500,
                lineHeight: 1.1,
                letterSpacing: '-0.01em',
                marginBottom: '2rem'
              }}>
                Our Work<br />
                <span style={{ color: '#cccccc' }}>In Pictures</span>
              </h2>
              <p style={{ 
                fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
                color: '#cccccc',
                fontWeight: 300,
                lineHeight: 1.5,
                marginBottom: '2rem'
              }}>
                Professional installations featuring our patented POLY LIGHT CASING technology 
                and advanced multi-level drainage systems.
              </p>
              <div style={{ display: 'grid', gap: '1rem', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#00ff88', 
                    borderRadius: '50%'
                  }} />
                  <span style={{ color: '#cccccc', fontSize: '0.875rem' }}>Patented POLY LIGHT CASING</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#00ff88', 
                    borderRadius: '50%'
                  }} />
                  <span style={{ color: '#cccccc', fontSize: '0.875rem' }}>Multi-level drainage technology</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#00ff88', 
                    borderRadius: '50%'
                  }} />
                  <span style={{ color: '#cccccc', fontSize: '0.875rem' }}>Smart Life app integration</span>
                </div>
              </div>
            </div>
            
            <div style={{
              transform: visibleSections.has('gallery') ? 'translateX(0)' : 'translateX(50px)',
              opacity: visibleSections.has('gallery') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.2s'
            }}>
              <InteractiveImageGallery />
            </div>
          </div>
        </div>
      </section>

      {/* Video Demo Section with Enhanced Interactivity */}
      <section id="demo" className="section section-dark">
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '4rem', 
            alignItems: 'center' 
          }}>
            <div style={{
              transform: visibleSections.has('demo') ? 'translateX(0)' : 'translateX(-50px)',
              opacity: visibleSections.has('demo') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <h2 style={{ 
                fontSize: 'clamp(2rem, 5vw, 4rem)',
                fontWeight: 500,
                lineHeight: 1.1,
                letterSpacing: '-0.01em',
                marginBottom: '2rem'
              }}>
                Veteran-Owned<br />
                <span style={{ color: '#cccccc' }}>& Dedicated</span>
              </h2>
              <p style={{ 
                fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
                color: '#cccccc',
                fontWeight: 300,
                lineHeight: 1.5,
                marginBottom: '4rem'
              }}>
                Professional installation and engineering support from our Texas-based veteran team. 
                Hardwired systems with patented POLY LIGHT CASING technology.
              </p>
              <div style={{ display: 'grid', gap: '2rem', marginBottom: '3rem' }}>
                {[
                  {
                    title: 'Quick to Start',
                    desc: 'Delays burn time and budget. We move from planning to execution without stall.',
                    note: 'Downtime is engineered out of the equation.'
                  },
                  {
                    title: 'Clear, Fair Pricing',
                    desc: 'High performance at transparent cost. Veteran-owned integrity in every quote.',
                    note: 'No hidden variables.'
                  },
                  {
                    title: 'Professional Integration',
                    desc: 'Industry-proven workflows for seamless golf course integration.',
                    note: 'Zero cleanup.'
                  }
                ].map((item, index) => (
                  <div 
                    key={index}
                    style={{ 
                      borderLeft: '1px solid #2a2a2a', 
                      paddingLeft: '2rem',
                      transform: visibleSections.has('demo') ? 'translateY(0)' : 'translateY(20px)',
                      opacity: visibleSections.has('demo') ? 1 : 0,
                      transition: `all 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1 + 0.3}s`,
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderLeftColor = '#00ff88';
                      e.currentTarget.style.transform = 'translateY(-2px) translateX(5px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderLeftColor = '#2a2a2a';
                      e.currentTarget.style.transform = 'translateY(0) translateX(0)';
                    }}
                  >
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 500, marginBottom: '0.5rem', color: '#ffffff' }}>
                      {item.title}
                    </h3>
                    <p style={{ color: '#cccccc', fontWeight: 300, fontSize: '1rem', lineHeight: 1.5 }}>
                      {item.desc}<br />
                      <span style={{ fontSize: '0.875rem', color: '#888888', fontStyle: 'italic' }}>
                        {item.note}
                      </span>
                    </p>
                  </div>
                ))}
              </div>
              <a 
                href="tel:469-642-7171" 
                style={{ 
                  fontSize: '0.875rem',
                  color: '#ffffff',
                  fontWeight: 300,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  textDecoration: 'underline',
                  transform: visibleSections.has('demo') ? 'translateY(0)' : 'translateY(20px)',
                  opacity: visibleSections.has('demo') ? 1 : 0,
                  transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.6s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.color = '#00ff88';
                  e.target.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.color = '#ffffff';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                contact us
              </a>
            </div>
            
            <div style={{ 
              position: 'relative',
              transform: visibleSections.has('demo') ? 'translateX(0)' : 'translateX(50px)',
              opacity: visibleSections.has('demo') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.3s'
            }}>
              <div style={{ 
                aspectRatio: '16/9', 
                backgroundColor: '#1a1a1a', 
                border: '1px solid #2a2a2a', 
                overflow: 'hidden',
                borderRadius: '8px',
                position: 'relative',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.02)';
                e.currentTarget.style.borderColor = '#00ff88';
                e.currentTarget.style.boxShadow = '0 20px 60px rgba(0,255,136,0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.borderColor = '#2a2a2a';
                e.currentTarget.style.boxShadow = 'none';
              }}>
                <iframe
                  src="https://www.youtube.com/embed/gboU0jlwcrU"
                  title="Nite Putter Pro Technology"
                  style={{ width: '100%', height: '100%', border: 'none' }}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
                
                {/* Video overlay info */}
                <div style={{
                  position: 'absolute',
                  top: '10px',
                  left: '10px',
                  background: 'rgba(0,0,0,0.8)',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  color: '#00ff88',
                  fontWeight: 500,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase'
                }}>
                  LIVE DEMO
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Animated Stats Section */}
      <section id="stats" className="section">
        <div className="container">
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '4rem',
            textAlign: 'center',
            transform: visibleSections.has('stats') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('stats') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            By the<br />
            <span style={{ color: '#cccccc' }}>Numbers</span>
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '2rem',
            textAlign: 'center',
            alignItems: 'start',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            {stats.map((stat, index) => (
              <div 
                key={index}
                style={{
                  transform: visibleSections.has('stats') ? 'translateY(0)' : 'translateY(50px)',
                  opacity: visibleSections.has('stats') ? 1 : 0,
                  transition: `all 1s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1 + 0.2}s`,
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px) scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0) scale(1)';
                }}
              >
                <AnimatedCounter 
                  end={stat.number} 
                  suffix={stat.suffix}
                  duration={2000 + index * 200}
                />
                <div style={{ 
                  fontSize: '0.8rem',
                  color: '#999999',
                  fontWeight: 400,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  marginTop: '1rem',
                  lineHeight: 1.4,
                  minHeight: '40px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced Client Showcase */}
      <section id="clients" className="section section-dark">
        <div className="container">
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '3rem',
            textAlign: 'center',
            transform: visibleSections.has('clients') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('clients') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            select installations we've<br />
            <span style={{ color: '#cccccc' }}>completed</span>
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '2rem',
            textAlign: 'center',
            marginBottom: '4rem'
          }}>
            {clients.map((client, index) => (
              <div 
                key={index} 
                style={{ 
                  padding: '2rem 1rem',
                  transform: visibleSections.has('clients') ? 'translateY(0)' : 'translateY(30px)',
                  opacity: visibleSections.has('clients') ? 1 : 0,
                  transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.05}s`,
                  cursor: 'pointer',
                  borderRadius: '8px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(0,255,136,0.05)';
                  e.currentTarget.style.transform = 'translateY(-5px) scale(1.02)';
                  e.currentTarget.querySelector('div').style.color = '#00ff88';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.transform = 'translateY(0) scale(1)';
                  e.currentTarget.querySelector('div').style.color = '#888888';
                }}
              >
                <div style={{ 
                  fontSize: '0.75rem', 
                  fontWeight: 300, 
                  letterSpacing: '0.1em', 
                  textTransform: 'uppercase',
                  color: '#888888',
                  transition: 'color 0.3s ease',
                  cursor: 'default'
                }}>
                  {client}
                </div>
              </div>
            ))}
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <div style={{
              display: 'inline-block',
              transform: visibleSections.has('clients') ? 'scale(1)' : 'scale(0.9)',
              opacity: visibleSections.has('clients') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.5s'
            }}>
              <img 
                src="https://niteputterpro.com/wp-content/uploads/2024/07/pic-3-1.jpg"
                alt="Professional Installation"
                style={{ 
                  maxWidth: '800px', 
                  width: '100%', 
                  height: 'auto', 
                  filter: 'grayscale(100%)', 
                  transition: 'all 0.5s ease',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.target.style.filter = 'grayscale(0%) brightness(1.1)';
                  e.target.style.transform = 'scale(1.02)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.filter = 'grayscale(100%)';
                  e.target.style.transform = 'scale(1)';
                }}
                onError={(e) => {
                  e.target.src = "https://images.unsplash.com/photo-1660165458059-57cfb6cc87e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwzfHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85";
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Contact/CTA Section */}
      <section id="contact" className="section">
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '4rem',
            transform: visibleSections.has('contact') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('contact') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            Ready to transform<br />
            <span style={{ color: '#cccccc' }}>your golf experience?</span>
          </h2>
          <p style={{ 
            fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
            color: '#cccccc',
            fontWeight: 300,
            lineHeight: 1.5,
            maxWidth: '600px', 
            margin: '0 auto 3rem',
            transform: visibleSections.has('contact') ? 'translateY(0)' : 'translateY(20px)',
            opacity: visibleSections.has('contact') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.2s'
          }}>
            Professional consultation and installation services available nationwide. 
            Veteran-owned team based in Heath, Texas.
          </p>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'stretch', 
            gap: '1.5rem', 
            flexWrap: 'wrap',
            marginTop: '3rem',
            transform: visibleSections.has('contact') ? 'translateY(0)' : 'translateY(20px)',
            opacity: visibleSections.has('contact') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.4s',
            '@media (max-width: 768px)': {
              flexDirection: 'column',
              alignItems: 'center'
            }
          }}>
            <a 
              href="tel:469-642-7171" 
              className="btn"
              style={{ 
                position: 'relative',
                padding: '1rem 2rem',
                minWidth: '220px',
                textAlign: 'center',
                marginBottom: '1rem'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-3px) scale(1.05)';
                e.target.style.boxShadow = '0 15px 40px rgba(255,255,255,0.2)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0) scale(1)';
                e.target.style.boxShadow = 'none';
              }}
            >
              CALL: (469) 642-7171
            </a>
            <Link 
              to="/contact" 
              className="btn btn-accent"
              style={{
                padding: '1rem 2rem',
                minWidth: '220px',
                textAlign: 'center',
                marginBottom: '1rem'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-3px) scale(1.05)';
                e.target.style.boxShadow = '0 15px 40px rgba(0,255,136,0.4)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0) scale(1)';
                e.target.style.boxShadow = 'none';
              }}
            >
              GET DETAILED QUOTE
            </Link>
          </div>
        </div>
      </section>

      {/* Spacer section for proper footer separation */}
      <div style={{ height: '6rem' }}></div>

      {/* Enhanced Footer */}
      <footer style={{ backgroundColor: '#1a1a1a', borderTop: '1px solid #2a2a2a', padding: '6rem 0 4rem' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '3rem', marginBottom: '3rem' }}>
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '0.1em', marginBottom: '2rem', marginTop: '1rem' }}>
                NITE PUTTER PRO
              </div>
              <p style={{ color: '#cccccc', fontWeight: 300, lineHeight: 1.6, marginBottom: '2rem', maxWidth: '300px' }}>
                Veteran-owned illuminated golf technology company. Professional installations 
                and premium lighting systems nationwide.
              </p>
              <div style={{ display: 'flex', gap: '2rem', fontSize: '0.875rem' }}>
                <div>
                  <div style={{ color: '#ffffff', marginBottom: '0.25rem' }}>VETERAN OWNED</div>
                  <div style={{ fontSize: '0.75rem', color: '#888888' }}>Supporting our military community</div>
                </div>
                <div>
                  <div style={{ color: '#ffffff', marginBottom: '0.25rem' }}>TEXAS BASED</div>
                  <div style={{ fontSize: '0.75rem', color: '#888888' }}>Heath, TX operations</div>
                </div>
              </div>
            </div>

            <div>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 300, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#ffffff', marginBottom: '1.5rem' }}>Navigation</h3>
              <div style={{ display: 'grid', gap: '0.75rem' }}>
                <Link to="/products" className="nav-link">Products</Link>
                <Link to="/technology" className="nav-link">Technology</Link>
                <Link to="/about" className="nav-link">About</Link>
                <Link to="/contact" className="nav-link">Contact</Link>
                <Link to="/shop" className="nav-link">Shop</Link>
              </div>
            </div>

            <div>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 300, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#ffffff', marginBottom: '1.5rem' }}>Contact</h3>
              <div style={{ display: 'grid', gap: '0.75rem', fontSize: '0.875rem', fontWeight: 300 }}>
                <div>
                  <div style={{ color: '#cccccc' }}>Phone</div>
                  <a href="tel:469-642-7171" style={{ color: '#ffffff', textDecoration: 'none' }}>(469) 642-7171</a>
                </div>
                <div>
                  <div style={{ color: '#cccccc' }}>Email</div>
                  <a href="mailto:niteputterpro@gmail.com" style={{ color: '#ffffff', textDecoration: 'none' }}>niteputterpro@gmail.com</a>
                </div>
                <div>
                  <div style={{ color: '#cccccc' }}>Address</div>
                  <div style={{ color: '#ffffff' }}>842 Faith Trail<br />Heath, TX 75032</div>
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ borderTop: '1px solid #2a2a2a', paddingTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <p style={{ fontSize: '0.75rem', color: '#888888', fontWeight: 300 }}>
              © 2025 Nite Putter Pro. All rights reserved.
            </p>
            <div style={{ display: 'flex', gap: '1.5rem' }}>
              <a href="#" style={{ fontSize: '0.75rem', color: '#888888', textDecoration: 'none', fontWeight: 300 }}>Privacy Policy</a>
              <a href="#" style={{ fontSize: '0.75rem', color: '#888888', textDecoration: 'none', fontWeight: 300 }}>Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Add CSS animations */}
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        .btn {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .nav-link {
          transition: all 0.3s ease;
        }
        
        .nav-link:hover {
          color: #00ff88;
          transform: translateY(-1px);
        }
      `}</style>
    </div>
  );
};

export default SpektralHome;