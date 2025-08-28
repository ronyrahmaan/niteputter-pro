// Spektral-Style JavaScript Animations and Interactions

class SpektralAnimations {
  constructor() {
    this.init();
  }

  init() {
    this.setupScrollAnimations();
    this.setupMobileMenu();
    this.setupSmoothScrolling();
    this.setupTextAnimations();
    this.setupParallax();
  }

  // Intersection Observer for scroll animations
  setupScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fadeInUp');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe all elements with animation classes
    document.querySelectorAll('.opacity-0').forEach(el => observer.observe(el));
  }

  // Mobile menu functionality
  setupMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-menu .nav-link');

    if (mobileMenuBtn && mobileMenu) {
      mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
      });

      // Close menu when clicking on links
      mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
          mobileMenu.classList.remove('active');
          document.body.style.overflow = '';
        });
      });

      // Close menu when clicking outside
      mobileMenu.addEventListener('click', (e) => {
        if (e.target === mobileMenu) {
          mobileMenu.classList.remove('active');
          document.body.style.overflow = '';
        }
      });
    }
  }

  // Smooth scrolling for navigation links
  setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  // Text animations (typewriter effect for hero)
  setupTextAnimations() {
    const heroText = document.querySelector('.hero-text');
    if (heroText) {
      this.typewriterEffect(heroText);
    }
  }

  typewriterEffect(element) {
    const text = element.textContent;
    element.textContent = '';
    element.style.opacity = '1';
    
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
      } else {
        clearInterval(timer);
      }
    }, 50);
  }

  // Subtle parallax effect
  setupParallax() {
    let ticking = false;

    const updateParallax = () => {
      const scrolled = window.pageYOffset;
      const parallaxElements = document.querySelectorAll('.parallax');
      
      parallaxElements.forEach(element => {
        const speed = 0.1;
        const yPos = -(scrolled * speed);
        element.style.transform = `translateY(${yPos}px)`;
      });
      
      ticking = false;
    };

    const requestTick = () => {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    };

    window.addEventListener('scroll', requestTick);
  }
}

// Navigation active state
class NavigationController {
  constructor() {
    this.init();
  }

  init() {
    this.updateActiveLink();
    window.addEventListener('scroll', this.throttle(this.updateActiveLink.bind(this), 100));
  }

  updateActiveLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (window.pageYOffset >= sectionTop - 200) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  }

  throttle(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Loading animation
class LoadingController {
  constructor() {
    this.init();
  }

  init() {
    window.addEventListener('load', () => {
      document.body.classList.add('loaded');
      this.animateElements();
    });
  }

  animateElements() {
    // Stagger animation for hero elements
    const heroElements = document.querySelectorAll('.hero .opacity-0');
    heroElements.forEach((element, index) => {
      setTimeout(() => {
        element.classList.add('animate-fadeInUp');
      }, index * 200);
    });
  }
}

// Card hover effects
class CardEffects {
  constructor() {
    this.init();
  }

  init() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
      card.addEventListener('mouseenter', this.onCardHover.bind(this));
      card.addEventListener('mouseleave', this.onCardLeave.bind(this));
    });
  }

  onCardHover(e) {
    const card = e.currentTarget;
    card.style.transform = 'translateY(-8px)';
  }

  onCardLeave(e) {
    const card = e.currentTarget;
    card.style.transform = 'translateY(-4px)';
  }
}

// Performance monitoring
class PerformanceMonitor {
  constructor() {
    this.init();
  }

  init() {
    // Monitor animation performance
    let lastTime = performance.now();
    const checkPerformance = (currentTime) => {
      const delta = currentTime - lastTime;
      if (delta > 16.67) { // If frame takes longer than 16.67ms (60fps)
        // Reduce animations if performance is poor
        document.body.classList.add('reduced-motion');
      }
      lastTime = currentTime;
      requestAnimationFrame(checkPerformance);
    };
    
    // Only monitor if performance API is available
    if (typeof performance !== 'undefined') {
      requestAnimationFrame(checkPerformance);
    }

    // Respect user's motion preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.body.classList.add('reduced-motion');
    }
  }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new SpektralAnimations();
  new NavigationController();
  new LoadingController();
  new CardEffects();
  new PerformanceMonitor();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SpektralAnimations,
    NavigationController,
    LoadingController,
    CardEffects,
    PerformanceMonitor
  };
}