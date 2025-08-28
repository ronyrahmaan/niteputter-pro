import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Footer from "../components/Footer";

const Technology = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setTimeout(() => setIsLoaded(true), 300);
  }, []);

  const features = [
    {
      title: "Patented POLY LIGHT CASING",
      description: "Advanced protection system engineered to withstand harsh environmental conditions while maintaining optimal performance.",
      details: [
        "Water-resistant sealed design",
        "Debris protection technology",
        "Easy maintenance access",
        "All-weather durability testing"
      ]
    },
    {
      title: "Multi-Level Drainage System",
      description: "Engineered drainage technology designed to handle extreme weather conditions and prevent system failures.",
      details: [
        "Mass flow optimization",
        "Heavy rain protection",
        "Flood resistance capability",
        "Long-term reliability assurance"
      ]
    },
    {
      title: "Smart Life Integration",
      description: "Bluetooth-enabled control system with comprehensive mobile app integration for complete customization.",
      details: [
        "Bluetooth 5.0 connectivity",
        "Color customization control",
        "Pattern programming",
        "Remote operation capability"
      ]
    },
    {
      title: "Professional Installation",
      description: "Veteran-engineered installation process designed for seamless integration with existing landscape systems.",
      details: [
        "12v low voltage integration",
        "Landscape system compatibility",
        "Professional setup service",
        "Ongoing technical support"
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
            <li><Link to="/technology" className="nav-link nav-active">TECHNOLOGY</Link></li>
            <li><Link to="/about" className="nav-link">ABOUT</Link></li>
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
      <section className="py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 text-sm font-light tracking-widest text-gray-400">
            <div className="mb-2">[01] Initializing Technology Systems...</div>
            <div className="mb-2 ml-8">// Loading POLY LIGHT CASING Protocols</div>
            <div className="mb-2 ml-12">&gt;&gt; Verifying Drainage Integration</div>
            <div className="mb-2 ml-12">&gt;&gt; Testing Smart Life Connectivity</div>
            <div className="mb-4">All systems operational -&gt;</div>
          </div>

          <h1 className="text-5xl md:text-8xl font-light mb-8 tracking-tight">
            TECHNOLOGY
          </h1>
          
          <p className="text-xl md:text-2xl font-light text-gray-300 mb-16 max-w-3xl leading-relaxed">
            Veteran-engineered illumination systems<br />
            with patented protection technology
          </p>
        </div>
      </section>

      {/* Core Technology Features */}
      <section className="py-32 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-6xl font-light mb-16 leading-tight text-center">
            Core<br />
            <span className="text-gray-400">Technologies</span>
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            <div className="space-y-8">
              {features.map((feature, index) => (
                <div 
                  key={index}
                  className={`border-l-2 pl-8 cursor-pointer transition-all duration-300 ${
                    activeFeature === index 
                      ? "border-white" 
                      : "border-white/20 hover:border-white/40"
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="text-xs text-gray-500">[0{index + 1}]</span>
                    <h3 className={`text-xl font-light transition-colors duration-300 ${
                      activeFeature === index ? "text-white" : "text-gray-400"
                    }`}>
                      {feature.title}
                    </h3>
                  </div>
                  
                  <p className={`font-light leading-relaxed mb-4 transition-colors duration-300 ${
                    activeFeature === index ? "text-gray-300" : "text-gray-500"
                  }`}>
                    {feature.description}
                  </p>
                  
                  {activeFeature === index && (
                    <div className="space-y-2 animate-fadeIn">
                      {feature.details.map((detail, detailIndex) => (
                        <div key={detailIndex} className="flex items-center space-x-3">
                          <div className="w-1 h-1 bg-white"></div>
                          <span className="text-sm text-gray-400 font-light">{detail}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <div className="relative">
              <img 
                src="https://niteputterpro.com/wp-content/uploads/2024/07/pic-3-1.jpg"
                alt="Technology Integration"
                className="w-full aspect-[4/3] object-cover grayscale hover:grayscale-0 transition-all duration-500"
                onError={(e) => {
                  e.target.src = "https://images.unsplash.com/photo-1660165458059-57cfb6cc87e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwzfHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85";
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Smart Life App Section */}
      <section className="py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="relative">
              <img 
                src="https://niteputterpro.com/wp-content/uploads/2025/03/IMG_2959.jpg"
                alt="Smart Life App"
                className="w-full aspect-[4/3] object-cover grayscale hover:grayscale-0 transition-all duration-500"
                onError={(e) => {
                  e.target.src = "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHw0fHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85";
                }}
              />
            </div>
            
            <div>
              <h2 className="text-4xl md:text-6xl font-light mb-8 leading-tight">
                Smart Life<br />
                <span className="text-gray-400">App Control</span>
              </h2>
              <p className="text-lg font-light text-gray-300 mb-12 leading-relaxed">
                Comprehensive mobile application for complete system control. 
                Bluetooth-enabled MR16 bulb technology with real-time customization.
              </p>
              
              <div className="space-y-8">
                <div className="border-l border-white/20 pl-8">
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="text-xs text-gray-500">[01]</span>
                    <h3 className="text-xl font-light text-white">Color Customization</h3>
                  </div>
                  <p className="text-gray-400 font-light">Full spectrum color control for perfect ambiance</p>
                </div>
                
                <div className="border-l border-white/20 pl-8">
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="text-xs text-gray-500">[02]</span>
                    <h3 className="text-xl font-light text-white">Pattern Programming</h3>
                  </div>
                  <p className="text-gray-400 font-light">Create custom lighting sequences and effects</p>
                </div>
                
                <div className="border-l border-white/20 pl-8">
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="text-xs text-gray-500">[03]</span>
                    <h3 className="text-xl font-light text-white">Remote Operation</h3>
                  </div>
                  <p className="text-gray-400 font-light">Control your system from anywhere via Bluetooth</p>
                </div>
              </div>
              
              <a 
                href="https://www.tlc-direct.co.uk/Technical/DataSheets/LEDlite_Smart/Smart_Life_Manual_en.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-12 text-sm font-light tracking-wider text-white border-b border-white/30 hover:border-white transition-colors duration-300"
              >
                download app manual
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Solution Framework */}
      <section className="py-32 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-6xl font-light mb-16 leading-tight text-center">
            Engineering<br />
            <span className="text-gray-400">Solutions</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
            <div>
              <h3 className="text-2xl font-light text-white mb-8">Industry Challenges</h3>
              <div className="space-y-6">
                <div className="border-l border-red-500/30 pl-8">
                  <h4 className="text-lg font-light text-red-400 mb-2">Lighting Failures</h4>
                  <p className="text-sm text-gray-400 font-light">Water damage, debris obstruction, connectivity issues</p>
                </div>
                <div className="border-l border-red-500/30 pl-8">
                  <h4 className="text-lg font-light text-red-400 mb-2">Poor Drainage</h4>
                  <p className="text-sm text-gray-400 font-light">System failures during heavy rain conditions</p>
                </div>
                <div className="border-l border-red-500/30 pl-8">
                  <h4 className="text-lg font-light text-red-400 mb-2">High Costs</h4>
                  <p className="text-sm text-gray-400 font-light">Expensive installation and maintenance requirements</p>
                </div>
                <div className="border-l border-red-500/30 pl-8">
                  <h4 className="text-lg font-light text-red-400 mb-2">Charging Issues</h4>
                  <p className="text-sm text-gray-400 font-light">Frequent battery replacement and system downtime</p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-2xl font-light text-white mb-8">Our Solutions</h3>
              <div className="space-y-6">
                <div className="border-l border-green-500/30 pl-8">
                  <h4 className="text-lg font-light text-green-400 mb-2">POLY LIGHT CASING</h4>
                  <p className="text-sm text-gray-400 font-light">Patented protection against water and debris</p>
                </div>
                <div className="border-l border-green-500/30 pl-8">
                  <h4 className="text-lg font-light text-green-400 mb-2">Multi-Level Drainage</h4>
                  <p className="text-sm text-gray-400 font-light">Engineered to handle extreme weather conditions</p>
                </div>
                <div className="border-l border-green-500/30 pl-8">
                  <h4 className="text-lg font-light text-green-400 mb-2">All-in-One Design</h4>
                  <p className="text-sm text-gray-400 font-light">Reduced material costs and simplified installation</p>
                </div>
                <div className="border-l border-green-500/30 pl-8">
                  <h4 className="text-lg font-light text-green-400 mb-2">Hardwired System</h4>
                  <p className="text-sm text-gray-400 font-light">12v integration with no charging requirements</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Video Demonstration */}
      <section className="py-32 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-light mb-8 leading-tight">
            See Technology<br />
            <span className="text-gray-400">In Action</span>
          </h2>
          <p className="text-lg font-light text-gray-300 mb-16 leading-relaxed max-w-2xl mx-auto">
            Comprehensive demonstration of our patented technology 
            and installation process by our veteran engineering team.
          </p>
          
          <div className="relative">
            <div className="aspect-video bg-gray-900 overflow-hidden border border-white/10">
              <iframe
                src="https://www.youtube.com/embed/gboU0jlwcrU"
                title="Nite Putter Pro Technology Demonstration"
                className="w-full h-full"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6 bg-gray-900/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-light mb-8 leading-tight">
            Experience advanced<br />
            <span className="text-gray-400">engineering</span>
          </h2>
          <p className="text-lg font-light text-gray-300 mb-12 leading-relaxed max-w-2xl mx-auto">
            Professional consultation available for custom installations. 
            Veteran-owned team ready to engineer your perfect solution.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link
              to="/products"
              className="border border-white/30 text-white px-8 py-4 text-sm font-light tracking-wider hover:bg-white hover:text-black transition-all duration-300"
            >
              VIEW PRODUCTS
            </Link>
            <Link
              to="/contact"
              className="text-sm font-light tracking-wider text-gray-400 px-8 py-4 hover:text-white transition-colors duration-300"
            >
              REQUEST CONSULTATION
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

export default Technology;