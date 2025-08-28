import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useCart } from "../contexts/CartContext";
import ShoppingCart from "./ShoppingCart";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const { getCartCount } = useCart();

  const navItems = [
    { name: "PRODUCTS", path: "/products" },
    { name: "TECHNOLOGY", path: "/technology" },
    { name: "ABOUT", path: "/about" },
    { name: "CONTACT", path: "/contact" },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    await logout();
    setIsUserMenuOpen(false);
  };

  return (
    <nav className="fixed top-0 w-full z-50 bg-black/90 backdrop-blur-sm border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex justify-between items-center h-20 gap-8">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <div className="text-xl font-light tracking-widest text-white">
              NITE PUTTER PRO
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8 ml-12">
            {navItems.map((item, index) => (
              <Link
                key={item.name}
                to={item.path}
                className={`text-sm font-light tracking-wider transition-colors duration-300 ${
                  isActive(item.path)
                    ? "text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <span className="text-xs text-gray-500 mr-2">[0{index + 1}]</span>
                {item.name}
              </Link>
            ))}
          </div>
            
          {/* Action buttons section */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Shop with Cart Count */}
            <Link
              to="/shop"
              className="relative text-sm font-light tracking-wider text-white border border-white/30 px-6 py-2 hover:bg-white hover:text-black transition-all duration-300"
            >
              SHOP
              {getCartCount() > 0 && (
                <span className="absolute -top-2 -right-2 bg-cyan-500 text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {getCartCount()}
                </span>
              )}
            </Link>

            {/* Shopping Cart Button */}
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative p-2 text-white hover:text-cyan-400 transition-colors duration-300"
              aria-label="Shopping Cart"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17M17 13v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6.01" />
              </svg>
              {getCartCount() > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {getCartCount()}
                </span>
              )}
            </button>

            {/* Authentication */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 text-sm font-light tracking-wider text-white hover:text-gray-300 transition-colors duration-300"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-black">
                      {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <span>{user?.first_name || user?.username}</span>
                  <svg className={`w-4 h-4 transition-transform duration-200 ${isUserMenuOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* User Dropdown */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-700 rounded-lg shadow-lg z-50">
                    <div className="py-2">
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 transition-colors duration-200"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        My Profile
                      </Link>
                      <Link
                        to="/orders"
                        className="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 transition-colors duration-200"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        Order History
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 transition-colors duration-200"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300"
                >
                  SIGN IN
                </Link>
                <Link
                  to="/register"
                  className="text-sm font-light tracking-wider text-white border border-white/30 px-4 py-2 hover:bg-white hover:text-black transition-all duration-300"
                >
                  JOIN US
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-white hover:text-gray-300 focus:outline-none"
            >
              <div className="w-6 h-5 relative flex flex-col justify-between">
                <span className={`w-full h-0.5 bg-current transform transition-all duration-300 ${isOpen ? 'rotate-45 translate-y-2' : ''}`}></span>
                <span className={`w-full h-0.5 bg-current transition-all duration-300 ${isOpen ? 'opacity-0' : ''}`}></span>
                <span className={`w-full h-0.5 bg-current transform transition-all duration-300 ${isOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
              </div>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden bg-black/95 backdrop-blur-sm border-t border-white/10">
            <div className="px-6 py-8 space-y-6">
              {navItems.map((item, index) => (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`block text-sm font-light tracking-wider transition-colors duration-300 ${
                    isActive(item.path)
                      ? "text-white"
                      : "text-gray-400 hover:text-white"
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  <span className="text-xs text-gray-500 mr-2">[0{index + 1}]</span>
                  {item.name}
                </Link>
              ))}
              
              <Link
                to="/shop"
                className="relative block text-sm font-light tracking-wider text-white border border-white/30 px-6 py-2 text-center hover:bg-white hover:text-black transition-all duration-300 mt-8"
                onClick={() => setIsOpen(false)}
              >
                SHOP {getCartCount() > 0 && `(${getCartCount()})`}
              </Link>

              {/* Mobile Cart Button */}
              <button
                onClick={() => { setIsCartOpen(true); setIsOpen(false); }}
                className="w-full text-left text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300 py-2 mt-4 flex items-center justify-between"
              >
                <span>SHOPPING CART</span>
                {getCartCount() > 0 && (
                  <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                    {getCartCount()}
                  </span>
                )}
              </button>

              {/* Mobile Authentication */}
              {isAuthenticated ? (
                <div className="pt-4 border-t border-gray-700">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-sm font-bold text-black">
                        {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <span className="text-white text-sm">
                      {user?.first_name || user?.username}
                    </span>
                  </div>
                  <Link
                    to="/profile"
                    className="block text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300 py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    MY PROFILE
                  </Link>
                  <Link
                    to="/orders"
                    className="block text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300 py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    ORDER HISTORY
                  </Link>
                  <button
                    onClick={() => { handleLogout(); setIsOpen(false); }}
                    className="block text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300 py-2"
                  >
                    SIGN OUT
                  </button>
                </div>
              ) : (
                <div className="pt-4 border-t border-gray-700 space-y-4">
                  <Link
                    to="/login"
                    className="block text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300"
                    onClick={() => setIsOpen(false)}
                  >
                    SIGN IN
                  </Link>
                  <Link
                    to="/register"
                    className="block text-sm font-light tracking-wider text-white border border-white/30 px-6 py-2 text-center hover:bg-white hover:text-black transition-all duration-300"
                    onClick={() => setIsOpen(false)}
                  >
                    JOIN US
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close user menu */}
      {isUserMenuOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsUserMenuOpen(false)}
        />
      )}

      {/* Shopping Cart Sidebar */}
      <ShoppingCart isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </nav>
  );
};

export default Navbar;