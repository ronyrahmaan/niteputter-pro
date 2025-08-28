"""
MongoDB Database Connection and Configuration
Production-ready database setup for NitePutter Pro
"""

import os
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT, GEO2D
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongodb():
    """Connect to MongoDB with retry logic"""
    max_retries = 3
    retry_count = 0
    
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "niteputter_pro")
    
    while retry_count < max_retries:
        try:
            logger.info(f"Connecting to MongoDB at {mongodb_url}")
            
            db.client = AsyncIOMotorClient(
                mongodb_url,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
                retryWrites=True,
                w="majority",
                journal=True,
                readPreference="primaryPreferred"
            )
            
            # Verify connection
            await db.client.admin.command('ping')
            
            db.database = db.client[database_name]
            
            logger.info(f"Successfully connected to MongoDB database: {database_name}")
            
            # Create indexes
            await create_indexes()
            
            return True
            
        except ConnectionFailure as e:
            retry_count += 1
            logger.error(f"MongoDB connection attempt {retry_count} failed: {e}")
            if retry_count >= max_retries:
                raise
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise

async def close_mongodb_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        # Product indexes
        product_indexes = [
            IndexModel([("sku", ASCENDING)], unique=True, name="sku_unique"),
            IndexModel([("slug", ASCENDING)], unique=True, name="slug_unique"),
            IndexModel([("category", ASCENDING)], name="category_index"),
            IndexModel([("status", ASCENDING)], name="status_index"),
            IndexModel([("price", ASCENDING)], name="price_index"),
            IndexModel([("created_at", DESCENDING)], name="created_at_index"),
            IndexModel([("average_rating", DESCENDING)], name="rating_index"),
            IndexModel([
                ("name", TEXT),
                ("description", TEXT),
                ("short_description", TEXT),
                ("features", TEXT)
            ], name="text_search_index"),
            IndexModel([
                ("category", ASCENDING),
                ("status", ASCENDING),
                ("price", ASCENDING)
            ], name="category_status_price_compound")
        ]
        
        await db.database.products.create_indexes(product_indexes)
        logger.info("Created product indexes")
        
        # Order indexes
        order_indexes = [
            IndexModel([("order_number", ASCENDING)], unique=True, name="order_number_unique"),
            IndexModel([("customer_email", ASCENDING)], name="customer_email_index"),
            IndexModel([("status", ASCENDING)], name="order_status_index"),
            IndexModel([("payment_status", ASCENDING)], name="payment_status_index"),
            IndexModel([("fulfillment_status", ASCENDING)], name="fulfillment_status_index"),
            IndexModel([("created_at", DESCENDING)], name="order_created_at_index"),
            IndexModel([("customer_id", ASCENDING)], name="customer_id_index"),
            IndexModel([
                ("status", ASCENDING),
                ("created_at", DESCENDING)
            ], name="status_date_compound"),
            IndexModel([
                ("customer_email", ASCENDING),
                ("created_at", DESCENDING)
            ], name="email_date_compound")
        ]
        
        await db.database.orders.create_indexes(order_indexes)
        logger.info("Created order indexes")
        
        # User indexes
        user_indexes = [
            IndexModel([("email", ASCENDING)], unique=True, name="email_unique"),
            IndexModel([("username", ASCENDING)], unique=True, sparse=True, name="username_unique"),
            IndexModel([("created_at", DESCENDING)], name="user_created_at_index"),
            IndexModel([("is_active", ASCENDING)], name="active_users_index"),
            IndexModel([("role", ASCENDING)], name="user_role_index")
        ]
        
        await db.database.users.create_indexes(user_indexes)
        logger.info("Created user indexes")
        
        # Cart indexes
        cart_indexes = [
            IndexModel([("session_id", ASCENDING)], unique=True, name="session_id_unique"),
            IndexModel([("user_id", ASCENDING)], sparse=True, name="cart_user_id_index"),
            IndexModel([("updated_at", ASCENDING)], name="cart_updated_at_index"),
            IndexModel([("expires_at", ASCENDING)], name="cart_expiry_index")
        ]
        
        await db.database.carts.create_indexes(cart_indexes)
        logger.info("Created cart indexes")
        
        # Review indexes
        review_indexes = [
            IndexModel([("product_id", ASCENDING)], name="review_product_index"),
            IndexModel([("customer_id", ASCENDING)], name="review_customer_index"),
            IndexModel([("rating", DESCENDING)], name="review_rating_index"),
            IndexModel([("created_at", DESCENDING)], name="review_date_index"),
            IndexModel([("verified_purchase", ASCENDING)], name="verified_purchase_index"),
            IndexModel([
                ("product_id", ASCENDING),
                ("rating", DESCENDING)
            ], name="product_rating_compound")
        ]
        
        await db.database.reviews.create_indexes(review_indexes)
        logger.info("Created review indexes")
        
        # Inventory tracking indexes
        inventory_indexes = [
            IndexModel([("product_id", ASCENDING)], unique=True, name="inventory_product_unique"),
            IndexModel([("quantity", ASCENDING)], name="inventory_quantity_index"),
            IndexModel([("low_stock_alert", ASCENDING)], name="low_stock_index"),
            IndexModel([("last_restocked", DESCENDING)], name="restock_date_index")
        ]
        
        await db.database.inventory.create_indexes(inventory_indexes)
        logger.info("Created inventory indexes")
        
        # Coupon indexes
        coupon_indexes = [
            IndexModel([("code", ASCENDING)], unique=True, name="coupon_code_unique"),
            IndexModel([("valid_from", ASCENDING)], name="coupon_valid_from_index"),
            IndexModel([("valid_until", ASCENDING)], name="coupon_valid_until_index"),
            IndexModel([("is_active", ASCENDING)], name="coupon_active_index")
        ]
        
        await db.database.coupons.create_indexes(coupon_indexes)
        logger.info("Created coupon indexes")
        
        # Analytics indexes
        analytics_indexes = [
            IndexModel([("event_type", ASCENDING)], name="event_type_index"),
            IndexModel([("timestamp", DESCENDING)], name="analytics_timestamp_index"),
            IndexModel([("user_id", ASCENDING)], sparse=True, name="analytics_user_index"),
            IndexModel([("session_id", ASCENDING)], name="analytics_session_index"),
            IndexModel([
                ("event_type", ASCENDING),
                ("timestamp", DESCENDING)
            ], name="event_time_compound")
        ]
        
        await db.database.analytics.create_indexes(analytics_indexes)
        logger.info("Created analytics indexes")
        
        logger.info("All database indexes created successfully")
        
    except OperationFailure as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't fail the application if indexes exist
        if "already exists" not in str(e):
            raise
    except Exception as e:
        logger.error(f"Unexpected error creating indexes: {e}")
        raise

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db.database is None:
        await connect_to_mongodb()
    return db.database

async def health_check() -> Dict[str, Any]:
    """Check database health"""
    try:
        if db.client is None:
            return {
                "status": "error",
                "message": "Database not connected"
            }
        
        # Ping database
        start = datetime.utcnow()
        await db.client.admin.command('ping')
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        
        # Get database stats
        stats = await db.database.command("dbStats")
        
        # Count documents
        product_count = await db.database.products.count_documents({})
        order_count = await db.database.orders.count_documents({})
        user_count = await db.database.users.count_documents({})
        
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "database_size": stats.get("dataSize", 0),
            "collections": {
                "products": product_count,
                "orders": order_count,
                "users": user_count
            },
            "indexes": stats.get("indexes", 0)
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# Import asyncio for retry logic
import asyncio

# Collection helpers
def get_collection(collection_name: str):
    """Get a collection from the database"""
    if not db.database:
        raise RuntimeError("Database not connected")
    return db.database[collection_name]

# Commonly used collections
def products_collection():
    return get_collection("products")

def orders_collection():
    return get_collection("orders")

def users_collection():
    return get_collection("users")

def carts_collection():
    return get_collection("carts")

def reviews_collection():
    return get_collection("reviews")

def inventory_collection():
    return get_collection("inventory")