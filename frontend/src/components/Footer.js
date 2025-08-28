import React from "react";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-black border-t border-white/10 text-white py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16">
          {/* Logo and Description */}
          <div className="space-y-8">
            <div>
              <div className="text-xl font-light tracking-widest text-white mb-6">
                NITE PUTTER PRO
              </div>
              <p className="text-gray-400 font-light leading-relaxed mb-8 max-w-lg">
                Veteran-owned illuminated golf technology company. Professional installations 
                and premium lighting solutions for golf courses nationwide.
              </p>
              <div className="flex flex-col sm:flex-row gap-6">
                <div className="text-sm font-light">
                  <div className="text-white mb-1 font-medium">VETERAN OWNED</div>
                  <div className="text-xs text-gray-500">Supporting our military community</div>
                </div>
                <div className="text-sm font-light">
                  <div className="text-white mb-1 font-medium">TEXAS BASED</div>
                  <div className="text-xs text-gray-500">Heath, TX operations</div>
                </div>
              </div>
            </div>
          </div>

          {/* Links and Contact */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            {/* Quick Links */}
            <div>
              <h3 className="text-sm font-medium tracking-wider text-white mb-6 uppercase">Navigation</h3>
              <ul className="space-y-3">
                <li><Link to="/products" className="text-gray-400 hover:text-white transition-colors font-light text-sm block">Products</Link></li>
                <li><Link to="/technology" className="text-gray-400 hover:text-white transition-colors font-light text-sm block">Technology</Link></li>
                <li><Link to="/about" className="text-gray-400 hover:text-white transition-colors font-light text-sm block">About</Link></li>
                <li><Link to="/contact" className="text-gray-400 hover:text-white transition-colors font-light text-sm block">Contact</Link></li>
                <li><Link to="/shop" className="text-gray-400 hover:text-white transition-colors font-light text-sm block">Shop</Link></li>
              </ul>
            </div>

            {/* Contact Info */}
            <div>
              <h3 className="text-sm font-medium tracking-wider text-white mb-6 uppercase">Contact</h3>
              <div className="space-y-4 text-sm font-light">
                <div>
                  <div className="text-gray-400 mb-1">Phone</div>
                  <a href="tel:469-642-7171" className="text-white hover:text-gray-300 transition-colors block">(469) 642-7171</a>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Email</div>
                  <a href="mailto:niteputterpro@gmail.com" className="text-white hover:text-gray-300 transition-colors block break-words">niteputterpro@gmail.com</a>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Address</div>
                  <div className="text-white leading-relaxed">842 Faith Trail<br />Heath, TX 75032</div>
                </div>
              </div>
              
              {/* Social Links */}
              <div className="mt-8">
                <div className="text-sm font-medium tracking-wider text-white mb-4 uppercase">Follow</div>
                <div className="flex space-x-4">
                  <a href="https://www.facebook.com/profile.php?id=61563079261207" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                    <span className="text-sm font-medium">FB</span>
                  </a>
                  <a href="https://x.com/niteputterpro?s=21" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                    <span className="text-sm font-medium">TW</span>
                  </a>
                  <a href="https://www.instagram.com/niteputterpro" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                    <span className="text-sm font-medium">IG</span>
                  </a>
                  <a href="https://www.youtube.com/watch?v=gboU0jlwcrU" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                    <span className="text-sm font-medium">YT</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-16 pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-gray-500 font-light">
            &copy; 2025 Nite Putter Pro. All rights reserved.
          </p>
          <div className="flex flex-wrap gap-6">
            <a href="#" className="text-xs text-gray-500 hover:text-gray-300 transition-colors font-light">Privacy Policy</a>
            <a href="#" className="text-xs text-gray-500 hover:text-gray-300 transition-colors font-light">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;