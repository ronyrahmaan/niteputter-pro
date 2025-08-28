"""
Script to setup initial communication data including FAQ categories, FAQs, and email templates
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from models.communication import EmailTemplateCreate, EmailTemplateType, FAQCreate
from database.communication_repository import CommunicationRepository

load_dotenv(ROOT_DIR / '.env')

# Default FAQ Categories and FAQs
FAQ_DATA = {
    "Product Information": [
        {
            "question": "What is included in the Nite Putter Pro Complete System?",
            "answer": "The Complete System includes our patented POLY LIGHT CASING technology, multi-level drainage system, hardwired 12v lighting system, and professional installation service. Everything you need for a complete nighttime putting experience."
        },
        {
            "question": "How does the Smart Life Bulb System work?",
            "answer": "Our Smart Life Bulb System features Bluetooth-enabled MR16 bulbs that you can control via smartphone app. Customize colors, brightness, and lighting patterns to create the perfect ambiance for your game."
        },
        {
            "question": "What's the difference between the complete system and individual components?",
            "answer": "The Complete System is a comprehensive solution that includes everything needed for installation. Individual components like the Smart Life Bulb System are designed for existing setups or custom installations."
        }
    ],
    "Installation & Setup": [
        {
            "question": "Do I need professional installation?",
            "answer": "We highly recommend professional installation for the Complete System to ensure proper wiring, drainage, and safety compliance. Our certified technicians provide installation service and training."
        },
        {
            "question": "How long does installation typically take?",
            "answer": "Installation time varies based on the complexity of your setup. Typically, a standard residential installation takes 4-6 hours, while commercial installations may require 1-2 days."
        },
        {
            "question": "Can I install the Smart Life Bulb System myself?",
            "answer": "Yes! The Smart Life Bulb System is designed for easy DIY installation. Simply replace your existing MR16 bulbs and download our app to get started."
        }
    ],
    "Technical Support": [
        {
            "question": "What if my lights stop working?",
            "answer": "First, check your power connections and ensure the transformer is functioning. If using Smart Life bulbs, verify your Bluetooth connection. Contact our support team if issues persist - we provide ongoing technical support."
        },
        {
            "question": "Are the lights weatherproof?",
            "answer": "Yes, our lighting systems are designed for outdoor use and are rated IP65 for weather resistance. They can withstand rain, snow, and extreme temperatures."
        },
        {
            "question": "How do I update the Smart Life app?",
            "answer": "App updates are available through your device's app store. We recommend enabling automatic updates to ensure you have the latest features and bug fixes."
        }
    ],
    "Orders & Shipping": [
        {
            "question": "How long does shipping take?",
            "answer": "Standard shipping takes 5-7 business days. Expedited shipping options are available at checkout. Installation service is typically scheduled within 2-3 weeks of product delivery."
        },
        {
            "question": "Can I track my order?",
            "answer": "Yes! Once your order ships, you'll receive a tracking number via email. You can also check your order status by logging into your account."
        },
        {
            "question": "What is your return policy?",
            "answer": "We offer a 30-day return policy for unused products in original packaging. Custom installations may have different return terms. Contact our support team for specific situations."
        }
    ]
}

# Default Email Templates
EMAIL_TEMPLATES = [
    {
        "name": "Welcome Email",
        "template_type": EmailTemplateType.WELCOME,
        "subject": "Welcome to Nite Putter Pro - Let's Light Up Your Game!",
        "html_content": """
        <h1>Welcome to Nite Putter Pro, {{first_name}}!</h1>
        
        <p>Thank you for joining the Nite Putter Pro community. We're excited to help you transform your putting green into a stunning nighttime experience.</p>
        
        <h2>What's Next?</h2>
        <ul>
            <li>Browse our complete product catalog</li>
            <li>Schedule a consultation for custom installations</li>
            <li>Join our newsletter for tips and promotions</li>
        </ul>
        
        <p>If you have any questions, our support team is here to help!</p>
        
        <p>Best regards,<br>The Nite Putter Pro Team</p>
        """,
        "variables": ["first_name"]
    },
    {
        "name": "Order Confirmation",
        "template_type": EmailTemplateType.ORDER_CONFIRMATION,
        "subject": "Order Confirmation #{{order_number}} - Nite Putter Pro",
        "html_content": """
        <h1>Order Confirmation</h1>
        
        <p>Hi {{customer_name}},</p>
        
        <p>Thank you for your order! We've received your order and it's being processed.</p>
        
        <h2>Order Details</h2>
        <p><strong>Order Number:</strong> {{order_number}}</p>
        <p><strong>Order Date:</strong> {{order_date}}</p>
        <p><strong>Total Amount:</strong> ${{total_amount}}</p>
        
        <h2>What Happens Next?</h2>
        <p>You'll receive a shipping confirmation email with tracking information once your order is dispatched. For installation services, our team will contact you within 24 hours to schedule your appointment.</p>
        
        <p>Questions? Reply to this email or contact our support team.</p>
        
        <p>Best regards,<br>The Nite Putter Pro Team</p>
        """,
        "variables": ["customer_name", "order_number", "order_date", "total_amount"]
    },
    {
        "name": "Contact Form Confirmation",
        "template_type": EmailTemplateType.CONTACT_CONFIRMATION,
        "subject": "We've Received Your Message - Nite Putter Pro",
        "html_content": """
        <h1>Thank You for Contacting Us!</h1>
        
        <p>Hi {{first_name}},</p>
        
        <p>We've received your message and our team will respond within 24 hours.</p>
        
        <h2>Your Message:</h2>
        <p><strong>Subject:</strong> {{subject}}</p>
        <p><strong>Message:</strong> {{message}}</p>
        
        <p>If you need immediate assistance, please call us at (469) 642-7171.</p>
        
        <p>Best regards,<br>The Nite Putter Pro Team</p>
        """,
        "variables": ["first_name", "subject", "message"]
    },
    {
        "name": "Support Ticket Reply",
        "template_type": EmailTemplateType.SUPPORT_REPLY,
        "subject": "Re: Support Ticket #{{ticket_number}} - {{subject}}",
        "html_content": """
        <h1>Support Ticket Update</h1>
        
        <p>Hi {{customer_name}},</p>
        
        <p>We've updated your support ticket. Here's the latest response:</p>
        
        <div style="border-left: 4px solid #007bff; padding-left: 16px; margin: 16px 0;">
            {{agent_response}}
        </div>
        
        <p><strong>Ticket #:</strong> {{ticket_number}}</p>
        <p><strong>Status:</strong> {{status}}</p>
        
        <p>You can view the full conversation and reply at: {{ticket_url}}</p>
        
        <p>Best regards,<br>{{agent_name}}<br>Nite Putter Pro Support</p>
        """,
        "variables": ["customer_name", "ticket_number", "subject", "agent_response", "status", "ticket_url", "agent_name"]
    },
    {
        "name": "Newsletter",
        "template_type": EmailTemplateType.NEWSLETTER,
        "subject": "{{newsletter_title}} - Nite Putter Pro Newsletter",
        "html_content": """
        <h1>{{newsletter_title}}</h1>
        
        <p>Hi {{first_name}},</p>
        
        {{newsletter_content}}
        
        <hr>
        
        <p><small>You're receiving this email because you subscribed to our newsletter. 
        <a href="{{unsubscribe_url}}">Unsubscribe here</a> if you no longer wish to receive these emails.</small></p>
        """,
        "variables": ["newsletter_title", "first_name", "newsletter_content", "unsubscribe_url"]
    }
]

async def setup_communication_data():
    """Setup initial communication data"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Initialize communication repository
        comm_repo = CommunicationRepository(db)
        
        # Create indexes
        await comm_repo.create_indexes()
        print("✅ Communication indexes created")
        
        # Create FAQ categories and FAQs
        print("\n📋 Setting up FAQs...")
        faq_count = 0
        
        for category_name, faqs in FAQ_DATA.items():
            # Create category
            category = await comm_repo.create_faq_category(
                name=category_name,
                description=f"Frequently asked questions about {category_name.lower()}",
                sort_order=faq_count
            )
            
            if category:
                print(f"✅ Created FAQ category: {category_name}")
                
                # Create FAQs for this category
                for i, faq_data in enumerate(faqs):
                    faq_create = FAQCreate(
                        category_id=category.id,
                        question=faq_data["question"],
                        answer=faq_data["answer"],
                        sort_order=i
                    )
                    
                    faq = await comm_repo.create_faq(faq_create, created_by="system")
                    if faq:
                        print(f"  ✅ Created FAQ: {faq_data['question'][:50]}...")
                        faq_count += 1
                    else:
                        print(f"  ❌ Failed to create FAQ: {faq_data['question'][:50]}...")
            else:
                print(f"❌ Failed to create category: {category_name}")
        
        print(f"\n📧 Setting up Email Templates...")
        template_count = 0
        
        for template_data in EMAIL_TEMPLATES:
            template_create = EmailTemplateCreate(**template_data)
            
            # Check if template already exists
            existing = await comm_repo.get_email_template(template_data["template_type"])
            if existing:
                print(f"  ⚠️ Template already exists: {template_data['name']}")
                continue
            
            template = await comm_repo.create_email_template(template_create, created_by="system")
            if template:
                print(f"  ✅ Created email template: {template_data['name']}")
                template_count += 1
            else:
                print(f"  ❌ Failed to create template: {template_data['name']}")
        
        # Display summary
        print(f"\n🎉 Communication data setup completed!")
        print(f"📋 FAQs created: {faq_count}")
        print(f"📧 Email templates created: {template_count}")
        
        # Get final stats
        stats = await comm_repo.get_communication_stats()
        print(f"\n📊 Communication System Stats:")
        print(f"  - FAQ Categories: {stats.get('faqs', {}).get('categories', 0)}")
        print(f"  - Total FAQs: {stats.get('faqs', {}).get('total', 0)}")
        print(f"  - Email Templates: {len(await comm_repo.get_email_templates())}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Setting up Communication & Support Data...")
    asyncio.run(setup_communication_data())