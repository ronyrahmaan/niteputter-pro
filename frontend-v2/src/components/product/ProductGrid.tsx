/**
 * ProductGrid Component
 * Displays a grid of products with filtering and sorting
 */

import React, { useState, useMemo } from 'react';
import { Grid, List, Filter, ChevronDown } from 'lucide-react';
import { Product, ProductFilters, ProductCategory } from '../../types/product';
import { ProductCard } from './ProductCard';
import { ProductQuickView } from './ProductQuickView';

interface ProductGridProps {
  products: Product[];
  title?: string;
  showFilters?: boolean;
  defaultView?: 'grid' | 'list';
  columns?: 3 | 4 | 5;
}

export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  title,
  showFilters = true,
  defaultView = 'grid',
  columns = 4
}) => {
  const [view, setView] = useState<'grid' | 'list'>(defaultView);
  const [quickViewProduct, setQuickViewProduct] = useState<Product | null>(null);
  const [filters, setFilters] = useState<ProductFilters>({
    sortBy: 'newest'
  });
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  
  // Apply filters and sorting
  const filteredProducts = useMemo(() => {
    let result = [...products];
    
    // Filter by category
    if (filters.category) {
      result = result.filter(p => p.category === filters.category);
    }
    
    // Filter by price range
    if (filters.minPrice !== undefined) {
      result = result.filter(p => p.price >= filters.minPrice!);
    }
    if (filters.maxPrice !== undefined) {
      result = result.filter(p => p.price <= filters.maxPrice!);
    }
    
    // Filter by stock status
    if (filters.inStock !== undefined) {
      result = result.filter(p => 
        filters.inStock ? p.inventory.quantity > 0 : p.inventory.quantity === 0
      );
    }
    
    // Filter by rating
    if (filters.rating !== undefined) {
      result = result.filter(p => p.average_rating >= filters.rating!);
    }
    
    // Sort products
    switch (filters.sortBy) {
      case 'price_asc':
        result.sort((a, b) => a.price - b.price);
        break;
      case 'price_desc':
        result.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        result.sort((a, b) => b.average_rating - a.average_rating);
        break;
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'newest':
      default:
        result.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
    }
    
    return result;
  }, [products, filters]);
  
  const handleFilterChange = (key: keyof ProductFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };
  
  const clearFilters = () => {
    setFilters({ sortBy: 'newest' });
  };
  
  const getGridCols = () => {
    switch (columns) {
      case 3: return 'lg:grid-cols-3';
      case 4: return 'lg:grid-cols-4';
      case 5: return 'lg:grid-cols-5';
      default: return 'lg:grid-cols-4';
    }
  };
  
  return (
    <>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          {title && (
            <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          )}
          
          <div className="flex items-center gap-4">
            {/* Results count */}
            <span className="text-sm text-gray-600">
              {filteredProducts.length} {filteredProducts.length === 1 ? 'product' : 'products'}
            </span>
            
            {/* View toggle */}
            <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setView('grid')}
                className={`p-2 rounded ${
                  view === 'grid' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
                } transition-colors`}
                title="Grid view"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setView('list')}
                className={`p-2 rounded ${
                  view === 'list' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
                } transition-colors`}
                title="List view"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
            
            {/* Sort dropdown */}
            <div className="relative">
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-md pl-3 pr-8 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="newest">Newest First</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="rating">Top Rated</option>
                <option value="name">Name: A-Z</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
            </div>
            
            {showFilters && (
              <button
                onClick={() => setShowFilterPanel(!showFilterPanel)}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                <Filter className="w-4 h-4" />
                Filters
              </button>
            )}
          </div>
        </div>
        
        {/* Filter Panel */}
        {showFilterPanel && (
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={filters.category || ''}
                  onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">All Categories</option>
                  <option value={ProductCategory.BASIC}>Basic</option>
                  <option value={ProductCategory.PRO}>Pro</option>
                  <option value={ProductCategory.COMPLETE}>Complete</option>
                  <option value={ProductCategory.ACCESSORIES}>Accessories</option>
                </select>
              </div>
              
              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price Range
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.minPrice || ''}
                    onChange={(e) => handleFilterChange('minPrice', e.target.value ? Number(e.target.value) : undefined)}
                    className="flex-1 border border-gray-300 rounded-md px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <span className="text-gray-500">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.maxPrice || ''}
                    onChange={(e) => handleFilterChange('maxPrice', e.target.value ? Number(e.target.value) : undefined)}
                    className="flex-1 border border-gray-300 rounded-md px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>
              
              {/* Stock Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Availability
                </label>
                <select
                  value={filters.inStock === undefined ? '' : filters.inStock.toString()}
                  onChange={(e) => handleFilterChange('inStock', e.target.value === '' ? undefined : e.target.value === 'true')}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">All Products</option>
                  <option value="true">In Stock</option>
                  <option value="false">Out of Stock</option>
                </select>
              </div>
              
              {/* Rating Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Rating
                </label>
                <select
                  value={filters.rating || ''}
                  onChange={(e) => handleFilterChange('rating', e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">All Ratings</option>
                  <option value="4">4+ Stars</option>
                  <option value="3">3+ Stars</option>
                  <option value="2">2+ Stars</option>
                  <option value="1">1+ Stars</option>
                </select>
              </div>
            </div>
            
            {/* Clear Filters */}
            <div className="mt-4 flex justify-end">
              <button
                onClick={clearFilters}
                className="text-sm text-gray-600 hover:text-gray-900 underline"
              >
                Clear all filters
              </button>
            </div>
          </div>
        )}
        
        {/* Product Grid/List */}
        {filteredProducts.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-600">No products found matching your filters.</p>
            <button
              onClick={clearFilters}
              className="mt-4 text-green-600 hover:text-green-700 underline"
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div className={
            view === 'grid'
              ? `grid grid-cols-1 sm:grid-cols-2 ${getGridCols()} gap-6`
              : 'space-y-4'
          }>
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                variant={view === 'list' ? 'compact' : 'default'}
                onQuickView={setQuickViewProduct}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* Quick View Modal */}
      {quickViewProduct && (
        <ProductQuickView
          product={quickViewProduct}
          onClose={() => setQuickViewProduct(null)}
        />
      )}
    </>
  );
};

export default ProductGrid;