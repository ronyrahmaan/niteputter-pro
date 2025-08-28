"""
Email Service for NitePutter Pro
Handles order confirmations, shipping notifications, and customer communications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import aiosmtplib
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@niteputterpro.com')
        self.company_name = "Nite Putter Pro"
        
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using async SMTP"""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.company_name} <{self.from_email}>"
            message['To'] = to_email
            
            # Add text version
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_order_confirmation(
        self, 
        customer_email: str, 
        customer_name: str, 
        order_data: Dict[str, Any]
    ) -> bool:
        """Send order confirmation email"""
        
        order_id = order_data.get('order_id')
        items = order_data.get('items', [])
        total = order_data.get('total', 0)
        
        # Generate order items HTML
        items_html = ""
        for item in items:
            items_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 15px; text-align: left;">
                    <strong>{item.get('name', 'Product')}</strong><br>
                    <small style="color: #666;">SKU: {item.get('id', 'N/A')}</small>
                </td>
                <td style="padding: 15px; text-align: center;">{item.get('quantity', 1)}</td>
                <td style="padding: 15px; text-align: right;">${item.get('price', 0):.2f}</td>
            </tr>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Order Confirmation - {self.company_name}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 300; letter-spacing: 2px;">NITE PUTTER PRO</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Professional Golf Lighting Technology</p>
            </div>
            
            <!-- Content -->
            <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px;">
                <h2 style="color: #0ea5e9; margin-top: 0;">Order Confirmation</h2>
                
                <p>Hi {customer_name},</p>
                
                <p>Thank you for your order! We've received your purchase and are preparing it for shipment.</p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1e293b;">Order Details</h3>
                    <p style="margin: 5px 0;"><strong>Order ID:</strong> {order_id}</p>
                    <p style="margin: 5px 0;"><strong>Order Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {customer_email}</p>
                </div>
                
                <!-- Order Items -->
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background: #1e293b; color: white;">
                            <th style="padding: 15px; text-align: left;">Product</th>
                            <th style="padding: 15px; text-align: center;">Qty</th>
                            <th style="padding: 15px; text-align: right;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr style="background: #f1f5f9; font-weight: bold;">
                            <td colspan="2" style="padding: 15px; text-align: right;">Total:</td>
                            <td style="padding: 15px; text-align: right; color: #0ea5e9;">${total:.2f}</td>
                        </tr>
                    </tbody>
                </table>
                
                <!-- What's Next -->
                <div style="background: #ecfccb; border-left: 4px solid #84cc16; padding: 20px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #365314;">What's Next?</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #4d7c0f;">
                        <li>We'll process your order within 1-2 business days</li>
                        <li>You'll receive a tracking number once your order ships</li>
                        <li>Estimated delivery: 3-5 business days</li>
                    </ul>
                </div>
                
                <!-- Support -->
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #64748b;">Need help? Contact us:</p>
                    <p style="margin: 5px 0;">📞 <a href="tel:469-642-7171" style="color: #0ea5e9; text-decoration: none;">(469) 642-7171</a></p>
                    <p style="margin: 5px 0;">📧 <a href="mailto:niteputterpro@gmail.com" style="color: #0ea5e9; text-decoration: none;">niteputterpro@gmail.com</a></p>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 14px;">
                    <p>Veteran-owned company proudly serving golfers nationwide</p>
                    <p>842 Faith Trail, Heath, TX 75032</p>
                    <p style="margin-top: 15px;">
                        <a href="https://www.facebook.com/profile.php?id=61563079261207" style="color: #0ea5e9; margin: 0 10px;">Facebook</a>
                        <a href="https://www.instagram.com/niteputterpro" style="color: #0ea5e9; margin: 0 10px;">Instagram</a>
                        <a href="https://x.com/niteputterpro?s=21" style="color: #0ea5e9; margin: 0 10px;">Twitter</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text version for email clients that don't support HTML
        text_content = f"""
        NITE PUTTER PRO - Order Confirmation
        
        Hi {customer_name},
        
        Thank you for your order! We've received your purchase and are preparing it for shipment.
        
        Order Details:
        - Order ID: {order_id}
        - Order Date: {datetime.now().strftime('%B %d, %Y')}
        - Email: {customer_email}
        - Total: ${total:.2f}
        
        What's Next?
        - We'll process your order within 1-2 business days
        - You'll receive a tracking number once your order ships
        - Estimated delivery: 3-5 business days
        
        Need help? Contact us:
        Phone: (469) 642-7171
        Email: niteputterpro@gmail.com
        
        Veteran-owned company proudly serving golfers nationwide
        842 Faith Trail, Heath, TX 75032
        """
        
        return await self.send_email(
            to_email=customer_email,
            subject=f"Order Confirmation - {order_id} - Nite Putter Pro",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_shipping_notification(
        self, 
        customer_email: str, 
        customer_name: str, 
        order_id: str, 
        tracking_number: str,
        carrier: str = "USPS"
    ) -> bool:
        """Send shipping notification email"""
        
        tracking_url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
        if carrier.lower() == "ups":
            tracking_url = f"https://www.ups.com/track?loc=en_US&tracknum={tracking_number}"
        elif carrier.lower() == "fedex":
            tracking_url = f"https://www.fedex.com/apps/fedextrack/?tracknumber={tracking_number}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your Order Has Shipped - {self.company_name}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 300; letter-spacing: 2px;">NITE PUTTER PRO</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Order Has Shipped! 📦</p>
            </div>
            
            <!-- Content -->
            <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px;">
                <h2 style="color: #0ea5e9; margin-top: 0;">Package On The Way!</h2>
                
                <p>Hi {customer_name},</p>
                
                <p>Great news! Your Nite Putter Pro order has shipped and is on its way to you.</p>
                
                <div style="background: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                    <h3 style="margin: 0 0 15px 0; color: #065f46;">Tracking Information</h3>
                    <p style="margin: 5px 0;"><strong>Order ID:</strong> {order_id}</p>
                    <p style="margin: 5px 0;"><strong>Carrier:</strong> {carrier}</p>
                    <p style="margin: 5px 0 15px 0;"><strong>Tracking Number:</strong> {tracking_number}</p>
                    
                    <a href="{tracking_url}" 
                       style="display: inline-block; background: #10b981; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 6px; font-weight: bold;">
                        TRACK YOUR PACKAGE
                    </a>
                </div>
                
                <!-- Delivery Info -->
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1e293b;">Delivery Information</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #475569;">
                        <li>Estimated delivery: 3-5 business days</li>
                        <li>Package will require signature upon delivery</li>
                        <li>If you're not home, carrier will attempt redelivery</li>
                        <li>Check tracking for real-time updates</li>
                    </ul>
                </div>
                
                <!-- Getting Started -->
                <div style="background: #fef7cd; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #92400e;">Getting Started with Your Nite Putter</h3>
                    <p style="color: #a16207; margin: 0;">
                        Once your package arrives, check out our quick start guide and video tutorials 
                        to get the most out of your new golf lighting system!
                    </p>
                </div>
                
                <!-- Support -->
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #64748b;">Questions about your order or delivery?</p>
                    <p style="margin: 5px 0;">📞 <a href="tel:469-642-7171" style="color: #0ea5e9; text-decoration: none;">(469) 642-7171</a></p>
                    <p style="margin: 5px 0;">📧 <a href="mailto:niteputterpro@gmail.com" style="color: #0ea5e9; text-decoration: none;">niteputterpro@gmail.com</a></p>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 14px;">
                    <p>Thank you for choosing Nite Putter Pro!</p>
                    <p>842 Faith Trail, Heath, TX 75032</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        NITE PUTTER PRO - Your Order Has Shipped!
        
        Hi {customer_name},
        
        Great news! Your Nite Putter Pro order has shipped and is on its way to you.
        
        Tracking Information:
        - Order ID: {order_id}
        - Carrier: {carrier}
        - Tracking Number: {tracking_number}
        - Track at: {tracking_url}
        
        Delivery Information:
        - Estimated delivery: 3-5 business days
        - Package will require signature upon delivery
        - Check tracking for real-time updates
        
        Questions? Contact us:
        Phone: (469) 642-7171
        Email: niteputterpro@gmail.com
        
        Thank you for choosing Nite Putter Pro!
        """
        
        return await self.send_email(
            to_email=customer_email,
            subject=f"Your Order Has Shipped! - {order_id} - Nite Putter Pro",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_welcome_email(self, customer_email: str, customer_name: str) -> bool:
        """Send welcome email to new customers"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Nite Putter Pro!</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 300; letter-spacing: 2px;">NITE PUTTER PRO</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Welcome to the Future of Golf Practice! ⛳</p>
            </div>
            
            <!-- Content -->
            <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px;">
                <h2 style="color: #0ea5e9; margin-top: 0;">Welcome, {customer_name}!</h2>
                
                <p>Thank you for joining the Nite Putter Pro family! We're excited to help you take your golf game to the next level with our innovative lighting technology.</p>
                
                <!-- What Makes Us Special -->
                <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 20px; margin: 20px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #166534;">Why Golfers Love Nite Putter Pro</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #166534;">
                        <li><strong>Practice Anytime:</strong> Night putting sessions whenever you want</li>
                        <li><strong>Professional Quality:</strong> Used by golf courses nationwide</li>
                        <li><strong>Easy Setup:</strong> Attaches to any putter in seconds</li>
                        <li><strong>Veteran-Owned:</strong> Supporting our military community</li>
                    </ul>
                </div>
                
                <!-- Product Highlights -->
                <div style="background: #fef7cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #92400e;">Our Product Range</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                        <div style="flex: 1; min-width: 150px;">
                            <strong style="color: #a16207;">Basic System ($149)</strong><br>
                            <small style="color: #a16207;">Perfect for casual practice</small>
                        </div>
                        <div style="flex: 1; min-width: 150px;">
                            <strong style="color: #a16207;">Pro System ($299)</strong><br>
                            <small style="color: #a16207;">Advanced features & tracking</small>
                        </div>
                        <div style="flex: 1; min-width: 150px;">
                            <strong style="color: #a16207;">Complete Kit ($499)</strong><br>
                            <small style="color: #a16207;">Everything you need</small>
                        </div>
                    </div>
                </div>
                
                <!-- Call to Action -->
                <div style="text-align: center; margin: 30px 0;">
                    <h3 style="color: #1e293b;">Ready to Transform Your Golf Game?</h3>
                    <a href="https://niteputterpro.com/shop" 
                       style="display: inline-block; background: linear-gradient(135deg, #0ea5e9, #3b82f6); color: white; 
                              padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px;">
                        SHOP NOW
                    </a>
                </div>
                
                <!-- Support -->
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #64748b;">Questions? We're here to help!</p>
                    <p style="margin: 5px 0;">📞 <a href="tel:469-642-7171" style="color: #0ea5e9; text-decoration: none;">(469) 642-7171</a></p>
                    <p style="margin: 5px 0;">📧 <a href="mailto:niteputterpro@gmail.com" style="color: #0ea5e9; text-decoration: none;">niteputterpro@gmail.com</a></p>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 14px;">
                    <p>Veteran-owned company proudly serving golfers nationwide</p>
                    <p>842 Faith Trail, Heath, TX 75032</p>
                    <p style="margin-top: 15px;">
                        <a href="https://www.facebook.com/profile.php?id=61563079261207" style="color: #0ea5e9; margin: 0 10px;">Facebook</a>
                        <a href="https://www.instagram.com/niteputterpro" style="color: #0ea5e9; margin: 0 10px;">Instagram</a>
                        <a href="https://x.com/niteputterpro?s=21" style="color: #0ea5e9; margin: 0 10px;">Twitter</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=customer_email,
            subject="Welcome to Nite Putter Pro - Let's Light Up Your Game! ⛳",
            html_content=html_content
        )

# Global email service instance
email_service = EmailService()