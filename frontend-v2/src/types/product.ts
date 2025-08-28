/**
 * Product Type Definitions for NitePutter Pro
 */

export interface Product {
  id: string;
  sku: string;
  name: string;
  slug: string;
  category: ProductCategory;
  status: ProductStatus;
  short_description: string;
  description: string;
  price: number;
  compare_at_price?: number;
  cost_per_unit?: number;
  images: ProductImage[];
  features: string[];
  whats_included: string[];
  specifications: ProductSpecification;
  shipping: ShippingInfo;
  inventory: InventoryInfo;
  seo: SEOInfo;
  average_rating: number;
  review_count: number;
  video_url?: string;
  instruction_manual_url?: string;
  created_at: string;
  updated_at: string;
}

export enum ProductCategory {
  BASIC = 'basic',
  PRO = 'pro',
  COMPLETE = 'complete',
  ACCESSORIES = 'accessories'
}

export enum ProductStatus {
  ACTIVE = 'active',
  DRAFT = 'draft',
  ARCHIVED = 'archived',
  OUT_OF_STOCK = 'out_of_stock'
}

export interface ProductImage {
  url: string;
  alt_text: string;
  is_primary: boolean;
  display_order: number;
}

export interface ProductSpecification {
  battery_life: string;
  charging_time: string;
  led_brightness: string;
  weight: string;
  material: string;
  water_resistance: string;
  warranty: string;
  [key: string]: string; // Allow additional specs
}

export interface ShippingInfo {
  weight: number;
  length: number;
  width: number;
  height: number;
  ships_separately: boolean;
}

export interface InventoryInfo {
  quantity: number;
  reserved_quantity: number;
  low_stock_threshold: number;
  track_inventory: boolean;
  allow_backorder: boolean;
}

export interface SEOInfo {
  meta_title?: string;
  meta_description?: string;
  url_slug: string;
  keywords: string[];
}

export interface CartItem extends Product {
  cart_quantity: number;
  subtotal: number;
}

export interface ProductFilters {
  category?: ProductCategory;
  minPrice?: number;
  maxPrice?: number;
  inStock?: boolean;
  rating?: number;
  sortBy?: 'price_asc' | 'price_desc' | 'rating' | 'newest' | 'name';
}

export interface ProductVariant {
  id: string;
  name: string;
  sku: string;
  price: number;
  inventory_quantity: number;
  options: {
    [key: string]: string;
  };
}