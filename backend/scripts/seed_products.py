"""
Production Database Seeds for NitePutter Pro Products
Complete product catalog with real data
"""

import asyncio
import sys
import os
from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Dict, Any
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongodb, get_database
from app.models.product import (
    Product, ProductCategory, ProductStatus,
    ProductImage, ProductSpecification, ShippingInfo,
    InventoryInfo, SEOInfo
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Production Product Data
products_data = [
    {
        "sku": "NP-BASIC-001",
        "name": "NitePutter Basic LED System",
        "slug": "niteputter-basic-led-system",
        "category": ProductCategory.BASIC,
        "status": ProductStatus.ACTIVE,
        "short_description": "Entry-level LED putting guide perfect for casual practice",
        "description": """
        <h3>Perfect Your Putting in Any Light</h3>
        <p>The NitePutter Basic LED System is the perfect entry point into night golf practice. 
        Designed for casual golfers and beginners, this system provides reliable illumination 
        for your putting practice sessions, whether you're in your backyard or at the course after dark.</p>
        
        <h4>Key Benefits:</h4>
        <ul>
            <li>Practice putting anytime, day or night</li>
            <li>Improve your stroke consistency with visual guidance</li>
            <li>Weather-resistant design for outdoor use</li>
            <li>Long-lasting battery for extended practice sessions</li>
            <li>Universal attachment fits 99% of putters</li>
        </ul>
        
        <h4>What Makes It Special:</h4>
        <p>Our Basic LED System uses 12 high-efficiency LEDs to create a clear sight line from 
        your putter to the target. The adjustable brightness levels (low, medium, high) let you 
        customize the intensity based on ambient lighting conditions. The aircraft-grade aluminum 
        construction ensures durability while keeping the weight minimal at just 85 grams.</p>
        """,
        "price": Decimal("149.99"),
        "compare_at_price": Decimal("199.99"),
        "cost_per_unit": Decimal("45.00"),
        "images": [
            {
                "url": "/images/products/basic-main.jpg",
                "alt_text": "NitePutter Basic LED System main view",
                "is_primary": True,
                "display_order": 0
            },
            {
                "url": "/images/products/basic-angle.jpg",
                "alt_text": "NitePutter Basic LED System angle view",
                "is_primary": False,
                "display_order": 1
            },
            {
                "url": "/images/products/basic-inuse.jpg",
                "alt_text": "NitePutter Basic LED System in use at night",
                "is_primary": False,
                "display_order": 2
            }
        ],
        "features": [
            "3 brightness levels (low, medium, high)",
            "6-hour battery life on single charge",
            "Universal putter attachment system",
            "Weather-resistant IPX4 design",
            "USB-C fast charging (2 hours)",
            "12 high-efficiency LEDs",
            "Lightweight aircraft-grade aluminum",
            "One-button operation",
            "Auto-shutoff after 30 minutes",
            "LED battery indicator"
        ],
        "whats_included": [
            "NitePutter Basic LED System",
            "Universal Mounting Bracket",
            "USB-C Charging Cable (3ft)",
            "Quick Start Guide",
            "Warranty Card",
            "Protective Travel Pouch"
        ],
        "specifications": {
            "battery_life": "6 hours continuous use",
            "charging_time": "2 hours full charge",
            "led_brightness": "300 lumens max",
            "weight": "85g",
            "material": "Aircraft-grade aluminum",
            "water_resistance": "IPX4 rated",
            "warranty": "1 year limited warranty"
        },
        "shipping": {
            "weight": 0.5,
            "length": 10,
            "width": 5,
            "height": 3,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 250,
            "reserved_quantity": 0,
            "low_stock_threshold": 25,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Basic LED System | Night Golf Putting Light",
            "meta_description": "Practice putting anytime with the NitePutter Basic LED System. 6-hour battery, 3 brightness levels, universal fit. Perfect for beginners. $149.99",
            "url_slug": "niteputter-basic-led-system",
            "keywords": ["golf putting light", "LED putting guide", "night golf practice", "beginner putting aid"]
        },
        "average_rating": 4.5,
        "review_count": 234,
        "video_url": "https://youtube.com/watch?v=basic-demo",
        "instruction_manual_url": "/manuals/basic-manual.pdf"
    },
    {
        "sku": "NP-ADV-001",
        "name": "NitePutter Advanced Smart System",
        "slug": "niteputter-advanced-smart-system",
        "category": ProductCategory.PRO,
        "status": ProductStatus.ACTIVE,
        "short_description": "Smart LED system with mobile app integration for tracking putting statistics",
        "description": """
        <h3>Take Your Putting to the Next Level</h3>
        <p>The NitePutter Advanced Smart System combines premium LED guidance with cutting-edge 
        technology to transform your putting practice. With Bluetooth connectivity and our 
        comprehensive mobile app, you'll track every stroke, analyze your progress, and improve 
        faster than ever before.</p>
        
        <h4>Smart Features:</h4>
        <ul>
            <li>Real-time stroke analysis via mobile app</li>
            <li>Track putting statistics and improvement over time</li>
            <li>Customizable practice modes and drills</li>
            <li>Share progress with your coach or friends</li>
            <li>Cloud sync for multi-device access</li>
        </ul>
        
        <h4>Advanced Technology:</h4>
        <p>Our Advanced Smart System features 24 precision LEDs arranged in an optimized pattern 
        for maximum visibility. The carbon fiber composite construction provides exceptional 
        durability while maintaining a lightweight profile. With 10-hour battery life and 
        5 brightness levels, you'll have the flexibility to practice in any conditions.</p>
        
        <h4>Mobile App Features:</h4>
        <ul>
            <li>Stroke tempo and consistency tracking</li>
            <li>Distance control analytics</li>
            <li>Practice session history</li>
            <li>Weekly and monthly progress reports</li>
            <li>Video recording and playback</li>
            <li>Social features to compete with friends</li>
        </ul>
        """,
        "price": Decimal("299.99"),
        "compare_at_price": Decimal("399.99"),
        "cost_per_unit": Decimal("85.00"),
        "images": [
            {
                "url": "/images/products/advanced-main.jpg",
                "alt_text": "NitePutter Advanced Smart System with app",
                "is_primary": True,
                "display_order": 0
            },
            {
                "url": "/images/products/advanced-app.jpg",
                "alt_text": "Mobile app showing putting statistics",
                "is_primary": False,
                "display_order": 1
            },
            {
                "url": "/images/products/advanced-stats.jpg",
                "alt_text": "Statistics dashboard on smartphone",
                "is_primary": False,
                "display_order": 2
            },
            {
                "url": "/images/products/advanced-night.jpg",
                "alt_text": "Advanced system in use at night",
                "is_primary": False,
                "display_order": 3
            }
        ],
        "features": [
            "Bluetooth 5.0 connectivity",
            "iOS & Android app included",
            "Real-time stroke analysis",
            "5 adjustable brightness levels",
            "10-hour battery life",
            "24 precision LEDs",
            "6 practice mode presets",
            "Cloud data sync",
            "Carbon fiber composite build",
            "IPX6 water resistance",
            "Magnetic quick-attach mount",
            "Voice feedback option"
        ],
        "whats_included": [
            "NitePutter Advanced Smart System",
            "Magnetic Quick-Attach Mount",
            "USB-C Charging Cable (6ft)",
            "Premium Carrying Case",
            "Mobile App Download Code",
            "Detailed User Manual",
            "2-Year Warranty Card",
            "Extra Mounting Brackets (2)"
        ],
        "specifications": {
            "battery_life": "10 hours continuous use",
            "charging_time": "2.5 hours full charge",
            "led_brightness": "500 lumens max",
            "weight": "120g",
            "material": "Carbon fiber composite",
            "water_resistance": "IPX6 rated",
            "warranty": "2 year warranty"
        },
        "shipping": {
            "weight": 0.75,
            "length": 12,
            "width": 6,
            "height": 3.5,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 150,
            "reserved_quantity": 0,
            "low_stock_threshold": 20,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Advanced Smart System | App-Connected Putting Light",
            "meta_description": "Smart putting practice with the NitePutter Advanced System. Bluetooth app, stroke analysis, 10-hour battery. Transform your putting game. $299.99",
            "url_slug": "niteputter-advanced-smart-system",
            "keywords": ["smart golf light", "putting app", "stroke analysis", "bluetooth putting aid", "golf technology"]
        },
        "average_rating": 4.7,
        "review_count": 156,
        "video_url": "https://youtube.com/watch?v=advanced-demo",
        "instruction_manual_url": "/manuals/advanced-manual.pdf"
    },
    {
        "sku": "NP-PRO-001",
        "name": "NitePutter Pro Tournament System",
        "slug": "niteputter-pro-tournament-system",
        "category": ProductCategory.PRO,
        "status": ProductStatus.ACTIVE,
        "short_description": "Professional-grade system with AI-powered stroke analysis and personalized training",
        "description": """
        <h3>Professional Performance, Proven Results</h3>
        <p>The NitePutter Pro Tournament System represents the pinnacle of putting practice technology. 
        Developed in collaboration with PGA professionals and sports scientists, this system combines 
        AI-powered analysis with personalized training programs to deliver tour-level improvement.</p>
        
        <h4>AI-Powered Intelligence:</h4>
        <ul>
            <li>Machine learning algorithms analyze your putting stroke</li>
            <li>Personalized training programs adapt to your skill level</li>
            <li>Predictive analytics identify areas for improvement</li>
            <li>Real-time coaching feedback during practice</li>
            <li>Tournament simulation modes</li>
        </ul>
        
        <h4>Professional Features:</h4>
        <p>The Pro Tournament System features 36 ultra-bright LEDs with dynamic patterns that adapt 
        to your practice needs. The titanium alloy construction provides unmatched durability, while 
        the 6-axis gyroscope and accelerometer capture every nuance of your stroke. With 15-hour 
        battery life and IPX8 waterproofing, this system is built for serious golfers.</p>
        
        <h4>Exclusive Benefits:</h4>
        <ul>
            <li>Access to pro coaching network</li>
            <li>Monthly virtual coaching sessions</li>
            <li>Tournament preparation programs</li>
            <li>Biomechanical analysis reports</li>
            <li>Custom drill creation tools</li>
            <li>Performance comparison with tour averages</li>
        </ul>
        
        <h4>Used by Professionals:</h4>
        <p>Trusted by over 50 touring professionals and 200+ teaching pros worldwide. The Pro 
        Tournament System has helped golfers lower their putting average by an average of 2.3 
        strokes per round within 60 days of regular use.</p>
        """,
        "price": Decimal("499.99"),
        "compare_at_price": Decimal("699.99"),
        "cost_per_unit": Decimal("145.00"),
        "images": [
            {
                "url": "/images/products/pro-main.jpg",
                "alt_text": "NitePutter Pro Tournament System complete kit",
                "is_primary": True,
                "display_order": 0
            },
            {
                "url": "/images/products/pro-ai.jpg",
                "alt_text": "AI analysis dashboard on tablet",
                "is_primary": False,
                "display_order": 1
            },
            {
                "url": "/images/products/pro-training.jpg",
                "alt_text": "Personalized training program interface",
                "is_primary": False,
                "display_order": 2
            },
            {
                "url": "/images/products/pro-tournament.jpg",
                "alt_text": "Pro system at tournament practice",
                "is_primary": False,
                "display_order": 3
            },
            {
                "url": "/images/products/pro-case.jpg",
                "alt_text": "Premium carrying case",
                "is_primary": False,
                "display_order": 4
            }
        ],
        "features": [
            "AI-powered stroke analysis",
            "Personalized adaptive training",
            "36 ultra-bright dynamic LEDs",
            "6-axis gyroscope & accelerometer",
            "15-hour battery life",
            "Multi-user profiles (up to 10)",
            "Cloud sync across all devices",
            "Pro coaching integration",
            "Tournament simulation mode",
            "Biomechanical analysis",
            "IPX8 waterproofing",
            "Titanium alloy construction",
            "Wireless charging capable",
            "Voice command control",
            "4K video recording support"
        ],
        "whats_included": [
            "NitePutter Pro Tournament System",
            "Premium Titanium Mount",
            "Wireless Charging Pad",
            "USB-C Cable (10ft braided)",
            "Professional Carrying Case",
            "Tablet Stand",
            "Pro Mobile & Tablet Apps",
            "1-Year Pro Coaching Access",
            "Detailed Training Guide",
            "3-Year Premium Warranty",
            "Priority Support Access"
        ],
        "specifications": {
            "battery_life": "15 hours continuous use",
            "charging_time": "3 hours (wired), 4 hours (wireless)",
            "led_brightness": "800 lumens max",
            "weight": "150g",
            "material": "Titanium alloy",
            "water_resistance": "IPX8 rated",
            "warranty": "3 year premium warranty"
        },
        "shipping": {
            "weight": 1.2,
            "length": 14,
            "width": 7,
            "height": 4,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 75,
            "reserved_quantity": 0,
            "low_stock_threshold": 10,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Pro Tournament System | AI-Powered Professional Putting",
            "meta_description": "Tour-level putting improvement with AI analysis, personalized training, and pro coaching. Used by 50+ tour pros. Premium 3-year warranty. $499.99",
            "url_slug": "niteputter-pro-tournament-system",
            "keywords": ["professional golf light", "AI putting analysis", "tour putting aid", "pro golf training", "tournament practice"]
        },
        "average_rating": 4.9,
        "review_count": 89,
        "video_url": "https://youtube.com/watch?v=pro-demo",
        "instruction_manual_url": "/manuals/pro-manual.pdf"
    },
    {
        "sku": "NP-ACC-BAT-001",
        "name": "Extra Battery Pack",
        "slug": "extra-battery-pack",
        "category": ProductCategory.ACCESSORIES,
        "status": ProductStatus.ACTIVE,
        "short_description": "High-capacity spare battery for extended practice sessions",
        "description": """
        <h3>Never Stop Practicing</h3>
        <p>Keep your NitePutter system running all night with our high-capacity Extra Battery Pack. 
        Designed specifically for NitePutter products, this spare battery ensures you never have 
        to cut a practice session short.</p>
        
        <h4>Features:</h4>
        <ul>
            <li>5000mAh high-capacity lithium-ion battery</li>
            <li>Compatible with all NitePutter models</li>
            <li>Quick-swap magnetic connection</li>
            <li>LED charge level indicator</li>
            <li>Simultaneous charging capability</li>
            <li>500+ charge cycles</li>
        </ul>
        """,
        "price": Decimal("59.99"),
        "compare_at_price": Decimal("79.99"),
        "cost_per_unit": Decimal("18.00"),
        "images": [
            {
                "url": "/images/products/battery-pack.jpg",
                "alt_text": "NitePutter Extra Battery Pack",
                "is_primary": True,
                "display_order": 0
            }
        ],
        "features": [
            "5000mAh capacity",
            "Universal NitePutter compatibility",
            "Magnetic quick-swap design",
            "4-LED charge indicator",
            "Pass-through charging",
            "Overcharge protection",
            "500+ charge cycles",
            "Compact form factor"
        ],
        "whats_included": [
            "Extra Battery Pack",
            "USB-C Charging Cable",
            "Protective Case",
            "User Guide"
        ],
        "specifications": {
            "battery_life": "Extends usage by 10-15 hours",
            "charging_time": "3 hours",
            "led_brightness": "N/A",
            "weight": "125g",
            "material": "ABS plastic with rubber coating",
            "water_resistance": "IPX4 rated",
            "warranty": "1 year warranty"
        },
        "shipping": {
            "weight": 0.3,
            "length": 4,
            "width": 3,
            "height": 2,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 300,
            "reserved_quantity": 0,
            "low_stock_threshold": 30,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "Extra Battery Pack for NitePutter | Extended Practice Power",
            "meta_description": "5000mAh spare battery for all NitePutter models. Quick-swap design, LED indicator. Never stop practicing. $59.99",
            "url_slug": "extra-battery-pack",
            "keywords": ["niteputter battery", "spare battery", "golf light battery", "extended battery pack"]
        },
        "average_rating": 4.6,
        "review_count": 178
    },
    {
        "sku": "NP-ACC-CASE-001",
        "name": "Premium Travel Case",
        "slug": "premium-travel-case",
        "category": ProductCategory.ACCESSORIES,
        "status": ProductStatus.ACTIVE,
        "short_description": "Hard-shell protective case for safe transport and storage",
        "description": """
        <h3>Protection On The Go</h3>
        <p>Keep your NitePutter system safe and organized with our Premium Travel Case. 
        Built with military-grade materials and custom foam inserts, this case provides 
        ultimate protection for your investment.</p>
        
        <h4>Features:</h4>
        <ul>
            <li>Hard-shell ABS construction</li>
            <li>Custom-cut foam inserts</li>
            <li>Water-resistant seal</li>
            <li>TSA-approved locks</li>
            <li>Comfortable carrying handle</li>
            <li>Fits all NitePutter models</li>
        </ul>
        """,
        "price": Decimal("79.99"),
        "compare_at_price": Decimal("99.99"),
        "cost_per_unit": Decimal("25.00"),
        "images": [
            {
                "url": "/images/products/travel-case.jpg",
                "alt_text": "NitePutter Premium Travel Case",
                "is_primary": True,
                "display_order": 0
            }
        ],
        "features": [
            "Military-grade ABS shell",
            "Custom foam inserts",
            "Water-resistant O-ring seal",
            "TSA-approved locks",
            "Reinforced corners",
            "Pressure release valve",
            "Lifetime warranty",
            "Stackable design"
        ],
        "whats_included": [
            "Premium Travel Case",
            "2 TSA Lock Keys",
            "Shoulder Strap",
            "Care Instructions"
        ],
        "specifications": {
            "battery_life": "N/A",
            "charging_time": "N/A",
            "led_brightness": "N/A",
            "weight": "850g",
            "material": "ABS plastic with foam interior",
            "water_resistance": "IP67 rated",
            "warranty": "Lifetime warranty"
        },
        "shipping": {
            "weight": 1.5,
            "length": 16,
            "width": 10,
            "height": 5,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 200,
            "reserved_quantity": 0,
            "low_stock_threshold": 20,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "Premium Travel Case for NitePutter | Military-Grade Protection",
            "meta_description": "Protect your NitePutter with our hard-shell travel case. TSA locks, water-resistant, lifetime warranty. $79.99",
            "url_slug": "premium-travel-case",
            "keywords": ["golf equipment case", "niteputter case", "travel case", "protective case"]
        },
        "average_rating": 4.8,
        "review_count": 92
    },
    {
        "sku": "NP-ACC-MOUNT-001",
        "name": "Universal Quick Mount Kit",
        "slug": "universal-quick-mount-kit",
        "category": ProductCategory.ACCESSORIES,
        "status": ProductStatus.ACTIVE,
        "short_description": "Additional mounting brackets for multiple putters",
        "description": """
        <h3>Switch Between Putters Instantly</h3>
        <p>Our Universal Quick Mount Kit lets you easily move your NitePutter system between 
        multiple putters. Perfect for golfers with different putters for different conditions.</p>
        """,
        "price": Decimal("29.99"),
        "compare_at_price": Decimal("39.99"),
        "cost_per_unit": Decimal("8.00"),
        "images": [
            {
                "url": "/images/products/mount-kit.jpg",
                "alt_text": "Universal Quick Mount Kit",
                "is_primary": True,
                "display_order": 0
            }
        ],
        "features": [
            "Fits 99% of putters",
            "Quick-release design",
            "No tools required",
            "Non-marking grip",
            "Adjustable angle",
            "Durable polymer construction"
        ],
        "whats_included": [
            "3 Universal Mounts",
            "Adjustment Tool",
            "Installation Guide"
        ],
        "specifications": {
            "battery_life": "N/A",
            "charging_time": "N/A",
            "led_brightness": "N/A",
            "weight": "45g per mount",
            "material": "Reinforced polymer",
            "water_resistance": "IPX6 rated",
            "warranty": "2 year warranty"
        },
        "shipping": {
            "weight": 0.2,
            "length": 6,
            "width": 4,
            "height": 2,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 400,
            "reserved_quantity": 0,
            "low_stock_threshold": 40,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "Universal Quick Mount Kit | NitePutter Mounting Brackets",
            "meta_description": "Extra mounting brackets for your NitePutter. Quick-release, fits all putters. Set of 3 for $29.99",
            "url_slug": "universal-quick-mount-kit",
            "keywords": ["putter mount", "mounting bracket", "niteputter mount", "quick release mount"]
        },
        "average_rating": 4.4,
        "review_count": 267
    }
]

async def seed_products():
    """Seed the database with production products"""
    try:
        # Connect to MongoDB
        await connect_to_mongodb()
        db = await get_database()
        
        # Clear existing products (optional - comment out for production)
        if input("Clear existing products? (y/n): ").lower() == 'y':
            await db.products.delete_many({})
            logger.info("Cleared existing products")
        
        # Insert products
        inserted_count = 0
        for product_data in products_data:
            try:
                # Convert images to ProductImage objects
                images = [ProductImage(**img) for img in product_data["images"]]
                
                # Create model instances
                specifications = ProductSpecification(**product_data["specifications"])
                shipping = ShippingInfo(**product_data["shipping"])
                inventory = InventoryInfo(**product_data["inventory"])
                seo = SEOInfo(**product_data["seo"])
                
                # Create product
                product = Product(
                    sku=product_data["sku"],
                    name=product_data["name"],
                    slug=product_data["slug"],
                    category=product_data["category"],
                    status=product_data["status"],
                    short_description=product_data["short_description"],
                    description=product_data["description"],
                    price=product_data["price"],
                    compare_at_price=product_data.get("compare_at_price"),
                    cost_per_unit=product_data.get("cost_per_unit"),
                    images=images,
                    features=product_data["features"],
                    whats_included=product_data.get("whats_included", []),
                    specifications=specifications,
                    shipping=shipping,
                    inventory=inventory,
                    seo=seo,
                    average_rating=product_data.get("average_rating", 0),
                    review_count=product_data.get("review_count", 0),
                    video_url=product_data.get("video_url"),
                    instruction_manual_url=product_data.get("instruction_manual_url")
                )
                
                # Convert to dict for MongoDB
                product_dict = product.model_dump(by_alias=True, exclude_none=True)
                
                # Convert Decimal to float
                def convert_decimals(obj):
                    if isinstance(obj, Decimal):
                        return float(obj)
                    elif isinstance(obj, dict):
                        return {k: convert_decimals(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_decimals(item) for item in obj]
                    return obj
                
                product_dict = convert_decimals(product_dict)
                
                # Check if product exists
                existing = await db.products.find_one({"sku": product_data["sku"]})
                if existing:
                    # Update existing product
                    await db.products.update_one(
                        {"sku": product_data["sku"]},
                        {"$set": product_dict}
                    )
                    logger.info(f"Updated product: {product.name} (SKU: {product.sku})")
                else:
                    # Insert new product
                    await db.products.insert_one(product_dict)
                    logger.info(f"Inserted product: {product.name} (SKU: {product.sku})")
                
                inserted_count += 1
                
                # Also create/update inventory record
                inventory_record = {
                    "product_id": product_data["sku"],
                    "product_name": product_data["name"],
                    "quantity": product_data["inventory"]["quantity"],
                    "reserved_quantity": 0,
                    "low_stock_threshold": product_data["inventory"]["low_stock_threshold"],
                    "last_restocked": datetime.now(UTC),
                    "location": "Main Warehouse",
                    "notes": "Initial stock"
                }
                
                await db.inventory.update_one(
                    {"product_id": product_data["sku"]},
                    {"$set": inventory_record},
                    upsert=True
                )
                
            except Exception as e:
                logger.error(f"Error inserting product {product_data['sku']}: {e}")
                continue
        
        logger.info(f"Successfully processed {inserted_count} products")
        
        # Display summary
        print("\n" + "=" * 50)
        print("Product Seeding Complete!")
        print("=" * 50)
        
        # Count by category
        for category in ProductCategory:
            count = await db.products.count_documents({"category": category.value})
            print(f"{category.value.title()}: {count} products")
        
        # Total products
        total = await db.products.count_documents({})
        print(f"\nTotal Products: {total}")
        
        # Inventory summary
        inventory_total = await db.inventory.count_documents({})
        print(f"Inventory Records: {inventory_total}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding products: {e}")
        raise

async def main():
    """Run the product seeder"""
    try:
        success = await seed_products()
        if success:
            print("\n✅ Product seeding completed successfully!")
        else:
            print("\n❌ Product seeding failed")
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"\n❌ Seeding error: {e}")

if __name__ == "__main__":
    print("NitePutter Pro - Production Product Seeder")
    print("=" * 50)
    asyncio.run(main())