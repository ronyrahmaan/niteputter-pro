import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, User, Menu, X, Search } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '@/store/auth.store';
import { useCartStore } from '@/store/cart.store';
import { cn } from '@/utils/cn';

const Header = () => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  
  const { isAuthenticated, user, logout } = useAuthStore();
  const cartItems = useCartStore(state => state.items);
  const cartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  
  const handleLogout = async () => {
    await logout();
    navigate('/');
  };
  
  const navLinks = [
    { href: '/shop', label: 'Shop' },
    { href: '/shop?category=basic', label: 'Basic' },
    { href: '/shop?category=pro', label: 'Pro' },
    { href: '/shop?category=complete', label: 'Complete Kits' },
    { href: '/about', label: 'About' },
  ];
  
  return (
    <header className="fixed top-0 left-0 right-0 bg-black/95 backdrop-blur-sm border-b border-white/10 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link
              to="/"
              className="text-xl font-light tracking-widest text-white hover:text-cyan-400 transition-colors"
            >
              NITEPUTTER PRO
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                to={link.href}
                className="text-gray-300 hover:text-white transition-colors text-sm font-medium"
              >
                {link.label}
              </Link>
            ))}
          </div>
          
          {/* Actions */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <button
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              className="text-gray-300 hover:text-white transition-colors"
            >
              <Search className="h-5 w-5" />
            </button>
            
            {/* User */}
            {isAuthenticated ? (
              <div className="relative group">
                <button className="text-gray-300 hover:text-white transition-colors flex items-center space-x-1">
                  <User className="h-5 w-5" />
                  <span className="hidden sm:inline text-sm">{user?.firstName}</span>
                </button>
                <div className="absolute right-0 mt-2 w-48 bg-gray-900 rounded-lg shadow-lg py-2 hidden group-hover:block">
                  <Link
                    to="/account"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
                  >
                    My Account
                  </Link>
                  <Link
                    to="/account/orders"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
                  >
                    Orders
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
                  >
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <Link
                to="/login"
                className="text-gray-300 hover:text-white transition-colors"
              >
                <User className="h-5 w-5" />
              </Link>
            )}
            
            {/* Cart */}
            <Link
              to="/cart"
              className="relative text-gray-300 hover:text-white transition-colors"
            >
              <ShoppingCart className="h-5 w-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-2 -right-2 h-5 w-5 bg-cyan-500 text-white text-xs rounded-full flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </Link>
            
            {/* Mobile Menu */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-gray-300 hover:text-white transition-colors"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
        
        {/* Search Bar */}
        {isSearchOpen && (
          <div className="py-4 border-t border-white/10">
            <div className="relative">
              <input
                type="text"
                placeholder="Search products..."
                className="w-full px-4 py-2 bg-gray-900 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                autoFocus
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
                <Search className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
        
        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                to={link.href}
                className="block py-2 text-gray-300 hover:text-white transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            {!isAuthenticated && (
              <>
                <Link
                  to="/login"
                  className="block py-2 text-gray-300 hover:text-white transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="block py-2 text-gray-300 hover:text-white transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Register
                </Link>
              </>
            )}
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;