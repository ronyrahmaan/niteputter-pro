import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useAuth } from './AuthContext';

const CartContext = createContext();

const initialCartState = {
  items: [],
  isLoading: false,
  error: null
};

const cartReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
      
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
      
    case 'LOAD_CART':
      return {
        ...state,
        items: action.payload || [],
        isLoading: false,
        error: null
      };

    case 'ADD_TO_CART':
      const existingItem = state.items.find(item => item.id === action.payload.id);
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          )
        };
      }
      return {
        ...state,
        items: [...state.items, { ...action.payload, quantity: 1 }]
      };

    case 'REMOVE_FROM_CART':
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload)
      };

    case 'UPDATE_QUANTITY':
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: Math.max(0, action.payload.quantity) }
            : item
        ).filter(item => item.quantity > 0)
      };

    case 'CLEAR_CART':
      return {
        ...state,
        items: []
      };

    default:
      return state;
  }
};

export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialCartState);
  const { user, isAuthenticated, apiClient, isLoading: authLoading } = useAuth();

  // Load cart data when authentication state changes
  useEffect(() => {
    if (!authLoading) {
      loadCart();
    }
  }, [isAuthenticated, user, authLoading]);

  const loadCart = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      if (isAuthenticated && user) {
        // Load cart from user profile
        const userCartItems = user.cart_items || [];
        const localCartItems = getLocalCart();
        
        // Merge local cart with user cart if there are local items
        if (localCartItems.length > 0) {
          const mergedCart = mergeCartItems(localCartItems, userCartItems);
          
          // Update server with merged cart
          if (mergedCart.length !== userCartItems.length || 
              !arraysEqual(mergedCart, userCartItems)) {
            await syncCartToServer(mergedCart);
          }
          
          dispatch({ type: 'LOAD_CART', payload: mergedCart });
          clearLocalCart(); // Clear local storage after sync
        } else {
          dispatch({ type: 'LOAD_CART', payload: userCartItems });
        }
        
      } else {
        // Load cart from local storage
        const localCart = getLocalCart();
        dispatch({ type: 'LOAD_CART', payload: localCart });
      }
      
    } catch (error) {
      console.error('Failed to load cart:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const syncCartToServer = async (cartItems) => {
    if (!isAuthenticated || !apiClient) return;

    try {
      // Convert cart format to match backend expectations
      const backendCartItems = cartItems.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price,
        name: item.name,
        image: item.image,
        added_at: new Date().toISOString()
      }));

      await apiClient.put('/auth/me/cart', { cart_items: backendCartItems });
    } catch (error) {
      console.error('Failed to sync cart to server:', error);
      throw error;
    }
  };

  const getLocalCart = () => {
    try {
      const savedCart = localStorage.getItem('nite_putter_cart');
      return savedCart ? JSON.parse(savedCart) : [];
    } catch (error) {
      console.error('Error loading cart from localStorage:', error);
      return [];
    }
  };

  const saveLocalCart = (cartItems) => {
    try {
      localStorage.setItem('nite_putter_cart', JSON.stringify(cartItems));
    } catch (error) {
      console.error('Error saving cart to localStorage:', error);
    }
  };

  const clearLocalCart = () => {
    try {
      localStorage.removeItem('nite_putter_cart');
    } catch (error) {
      console.error('Error clearing cart from localStorage:', error);
    }
  };

  const mergeCartItems = (localItems, serverItems) => {
    const merged = [...serverItems];
    
    localItems.forEach(localItem => {
      const existingIndex = merged.findIndex(
        item => item.id === localItem.id
      );
      
      if (existingIndex >= 0) {
        // Combine quantities for existing items
        merged[existingIndex].quantity += localItem.quantity;
      } else {
        // Add new items from local cart
        merged.push(localItem);
      }
    });
    
    return merged;
  };

  const arraysEqual = (a, b) => {
    if (a.length !== b.length) return false;
    return a.every((item, index) => 
      item.id === b[index].id && 
      item.quantity === b[index].quantity
    );
  };

  const addToCart = async (product) => {
    try {
      // Calculate new cart state immediately to avoid race conditions
      const existingItem = state.items.find(item => item.id === product.id);
      let newItems;
      
      if (existingItem) {
        newItems = state.items.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        newItems = [...state.items, { ...product, quantity: 1 }];
      }
      
      // Update local state
      dispatch({ type: 'ADD_TO_CART', payload: product });
      
      // Sync with persistence layer using calculated state
      if (isAuthenticated) {
        await syncCartToServer(newItems);
      } else {
        saveLocalCart(newItems);
      }
    } catch (error) {
      console.error('Failed to add item to cart:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const removeFromCart = async (productId) => {
    try {
      dispatch({ type: 'REMOVE_FROM_CART', payload: productId });
      
      const newItems = state.items.filter(item => item.id !== productId);

      if (isAuthenticated) {
        await syncCartToServer(newItems);
      } else {
        saveLocalCart(newItems);
      }
    } catch (error) {
      console.error('Failed to remove item from cart:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const updateQuantity = async (productId, quantity) => {
    try {
      dispatch({ type: 'UPDATE_QUANTITY', payload: { id: productId, quantity } });
      
      const newItems = state.items.map(item =>
        item.id === productId ? { ...item, quantity } : item
      ).filter(item => item.quantity > 0);

      if (isAuthenticated) {
        await syncCartToServer(newItems);
      } else {
        saveLocalCart(newItems);
      }
    } catch (error) {
      console.error('Failed to update cart item quantity:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const clearCart = async () => {
    try {
      dispatch({ type: 'CLEAR_CART' });

      if (isAuthenticated) {
        await syncCartToServer([]);
      } else {
        clearLocalCart();
      }
    } catch (error) {
      console.error('Failed to clear cart:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const getCartTotal = () => {
    return state.items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getCartCount = () => {
    return state.items.reduce((count, item) => count + item.quantity, 0);
  };

  const value = {
    cart: state.items,
    isLoading: state.isLoading,
    error: state.error,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartTotal,
    getCartCount,
    loadCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export default CartContext;