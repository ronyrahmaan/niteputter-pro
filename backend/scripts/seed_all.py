"""
Master Database Seeder for NitePutter Pro
Seeds all production data in the correct order
"""

import asyncio
import sys
import os
from datetime import datetime, UTC
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongodb, get_database
from seed_products import seed_products
from seed_users import seed_users
from seed_reviews_coupons import seed_reviews, seed_coupons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_database_connection():
    """Verify database connection"""
    try:
        await connect_to_mongodb()
        db = await get_database()
        
        # Test connection
        await db.command('ping')
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def display_current_stats():
    """Display current database statistics"""
    try:
        db = await get_database()
        
        print("\n📊 Current Database Statistics:")
        print("-" * 40)
        
        collections = [
            ("Products", "products"),
            ("Users", "users"),
            ("Orders", "orders"),
            ("Reviews", "reviews"),
            ("Coupons", "coupons"),
            ("Carts", "carts"),
            ("Inventory", "inventory")
        ]
        
        for name, collection in collections:
            count = await db[collection].count_documents({})
            print(f"{name:12} : {count:6} documents")
        
        print("-" * 40)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")

async def seed_all_data(skip_existing=False):
    """Seed all data in the correct order"""
    try:
        print("\n🌱 Starting Complete Database Seeding...")
        print("=" * 50)
        
        # 1. Seed Products (required for reviews)
        print("\n1️⃣  Seeding Products...")
        print("-" * 40)
        try:
            await seed_products()
            print("✅ Products seeded successfully")
        except Exception as e:
            logger.error(f"❌ Product seeding failed: {e}")
            if not skip_existing:
                return False
        
        # 2. Seed Users (required for orders)
        print("\n2️⃣  Seeding Users...")
        print("-" * 40)
        try:
            await seed_users()
            print("✅ Users seeded successfully")
        except Exception as e:
            logger.error(f"❌ User seeding failed: {e}")
            if not skip_existing:
                return False
        
        # 3. Seed Reviews
        print("\n3️⃣  Seeding Reviews...")
        print("-" * 40)
        try:
            review_count = await seed_reviews()
            print(f"✅ {review_count} reviews seeded successfully")
        except Exception as e:
            logger.error(f"❌ Review seeding failed: {e}")
            if not skip_existing:
                return False
        
        # 4. Seed Coupons
        print("\n4️⃣  Seeding Coupons...")
        print("-" * 40)
        try:
            coupon_count = await seed_coupons()
            print(f"✅ {coupon_count} coupons seeded successfully")
        except Exception as e:
            logger.error(f"❌ Coupon seeding failed: {e}")
            if not skip_existing:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Seeding error: {e}")
        return False

async def create_indexes():
    """Ensure all indexes are created"""
    try:
        db = await get_database()
        
        print("\n🔍 Creating Database Indexes...")
        
        # Products indexes
        await db.products.create_index("sku", unique=True)
        await db.products.create_index("slug", unique=True)
        await db.products.create_index("category")
        await db.products.create_index("status")
        await db.products.create_index([("name", "text"), ("description", "text")])
        
        # Users indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("role")
        await db.users.create_index("status")
        
        # Orders indexes
        await db.orders.create_index("order_number", unique=True)
        await db.orders.create_index("customer_email")
        await db.orders.create_index("status")
        await db.orders.create_index("created_at")
        
        # Reviews indexes
        await db.reviews.create_index("product_id")
        await db.reviews.create_index("customer_email")
        await db.reviews.create_index("rating")
        
        # Coupons indexes
        await db.coupons.create_index("code", unique=True)
        await db.coupons.create_index("is_active")
        
        # Carts indexes
        await db.carts.create_index("session_id")
        await db.carts.create_index("user_id")
        await db.carts.create_index("status")
        
        print("✅ All indexes created successfully")
        
    except Exception as e:
        logger.error(f"Index creation error: {e}")

async def main():
    """Main seeding function"""
    try:
        print("\n" + "=" * 60)
        print("  🏌️  NitePutter Pro - Production Database Seeder")
        print("=" * 60)
        
        # Check connection
        if not await check_database_connection():
            print("\n❌ Cannot proceed without database connection")
            print("Please ensure MongoDB is running and accessible")
            return
        
        # Display current stats
        await display_current_stats()
        
        # Seeding options
        print("\n⚙️  Seeding Options:")
        print("1. Full seed (clear existing data)")
        print("2. Incremental seed (skip existing)")
        print("3. Create indexes only")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            # Full seed with confirmation
            print("\n⚠️  WARNING: This will clear existing data!")
            confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()
            
            if confirm == "yes":
                db = await get_database()
                
                # Clear collections
                print("\n🗑️  Clearing existing data...")
                collections = ["products", "users", "reviews", "coupons", "orders", "carts"]
                for collection in collections:
                    count = await db[collection].count_documents({})
                    if count > 0:
                        await db[collection].delete_many({})
                        print(f"  Cleared {count} documents from {collection}")
                
                # Seed all data
                success = await seed_all_data(skip_existing=False)
                
                if success:
                    # Create indexes
                    await create_indexes()
                    
                    # Final stats
                    await display_current_stats()
                    
                    print("\n" + "=" * 60)
                    print("  ✅ Full database seeding completed successfully!")
                    print("=" * 60)
                else:
                    print("\n❌ Seeding failed")
            else:
                print("Seeding cancelled")
                
        elif choice == "2":
            # Incremental seed
            print("\n📝 Running incremental seed (preserving existing data)...")
            
            success = await seed_all_data(skip_existing=True)
            
            if success:
                # Create indexes
                await create_indexes()
                
                # Final stats
                await display_current_stats()
                
                print("\n" + "=" * 60)
                print("  ✅ Incremental seeding completed successfully!")
                print("=" * 60)
            else:
                print("\n⚠️  Some seeding operations failed (existing data preserved)")
                
        elif choice == "3":
            # Create indexes only
            await create_indexes()
            await display_current_stats()
            
        elif choice == "4":
            print("👋 Exiting...")
            return
        else:
            print("Invalid option")
        
        # Display access info
        print("\n📋 Quick Access Info:")
        print("-" * 40)
        print("Admin Login:")
        print("  Email: admin@niteputterpro.com")
        print("  Password: AdminPass123!")
        print("\nTest Customer:")
        print("  Email: john.doe@example.com")
        print("  Password: Customer123!")
        print("\nActive Coupon Codes:")
        print("  WELCOME10 - 10% off first purchase")
        print("  SUMMER25 - $25 off orders over $200")
        print("  FREESHIP - Free shipping over $150")
        print("-" * 40)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())