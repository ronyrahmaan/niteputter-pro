from motor.motor_asyncio import AsyncIOMotorDatabase
from models.ecommerce import (
    Coupon, CouponCreate, CouponStatus, CouponUsage, DiscountType,
    ShippingZone, ShippingRate, ShippingMethod, ShippingCalculation,
    TaxRule, TaxClass, TaxCalculation,
    ReturnRequest, ReturnRequestCreate, ReturnRequestUpdate, ReturnStatus,
    Currency, CurrencyRate, CurrencyConversion,
    StockMovement, StockMovementType, LowStockAlert,
    EnhancedOrder, OrderStatus, PaymentStatus, OrderItem,
    GiftCard, GiftCardStatus, GiftCardTransaction
)
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

class EcommerceRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        
        # Collections
        self.coupons_collection = database.coupons
        self.coupon_usage_collection = database.coupon_usage
        self.shipping_zones_collection = database.shipping_zones
        self.shipping_rates_collection = database.shipping_rates
        self.tax_rules_collection = database.tax_rules
        self.return_requests_collection = database.return_requests
        self.currency_rates_collection = database.currency_rates
        self.stock_movements_collection = database.stock_movements
        self.low_stock_alerts_collection = database.low_stock_alerts
        self.enhanced_orders_collection = database.enhanced_orders
        self.gift_cards_collection = database.gift_cards
        self.gift_card_transactions_collection = database.gift_card_transactions
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Coupon indexes
            await self.coupons_collection.create_index("code", unique=True)
            await self.coupons_collection.create_index("status")
            await self.coupons_collection.create_index("valid_from")
            await self.coupons_collection.create_index("valid_until")
            
            await self.coupon_usage_collection.create_index("coupon_id")
            await self.coupon_usage_collection.create_index("user_id")
            await self.coupon_usage_collection.create_index("order_id")
            
            # Shipping indexes
            await self.shipping_zones_collection.create_index("is_active")
            await self.shipping_rates_collection.create_index("zone_id")
            await self.shipping_rates_collection.create_index("method")
            await self.shipping_rates_collection.create_index("is_active")
            
            # Tax indexes
            await self.tax_rules_collection.create_index([("country", 1), ("state", 1)])
            await self.tax_rules_collection.create_index("tax_class")
            await self.tax_rules_collection.create_index("is_active")
            
            # Return indexes
            await self.return_requests_collection.create_index("return_number", unique=True)
            await self.return_requests_collection.create_index("order_id")
            await self.return_requests_collection.create_index("customer_email")
            await self.return_requests_collection.create_index("status")
            
            # Currency indexes
            await self.currency_rates_collection.create_index([("base_currency", 1), ("target_currency", 1)])
            await self.currency_rates_collection.create_index("last_updated")
            
            # Stock movement indexes
            await self.stock_movements_collection.create_index("product_id")
            await self.stock_movements_collection.create_index("movement_type")
            await self.stock_movements_collection.create_index("created_at")
            
            # Alert indexes
            await self.low_stock_alerts_collection.create_index("product_id")
            await self.low_stock_alerts_collection.create_index("priority")
            await self.low_stock_alerts_collection.create_index("acknowledged_by")
            
            # Enhanced order indexes
            await self.enhanced_orders_collection.create_index("order_number", unique=True)
            await self.enhanced_orders_collection.create_index("customer_email")
            await self.enhanced_orders_collection.create_index("user_id")
            await self.enhanced_orders_collection.create_index("order_status")
            await self.enhanced_orders_collection.create_index("created_at")
            
            # Gift card indexes
            await self.gift_cards_collection.create_index("code", unique=True)
            await self.gift_cards_collection.create_index("status")
            await self.gift_cards_collection.create_index("recipient_email")
            
            await self.gift_card_transactions_collection.create_index("gift_card_id")
            await self.gift_card_transactions_collection.create_index("order_id")
            
            logger.info("E-commerce collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create e-commerce indexes: {e}")
    
    # Coupon Management
    async def create_coupon(self, coupon: CouponCreate, created_by: Optional[str] = None) -> Optional[Coupon]:
        """Create new coupon"""
        try:
            coupon_dict = coupon.dict()
            coupon_dict['created_by'] = created_by
            
            coupon_obj = Coupon(**coupon_dict)
            
            await self.coupons_collection.insert_one(coupon_obj.dict())
            return coupon_obj
        except Exception as e:
            logger.error(f"Failed to create coupon: {e}")
            return None
    
    async def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """Get coupon by code"""
        try:
            coupon_doc = await self.coupons_collection.find_one({"code": code.upper()})
            if coupon_doc:
                return Coupon(**coupon_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get coupon by code: {e}")
            return None
    
    async def get_coupons(
        self,
        status: Optional[CouponStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Coupon], int]:
        """Get coupons with filtering and pagination"""
        try:
            query = {}
            if status:
                query["status"] = status
            
            total_count = await self.coupons_collection.count_documents(query)
            
            skip = (page - 1) * page_size
            cursor = self.coupons_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            coupon_docs = await cursor.to_list(length=page_size)
            
            coupons = [Coupon(**doc) for doc in coupon_docs]
            
            return coupons, total_count
            
        except Exception as e:
            logger.error(f"Failed to get coupons: {e}")
            return [], 0
    
    async def validate_coupon(self, code: str, user_id: Optional[str] = None, order_total: float = 0.0) -> Tuple[bool, str, Optional[Coupon]]:
        """Validate coupon for use"""
        try:
            coupon = await self.get_coupon_by_code(code)
            
            if not coupon:
                return False, "Coupon not found", None
            
            # Check status
            if coupon.status != CouponStatus.ACTIVE:
                return False, "Coupon is not active", None
            
            # Check date validity
            now = datetime.utcnow()
            if coupon.valid_from > now:
                return False, "Coupon is not yet valid", None
            
            if coupon.valid_until and coupon.valid_until < now:
                return False, "Coupon has expired", None
            
            # Check usage limits
            if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
                return False, "Coupon usage limit reached", None
            
            # Check per-user usage limit
            if user_id and coupon.usage_limit_per_user:
                user_usage = await self.coupon_usage_collection.count_documents({
                    "coupon_id": coupon.id,
                    "user_id": user_id
                })
                if user_usage >= coupon.usage_limit_per_user:
                    return False, "User usage limit reached for this coupon", None
            
            # Check minimum order amount
            if coupon.minimum_order_amount and order_total < coupon.minimum_order_amount:
                return False, f"Minimum order amount ${coupon.minimum_order_amount:.2f} required", None
            
            # Check customer eligibility
            if coupon.applicable_customers and user_id not in coupon.applicable_customers:
                return False, "Coupon not applicable to this customer", None
            
            # Check new customer requirement
            if coupon.new_customers_only and user_id:
                # Check if user has previous orders
                previous_orders = await self.enhanced_orders_collection.count_documents({
                    "user_id": user_id,
                    "order_status": {"$ne": OrderStatus.CANCELLED.value}
                })
                if previous_orders > 0:
                    return False, "Coupon is only for new customers", None
            
            return True, "Coupon is valid", coupon
            
        except Exception as e:
            logger.error(f"Failed to validate coupon: {e}")
            return False, "Error validating coupon", None
    
    async def use_coupon(self, coupon_id: str, user_id: Optional[str], order_id: str, discount_amount: float) -> bool:
        """Record coupon usage"""
        try:
            # Record usage
            usage = CouponUsage(
                coupon_id=coupon_id,
                coupon_code="",  # Will be filled from coupon data
                user_id=user_id,
                order_id=order_id,
                discount_amount=discount_amount
            )
            
            # Get coupon code
            coupon = await self.coupons_collection.find_one({"id": coupon_id})
            if coupon:
                usage.coupon_code = coupon["code"]
            
            await self.coupon_usage_collection.insert_one(usage.dict())
            
            # Increment usage count
            await self.coupons_collection.update_one(
                {"id": coupon_id},
                {"$inc": {"usage_count": 1}}
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to record coupon usage: {e}")
            return False
    
    async def calculate_discount(self, coupon: Coupon, order_total: float, items: List[Dict[str, Any]] = None) -> float:
        """Calculate discount amount for coupon"""
        try:
            if coupon.discount_type == DiscountType.PERCENTAGE:
                discount = (order_total * coupon.discount_value) / 100
                if coupon.maximum_discount_amount:
                    discount = min(discount, coupon.maximum_discount_amount)
                return discount
            
            elif coupon.discount_type == DiscountType.FIXED_AMOUNT:
                return min(coupon.discount_value, order_total)
            
            elif coupon.discount_type == DiscountType.FREE_SHIPPING:
                # This would be handled separately in shipping calculation
                return 0.0
            
            elif coupon.discount_type == DiscountType.BUY_X_GET_Y:
                # Complex logic for buy X get Y offers
                # Simplified version - would need more sophisticated implementation
                if items and coupon.buy_x_quantity and coupon.get_y_quantity:
                    # Find qualifying items
                    qualifying_quantity = 0
                    for item in items:
                        if not coupon.applicable_products or item.get('product_id') in coupon.applicable_products:
                            qualifying_quantity += item.get('quantity', 0)
                    
                    # Calculate free items
                    free_sets = qualifying_quantity // coupon.buy_x_quantity
                    free_quantity = free_sets * coupon.get_y_quantity
                    
                    # Calculate discount (assuming free item is cheapest)
                    if free_quantity > 0:
                        # Simplified - return average item price * free quantity
                        avg_price = order_total / sum(item.get('quantity', 0) for item in items)
                        return avg_price * free_quantity
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate discount: {e}")
            return 0.0
    
    # Shipping Management
    async def create_shipping_zone(self, zone: ShippingZone) -> Optional[ShippingZone]:
        """Create shipping zone"""
        try:
            await self.shipping_zones_collection.insert_one(zone.dict())
            return zone
        except Exception as e:
            logger.error(f"Failed to create shipping zone: {e}")
            return None
    
    async def create_shipping_rate(self, rate: ShippingRate) -> Optional[ShippingRate]:
        """Create shipping rate"""
        try:
            await self.shipping_rates_collection.insert_one(rate.dict())
            return rate
        except Exception as e:
            logger.error(f"Failed to create shipping rate: {e}")
            return None
    
    async def calculate_shipping(self, country: str, state: str, weight: float, order_value: float) -> List[ShippingCalculation]:
        """Calculate available shipping options"""
        try:
            # Find applicable zones
            zone_query = {
                "$or": [
                    {"countries": country},
                    {"states": state},
                    {"countries": {"$size": 0}, "states": {"$size": 0}}  # Global zone
                ],
                "is_active": True
            }
            
            zones = await self.shipping_zones_collection.find(zone_query).to_list(None)
            
            shipping_options = []
            
            for zone in zones:
                # Find rates for this zone
                rate_query = {
                    "zone_id": zone["id"],
                    "is_active": True
                }
                
                # Apply order value filters
                if order_value > 0:
                    rate_query["$or"] = [
                        {"min_order_value": {"$lte": order_value}},
                        {"min_order_value": None}
                    ]
                
                rates = await self.shipping_rates_collection.find(rate_query).to_list(None)
                
                for rate in rates:
                    # Check weight constraints
                    if rate.get("min_weight") and weight < rate["min_weight"]:
                        continue
                    if rate.get("max_weight") and weight > rate["max_weight"]:
                        continue
                    
                    # Check order value constraints
                    if rate.get("max_order_value") and order_value > rate["max_order_value"]:
                        continue
                    
                    # Calculate shipping cost
                    base_cost = rate["base_rate"]
                    weight_cost = (rate.get("rate_per_kg", 0) * weight) if weight > 0 else 0
                    item_cost = rate.get("rate_per_item", 0)  # Would need item count
                    
                    total_cost = base_cost + weight_cost + item_cost
                    
                    shipping_calc = ShippingCalculation(
                        shipping_method=ShippingMethod(rate["method"]),
                        shipping_zone=zone["name"],
                        rate_name=rate["name"],
                        base_rate=base_cost,
                        weight_charge=weight_cost,
                        item_charge=item_cost,
                        total_shipping_cost=total_cost,
                        estimated_delivery_min=rate["min_delivery_days"],
                        estimated_delivery_max=rate["max_delivery_days"],
                        is_free_shipping=(total_cost == 0)
                    )
                    
                    shipping_options.append(shipping_calc)
            
            return shipping_options
            
        except Exception as e:
            logger.error(f"Failed to calculate shipping: {e}")
            return []
    
    # Tax Management
    async def create_tax_rule(self, tax_rule: TaxRule) -> Optional[TaxRule]:
        """Create tax rule"""
        try:
            await self.tax_rules_collection.insert_one(tax_rule.dict())
            return tax_rule
        except Exception as e:
            logger.error(f"Failed to create tax rule: {e}")
            return None
    
    async def calculate_tax(self, subtotal: float, shipping_cost: float, country: str, state: str = None, postal_code: str = None) -> TaxCalculation:
        """Calculate tax based on location"""
        try:
            # Find applicable tax rules
            query = {
                "country": country,
                "is_active": True
            }
            if state:
                query["$or"] = [
                    {"state": state},
                    {"state": None}
                ]
            
            tax_rules = await self.tax_rules_collection.find(query).sort("priority", -1).to_list(None)
            
            tax_breakdown = []
            total_tax = 0.0
            taxable_amount = subtotal
            
            for rule in tax_rules:
                # Check postal code pattern if specified
                if rule.get("postal_code_pattern") and postal_code:
                    import re
                    if not re.match(rule["postal_code_pattern"], postal_code):
                        continue
                
                # Calculate tax for this rule
                tax_amount = (taxable_amount * rule["tax_rate"]) / 100
                
                # Add shipping tax if applicable
                shipping_tax = 0.0
                if rule.get("applies_to_shipping", False) and shipping_cost > 0:
                    shipping_tax = (shipping_cost * rule["tax_rate"]) / 100
                    tax_amount += shipping_tax
                
                tax_breakdown.append({
                    "rule_name": rule["name"],
                    "tax_rate": rule["tax_rate"],
                    "taxable_amount": taxable_amount,
                    "tax_amount": tax_amount,
                    "shipping_tax": shipping_tax
                })
                
                total_tax += tax_amount
                
                # For compound taxes, add this tax to taxable amount for next rule
                if rule.get("compound_tax", False):
                    taxable_amount += tax_amount
            
            return TaxCalculation(
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_breakdown=tax_breakdown,
                total_tax=total_tax,
                total_amount=subtotal + shipping_cost + total_tax
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate tax: {e}")
            return TaxCalculation(
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total_tax=0.0,
                total_amount=subtotal + shipping_cost
            )
    
    # Return Management
    async def create_return_request(self, return_request: ReturnRequestCreate, user_id: Optional[str] = None) -> Optional[ReturnRequest]:
        """Create return request"""
        try:
            return_dict = return_request.dict()
            return_dict['user_id'] = user_id
            
            return_obj = ReturnRequest(**return_dict)
            
            await self.return_requests_collection.insert_one(return_obj.dict())
            return return_obj
        except Exception as e:
            logger.error(f"Failed to create return request: {e}")
            return None
    
    async def get_return_requests(
        self,
        user_id: Optional[str] = None,
        status: Optional[ReturnStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ReturnRequest], int]:
        """Get return requests with filtering"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if status:
                query["status"] = status
            
            total_count = await self.return_requests_collection.count_documents(query)
            
            skip = (page - 1) * page_size
            cursor = self.return_requests_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            return_docs = await cursor.to_list(length=page_size)
            
            returns = [ReturnRequest(**doc) for doc in return_docs]
            
            return returns, total_count
            
        except Exception as e:
            logger.error(f"Failed to get return requests: {e}")
            return [], 0
    
    # Currency Management
    async def get_exchange_rate(self, from_currency: Currency, to_currency: Currency) -> Optional[float]:
        """Get exchange rate between currencies"""
        try:
            if from_currency == to_currency:
                return 1.0
            
            # Try direct rate
            rate_doc = await self.currency_rates_collection.find_one({
                "base_currency": from_currency,
                "target_currency": to_currency,
                "is_active": True
            })
            
            if rate_doc:
                return rate_doc["exchange_rate"]
            
            # Try inverse rate
            inverse_doc = await self.currency_rates_collection.find_one({
                "base_currency": to_currency,
                "target_currency": from_currency,
                "is_active": True
            })
            
            if inverse_doc:
                return 1.0 / inverse_doc["exchange_rate"]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get exchange rate: {e}")
            return None
    
    async def get_all_exchange_rates(self, base_currency: Currency = Currency.USD) -> Dict[str, float]:
        """Get all exchange rates for a base currency"""
        try:
            rates = {}
            
            # Get all active currency rates
            rate_docs = await self.currency_rates_collection.find({
                "base_currency": base_currency,
                "is_active": True
            }).to_list(None)
            
            for rate_doc in rate_docs:
                rates[rate_doc["target_currency"]] = rate_doc["exchange_rate"]
            
            # Add base currency with rate 1.0
            rates[base_currency.value] = 1.0
            
            # If no rates found, add some default rates for demonstration
            if not rate_docs:
                rates.update({
                    "USD": 1.0,
                    "EUR": 0.85,
                    "GBP": 0.73,
                    "CAD": 1.35,
                    "AUD": 1.45,
                    "JPY": 110.0
                })
            
            return rates
            
        except Exception as e:
            logger.error(f"Failed to get exchange rates: {e}")
            return {base_currency.value: 1.0}
    
    async def convert_currency(self, amount: float, from_currency: Currency, to_currency: Currency) -> Optional[CurrencyConversion]:
        """Convert amount between currencies"""
        try:
            exchange_rate = await self.get_exchange_rate(from_currency, to_currency)
            
            if exchange_rate is None:
                return None
            
            converted_amount = amount * exchange_rate
            
            return CurrencyConversion(
                amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
                exchange_rate=exchange_rate,
                converted_amount=converted_amount
            )
            
        except Exception as e:
            logger.error(f"Failed to convert currency: {e}")
            return None
    
    # Stock Management
    async def record_stock_movement(self, movement: StockMovement) -> bool:
        """Record stock movement"""
        try:
            await self.stock_movements_collection.insert_one(movement.dict())
            
            # Update product stock
            await self.db.products.update_one(
                {"id": movement.product_id},
                {"$set": {"inventory_count": movement.new_stock, "updated_at": datetime.utcnow()}}
            )
            
            # Check for low stock alerts
            await self._check_low_stock_alert(movement.product_id, movement.new_stock)
            
            return True
        except Exception as e:
            logger.error(f"Failed to record stock movement: {e}")
            return False
    
    async def _check_low_stock_alert(self, product_id: str, current_stock: int):
        """Check if low stock alert should be created"""
        try:
            # Get product threshold
            product = await self.db.products.find_one({"id": product_id})
            if not product:
                return
            
            threshold = product.get("low_stock_threshold", 5)
            
            if current_stock <= threshold:
                # Check if alert already exists
                existing_alert = await self.low_stock_alerts_collection.find_one({
                    "product_id": product_id,
                    "acknowledged_by": None
                })
                
                if not existing_alert:
                    # Create new alert
                    alert = LowStockAlert(
                        product_id=product_id,
                        product_name=product.get("name", "Unknown"),
                        current_stock=current_stock,
                        threshold=threshold,
                        suggested_reorder_quantity=max(threshold * 2, 10),
                        priority="high" if current_stock == 0 else "medium" if current_stock <= threshold / 2 else "low"
                    )
                    
                    await self.low_stock_alerts_collection.insert_one(alert.dict())
            
        except Exception as e:
            logger.error(f"Failed to check low stock alert: {e}")
    
    async def get_low_stock_alerts(
        self,
        priority: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[LowStockAlert], int]:
        """Get low stock alerts with filtering"""
        try:
            query = {}
            
            if priority:
                query["priority"] = priority
            
            if acknowledged is not None:
                if acknowledged:
                    query["acknowledged_by"] = {"$ne": None}
                else:
                    query["acknowledged_by"] = None
            
            total_count = await self.low_stock_alerts_collection.count_documents(query)
            
            skip = (page - 1) * page_size
            cursor = self.low_stock_alerts_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            alert_docs = await cursor.to_list(length=page_size)
            
            alerts = [LowStockAlert(**doc) for doc in alert_docs]
            
            return alerts, total_count
            
        except Exception as e:
            logger.error(f"Failed to get low stock alerts: {e}")
            return [], 0
    
    # Gift Card Management
    async def create_gift_card(self, gift_card: GiftCard, created_by: Optional[str] = None) -> Optional[GiftCard]:
        """Create gift card"""
        try:
            gift_card_dict = gift_card.dict()
            gift_card_dict['created_by'] = created_by
            gift_card_dict['current_balance'] = gift_card.initial_amount
            
            gift_card_obj = GiftCard(**gift_card_dict)
            
            await self.gift_cards_collection.insert_one(gift_card_obj.dict())
            return gift_card_obj
        except Exception as e:
            logger.error(f"Failed to create gift card: {e}")
            return None
    
    async def get_gift_card_by_code(self, code: str) -> Optional[GiftCard]:
        """Get gift card by code"""
        try:
            gift_card_doc = await self.gift_cards_collection.find_one({"code": code.upper()})
            if gift_card_doc:
                return GiftCard(**gift_card_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get gift card by code: {e}")
            return None
    
    # Analytics and Reporting
    async def get_ecommerce_stats(self) -> Dict[str, Any]:
        """Get e-commerce statistics"""
        try:
            stats = {}
            
            # Coupon stats
            stats["coupons"] = {
                "total_active": await self.coupons_collection.count_documents({"status": CouponStatus.ACTIVE}),
                "total_used": await self.coupon_usage_collection.count_documents({}),
            }
            
            # Return stats
            stats["returns"] = {
                "total_requests": await self.return_requests_collection.count_documents({}),
                "pending_requests": await self.return_requests_collection.count_documents({"status": ReturnStatus.REQUESTED}),
            }
            
            # Stock alerts
            stats["inventory"] = {
                "active_alerts": await self.low_stock_alerts_collection.count_documents({"acknowledged_by": None}),
            }
            
            # Gift cards
            stats["gift_cards"] = {
                "active_cards": await self.gift_cards_collection.count_documents({"status": GiftCardStatus.ACTIVE}),
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get e-commerce stats: {e}")
            return {}