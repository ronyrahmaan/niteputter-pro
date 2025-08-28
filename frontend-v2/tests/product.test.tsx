/**
 * Frontend Product Tests
 * Tests product display, cart functionality, and responsive design
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { ProductCard } from '../src/components/product/ProductCard';
import { ProductGrid } from '../src/components/product/ProductGrid';
import { Cart } from '../src/components/cart/Cart';
import { useCartStore } from '../src/stores/cartStore';
import { useWishlistStore } from '../src/stores/wishlistStore';

// Mock product data
const mockProduct = {
  id: '1',
  sku: 'NP-TEST-001',
  name: 'Test NitePutter LED',
  slug: 'test-niteputter-led',
  category: 'basic',
  status: 'active',
  short_description: 'Test product description',
  description: 'Detailed test product description',
  price: 149.99,
  compare_at_price: 199.99,
  images: [
    {
      url: 'https://example.com/test-image.jpg',
      alt_text: 'Test product',
      is_primary: true,
      display_order: 1
    }
  ],
  features: ['Feature 1', 'Feature 2'],
  specifications: {
    battery_life: '10 hours',
    weight: '150g',
    warranty: '1 year'
  },
  inventory: {
    quantity: 100,
    reserved_quantity: 0,
    low_stock_threshold: 10,
    track_inventory: true,
    allow_backorder: false
  },
  average_rating: 4.5,
  review_count: 25,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
};

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('ProductCard Component', () => {
  beforeEach(() => {
    // Reset stores
    useCartStore.getState().clearCart();
    useWishlistStore.getState().clearWishlist();
  });

  test('renders product information correctly', () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    expect(screen.getByText(mockProduct.name)).toBeInTheDocument();
    expect(screen.getByText(mockProduct.short_description)).toBeInTheDocument();
    expect(screen.getByText('$149.99')).toBeInTheDocument();
    expect(screen.getByText('$199.99')).toBeInTheDocument(); // Compare at price
  });

  test('displays discount badge when applicable', () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    expect(screen.getByText('25% OFF')).toBeInTheDocument();
  });

  test('adds product to cart', async () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    const addToCartButton = screen.getByRole('button', { name: /add to cart/i });
    fireEvent.click(addToCartButton);

    await waitFor(() => {
      const cartItems = useCartStore.getState().items;
      expect(cartItems).toHaveLength(1);
      expect(cartItems[0].id).toBe(mockProduct.id);
    });
  });

  test('adds product to wishlist', async () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    const wishlistButton = screen.getByRole('button', { name: /wishlist/i });
    fireEvent.click(wishlistButton);

    await waitFor(() => {
      const wishlistItems = useWishlistStore.getState().items;
      expect(wishlistItems).toHaveLength(1);
      expect(wishlistItems[0].id).toBe(mockProduct.id);
    });
  });

  test('shows out of stock status', () => {
    const outOfStockProduct = {
      ...mockProduct,
      inventory: { ...mockProduct.inventory, quantity: 0 }
    };

    render(
      <TestWrapper>
        <ProductCard product={outOfStockProduct} />
      </TestWrapper>
    );

    expect(screen.getByText('Out of Stock')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add to cart/i })).toBeDisabled();
  });

  test('shows low stock warning', () => {
    const lowStockProduct = {
      ...mockProduct,
      inventory: { ...mockProduct.inventory, quantity: 5 }
    };

    render(
      <TestWrapper>
        <ProductCard product={lowStockProduct} />
      </TestWrapper>
    );

    expect(screen.getByText('Only 5 left')).toBeInTheDocument();
  });

  test('displays rating correctly', () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    expect(screen.getByText(`(${mockProduct.review_count})`)).toBeInTheDocument();
    // Check for star rating display
    const stars = screen.getAllByText(/★|☆/);
    expect(stars.length).toBeGreaterThan(0);
  });
});

describe('ProductGrid Component', () => {
  const mockProducts = [
    mockProduct,
    { ...mockProduct, id: '2', name: 'Product 2', price: 299.99 },
    { ...mockProduct, id: '3', name: 'Product 3', price: 99.99 }
  ];

  test('renders multiple products', () => {
    render(
      <TestWrapper>
        <ProductGrid products={mockProducts} />
      </TestWrapper>
    );

    expect(screen.getByText('Product 2')).toBeInTheDocument();
    expect(screen.getByText('Product 3')).toBeInTheDocument();
  });

  test('filters products by category', () => {
    const mixedProducts = [
      mockProduct,
      { ...mockProduct, id: '2', category: 'pro' },
      { ...mockProduct, id: '3', category: 'accessories' }
    ];

    render(
      <TestWrapper>
        <ProductGrid products={mixedProducts} />
      </TestWrapper>
    );

    const categoryFilter = screen.getByRole('combobox', { name: /category/i });
    fireEvent.change(categoryFilter, { target: { value: 'basic' } });

    // Only basic category products should be visible
    expect(screen.getByText(mockProduct.name)).toBeInTheDocument();
  });

  test('sorts products by price', () => {
    render(
      <TestWrapper>
        <ProductGrid products={mockProducts} />
      </TestWrapper>
    );

    const sortSelect = screen.getByRole('combobox', { name: /sort/i });
    fireEvent.change(sortSelect, { target: { value: 'price_asc' } });

    // Products should be sorted by price ascending
    const productCards = screen.getAllByTestId('product-card');
    expect(productCards[0]).toHaveTextContent('$99.99');
    expect(productCards[2]).toHaveTextContent('$299.99');
  });

  test('switches between grid and list view', () => {
    render(
      <TestWrapper>
        <ProductGrid products={mockProducts} />
      </TestWrapper>
    );

    const listViewButton = screen.getByRole('button', { name: /list view/i });
    fireEvent.click(listViewButton);

    // Check if products are in list format
    expect(screen.getByTestId('product-list')).toBeInTheDocument();

    const gridViewButton = screen.getByRole('button', { name: /grid view/i });
    fireEvent.click(gridViewButton);

    // Check if products are in grid format
    expect(screen.getByTestId('product-grid')).toBeInTheDocument();
  });
});

describe('Cart Functionality', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart();
  });

  test('displays empty cart message', () => {
    render(
      <TestWrapper>
        <Cart />
      </TestWrapper>
    );

    expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
  });

  test('displays cart items', () => {
    // Add item to cart
    useCartStore.getState().addItem(mockProduct, 2);

    render(
      <TestWrapper>
        <Cart />
      </TestWrapper>
    );

    expect(screen.getByText(mockProduct.name)).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Quantity
  });

  test('updates item quantity', async () => {
    useCartStore.getState().addItem(mockProduct, 1);

    render(
      <TestWrapper>
        <Cart />
      </TestWrapper>
    );

    const increaseButton = screen.getByRole('button', { name: /increase/i });
    fireEvent.click(increaseButton);

    await waitFor(() => {
      expect(useCartStore.getState().items[0].cart_quantity).toBe(2);
    });
  });

  test('removes item from cart', async () => {
    useCartStore.getState().addItem(mockProduct, 1);

    render(
      <TestWrapper>
        <Cart />
      </TestWrapper>
    );

    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(useCartStore.getState().items).toHaveLength(0);
    });
  });

  test('calculates cart total correctly', () => {
    useCartStore.getState().addItem(mockProduct, 2);

    render(
      <TestWrapper>
        <Cart />
      </TestWrapper>
    );

    // 149.99 * 2 = 299.98
    expect(screen.getByText('$299.98')).toBeInTheDocument();
  });

  test('prevents adding more than available inventory', () => {
    const limitedProduct = {
      ...mockProduct,
      inventory: { ...mockProduct.inventory, quantity: 5 }
    };

    useCartStore.getState().addItem(limitedProduct, 5);

    render(
      <TestWrapper>
        <Cart />
      </TestWrapper>
    );

    const increaseButton = screen.getByRole('button', { name: /increase/i });
    fireEvent.click(increaseButton);

    // Should show error message
    expect(screen.getByText(/only 5 items available/i)).toBeInTheDocument();
  });
});

describe('Responsive Design', () => {
  test('renders mobile view correctly', () => {
    // Set viewport to mobile size
    window.innerWidth = 375;
    
    render(
      <TestWrapper>
        <ProductGrid products={[mockProduct]} />
      </TestWrapper>
    );

    // Should show mobile-optimized layout
    const grid = screen.getByTestId('product-grid');
    expect(grid).toHaveClass('grid-cols-1');
  });

  test('renders tablet view correctly', () => {
    // Set viewport to tablet size
    window.innerWidth = 768;
    
    render(
      <TestWrapper>
        <ProductGrid products={[mockProduct]} />
      </TestWrapper>
    );

    // Should show tablet-optimized layout
    const grid = screen.getByTestId('product-grid');
    expect(grid).toHaveClass('sm:grid-cols-2');
  });

  test('renders desktop view correctly', () => {
    // Set viewport to desktop size
    window.innerWidth = 1920;
    
    render(
      <TestWrapper>
        <ProductGrid products={[mockProduct]} />
      </TestWrapper>
    );

    // Should show desktop-optimized layout
    const grid = screen.getByTestId('product-grid');
    expect(grid).toHaveClass('lg:grid-cols-4');
  });

  test('mobile menu toggles correctly', () => {
    window.innerWidth = 375;
    
    render(
      <TestWrapper>
        <Header />
      </TestWrapper>
    );

    const menuButton = screen.getByRole('button', { name: /menu/i });
    fireEvent.click(menuButton);

    // Mobile menu should be visible
    expect(screen.getByTestId('mobile-menu')).toBeVisible();
    
    fireEvent.click(menuButton);
    
    // Mobile menu should be hidden
    expect(screen.getByTestId('mobile-menu')).not.toBeVisible();
  });
});

describe('Accessibility', () => {
  test('has proper ARIA labels', () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /add to cart/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: new RegExp(mockProduct.name, 'i') })).toBeInTheDocument();
  });

  test('keyboard navigation works', () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    const addToCartButton = screen.getByRole('button', { name: /add to cart/i });
    
    // Tab to button
    addToCartButton.focus();
    expect(document.activeElement).toBe(addToCartButton);
    
    // Enter key press
    fireEvent.keyDown(addToCartButton, { key: 'Enter' });
    expect(useCartStore.getState().items).toHaveLength(1);
  });

  test('has proper focus indicators', () => {
    render(
      <TestWrapper>
        <ProductCard product={mockProduct} />
      </TestWrapper>
    );

    const button = screen.getByRole('button', { name: /add to cart/i });
    button.focus();
    
    // Check for focus styles
    expect(button).toHaveClass('focus:ring');
  });
});