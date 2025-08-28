/**
 * Formatting Utilities for NitePutter Pro
 */

/**
 * Format price with currency symbol
 */
export const formatPrice = (price: number | string, currency: string = 'USD'): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(numPrice);
};

/**
 * Format percentage discount
 */
export const formatDiscount = (originalPrice: number, salePrice: number): string => {
  const discount = ((originalPrice - salePrice) / originalPrice) * 100;
  return `${Math.round(discount)}% OFF`;
};

/**
 * Format date
 */
export const formatDate = (date: string | Date, format: 'short' | 'long' | 'relative' = 'short'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (format === 'relative') {
    const now = new Date();
    const diff = now.getTime() - dateObj.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} years ago`;
  }
  
  if (format === 'long') {
    return dateObj.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Format product SKU
 */
export const formatSKU = (sku: string): string => {
  return sku.toUpperCase().replace(/[^A-Z0-9-]/g, '');
};

/**
 * Format weight
 */
export const formatWeight = (weight: number, unit: 'kg' | 'g' | 'lbs' | 'oz' = 'lbs'): string => {
  const conversions = {
    kg: { lbs: 2.20462, oz: 35.274, g: 1000 },
    g: { lbs: 0.00220462, oz: 0.035274, kg: 0.001 },
    lbs: { kg: 0.453592, oz: 16, g: 453.592 },
    oz: { kg: 0.0283495, lbs: 0.0625, g: 28.3495 }
  };
  
  if (unit === 'lbs' && weight < 1) {
    const oz = weight * 16;
    return `${oz.toFixed(1)} oz`;
  }
  
  return `${weight.toFixed(2)} ${unit}`;
};

/**
 * Format rating stars
 */
export const formatRating = (rating: number): string => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
  
  let stars = '★'.repeat(fullStars);
  if (hasHalfStar) stars += '⯨';
  stars += '☆'.repeat(emptyStars);
  
  return stars;
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
};

/**
 * Format phone number
 */
export const formatPhone = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  return phone;
};

/**
 * Format order number
 */
export const formatOrderNumber = (orderNumber: string): string => {
  return `#${orderNumber.toUpperCase()}`;
};

/**
 * Format inventory status
 */
export const formatInventoryStatus = (quantity: number, lowThreshold: number = 10): {
  text: string;
  color: string;
  available: boolean;
} => {
  if (quantity === 0) {
    return { text: 'Out of Stock', color: 'red', available: false };
  }
  if (quantity <= lowThreshold) {
    return { text: `Only ${quantity} left`, color: 'orange', available: true };
  }
  return { text: 'In Stock', color: 'green', available: true };
};

/**
 * Format shipping time
 */
export const formatShippingTime = (days: number): string => {
  if (days === 1) return 'Next Day Delivery';
  if (days <= 2) return '2-Day Shipping';
  if (days <= 5) return `${days}-Day Shipping`;
  return `Ships in ${days} business days`;
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
};