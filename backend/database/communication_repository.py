from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from models.communication import (
    ContactForm, ContactFormCreate, ContactFormUpdate, ContactStatus,
    NewsletterSubscription, NewsletterSubscriptionCreate,
    EmailTemplate, EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateType,
    EmailLog, EmailStatus, SupportTicket, SupportTicketCreate, SupportTicketUpdate,
    TicketMessage, TicketMessageCreate, TicketStatus, FAQ, FAQCreate, FAQUpdate,
    FAQCategory, NotificationTemplate, NotificationQueue
)
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

class CommunicationRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        
        # Collections
        self.contact_forms_collection = database.contact_forms
        self.newsletter_subscriptions_collection = database.newsletter_subscriptions
        self.email_templates_collection = database.email_templates
        self.email_logs_collection = database.email_logs
        self.support_tickets_collection = database.support_tickets
        self.ticket_messages_collection = database.ticket_messages
        self.faq_categories_collection = database.faq_categories
        self.faqs_collection = database.faqs
        self.notification_templates_collection = database.notification_templates
        self.notification_queue_collection = database.notification_queue
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Contact forms indexes
            await self.contact_forms_collection.create_index("email")
            await self.contact_forms_collection.create_index("status")
            await self.contact_forms_collection.create_index("contact_type")
            await self.contact_forms_collection.create_index("created_at")
            await self.contact_forms_collection.create_index("assigned_to")
            
            # Newsletter subscriptions indexes
            await self.newsletter_subscriptions_collection.create_index("email", unique=True)
            await self.newsletter_subscriptions_collection.create_index("is_active")
            await self.newsletter_subscriptions_collection.create_index("created_at")
            
            # Email templates indexes
            await self.email_templates_collection.create_index("template_type")
            await self.email_templates_collection.create_index("is_active")
            
            # Email logs indexes
            await self.email_logs_collection.create_index("recipient_email")
            await self.email_logs_collection.create_index("status")
            await self.email_logs_collection.create_index("template_type")
            await self.email_logs_collection.create_index("created_at")
            await self.email_logs_collection.create_index("tracking_id", unique=True)
            
            # Support tickets indexes
            await self.support_tickets_collection.create_index("ticket_number", unique=True)
            await self.support_tickets_collection.create_index("customer_email")
            await self.support_tickets_collection.create_index("user_id")
            await self.support_tickets_collection.create_index("status")
            await self.support_tickets_collection.create_index("priority")
            await self.support_tickets_collection.create_index("assigned_to")
            await self.support_tickets_collection.create_index("created_at")
            
            # Ticket messages indexes
            await self.ticket_messages_collection.create_index("ticket_id")
            await self.ticket_messages_collection.create_index("created_at")
            await self.ticket_messages_collection.create_index("sender_type")
            
            # FAQ indexes
            await self.faqs_collection.create_index("category_id")
            await self.faqs_collection.create_index("is_active")
            await self.faqs_collection.create_index("sort_order")
            await self.faqs_collection.create_index([("question", "text"), ("answer", "text")])
            
            # FAQ categories indexes
            await self.faq_categories_collection.create_index("sort_order")
            await self.faq_categories_collection.create_index("is_active")
            
            # Notification templates indexes
            await self.notification_templates_collection.create_index("trigger_event")
            await self.notification_templates_collection.create_index("notification_type")
            await self.notification_templates_collection.create_index("is_active")
            
            # Notification queue indexes
            await self.notification_queue_collection.create_index("status")
            await self.notification_queue_collection.create_index("scheduled_at")
            await self.notification_queue_collection.create_index("notification_type")
            
            logger.info("Communication collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create communication indexes: {e}")
    
    # Contact Form Management
    async def create_contact_form(self, contact_form: ContactFormCreate, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[ContactForm]:
        """Create new contact form submission"""
        try:
            contact_obj = ContactForm(
                **contact_form.dict(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            await self.contact_forms_collection.insert_one(contact_obj.dict())
            
            # TODO: Send notification to admin
            # TODO: Send confirmation email to customer
            
            return contact_obj
        except Exception as e:
            logger.error(f"Failed to create contact form: {e}")
            return None
    
    async def get_contact_forms(
        self, 
        status: Optional[ContactStatus] = None,
        assigned_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ContactForm], int]:
        """Get contact forms with filtering and pagination"""
        try:
            query = {}
            
            if status:
                query["status"] = status
            if assigned_to:
                query["assigned_to"] = assigned_to
            
            # Get total count
            total_count = await self.contact_forms_collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Execute query
            cursor = self.contact_forms_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            contact_docs = await cursor.to_list(length=page_size)
            
            contacts = [ContactForm(**doc) for doc in contact_docs]
            
            return contacts, total_count
            
        except Exception as e:
            logger.error(f"Failed to get contact forms: {e}")
            return [], 0
    
    async def update_contact_form(self, contact_id: str, update_data: ContactFormUpdate, updated_by: Optional[str] = None) -> Optional[ContactForm]:
        """Update contact form"""
        try:
            update_dict = update_data.dict(exclude_unset=True)
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                # Set resolved_at if status changed to resolved
                if update_dict.get("status") == ContactStatus.RESOLVED and update_data.status == ContactStatus.RESOLVED:
                    update_dict["resolved_at"] = datetime.utcnow()
                
                result = await self.contact_forms_collection.update_one(
                    {"id": contact_id},
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    contact_doc = await self.contact_forms_collection.find_one({"id": contact_id})
                    if contact_doc:
                        return ContactForm(**contact_doc)
            
            return None
        except Exception as e:
            logger.error(f"Failed to update contact form: {e}")
            return None
    
    # Newsletter Management
    async def subscribe_newsletter(self, subscription: NewsletterSubscriptionCreate, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[NewsletterSubscription]:
        """Subscribe to newsletter"""
        try:
            # Check if already subscribed
            existing = await self.newsletter_subscriptions_collection.find_one({"email": subscription.email})
            if existing:
                # Reactivate if previously unsubscribed
                if not existing.get("is_active"):
                    await self.newsletter_subscriptions_collection.update_one(
                        {"email": subscription.email},
                        {
                            "$set": {
                                "is_active": True,
                                "updated_at": datetime.utcnow(),
                                "unsubscribed_at": None,
                                "interests": subscription.interests
                            }
                        }
                    )
                    updated_doc = await self.newsletter_subscriptions_collection.find_one({"email": subscription.email})
                    return NewsletterSubscription(**updated_doc)
                else:
                    return None  # Already subscribed
            
            subscription_obj = NewsletterSubscription(
                **subscription.dict(),
                ip_address=ip_address,
                user_agent=user_agent,
                double_opt_in_token=str(uuid.uuid4())
            )
            
            await self.newsletter_subscriptions_collection.insert_one(subscription_obj.dict())
            
            # TODO: Send double opt-in email
            
            return subscription_obj
        except Exception as e:
            logger.error(f"Failed to subscribe to newsletter: {e}")
            return None
    
    async def unsubscribe_newsletter(self, email: str = None, token: str = None) -> bool:
        """Unsubscribe from newsletter"""
        try:
            query = {}
            if email:
                query["email"] = email
            elif token:
                query["unsubscribe_token"] = token
            else:
                return False
            
            result = await self.newsletter_subscriptions_collection.update_one(
                query,
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow(),
                        "unsubscribed_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to unsubscribe from newsletter: {e}")
            return False
    
    async def get_newsletter_subscribers(self, active_only: bool = True, page: int = 1, page_size: int = 50) -> Tuple[List[NewsletterSubscription], int]:
        """Get newsletter subscribers"""
        try:
            query = {}
            if active_only:
                query["is_active"] = True
            
            total_count = await self.newsletter_subscriptions_collection.count_documents(query)
            
            skip = (page - 1) * page_size
            cursor = self.newsletter_subscriptions_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            subscription_docs = await cursor.to_list(length=page_size)
            
            subscriptions = [NewsletterSubscription(**doc) for doc in subscription_docs]
            
            return subscriptions, total_count
        except Exception as e:
            logger.error(f"Failed to get newsletter subscribers: {e}")
            return [], 0
    
    # Email Template Management
    async def create_email_template(self, template: EmailTemplateCreate, created_by: Optional[str] = None) -> Optional[EmailTemplate]:
        """Create email template"""
        try:
            template_obj = EmailTemplate(**template.dict(), created_by=created_by)
            
            await self.email_templates_collection.insert_one(template_obj.dict())
            return template_obj
        except Exception as e:
            logger.error(f"Failed to create email template: {e}")
            return None
    
    async def get_email_template(self, template_type: EmailTemplateType) -> Optional[EmailTemplate]:
        """Get email template by type"""
        try:
            template_doc = await self.email_templates_collection.find_one({
                "template_type": template_type,
                "is_active": True
            })
            
            if template_doc:
                return EmailTemplate(**template_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get email template: {e}")
            return None
    
    async def get_email_templates(self, active_only: bool = True) -> List[EmailTemplate]:
        """Get all email templates"""
        try:
            query = {}
            if active_only:
                query["is_active"] = True
            
            cursor = self.email_templates_collection.find(query).sort("created_at", -1)
            template_docs = await cursor.to_list(length=None)
            
            return [EmailTemplate(**doc) for doc in template_docs]
        except Exception as e:
            logger.error(f"Failed to get email templates: {e}")
            return []
    
    # Email Logging
    async def log_email(self, email_log: EmailLog) -> bool:
        """Log email send attempt"""
        try:
            await self.email_logs_collection.insert_one(email_log.dict())
            return True
        except Exception as e:
            logger.error(f"Failed to log email: {e}")
            return False
    
    async def update_email_status(self, tracking_id: str, status: EmailStatus, **kwargs) -> bool:
        """Update email status"""
        try:
            update_data = {"status": status, "updated_at": datetime.utcnow()}
            
            # Add timestamp fields based on status
            if status == EmailStatus.SENT:
                update_data["sent_at"] = datetime.utcnow()
            elif status == EmailStatus.DELIVERED:
                update_data["delivered_at"] = datetime.utcnow()
            elif status == EmailStatus.OPENED:
                update_data["opened_at"] = datetime.utcnow()
            elif status == EmailStatus.CLICKED:
                update_data["clicked_at"] = datetime.utcnow()
            elif status == EmailStatus.BOUNCED:
                update_data["bounced_at"] = datetime.utcnow()
            
            # Add any additional data
            update_data.update(kwargs)
            
            result = await self.email_logs_collection.update_one(
                {"tracking_id": tracking_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update email status: {e}")
            return False
    
    # Support Ticket Management
    async def create_support_ticket(self, ticket: SupportTicketCreate, user_id: Optional[str] = None) -> Optional[SupportTicket]:
        """Create new support ticket"""
        try:
            ticket_obj = SupportTicket(**ticket.dict(), user_id=user_id)
            
            await self.support_tickets_collection.insert_one(ticket_obj.dict())
            
            # TODO: Send confirmation email to customer
            # TODO: Notify admin team
            
            return ticket_obj
        except Exception as e:
            logger.error(f"Failed to create support ticket: {e}")
            return None
    
    async def get_support_tickets(
        self,
        status: Optional[TicketStatus] = None,
        assigned_to: Optional[str] = None,
        customer_email: Optional[str] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[SupportTicket], int]:
        """Get support tickets with filtering"""
        try:
            query = {}
            
            if status:
                query["status"] = status
            if assigned_to:
                query["assigned_to"] = assigned_to
            if customer_email:
                query["customer_email"] = customer_email
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self.support_tickets_collection.count_documents(query)
            
            skip = (page - 1) * page_size
            cursor = self.support_tickets_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            ticket_docs = await cursor.to_list(length=page_size)
            
            tickets = [SupportTicket(**doc) for doc in ticket_docs]
            
            return tickets, total_count
        except Exception as e:
            logger.error(f"Failed to get support tickets: {e}")
            return [], 0
    
    async def get_support_ticket(self, ticket_id: str = None, ticket_number: str = None) -> Optional[SupportTicket]:
        """Get support ticket by ID or number"""
        try:
            query = {}
            if ticket_id:
                query["id"] = ticket_id
            elif ticket_number:
                query["ticket_number"] = ticket_number
            else:
                return None
            
            ticket_doc = await self.support_tickets_collection.find_one(query)
            if ticket_doc:
                return SupportTicket(**ticket_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get support ticket: {e}")
            return None
    
    async def update_support_ticket(self, ticket_id: str, update_data: SupportTicketUpdate) -> Optional[SupportTicket]:
        """Update support ticket"""
        try:
            update_dict = update_data.dict(exclude_unset=True)
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                # Set timestamps based on status changes
                if update_dict.get("status") == TicketStatus.RESOLVED:
                    update_dict["resolved_at"] = datetime.utcnow()
                elif update_dict.get("status") == TicketStatus.CLOSED:
                    update_dict["closed_at"] = datetime.utcnow()
                
                result = await self.support_tickets_collection.update_one(
                    {"id": ticket_id},
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    ticket_doc = await self.support_tickets_collection.find_one({"id": ticket_id})
                    if ticket_doc:
                        return SupportTicket(**ticket_doc)
            
            return None
        except Exception as e:
            logger.error(f"Failed to update support ticket: {e}")
            return None
    
    # Ticket Messages
    async def add_ticket_message(self, ticket_id: str, message: TicketMessageCreate, sender_type: str, sender_id: Optional[str] = None, sender_name: str = "Unknown", sender_email: str = "unknown@example.com") -> Optional[TicketMessage]:
        """Add message to support ticket"""
        try:
            message_obj = TicketMessage(
                ticket_id=ticket_id,
                sender_type=sender_type,
                sender_id=sender_id,
                sender_name=sender_name,
                sender_email=sender_email,
                **message.dict()
            )
            
            await self.ticket_messages_collection.insert_one(message_obj.dict())
            
            # Update ticket timestamps
            update_data = {"updated_at": datetime.utcnow()}
            if sender_type == "customer":
                update_data["last_customer_response"] = datetime.utcnow()
            elif sender_type == "agent":
                update_data["last_agent_response"] = datetime.utcnow()
            
            await self.support_tickets_collection.update_one(
                {"id": ticket_id},
                {"$set": update_data}
            )
            
            return message_obj
        except Exception as e:
            logger.error(f"Failed to add ticket message: {e}")
            return None
    
    async def get_ticket_messages(self, ticket_id: str, include_internal: bool = False) -> List[TicketMessage]:
        """Get messages for a support ticket"""
        try:
            query = {"ticket_id": ticket_id}
            if not include_internal:
                query["is_internal"] = False
            
            cursor = self.ticket_messages_collection.find(query).sort("created_at", 1)
            message_docs = await cursor.to_list(length=None)
            
            return [TicketMessage(**doc) for doc in message_docs]
        except Exception as e:
            logger.error(f"Failed to get ticket messages: {e}")
            return []
    
    # FAQ Management
    async def create_faq_category(self, name: str, description: Optional[str] = None, sort_order: int = 0) -> Optional[FAQCategory]:
        """Create FAQ category"""
        try:
            category = FAQCategory(name=name, description=description, sort_order=sort_order)
            
            await self.faq_categories_collection.insert_one(category.dict())
            return category
        except Exception as e:
            logger.error(f"Failed to create FAQ category: {e}")
            return None
    
    async def get_faq_categories(self, active_only: bool = True) -> List[FAQCategory]:
        """Get FAQ categories"""
        try:
            query = {}
            if active_only:
                query["is_active"] = True
            
            cursor = self.faq_categories_collection.find(query).sort("sort_order", 1)
            category_docs = await cursor.to_list(length=None)
            
            return [FAQCategory(**doc) for doc in category_docs]
        except Exception as e:
            logger.error(f"Failed to get FAQ categories: {e}")
            return []
    
    async def create_faq(self, faq: FAQCreate, created_by: Optional[str] = None) -> Optional[FAQ]:
        """Create FAQ"""
        try:
            faq_obj = FAQ(**faq.dict(), created_by=created_by)
            
            await self.faqs_collection.insert_one(faq_obj.dict())
            return faq_obj
        except Exception as e:
            logger.error(f"Failed to create FAQ: {e}")
            return None
    
    async def get_faqs(self, category_id: Optional[str] = None, active_only: bool = True) -> List[FAQ]:
        """Get FAQs"""
        try:
            query = {}
            if category_id:
                query["category_id"] = category_id
            if active_only:
                query["is_active"] = True
            
            cursor = self.faqs_collection.find(query).sort("sort_order", 1)
            faq_docs = await cursor.to_list(length=None)
            
            return [FAQ(**doc) for doc in faq_docs]
        except Exception as e:
            logger.error(f"Failed to get FAQs: {e}")
            return []
    
    async def search_faqs(self, query: str, limit: int = 10) -> List[FAQ]:
        """Search FAQs by text"""
        try:
            search_results = await self.faqs_collection.find(
                {
                    "$text": {"$search": query},
                    "is_active": True
                },
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit).to_list(length=limit)
            
            return [FAQ(**doc) for doc in search_results]
        except Exception as e:
            logger.error(f"Failed to search FAQs: {e}")
            return []
    
    async def increment_faq_view_count(self, faq_id: str) -> bool:
        """Increment FAQ view count"""
        try:
            result = await self.faqs_collection.update_one(
                {"id": faq_id},
                {"$inc": {"view_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment FAQ view count: {e}")
            return False
    
    # Analytics and Reporting
    async def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        try:
            stats = {}
            
            # Contact form stats
            stats["contact_forms"] = {
                "total": await self.contact_forms_collection.count_documents({}),
                "pending": await self.contact_forms_collection.count_documents({"status": ContactStatus.NEW}),
                "in_progress": await self.contact_forms_collection.count_documents({"status": ContactStatus.IN_PROGRESS}),
                "resolved": await self.contact_forms_collection.count_documents({"status": ContactStatus.RESOLVED})
            }
            
            # Newsletter stats
            stats["newsletter"] = {
                "total_subscribers": await self.newsletter_subscriptions_collection.count_documents({"is_active": True}),
                "total_unsubscribed": await self.newsletter_subscriptions_collection.count_documents({"is_active": False})
            }
            
            # Support ticket stats
            stats["support_tickets"] = {
                "total": await self.support_tickets_collection.count_documents({}),
                "open": await self.support_tickets_collection.count_documents({"status": TicketStatus.OPEN}),
                "in_progress": await self.support_tickets_collection.count_documents({"status": TicketStatus.IN_PROGRESS}),
                "resolved": await self.support_tickets_collection.count_documents({"status": TicketStatus.RESOLVED})
            }
            
            # Email stats
            stats["emails"] = {
                "total_sent": await self.email_logs_collection.count_documents({}),
                "delivered": await self.email_logs_collection.count_documents({"status": EmailStatus.DELIVERED}),
                "opened": await self.email_logs_collection.count_documents({"status": EmailStatus.OPENED}),
                "bounced": await self.email_logs_collection.count_documents({"status": EmailStatus.BOUNCED})
            }
            
            # FAQ stats
            stats["faqs"] = {
                "total": await self.faqs_collection.count_documents({"is_active": True}),
                "categories": await self.faq_categories_collection.count_documents({"is_active": True})
            }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get communication stats: {e}")
            return {}