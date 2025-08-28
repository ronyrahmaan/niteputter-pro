import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import { useAuthStore } from '@/store/auth.store';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Get token from auth store
    const tokens = useAuthStore.getState().tokens;
    if (tokens?.accessToken) {
      config.headers.Authorization = `Bearer ${tokens.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshed = await useAuthStore.getState().refreshToken();
        
        if (refreshed) {
          // Retry the original request with new token
          const tokens = useAuthStore.getState().tokens;
          originalRequest.headers.Authorization = `Bearer ${tokens?.accessToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    
    // Handle other errors
    const errorMessage = (error.response?.data as any)?.message || 
                        error.message || 
                        'An unexpected error occurred';
    
    return Promise.reject(new Error(errorMessage));
  }
);

export default api;