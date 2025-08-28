"""
Payment API Routes for NitePutter Pro
Stripe payment endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Header, Body, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
from pydantic import BaseModel, Field
from decimal import Decimal

from ..services.payment_service import payment_service
from ..services.cart_service import cart_service
from ..services.auth_service import auth_service, security
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Request/Response Models
class CreatePaymentIntentRequest(BaseModel):
    """Request model for creating payment intent"""
    amount: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field(default="usd", description="Currency code")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    customer_email: Optional[str] = Field(default=None, description="Customer email")
    shipping: Optional[Dict[str, Any]] = Field(default=None, description="Shipping information")
    description: Optional[str] = Field(default=None, description="Payment description")

class UpdatePaymentIntentRequest(BaseModel):
    """Request model for updating payment intent"""
    amount: Optional[int] = Field(default=None, gt=0, description="New amount in cents")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Updated metadata")
    shipping: Optional[Dict[str, Any]] = Field(default=None, description="Updated shipping")

class CreateRefundRequest(BaseModel):
    """Request model for creating refund"""
    payment_intent_id: str = Field(..., description="Payment intent to refund")
    amount: Optional[int] = Field(default=None, gt=0, description="Amount to refund in cents")
    reason: str = Field(default="requested_by_customer", description="Refund reason")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class CalculateTaxRequest(BaseModel):
    """Request model for tax calculation"""
    amount: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field(default="usd", description="Currency code")
    shipping_address: Dict[str, Any] = Field(..., description="Shipping address")

class CreateCustomerRequest(BaseModel):
    """Request model for creating Stripe customer"""
    email: str = Field(..., description="Customer email")
    name: Optional[str] = Field(default=None, description="Customer name")
    phone: Optional[str] = Field(default=None, description="Customer phone")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


@router.post("/create-payment-intent")
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-Id")
) -> Dict[str, Any]:
    """
    Create a new payment intent for checkout
    
    - **amount**: Amount in cents (e.g., 14999 for $149.99)
    - **currency**: Currency code (default: usd)
    - **metadata**: Additional metadata to attach
    - **customer_email**: Customer email for receipt
    - **shipping**: Shipping information
    - **description**: Payment description
    """
    try:
        # Add session ID to metadata if available
        metadata = request.metadata or {}
        if session_id:
            metadata["session_id"] = session_id
        
        result = await payment_service.create_payment_intent(
            amount=request.amount,
            currency=request.currency,
            metadata=metadata,
            customer_email=request.customer_email,
            shipping=request.shipping,
            description=request.description,
            statement_descriptor="NITEPUTTER PRO"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Payment intent creation failed"))
        
        return {
            "success": True,
            "client_secret": result["client_secret"],
            "payment_intent_id": result["payment_intent_id"],
            "publishable_key": result["publishable_key"],
            "amount": result["amount"],
            "currency": result["currency"]
        }
        
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-payment-intent-from-cart")
async def create_payment_intent_from_cart(
    session_id: str = Header(..., alias="X-Session-Id"),
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create payment intent from current cart
    """
    try:
        # Get cart
        cart = await cart_service.get_or_create_cart(session_id, user_id)
        
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Validate cart items
        issues = await cart_service.validate_cart_items(cart)
        if issues:
            return {
                "success": False,
                "issues": issues,
                "message": "Cart has validation issues"
            }
        
        # Calculate total amount in cents
        amount_cents = int(cart.totals.total * 100)
        
        # Create metadata
        metadata = {
            "cart_id": str(cart.id),
            "session_id": session_id,
            "item_count": cart.totals.item_count,
            "user_id": user_id or ""
        }
        
        # Create payment intent
        result = await payment_service.create_payment_intent(
            amount=amount_cents,
            currency=cart.currency.lower(),
            metadata=metadata,
            customer_email=cart.customer_email,
            description=f"NitePutter Pro Order - {cart.totals.item_count} items",
            statement_descriptor="NITEPUTTER PRO"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Payment intent creation failed"))
        
        # Reserve stock for checkout
        await cart_service.reserve_cart_stock(session_id, settings.RESERVE_STOCK_MINUTES)
        
        return {
            "success": True,
            "client_secret": result["client_secret"],
            "payment_intent_id": result["payment_intent_id"],
            "publishable_key": result["publishable_key"],
            "amount": result["amount"],
            "currency": result["currency"],
            "cart_summary": {
                "items": cart.totals.item_count,
                "subtotal": float(cart.totals.subtotal),
                "tax": float(cart.totals.tax_amount),
                "shipping": float(cart.totals.shipping_estimate),
                "total": float(cart.totals.total)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent from cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update-payment-intent/{payment_intent_id}")
async def update_payment_intent(
    payment_intent_id: str,
    request: UpdatePaymentIntentRequest
) -> Dict[str, Any]:
    """
    Update an existing payment intent
    """
    try:
        result = await payment_service.update_payment_intent(
            payment_intent_id=payment_intent_id,
            amount=request.amount,
            metadata=request.metadata,
            shipping=request.shipping
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating payment intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/confirm-payment/{payment_intent_id}")
async def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
    """
    Confirm payment status
    """
    try:
        result = await payment_service.confirm_payment(payment_intent_id)
        
        return {
            "success": result["success"],
            "status": result.get("status"),
            "payment_intent_id": payment_intent_id,
            "paid": result.get("status") == "succeeded",
            "amount": result.get("amount"),
            "receipt_url": result.get("receipt_url"),
            "card_brand": result.get("card_brand"),
            "card_last4": result.get("card_last4")
        }
        
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-payment/{payment_intent_id}")
async def cancel_payment(
    payment_intent_id: str,
    cancellation_reason: Optional[str] = "requested_by_customer"
) -> Dict[str, Any]:
    """
    Cancel a payment intent
    """
    try:
        result = await payment_service.cancel_payment_intent(
            payment_intent_id=payment_intent_id,
            cancellation_reason=cancellation_reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Cancellation failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error canceling payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-refund")
async def create_refund(request: CreateRefundRequest) -> Dict[str, Any]:
    """
    Create a refund for a payment
    """
    try:
        result = await payment_service.create_refund(
            payment_intent_id=request.payment_intent_id,
            amount=request.amount,
            reason=request.reason,
            metadata=request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Refund creation failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating refund: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-tax")
async def calculate_tax(request: CalculateTaxRequest) -> Dict[str, Any]:
    """
    Calculate tax for an amount and address
    """
    try:
        result = await payment_service.calculate_tax(
            amount=request.amount,
            currency=request.currency,
            shipping_address=request.shipping_address
        )
        
        return {
            "success": result["success"],
            "tax_amount": result["tax_amount"],
            "tax_rate": result["tax_rate"],
            "total_with_tax": request.amount + result["tax_amount"]
        }
        
    except Exception as e:
        logger.error(f"Error calculating tax: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-customer")
async def create_customer(request: CreateCustomerRequest) -> Dict[str, Any]:
    """
    Create a Stripe customer
    """
    try:
        result = await payment_service.create_customer(
            email=request.email,
            name=request.name,
            phone=request.phone,
            metadata=request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Customer creation failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-setup-intent")
async def create_setup_intent(
    customer_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a SetupIntent for saving payment methods
    """
    try:
        result = await payment_service.create_setup_intent(
            customer_id=customer_id,
            usage="off_session"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Setup intent creation failed"))
        
        return {
            "success": True,
            "client_secret": result["client_secret"],
            "setup_intent_id": result["setup_intent_id"],
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
        }
        
    except Exception as e:
        logger.error(f"Error creating setup intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
) -> Dict[str, Any]:
    """
    Handle Stripe webhooks
    """
    try:
        # Get raw body
        payload = await request.body()
        
        # Verify webhook signature
        verification_result = await payment_service.verify_webhook_signature(
            payload=payload,
            sig_header=stripe_signature
        )
        
        if not verification_result["success"]:
            raise HTTPException(status_code=400, detail=verification_result.get("error", "Invalid webhook"))
        
        # Handle the event
        event = verification_result["event"]
        handle_result = await payment_service.handle_webhook_event(event)
        
        logger.info(f"Processed webhook event: {event.type}")
        
        return {"success": True, "event_type": event.type}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        # Return 200 to prevent Stripe from retrying
        return {"success": False, "error": str(e)}


@router.get("/config")
async def get_stripe_config() -> Dict[str, Any]:
    """
    Get Stripe configuration for frontend
    """
    return {
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "supported_countries": ["US", "CA"],
        "supported_payment_methods": ["card"],
        "features": {
            "apple_pay": True,
            "google_pay": True,
            "save_payment_method": True,
            "tax_calculation": settings.ENABLE_TAX_CALCULATION
        }
    }


@router.get("/payment-methods/{customer_id}")
async def list_payment_methods(customer_id: str) -> Dict[str, Any]:
    """
    List saved payment methods for a customer
    """
    try:
        methods = await payment_service.list_payment_methods(customer_id)
        
        return {
            "success": True,
            "payment_methods": methods
        }
        
    except Exception as e:
        logger.error(f"Error listing payment methods: {e}")
        raise HTTPException(status_code=500, detail=str(e))