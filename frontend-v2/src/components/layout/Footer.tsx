import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Youtube, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-black border-t border-white/10 text-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16">
          {/* Company Info */}
          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-light tracking-widest text-white mb-6">
                NITEPUTTER PRO
              </h3>
              <p className="text-gray-400 font-light leading-relaxed max-w-lg">
                Veteran-owned illuminated golf technology company. Professional installations 
                and premium lighting solutions for golf courses nationwide.
              </p>
            </div>
            
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
          
          {/* Links and Contact */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            {/* Navigation */}
            <div>
              <h3 className="text-sm font-medium tracking-wider text-white mb-6 uppercase">
                Navigation
              </h3>
              <ul className="space-y-3">
                <li>
                  <Link
                    to="/shop"
                    className="text-gray-400 hover:text-white transition-colors font-light text-sm block"
                  >
                    Shop All Products
                  </Link>
                </li>
                <li>
                  <Link
                    to="/about"
                    className="text-gray-400 hover:text-white transition-colors font-light text-sm block"
                  >
                    About Us
                  </Link>
                </li>
                <li>
                  <Link
                    to="/technology"
                    className="text-gray-400 hover:text-white transition-colors font-light text-sm block"
                  >
                    Technology
                  </Link>
                </li>
                <li>
                  <Link
                    to="/contact"
                    className="text-gray-400 hover:text-white transition-colors font-light text-sm block"
                  >
                    Contact
                  </Link>
                </li>
                <li>
                  <Link
                    to="/support"
                    className="text-gray-400 hover:text-white transition-colors font-light text-sm block"
                  >
                    Support
                  </Link>
                </li>
              </ul>
            </div>
            
            {/* Contact Info */}
            <div>
              <h3 className="text-sm font-medium tracking-wider text-white mb-6 uppercase">
                Contact
              </h3>
              <div className="space-y-4 text-sm font-light">
                <div className="flex items-start space-x-3">
                  <Phone className="h-4 w-4 text-gray-400 mt-0.5" />
                  <div>
                    <div className="text-gray-400 mb-1">Phone</div>
                    <a
                      href="tel:469-642-7171"
                      className="text-white hover:text-gray-300 transition-colors block"
                    >
                      (469) 642-7171
                    </a>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <Mail className="h-4 w-4 text-gray-400 mt-0.5" />
                  <div>
                    <div className="text-gray-400 mb-1">Email</div>
                    <a
                      href="mailto:niteputterpro@gmail.com"
                      className="text-white hover:text-gray-300 transition-colors block break-words"
                    >
                      niteputterpro@gmail.com
                    </a>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <MapPin className="h-4 w-4 text-gray-400 mt-0.5" />
                  <div>
                    <div className="text-gray-400 mb-1">Address</div>
                    <div className="text-white leading-relaxed">
                      842 Faith Trail<br />
                      Heath, TX 75032
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Social Links */}
              <div className="mt-8">
                <div className="text-sm font-medium tracking-wider text-white mb-4 uppercase">
                  Follow Us
                </div>
                <div className="flex space-x-4">
                  <a
                    href="https://www.facebook.com/profile.php?id=61563079261207"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <Facebook className="h-5 w-5" />
                  </a>
                  <a
                    href="https://x.com/niteputterpro?s=21"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <Twitter className="h-5 w-5" />
                  </a>
                  <a
                    href="https://www.instagram.com/niteputterpro"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <Instagram className="h-5 w-5" />
                  </a>
                  <a
                    href="https://www.youtube.com/watch?v=gboU0jlwcrU"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <Youtube className="h-5 w-5" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Bottom Bar */}
        <div className="mt-16 pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-gray-500 font-light">
            &copy; 2025 NitePutter Pro. All rights reserved.
          </p>
          <div className="flex flex-wrap gap-6">
            <Link
              to="/privacy"
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors font-light"
            >
              Privacy Policy
            </Link>
            <Link
              to="/terms"
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors font-light"
            >
              Terms of Service
            </Link>
            <Link
              to="/sitemap"
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors font-light"
            >
              Sitemap
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;