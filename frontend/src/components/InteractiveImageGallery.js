import React, { useState, useEffect } from 'react';

const InteractiveImageGallery = () => {
  const [activeImage, setActiveImage] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);

  const images = [
    {
      src: "https://niteputterpro.com/wp-content/uploads/2024/07/image0.png",
      fallback: "https://images.unsplash.com/photo-1699058455528-a603ab53c041?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxuaWdodCUyMGdvbGZ8ZW58MHx8fHwxNzU1OTc0MTI1fDA&ixlib=rb-4.1.0&q=85",
      title: "Nite Putter Pro System",
      description: "Complete illuminated golf cup installation"
    },
    {
      src: "https://niteputterpro.com/wp-content/uploads/2024/07/PIC-1.jpg",
      fallback: "https://images.unsplash.com/photo-1699058455559-5145f3ec80c3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHw0fHxuaWdodCUyMGdvbGZ8ZW58MHx8fHwxNzU1OTc0MTI1fDA&ixlib=rb-4.1.0&q=85",
      title: "Professional Installation",
      description: "Patented POLY LIGHT CASING technology"
    },
    {
      src: "https://niteputterpro.com/wp-content/uploads/2024/07/pic-3-1.jpg",
      fallback: "https://images.unsplash.com/photo-1660165458059-57cfb6cc87e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwzfHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85",
      title: "Advanced Technology",
      description: "Multi-level drainage system"
    },
    {
      src: "https://niteputterpro.com/wp-content/uploads/2025/03/IMG_2959.jpg",
      fallback: "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHw0fHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85",
      title: "Smart Life App",
      description: "Bluetooth-enabled control system"
    }
  ];

  useEffect(() => {
    setIsLoaded(true);
    
    // Auto-rotate images
    const interval = setInterval(() => {
      setActiveImage((prev) => (prev + 1) % images.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ position: 'relative', height: '600px', overflow: 'hidden' }}>
      {/* Main Image Display */}
      <div style={{ 
        position: 'relative', 
        width: '100%', 
        height: '100%',
        background: '#1a1a1a',
        border: '1px solid #2a2a2a'
      }}>
        {images.map((image, index) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              opacity: activeImage === index ? 1 : 0,
              transform: `translateX(${activeImage === index ? 0 : activeImage > index ? -100 : 100}px)`,
              transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
              zIndex: activeImage === index ? 2 : 1
            }}
          >
            <img
              src={image.src}
              alt={image.title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                filter: 'grayscale(60%) contrast(1.1)',
                transition: 'filter 0.5s ease'
              }}
              onError={(e) => {
                e.target.src = image.fallback;
              }}
              onMouseEnter={(e) => {
                e.target.style.filter = 'grayscale(0%) contrast(1.2) brightness(1.1)';
              }}
              onMouseLeave={(e) => {
                e.target.style.filter = 'grayscale(60%) contrast(1.1)';
              }}
            />
            
            {/* Image Overlay Info */}
            <div style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              background: 'linear-gradient(transparent, rgba(0,0,0,0.8))',
              padding: '3rem 2rem 2rem',
              color: '#ffffff',
              transform: `translateY(${activeImage === index ? 0 : 20}px)`,
              opacity: activeImage === index ? 1 : 0,
              transition: 'all 0.6s ease'
            }}>
              <h3 style={{ 
                fontSize: '1.5rem', 
                fontWeight: 500, 
                marginBottom: '0.5rem',
                color: '#00ff88'
              }}>
                {image.title}
              </h3>
              <p style={{ 
                color: '#cccccc', 
                fontWeight: 300,
                fontSize: '1rem'
              }}>
                {image.description}
              </p>
            </div>
          </div>
        ))}

        {/* Navigation Dots */}
        <div style={{
          position: 'absolute',
          bottom: '20px',
          right: '20px',
          display: 'flex',
          gap: '12px',
          zIndex: 10
        }}>
          {images.map((_, index) => (
            <button
              key={index}
              onClick={() => setActiveImage(index)}
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                border: 'none',
                background: activeImage === index ? '#00ff88' : 'rgba(255,255,255,0.3)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                transform: activeImage === index ? 'scale(1.2)' : 'scale(1)'
              }}
              onMouseEnter={(e) => {
                if (activeImage !== index) {
                  e.target.style.background = 'rgba(255,255,255,0.6)';
                }
              }}
              onMouseLeave={(e) => {
                if (activeImage !== index) {
                  e.target.style.background = 'rgba(255,255,255,0.3)';
                }
              }}
            />
          ))}
        </div>

        {/* Progress Bar */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '2px',
          background: 'rgba(255,255,255,0.1)',
          zIndex: 10
        }}>
          <div style={{
            height: '100%',
            background: 'linear-gradient(90deg, #00ff88, #ffffff)',
            width: `${((activeImage + 1) / images.length) * 100}%`,
            transition: 'width 0.8s ease'
          }} />
        </div>
      </div>

      {/* Thumbnail Strip */}
      <div style={{
        position: 'absolute',
        left: '20px',
        top: '50%',
        transform: 'translateY(-50%)',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        zIndex: 5
      }}>
        {images.map((image, index) => (
          <div
            key={index}
            onClick={() => setActiveImage(index)}
            style={{
              width: '60px',
              height: '40px',
              cursor: 'pointer',
              border: activeImage === index ? '2px solid #00ff88' : '2px solid transparent',
              borderRadius: '4px',
              overflow: 'hidden',
              transition: 'all 0.3s ease',
              transform: activeImage === index ? 'scale(1.1)' : 'scale(1)',
              opacity: activeImage === index ? 1 : 0.6
            }}
            onMouseEnter={(e) => {
              e.target.style.opacity = '1';
              e.target.style.transform = 'scale(1.05)';
            }}
            onMouseLeave={(e) => {
              e.target.style.opacity = activeImage === index ? '1' : '0.6';
              e.target.style.transform = activeImage === index ? 'scale(1.1)' : 'scale(1)';
            }}
          >
            <img
              src={image.src}
              alt={image.title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
              onError={(e) => {
                e.target.src = image.fallback;
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default InteractiveImageGallery;