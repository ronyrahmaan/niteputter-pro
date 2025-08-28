/**
 * Wishlist Store using Zustand
 * Manages wishlist/favorites state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Product } from '../types/product';

interface WishlistState {
  items: Product[];
  
  // Actions
  addItem: (product: Product) => void;
  removeItem: (productId: string) => void;
  clearWishlist: () => void;
  isInWishlist: (productId: string) => boolean;
  
  // Computed
  getItemCount: () => number;
}

export const useWishlistStore = create<WishlistState>()(
  persist(
    (set, get) => ({
      items: [],
      
      addItem: (product: Product) => {
        const currentItems = get().items;
        const exists = currentItems.some(item => item.id === product.id);
        
        if (!exists) {
          set({ items: [...currentItems, product] });
        }
      },
      
      removeItem: (productId: string) => {
        set(state => ({
          items: state.items.filter(item => item.id !== productId)
        }));
      },
      
      clearWishlist: () => {
        set({ items: [] });
      },
      
      isInWishlist: (productId: string) => {
        return get().items.some(item => item.id === productId);
      },
      
      getItemCount: () => {
        return get().items.length;
      }
    }),
    {
      name: 'niteputter-wishlist', // localStorage key
    }
  )
);