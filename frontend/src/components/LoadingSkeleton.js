import React from 'react';

export const ProductCardSkeleton = () => {
  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl p-6 animate-pulse">
      {/* Image Skeleton */}
      <div className="aspect-square bg-gray-800 rounded-lg mb-6"></div>
      
      {/* Title Skeleton */}
      <div className="h-6 bg-gray-800 rounded mb-3"></div>
      
      {/* Description Skeleton */}
      <div className="space-y-2 mb-4">
        <div className="h-4 bg-gray-800 rounded w-full"></div>
        <div className="h-4 bg-gray-800 rounded w-3/4"></div>
      </div>
      
      {/* Price and Button Skeleton */}
      <div className="flex items-center justify-between">
        <div className="h-6 bg-gray-800 rounded w-20"></div>
        <div className="h-10 bg-gray-800 rounded w-24"></div>
      </div>
    </div>
  );
};

export const ProductGridSkeleton = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {Array.from({ length: count }).map((_, index) => (
        <ProductCardSkeleton key={index} />
      ))}
    </div>
  );
};

export const CartItemSkeleton = () => {
  return (
    <div className="flex items-center gap-4 py-4 border-b border-gray-800 animate-pulse">
      {/* Image Skeleton */}
      <div className="w-16 h-16 bg-gray-800 rounded"></div>
      
      {/* Content Skeleton */}
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-800 rounded w-3/4"></div>
        <div className="h-4 bg-gray-800 rounded w-1/2"></div>
      </div>
      
      {/* Quantity Controls Skeleton */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-gray-800 rounded"></div>
        <div className="w-12 h-8 bg-gray-800 rounded"></div>
        <div className="w-8 h-8 bg-gray-800 rounded"></div>
      </div>
    </div>
  );
};

export const PageHeaderSkeleton = () => {
  return (
    <div className="text-center py-20 animate-pulse">
      <div className="h-12 bg-gray-800 rounded w-64 mx-auto mb-4"></div>
      <div className="h-6 bg-gray-800 rounded w-96 mx-auto"></div>
    </div>
  );
};

export const FormSkeleton = () => {
  return (
    <div className="space-y-6 animate-pulse">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="space-y-2">
          <div className="h-4 bg-gray-800 rounded w-24"></div>
          <div className="h-10 bg-gray-800 rounded w-full"></div>
        </div>
      ))}
      <div className="h-12 bg-gray-800 rounded w-full"></div>
    </div>
  );
};

export const TableRowSkeleton = ({ columns = 4 }) => {
  return (
    <tr className="animate-pulse">
      {Array.from({ length: columns }).map((_, index) => (
        <td key={index} className="py-4 px-6">
          <div className="h-4 bg-gray-800 rounded"></div>
        </td>
      ))}
    </tr>
  );
};

export const NavbarSkeleton = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 bg-black/95 backdrop-blur-sm border-b border-white/10 z-50 animate-pulse">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo Skeleton */}
          <div className="h-8 bg-gray-800 rounded w-48"></div>
          
          {/* Menu Items Skeleton */}
          <div className="hidden md:flex items-center space-x-8">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-4 bg-gray-800 rounded w-16"></div>
            ))}
          </div>
          
          {/* Action Buttons Skeleton */}
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gray-800 rounded-full"></div>
            <div className="w-10 h-10 bg-gray-800 rounded-full"></div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default {
  ProductCardSkeleton,
  ProductGridSkeleton,
  CartItemSkeleton,
  PageHeaderSkeleton,
  FormSkeleton,
  TableRowSkeleton,
  NavbarSkeleton
};