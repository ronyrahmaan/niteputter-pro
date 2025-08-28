/**
 * Cart Store using Zustand
 * Manages shopping cart state and operations
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Product, CartItem } from '../types/product';
import toast from 'react-hot-toast';

interface CartState {
  items: CartItem[];
  isOpen: boolean;
  
  // Actions
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  toggleCart: () => void;
  
  // Computed values
  getTotalItems: () => number;
  getSubtotal: () => number;
  getItemQuantity: (productId: string) => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      isOpen: false,
      
      addItem: (product: Product, quantity = 1) => {
        const currentItems = get().items;
        const existingItem = currentItems.find(item => item.id === product.id);
        
        if (existingItem) {
          // Update quantity if item already exists
          const newQuantity = existingItem.cart_quantity + quantity;
          
          // Check inventory limit
          if (newQuantity > product.inventory.quantity) {
            toast.error(`Only ${product.inventory.quantity} items available`);
            return;
          }
          
          set({
            items: currentItems.map(item =>
              item.id === product.id
                ? {
                    ...item,
                    cart_quantity: newQuantity,
                    subtotal: newQuantity * item.price
                  }
                : item
            )
          });
        } else {
          // Add new item to cart
          if (quantity > product.inventory.quantity) {
            toast.error(`Only ${product.inventory.quantity} items available`);
            return;
          }
          
          const cartItem: CartItem = {
            ...product,
            cart_quantity: quantity,
            subtotal: quantity * product.price
          };
          
          set({ items: [...currentItems, cartItem] });
        }
      },
      
      removeItem: (productId: string) => {
        set(state => ({
          items: state.items.filter(item => item.id !== productId)
        }));
      },
      
      updateQuantity: (productId: string, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(productId);
          return;
        }
        
        const currentItems = get().items;
        const item = currentItems.find(i => i.id === productId);
        
        if (item && quantity > item.inventory.quantity) {
          toast.error(`Only ${item.inventory.quantity} items available`);
          return;
        }
        
        set({
          items: currentItems.map(item =>
            item.id === productId
              ? {
                  ...item,
                  cart_quantity: quantity,
                  subtotal: quantity * item.price
                }
              : item
          )
        });
      },
      
      clearCart: () => {
        set({ items: [] });
      },
      
      toggleCart: () => {
        set(state => ({ isOpen: !state.isOpen }));
      },
      
      getTotalItems: () => {
        return get().items.reduce((total, item) => total + item.cart_quantity, 0);
      },
      
      getSubtotal: () => {
        return get().items.reduce((total, item) => total + item.subtotal, 0);
      },
      
      getItemQuantity: (productId: string) => {
        const item = get().items.find(i => i.id === productId);
        return item?.cart_quantity || 0;
      }
    }),
    {
      name: 'niteputter-cart', // localStorage key
      partialize: (state) => ({ items: state.items }) // Only persist items, not UI state
    }
  )
);