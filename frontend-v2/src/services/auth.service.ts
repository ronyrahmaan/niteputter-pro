import api from './api';
import { 
  LoginCredentials, 
  RegisterData, 
  User, 
  AuthTokens, 
  ApiResponse 
} from '@/types';

class AuthService {
  async login(credentials: LoginCredentials): Promise<ApiResponse<{ user: User; tokens: AuthTokens }>> {
    try {
      const response = await api.post('/auth/login', credentials);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Login failed',
      };
    }
  }
  
  async register(data: RegisterData): Promise<ApiResponse<{ user: User; tokens: AuthTokens }>> {
    try {
      const response = await api.post('/auth/register', data);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Registration failed',
      };
    }
  }
  
  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Logout anyway on client side
      console.error('Logout error:', error);
    }
  }
  
  async refreshToken(refreshToken: string): Promise<ApiResponse<{ tokens: AuthTokens }>> {
    try {
      const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Token refresh failed',
      };
    }
  }
  
  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const response = await api.get('/auth/me');
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to get user',
      };
    }
  }
  
  async updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    try {
      const response = await api.put('/auth/me', data);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to update profile',
      };
    }
  }
  
  async changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse<void>> {
    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      return {
        success: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to change password',
      };
    }
  }
  
  async requestPasswordReset(email: string): Promise<ApiResponse<void>> {
    try {
      await api.post('/auth/forgot-password', { email });
      return {
        success: true,
        message: 'Password reset email sent',
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to request password reset',
      };
    }
  }
  
  async resetPassword(token: string, newPassword: string): Promise<ApiResponse<void>> {
    try {
      await api.post('/auth/reset-password', {
        token,
        new_password: newPassword,
      });
      return {
        success: true,
        message: 'Password reset successfully',
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to reset password',
      };
    }
  }
}

export const authService = new AuthService();