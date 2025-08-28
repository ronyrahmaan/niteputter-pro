"""
Shopping Cart Service for NitePutter Pro
Persistent cart management with MongoDB
"""

import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from bson import ObjectId
import logging

from ..database import get_database
from ..models.cart import (
    ShoppingCart, CartStatus, CartItem, CartItemStatus,
    CartItemAdd, CartItemUpdate, CartCouponApply,
    AppliedCoupon, CartTotals
)
from ..models.product import Product

logger = logging.getLogger(__name__)

class CartService:
    """Service for managing shopping carts"""
    
    async def get_or_create_cart(self, session_id: str, user_id: Optional[str] = None) -> ShoppingCart:
        """Get existing cart or create new one"""
        db = await get_database()
        
        # Try to find existing cart
        query = {"session_id": session_id, "status": CartStatus.ACTIVE.value}
        cart_doc = await db.carts.find_one(query)
        
        if cart_doc:
            cart = ShoppingCart(**cart_doc)
            
            # If user logged in and cart doesn't have user_id, update it
            if user_id and not cart.user_id:
                cart.user_id = user_id
                await self.merge_user_carts(user_id, session_id)
            
            return cart
        
        # Create new cart
        cart = ShoppingCart(
            session_id=session_id,
            user_id=user_id,
            status=CartStatus.ACTIVE
        )
        
        cart_dict = self._cart_to_dict(cart)
        result = await db.carts.insert_one(cart_dict)
        cart.id = str(result.inserted_id)
        
        logger.info(f"Created new cart with session_id: {session_id}")
        return cart
    
    async def merge_user_carts(self, user_id: str, session_id: str):
        """Merge user's previous carts when they log in"""
        db = await get_database()
        
        # Find user's previous cart
        user_cart = await db.carts.find_one({
            "user_id": user_id,
            "status": CartStatus.ACTIVE.value,
            "session_id": {"$ne": session_id}
        })
        
        if user_cart:
            # Get current session cart
            session_cart = await db.carts.find_one({
                "session_id": session_id,
                "status": CartStatus.ACTIVE.value
            })
            
            if session_cart:
                # Merge items from user cart to session cart
                session_cart_obj = ShoppingCart(**session_cart)
                user_cart_obj = ShoppingCart(**user_cart)
                
                session_cart_obj.merge_with(user_cart_obj)
                
                # Update session cart
                await db.carts.update_one(
                    {"_id": session_cart["_id"]},
                    {"$set": self._cart_to_dict(session_cart_obj)}
                )
                
                # Mark user cart as merged
                await db.carts.update_one(
                    {"_id": user_cart["_id"]},
                    {"$set": {"status": CartStatus.MERGED.value}}
                )
                
                logger.info(f"Merged carts for user: {user_id}")
    
    async def add_to_cart(self, session_id: str, item_data: CartItemAdd, user_id: Optional[str] = None) -> ShoppingCart:
        """Add item to cart"""
        db = await get_database()
        
        # Get product details
        product_doc = await db.products.find_one({"_id": ObjectId(item_data.product_id)})
        if not product_doc:
            raise ValueError(f"Product not found: {item_data.product_id}")
        
        product = Product(**product_doc)
        
        # Check stock availability
        if not product.is_in_stock():
            raise ValueError(f"Product out of stock: {product.name}")
        
        # Get or create cart
        cart = await self.get_or_create_cart(session_id, user_id)
        
        # Add item to cart
        product_data = {
            "id": str(product.id),
            "sku": product.sku,
            "name": product.name,
            "image": product.images[0].url if product.images else None,
            "price": str(product.price),
            "compare_at_price": str(product.compare_at_price) if product.compare_at_price else str(product.price)
        }
        
        cart.add_item(product_data, item_data.quantity)
        
        # Update cart in database
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Added {item_data.quantity}x {product.name} to cart {cart.id}")
        return cart
    
    async def update_cart_item(self, session_id: str, product_id: str, update_data: CartItemUpdate) -> ShoppingCart:
        """Update cart item quantity"""
        db = await get_database()
        
        cart = await self.get_or_create_cart(session_id)
        
        if not cart.update_item_quantity(product_id, update_data.quantity):
            raise ValueError(f"Product not found in cart: {product_id}")
        
        # Update cart in database
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Updated quantity for product {product_id} in cart {cart.id}")
        return cart
    
    async def remove_from_cart(self, session_id: str, product_id: str) -> ShoppingCart:
        """Remove item from cart"""
        db = await get_database()
        
        cart = await self.get_or_create_cart(session_id)
        
        if not cart.remove_item(product_id):
            raise ValueError(f"Product not found in cart: {product_id}")
        
        # Update cart in database
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Removed product {product_id} from cart {cart.id}")
        return cart
    
    async def apply_coupon(self, session_id: str, coupon_code: str) -> ShoppingCart:
        """Apply coupon to cart"""
        db = await get_database()
        
        # Get coupon details
        coupon = await db.coupons.find_one({
            "code": coupon_code,
            "is_active": True,
            "valid_from": {"$lte": datetime.now(UTC)},
            "valid_until": {"$gte": datetime.now(UTC)}
        })
        
        if not coupon:
            raise ValueError(f"Invalid or expired coupon: {coupon_code}")
        
        cart = await self.get_or_create_cart(session_id)
        
        if not cart.apply_coupon(coupon):
            raise ValueError(f"Coupon cannot be applied: {coupon_code}")
        
        # Update cart in database
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Applied coupon {coupon_code} to cart {cart.id}")
        return cart
    
    async def remove_coupon(self, session_id: str, coupon_code: str) -> ShoppingCart:
        """Remove coupon from cart"""
        db = await get_database()
        
        cart = await self.get_or_create_cart(session_id)
        
        if not cart.remove_coupon(coupon_code):
            raise ValueError(f"Coupon not found in cart: {coupon_code}")
        
        # Update cart in database
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Removed coupon {coupon_code} from cart {cart.id}")
        return cart
    
    async def clear_cart(self, session_id: str) -> ShoppingCart:
        """Clear all items from cart"""
        db = await get_database()
        
        cart = await self.get_or_create_cart(session_id)
        cart.clear()
        
        # Update cart in database
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Cleared cart {cart.id}")
        return cart
    
    async def validate_cart_items(self, cart: ShoppingCart) -> List[Dict[str, Any]]:
        """Validate cart items against current product data"""
        db = await get_database()
        issues = []
        
        for item in cart.items:
            product_doc = await db.products.find_one({"_id": ObjectId(item.product_id)})
            
            if not product_doc:
                item.status = CartItemStatus.DISCONTINUED
                issues.append({
                    "product_id": item.product_id,
                    "issue": "Product no longer available",
                    "action": "remove"
                })
                continue
            
            product = Product(**product_doc)
            
            # Check stock
            available_qty = product.get_available_quantity()
            if available_qty == 0:
                item.status = CartItemStatus.OUT_OF_STOCK
                issues.append({
                    "product_id": item.product_id,
                    "issue": "Out of stock",
                    "action": "remove"
                })
            elif available_qty < item.quantity:
                item.status = CartItemStatus.LIMITED_STOCK
                item.stock_available = available_qty
                issues.append({
                    "product_id": item.product_id,
                    "issue": f"Only {available_qty} available",
                    "action": "adjust_quantity",
                    "new_quantity": available_qty
                })
            
            # Check price changes
            if product.price != item.unit_price:
                item.status = CartItemStatus.PRICE_CHANGED
                item.original_price = item.unit_price
                item.unit_price = product.price
                issues.append({
                    "product_id": item.product_id,
                    "issue": f"Price changed from ${item.original_price} to ${product.price}",
                    "action": "update_price"
                })
        
        # Recalculate totals if there were issues
        if issues:
            cart.calculate_totals()
            cart_dict = self._cart_to_dict(cart)
            await db.carts.update_one(
                {"_id": ObjectId(cart.id)},
                {"$set": cart_dict}
            )
        
        return issues
    
    async def reserve_cart_stock(self, session_id: str, duration_minutes: int = 15) -> bool:
        """Reserve stock for cart items during checkout"""
        db = await get_database()
        
        cart = await self.get_or_create_cart(session_id)
        
        # Validate items first
        issues = await self.validate_cart_items(cart)
        if issues:
            return False
        
        # Reserve stock for each item
        cart.reserve_stock(duration_minutes)
        
        # Update inventory reservations
        for item in cart.items:
            await db.inventory.update_one(
                {"product_id": item.product_sku},
                {"$inc": {"reserved_quantity": item.quantity}}
            )
        
        # Update cart
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Reserved stock for cart {cart.id}")
        return True
    
    async def convert_cart_to_order(self, session_id: str, order_id: str):
        """Mark cart as converted to order"""
        db = await get_database()
        
        cart = await self.get_or_create_cart(session_id)
        cart.mark_as_converted(order_id)
        
        # Release reserved stock
        for item in cart.items:
            if item.reserved_until:
                await db.inventory.update_one(
                    {"product_id": item.product_sku},
                    {
                        "$inc": {
                            "reserved_quantity": -item.quantity,
                            "quantity": -item.quantity
                        }
                    }
                )
        
        # Update cart
        cart_dict = self._cart_to_dict(cart)
        await db.carts.update_one(
            {"_id": ObjectId(cart.id)},
            {"$set": cart_dict}
        )
        
        logger.info(f"Converted cart {cart.id} to order {order_id}")
    
    async def cleanup_abandoned_carts(self):
        """Clean up abandoned carts and release reserved stock"""
        db = await get_database()
        
        # Find abandoned carts
        cutoff_time = datetime.now(UTC) - timedelta(hours=1)
        abandoned_carts = await db.carts.find({
            "status": CartStatus.ACTIVE.value,
            "updated_at": {"$lt": cutoff_time}
        }).to_list(None)
        
        for cart_doc in abandoned_carts:
            cart = ShoppingCart(**cart_doc)
            
            # Release reserved stock if expired
            for item in cart.items:
                if item.reserved_until and item.reserved_until < datetime.now(UTC):
                    await db.inventory.update_one(
                        {"product_id": item.product_sku},
                        {"$inc": {"reserved_quantity": -item.quantity}}
                    )
            
            # Mark cart as abandoned
            await db.carts.update_one(
                {"_id": cart_doc["_id"]},
                {"$set": {"status": CartStatus.ABANDONED.value}}
            )
            
            # Send abandonment email if not already sent
            if not cart.abandonment_email_sent and cart.customer_email:
                # Would integrate with email service
                # await email_service.send_cart_abandonment_email(cart)
                await db.carts.update_one(
                    {"_id": cart_doc["_id"]},
                    {"$set": {
                        "abandonment_email_sent": True,
                        "abandonment_email_sent_at": datetime.now(UTC)
                    }}
                )
        
        logger.info(f"Cleaned up {len(abandoned_carts)} abandoned carts")
    
    def _cart_to_dict(self, cart: ShoppingCart) -> Dict[str, Any]:
        """Convert cart to dictionary for MongoDB"""
        cart_dict = cart.model_dump(by_alias=True, exclude_none=True)
        
        # Convert Decimal to float
        def convert_decimals(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            return obj
        
        return convert_decimals(cart_dict)


# Create singleton instance
cart_service = CartService()