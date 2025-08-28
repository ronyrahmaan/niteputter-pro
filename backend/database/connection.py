"""
Professional MongoDB Connection Management
Senior-level database connection handling with connection pooling,
retry logic, and environment-based configuration.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
import asyncio
from config import settings

logger = logging.getLogger("niteputter.database")

class DatabaseManager:
    """Professional database connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_retries = 3
        self._retry_delay = 2
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """Connect to MongoDB with retry logic and connection pooling"""
        if self.database:
            return self.database
        
        for attempt in range(self._connection_retries):
            try:
                logger.info(f"Connecting to MongoDB (attempt {attempt + 1}/{self._connection_retries})")
                
                # Professional connection configuration
                self.client = AsyncIOMotorClient(
                    settings.database_url,
                    maxPoolSize=50,  # Connection pool for high concurrency
                    minPoolSize=5,   # Minimum connections maintained
                    maxIdleTimeMS=30000,  # Close idle connections after 30s
                    serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
                    connectTimeoutMS=10000,  # 10s timeout for connection
                    socketTimeoutMS=20000,  # 20s timeout for socket operations
                    retryWrites=True,  # Retry writes on network errors
                    retryReads=True,   # Retry reads on network errors
                    w='majority',      # Write concern for data safety
                    readPreference='primary'  # Read from primary for consistency
                )
                
                # Test connection
                await self.client.admin.command('ping')
                
                # Get database
                db_name = settings.database_url.split('/')[-1].split('?')[0]
                self.database = self.client[db_name]
                
                logger.info(f"Successfully connected to MongoDB: {db_name}")
                return self.database
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self._connection_retries - 1:
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error("Failed to connect to MongoDB after all retry attempts")
                    raise
        
        raise ConnectionFailure("Could not establish database connection")
    
    async def disconnect(self):
        """Gracefully disconnect from MongoDB"""
        if self.client:
            logger.info("Disconnecting from MongoDB")
            self.client.close()
            self.client = None
            self.database = None
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance, connecting if necessary"""
        if not self.database:
            await self.connect()
        return self.database
    
    async def health_check(self) -> dict:
        """Check database health for monitoring"""
        try:
            if not self.database:
                return {"status": "disconnected", "error": "No database connection"}
            
            # Ping database
            start_time = asyncio.get_event_loop().time()
            await self.client.admin.command('ping')
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Get server info
            server_info = await self.client.admin.command('buildInfo')
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "mongodb_version": server_info.get('version', 'unknown'),
                "connection_pool": {
                    "current_connections": self.client.topology_description.has_server,
                    "max_pool_size": 50
                }
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> AsyncIOMotorDatabase:
    """Dependency injection for FastAPI"""
    return await db_manager.get_database()

# Startup/shutdown events for FastAPI
async def startup_database():
    """Initialize database connection on app startup"""
    logger.info("Initializing database connection...")
    await db_manager.connect()

async def shutdown_database():
    """Close database connection on app shutdown"""
    logger.info("Closing database connection...")
    await db_manager.disconnect()