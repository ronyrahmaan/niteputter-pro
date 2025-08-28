"""
Production Database Seeds for NitePutter Pro Users
Sample users with different roles and profiles
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
import logging
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongodb, get_database
from app.models.user import User, UserRole, UserStatus, Address
from app.core.security import security

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Users Data
users_data = [
    {
        "email": "admin@niteputterpro.com",
        "password": "AdminPass123!",
        "first_name": "Admin",
        "last_name": "User",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE,
        "is_verified": True,
        "phone": "+1234567890",
        "profile": {
            "bio": "System administrator for NitePutter Pro",
            "golf_handicap": 5.2,
            "years_playing": 15,
            "skill_level": "advanced"
        }
    },
    {
        "email": "staff@niteputterpro.com",
        "password": "StaffPass123!",
        "first_name": "Staff",
        "last_name": "Member",
        "role": UserRole.STAFF,
        "status": UserStatus.ACTIVE,
        "is_verified": True,
        "phone": "+1234567891",
        "profile": {
            "bio": "Customer support specialist",
            "golf_handicap": 12.0,
            "years_playing": 5,
            "skill_level": "intermediate"
        }
    },
    {
        "email": "john.doe@example.com",
        "password": "Customer123!",
        "first_name": "John",
        "last_name": "Doe",
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE,
        "is_verified": True,
        "phone": "+1234567892",
        "loyalty_points": 500,
        "vip_tier": "silver",
        "profile": {
            "bio": "Weekend golfer looking to improve my putting",
            "golf_handicap": 18.5,
            "favorite_course": "Pebble Beach",
            "years_playing": 3,
            "preferred_tee_time": "morning",
            "skill_level": "beginner"
        },
        "addresses": [
            {
                "label": "home",
                "first_name": "John",
                "last_name": "Doe",
                "street_line1": "123 Main Street",
                "city": "Los Angeles",
                "state_province": "CA",
                "postal_code": "90001",
                "country": "US",
                "phone": "+1234567892",
                "is_default": True,
                "is_billing": True,
                "is_shipping": True
            }
        ]
    },
    {
        "email": "jane.smith@example.com",
        "password": "Customer123!",
        "first_name": "Jane",
        "last_name": "Smith",
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE,
        "is_verified": True,
        "phone": "+1234567893",
        "loyalty_points": 1500,
        "vip_tier": "gold",
        "profile": {
            "bio": "Competitive golfer and putting enthusiast",
            "golf_handicap": 8.2,
            "favorite_course": "Augusta National",
            "years_playing": 10,
            "preferred_tee_time": "afternoon",
            "skill_level": "advanced"
        },
        "addresses": [
            {
                "label": "home",
                "first_name": "Jane",
                "last_name": "Smith",
                "street_line1": "456 Oak Avenue",
                "street_line2": "Apt 2B",
                "city": "New York",
                "state_province": "NY",
                "postal_code": "10001",
                "country": "US",
                "phone": "+1234567893",
                "is_default": True,
                "is_billing": True,
                "is_shipping": True
            }
        ]
    },
    {
        "email": "mike.wilson@example.com",
        "password": "Customer123!",
        "first_name": "Mike",
        "last_name": "Wilson",
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE,
        "is_verified": True,
        "phone": "+1234567894",
        "loyalty_points": 250,
        "vip_tier": "bronze",
        "profile": {
            "bio": "Just started playing golf and loving it",
            "golf_handicap": 25.0,
            "years_playing": 1,
            "preferred_tee_time": "evening",
            "skill_level": "beginner"
        }
    },
    {
        "email": "sarah.johnson@example.com",
        "password": "Customer123!",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE,
        "is_verified": True,
        "phone": "+1234567895",
        "loyalty_points": 3000,
        "vip_tier": "platinum",
        "profile": {
            "bio": "Golf instructor and NitePutter Pro ambassador",
            "golf_handicap": 2.1,
            "favorite_course": "St. Andrews",
            "years_playing": 20,
            "preferred_tee_time": "morning",
            "skill_level": "pro"
        },
        "addresses": [
            {
                "label": "home",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "street_line1": "789 Pine Street",
                "city": "Chicago",
                "state_province": "IL",
                "postal_code": "60601",
                "country": "US",
                "phone": "+1234567895",
                "is_default": True,
                "is_billing": True,
                "is_shipping": True
            },
            {
                "label": "work",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "company": "Golf Academy",
                "street_line1": "321 Golf Drive",
                "city": "Chicago",
                "state_province": "IL",
                "postal_code": "60602",
                "country": "US",
                "phone": "+1234567896",
                "is_default": False,
                "is_billing": False,
                "is_shipping": True
            }
        ]
    }
]

async def seed_users():
    """Seed the database with sample users"""
    try:
        # Connect to MongoDB
        await connect_to_mongodb()
        db = await get_database()
        
        # Ask about clearing
        if input("Clear existing users? (y/n): ").lower() == 'y':
            # Keep the original admin if it exists
            admin_backup = await db.users.find_one({"email": "admin@niteputterpro.com"})
            await db.users.delete_many({})
            if admin_backup:
                await db.users.insert_one(admin_backup)
                logger.info("Preserved original admin user")
            else:
                logger.info("Cleared existing users")
        
        # Insert users
        inserted_count = 0
        for user_data in users_data:
            try:
                # Check if user exists
                existing = await db.users.find_one({"email": user_data["email"]})
                if existing:
                    logger.info(f"User already exists: {user_data['email']}")
                    continue
                
                # Create user instance
                user = User(
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    status=user_data["status"],
                    is_verified=user_data["is_verified"],
                    phone=user_data.get("phone"),
                    loyalty_points=user_data.get("loyalty_points", 0),
                    vip_tier=user_data.get("vip_tier"),
                    profile=user_data.get("profile", {}),
                    created_at=datetime.now(UTC) - timedelta(days=random.randint(30, 365))
                )
                
                # Hash password
                user.set_password(user_data["password"])
                
                # Add addresses if provided
                if "addresses" in user_data:
                    user.addresses = [Address(**addr) for addr in user_data["addresses"]]
                
                # Set login history
                if user.is_verified:
                    user.last_login = datetime.now(UTC) - timedelta(days=random.randint(1, 7))
                    user.login_count = random.randint(5, 50)
                
                # Convert to dict for MongoDB
                user_dict = user.model_dump(by_alias=True, exclude_none=True)
                
                # Insert user
                result = await db.users.insert_one(user_dict)
                logger.info(f"Inserted user: {user.email} (Role: {user.role.value})")
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"Error inserting user {user_data['email']}: {e}")
                continue
        
        logger.info(f"Successfully inserted {inserted_count} users")
        
        # Display summary
        print("\n" + "=" * 50)
        print("User Seeding Complete!")
        print("=" * 50)
        
        # Count by role
        for role in UserRole:
            count = await db.users.count_documents({"role": role.value})
            print(f"{role.value.title()}: {count} users")
        
        # Total users
        total = await db.users.count_documents({})
        print(f"\nTotal Users: {total}")
        
        # Display credentials
        print("\n📝 Test Credentials:")
        print("-" * 30)
        for user in users_data[:3]:  # Show first 3 users
            print(f"Email: {user['email']}")
            print(f"Password: {user['password']}")
            print(f"Role: {user['role'].value}")
            print("-" * 30)
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding users: {e}")
        raise

async def main():
    """Run the user seeder"""
    try:
        success = await seed_users()
        if success:
            print("\n✅ User seeding completed successfully!")
        else:
            print("\n❌ User seeding failed")
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"\n❌ Seeding error: {e}")

if __name__ == "__main__":
    print("NitePutter Pro - User Database Seeder")
    print("=" * 50)
    asyncio.run(main())