import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Cart, CartItem, NitePutterProduct } from '@/types';
import { cartService } from '@/services/cart.service';
import toast from 'react-hot-toast';

interface CartStore extends Cart {
  // Actions
  addToCart: (product: NitePutterProduct, quantity?: number) => Promise<void>;
  removeFromCart: (productId: string) => Promise<void>;
  updateQuantity: (productId: string, quantity: number) => Promise<void>;
  clearCart: () => Promise<void>;
  syncCart: () => Promise<void>;
  calculateTotals: () => void;
  isLoading: boolean;
  error: string | null;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      // Initial state
      items: [],
      subtotal: 0,
      estimatedShipping: 0,
      estimatedTax: 0,
      total: 0,
      lastUpdated: new Date(),
      isLoading: false,
      error: null,

      // Add to cart
      addToCart: async (product: NitePutterProduct, quantity = 1) => {
        set({ isLoading: true, error: null });
        
        try {
          const { items } = get();
          const existingItem = items.find(item => item.product.id === product.id);
          
          let newItems: CartItem[];
          if (existingItem) {
            // Update quantity if item already in cart
            newItems = items.map(item =>
              item.product.id === product.id
                ? { ...item, quantity: item.quantity + quantity }
                : item
            );
          } else {
            // Add new item to cart
            const newItem: CartItem = {
              id: `${product.id}-${Date.now()}`,
              product,
              quantity,
              addedAt: new Date(),
            };
            newItems = [...items, newItem];
          }
          
          set({ items: newItems, lastUpdated: new Date() });
          get().calculateTotals();
          
          // Sync with backend if authenticated
          const authState = (window as any).authStore?.getState();
          if (authState?.isAuthenticated) {
            await cartService.syncCart(newItems);
          }
          
          set({ isLoading: false });
          toast.success(`${product.name} added to cart!`);
        } catch (error: any) {
          set({ isLoading: false, error: error.message });
          toast.error('Failed to add item to cart');
        }
      },

      // Remove from cart
      removeFromCart: async (productId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const { items } = get();
          const newItems = items.filter(item => item.product.id !== productId);
          
          set({ items: newItems, lastUpdated: new Date() });
          get().calculateTotals();
          
          // Sync with backend if authenticated
          const authState = (window as any).authStore?.getState();
          if (authState?.isAuthenticated) {
            await cartService.syncCart(newItems);
          }
          
          set({ isLoading: false });
          toast.success('Item removed from cart');
        } catch (error: any) {
          set({ isLoading: false, error: error.message });
          toast.error('Failed to remove item');
        }
      },

      // Update quantity
      updateQuantity: async (productId: string, quantity: number) => {
        if (quantity < 1) {
          return get().removeFromCart(productId);
        }
        
        set({ isLoading: true, error: null });
        
        try {
          const { items } = get();
          const newItems = items.map(item =>
            item.product.id === productId
              ? { ...item, quantity }
              : item
          );
          
          set({ items: newItems, lastUpdated: new Date() });
          get().calculateTotals();
          
          // Sync with backend if authenticated
          const authState = (window as any).authStore?.getState();
          if (authState?.isAuthenticated) {
            await cartService.syncCart(newItems);
          }
          
          set({ isLoading: false });
        } catch (error: any) {
          set({ isLoading: false, error: error.message });
          toast.error('Failed to update quantity');
        }
      },

      // Clear cart
      clearCart: async () => {
        set({ isLoading: true, error: null });
        
        try {
          set({
            items: [],
            subtotal: 0,
            estimatedShipping: 0,
            estimatedTax: 0,
            total: 0,
            lastUpdated: new Date(),
          });
          
          // Sync with backend if authenticated
          const authState = (window as any).authStore?.getState();
          if (authState?.isAuthenticated) {
            await cartService.syncCart([]);
          }
          
          set({ isLoading: false });
          toast.success('Cart cleared');
        } catch (error: any) {
          set({ isLoading: false, error: error.message });
          toast.error('Failed to clear cart');
        }
      },

      // Sync cart with backend
      syncCart: async () => {
        const authState = (window as any).authStore?.getState();
        if (!authState?.isAuthenticated) return;
        
        set({ isLoading: true, error: null });
        
        try {
          const response = await cartService.getCart();
          if (response.success && response.data) {
            set({
              items: response.data.items,
              lastUpdated: new Date(),
              isLoading: false,
            });
            get().calculateTotals();
          } else {
            // If backend cart is empty, sync local cart to backend
            const { items } = get();
            if (items.length > 0) {
              await cartService.syncCart(items);
            }
            set({ isLoading: false });
          }
        } catch (error: any) {
          set({ isLoading: false, error: error.message });
        }
      },

      // Calculate totals
      calculateTotals: () => {
        const { items } = get();
        
        const subtotal = items.reduce((total, item) => {
          const price = item.product.salePrice || item.product.basePrice;
          return total + (price * item.quantity);
        }, 0);
        
        // Basic shipping calculation (could be enhanced with shipping service)
        const estimatedShipping = subtotal > 100 ? 0 : 9.99;
        
        // Basic tax calculation (8% for example)
        const estimatedTax = subtotal * 0.08;
        
        const total = subtotal + estimatedShipping + estimatedTax;
        
        set({
          subtotal: Math.round(subtotal * 100) / 100,
          estimatedShipping: Math.round(estimatedShipping * 100) / 100,
          estimatedTax: Math.round(estimatedTax * 100) / 100,
          total: Math.round(total * 100) / 100,
        });
      },
    }),
    {
      name: 'niteputter-cart',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        items: state.items,
        lastUpdated: state.lastUpdated,
      }),
      onRehydrateStorage: () => (state) => {
        // Recalculate totals when cart is rehydrated
        state?.calculateTotals();
      },
    }
  )
);