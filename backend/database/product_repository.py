from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from models.product import (
    ProductCreate, ProductInDB, ProductUpdate, ProductFilter, 
    ProductResponse, InventoryUpdate, InventoryHistory, ProductStatus
)
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class ProductRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.products_collection = database.products
        self.inventory_history_collection = database.inventory_history
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Product indexes
            await self.products_collection.create_index("sku", unique=True)
            await self.products_collection.create_index("category")
            await self.products_collection.create_index("status")
            await self.products_collection.create_index("is_featured")
            await self.products_collection.create_index("base_price")
            await self.products_collection.create_index("created_at")
            await self.products_collection.create_index("tags")
            await self.products_collection.create_index([("name", "text"), ("description", "text")])
            
            # Inventory history indexes
            await self.inventory_history_collection.create_index("product_id")
            await self.inventory_history_collection.create_index("created_at")
            await self.inventory_history_collection.create_index("change_type")
            
            logger.info("Product collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create product indexes: {e}")
    
    async def create_product(self, product: ProductCreate, created_by: Optional[str] = None) -> Optional[ProductInDB]:
        """Create new product"""
        try:
            product_dict = product.dict()
            product_dict['created_by'] = created_by
            product_dict['updated_by'] = created_by
            
            product_in_db = ProductInDB(**product_dict)
            
            # Convert to dict for MongoDB insertion
            product_doc = product_in_db.dict()
            result = await self.products_collection.insert_one(product_doc)
            
            if result.inserted_id:
                return await self.get_product_by_id(product_in_db.id)
            return None
            
        except DuplicateKeyError as e:
            logger.error(f"Product creation failed - duplicate SKU: {e}")
            return None
        except Exception as e:
            logger.error(f"Product creation failed: {e}")
            return None
    
    async def get_product_by_id(self, product_id: str) -> Optional[ProductInDB]:
        """Retrieve product by ID"""
        try:
            product_doc = await self.products_collection.find_one({"id": product_id})
            if product_doc:
                return ProductInDB(**product_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get product by ID: {e}")
            return None
    
    async def get_product_by_sku(self, sku: str) -> Optional[ProductInDB]:
        """Retrieve product by SKU"""
        try:
            product_doc = await self.products_collection.find_one({"sku": sku.upper()})
            if product_doc:
                return ProductInDB(**product_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get product by SKU: {e}")
            return None
    
    async def update_product(self, product_id: str, product_update: ProductUpdate, updated_by: Optional[str] = None) -> Optional[ProductInDB]:
        """Update product information"""
        try:
            update_dict = product_update.dict(exclude_unset=True)
            
            if update_dict:
                update_dict['updated_at'] = datetime.utcnow()
                update_dict['updated_by'] = updated_by
                
                result = await self.products_collection.update_one(
                    {"id": product_id}, 
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    return await self.get_product_by_id(product_id)
            
            return await self.get_product_by_id(product_id)
            
        except Exception as e:
            logger.error(f"Failed to update product: {e}")
            return None
    
    async def delete_product(self, product_id: str) -> bool:
        """Soft delete product by setting status to discontinued"""
        try:
            result = await self.products_collection.update_one(
                {"id": product_id},
                {"$set": {"status": ProductStatus.DISCONTINUED, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to delete product: {e}")
            return False
    
    async def hard_delete_product(self, product_id: str) -> bool:
        """Permanently delete product from database"""
        try:
            result = await self.products_collection.delete_one({"id": product_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to hard delete product: {e}")
            return False
    
    async def get_products(
        self, 
        filters: Optional[ProductFilter] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Tuple[List[ProductInDB], int]:
        """Get products with filtering, pagination, and sorting"""
        try:
            # Build query
            query = {}
            
            if filters:
                if filters.category:
                    query["category"] = filters.category
                if filters.status:
                    query["status"] = filters.status
                if filters.is_featured is not None:
                    query["is_featured"] = filters.is_featured
                if filters.min_price is not None or filters.max_price is not None:
                    price_query = {}
                    if filters.min_price is not None:
                        price_query["$gte"] = filters.min_price
                    if filters.max_price is not None:
                        price_query["$lte"] = filters.max_price
                    query["base_price"] = price_query
                if filters.tags:
                    query["tags"] = {"$in": filters.tags}
                if filters.search:
                    # Text search in name and description
                    query["$text"] = {"$search": filters.search}
                if filters.low_stock_only:
                    query["$expr"] = {"$lte": ["$inventory_count", "$low_stock_threshold"]}
                if filters.out_of_stock_only:
                    query["inventory_count"] = 0
            
            # Get total count
            total_count = await self.products_collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Execute query with pagination and sorting
            cursor = self.products_collection.find(query).sort(sort_by, sort_order).skip(skip).limit(page_size)
            products_docs = await cursor.to_list(length=page_size)
            
            products = [ProductInDB(**doc) for doc in products_docs]
            
            return products, total_count
            
        except Exception as e:
            logger.error(f"Failed to get products: {e}")
            return [], 0
    
    async def get_featured_products(self, limit: int = 10) -> List[ProductInDB]:
        """Get featured products"""
        try:
            cursor = self.products_collection.find(
                {"is_featured": True, "status": ProductStatus.ACTIVE}
            ).sort("created_at", -1).limit(limit)
            
            products_docs = await cursor.to_list(length=limit)
            return [ProductInDB(**doc) for doc in products_docs]
        except Exception as e:
            logger.error(f"Failed to get featured products: {e}")
            return []
    
    async def get_low_stock_products(self) -> List[ProductInDB]:
        """Get products with low stock"""
        try:
            cursor = self.products_collection.find({
                "$expr": {"$lte": ["$inventory_count", "$low_stock_threshold"]},
                "inventory_count": {"$gt": 0},
                "status": ProductStatus.ACTIVE
            })
            
            products_docs = await cursor.to_list(length=None)
            return [ProductInDB(**doc) for doc in products_docs]
        except Exception as e:
            logger.error(f"Failed to get low stock products: {e}")
            return []
    
    async def update_inventory(
        self, 
        product_id: str, 
        inventory_update: InventoryUpdate,
        change_type: str = "adjustment",
        updated_by: Optional[str] = None
    ) -> bool:
        """Update product inventory and log the change"""
        try:
            # Get current product
            product = await self.get_product_by_id(product_id)
            if not product:
                return False
            
            previous_count = product.inventory_count
            new_count = inventory_update.inventory_count
            change_amount = new_count - previous_count
            
            # Update product inventory
            result = await self.products_collection.update_one(
                {"id": product_id},
                {
                    "$set": {
                        "inventory_count": new_count,
                        "updated_at": datetime.utcnow(),
                        "updated_by": updated_by
                    }
                }
            )
            
            if result.modified_count > 0:
                # Log inventory change
                inventory_history = InventoryHistory(
                    product_id=product_id,
                    previous_count=previous_count,
                    new_count=new_count,
                    change_amount=change_amount,
                    change_type=change_type,
                    notes=inventory_update.notes,
                    created_by=updated_by
                )
                
                await self.inventory_history_collection.insert_one(inventory_history.dict())
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update inventory: {e}")
            return False
    
    async def get_inventory_history(self, product_id: str, limit: int = 50) -> List[InventoryHistory]:
        """Get inventory history for a product"""
        try:
            cursor = self.inventory_history_collection.find(
                {"product_id": product_id}
            ).sort("created_at", -1).limit(limit)
            
            history_docs = await cursor.to_list(length=limit)
            return [InventoryHistory(**doc) for doc in history_docs]
        except Exception as e:
            logger.error(f"Failed to get inventory history: {e}")
            return []
    
    async def increment_view_count(self, product_id: str) -> bool:
        """Increment product view count"""
        try:
            result = await self.products_collection.update_one(
                {"id": product_id},
                {"$inc": {"view_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment view count: {e}")
            return False
    
    async def increment_purchase_count(self, product_id: str) -> bool:
        """Increment product purchase count and update last purchased"""
        try:
            result = await self.products_collection.update_one(
                {"id": product_id},
                {
                    "$inc": {"purchase_count": 1},
                    "$set": {"last_purchased": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment purchase count: {e}")
            return False
    
    async def get_categories_with_counts(self) -> Dict[str, int]:
        """Get product categories with product counts"""
        try:
            pipeline = [
                {"$match": {"status": ProductStatus.ACTIVE}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            result = await self.products_collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in result}
        except Exception as e:
            logger.error(f"Failed to get categories with counts: {e}")
            return {}
    
    async def search_products(self, query: str, limit: int = 20) -> List[ProductInDB]:
        """Full-text search products"""
        try:
            # Use text search
            cursor = self.products_collection.find(
                {
                    "$text": {"$search": query},
                    "status": ProductStatus.ACTIVE
                },
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            products_docs = await cursor.to_list(length=limit)
            return [ProductInDB(**doc) for doc in products_docs]
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []