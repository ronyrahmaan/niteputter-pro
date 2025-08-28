import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { AuthState, User, AuthTokens, LoginCredentials, RegisterData } from '@/types';
import { authService } from '@/services/auth.service';
import toast from 'react-hot-toast';

interface AuthStore extends AuthState {
  // Actions
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  updateUser: (user: Partial<User>) => void;
  clearError: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login action
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login(credentials);
          if (response.success && response.data) {
            const { user, tokens } = response.data;
            set({
              user,
              tokens,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            toast.success(`Welcome back, ${user.firstName}!`);
            return true;
          } else {
            const errorMsg = response.error || 'Login failed';
            set({ isLoading: false, error: errorMsg });
            toast.error(errorMsg);
            return false;
          }
        } catch (error: any) {
          const errorMsg = error.message || 'An error occurred during login';
          set({ isLoading: false, error: errorMsg });
          toast.error(errorMsg);
          return false;
        }
      },

      // Register action
      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.register(data);
          if (response.success && response.data) {
            const { user, tokens } = response.data;
            set({
              user,
              tokens,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            toast.success('Account created successfully!');
            return true;
          } else {
            const errorMsg = response.error || 'Registration failed';
            set({ isLoading: false, error: errorMsg });
            toast.error(errorMsg);
            return false;
          }
        } catch (error: any) {
          const errorMsg = error.message || 'An error occurred during registration';
          set({ isLoading: false, error: errorMsg });
          toast.error(errorMsg);
          return false;
        }
      },

      // Logout action
      logout: async () => {
        set({ isLoading: true });
        try {
          await authService.logout();
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
          toast.success('Logged out successfully');
        } catch (error) {
          console.error('Logout error:', error);
          // Clear state even if API call fails
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      // Refresh token action
      refreshToken: async () => {
        const { tokens } = get();
        if (!tokens?.refreshToken) {
          set({ isAuthenticated: false });
          return false;
        }

        try {
          const response = await authService.refreshToken(tokens.refreshToken);
          if (response.success && response.data) {
            set({
              tokens: response.data.tokens,
              isAuthenticated: true,
              error: null,
            });
            return true;
          } else {
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              error: 'Session expired',
            });
            return false;
          }
        } catch (error) {
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            error: 'Session expired',
          });
          return false;
        }
      },

      // Update user action
      updateUser: (userUpdate: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...userUpdate },
          });
        }
      },

      // Clear error action
      clearError: () => {
        set({ error: null });
      },

      // Check authentication status
      checkAuth: async () => {
        const { tokens } = get();
        if (!tokens?.accessToken) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const response = await authService.getCurrentUser();
          if (response.success && response.data) {
            set({
              user: response.data,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            // Try refreshing token
            const refreshed = await get().refreshToken();
            if (!refreshed) {
              set({
                user: null,
                tokens: null,
                isAuthenticated: false,
                isLoading: false,
              });
            }
          }
        } catch (error) {
          // Try refreshing token
          const refreshed = await get().refreshToken();
          if (!refreshed) {
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        }
      },
    }),
    {
      name: 'niteputter-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);