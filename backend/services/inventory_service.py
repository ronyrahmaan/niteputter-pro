"""
Inventory Management Service for NitePutter Pro
Handles stock levels, low stock alerts, and inventory tracking
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class InventoryService:
    def __init__(self, db):
        self.db = db
        self.low_stock_threshold = 10  # Default low stock threshold
        self.critical_stock_threshold = 5  # Critical stock level
        
    async def check_stock(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Check if product has sufficient stock"""
        try:
            product = await self.db.products.find_one({"_id": product_id})
            
            if not product:
                return {
                    "available": False,
                    "error": "Product not found",
                    "current_stock": 0
                }
            
            current_stock = product.get("inventory_count", 0)
            is_available = current_stock >= quantity
            
            return {
                "available": is_available,
                "current_stock": current_stock,
                "requested": quantity,
                "shortage": max(0, quantity - current_stock) if not is_available else 0,
                "is_low_stock": current_stock <= self.low_stock_threshold,
                "is_critical": current_stock <= self.critical_stock_threshold
            }
            
        except Exception as e:
            logger.error(f"Error checking stock for product {product_id}: {str(e)}")
            return {
                "available": False,
                "error": str(e),
                "current_stock": 0
            }
    
    async def reserve_stock(
        self, 
        product_id: str, 
        quantity: int, 
        order_id: str,
        duration_minutes: int = 15
    ) -> Dict[str, Any]:
        """Reserve stock for a pending order"""
        try:
            # Check stock availability first
            stock_check = await self.check_stock(product_id, quantity)
            if not stock_check["available"]:
                return {
                    "success": False,
                    "error": "Insufficient stock",
                    "details": stock_check
                }
            
            # Create reservation
            reservation = {
                "product_id": product_id,
                "order_id": order_id,
                "quantity": quantity,
                "reserved_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=duration_minutes),
                "status": "active"
            }
            
            # Insert reservation
            await self.db.inventory_reservations.insert_one(reservation)
            
            # Update available stock (temporarily reduce)
            await self.db.products.update_one(
                {"_id": product_id},
                {"$inc": {"available_stock": -quantity}}
            )
            
            logger.info(f"Reserved {quantity} units of {product_id} for order {order_id}")
            
            return {
                "success": True,
                "reservation_id": str(reservation["_id"]) if "_id" in reservation else order_id,
                "expires_at": reservation["expires_at"],
                "quantity_reserved": quantity
            }
            
        except Exception as e:
            logger.error(f"Error reserving stock: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def confirm_reservation(self, order_id: str) -> Dict[str, Any]:
        """Confirm a stock reservation when payment is completed"""
        try:
            # Find all reservations for this order
            reservations = await self.db.inventory_reservations.find(
                {
                    "order_id": order_id,
                    "status": "active"
                }
            ).to_list(100)
            
            if not reservations:
                return {
                    "success": False,
                    "error": "No active reservations found for this order"
                }
            
            confirmed_items = []
            
            for reservation in reservations:
                # Update inventory count (permanent reduction)
                result = await self.db.products.update_one(
                    {"_id": reservation["product_id"]},
                    {
                        "$inc": {
                            "inventory_count": -reservation["quantity"],
                            "sold_count": reservation["quantity"]
                        }
                    }
                )
                
                # Mark reservation as confirmed
                await self.db.inventory_reservations.update_one(
                    {"_id": reservation["_id"]},
                    {
                        "$set": {
                            "status": "confirmed",
                            "confirmed_at": datetime.utcnow()
                        }
                    }
                )
                
                confirmed_items.append({
                    "product_id": reservation["product_id"],
                    "quantity": reservation["quantity"]
                })
                
                # Check if product needs restocking
                await self._check_restock_needed(reservation["product_id"])
            
            logger.info(f"Confirmed reservations for order {order_id}")
            
            return {
                "success": True,
                "confirmed_items": confirmed_items,
                "order_id": order_id
            }
            
        except Exception as e:
            logger.error(f"Error confirming reservation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def release_reservation(self, order_id: str) -> Dict[str, Any]:
        """Release stock reservation (e.g., order cancelled or expired)"""
        try:
            # Find all reservations for this order
            reservations = await self.db.inventory_reservations.find(
                {
                    "order_id": order_id,
                    "status": "active"
                }
            ).to_list(100)
            
            if not reservations:
                return {
                    "success": True,
                    "message": "No active reservations to release"
                }
            
            released_items = []
            
            for reservation in reservations:
                # Return stock to available pool
                await self.db.products.update_one(
                    {"_id": reservation["product_id"]},
                    {"$inc": {"available_stock": reservation["quantity"]}}
                )
                
                # Mark reservation as released
                await self.db.inventory_reservations.update_one(
                    {"_id": reservation["_id"]},
                    {
                        "$set": {
                            "status": "released",
                            "released_at": datetime.utcnow()
                        }
                    }
                )
                
                released_items.append({
                    "product_id": reservation["product_id"],
                    "quantity": reservation["quantity"]
                })
            
            logger.info(f"Released reservations for order {order_id}")
            
            return {
                "success": True,
                "released_items": released_items,
                "order_id": order_id
            }
            
        except Exception as e:
            logger.error(f"Error releasing reservation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup_expired_reservations(self) -> Dict[str, Any]:
        """Clean up expired reservations (should run periodically)"""
        try:
            # Find expired reservations
            expired = await self.db.inventory_reservations.find(
                {
                    "status": "active",
                    "expires_at": {"$lt": datetime.utcnow()}
                }
            ).to_list(1000)
            
            released_count = 0
            
            for reservation in expired:
                # Release the reservation
                await self.release_reservation(reservation["order_id"])
                released_count += 1
            
            logger.info(f"Cleaned up {released_count} expired reservations")
            
            return {
                "success": True,
                "released_count": released_count
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired reservations: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_stock(
        self, 
        product_id: str, 
        quantity: int, 
        operation: str = "set",
        reason: str = ""
    ) -> Dict[str, Any]:
        """Update product stock levels"""
        try:
            if operation == "set":
                # Set absolute stock level
                update = {"$set": {"inventory_count": quantity}}
            elif operation == "add":
                # Add to existing stock
                update = {"$inc": {"inventory_count": quantity}}
            elif operation == "subtract":
                # Subtract from existing stock
                update = {"$inc": {"inventory_count": -quantity}}
            else:
                return {
                    "success": False,
                    "error": f"Invalid operation: {operation}"
                }
            
            # Update product
            result = await self.db.products.update_one(
                {"_id": product_id},
                update
            )
            
            if result.modified_count == 0:
                return {
                    "success": False,
                    "error": "Product not found or stock unchanged"
                }
            
            # Log stock adjustment
            await self.db.inventory_logs.insert_one({
                "product_id": product_id,
                "operation": operation,
                "quantity": quantity,
                "reason": reason,
                "adjusted_by": "system",
                "adjusted_at": datetime.utcnow()
            })
            
            # Check if restocking is needed
            await self._check_restock_needed(product_id)
            
            # Get updated stock level
            product = await self.db.products.find_one(
                {"_id": product_id},
                {"inventory_count": 1}
            )
            
            return {
                "success": True,
                "product_id": product_id,
                "new_stock_level": product.get("inventory_count", 0),
                "operation": operation,
                "quantity_changed": quantity
            }
            
        except Exception as e:
            logger.error(f"Error updating stock: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_low_stock_products(self, threshold: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of products with low stock"""
        try:
            threshold = threshold or self.low_stock_threshold
            
            products = await self.db.products.find(
                {
                    "inventory_count": {"$lte": threshold},
                    "is_active": True
                }
            ).to_list(100)
            
            low_stock_items = []
            
            for product in products:
                stock_level = product.get("inventory_count", 0)
                
                low_stock_items.append({
                    "product_id": str(product["_id"]),
                    "sku": product.get("sku", ""),
                    "name": product.get("name", ""),
                    "current_stock": stock_level,
                    "threshold": threshold,
                    "is_critical": stock_level <= self.critical_stock_threshold,
                    "reorder_quantity": product.get("reorder_quantity", 50),
                    "supplier": product.get("supplier", "Unknown")
                })
            
            return low_stock_items
            
        except Exception as e:
            logger.error(f"Error getting low stock products: {str(e)}")
            return []
    
    async def _check_restock_needed(self, product_id: str) -> None:
        """Check if a product needs restocking and send alert"""
        try:
            product = await self.db.products.find_one({"_id": product_id})
            if not product:
                return
            
            stock_level = product.get("inventory_count", 0)
            
            # Check if stock is low
            if stock_level <= self.low_stock_threshold:
                alert_level = "critical" if stock_level <= self.critical_stock_threshold else "low"
                
                # Create alert
                await self.db.inventory_alerts.insert_one({
                    "product_id": product_id,
                    "product_name": product.get("name", ""),
                    "sku": product.get("sku", ""),
                    "stock_level": stock_level,
                    "alert_level": alert_level,
                    "threshold": self.low_stock_threshold,
                    "created_at": datetime.utcnow(),
                    "status": "pending"
                })
                
                logger.warning(
                    f"Low stock alert: {product.get('name', 'Product')} "
                    f"(ID: {product_id}) has {stock_level} units remaining"
                )
                
                # TODO: Send email notification to admin
                
        except Exception as e:
            logger.error(f"Error checking restock for product {product_id}: {str(e)}")
    
    async def get_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        try:
            # Get all active products
            products = await self.db.products.find(
                {"is_active": True}
            ).to_list(1000)
            
            total_products = len(products)
            total_stock_value = 0
            out_of_stock = 0
            low_stock = 0
            healthy_stock = 0
            
            category_breakdown = {}
            
            for product in products:
                stock = product.get("inventory_count", 0)
                price = float(product.get("base_price", 0))
                category = product.get("category", "uncategorized")
                
                # Calculate stock value
                stock_value = stock * price
                total_stock_value += stock_value
                
                # Categorize stock levels
                if stock == 0:
                    out_of_stock += 1
                elif stock <= self.low_stock_threshold:
                    low_stock += 1
                else:
                    healthy_stock += 1
                
                # Category breakdown
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        "count": 0,
                        "total_stock": 0,
                        "stock_value": 0
                    }
                
                category_breakdown[category]["count"] += 1
                category_breakdown[category]["total_stock"] += stock
                category_breakdown[category]["stock_value"] += stock_value
            
            return {
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_products": total_products,
                    "total_stock_value": round(total_stock_value, 2),
                    "out_of_stock_count": out_of_stock,
                    "low_stock_count": low_stock,
                    "healthy_stock_count": healthy_stock
                },
                "stock_health": {
                    "out_of_stock_percentage": round((out_of_stock / total_products * 100), 2) if total_products > 0 else 0,
                    "low_stock_percentage": round((low_stock / total_products * 100), 2) if total_products > 0 else 0,
                    "healthy_stock_percentage": round((healthy_stock / total_products * 100), 2) if total_products > 0 else 0
                },
                "category_breakdown": category_breakdown,
                "alerts": await self.get_low_stock_products()
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }