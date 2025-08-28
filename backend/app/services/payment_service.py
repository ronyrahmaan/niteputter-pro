"""
Stripe Payment Integration Service for NitePutter Pro
Complete payment processing with Stripe API
"""

import stripe
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from decimal import Decimal
import logging
import json

# Import settings
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class PaymentService:
    """Complete Stripe payment processing service"""
    
    @staticmethod
    async def create_payment_intent(
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None,
        customer_email: Optional[str] = None,
        shipping: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        receipt_email: Optional[str] = None,
        statement_descriptor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Stripe PaymentIntent for checkout
        
        Args:
            amount: Amount in cents (e.g., 14999 for $149.99)
            currency: Currency code (default: usd)
            metadata: Additional metadata to attach
            customer_email: Customer email for receipt
            shipping: Shipping information
            description: Payment description
            receipt_email: Email for receipt
            statement_descriptor: Text on bank statement
            
        Returns:
            Dictionary with payment intent details
        """
        try:
            # Build payment intent parameters
            params = {
                "amount": amount,
                "currency": currency,
                "payment_method_types": ["card"],
                "capture_method": "automatic",
                "metadata": metadata or {}
            }
            
            # Add optional parameters
            if customer_email:
                params["receipt_email"] = customer_email or receipt_email
                
            if description:
                params["description"] = description
                
            if statement_descriptor:
                # Max 22 characters for statement descriptor
                params["statement_descriptor"] = statement_descriptor[:22]
                
            if shipping:
                params["shipping"] = {
                    "name": shipping.get("name", ""),
                    "phone": shipping.get("phone", ""),
                    "address": {
                        "line1": shipping.get("line1", ""),
                        "line2": shipping.get("line2", ""),
                        "city": shipping.get("city", ""),
                        "state": shipping.get("state", ""),
                        "postal_code": shipping.get("postal_code", ""),
                        "country": shipping.get("country", "US")
                    }
                }
            
            # Create the payment intent
            intent = stripe.PaymentIntent.create(**params)
            
            logger.info(f"Created payment intent: {intent.id} for amount: ${amount/100:.2f}")
            
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status,
                "publishable_key": STRIPE_PUBLISHABLE_KEY
            }
            
        except stripe.error.CardError as e:
            # Card was declined
            logger.error(f"Card error: {e}")
            return {
                "success": False,
                "error": str(e.user_message),
                "error_type": "card_error",
                "decline_code": e.decline_code
            }
            
        except stripe.error.RateLimitError as e:
            # Too many requests to Stripe API
            logger.error(f"Rate limit error: {e}")
            return {
                "success": False,
                "error": "Too many requests. Please try again later.",
                "error_type": "rate_limit"
            }
            
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied
            logger.error(f"Invalid request: {e}")
            return {
                "success": False,
                "error": "Invalid payment request.",
                "error_type": "invalid_request"
            }
            
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe failed
            logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "error": "Payment authentication failed.",
                "error_type": "authentication_error"
            }
            
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            logger.error(f"API connection error: {e}")
            return {
                "success": False,
                "error": "Network error. Please try again.",
                "error_type": "api_connection_error"
            }
            
        except stripe.error.StripeError as e:
            # Generic Stripe error
            logger.error(f"Stripe error: {e}")
            return {
                "success": False,
                "error": f"Payment processing error: {str(e)}",
                "error_type": "stripe_error"
            }
            
        except Exception as e:
            # Other errors
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": "An unexpected error occurred.",
                "error_type": "unknown_error"
            }
    
    @staticmethod
    async def update_payment_intent(
        payment_intent_id: str,
        amount: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        shipping: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update an existing payment intent"""
        try:
            update_params = {}
            
            if amount is not None:
                update_params["amount"] = amount
                
            if metadata is not None:
                update_params["metadata"] = metadata
                
            if shipping is not None:
                update_params["shipping"] = {
                    "name": shipping.get("name", ""),
                    "phone": shipping.get("phone", ""),
                    "address": {
                        "line1": shipping.get("line1", ""),
                        "line2": shipping.get("line2", ""),
                        "city": shipping.get("city", ""),
                        "state": shipping.get("state", ""),
                        "postal_code": shipping.get("postal_code", ""),
                        "country": shipping.get("country", "US")
                    }
                }
            
            intent = stripe.PaymentIntent.modify(payment_intent_id, **update_params)
            
            logger.info(f"Updated payment intent: {payment_intent_id}")
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "amount": intent.amount,
                "status": intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error updating payment intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm payment was successful
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            Dictionary with payment confirmation details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            is_succeeded = intent.status == "succeeded"
            
            result = {
                "success": is_succeeded,
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "amount_received": intent.amount_received,
                "currency": intent.currency,
                "payment_method": intent.payment_method,
                "created": datetime.fromtimestamp(intent.created, UTC),
            }
            
            # Add charge details if payment succeeded
            if is_succeeded and intent.charges and intent.charges.data:
                charge = intent.charges.data[0]
                result.update({
                    "charge_id": charge.id,
                    "receipt_url": charge.receipt_url,
                    "paid": charge.paid,
                    "refunded": charge.refunded,
                    "card_brand": charge.payment_method_details.card.brand if charge.payment_method_details else None,
                    "card_last4": charge.payment_method_details.card.last4 if charge.payment_method_details else None
                })
            
            logger.info(f"Payment intent {payment_intent_id} status: {intent.status}")
            
            return result
            
        except stripe.error.StripeError as e:
            logger.error(f"Error confirming payment: {e}")
            return {
                "success": False,
                "error": str(e),
                "payment_intent_id": payment_intent_id
            }
    
    @staticmethod
    async def cancel_payment_intent(
        payment_intent_id: str,
        cancellation_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel a payment intent"""
        try:
            params = {}
            if cancellation_reason:
                # Valid reasons: duplicate, fraudulent, requested_by_customer, abandoned
                params["cancellation_reason"] = cancellation_reason
            
            intent = stripe.PaymentIntent.cancel(payment_intent_id, **params)
            
            logger.info(f"Cancelled payment intent: {payment_intent_id}")
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "status": intent.status,
                "cancellation_reason": intent.cancellation_reason
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling payment intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def create_refund(
        payment_intent_id: str,
        amount: Optional[int] = None,
        reason: str = "requested_by_customer",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment
        
        Args:
            payment_intent_id: Payment intent to refund
            amount: Amount in cents to refund (None for full refund)
            reason: Refund reason
            metadata: Additional metadata
            
        Returns:
            Dictionary with refund details
        """
        try:
            refund_params = {
                "payment_intent": payment_intent_id,
                "reason": reason  # duplicate, fraudulent, requested_by_customer
            }
            
            if amount is not None:
                refund_params["amount"] = amount
                
            if metadata:
                refund_params["metadata"] = metadata
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info(f"Created refund {refund.id} for payment {payment_intent_id}")
            
            return {
                "success": True,
                "refund_id": refund.id,
                "amount": refund.amount,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason,
                "receipt_number": refund.receipt_number,
                "created": datetime.fromtimestamp(refund.created, UTC)
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating refund: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def list_payment_methods(customer_id: str) -> List[Dict[str, Any]]:
        """List saved payment methods for a customer"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            methods = []
            for pm in payment_methods.data:
                methods.append({
                    "id": pm.id,
                    "type": pm.type,
                    "card": {
                        "brand": pm.card.brand,
                        "last4": pm.card.last4,
                        "exp_month": pm.card.exp_month,
                        "exp_year": pm.card.exp_year
                    } if pm.card else None,
                    "created": datetime.fromtimestamp(pm.created, UTC)
                })
            
            return methods
            
        except stripe.error.StripeError as e:
            logger.error(f"Error listing payment methods: {e}")
            return []
    
    @staticmethod
    async def create_setup_intent(
        customer_id: Optional[str] = None,
        payment_method_types: List[str] = None,
        usage: str = "off_session"
    ) -> Dict[str, Any]:
        """
        Create a SetupIntent for saving payment methods
        
        Args:
            customer_id: Stripe customer ID
            payment_method_types: List of payment method types
            usage: How the payment method will be used (on_session/off_session)
            
        Returns:
            Dictionary with setup intent details
        """
        try:
            params = {
                "payment_method_types": payment_method_types or ["card"],
                "usage": usage
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            setup_intent = stripe.SetupIntent.create(**params)
            
            logger.info(f"Created setup intent: {setup_intent.id}")
            
            return {
                "success": True,
                "client_secret": setup_intent.client_secret,
                "setup_intent_id": setup_intent.id,
                "status": setup_intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating setup intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def create_customer(
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer"""
        try:
            params = {
                "email": email,
                "metadata": metadata or {}
            }
            
            if name:
                params["name"] = name
                
            if phone:
                params["phone"] = phone
            
            customer = stripe.Customer.create(**params)
            
            logger.info(f"Created Stripe customer: {customer.id}")
            
            return {
                "success": True,
                "customer_id": customer.id,
                "email": customer.email
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating customer: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def update_customer(
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        default_payment_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a Stripe customer"""
        try:
            update_params = {}
            
            if email:
                update_params["email"] = email
            if name:
                update_params["name"] = name
            if phone:
                update_params["phone"] = phone
            if default_payment_method:
                update_params["invoice_settings"] = {
                    "default_payment_method": default_payment_method
                }
            
            customer = stripe.Customer.modify(customer_id, **update_params)
            
            logger.info(f"Updated Stripe customer: {customer_id}")
            
            return {
                "success": True,
                "customer_id": customer.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error updating customer: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def calculate_tax(
        amount: int,
        currency: str = "usd",
        shipping_address: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate tax using Stripe Tax
        
        Args:
            amount: Amount in cents
            currency: Currency code
            shipping_address: Shipping address for tax calculation
            
        Returns:
            Dictionary with tax calculation
        """
        try:
            if not shipping_address:
                return {
                    "success": True,
                    "tax_amount": 0,
                    "tax_rate": 0
                }
            
            # Create a tax calculation
            calculation = stripe.tax.Calculation.create(
                currency=currency,
                line_items=[{
                    "amount": amount,
                    "reference": "niteputter_product",
                    "tax_behavior": "exclusive"
                }],
                customer_details={
                    "address": {
                        "line1": shipping_address.get("line1", ""),
                        "city": shipping_address.get("city", ""),
                        "state": shipping_address.get("state", ""),
                        "postal_code": shipping_address.get("postal_code", ""),
                        "country": shipping_address.get("country", "US")
                    },
                    "address_source": "shipping"
                }
            )
            
            tax_amount = calculation.tax_amount_exclusive
            
            return {
                "success": True,
                "tax_amount": tax_amount,
                "tax_rate": (tax_amount / amount * 100) if amount > 0 else 0,
                "calculation_id": calculation.id
            }
            
        except stripe.error.StripeError as e:
            logger.warning(f"Tax calculation error: {e}")
            # Return 0 tax if calculation fails
            return {
                "success": True,
                "tax_amount": 0,
                "tax_rate": 0
            }
    
    @staticmethod
    async def verify_webhook_signature(
        payload: bytes,
        sig_header: str
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            sig_header: Stripe signature header
            
        Returns:
            Parsed webhook event or error
        """
        try:
            if STRIPE_WEBHOOK_SECRET:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, STRIPE_WEBHOOK_SECRET
                )
            else:
                # For testing without webhook secret
                event = stripe.Event.construct_from(
                    json.loads(payload), stripe.api_key
                )
            
            return {
                "success": True,
                "event": event
            }
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return {
                "success": False,
                "error": "Invalid payload"
            }
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return {
                "success": False,
                "error": "Invalid signature"
            }
    
    @staticmethod
    async def handle_webhook_event(event: stripe.Event) -> Dict[str, Any]:
        """
        Handle different webhook events
        
        Args:
            event: Stripe webhook event
            
        Returns:
            Processing result
        """
        event_handlers = {
            "payment_intent.succeeded": PaymentService._handle_payment_succeeded,
            "payment_intent.payment_failed": PaymentService._handle_payment_failed,
            "payment_intent.canceled": PaymentService._handle_payment_canceled,
            "charge.refunded": PaymentService._handle_charge_refunded,
            "customer.created": PaymentService._handle_customer_created,
            "customer.deleted": PaymentService._handle_customer_deleted
        }
        
        handler = event_handlers.get(event.type)
        if handler:
            return await handler(event.data.object)
        
        logger.info(f"Unhandled webhook event type: {event.type}")
        return {"success": True, "message": f"Event {event.type} received"}
    
    @staticmethod
    async def _handle_payment_succeeded(payment_intent: stripe.PaymentIntent) -> Dict[str, Any]:
        """Handle successful payment webhook"""
        logger.info(f"Payment succeeded: {payment_intent.id}")
        
        # Update order status in database
        # This would integrate with order service
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "amount": payment_intent.amount
        }
    
    @staticmethod
    async def _handle_payment_failed(payment_intent: stripe.PaymentIntent) -> Dict[str, Any]:
        """Handle failed payment webhook"""
        logger.info(f"Payment failed: {payment_intent.id}")
        
        # Update order status in database
        # Send failure notification
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "failure_message": payment_intent.last_payment_error.message if payment_intent.last_payment_error else None
        }
    
    @staticmethod
    async def _handle_payment_canceled(payment_intent: stripe.PaymentIntent) -> Dict[str, Any]:
        """Handle canceled payment webhook"""
        logger.info(f"Payment canceled: {payment_intent.id}")
        
        # Release reserved inventory
        # Update order status
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id
        }
    
    @staticmethod
    async def _handle_charge_refunded(charge: stripe.Charge) -> Dict[str, Any]:
        """Handle refund webhook"""
        logger.info(f"Charge refunded: {charge.id}")
        
        # Update order refund status
        # Update inventory if needed
        
        return {
            "success": True,
            "charge_id": charge.id,
            "amount_refunded": charge.amount_refunded
        }
    
    @staticmethod
    async def _handle_customer_created(customer: stripe.Customer) -> Dict[str, Any]:
        """Handle customer created webhook"""
        logger.info(f"Customer created: {customer.id}")
        
        # Store customer ID in database
        
        return {
            "success": True,
            "customer_id": customer.id
        }
    
    @staticmethod
    async def _handle_customer_deleted(customer: stripe.Customer) -> Dict[str, Any]:
        """Handle customer deleted webhook"""
        logger.info(f"Customer deleted: {customer.id}")
        
        # Update customer status in database
        
        return {
            "success": True,
            "customer_id": customer.id
        }


# Export singleton instance
payment_service = PaymentService()