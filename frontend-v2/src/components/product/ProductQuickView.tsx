/**
 * ProductQuickView Component
 * Modal overlay for quick product preview
 */

import React, { useState } from 'react';
import { X, ShoppingCart, Heart, Star, Package, Truck, Shield, ChevronLeft, ChevronRight } from 'lucide-react';
import { Product } from '../../types/product';
import { formatPrice, formatInventoryStatus, formatShippingTime } from '../../utils/format';
import { useCartStore } from '../../stores/cartStore';
import { useWishlistStore } from '../../stores/wishlistStore';
import { toast } from 'react-hot-toast';
import { Link } from 'react-router-dom';

interface ProductQuickViewProps {
  product: Product;
  onClose: () => void;
}

export const ProductQuickView: React.FC<ProductQuickViewProps> = ({ product, onClose }) => {
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const addToCart = useCartStore(state => state.addItem);
  const { addItem: addToWishlist, removeItem: removeFromWishlist, isInWishlist } = useWishlistStore();
  
  const inventoryStatus = formatInventoryStatus(product.inventory.quantity, product.inventory.low_stock_threshold);
  const hasDiscount = product.compare_at_price && product.compare_at_price > product.price;
  const discountAmount = hasDiscount ? product.compare_at_price! - product.price : 0;
  const discountPercent = hasDiscount ? Math.round((discountAmount / product.compare_at_price!) * 100) : 0;
  
  const handleAddToCart = () => {
    if (!inventoryStatus.available) {
      toast.error('Product is out of stock');
      return;
    }
    
    if (quantity > product.inventory.quantity) {
      toast.error(`Only ${product.inventory.quantity} items available`);
      return;
    }
    
    addToCart(product, quantity);
    toast.success(`${quantity} ${quantity === 1 ? 'item' : 'items'} added to cart`);
    onClose();
  };
  
  const handleWishlistToggle = () => {
    if (isInWishlist(product.id)) {
      removeFromWishlist(product.id);
      toast.success('Removed from wishlist');
    } else {
      addToWishlist(product);
      toast.success('Added to wishlist');
    }
  };
  
  const handleQuantityChange = (value: number) => {
    if (value < 1) return;
    if (value > product.inventory.quantity) {
      toast.error(`Only ${product.inventory.quantity} items available`);
      return;
    }
    setQuantity(value);
  };
  
  const nextImage = () => {
    setSelectedImage((prev) => (prev + 1) % product.images.length);
  };
  
  const prevImage = () => {
    setSelectedImage((prev) => (prev - 1 + product.images.length) % product.images.length);
  };
  
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="relative bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-auto">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="grid grid-cols-1 lg:grid-cols-2">
            {/* Image Gallery */}
            <div className="p-8 bg-gray-50">
              <div className="relative aspect-square">
                {product.images.length > 1 && (
                  <>
                    <button
                      onClick={prevImage}
                      className="absolute left-2 top-1/2 -translate-y-1/2 z-10 p-2 bg-white/90 rounded-full shadow-md hover:bg-white transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    <button
                      onClick={nextImage}
                      className="absolute right-2 top-1/2 -translate-y-1/2 z-10 p-2 bg-white/90 rounded-full shadow-md hover:bg-white transition-colors"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </>
                )}
                
                <img
                  src={product.images[selectedImage].url}
                  alt={product.images[selectedImage].alt_text}
                  className="w-full h-full object-cover rounded-lg"
                />
                
                {hasDiscount && (
                  <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                    -{discountPercent}% OFF
                  </div>
                )}
              </div>
              
              {/* Thumbnail Images */}
              {product.images.length > 1 && (
                <div className="flex gap-2 mt-4 overflow-x-auto">
                  {product.images.map((image, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImage(index)}
                      className={`flex-shrink-0 w-20 h-20 rounded-md overflow-hidden border-2 transition-colors ${
                        selectedImage === index ? 'border-green-600' : 'border-gray-200 hover:border-gray-400'
                      }`}
                    >
                      <img
                        src={image.url}
                        alt={image.alt_text}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            {/* Product Info */}
            <div className="p-8">
              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">{product.category.toUpperCase()}</p>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h2>
                <p className="text-gray-600">{product.short_description}</p>
              </div>
              
              {/* Rating */}
              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <div className="flex text-yellow-400">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${
                          i < Math.floor(product.average_rating) ? 'fill-current' : ''
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-gray-600">
                    {product.average_rating} ({product.review_count} reviews)
                  </span>
                </div>
                
                <Link
                  to={`/product/${product.slug}`}
                  className="text-green-600 hover:text-green-700 underline text-sm"
                  onClick={onClose}
                >
                  View full details
                </Link>
              </div>
              
              {/* Price */}
              <div className="mb-6 pb-6 border-b">
                <div className="flex items-end gap-3 mb-2">
                  <span className="text-3xl font-bold text-green-600">
                    {formatPrice(product.price)}
                  </span>
                  {hasDiscount && (
                    <>
                      <span className="text-xl text-gray-500 line-through">
                        {formatPrice(product.compare_at_price!)}
                      </span>
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm font-semibold">
                        Save {formatPrice(discountAmount)}
                      </span>
                    </>
                  )}
                </div>
                
                <div className={`flex items-center gap-2 text-sm font-medium text-${inventoryStatus.color}-600`}>
                  <Package className="w-4 h-4" />
                  {inventoryStatus.text}
                </div>
              </div>
              
              {/* Features */}
              {product.features.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Key Features</h3>
                  <ul className="space-y-2">
                    {product.features.slice(0, 4).map((feature, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                        <span className="w-1.5 h-1.5 bg-green-600 rounded-full mt-1.5 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Add to Cart Section */}
              <div className="mb-6">
                <div className="flex items-center gap-4 mb-4">
                  <div>
                    <label htmlFor="quantity" className="text-sm font-medium text-gray-700 block mb-1">
                      Quantity
                    </label>
                    <div className="flex items-center border border-gray-300 rounded-md">
                      <button
                        onClick={() => handleQuantityChange(quantity - 1)}
                        className="px-3 py-2 hover:bg-gray-100 transition-colors"
                        disabled={quantity <= 1}
                      >
                        -
                      </button>
                      <input
                        id="quantity"
                        type="number"
                        value={quantity}
                        onChange={(e) => handleQuantityChange(parseInt(e.target.value) || 1)}
                        className="w-16 text-center border-x border-gray-300 py-2 focus:outline-none"
                        min="1"
                        max={product.inventory.quantity}
                      />
                      <button
                        onClick={() => handleQuantityChange(quantity + 1)}
                        className="px-3 py-2 hover:bg-gray-100 transition-colors"
                        disabled={quantity >= product.inventory.quantity}
                      >
                        +
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-1">Total Price</p>
                    <p className="text-xl font-bold text-gray-900">
                      {formatPrice(product.price * quantity)}
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-3">
                  <button
                    onClick={handleAddToCart}
                    disabled={!inventoryStatus.available}
                    className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors font-semibold flex items-center justify-center gap-2"
                  >
                    <ShoppingCart className="w-5 h-5" />
                    Add to Cart
                  </button>
                  
                  <button
                    onClick={handleWishlistToggle}
                    className={`px-6 py-3 border rounded-md transition-colors flex items-center gap-2 ${
                      isInWishlist(product.id)
                        ? 'bg-red-50 border-red-300 text-red-600 hover:bg-red-100'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <Heart className={`w-5 h-5 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
                    {isInWishlist(product.id) ? 'Saved' : 'Save'}
                  </button>
                </div>
              </div>
              
              {/* Shipping & Warranty */}
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3 text-gray-600">
                  <Truck className="w-4 h-4 text-green-600" />
                  <span>{formatShippingTime(3)} on orders over $150</span>
                </div>
                <div className="flex items-center gap-3 text-gray-600">
                  <Shield className="w-4 h-4 text-green-600" />
                  <span>{product.specifications.warranty} warranty included</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductQuickView;