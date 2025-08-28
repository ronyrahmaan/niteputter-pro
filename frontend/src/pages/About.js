import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Footer from "../components/Footer";

const About = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [visibleSections, setVisibleSections] = useState(new Set());

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

  const values = [
    {
      title: "Innovation",
      description: "patented POLY LIGHT CASING technology",
      icon: "💡"
    },
    {
      title: "Quality",
      description: "premium materials and craftsmanship",
      icon: "⭐"
    },
    {
      title: "Veteran Pride",
      description: "proudly veteran-owned operation",
      icon: "🇺🇸"
    },
    {
      title: "Affordability",
      description: "cost-effective solutions",
      icon: "💰"
    }
  ];

  const milestones = [
    {
      year: "2020",
      title: "Company Founded",
      description: "veteran-owned company established with mission to revolutionize backyard putting"
    },
    {
      year: "2021",
      title: "Engineering Partnership",
      description: "collaborated with skilled engineer to develop groundbreaking prototype"
    },
    {
      year: "2022",
      title: "Patented Technology",
      description: "developed patented POLY LIGHT CASING with multi-level drainage"
    },
    {
      year: "2023",
      title: "Product Launch",
      description: "official launch of illuminated golf cups with hardwired system"
    },
    {
      year: "2024",
      title: "Smart Technology",
      description: "introduced Bluetooth-enabled MR16 bulb with Smart Life app"
    },
    {
      year: "2025",
      title: "Industry Leadership",
      description: "established as leader in cost-effective illuminated golf solutions"
    }
  ];

  const team = [
    {
      name: "Bucky Thrash",
      position: "Co-Founder & CEO",
      bio: "veteran entrepreneur revolutionizing putting experiences"
    },
    {
      name: "Dusty Thrash", 
      position: "Co-Founder & Operations",
      bio: "engineering expert focused on innovation"
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
            <li><Link to="/about" className="nav-link nav-active">ABOUT</Link></li>
            <li><Link to="/contact" className="nav-link">CONTACT</Link></li>
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
              ABOUT<br />
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
              veteran-owned innovators<br />
              transforming golf experiences
            </div>
          </div>
        </div>
      </section>

      {/* Our Story Section */}
      <section id="story" className="section section-dark">
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
            gap: '4rem', 
            alignItems: 'center' 
          }}>
            <div style={{
              transform: visibleSections.has('story') ? 'translateX(0)' : 'translateX(-50px)',
              opacity: visibleSections.has('story') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <h2 style={{ 
                fontSize: 'clamp(2rem, 5vw, 4rem)',
                fontWeight: 500,
                lineHeight: 1.1,
                letterSpacing: '-0.01em',
                marginBottom: '2rem'
              }}>
                Our<br />
                <span style={{ color: '#cccccc' }}>Story</span>
              </h2>
              <div style={{ 
                fontSize: '1.125rem',
                color: '#cccccc',
                fontWeight: 300,
                lineHeight: 1.6,
                marginBottom: '3rem'
              }}>
                <p style={{ marginBottom: '2rem' }}>
                  Founded in 2020 as a veteran-owned company dedicated to revolutionizing putting experiences. 
                  We collaborated with skilled engineers to develop groundbreaking prototype technology.
                </p>
                <p style={{ marginBottom: '2rem' }}>
                  Our mission: provide cost-effective, reliable illuminated golf cups that solve real problems—
                  lighting failures, poor drainage, high costs, and charging hassles.
                </p>
                <p>
                  Today, our patented POLY LIGHT CASING technology represents the pinnacle of illuminated 
                  golf innovation, bringing families together for unforgettable experiences.
                </p>
              </div>
              
              <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '12px', 
                    height: '12px', 
                    background: '#00ff88', 
                    borderRadius: '50%'
                  }} />
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>VETERAN OWNED</div>
                    <div style={{ fontSize: '0.75rem', color: '#888888' }}>supporting military community</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '12px', 
                    height: '12px', 
                    background: '#00ff88', 
                    borderRadius: '50%'
                  }} />
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>TEXAS BASED</div>
                    <div style={{ fontSize: '0.75rem', color: '#888888' }}>Heath operations</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div style={{
              transform: visibleSections.has('story') ? 'translateX(0)' : 'translateX(50px)',
              opacity: visibleSections.has('story') ? 1 : 0,
              transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1) 0.2s'
            }}>
              <img 
                src="https://niteputterpro.com/wp-content/uploads/2024/07/image0.png"
                alt="Nite Putter Pro System"
                style={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: '8px',
                  filter: 'grayscale(60%)',
                  transition: 'filter 0.5s ease'
                }}
                onError={(e) => {
                  e.target.src = "https://images.unsplash.com/photo-1699058455528-a603ab53c041?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxuaWdodCUyMGdvbGZ8ZW58MHx8fHwxNzU1OTc0MTI1fDA&ixlib=rb-4.1.0&q=85";
                }}
                onMouseEnter={(e) => {
                  e.target.style.filter = 'grayscale(0%)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.filter = 'grayscale(60%)';
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section id="values" className="section">
        <div className="container">
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '4rem',
            textAlign: 'center',
            transform: visibleSections.has('values') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('values') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            Our<br />
            <span style={{ color: '#cccccc' }}>Values</span>
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '3rem'
          }}>
            {values.map((value, index) => (
              <div 
                key={index}
                style={{ 
                  borderLeft: '1px solid #2a2a2a', 
                  paddingLeft: '2rem',
                  transform: visibleSections.has('values') ? 'translateY(0)' : 'translateY(30px)',
                  opacity: visibleSections.has('values') ? 1 : 0,
                  transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`,
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderLeftColor = '#00ff88';
                  e.currentTarget.style.transform = 'translateY(-5px) translateX(10px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderLeftColor = '#2a2a2a';
                  e.currentTarget.style.transform = 'translateY(0) translateX(0)';
                }}
              >
                <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>{value.icon}</div>
                <h3 style={{ 
                  fontSize: '1.25rem', 
                  fontWeight: 500, 
                  marginBottom: '0.5rem' 
                }}>
                  {value.title}
                </h3>
                <p style={{ color: '#cccccc', fontWeight: 300, fontSize: '0.875rem' }}>
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline Section */}
      <section id="timeline" className="section section-dark">
        <div className="container">
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '4rem',
            textAlign: 'center',
            transform: visibleSections.has('timeline') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('timeline') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            Our<br />
            <span style={{ color: '#cccccc' }}>Journey</span>
          </h2>
          
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'grid', gap: '3rem' }}>
              {milestones.map((milestone, index) => (
                <div 
                  key={index}
                  style={{ 
                    borderLeft: '1px solid #2a2a2a', 
                    paddingLeft: '2rem',
                    position: 'relative',
                    transform: visibleSections.has('timeline') ? 'translateX(0)' : 'translateX(-50px)',
                    opacity: visibleSections.has('timeline') ? 1 : 0,
                    transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`,
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderLeftColor = '#00ff88';
                    e.currentTarget.style.transform = 'translateX(10px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderLeftColor = '#2a2a2a';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }}
                >
                  <div style={{
                    position: 'absolute',
                    left: '-6px',
                    top: '0.5rem',
                    width: '12px',
                    height: '12px',
                    background: '#00ff88',
                    borderRadius: '50%',
                    border: '2px solid #0a0a0a'
                  }} />
                  <div style={{ 
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    color: '#00ff88',
                    marginBottom: '0.5rem'
                  }}>
                    {milestone.year}
                  </div>
                  <h3 style={{ 
                    fontSize: '1.125rem', 
                    fontWeight: 500, 
                    marginBottom: '0.5rem' 
                  }}>
                    {milestone.title}
                  </h3>
                  <p style={{ color: '#cccccc', fontWeight: 300, fontSize: '0.875rem' }}>
                    {milestone.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section id="team" className="section">
        <div className="container">
          <h2 style={{ 
            fontSize: 'clamp(2rem, 5vw, 4rem)',
            fontWeight: 500,
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
            marginBottom: '4rem',
            textAlign: 'center',
            transform: visibleSections.has('team') ? 'translateY(0)' : 'translateY(30px)',
            opacity: visibleSections.has('team') ? 1 : 0,
            transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            Our<br />
            <span style={{ color: '#cccccc' }}>Team</span>
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '3rem',
            maxWidth: '800px',
            margin: '0 auto'
          }}>
            {team.map((member, index) => (
              <div 
                key={index}
                style={{ 
                  borderLeft: '1px solid #2a2a2a', 
                  paddingLeft: '2rem',
                  transform: visibleSections.has('team') ? 'translateY(0)' : 'translateY(30px)',
                  opacity: visibleSections.has('team') ? 1 : 0,
                  transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`,
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderLeftColor = '#00ff88';
                  e.currentTarget.style.transform = 'translateY(-5px) translateX(10px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderLeftColor = '#2a2a2a';
                  e.currentTarget.style.transform = 'translateY(0) translateX(0)';
                }}
              >
                <h3 style={{ 
                  fontSize: '1.25rem', 
                  fontWeight: 500, 
                  marginBottom: '0.5rem' 
                }}>
                  {member.name}
                </h3>
                <div style={{ 
                  color: '#00ff88', 
                  fontSize: '0.875rem',
                  fontWeight: 400,
                  marginBottom: '1rem'
                }}>
                  {member.position}
                </div>
                <p style={{ color: '#cccccc', fontWeight: 300, fontSize: '0.875rem' }}>
                  {member.bio}
                </p>
              </div>
            ))}
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
            Join Our<br />
            <span style={{ color: '#cccccc' }}>Mission</span>
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
            be part of the revolution<br />
            transforming backyard experiences
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
              CONTACT US
            </Link>
            <Link 
              to="/shop" 
              className="btn btn-accent"
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 500,
                letterSpacing: '0.05em'
              }}
            >
              SHOP NOW
            </Link>
          </div>
        </div>
      </section>
      
      {/* Spacer for proper footer separation */}
      <div style={{ height: '4rem' }}></div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default About;