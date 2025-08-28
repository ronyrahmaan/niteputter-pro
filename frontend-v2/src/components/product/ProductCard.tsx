/**
 * ProductCard Component
 * Displays product information in various layouts
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Heart, Eye, Star, Package, Zap } from 'lucide-react';
import { Product } from '../../types/product';
import { formatPrice, formatDiscount, formatRating, formatInventoryStatus } from '../../utils/format';
import { useCartStore } from '../../stores/cartStore';
import { useWishlistStore } from '../../stores/wishlistStore';
import { toast } from 'react-hot-toast';

interface ProductCardProps {
  product: Product;
  variant?: 'default' | 'compact' | 'featured';
  onQuickView?: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ 
  product, 
  variant = 'default',
  onQuickView 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [selectedImage, setSelectedImage] = useState(0);
  const addToCart = useCartStore(state => state.addItem);
  const { addItem: addToWishlist, removeItem: removeFromWishlist, isInWishlist } = useWishlistStore();
  
  const primaryImage = product.images.find(img => img.is_primary) || product.images[0];
  const secondaryImage = product.images.find(img => !img.is_primary) || product.images[1];
  const inventoryStatus = formatInventoryStatus(product.inventory.quantity, product.inventory.low_stock_threshold);
  const hasDiscount = product.compare_at_price && product.compare_at_price > product.price;
  
  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!inventoryStatus.available) {
      toast.error('Product is out of stock');
      return;
    }
    addToCart(product);
    toast.success(`${product.name} added to cart`);
  };
  
  const handleWishlistToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    if (isInWishlist(product.id)) {
      removeFromWishlist(product.id);
      toast.success('Removed from wishlist');
    } else {
      addToWishlist(product);
      toast.success('Added to wishlist');
    }
  };
  
  const handleQuickView = (e: React.MouseEvent) => {
    e.preventDefault();
    onQuickView?.(product);
  };
  
  // Compact variant for list views
  if (variant === 'compact') {
    return (
      <div className="flex gap-4 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
        <Link to={`/product/${product.slug}`} className="flex-shrink-0">
          <img 
            src={primaryImage.url} 
            alt={primaryImage.alt_text}
            className="w-24 h-24 object-cover rounded-md"
          />
        </Link>
        
        <div className="flex-1 min-w-0">
          <Link to={`/product/${product.slug}`}>
            <h3 className="font-semibold text-gray-900 hover:text-green-600 transition-colors truncate">
              {product.name}
            </h3>
          </Link>
          
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
            {product.short_description}
          </p>
          
          <div className="flex items-center gap-2 mt-2">
            <span className="text-lg font-bold text-green-600">{formatPrice(product.price)}</span>
            {hasDiscount && (
              <span className="text-sm text-gray-500 line-through">
                {formatPrice(product.compare_at_price!)}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2 mt-2">
            <div className="flex text-yellow-400">
              {formatRating(product.average_rating).split('').map((star, i) => (
                <span key={i}>{star}</span>
              ))}
            </div>
            <span className="text-sm text-gray-600">({product.review_count})</span>
            
            <span className={`ml-auto text-sm font-medium text-${inventoryStatus.color}-600`}>
              {inventoryStatus.text}
            </span>
          </div>
        </div>
        
        <div className="flex flex-col gap-2">
          <button
            onClick={handleAddToCart}
            disabled={!inventoryStatus.available}
            className="p-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
            title="Add to Cart"
          >
            <ShoppingCart className="w-5 h-5" />
          </button>
          
          <button
            onClick={handleWishlistToggle}
            className={`p-2 border rounded-md transition-colors ${
              isInWishlist(product.id) 
                ? 'bg-red-50 border-red-300 text-red-600' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            title="Add to Wishlist"
          >
            <Heart className={`w-5 h-5 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>
    );
  }
  
  // Featured variant for homepage/promotions
  if (variant === 'featured') {
    return (
      <div className="group bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
        {hasDiscount && (
          <div className="absolute top-4 left-4 z-10 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
            {formatDiscount(product.compare_at_price!, product.price)}
          </div>
        )}
        
        {product.category === 'pro' && (
          <div className="absolute top-4 right-4 z-10 bg-gold-600 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
            <Zap className="w-4 h-4" />
            PRO
          </div>
        )}
        
        <Link to={`/product/${product.slug}`} className="block relative h-80 overflow-hidden">
          <img 
            src={isHovered && secondaryImage ? secondaryImage.url : primaryImage.url}
            alt={primaryImage.alt_text}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          />
          
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          
          <div className="absolute bottom-4 left-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleAddToCart}
              disabled={!inventoryStatus.available}
              className="flex-1 bg-white/90 backdrop-blur text-gray-900 py-2 px-4 rounded-md hover:bg-white transition-colors font-semibold"
            >
              Add to Cart
            </button>
            
            <button
              onClick={handleQuickView}
              className="p-2 bg-white/90 backdrop-blur text-gray-900 rounded-md hover:bg-white transition-colors"
              title="Quick View"
            >
              <Eye className="w-5 h-5" />
            </button>
          </div>
        </Link>
        
        <div className="p-6">
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-sm text-gray-500 mb-1">{product.category.toUpperCase()}</p>
              <Link to={`/product/${product.slug}`}>
                <h3 className="text-xl font-bold text-gray-900 hover:text-green-600 transition-colors">
                  {product.name}
                </h3>
              </Link>
            </div>
            
            <button
              onClick={handleWishlistToggle}
              className={`p-2 rounded-full transition-colors ${
                isInWishlist(product.id)
                  ? 'bg-red-50 text-red-600'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Heart className={`w-5 h-5 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
            </button>
          </div>
          
          <p className="text-gray-600 mb-4 line-clamp-2">{product.short_description}</p>
          
          <div className="flex items-center gap-2 mb-4">
            <div className="flex text-yellow-400">
              {formatRating(product.average_rating).split('').map((star, i) => (
                <span key={i} className="text-lg">{star}</span>
              ))}
            </div>
            <span className="text-gray-600">({product.review_count} reviews)</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <span className="text-2xl font-bold text-green-600">{formatPrice(product.price)}</span>
              {hasDiscount && (
                <span className="ml-2 text-lg text-gray-500 line-through">
                  {formatPrice(product.compare_at_price!)}
                </span>
              )}
            </div>
            
            <div className={`flex items-center gap-1 text-sm font-medium text-${inventoryStatus.color}-600`}>
              <Package className="w-4 h-4" />
              {inventoryStatus.text}
            </div>
          </div>
          
          {product.features.length > 0 && (
            <ul className="mt-4 space-y-1">
              {product.features.slice(0, 3).map((feature, index) => (
                <li key={index} className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="w-1 h-1 bg-green-600 rounded-full" />
                  {feature}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  }
  
  // Default card variant
  return (
    <div className="group bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow overflow-hidden">
      {hasDiscount && (
        <div className="absolute top-2 left-2 z-10 bg-red-600 text-white px-2 py-1 rounded text-xs font-semibold">
          {formatDiscount(product.compare_at_price!, product.price)}
        </div>
      )}
      
      <Link to={`/product/${product.slug}`} className="block relative aspect-square overflow-hidden">
        <img 
          src={isHovered && secondaryImage ? secondaryImage.url : primaryImage.url}
          alt={primaryImage.alt_text}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        />
        
        <div className="absolute top-2 right-2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleWishlistToggle}
            className={`p-2 bg-white/90 backdrop-blur rounded-full shadow-md hover:bg-white transition-colors ${
              isInWishlist(product.id) ? 'text-red-600' : 'text-gray-600'
            }`}
            title="Add to Wishlist"
          >
            <Heart className={`w-4 h-4 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
          </button>
          
          <button
            onClick={handleQuickView}
            className="p-2 bg-white/90 backdrop-blur rounded-full shadow-md hover:bg-white transition-colors text-gray-600"
            title="Quick View"
          >
            <Eye className="w-4 h-4" />
          </button>
        </div>
      </Link>
      
      <div className="p-4">
        <p className="text-xs text-gray-500 mb-1">{product.category.toUpperCase()}</p>
        
        <Link to={`/product/${product.slug}`}>
          <h3 className="font-semibold text-gray-900 hover:text-green-600 transition-colors line-clamp-2">
            {product.name}
          </h3>
        </Link>
        
        <div className="flex items-center gap-1 mt-2">
          <div className="flex text-yellow-400 text-sm">
            {formatRating(product.average_rating).split('').map((star, i) => (
              <span key={i}>{star}</span>
            ))}
          </div>
          <span className="text-xs text-gray-600">({product.review_count})</span>
        </div>
        
        <div className="flex items-center justify-between mt-3">
          <div>
            <span className="text-lg font-bold text-green-600">{formatPrice(product.price)}</span>
            {hasDiscount && (
              <span className="ml-1 text-sm text-gray-500 line-through">
                {formatPrice(product.compare_at_price!)}
              </span>
            )}
          </div>
          
          <span className={`text-xs font-medium text-${inventoryStatus.color}-600`}>
            {inventoryStatus.text}
          </span>
        </div>
        
        <button
          onClick={handleAddToCart}
          disabled={!inventoryStatus.available}
          className="w-full mt-3 bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors font-semibold flex items-center justify-center gap-2"
        >
          <ShoppingCart className="w-4 h-4" />
          Add to Cart
        </button>
      </div>
    </div>
  );
};

export default ProductCard;