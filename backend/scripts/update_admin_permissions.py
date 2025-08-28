"""
Script to update admin permissions for existing admins
This adds the new e-commerce permissions to existing super admins
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
from models.admin import AdminRole, ROLE_PERMISSIONS
from database.admin_repository import AdminRepository

load_dotenv(ROOT_DIR / '.env')

async def update_admin_permissions():
    """Update permissions for existing admins"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Initialize admin repository
        admin_repo = AdminRepository(db)
        
        print("🔧 Updating Admin Permissions")
        print("=" * 40)
        
        # Get all admins
        all_admins, total_count = await admin_repo.get_admins()
        print(f"Found {total_count} admin(s) to update")
        
        updated_count = 0
        
        for admin in all_admins:
            print(f"\n📝 Updating {admin.email} ({admin.role})...")
            
            # Get the correct permissions for this role
            correct_permissions = ROLE_PERMISSIONS.get(admin.role, [])
            
            # Update the admin's permissions
            result = await admin_repo.admins_collection.update_one(
                {"id": admin.id},
                {"$set": {"permissions": [perm.value for perm in correct_permissions]}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Updated permissions for {admin.email}")
                print(f"   New permission count: {len(correct_permissions)}")
                updated_count += 1
            else:
                print(f"⚠️  No update needed for {admin.email}")
        
        print(f"\n🎉 Updated {updated_count} admin(s) successfully!")
        
        # Verify the updates
        print("\n📊 Verification:")
        all_admins, _ = await admin_repo.get_admins()
        for admin in all_admins:
            print(f"   {admin.email} ({admin.role}): {len(admin.permissions)} permissions")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Failed to update admin permissions: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Admin Permission Update Tool")
    print("=" * 40)
    print("This tool will update permissions for existing admins")
    print("to include the new e-commerce permissions.\n")
    
    asyncio.run(update_admin_permissions())