import api from './api';
import { 
  NitePutterProduct, 
  ApiResponse, 
  PaginatedResponse,
  ProductFilters,
  ProductReview
} from '@/types';

class ProductService {
  async getProducts(
    page = 1, 
    pageSize = 12, 
    filters?: ProductFilters
  ): Promise<ApiResponse<PaginatedResponse<NitePutterProduct>>> {
    try {
      const params: any = {
        page,
        page_size: pageSize,
      };
      
      if (filters) {
        if (filters.category?.length) {
          params.category = filters.category.join(',');
        }
        if (filters.priceRange) {
          params.min_price = filters.priceRange.min;
          params.max_price = filters.priceRange.max;
        }
        if (filters.inStock !== undefined) {
          params.in_stock = filters.inStock;
        }
        if (filters.rating) {
          params.min_rating = filters.rating;
        }
        if (filters.sortBy) {
          params.sort_by = filters.sortBy;
        }
      }
      
      const response = await api.get('/products', { params });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to fetch products',
      };
    }
  }
  
  async getProduct(id: string): Promise<ApiResponse<NitePutterProduct>> {
    try {
      const response = await api.get(`/products/${id}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to fetch product',
      };
    }
  }
  
  async getProductBySku(sku: string): Promise<ApiResponse<NitePutterProduct>> {
    try {
      const response = await api.get(`/products/sku/${sku}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to fetch product',
      };
    }
  }
  
  async getFeaturedProducts(): Promise<ApiResponse<NitePutterProduct[]>> {
    try {
      const response = await api.get('/products/featured');
      return {
        success: true,
        data: response.data.products || [],
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to fetch featured products',
      };
    }
  }
  
  async getRelatedProducts(productId: string): Promise<ApiResponse<NitePutterProduct[]>> {
    try {
      const response = await api.get(`/products/${productId}/related`);
      return {
        success: true,
        data: response.data.products || [],
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to fetch related products',
      };
    }
  }
  
  async searchProducts(query: string): Promise<ApiResponse<NitePutterProduct[]>> {
    try {
      const response = await api.get('/products/search', {
        params: { q: query },
      });
      return {
        success: true,
        data: response.data.products || [],
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to search products',
      };
    }
  }
  
  async getProductReviews(
    productId: string,
    page = 1,
    pageSize = 10
  ): Promise<ApiResponse<PaginatedResponse<ProductReview>>> {
    try {
      const response = await api.get(`/products/${productId}/reviews`, {
        params: { page, page_size: pageSize },
      });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to fetch reviews',
      };
    }
  }
  
  async addProductReview(
    productId: string,
    review: {
      rating: number;
      title: string;
      comment: string;
    }
  ): Promise<ApiResponse<ProductReview>> {
    try {
      const response = await api.post(`/products/${productId}/reviews`, review);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to add review',
      };
    }
  }
  
  async checkStock(productId: string, quantity: number): Promise<ApiResponse<{
    available: boolean;
    currentStock: number;
    message?: string;
  }>> {
    try {
      const response = await api.post(`/products/${productId}/check-stock`, { quantity });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to check stock',
      };
    }
  }
}

export const productService = new ProductService();