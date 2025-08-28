"""
Stripe Payment Service for NitePutter Pro
Real Stripe integration for production checkout
"""

import os
import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from decimal import Decimal
from bson import ObjectId
import logging

from ..database import get_database
from ..models.order import (
    Order, OrderStatus, PaymentStatus, PaymentMethod,
    OrderItem, ShippingInfo, PaymentInfo, Address
)
from ..models.cart import ShoppingCart
from ..services.cart_service import cart_service

logger = logging.getLogger(__name__)

# Initialize Stripe with the API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Webhook endpoint secret for verifying webhooks
WEBHOOK_ENDPOINT_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

class StripeService:
    """Service for handling Stripe payments"""
    
    def __init__(self):
        self.stripe = stripe
        self.webhook_secret = WEBHOOK_ENDPOINT_SECRET
    
    async def create_checkout_session(
        self,
        cart: ShoppingCart,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        shipping_address: Optional[Dict[str, Any]] = None
    ) -> stripe.checkout.Session:
        """
        Create a Stripe Checkout session for the cart
        """
        # Validate cart items first
        issues = await cart_service.validate_cart_items(cart)
        if issues:
            raise ValueError(f"Cart has validation issues: {issues}")
        
        # Reserve stock for checkout
        await cart_service.reserve_cart_stock(cart.session_id)
        
        # Build line items for Stripe
        line_items = []
        for item in cart.items:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.product_name,
                        "description": item.variant_title or "",
                        "images": [item.product_image] if item.product_image else [],
                        "metadata": {
                            "product_id": item.product_id,
                            "sku": item.product_sku
                        }
                    },
                    "unit_amount": int(item.unit_price * 100),  # Convert to cents
                },
                "quantity": item.quantity
            })
        
        # Create checkout session parameters
        session_params = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "cart_id": str(cart.id),
                "session_id": cart.session_id,
                "user_id": cart.user_id or ""
            },
            "shipping_address_collection": {
                "allowed_countries": ["US", "CA"]
            },
            "shipping_options": [
                {
                    "shipping_rate_data": {
                        "type": "fixed_amount",
                        "fixed_amount": {"amount": 999, "currency": "usd"},
                        "display_name": "Standard Shipping",
                        "delivery_estimate": {
                            "minimum": {"unit": "business_day", "value": 5},
                            "maximum": {"unit": "business_day", "value": 7}
                        }
                    }
                },
                {
                    "shipping_rate_data": {
                        "type": "fixed_amount",
                        "fixed_amount": {"amount": 1999, "currency": "usd"},
                        "display_name": "Express Shipping",
                        "delivery_estimate": {
                            "minimum": {"unit": "business_day", "value": 2},
                            "maximum": {"unit": "business_day", "value": 3}
                        }
                    }
                }
            ],
            "allow_promotion_codes": True,
            "automatic_tax": {"enabled": True},
            "invoice_creation": {
                "enabled": True,
                "invoice_data": {
                    "description": "NitePutter Pro Order",
                    "metadata": {"system": "niteputter_pro"},
                    "custom_fields": [
                        {"name": "Order Source", "value": "Website"}
                    ],
                    "rendering_options": {"amount_tax_display": "include_inclusive_tax"}
                }
            }
        }
        
        # Add customer email if provided
        if customer_email:
            session_params["customer_email"] = customer_email
        
        # Add applied coupons as discounts
        if cart.coupons:
            discounts = []
            for coupon in cart.coupons:
                # Create or retrieve Stripe coupon
                stripe_coupon = await self._get_or_create_stripe_coupon(coupon)
                if stripe_coupon:
                    discounts.append({"coupon": stripe_coupon.id})
            
            if discounts:
                session_params["discounts"] = discounts
        
        # Create the session
        try:
            session = self.stripe.checkout.Session.create(**session_params)
            
            # Store checkout session ID in cart for tracking
            db = await get_database()
            await db.carts.update_one(
                {"_id": ObjectId(cart.id)},
                {"$set": {"stripe_checkout_session_id": session.id}}
            )
            
            logger.info(f"Created Stripe checkout session: {session.id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
    
    async def _get_or_create_stripe_coupon(self, coupon_data: Dict[str, Any]) -> Optional[stripe.Coupon]:
        """Get or create a Stripe coupon"""
        try:
            # Try to retrieve existing coupon
            coupon_id = f"niteputter_{coupon_data['code'].lower()}"
            try:
                return self.stripe.Coupon.retrieve(coupon_id)
            except stripe.error.InvalidRequestError:
                pass
            
            # Create new coupon
            coupon_params = {
                "id": coupon_id,
                "name": coupon_data.get("description", coupon_data["code"]),
                "metadata": {"source": "niteputter_pro"}
            }
            
            if coupon_data["type"] == "percentage":
                coupon_params["percent_off"] = float(coupon_data["value"])
            elif coupon_data["type"] == "fixed_amount":
                coupon_params["amount_off"] = int(coupon_data["value"] * 100)
                coupon_params["currency"] = "usd"
            
            return self.stripe.Coupon.create(**coupon_params)
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe coupon: {e}")
            return None
    
    async def handle_checkout_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook for checkout events"""
        try:
            # Verify webhook signature
            if self.webhook_secret:
                event = self.stripe.Webhook.construct_event(
                    payload, sig_header, self.webhook_secret
                )
            else:
                # For testing without webhook secret
                import json
                event = stripe.Event.construct_from(
                    json.loads(payload), stripe.api_key
                )
            
            # Handle the event
            if event.type == 'checkout.session.completed':
                session = event.data.object
                await self._handle_checkout_completed(session)
                
            elif event.type == 'checkout.session.expired':
                session = event.data.object
                await self._handle_checkout_expired(session)
                
            elif event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                await self._handle_payment_succeeded(payment_intent)
                
            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                await self._handle_payment_failed(payment_intent)
            
            return {"status": "success", "event_type": event.type}
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise
    
    async def _handle_checkout_completed(self, session: stripe.checkout.Session):
        """Handle successful checkout completion"""
        logger.info(f"Processing completed checkout session: {session.id}")
        
        db = await get_database()
        
        # Get cart from metadata
        cart_id = session.metadata.get("cart_id")
        if not cart_id:
            logger.error(f"No cart_id in session metadata: {session.id}")
            return
        
        cart_doc = await db.carts.find_one({"_id": ObjectId(cart_id)})
        if not cart_doc:
            logger.error(f"Cart not found: {cart_id}")
            return
        
        cart = ShoppingCart(**cart_doc)
        
        # Create order from cart
        order = await self._create_order_from_session(session, cart)
        
        # Insert order into database
        order_dict = order.model_dump(by_alias=True, exclude_none=True)
        order_dict = self._convert_decimals(order_dict)
        result = await db.orders.insert_one(order_dict)
        order_id = str(result.inserted_id)
        
        # Convert cart to order
        await cart_service.convert_cart_to_order(cart.session_id, order_id)
        
        # Send order confirmation email
        from ..services.email_service import email_service
        if email_service:
            await email_service.send_order_confirmation(
                customer_email=order.customer_email,
                customer_name=f"{session.shipping_details.name}",
                order_data={
                    "order_number": order.order_number,
                    "total": float(order.total),
                    "items": [
                        {
                            "name": item.product_name,
                            "quantity": item.quantity,
                            "price": float(item.price)
                        }
                        for item in order.items
                    ]
                }
            )
        
        logger.info(f"Created order {order.order_number} from checkout session {session.id}")
    
    async def _create_order_from_session(self, session: stripe.checkout.Session, cart: ShoppingCart) -> Order:
        """Create order object from Stripe session"""
        # Get full session details with line items
        full_session = self.stripe.checkout.Session.retrieve(
            session.id,
            expand=["line_items", "customer", "payment_intent"]
        )
        
        # Build order items from cart
        order_items = []
        for cart_item in cart.items:
            order_item = OrderItem(
                product_id=cart_item.product_id,
                product_sku=cart_item.product_sku,
                product_name=cart_item.product_name,
                product_image=cart_item.product_image,
                variant_id=cart_item.variant_id,
                variant_title=cart_item.variant_title,
                price=cart_item.unit_price,
                quantity=cart_item.quantity,
                subtotal=cart_item.subtotal,
                tax_amount=Decimal("0"),  # Will be calculated from Stripe
                discount_amount=cart_item.discount_amount,
                total=cart_item.subtotal
            )
            order_items.append(order_item)
        
        # Build addresses
        shipping = full_session.shipping_details
        billing_address = Address(
            first_name=shipping.name.split()[0] if shipping.name else "",
            last_name=" ".join(shipping.name.split()[1:]) if shipping.name else "",
            street_line1=shipping.address.line1,
            street_line2=shipping.address.line2,
            city=shipping.address.city,
            state_province=shipping.address.state,
            postal_code=shipping.address.postal_code,
            country=shipping.address.country,
            phone=shipping.phone or ""
        )
        shipping_address = billing_address.model_copy()
        
        # Build payment info
        payment_info = PaymentInfo(
            method=PaymentMethod.STRIPE,
            status=PaymentStatus.COMPLETED,
            stripe_payment_intent_id=full_session.payment_intent.id if full_session.payment_intent else None,
            amount=Decimal(str(full_session.amount_total / 100)),
            currency=full_session.currency.upper()
        )
        
        # Build shipping info
        shipping_info = ShippingInfo(
            method="standard",  # Based on selected shipping option
            cost=Decimal(str(full_session.total_details.amount_shipping / 100))
        )
        
        # Create order
        order = Order(
            customer_email=full_session.customer_email or cart.customer_email,
            customer_phone=shipping.phone or "",
            billing_address=billing_address,
            shipping_address=shipping_address,
            items=order_items,
            subtotal=Decimal(str(full_session.amount_subtotal / 100)),
            shipping_total=Decimal(str(full_session.total_details.amount_shipping / 100)),
            tax_total=Decimal(str(full_session.total_details.amount_tax / 100)),
            discount_total=Decimal(str(full_session.total_details.amount_discount / 100)),
            total=Decimal(str(full_session.amount_total / 100)),
            payment=payment_info,
            shipping=shipping_info,
            status=OrderStatus.PROCESSING,
            payment_status=PaymentStatus.COMPLETED,
            processed_at=datetime.now(UTC),
            source="stripe_checkout"
        )
        
        return order
    
    async def _handle_checkout_expired(self, session: stripe.checkout.Session):
        """Handle expired checkout session"""
        logger.info(f"Checkout session expired: {session.id}")
        
        # Release reserved stock
        cart_id = session.metadata.get("cart_id")
        if cart_id:
            db = await get_database()
            cart_doc = await db.carts.find_one({"_id": ObjectId(cart_id)})
            if cart_doc:
                cart = ShoppingCart(**cart_doc)
                
                # Release stock reservations
                for item in cart.items:
                    if item.reserved_until:
                        await db.inventory.update_one(
                            {"product_id": item.product_sku},
                            {"$inc": {"reserved_quantity": -item.quantity}}
                        )
                
                # Clear reservations in cart
                await db.carts.update_one(
                    {"_id": ObjectId(cart_id)},
                    {"$set": {"items.$[].reserved_until": None}}
                )
    
    async def _handle_payment_succeeded(self, payment_intent: stripe.PaymentIntent):
        """Handle successful payment"""
        logger.info(f"Payment succeeded: {payment_intent.id}")
        
        # Update order payment status if needed
        db = await get_database()
        await db.orders.update_one(
            {"payment.stripe_payment_intent_id": payment_intent.id},
            {"$set": {
                "payment_status": PaymentStatus.COMPLETED.value,
                "payment.status": PaymentStatus.COMPLETED.value,
                "payment.paid_at": datetime.now(UTC)
            }}
        )
    
    async def _handle_payment_failed(self, payment_intent: stripe.PaymentIntent):
        """Handle failed payment"""
        logger.info(f"Payment failed: {payment_intent.id}")
        
        # Update order payment status
        db = await get_database()
        await db.orders.update_one(
            {"payment.stripe_payment_intent_id": payment_intent.id},
            {"$set": {
                "payment_status": PaymentStatus.FAILED.value,
                "payment.status": PaymentStatus.FAILED.value
            }}
        )
    
    async def create_refund(self, order_id: str, amount: Optional[Decimal] = None, reason: str = "requested_by_customer") -> stripe.Refund:
        """Create a refund for an order"""
        db = await get_database()
        
        # Get order
        order_doc = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order_doc:
            raise ValueError(f"Order not found: {order_id}")
        
        order = Order(**order_doc)
        
        # Check if order can be refunded
        if not order.can_be_refunded():
            raise ValueError("Order cannot be refunded")
        
        # Determine refund amount
        refund_amount = amount or order.total
        refund_amount_cents = int(refund_amount * 100)
        
        # Create Stripe refund
        try:
            refund = self.stripe.Refund.create(
                payment_intent=order.payment.stripe_payment_intent_id,
                amount=refund_amount_cents,
                reason=reason,
                metadata={
                    "order_id": order_id,
                    "order_number": order.order_number
                }
            )
            
            # Update order with refund info
            refund_info = {
                "refund_id": refund.id,
                "amount": refund_amount,
                "reason": reason,
                "status": refund.status,
                "created_at": datetime.now(UTC),
                "processed_at": datetime.now(UTC) if refund.status == "succeeded" else None
            }
            
            await db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$push": {"refunds": refund_info},
                    "$inc": {"total_refunded": float(refund_amount)},
                    "$set": {
                        "payment_status": PaymentStatus.REFUNDED.value if refund_amount == order.total else PaymentStatus.PARTIALLY_REFUNDED.value
                    }
                }
            )
            
            logger.info(f"Created refund {refund.id} for order {order.order_number}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating refund: {e}")
            raise
    
    def _convert_decimals(self, obj):
        """Convert Decimal values to float for MongoDB"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals(item) for item in obj]
        return obj


# Create singleton instance
stripe_service = StripeService()