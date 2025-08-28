import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  tokens: null,
  error: null
};

function authReducer(state, action) {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
      
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isLoading: false,
        error: null
      };
      
    case 'AUTH_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        tokens: null,
        isLoading: false,
        error: action.payload
      };
      
    case 'LOGOUT':
      return {
        ...initialState,
        isLoading: false
      };
      
    case 'UPDATE_USER':
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
      
    case 'UPDATE_TOKENS':
      return {
        ...state,
        tokens: action.payload
      };
      
    default:
      return state;
  }
}

// Token storage utilities
class TokenStorage {
  constructor() {
    this.accessTokenKey = 'access_token';
    this.refreshTokenKey = 'refresh_token';
  }

  setTokens(tokens) {
    if (tokens.access_token) {
      // Store access token in memory for security
      this.accessToken = tokens.access_token;
      // Also store in sessionStorage for page refresh persistence
      sessionStorage.setItem(this.accessTokenKey, tokens.access_token);
    }

    if (tokens.refresh_token) {
      // Store refresh token in localStorage for longer persistence
      localStorage.setItem(this.refreshTokenKey, tokens.refresh_token);
    }
  }

  getTokens() {
    const access_token = this.accessToken || sessionStorage.getItem(this.accessTokenKey);
    const refresh_token = localStorage.getItem(this.refreshTokenKey);
    
    return {
      access_token,
      refresh_token
    };
  }

  clearTokens() {
    this.accessToken = null;
    sessionStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
  }

  getAccessToken() {
    return this.accessToken || sessionStorage.getItem(this.accessTokenKey);
  }

  hasValidTokens() {
    const access_token = this.getAccessToken();
    return Boolean(access_token);
  }

  // Token expiration checking
  isTokenExpired(token) {
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp <= currentTime;
    } catch (error) {
      return true;
    }
  }
}

const tokenStorage = new TokenStorage();

// API configuration
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create API client with interceptors
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Auth API client (without interceptors to prevent loops)
const authClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json'
  }
});

let isRefreshing = false;
let refreshQueue = [];

// Process queued requests after token refresh
const processQueue = (error, token = null) => {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  refreshQueue = [];
};

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const tokens = tokenStorage.getTokens();
    if (tokens?.access_token) {
      config.headers.Authorization = `Bearer ${tokens.access_token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue the request while refresh is in progress
        return new Promise((resolve, reject) => {
          refreshQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const tokens = tokenStorage.getTokens();
        if (!tokens?.refresh_token) {
          throw new Error('No refresh token');
        }

        const formData = new FormData();
        formData.append('refresh_token', tokens.refresh_token);

        const response = await authClient.post('/auth/refresh', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        const { access_token } = response.data;
        const newTokens = {
          access_token,
          refresh_token: tokens.refresh_token
        };

        tokenStorage.setTokens(newTokens);
        processQueue(null, access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);

      } catch (refreshError) {
        processQueue(refreshError, null);
        tokenStorage.clearTokens();
        
        // Redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const tokens = tokenStorage.getTokens();
        if (tokens?.access_token && !tokenStorage.isTokenExpired(tokens.access_token)) {
          // Get current user
          const response = await apiClient.get('/auth/me');
          const user = response.data;
          
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: { user, tokens }
          });
        } else {
          dispatch({ type: 'AUTH_FAILURE', payload: null });
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        tokenStorage.clearTokens();
        dispatch({ type: 'AUTH_FAILURE', payload: error.message });
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const formData = new FormData();
      formData.append('username', email); // OAuth2 uses 'username' field for email
      formData.append('password', password);

      const response = await authClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const { user, access_token, refresh_token } = response.data;
      
      const tokens = { access_token, refresh_token };
      tokenStorage.setTokens(tokens);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, tokens }
      });
      
      return { success: true, user };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const response = await authClient.post('/auth/register', userData);
      const user = response.data;
      
      // Auto-login after successful registration
      const loginResult = await login(userData.email, userData.password);
      
      return loginResult;
    } catch (error) {
      let errorMessage = 'Registration failed';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail[0]?.msg || 'Registration failed';
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      // Clear tokens and state
      tokenStorage.clearTokens();
      dispatch({ type: 'LOGOUT' });
    } catch (error) {
      console.error('Logout failed:', error);
      // Clear tokens anyway
      tokenStorage.clearTokens();
      dispatch({ type: 'LOGOUT' });
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await apiClient.put('/auth/me', profileData);
      const updatedUser = response.data;
      
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      return { success: true, user: updatedUser };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    apiClient // Export for use in other components
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { apiClient };