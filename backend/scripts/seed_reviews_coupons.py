"""
Production Database Seeds for Reviews and Coupons
Sample product reviews and promotional coupons
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from typing import List, Dict, Any
import logging
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongodb, get_database
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Reviews Data
reviews_data = [
    # NitePutter Basic LED System Reviews
    {
        "product_sku": "NPP-BASIC-001",
        "reviews": [
            {
                "customer_name": "John D.",
                "customer_email": "john.doe@example.com",
                "rating": 5,
                "title": "Game Changer!",
                "comment": "This has completely transformed my evening practice sessions. The LED is bright enough without being distracting, and the battery life is excellent. Highly recommend for anyone wanting to practice after work.",
                "verified_purchase": True,
                "helpful_count": 45,
                "images": []
            },
            {
                "customer_name": "Mike W.",
                "customer_email": "mike.wilson@example.com",
                "rating": 4,
                "title": "Great value for money",
                "comment": "Good quality product for the price. The mount is sturdy and fits my putter perfectly. Only wish it had more brightness levels, but the 3 options work well enough.",
                "verified_purchase": True,
                "helpful_count": 32,
                "images": []
            },
            {
                "customer_name": "David S.",
                "customer_email": "david.s@example.com",
                "rating": 5,
                "title": "Perfect for beginners",
                "comment": "As someone new to golf, this has helped me practice my putting form consistently. The visual guide really helps with alignment. Battery charges quickly too.",
                "verified_purchase": True,
                "helpful_count": 28,
                "images": []
            },
            {
                "customer_name": "Robert L.",
                "customer_email": "robert.l@example.com",
                "rating": 4,
                "title": "Solid product",
                "comment": "Does exactly what it promises. Easy to attach, bright enough for night practice, and seems durable. Been using it for 2 months with no issues.",
                "verified_purchase": True,
                "helpful_count": 19,
                "images": []
            }
        ]
    },
    # NitePutter Pro LED System Reviews
    {
        "product_sku": "NPP-PRO-001",
        "reviews": [
            {
                "customer_name": "Jane S.",
                "customer_email": "jane.smith@example.com",
                "rating": 5,
                "title": "Worth every penny!",
                "comment": "This Pro LED System has completely transformed my practice sessions! The bright LEDs make night practice incredibly effective. The battery life is amazing - easily gets 10+ hours.",
                "verified_purchase": True,
                "helpful_count": 67,
                "images": []
            },
            {
                "customer_name": "Tom B.",
                "customer_email": "tom.b@example.com",
                "rating": 5,
                "title": "Professional quality",
                "comment": "I'm a golf instructor and bought this Pro system for my students. The adjustable brightness and multiple mounting options are perfect for different training scenarios. The build quality is exceptional.",
                "verified_purchase": True,
                "helpful_count": 54,
                "images": []
            },
            {
                "customer_name": "Lisa M.",
                "customer_email": "lisa.m@example.com",
                "rating": 4,
                "title": "Great features, minor app issues",
                "comment": "Love the Pro hardware and the concept. The magnetic mount is incredibly secure and the USB-C charging is convenient. Customer support was helpful with setup.",
                "verified_purchase": True,
                "helpful_count": 41,
                "images": []
            }
        ]
    },
    # NitePutter Complete Practice Kit Reviews
    {
        "product_sku": "NPP-COMPLETE-001",
        "reviews": [
            {
                "customer_name": "Sarah J.",
                "customer_email": "sarah.johnson@example.com",
                "rating": 5,
                "title": "Tour-level equipment",
                "comment": "As a competitive golfer, this Complete Practice Kit has everything I need. The putting mat, alignment tools, and LED system work perfectly together. Has helped me drop 2 strokes from my putting average. The carrying case makes it easy to take anywhere.",
                "verified_purchase": True,
                "helpful_count": 89,
                "images": []
            },
            {
                "customer_name": "Mark T.",
                "customer_email": "mark.t@example.com",
                "rating": 5,
                "title": "Exceeded expectations",
                "comment": "I was skeptical about the price but this Complete Kit is professional equipment. The premium putting mat is tour quality, the LED system is brilliant, and everything fits in the included case. Has genuinely improved my game.",
                "verified_purchase": True,
                "helpful_count": 76,
                "images": []
            }
        ]
    }
]

# Sample Coupons Data
coupons_data = [
    {
        "code": "WELCOME10",
        "description": "10% off your first purchase",
        "type": "percentage",
        "value": Decimal("10"),
        "min_purchase": Decimal("100"),
        "usage_limit": 1000,
        "usage_count": 342,
        "valid_from": datetime.now(UTC) - timedelta(days=30),
        "valid_until": datetime.now(UTC) + timedelta(days=60),
        "is_active": True,
        "applicable_products": [],  # All products
        "applicable_categories": []  # All categories
    },
    {
        "code": "SUMMER25",
        "description": "$25 off orders over $200",
        "type": "fixed_amount",
        "value": Decimal("25"),
        "min_purchase": Decimal("200"),
        "usage_limit": 500,
        "usage_count": 127,
        "valid_from": datetime.now(UTC) - timedelta(days=15),
        "valid_until": datetime.now(UTC) + timedelta(days=45),
        "is_active": True,
        "applicable_products": [],
        "applicable_categories": []
    },
    {
        "code": "PROUSER",
        "description": "15% off Pro LED System",
        "type": "percentage",
        "value": Decimal("15"),
        "min_purchase": Decimal("0"),
        "usage_limit": 100,
        "usage_count": 23,
        "valid_from": datetime.now(UTC),
        "valid_until": datetime.now(UTC) + timedelta(days=30),
        "is_active": True,
        "applicable_products": ["NPP-PRO-001"],
        "applicable_categories": []
    },
    {
        "code": "BUNDLE20",
        "description": "20% off when buying 2+ items",
        "type": "percentage",
        "value": Decimal("20"),
        "min_purchase": Decimal("250"),
        "min_items": 2,
        "usage_limit": 200,
        "usage_count": 45,
        "valid_from": datetime.now(UTC),
        "valid_until": datetime.now(UTC) + timedelta(days=90),
        "is_active": True,
        "applicable_products": [],
        "applicable_categories": []
    },
    {
        "code": "MILITARY15",
        "description": "15% military discount",
        "type": "percentage",
        "value": Decimal("15"),
        "min_purchase": Decimal("0"),
        "usage_limit": None,  # Unlimited
        "usage_count": 89,
        "valid_from": datetime.now(UTC) - timedelta(days=365),
        "valid_until": datetime.now(UTC) + timedelta(days=365),
        "is_active": True,
        "applicable_products": [],
        "applicable_categories": [],
        "requires_verification": True
    },
    {
        "code": "FREESHIP",
        "description": "Free shipping on orders over $150",
        "type": "free_shipping",
        "value": Decimal("0"),
        "min_purchase": Decimal("150"),
        "usage_limit": 1000,
        "usage_count": 456,
        "valid_from": datetime.now(UTC) - timedelta(days=7),
        "valid_until": datetime.now(UTC) + timedelta(days=23),
        "is_active": True,
        "applicable_products": [],
        "applicable_categories": []
    }
]

async def seed_reviews():
    """Seed the database with product reviews"""
    try:
        db = await get_database()
        
        inserted_count = 0
        
        for product_reviews in reviews_data:
            product_sku = product_reviews["product_sku"]
            
            # Get product
            product = await db.products.find_one({"sku": product_sku})
            if not product:
                logger.warning(f"Product not found: {product_sku}")
                continue
            
            for review_data in product_reviews["reviews"]:
                try:
                    # Create review document
                    review = {
                        "product_id": str(product["_id"]),
                        "product_sku": product_sku,
                        "customer_name": review_data["customer_name"],
                        "customer_email": review_data["customer_email"],
                        "rating": review_data["rating"],
                        "title": review_data["title"],
                        "comment": review_data["comment"],
                        "verified_purchase": review_data["verified_purchase"],
                        "helpful_count": review_data["helpful_count"],
                        "not_helpful_count": random.randint(0, 5),
                        "images": review_data["images"],
                        "created_at": datetime.now(UTC) - timedelta(days=random.randint(1, 180)),
                        "updated_at": datetime.now(UTC),
                        "status": "approved",
                        "featured": review_data["rating"] == 5 and review_data["helpful_count"] > 50
                    }
                    
                    # Check if review exists
                    existing = await db.reviews.find_one({
                        "product_sku": product_sku,
                        "customer_email": review_data["customer_email"]
                    })
                    
                    if not existing:
                        await db.reviews.insert_one(review)
                        inserted_count += 1
                        logger.info(f"Inserted review for {product_sku} by {review_data['customer_name']}")
                    
                except Exception as e:
                    logger.error(f"Error inserting review: {e}")
                    continue
        
        # Update product ratings
        for product_reviews in reviews_data:
            product_sku = product_reviews["product_sku"]
            
            # Calculate average rating
            reviews = await db.reviews.find({"product_sku": product_sku}).to_list(None)
            if reviews:
                avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
                review_count = len(reviews)
                
                await db.products.update_one(
                    {"sku": product_sku},
                    {"$set": {
                        "average_rating": round(avg_rating, 1),
                        "review_count": review_count
                    }}
                )
                logger.info(f"Updated {product_sku}: rating={avg_rating:.1f}, count={review_count}")
        
        logger.info(f"Successfully inserted {inserted_count} reviews")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Error seeding reviews: {e}")
        raise

async def seed_coupons():
    """Seed the database with promotional coupons"""
    try:
        db = await get_database()
        
        inserted_count = 0
        
        for coupon_data in coupons_data:
            try:
                # Convert Decimal to float for MongoDB
                coupon = {
                    "code": coupon_data["code"],
                    "description": coupon_data["description"],
                    "type": coupon_data["type"],
                    "value": float(coupon_data["value"]),
                    "min_purchase": float(coupon_data["min_purchase"]),
                    "min_items": coupon_data.get("min_items", 1),
                    "usage_limit": coupon_data["usage_limit"],
                    "usage_count": coupon_data["usage_count"],
                    "valid_from": coupon_data["valid_from"],
                    "valid_until": coupon_data["valid_until"],
                    "is_active": coupon_data["is_active"],
                    "applicable_products": coupon_data["applicable_products"],
                    "applicable_categories": coupon_data["applicable_categories"],
                    "requires_verification": coupon_data.get("requires_verification", False),
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC)
                }
                
                # Check if coupon exists
                existing = await db.coupons.find_one({"code": coupon_data["code"]})
                
                if existing:
                    # Update existing coupon
                    await db.coupons.update_one(
                        {"code": coupon_data["code"]},
                        {"$set": coupon}
                    )
                    logger.info(f"Updated coupon: {coupon_data['code']}")
                else:
                    # Insert new coupon
                    await db.coupons.insert_one(coupon)
                    logger.info(f"Inserted coupon: {coupon_data['code']}")
                
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"Error inserting coupon {coupon_data['code']}: {e}")
                continue
        
        logger.info(f"Successfully processed {inserted_count} coupons")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Error seeding coupons: {e}")
        raise

async def main():
    """Run the review and coupon seeder"""
    try:
        # Connect to MongoDB
        await connect_to_mongodb()
        
        print("NitePutter Pro - Reviews & Coupons Seeder")
        print("=" * 50)
        
        # Ask about clearing
        if input("Clear existing reviews? (y/n): ").lower() == 'y':
            db = await get_database()
            await db.reviews.delete_many({})
            logger.info("Cleared existing reviews")
        
        if input("Clear existing coupons? (y/n): ").lower() == 'y':
            db = await get_database()
            await db.coupons.delete_many({})
            logger.info("Cleared existing coupons")
        
        # Seed reviews
        print("\nSeeding Reviews...")
        review_count = await seed_reviews()
        
        # Seed coupons
        print("\nSeeding Coupons...")
        coupon_count = await seed_coupons()
        
        # Display summary
        db = await get_database()
        
        print("\n" + "=" * 50)
        print("Seeding Complete!")
        print("=" * 50)
        
        # Reviews summary
        total_reviews = await db.reviews.count_documents({})
        print(f"\n📝 Reviews: {total_reviews} total")
        
        # Show review distribution
        for rating in range(5, 0, -1):
            count = await db.reviews.count_documents({"rating": rating})
            stars = "⭐" * rating
            print(f"  {stars}: {count} reviews")
        
        # Coupons summary
        total_coupons = await db.coupons.count_documents({})
        active_coupons = await db.coupons.count_documents({"is_active": True})
        print(f"\n🎟️  Coupons: {total_coupons} total ({active_coupons} active)")
        
        # Show active coupon codes
        print("\n📋 Active Coupon Codes:")
        active = await db.coupons.find({"is_active": True}).to_list(None)
        for coupon in active:
            print(f"  • {coupon['code']}: {coupon['description']}")
        
        print("\n✅ Reviews and coupons seeding completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"\n❌ Seeding error: {e}")

if __name__ == "__main__":
    asyncio.run(main())