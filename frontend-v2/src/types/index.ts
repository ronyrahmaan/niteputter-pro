// Core Type Definitions for NitePutter Pro

// ===== Product Types =====
export interface ProductImage {
  url: string;
  alt: string;
  isPrimary: boolean;
}

export interface TechnicalSpec {
  name: string;
  value: string;
}

export interface InventoryInfo {
  inStock: boolean;
  quantity: number;
  lowStockThreshold: number;
}

export interface ReviewsSummary {
  averageRating: number;
  totalReviews: number;
  ratingDistribution: Record<number, number>;
}

export interface ShippingInfo {
  weight: number;
  dimensions: {
    length: number;
    width: number;
    height: number;
  };
  shipsFrom: string;
  estimatedDelivery: string;
}

export type ProductCategory = 'basic' | 'pro' | 'complete' | 'accessories';

export interface NitePutterProduct {
  id: string;
  sku: string;
  name: string;
  category: ProductCategory;
  description: string;
  shortDescription: string;
  features: string[];
  technicalSpecs: TechnicalSpec[];
  basePrice: number;
  salePrice?: number;
  images: ProductImage[];
  inventory: InventoryInfo;
  reviewsSummary: ReviewsSummary;
  shippingInfo: ShippingInfo;
  createdAt: Date;
  updatedAt: Date;
}

// ===== User Types =====
export interface User {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  isVerified: boolean;
  createdAt: Date;
  lastLogin?: Date;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  newsletter: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  defaultShippingAddress?: Address;
  defaultBillingAddress?: Address;
}

// ===== Order Types =====
export interface Address {
  id?: string;
  firstName: string;
  lastName: string;
  street: string;
  apartment?: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  phone: string;
  isDefault?: boolean;
}

export interface OrderItem {
  productId: string;
  productName: string;
  sku: string;
  price: number;
  quantity: number;
  subtotal: number;
  image?: string;
}

export type OrderStatus = 
  | 'pending'
  | 'processing'
  | 'paid'
  | 'shipped'
  | 'delivered'
  | 'cancelled'
  | 'refunded';

export interface PaymentInfo {
  method: 'stripe';
  transactionId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  paidAt?: Date;
}

export interface ShippingMethod {
  id: string;
  name: string;
  description: string;
  price: number;
  estimatedDelivery: string;
}

export interface Order {
  id: string;
  orderId: string;
  customerId: string;
  items: OrderItem[];
  shippingAddress: Address;
  billingAddress: Address;
  paymentInfo: PaymentInfo;
  shippingMethod: ShippingMethod;
  orderStatus: OrderStatus;
  trackingNumber?: string;
  carrier?: string;
  subtotal: number;
  shippingCost: number;
  tax: number;
  discount?: number;
  orderTotal: number;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
  shippedAt?: Date;
  deliveredAt?: Date;
}

// ===== Cart Types =====
export interface CartItem {
  id: string;
  product: NitePutterProduct;
  quantity: number;
  addedAt: Date;
}

export interface Cart {
  items: CartItem[];
  subtotal: number;
  estimatedShipping: number;
  estimatedTax: number;
  total: number;
  lastUpdated: Date;
}

// ===== Review Types =====
export interface ProductReview {
  id: string;
  productId: string;
  userId: string;
  userName: string;
  rating: number;
  title: string;
  comment: string;
  verified: boolean;
  helpful: number;
  notHelpful: number;
  images?: string[];
  createdAt: Date;
  updatedAt?: Date;
}

// ===== API Response Types =====
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ===== Auth Types =====
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  password: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ===== Analytics Types =====
export interface SalesData {
  date: string;
  revenue: number;
  orders: number;
  averageOrderValue: number;
}

export interface ProductMetrics {
  productId: string;
  productName: string;
  views: number;
  addedToCart: number;
  purchased: number;
  revenue: number;
  conversionRate: number;
}

export interface DashboardStats {
  totalRevenue: number;
  totalOrders: number;
  totalCustomers: number;
  averageOrderValue: number;
  conversionRate: number;
  returningCustomerRate: number;
  topProducts: ProductMetrics[];
  salesTrend: SalesData[];
}

// ===== Form Types =====
export interface CheckoutFormData {
  email: string;
  shippingAddress: Address;
  billingAddress: Address;
  sameAsShipping: boolean;
  shippingMethod: string;
  paymentMethod: string;
  saveAddress: boolean;
  newsletter: boolean;
  notes?: string;
}

export interface ContactFormData {
  name: string;
  email: string;
  phone?: string;
  subject: string;
  message: string;
}

// ===== Notification Types =====
export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// ===== Filter Types =====
export interface ProductFilters {
  category?: ProductCategory[];
  priceRange?: {
    min: number;
    max: number;
  };
  inStock?: boolean;
  rating?: number;
  sortBy?: 'price-asc' | 'price-desc' | 'rating' | 'newest' | 'popular';
}

export interface SearchParams {
  query: string;
  filters?: ProductFilters;
  page?: number;
  pageSize?: number;
}

// ===== Shipping Types =====
export interface ShippingQuote {
  method: string;
  carrier: string;
  service: string;
  rate: number;
  estimatedDays: string;
  trackingAvailable: boolean;
}

export interface TrackingInfo {
  trackingNumber: string;
  carrier: string;
  status: string;
  estimatedDelivery?: Date;
  trackingUrl: string;
  events?: TrackingEvent[];
  lastUpdate: Date;
}

export interface TrackingEvent {
  date: Date;
  location: string;
  status: string;
  description: string;
}