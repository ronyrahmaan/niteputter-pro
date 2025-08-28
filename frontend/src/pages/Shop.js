import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../contexts/CartContext";
import ShoppingCart from "../components/ShoppingCart";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { ProductGridSkeleton } from "../components/LoadingSkeleton";

const Shop = () => {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [sortBy, setSortBy] = useState("featured");
  const [isLoaded, setIsLoaded] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [favorites, setFavorites] = useState(new Set());
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { addToCart, getCartCount, getCartTotal, cart, clearCart } = useCart();

  // Load favorites from localStorage on mount
  useEffect(() => {
    const savedFavorites = localStorage.getItem('nite_putter_favorites');
    if (savedFavorites) {
      try {
        const favoritesArray = JSON.parse(savedFavorites);
        setFavorites(new Set(favoritesArray));
      } catch (error) {
        console.error('Error loading favorites:', error);
      }
    }
  }, []);

  // Save favorites to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('nite_putter_favorites', JSON.stringify([...favorites]));
  }, [favorites]);

  // Fetch products from API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products`);
        if (response.ok) {
          const data = await response.json();
          // Transform backend products to frontend format
          const transformedProducts = data.products.map(product => ({
            id: product.sku, // Use SKU as ID for cart compatibility
            name: product.name,
            category: product.category === 'complete_systems' ? 'kits' : 
                     product.category === 'accessories' ? 'cups' : 'services',
            price: product.base_price,
            originalPrice: product.base_price * 1.2, // Add 20% as "original price"
            image: product.images?.[0]?.url || "https://niteputterpro.com/wp-content/uploads/2024/07/image0.png",
            description: product.short_description || product.description,
            features: product.features || [],
            rating: 4.8, // Default rating
            reviews: Math.floor(Math.random() * 200) + 50, // Random review count
            inStock: !product.is_out_of_stock,
            bestseller: product.is_featured || false
          }));
          setProducts(transformedProducts);
        } else {
          console.error('Failed to fetch products:', response.statusText);
          // Fall back to empty array if API fails
          setProducts([]);
        }
      } catch (error) {
        console.error('Error fetching products:', error);
        // Fall back to empty array if API fails
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Handle favorite toggle
  const toggleFavorite = (productId) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(productId)) {
        newFavorites.delete(productId);
      } else {
        newFavorites.add(productId);
      }
      return newFavorites;
    });
  };

  // Checkout handler for the shop page
  const handleShopCheckout = async () => {
    if (cart.length === 0) return;

    try {
      const originUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      
      if (cart.length === 1) {
        // Single item checkout
        const item = cart[0];
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/checkout/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            package_id: item.id,
            quantity: item.quantity,
            origin_url: originUrl,
            customer_info: {}
          })
        });

        if (!response.ok) {
          throw new Error('Failed to create checkout session');
        }

        const data = await response.json();
        
        // Redirect to Stripe Checkout
        window.location.href = data.url;
      } else {
        // Multiple items - redirect to custom checkout page  
        sessionStorage.setItem('checkout_cart', JSON.stringify(cart));
        window.location.href = '/checkout';
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to start checkout. Please try again.');
    }
  };

  useEffect(() => {
    setTimeout(() => setIsLoaded(true), 300);
  }, []);

  // Products are now loaded from the API via useEffect above

  const categories = [
    { id: "all", name: "All Products" },
    { id: "kits", name: "Complete Kits" },
    { id: "cups", name: "Individual Cups" },
    { id: "services", name: "Services" }
  ];



  const filteredProducts = selectedCategory === "all" 
    ? products 
    : products.filter(product => product.category === selectedCategory);

  const sortedProducts = [...filteredProducts].sort((a, b) => {
    switch (sortBy) {
      case "price-low":
        return a.price - b.price;
      case "price-high":
        return b.price - a.price;
      case "rating":
        return b.rating - a.rating;
      case "name":
        return a.name.localeCompare(b.name);
      default:
        return b.bestseller - a.bestseller;
    }
  });

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

      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-r from-cyan-900/50 via-purple-900/50 to-pink-900/50">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">NITE PUTTER SHOP</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
            Shop our complete collection of revolutionary night golf technology. Premium quality, cutting-edge features, and exceptional customer support.
          </p>
          {getCartCount() > 0 && (
            <div className="inline-flex items-center bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-full font-bold">
              🛒 {getCartCount()} items in cart - ${getCartTotal().toFixed(2)}
            </div>
          )}
        </div>
      </section>

      {/* Filters and Sorting */}
      <section className="py-12 bg-black">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col lg:flex-row justify-between items-center gap-6">
            {/* Category Filter */}
            <div className="flex flex-wrap gap-3">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`px-6 py-2 rounded-full font-medium transition-all duration-300 ${
                    selectedCategory === category.id
                      ? "bg-gradient-to-r from-cyan-500 to-purple-600 text-white"
                      : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>

            {/* Sort Options */}
            <div className="flex items-center gap-4">
              <span className="text-gray-400">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-cyan-500 focus:outline-none"
              >
                <option value="featured">Featured</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Customer Rating</option>
                <option value="name">Name A-Z</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section className="py-20 bg-gradient-to-b from-black to-gray-900">
        <div className="max-w-7xl mx-auto px-4">
          {loading ? (
            <ProductGridSkeleton count={8} />
          ) : products.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-white text-xl">No products available</div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
              {sortedProducts.map((product) => (
              <div key={product.id} className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl overflow-hidden border border-gray-700 hover:border-cyan-500/50 transition-all duration-300 transform hover:scale-105">
                {/* Product Image */}
                <div className="relative h-64 overflow-hidden">
                  <img 
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                  
                  {/* Badges */}
                  <div className="absolute top-4 right-4 flex flex-col gap-2">
                    {product.bestseller && (
                      <span className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                        BESTSELLER
                      </span>
                    )}
                    {product.originalPrice > product.price && (
                      <span className="bg-gradient-to-r from-red-500 to-red-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                        SALE
                      </span>
                    )}
                    {!product.inStock && (
                      <span className="bg-gray-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                        OUT OF STOCK
                      </span>
                    )}
                  </div>

                  {/* Price */}
                  <div className="absolute top-4 left-4">
                    <div className="bg-black/70 px-3 py-1 rounded-full">
                      <span className="text-white font-bold">
                        ${product.price}{product.category === 'software' && '/mo'}
                      </span>
                      {product.originalPrice > product.price && (
                        <span className="text-gray-400 line-through ml-2 text-sm">
                          ${product.originalPrice}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-6">
                  <h3 className="text-xl font-bold text-white mb-2">{product.name}</h3>
                  <p className="text-gray-400 mb-4 text-sm">{product.description}</p>
                  
                  {/* Rating */}
                  <div className="flex items-center mb-4">
                    <div className="flex text-yellow-400">
                      {[...Array(5)].map((_, i) => (
                        <span key={i} className={i < Math.floor(product.rating) ? "★" : "☆"}>
                          {i < Math.floor(product.rating) ? "★" : "☆"}
                        </span>
                      ))}
                    </div>
                    <span className="text-gray-400 text-sm ml-2">
                      {product.rating} ({product.reviews} reviews)
                    </span>
                  </div>

                  {/* Features */}
                  <div className="space-y-1 mb-6">
                    {product.features.slice(0, 2).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 bg-gradient-to-r from-cyan-400 to-purple-600 rounded-full"></div>
                        <span className="text-xs text-gray-300">{feature}</span>
                      </div>
                    ))}
                    {product.features.length > 2 && (
                      <span className="text-xs text-gray-500">+{product.features.length - 2} more features</span>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => addToCart(product)}
                      disabled={!product.inStock}
                      className={`flex-1 py-3 px-4 rounded-full font-bold text-sm transition-all duration-300 transform hover:scale-105 ${
                        product.inStock
                          ? "bg-gradient-to-r from-cyan-500 to-purple-600 text-white hover:from-cyan-600 hover:to-purple-700"
                          : "bg-gray-600 text-gray-400 cursor-not-allowed"
                      }`}
                    >
                      {product.inStock ? "ADD TO CART" : "OUT OF STOCK"}
                    </button>
                    <button 
                      onClick={() => toggleFavorite(product.id)}
                      className={`px-4 py-3 border rounded-full transition-all duration-300 transform hover:scale-105 ${
                        favorites.has(product.id)
                          ? "border-red-400 text-red-400 bg-red-400/10"
                          : "border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-gray-900"
                      }`}
                    >
                      <svg className="w-4 h-4" fill={favorites.has(product.id) ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Special Offers Section */}
      <section className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
            <span className="bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">SPECIAL OFFERS</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-green-900/50 to-green-800/50 p-8 rounded-2xl border border-green-500/30 text-center">
              <div className="text-4xl mb-4">🏌️</div>
              <h3 className="text-2xl font-bold text-green-400 mb-4">Golf Course Package</h3>
              <p className="text-gray-300 mb-6">
                Special pricing for golf courses and entertainment facilities. Save up to 30% on bulk orders.
              </p>
              <Link 
                to="/contact"
                className="inline-block bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-full font-bold hover:from-green-600 hover:to-green-700 transition-all duration-300"
              >
                GET QUOTE
              </Link>
            </div>
            
            <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/50 p-8 rounded-2xl border border-purple-500/30 text-center">
              <div className="text-4xl mb-4">🎓</div>
              <h3 className="text-2xl font-bold text-purple-400 mb-4">Educational Discount</h3>
              <p className="text-gray-300 mb-6">
                Schools and educational institutions receive 20% off all products. Valid ID required.
              </p>
              <Link 
                to="/contact"
                className="inline-block bg-gradient-to-r from-purple-500 to-purple-600 text-white px-6 py-3 rounded-full font-bold hover:from-purple-600 hover:to-purple-700 transition-all duration-300"
              >
                APPLY NOW
              </Link>
            </div>
            
            <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/50 p-8 rounded-2xl border border-blue-500/30 text-center">
              <div className="text-4xl mb-4">🇺🇸</div>
              <h3 className="text-2xl font-bold text-blue-400 mb-4">Veteran Discount</h3>
              <p className="text-gray-300 mb-6">
                Thank you for your service! Veterans receive 15% off all purchases year-round.
              </p>
              <Link 
                to="/contact"
                className="inline-block bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-3 rounded-full font-bold hover:from-blue-600 hover:to-blue-700 transition-all duration-300"
              >
                VERIFY STATUS
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Shopping Cart Summary (if items in cart) */}
      {getCartCount() > 0 && (
        <section className="py-12 bg-gradient-to-r from-cyan-900/50 via-purple-900/50 to-pink-900/50">
          <div className="max-w-4xl mx-auto px-4">
            <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 p-8 rounded-2xl border border-cyan-500/30">
              <h3 className="text-2xl font-bold text-white mb-6">Shopping Cart Summary</h3>
              <div className="space-y-4 mb-6">
                {cart.map((item) => (
                  <div key={item.id} className="flex items-center justify-between py-2 border-b border-gray-700">
                    <div className="flex items-center space-x-4">
                      <img src={item.image} alt={item.name} className="w-12 h-12 rounded-lg object-cover" />
                      <div>
                        <h4 className="text-white font-medium">{item.name}</h4>
                        <p className="text-gray-400 text-sm">Quantity: {item.quantity}</p>
                      </div>
                    </div>
                    <div className="text-cyan-400 font-bold">
                      ${(item.price * item.quantity).toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-between text-xl font-bold text-white">
                <span>Total:</span>
                <span className="text-cyan-400">${getCartTotal().toFixed(2)}</span>
              </div>
              <div className="flex gap-4 mt-6">
                <button 
                  onClick={() => clearCart()}
                  className="flex-1 bg-gray-600 text-white py-3 rounded-full font-bold hover:bg-gray-700 transition-all duration-300"
                >
                  CLEAR CART
                </button>
                <button 
                  onClick={handleShopCheckout}
                  className="flex-1 bg-gradient-to-r from-cyan-500 to-purple-600 text-white py-3 rounded-full font-bold hover:from-cyan-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
                >
                  PROCEED TO CHECKOUT
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Trust Badges */}
      <section className="py-12 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="flex items-center justify-center space-x-2">
              <div className="text-2xl">🚚</div>
              <div>
                <div className="font-bold text-white">Free Shipping</div>
                <div className="text-sm text-gray-400">Orders over $200</div>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="text-2xl">🔒</div>
              <div>
                <div className="font-bold text-white">Secure Payment</div>
                <div className="text-sm text-gray-400">256-bit SSL encryption</div>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="text-2xl">↩️</div>
              <div>
                <div className="font-bold text-white">30-Day Returns</div>
                <div className="text-sm text-gray-400">Hassle-free returns</div>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="text-2xl">🛡️</div>
              <div>
                <div className="font-bold text-white">2-Year Warranty</div>
                <div className="text-sm text-gray-400">Full product coverage</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-cyan-900/50 via-purple-900/50 to-pink-900/50">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Questions About <span className="bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">Our Products?</span>
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Our expert team is here to help you choose the perfect night golf solution for your needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/contact"
              className="bg-gradient-to-r from-cyan-500 to-purple-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:from-cyan-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
            >
              CONTACT EXPERT
            </Link>
            <a 
              href="/api/catalog"
              className="border-2 border-cyan-400 text-cyan-400 px-8 py-4 rounded-full font-bold text-lg hover:bg-cyan-400 hover:text-gray-900 transition-all duration-300"
            >
              DOWNLOAD CATALOG
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

export default Shop;