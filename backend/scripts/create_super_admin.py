"""
Script to create the first super admin for the admin dashboard
Run this script to create a super admin account
"""

import asyncio
import os
import sys
from pathlib import Path
import getpass

# Add the backend directory to the Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from models.admin import AdminCreate, AdminRole
from database.admin_repository import AdminRepository

load_dotenv(ROOT_DIR / '.env')

async def create_super_admin():
    """Create the first super admin"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Initialize admin repository
        admin_repo = AdminRepository(db)
        
        # Create indexes
        await admin_repo.create_indexes()
        print("✅ Admin indexes created")
        
        # Check if any super admin already exists
        existing_admins, count = await admin_repo.get_admins(role=AdminRole.SUPER_ADMIN)
        if count > 0:
            print(f"⚠️  {count} super admin(s) already exist:")
            for admin in existing_admins:
                print(f"   - {admin.email} ({admin.first_name} {admin.last_name})")
            
            response = input("\nDo you want to create another super admin? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled")
                return
        
        print("\n🔧 Creating Super Admin Account")
        print("=" * 40)
        
        # Get admin details from user input
        email = input("Email: ").strip()
        while not email or '@' not in email:
            print("❌ Please enter a valid email address")
            email = input("Email: ").strip()
        
        # Check if admin with this email already exists
        existing = await admin_repo.get_admin_by_email(email)
        if existing:
            print(f"❌ Admin with email {email} already exists")
            return
        
        username = input("Username: ").strip()
        while not username or len(username) < 3:
            print("❌ Username must be at least 3 characters")
            username = input("Username: ").strip()
        
        first_name = input("First Name: ").strip()
        while not first_name:
            print("❌ First name is required")
            first_name = input("First Name: ").strip()
        
        last_name = input("Last Name: ").strip()
        while not last_name:
            print("❌ Last name is required")
            last_name = input("Last Name: ").strip()
        
        # Get password securely
        password = getpass.getpass("Password (min 8 characters): ")
        while len(password) < 8:
            print("❌ Password must be at least 8 characters")
            password = getpass.getpass("Password (min 8 characters): ")
        
        confirm_password = getpass.getpass("Confirm Password: ")
        while password != confirm_password:
            print("❌ Passwords do not match")
            confirm_password = getpass.getpass("Confirm Password: ")
        
        # Create super admin
        admin_create = AdminCreate(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=AdminRole.SUPER_ADMIN,
            is_active=True
        )
        
        print("\n⏳ Creating super admin...")
        created_admin = await admin_repo.create_admin(admin_create)
        
        if created_admin:
            print("\n🎉 Super Admin Created Successfully!")
            print("=" * 40)
            print(f"Email: {created_admin.email}")
            print(f"Username: {created_admin.username}")
            print(f"Name: {created_admin.first_name} {created_admin.last_name}")
            print(f"Role: {created_admin.role}")
            print(f"Permissions: {len(created_admin.permissions)} permissions granted")
            print(f"Created: {created_admin.created_at}")
            print("\n✅ You can now login to the admin dashboard with these credentials")
        else:
            print("❌ Failed to create super admin")
            return
        
        # Display summary
        all_admins, total_count = await admin_repo.get_admins()
        print(f"\n📊 Total admins in database: {total_count}")
        
        # Close connection
        client.close()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to create super admin: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Super Admin Creation Tool")
    print("=" * 40)
    print("This tool will help you create the first super admin account")
    print("for the Nite Putter Pro admin dashboard.\n")
    
    asyncio.run(create_super_admin())