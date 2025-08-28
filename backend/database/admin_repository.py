from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from models.admin import (
    AdminCreate, AdminInDB, AdminUpdate, AdminRole, AdminPermission, 
    ROLE_PERMISSIONS, DashboardStats, SalesAnalytics, UserAnalytics,
    RecentActivity, SystemHealth, AdminSettings
)
from models.product import ProductStatus
from auth.auth_handler import auth_handler
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AdminRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.admins_collection = database.admins
        self.activity_logs_collection = database.activity_logs
        self.settings_collection = database.admin_settings
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Admin indexes
            await self.admins_collection.create_index("email", unique=True)
            await self.admins_collection.create_index("username", unique=True)
            await self.admins_collection.create_index("role")
            await self.admins_collection.create_index("is_active")
            await self.admins_collection.create_index("created_at")
            
            # Activity logs indexes
            await self.activity_logs_collection.create_index("type")
            await self.activity_logs_collection.create_index("created_at")
            await self.activity_logs_collection.create_index("admin_id")
            await self.activity_logs_collection.create_index("user_id")
            
            logger.info("Admin collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create admin indexes: {e}")
    
    async def create_admin(self, admin: AdminCreate) -> Optional[AdminInDB]:
        """Create new admin user"""
        try:
            hashed_password = auth_handler.get_password_hash(admin.password)
            admin_dict = admin.dict()
            del admin_dict['password']
            admin_dict['hashed_password'] = hashed_password
            
            # Set permissions based on role if not explicitly provided
            if not admin_dict.get('permissions'):
                admin_dict['permissions'] = ROLE_PERMISSIONS.get(admin.role, [])
            
            admin_in_db = AdminInDB(**admin_dict)
            
            # Convert to dict for MongoDB insertion
            admin_doc = admin_in_db.dict()
            result = await self.admins_collection.insert_one(admin_doc)
            
            if result.inserted_id:
                await self.log_activity(
                    "admin_created",
                    f"New admin created: {admin.email}",
                    admin_id=admin.created_by,
                    related_id=admin_in_db.id
                )
                return await self.get_admin_by_id(admin_in_db.id)
            return None
            
        except DuplicateKeyError as e:
            logger.error(f"Admin creation failed - duplicate key: {e}")
            return None
        except Exception as e:
            logger.error(f"Admin creation failed: {e}")
            return None
    
    async def get_admin_by_id(self, admin_id: str) -> Optional[AdminInDB]:
        """Retrieve admin by ID"""
        try:
            admin_doc = await self.admins_collection.find_one({"id": admin_id})
            if admin_doc:
                return AdminInDB(**admin_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get admin by ID: {e}")
            return None
    
    async def get_admin_by_email(self, email: str) -> Optional[AdminInDB]:
        """Retrieve admin by email"""
        try:
            admin_doc = await self.admins_collection.find_one({"email": email})
            if admin_doc:
                return AdminInDB(**admin_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get admin by email: {e}")
            return None
    
    async def authenticate_admin(self, email: str, password: str) -> Optional[AdminInDB]:
        """Authenticate admin credentials"""
        admin = await self.get_admin_by_email(email)
        if not admin or not admin.is_active:
            return None
            
        if not auth_handler.verify_password(password, admin.hashed_password):
            return None
        
        # Update last login
        await self.admins_collection.update_one(
            {"id": admin.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        await self.log_activity(
            "admin_login",
            f"Admin logged in: {email}",
            admin_id=admin.id
        )
        
        return admin
    
    async def update_admin(self, admin_id: str, admin_update: AdminUpdate, updated_by: Optional[str] = None) -> Optional[AdminInDB]:
        """Update admin information"""
        try:
            update_dict = admin_update.dict(exclude_unset=True)
            
            if 'password' in update_dict:
                update_dict['hashed_password'] = auth_handler.get_password_hash(
                    update_dict['password']
                )
                del update_dict['password']
            
            # Update permissions based on role if role changed
            if 'role' in update_dict:
                update_dict['permissions'] = ROLE_PERMISSIONS.get(update_dict['role'], [])
            
            if update_dict:
                update_dict['updated_at'] = datetime.utcnow()
                update_dict['updated_by'] = updated_by
                
                result = await self.admins_collection.update_one(
                    {"id": admin_id}, 
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    await self.log_activity(
                        "admin_updated",
                        f"Admin updated: {admin_id}",
                        admin_id=updated_by,
                        related_id=admin_id,
                        metadata={"updated_fields": list(update_dict.keys())}
                    )
                    return await self.get_admin_by_id(admin_id)
            
            return await self.get_admin_by_id(admin_id)
            
        except Exception as e:
            logger.error(f"Failed to update admin: {e}")
            return None
    
    async def get_admins(
        self, 
        role: Optional[AdminRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[AdminInDB], int]:
        """Get admins with filtering and pagination"""
        try:
            query = {}
            
            if role:
                query["role"] = role
            if is_active is not None:
                query["is_active"] = is_active
            
            # Get total count
            total_count = await self.admins_collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Execute query
            cursor = self.admins_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            admin_docs = await cursor.to_list(length=page_size)
            
            admins = [AdminInDB(**doc) for doc in admin_docs]
            
            return admins, total_count
            
        except Exception as e:
            logger.error(f"Failed to get admins: {e}")
            return [], 0
    
    async def delete_admin(self, admin_id: str, deleted_by: Optional[str] = None) -> bool:
        """Soft delete admin by setting is_active to False"""
        try:
            result = await self.admins_collection.update_one(
                {"id": admin_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow(), "updated_by": deleted_by}}
            )
            
            if result.modified_count > 0:
                await self.log_activity(
                    "admin_deleted",
                    f"Admin deleted: {admin_id}",
                    admin_id=deleted_by,
                    related_id=admin_id
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete admin: {e}")
            return False
    
    async def has_permission(self, admin_id: str, permission: AdminPermission) -> bool:
        """Check if admin has specific permission"""
        try:
            admin = await self.get_admin_by_id(admin_id)
            if not admin or not admin.is_active:
                return False
            
            return permission in admin.permissions
        except Exception as e:
            logger.error(f"Failed to check admin permission: {e}")
            return False
    
    # Analytics and Dashboard Methods
    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics"""
        try:
            stats = DashboardStats()
            
            # User statistics
            stats.total_users = await self.db.users.count_documents({})
            stats.active_users = await self.db.users.count_documents({"is_active": True})
            
            # Order statistics
            stats.total_orders = await self.db.payment_transactions.count_documents({"payment_status": "paid"})
            
            # Revenue statistics
            revenue_pipeline = [
                {"$match": {"payment_status": "paid"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            revenue_result = await self.db.payment_transactions.aggregate(revenue_pipeline).to_list(1)
            if revenue_result:
                stats.total_revenue = revenue_result[0]["total"]
            
            # Today's statistics
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            stats.orders_today = await self.db.payment_transactions.count_documents({
                "payment_status": "paid",
                "created_at": {"$gte": today, "$lt": tomorrow}
            })
            
            today_revenue_pipeline = [
                {"$match": {
                    "payment_status": "paid",
                    "created_at": {"$gte": today, "$lt": tomorrow}
                }},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            today_revenue_result = await self.db.payment_transactions.aggregate(today_revenue_pipeline).to_list(1)
            if today_revenue_result:
                stats.revenue_today = today_revenue_result[0]["total"]
            
            # Product statistics
            stats.products_count = await self.db.products.count_documents({"status": ProductStatus.ACTIVE})
            stats.low_stock_products = await self.db.products.count_documents({
                "$expr": {"$lte": ["$inventory_count", "$low_stock_threshold"]},
                "inventory_count": {"$gt": 0},
                "status": ProductStatus.ACTIVE
            })
            stats.out_of_stock_products = await self.db.products.count_documents({
                "inventory_count": 0,
                "status": ProductStatus.ACTIVE
            })
            
            # Pending orders (assuming you have order status tracking)
            stats.pending_orders = await self.db.payment_transactions.count_documents({"payment_status": "pending"})
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return DashboardStats()
    
    async def get_sales_analytics(self, days: int = 30) -> SalesAnalytics:
        """Get sales analytics data"""
        try:
            analytics = SalesAnalytics()
            
            # Daily sales for last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            daily_pipeline = [
                {"$match": {
                    "payment_status": "paid",
                    "created_at": {"$gte": start_date}
                }},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "sales": {"$sum": "$amount"},
                    "orders": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            daily_results = await self.db.payment_transactions.aggregate(daily_pipeline).to_list(None)
            analytics.daily_sales = [
                {
                    "date": f"{result['_id']['year']}-{result['_id']['month']:02d}-{result['_id']['day']:02d}",
                    "sales": result["sales"],
                    "orders": result["orders"]
                }
                for result in daily_results
            ]
            
            # Top products
            top_products_pipeline = [
                {"$match": {"payment_status": "paid"}},
                {"$group": {
                    "_id": "$package_id",
                    "total_sales": {"$sum": "$amount"},
                    "total_orders": {"$sum": 1},
                    "total_quantity": {"$sum": "$quantity"}
                }},
                {"$sort": {"total_sales": -1}},
                {"$limit": 10}
            ]
            
            top_products_results = await self.db.payment_transactions.aggregate(top_products_pipeline).to_list(None)
            analytics.top_products = [
                {
                    "product_id": result["_id"],
                    "total_sales": result["total_sales"],
                    "total_orders": result["total_orders"],
                    "total_quantity": result["total_quantity"]
                }
                for result in top_products_results
            ]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get sales analytics: {e}")
            return SalesAnalytics()
    
    async def get_user_analytics(self, days: int = 30) -> UserAnalytics:
        """Get user analytics data"""
        try:
            analytics = UserAnalytics()
            
            # Date ranges
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # New users counts
            analytics.new_users_today = await self.db.users.count_documents({
                "created_at": {"$gte": today}
            })
            
            analytics.new_users_this_week = await self.db.users.count_documents({
                "created_at": {"$gte": week_ago}
            })
            
            analytics.new_users_this_month = await self.db.users.count_documents({
                "created_at": {"$gte": month_ago}
            })
            
            # User growth over time
            start_date = now - timedelta(days=days)
            growth_pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "new_users": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            growth_results = await self.db.users.aggregate(growth_pipeline).to_list(None)
            analytics.user_growth = [
                {
                    "date": f"{result['_id']['year']}-{result['_id']['month']:02d}-{result['_id']['day']:02d}",
                    "new_users": result["new_users"]
                }
                for result in growth_results
            ]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return UserAnalytics()
    
    async def log_activity(
        self, 
        activity_type: str, 
        description: str,
        admin_id: Optional[str] = None,
        user_id: Optional[str] = None,
        related_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log admin activity"""
        try:
            activity = RecentActivity(
                type=activity_type,
                description=description,
                admin_id=admin_id,
                user_id=user_id,
                related_id=related_id,
                metadata=metadata or {}
            )
            
            await self.activity_logs_collection.insert_one(activity.dict())
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    async def get_recent_activities(self, limit: int = 50) -> List[RecentActivity]:
        """Get recent admin activities"""
        try:
            cursor = self.activity_logs_collection.find({}).sort("created_at", -1).limit(limit)
            activity_docs = await cursor.to_list(length=limit)
            
            return [RecentActivity(**doc) for doc in activity_docs]
        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
            return []
    
    async def get_system_health(self) -> SystemHealth:
        """Get system health metrics"""
        try:
            health = SystemHealth()
            
            # Database status check
            try:
                await self.db.command("ping")
                health.database_status = "healthy"
            except:
                health.database_status = "error"
            
            # Active sessions (count active users)
            health.active_sessions = await self.db.users.count_documents({"is_active": True})
            
            # TODO: Add more system metrics like memory usage, disk usage, etc.
            # These would require additional system monitoring tools
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return SystemHealth(database_status="error")
    
    # Settings Management
    async def get_settings(self) -> AdminSettings:
        """Get admin settings"""
        try:
            settings_doc = await self.settings_collection.find_one({"type": "admin_settings"})
            if settings_doc:
                # Remove MongoDB _id field
                if '_id' in settings_doc:
                    del settings_doc['_id']
                if 'type' in settings_doc:
                    del settings_doc['type']
                return AdminSettings(**settings_doc)
            else:
                # Return default settings
                return AdminSettings(
                    contact_email="contact@niteputterpro.com",
                    support_email="support@niteputterpro.com",
                    company_address="842 Faith Trail, Heath, TX 75032",
                    company_phone="(469) 642-7171"
                )
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")
            return AdminSettings(
                contact_email="contact@niteputterpro.com",
                support_email="support@niteputterpro.com",
                company_address="842 Faith Trail, Heath, TX 75032",
                company_phone="(469) 642-7171"
            )
    
    async def update_settings(self, settings: AdminSettings, updated_by: Optional[str] = None) -> bool:
        """Update admin settings"""
        try:
            settings_dict = settings.dict()
            settings_dict['type'] = "admin_settings"
            settings_dict['updated_at'] = datetime.utcnow()
            settings_dict['updated_by'] = updated_by
            
            result = await self.settings_collection.replace_one(
                {"type": "admin_settings"},
                settings_dict,
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                await self.log_activity(
                    "settings_updated",
                    "Admin settings updated",
                    admin_id=updated_by
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return False