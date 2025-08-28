"""
Quick Database Status Check
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongodb, get_database

async def check_database():
    """Check database status and contents"""
    try:
        # Connect
        await connect_to_mongodb()
        db = await get_database()
        
        print("\n" + "=" * 60)
        print("  📊 NitePutter Pro Database Status")
        print("=" * 60)
        
        # Check collections
        collections = [
            ("Products", "products"),
            ("Users", "users"),
            ("Orders", "orders"),
            ("Reviews", "reviews"),
            ("Coupons", "coupons"),
            ("Carts", "carts"),
            ("Inventory", "inventory")
        ]
        
        print("\n📦 Collection Counts:")
        print("-" * 40)
        for name, collection in collections:
            count = await db[collection].count_documents({})
            status = "✅" if count > 0 else "⚠️"
            print(f"{status} {name:12} : {count:6} documents")
        
        # Show some sample data
        print("\n🏷️ Sample Products:")
        print("-" * 40)
        products = await db.products.find({}, {"name": 1, "sku": 1, "price": 1}).limit(3).to_list(None)
        for p in products:
            print(f"  • {p['name'][:30]:30} (SKU: {p['sku']}) - ${p['price']:.2f}")
        
        print("\n👥 Sample Users:")
        print("-" * 40)
        users = await db.users.find({}, {"email": 1, "role": 1, "first_name": 1, "last_name": 1}).limit(3).to_list(None)
        for u in users:
            print(f"  • {u['email']:30} - {u['first_name']} {u['last_name']} ({u['role']})")
        
        print("\n🎟️ Active Coupons:")
        print("-" * 40)
        coupons = await db.coupons.find({"is_active": True}, {"code": 1, "description": 1}).limit(5).to_list(None)
        for c in coupons:
            print(f"  • {c['code']:12} - {c['description']}")
        
        print("\n✅ Database is ready for use!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Database check failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())