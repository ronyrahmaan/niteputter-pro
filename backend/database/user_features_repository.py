from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user_features import (
    WishlistItem, WishlistResponse, Address, AddressCreate, AddressUpdate,
    UserPreferences, UserPreferencesUpdate, UserActivity, ActivityType,
    ProductReview, ProductReviewCreate, ProductReviewUpdate, ProductReviewResponse,
    UserProfileStats, SearchHistory, PopularSearch
)
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class UserFeaturesRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.users_collection = database.users
        self.wishlists_collection = database.wishlists
        self.addresses_collection = database.addresses
        self.preferences_collection = database.user_preferences
        self.activities_collection = database.user_activities
        self.reviews_collection = database.product_reviews
        self.search_history_collection = database.search_history
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Wishlist indexes
            await self.wishlists_collection.create_index([("user_id", 1), ("product_id", 1)], unique=True)
            await self.wishlists_collection.create_index("user_id")
            await self.wishlists_collection.create_index("added_at")
            
            # Address indexes
            await self.addresses_collection.create_index("user_id")
            await self.addresses_collection.create_index([("user_id", 1), ("is_primary", 1)])
            
            # Preferences indexes
            await self.preferences_collection.create_index("user_id", unique=True)
            
            # Activity indexes
            await self.activities_collection.create_index("user_id")
            await self.activities_collection.create_index("activity_type")
            await self.activities_collection.create_index("created_at")
            await self.activities_collection.create_index([("user_id", 1), ("created_at", -1)])
            
            # Review indexes
            await self.reviews_collection.create_index("product_id")
            await self.reviews_collection.create_index("user_id")
            await self.reviews_collection.create_index("is_approved")
            await self.reviews_collection.create_index("rating")
            await self.reviews_collection.create_index("created_at")
            
            # Search history indexes
            await self.search_history_collection.create_index("user_id")
            await self.search_history_collection.create_index("query")
            await self.search_history_collection.create_index("created_at")
            
            logger.info("User features collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create user features indexes: {e}")
    
    # Wishlist Management
    async def add_to_wishlist(self, user_id: str, product_id: str, notes: Optional[str] = None) -> bool:
        """Add product to user's wishlist"""
        try:
            wishlist_item = WishlistItem(product_id=product_id, notes=notes)
            wishlist_doc = {
                "user_id": user_id,
                **wishlist_item.dict()
            }
            
            await self.wishlists_collection.insert_one(wishlist_doc)
            
            # Log activity
            await self.log_user_activity(
                user_id, 
                ActivityType.WISHLIST_ADD, 
                f"Added product to wishlist",
                {"product_id": product_id}
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to add to wishlist: {e}")
            return False
    
    async def remove_from_wishlist(self, user_id: str, product_id: str) -> bool:
        """Remove product from user's wishlist"""
        try:
            result = await self.wishlists_collection.delete_one({
                "user_id": user_id,
                "product_id": product_id
            })
            
            if result.deleted_count > 0:
                await self.log_user_activity(
                    user_id,
                    ActivityType.WISHLIST_REMOVE,
                    f"Removed product from wishlist",
                    {"product_id": product_id}
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove from wishlist: {e}")
            return False
    
    async def get_user_wishlist(self, user_id: str) -> List[WishlistResponse]:
        """Get user's wishlist with product details"""
        try:
            # Aggregation pipeline to join with products
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$lookup": {
                    "from": "products",
                    "localField": "product_id",
                    "foreignField": "id",
                    "as": "product"
                }},
                {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},
                {"$sort": {"added_at": -1}}
            ]
            
            cursor = self.wishlists_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            wishlist_items = []
            for result in results:
                product = result.get("product", {})
                
                wishlist_item = WishlistResponse(
                    id=result["id"],
                    product_id=result["product_id"],
                    product_name=product.get("name"),
                    product_price=product.get("base_price"),
                    product_image=product.get("images", [{}])[0].get("url") if product.get("images") else None,
                    added_at=result["added_at"],
                    notes=result.get("notes")
                )
                wishlist_items.append(wishlist_item)
            
            return wishlist_items
        except Exception as e:
            logger.error(f"Failed to get user wishlist: {e}")
            return []
    
    async def is_in_wishlist(self, user_id: str, product_id: str) -> bool:
        """Check if product is in user's wishlist"""
        try:
            count = await self.wishlists_collection.count_documents({
                "user_id": user_id,
                "product_id": product_id
            })
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check wishlist status: {e}")
            return False
    
    # Address Management
    async def add_address(self, user_id: str, address: AddressCreate) -> Optional[Address]:
        """Add new address for user"""
        try:
            # If this is set as primary, unset other primary addresses
            if address.is_primary:
                await self.addresses_collection.update_many(
                    {"user_id": user_id, "is_primary": True},
                    {"$set": {"is_primary": False, "updated_at": datetime.utcnow()}}
                )
            
            address_obj = Address(**address.dict())
            address_doc = {
                "user_id": user_id,
                **address_obj.dict()
            }
            
            await self.addresses_collection.insert_one(address_doc)
            
            await self.log_user_activity(
                user_id,
                ActivityType.ADDRESS_ADD,
                f"Added new {address.type} address",
                {"address_type": address.type}
            )
            
            return address_obj
        except Exception as e:
            logger.error(f"Failed to add address: {e}")
            return None
    
    async def update_address(self, user_id: str, address_id: str, address_update: AddressUpdate) -> Optional[Address]:
        """Update user address"""
        try:
            update_dict = address_update.dict(exclude_unset=True)
            
            # If setting as primary, unset other primary addresses
            if update_dict.get("is_primary"):
                await self.addresses_collection.update_many(
                    {"user_id": user_id, "is_primary": True, "id": {"$ne": address_id}},
                    {"$set": {"is_primary": False, "updated_at": datetime.utcnow()}}
                )
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                result = await self.addresses_collection.update_one(
                    {"user_id": user_id, "id": address_id},
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    await self.log_user_activity(
                        user_id,
                        ActivityType.ADDRESS_UPDATE,
                        f"Updated address",
                        {"address_id": address_id}
                    )
                    
                    # Return updated address
                    address_doc = await self.addresses_collection.find_one({
                        "user_id": user_id, 
                        "id": address_id
                    })
                    if address_doc:
                        return Address(**address_doc)
            
            return None
        except Exception as e:
            logger.error(f"Failed to update address: {e}")
            return None
    
    async def delete_address(self, user_id: str, address_id: str) -> bool:
        """Delete user address"""
        try:
            result = await self.addresses_collection.delete_one({
                "user_id": user_id,
                "id": address_id
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete address: {e}")
            return False
    
    async def get_user_addresses(self, user_id: str) -> List[Address]:
        """Get all user addresses"""
        try:
            cursor = self.addresses_collection.find({"user_id": user_id}).sort("created_at", -1)
            address_docs = await cursor.to_list(length=None)
            
            return [Address(**doc) for doc in address_docs]
        except Exception as e:
            logger.error(f"Failed to get user addresses: {e}")
            return []
    
    async def get_primary_address(self, user_id: str) -> Optional[Address]:
        """Get user's primary address"""
        try:
            address_doc = await self.addresses_collection.find_one({
                "user_id": user_id,
                "is_primary": True
            })
            
            if address_doc:
                return Address(**address_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get primary address: {e}")
            return None
    
    # User Preferences Management
    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences (create default if not exists)"""
        try:
            prefs_doc = await self.preferences_collection.find_one({"user_id": user_id})
            
            if prefs_doc:
                return UserPreferences(**prefs_doc)
            else:
                # Create default preferences
                default_prefs = UserPreferences(user_id=user_id)
                await self.preferences_collection.insert_one(default_prefs.dict())
                return default_prefs
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            # Return default preferences on error
            return UserPreferences(user_id=user_id)
    
    async def update_user_preferences(self, user_id: str, preferences_update: UserPreferencesUpdate) -> bool:
        """Update user preferences"""
        try:
            update_dict = preferences_update.dict(exclude_unset=True)
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                result = await self.preferences_collection.update_one(
                    {"user_id": user_id},
                    {"$set": update_dict},
                    upsert=True
                )
                
                return result.upserted_id is not None or result.modified_count > 0
            
            return True
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False
    
    # User Activity Tracking
    async def log_user_activity(
        self, 
        user_id: str, 
        activity_type: ActivityType, 
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Log user activity"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                metadata=metadata or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            await self.activities_collection.insert_one(activity.dict())
            return True
        except Exception as e:
            logger.error(f"Failed to log user activity: {e}")
            return False
    
    async def get_user_activities(
        self, 
        user_id: str, 
        limit: int = 50,
        activity_types: Optional[List[ActivityType]] = None
    ) -> List[UserActivity]:
        """Get user activities"""
        try:
            query = {"user_id": user_id}
            
            if activity_types:
                query["activity_type"] = {"$in": activity_types}
            
            cursor = self.activities_collection.find(query).sort("created_at", -1).limit(limit)
            activity_docs = await cursor.to_list(length=limit)
            
            return [UserActivity(**doc) for doc in activity_docs]
        except Exception as e:
            logger.error(f"Failed to get user activities: {e}")
            return []
    
    # Product Reviews
    async def create_review(self, user_id: str, review: ProductReviewCreate) -> Optional[ProductReview]:
        """Create product review"""
        try:
            # Check if user already reviewed this product
            existing = await self.reviews_collection.find_one({
                "user_id": user_id,
                "product_id": review.product_id
            })
            
            if existing:
                return None  # User already reviewed this product
            
            # Check if user purchased this product (for verified purchase badge)
            purchase_count = await self.db.payment_transactions.count_documents({
                "customer_info.email": user_id,  # Assuming email is used as user identifier
                "package_id": review.product_id,
                "payment_status": "paid"
            })
            
            review_obj = ProductReview(
                user_id=user_id,
                product_id=review.product_id,
                rating=review.rating,
                title=review.title,
                content=review.content,
                is_verified_purchase=purchase_count > 0
            )
            
            await self.reviews_collection.insert_one(review_obj.dict())
            
            await self.log_user_activity(
                user_id,
                ActivityType.PRODUCT_VIEW,  # Could add REVIEW_CREATE activity type
                f"Created review for product",
                {"product_id": review.product_id, "rating": review.rating}
            )
            
            return review_obj
        except Exception as e:
            logger.error(f"Failed to create review: {e}")
            return None
    
    async def get_product_reviews(
        self, 
        product_id: str, 
        limit: int = 20,
        approved_only: bool = True
    ) -> List[ProductReviewResponse]:
        """Get reviews for a product"""
        try:
            query = {"product_id": product_id}
            if approved_only:
                query["is_approved"] = True
            
            # Aggregation to include username
            pipeline = [
                {"$match": query},
                {"$lookup": {
                    "from": "users",
                    "localField": "user_id", 
                    "foreignField": "id",
                    "as": "user"
                }},
                {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
                {"$sort": {"created_at": -1}},
                {"$limit": limit}
            ]
            
            cursor = self.reviews_collection.aggregate(pipeline)
            results = await cursor.to_list(length=limit)
            
            reviews = []
            for result in results:
                user = result.get("user", {})
                
                review = ProductReviewResponse(
                    id=result["id"],
                    user_id=result["user_id"],
                    username=user.get("username", "Anonymous"),
                    product_id=result["product_id"],
                    rating=result["rating"],
                    title=result["title"],
                    content=result["content"],
                    is_verified_purchase=result["is_verified_purchase"],
                    is_approved=result["is_approved"],
                    helpful_votes=result["helpful_votes"],
                    created_at=result["created_at"],
                    updated_at=result["updated_at"]
                )
                reviews.append(review)
            
            return reviews
        except Exception as e:
            logger.error(f"Failed to get product reviews: {e}")
            return []
    
    async def get_user_reviews(self, user_id: str, limit: int = 20) -> List[ProductReviewResponse]:
        """Get reviews by user"""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$lookup": {
                    "from": "products",
                    "localField": "product_id",
                    "foreignField": "id", 
                    "as": "product"
                }},
                {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},
                {"$sort": {"created_at": -1}},
                {"$limit": limit}
            ]
            
            cursor = self.reviews_collection.aggregate(pipeline)
            results = await cursor.to_list(length=limit)
            
            reviews = []
            for result in results:
                review = ProductReviewResponse(
                    id=result["id"],
                    user_id=result["user_id"],
                    username=None,  # Don't expose username for user's own reviews
                    product_id=result["product_id"],
                    rating=result["rating"],
                    title=result["title"],
                    content=result["content"],
                    is_verified_purchase=result["is_verified_purchase"],
                    is_approved=result["is_approved"],
                    helpful_votes=result["helpful_votes"],
                    created_at=result["created_at"],
                    updated_at=result["updated_at"]
                )
                reviews.append(review)
            
            return reviews
        except Exception as e:
            logger.error(f"Failed to get user reviews: {e}")
            return []
    
    # Search History
    async def log_search(self, user_id: str, query: str, results_count: int = 0, clicked_product_id: Optional[str] = None) -> bool:
        """Log user search"""
        try:
            search = SearchHistory(
                user_id=user_id,
                query=query.lower().strip(),
                results_count=results_count,
                clicked_product_id=clicked_product_id
            )
            
            await self.search_history_collection.insert_one(search.dict())
            
            await self.log_user_activity(
                user_id,
                ActivityType.PRODUCT_SEARCH,
                f"Searched for: {query}",
                {"query": query, "results_count": results_count}
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            return False
    
    async def get_user_search_history(self, user_id: str, limit: int = 20) -> List[SearchHistory]:
        """Get user's search history"""
        try:
            cursor = self.search_history_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
            search_docs = await cursor.to_list(length=limit)
            
            return [SearchHistory(**doc) for doc in search_docs]
        except Exception as e:
            logger.error(f"Failed to get search history: {e}")
            return []
    
    async def get_popular_searches(self, limit: int = 10) -> List[PopularSearch]:
        """Get popular search queries"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$query",
                    "search_count": {"$sum": 1},
                    "last_searched": {"$max": "$created_at"}
                }},
                {"$sort": {"search_count": -1}},
                {"$limit": limit}
            ]
            
            cursor = self.search_history_collection.aggregate(pipeline)
            results = await cursor.to_list(length=limit)
            
            popular_searches = []
            for result in results:
                search = PopularSearch(
                    query=result["_id"],
                    search_count=result["search_count"],
                    last_searched=result["last_searched"]
                )
                popular_searches.append(search)
            
            return popular_searches
        except Exception as e:
            logger.error(f"Failed to get popular searches: {e}")
            return []
    
    # User Profile Stats
    async def get_user_profile_stats(self, user_id: str) -> UserProfileStats:
        """Get user profile statistics"""
        try:
            # Get user creation date
            user = await self.users_collection.find_one({"id": user_id})
            member_since = user.get("created_at", datetime.utcnow()) if user else datetime.utcnow()
            
            # Get order stats (assuming orders are linked by email)
            user_email = user.get("email") if user else None
            
            total_orders = 0
            total_spent = 0.0
            last_order = None
            
            if user_email:
                # Count orders
                total_orders = await self.db.payment_transactions.count_documents({
                    "customer_info.email": user_email,
                    "payment_status": "paid"
                })
                
                # Calculate total spent
                spent_pipeline = [
                    {"$match": {
                        "customer_info.email": user_email,
                        "payment_status": "paid"
                    }},
                    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                ]
                spent_result = await self.db.payment_transactions.aggregate(spent_pipeline).to_list(1)
                if spent_result:
                    total_spent = spent_result[0]["total"]
                
                # Get last order date
                last_order_doc = await self.db.payment_transactions.find_one(
                    {
                        "customer_info.email": user_email,
                        "payment_status": "paid"
                    },
                    sort=[("created_at", -1)]
                )
                if last_order_doc:
                    last_order = last_order_doc["created_at"]
            
            # Get other stats
            products_reviewed = await self.reviews_collection.count_documents({"user_id": user_id})
            wishlist_items = await self.wishlists_collection.count_documents({"user_id": user_id})
            addresses_count = await self.addresses_collection.count_documents({"user_id": user_id})
            
            # Get favorite category (most ordered)
            favorite_category = None
            if user_email:
                category_pipeline = [
                    {"$match": {
                        "customer_info.email": user_email,
                        "payment_status": "paid"
                    }},
                    {"$lookup": {
                        "from": "products",
                        "localField": "package_id",
                        "foreignField": "id",
                        "as": "product"
                    }},
                    {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},
                    {"$group": {
                        "_id": "$product.category",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": 1}
                ]
                
                category_result = await self.db.payment_transactions.aggregate(category_pipeline).to_list(1)
                if category_result and category_result[0]["_id"]:
                    favorite_category = category_result[0]["_id"]
            
            return UserProfileStats(
                total_orders=total_orders,
                total_spent=total_spent,
                products_reviewed=products_reviewed,
                wishlist_items=wishlist_items,
                addresses_count=addresses_count,
                member_since=member_since,
                last_order=last_order,
                favorite_category=favorite_category
            )
            
        except Exception as e:
            logger.error(f"Failed to get user profile stats: {e}")
            return UserProfileStats(member_since=datetime.utcnow())