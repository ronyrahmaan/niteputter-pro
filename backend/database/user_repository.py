from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from models.user import UserCreate, UserInDB, UserUpdate
from auth.auth_handler import auth_handler
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.users
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            await self.collection.create_index("email", unique=True)
            await self.collection.create_index("username", unique=True)
            await self.collection.create_index("created_at")
            await self.collection.create_index("is_active")
            logger.info("User collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
        
    async def create_user(self, user: UserCreate) -> Optional[UserInDB]:
        """Create new user with hashed password"""
        try:
            hashed_password = auth_handler.get_password_hash(user.password)
            user_dict = user.dict()
            del user_dict['password']
            user_dict['hashed_password'] = hashed_password
            
            user_in_db = UserInDB(**user_dict)
            
            # Convert to dict for MongoDB insertion
            user_doc = user_in_db.dict()
            result = await self.collection.insert_one(user_doc)
            
            if result.inserted_id:
                return await self.get_user_by_id(user_in_db.id)
            return None
            
        except DuplicateKeyError as e:
            logger.error(f"User creation failed - duplicate key: {e}")
            return None
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Retrieve user by email address"""
        try:
            user_doc = await self.collection.find_one({"email": email})
            if user_doc:
                return UserInDB(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Retrieve user by ID"""
        try:
            user_doc = await self.collection.find_one({"id": user_id})
            if user_doc:
                return UserInDB(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Retrieve user by username"""
        try:
            user_doc = await self.collection.find_one({"username": username})
            if user_doc:
                return UserInDB(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user credentials"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
            
        if not auth_handler.verify_password(password, user.hashed_password):
            return None
            
        return user
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user profile information"""
        try:
            update_dict = user_update.dict(exclude_unset=True)
            
            if 'password' in update_dict:
                update_dict['hashed_password'] = auth_handler.get_password_hash(
                    update_dict['password']
                )
                del update_dict['password']
            
            if update_dict:
                update_dict['updated_at'] = datetime.utcnow()
                result = await self.collection.update_one(
                    {"id": user_id}, 
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    return await self.get_user_by_id(user_id)
            
            return await self.get_user_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return None
    
    async def update_cart_items(self, user_id: str, cart_items: List[Dict[str, Any]]) -> bool:
        """Update user's cart items"""
        try:
            result = await self.collection.update_one(
                {"id": user_id},
                {"$set": {"cart_items": cart_items, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Cart update failed: {e}")
            return False
    
    async def get_user_cart(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's cart items"""
        try:
            user = await self.get_user_by_id(user_id)
            if user:
                return user.cart_items
            return []
        except Exception as e:
            logger.error(f"Failed to get user cart: {e}")
            return []