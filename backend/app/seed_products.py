"""
Seed NitePutter Pro Product Catalog
Real production data for golf lighting products
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import logging
from database import connect_to_mongodb, get_database
from models.product import (
    Product, ProductCategory, ProductStatus, 
    ProductImage, ProductSpecification, ShippingInfo, 
    InventoryInfo, SEOInfo
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real NitePutter Product Catalog
NITEPUTTER_PRODUCTS = [
    {
        "sku": "NPP-BASIC-001",
        "name": "NitePutter Basic LED Light",
        "slug": "niteputter-basic-led-light",
        "category": ProductCategory.BASIC,
        "status": ProductStatus.ACTIVE,
        "short_description": "Essential LED lighting for night putting practice with easy clip-on design",
        "description": """
        <h3>Perfect Your Putting Day or Night</h3>
        <p>The NitePutter Basic LED Light transforms your putter into a precision training tool that works 24/7. 
        Engineered with professional-grade components and backed by veteran craftsmanship, this essential 
        lighting system lets you practice your putting stroke anytime, anywhere.</p>
        
        <h4>Key Features:</h4>
        <ul>
            <li>500 lumen high-intensity LED for optimal ball and line visibility</li>
            <li>Universal clip design fits 99% of putters on the market</li>
            <li>8-10 hour battery life on a single charge</li>
            <li>USB-C fast charging - fully charged in 2 hours</li>
            <li>Weather-resistant IPX6 rating for outdoor use</li>
            <li>Lightweight aircraft-grade aluminum construction (45g)</li>
        </ul>
        
        <h4>Why Choose NitePutter Basic?</h4>
        <p>Whether you're an early morning golfer or prefer evening practice sessions, the NitePutter Basic 
        ensures you never miss a practice opportunity. The precision-engineered light angle illuminates both 
        your ball and target line without creating shadows or glare.</p>
        """,
        "features": [
            "500 lumen LED brightness",
            "8-10 hour battery life",
            "USB-C fast charging (2 hours)",
            "Universal putter compatibility",
            "IPX6 weather resistance",
            "45g lightweight design",
            "Aircraft-grade aluminum body",
            "One-touch on/off operation"
        ],
        "whats_included": [
            "NitePutter Basic LED Light",
            "USB-C Charging Cable (3ft)",
            "Universal Mounting Clip",
            "Quick Start Guide",
            "Warranty Registration Card"
        ],
        "price": Decimal("149.99"),
        "compare_at_price": Decimal("179.99"),
        "cost_per_unit": Decimal("52.00"),
        "images": [
            {
                "url": "/images/products/basic-led-main.jpg",
                "alt_text": "NitePutter Basic LED Light mounted on putter",
                "is_primary": True,
                "display_order": 0
            },
            {
                "url": "/images/products/basic-led-angle.jpg",
                "alt_text": "NitePutter Basic LED Light side view",
                "is_primary": False,
                "display_order": 1
            },
            {
                "url": "/images/products/basic-led-night.jpg",
                "alt_text": "NitePutter Basic in use at night",
                "is_primary": False,
                "display_order": 2
            }
        ],
        "video_url": "https://youtube.com/watch?v=niteputter-basic-demo",
        "instruction_manual_url": "/manuals/niteputter-basic-manual.pdf",
        "specifications": {
            "battery_life": "8-10 hours continuous use",
            "charging_time": "2 hours full charge",
            "led_brightness": "500 lumens",
            "weight": "45g",
            "material": "Aircraft-grade aluminum",
            "water_resistance": "IPX6 rated",
            "warranty": "2 year limited warranty"
        },
        "shipping": {
            "weight": 0.5,
            "length": 6,
            "width": 4,
            "height": 2,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 250,
            "reserved_quantity": 0,
            "low_stock_threshold": 20,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Basic LED Light | Night Golf Putting Practice",
            "meta_description": "Transform your putting practice with the NitePutter Basic LED Light. 500 lumens, 8-10 hour battery, universal fit. Perfect for day or night practice.",
            "url_slug": "niteputter-basic-led-light",
            "keywords": ["golf light", "putting light", "night golf", "LED putter light", "golf training aid"]
        },
        "average_rating": 4.7,
        "review_count": 142
    },
    {
        "sku": "NPP-PRO-001",
        "name": "NitePutter Pro LED System",
        "slug": "niteputter-pro-led-system",
        "category": ProductCategory.PRO,
        "status": ProductStatus.ACTIVE,
        "short_description": "Professional-grade LED system with adjustable brightness and advanced features",
        "description": """
        <h3>The Choice of Serious Golfers</h3>
        <p>The NitePutter Pro LED System represents the pinnacle of golf lighting technology. Designed in 
        collaboration with PGA professionals and tested by thousands of golfers, this advanced system delivers 
        unmatched performance for serious practice sessions.</p>
        
        <h4>Advanced Technology:</h4>
        <ul>
            <li>Variable brightness control (100-1000 lumens) with memory function</li>
            <li>Dual-beam technology illuminates ball and target line independently</li>
            <li>Smart battery management with LED indicator</li>
            <li>Bluetooth connectivity for mobile app control</li>
            <li>Premium carbon fiber and titanium construction</li>
            <li>Advanced optics for zero shadow casting</li>
        </ul>
        
        <h4>Professional Performance:</h4>
        <p>Used by golf instructors and serious players worldwide, the Pro System's adjustable brightness and 
        dual-beam technology ensure perfect visibility in any lighting condition. The companion mobile app 
        tracks your practice sessions and provides performance analytics.</p>
        """,
        "features": [
            "100-1000 lumen adjustable brightness",
            "Dual-beam independent lighting",
            "12-15 hour battery life",
            "Bluetooth app connectivity",
            "Carbon fiber & titanium build",
            "Smart battery management",
            "Memory brightness settings",
            "Zero shadow optics",
            "Magnetic quick-release mount"
        ],
        "whats_included": [
            "NitePutter Pro LED System",
            "Magnetic Quick-Release Mount",
            "USB-C Charging Cable (6ft)",
            "Protective Carrying Case",
            "Mobile App Access Code",
            "Professional Setup Guide",
            "Premium Warranty Package"
        ],
        "price": Decimal("299.99"),
        "compare_at_price": Decimal("349.99"),
        "cost_per_unit": Decimal("95.00"),
        "images": [
            {
                "url": "/images/products/pro-system-main.jpg",
                "alt_text": "NitePutter Pro LED System complete kit",
                "is_primary": True,
                "display_order": 0
            },
            {
                "url": "/images/products/pro-system-mounted.jpg",
                "alt_text": "NitePutter Pro mounted on putter",
                "is_primary": False,
                "display_order": 1
            },
            {
                "url": "/images/products/pro-system-app.jpg",
                "alt_text": "NitePutter Pro mobile app interface",
                "is_primary": False,
                "display_order": 2
            },
            {
                "url": "/images/products/pro-system-case.jpg",
                "alt_text": "NitePutter Pro with carrying case",
                "is_primary": False,
                "display_order": 3
            }
        ],
        "video_url": "https://youtube.com/watch?v=niteputter-pro-demo",
        "instruction_manual_url": "/manuals/niteputter-pro-manual.pdf",
        "specifications": {
            "battery_life": "12-15 hours continuous use",
            "charging_time": "3 hours full charge",
            "led_brightness": "100-1000 lumens adjustable",
            "weight": "62g",
            "material": "Carbon fiber & titanium alloy",
            "water_resistance": "IPX7 rated",
            "warranty": "3 year premium warranty"
        },
        "shipping": {
            "weight": 1.2,
            "length": 10,
            "width": 8,
            "height": 4,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 150,
            "reserved_quantity": 0,
            "low_stock_threshold": 15,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Pro LED System | Professional Golf Lighting",
            "meta_description": "Professional golf lighting with the NitePutter Pro LED System. Adjustable 100-1000 lumens, Bluetooth connectivity, 12-15 hour battery. Used by PGA pros.",
            "url_slug": "niteputter-pro-led-system",
            "keywords": ["professional golf light", "adjustable putting light", "bluetooth golf light", "PGA training aid", "premium golf accessories"]
        },
        "average_rating": 4.9,
        "review_count": 89
    },
    {
        "sku": "NPP-COMPLETE-001",
        "name": "NitePutter Complete Practice Kit",
        "slug": "niteputter-complete-practice-kit",
        "category": ProductCategory.COMPLETE,
        "status": ProductStatus.ACTIVE,
        "short_description": "Complete night golf practice solution with lights, targets, and training aids",
        "description": """
        <h3>Everything You Need for 24/7 Practice</h3>
        <p>The NitePutter Complete Practice Kit is the ultimate solution for golfers serious about improving 
        their putting game. This comprehensive package includes everything needed to create a professional 
        practice environment at home or on the course, day or night.</p>
        
        <h4>Complete Package Includes:</h4>
        <ul>
            <li>NitePutter Pro LED System with all accessories</li>
            <li>Set of 6 illuminated target cups with auto-return</li>
            <li>LED alignment sticks (set of 3)</li>
            <li>Glow-in-the-dark practice balls (dozen)</li>
            <li>Portable putting mat with built-in lighting</li>
            <li>Professional training guide and video series access</li>
        </ul>
        
        <h4>Transform Your Practice:</h4>
        <p>Whether you're practicing in your backyard, basement, or at the course after dark, this complete 
        kit provides everything needed for effective practice sessions. The illuminated targets and alignment 
        aids ensure you're building proper muscle memory and improving your accuracy.</p>
        """,
        "features": [
            "NitePutter Pro LED System included",
            "6 illuminated auto-return cups",
            "3 LED alignment sticks",
            "12 glow practice balls",
            "10ft x 3ft illuminated mat",
            "Mobile app with drills",
            "Video training library access",
            "Portable storage system",
            "Weather-resistant components"
        ],
        "whats_included": [
            "NitePutter Pro LED System",
            "6 Illuminated Target Cups",
            "3 LED Alignment Sticks",
            "12 Glow Practice Balls",
            "Portable Illuminated Putting Mat",
            "Deluxe Carrying Bag",
            "USB Charging Hub",
            "Professional Training Guide",
            "1-Year Video Library Access",
            "Complete Warranty Package"
        ],
        "price": Decimal("599.99"),
        "compare_at_price": Decimal("749.99"),
        "cost_per_unit": Decimal("210.00"),
        "images": [
            {
                "url": "/images/products/complete-kit-full.jpg",
                "alt_text": "NitePutter Complete Practice Kit full setup",
                "is_primary": True,
                "display_order": 0
            },
            {
                "url": "/images/products/complete-kit-components.jpg",
                "alt_text": "All components of the Complete Kit",
                "is_primary": False,
                "display_order": 1
            },
            {
                "url": "/images/products/complete-kit-night.jpg",
                "alt_text": "Complete Kit in use at night",
                "is_primary": False,
                "display_order": 2
            },
            {
                "url": "/images/products/complete-kit-bag.jpg",
                "alt_text": "Complete Kit storage bag",
                "is_primary": False,
                "display_order": 3
            }
        ],
        "video_url": "https://youtube.com/watch?v=niteputter-complete-demo",
        "instruction_manual_url": "/manuals/niteputter-complete-manual.pdf",
        "specifications": {
            "battery_life": "Varies by component (8-15 hours)",
            "charging_time": "3-4 hours full charge all components",
            "led_brightness": "100-1000 lumens (main light)",
            "weight": "8.5 lbs total kit",
            "material": "Mixed premium materials",
            "water_resistance": "IPX6-IPX7 rated components",
            "warranty": "3 year comprehensive warranty"
        },
        "shipping": {
            "weight": 12.0,
            "length": 36,
            "width": 12,
            "height": 8,
            "ships_separately": True
        },
        "inventory": {
            "quantity": 75,
            "reserved_quantity": 0,
            "low_stock_threshold": 10,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Complete Practice Kit | Full Night Golf Training System",
            "meta_description": "Complete night golf practice solution with NitePutter Pro LED, illuminated targets, alignment aids, and training materials. Everything for 24/7 practice.",
            "url_slug": "niteputter-complete-practice-kit",
            "keywords": ["complete golf kit", "night practice system", "golf training kit", "putting practice set", "illuminated golf aids"]
        },
        "average_rating": 4.8,
        "review_count": 56
    },
    {
        "sku": "NPP-ACC-BATTERY-001",
        "name": "NitePutter Extra Battery Pack",
        "slug": "niteputter-extra-battery-pack",
        "category": ProductCategory.ACCESSORIES,
        "status": ProductStatus.ACTIVE,
        "short_description": "High-capacity rechargeable battery pack for extended practice sessions",
        "description": """
        <h3>Never Stop Practicing</h3>
        <p>Keep your NitePutter running all night with our high-capacity extra battery pack. Engineered 
        specifically for NitePutter products, this premium lithium-ion battery delivers consistent power 
        and long life.</p>
        
        <h4>Features:</h4>
        <ul>
            <li>5000mAh high-capacity lithium-ion cells</li>
            <li>Compatible with all NitePutter LED products</li>
            <li>LED charge indicator (4 levels)</li>
            <li>Quick-swap magnetic connection</li>
            <li>Simultaneous charge while in use capability</li>
        </ul>
        """,
        "features": [
            "5000mAh capacity",
            "15+ hour runtime",
            "Quick-swap magnetic mount",
            "LED charge indicator",
            "Pass-through charging",
            "500+ charge cycles",
            "Overcharge protection",
            "1-year battery warranty"
        ],
        "whats_included": [
            "Extra Battery Pack",
            "USB-C Charging Cable",
            "Protective Case",
            "User Manual"
        ],
        "price": Decimal("49.99"),
        "compare_at_price": Decimal("59.99"),
        "cost_per_unit": Decimal("18.00"),
        "images": [
            {
                "url": "/images/products/battery-pack-main.jpg",
                "alt_text": "NitePutter Extra Battery Pack",
                "is_primary": True,
                "display_order": 0
            }
        ],
        "specifications": {
            "battery_life": "15+ hours",
            "charging_time": "3 hours",
            "led_brightness": "N/A",
            "weight": "120g",
            "material": "ABS plastic housing",
            "water_resistance": "IPX4 rated",
            "warranty": "1 year warranty"
        },
        "shipping": {
            "weight": 0.5,
            "length": 4,
            "width": 3,
            "height": 2,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 200,
            "reserved_quantity": 0,
            "low_stock_threshold": 25,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "NitePutter Extra Battery Pack | Extended Practice Power",
            "meta_description": "5000mAh extra battery pack for NitePutter LED lights. 15+ hour runtime, quick-swap design. Never stop practicing.",
            "url_slug": "niteputter-extra-battery-pack",
            "keywords": ["golf light battery", "niteputter battery", "rechargeable battery pack", "golf accessories"]
        },
        "average_rating": 4.6,
        "review_count": 78
    },
    {
        "sku": "NPP-ACC-MOUNT-001",
        "name": "Universal Magnetic Mount Kit",
        "slug": "universal-magnetic-mount-kit",
        "category": ProductCategory.ACCESSORIES,
        "status": ProductStatus.ACTIVE,
        "short_description": "Magnetic mounting system for any putter style with quick-release design",
        "description": """
        <h3>Mount to Any Putter in Seconds</h3>
        <p>Our Universal Magnetic Mount Kit ensures your NitePutter light fits perfectly on any putter, 
        from blade to mallet styles. The powerful neodymium magnets provide secure attachment while the 
        quick-release design lets you switch between clubs instantly.</p>
        
        <h4>Universal Compatibility:</h4>
        <ul>
            <li>Fits blade, mallet, and center-shaft putters</li>
            <li>Adjustable angle for optimal light positioning</li>
            <li>Non-marking protective padding</li>
            <li>Tool-free installation</li>
        </ul>
        """,
        "features": [
            "Universal putter fit",
            "Neodymium magnets",
            "Quick-release design",
            "360° adjustable angle",
            "Non-marking pads",
            "Aluminum construction",
            "Tool-free setup",
            "Lifetime warranty"
        ],
        "whats_included": [
            "Magnetic Mount Base",
            "3 Adapter Plates (different sizes)",
            "Protective Pads Set",
            "Installation Guide"
        ],
        "price": Decimal("29.99"),
        "compare_at_price": Decimal("39.99"),
        "cost_per_unit": Decimal("11.00"),
        "images": [
            {
                "url": "/images/products/mount-kit-main.jpg",
                "alt_text": "Universal Magnetic Mount Kit",
                "is_primary": True,
                "display_order": 0
            }
        ],
        "specifications": {
            "battery_life": "N/A",
            "charging_time": "N/A",
            "led_brightness": "N/A",
            "weight": "35g",
            "material": "Aluminum & neodymium",
            "water_resistance": "IPX6 rated",
            "warranty": "Lifetime warranty"
        },
        "shipping": {
            "weight": 0.3,
            "length": 5,
            "width": 4,
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
            "meta_title": "Universal Magnetic Mount Kit for NitePutter",
            "meta_description": "Quick-release magnetic mount for NitePutter lights. Fits all putter styles. Tool-free installation with lifetime warranty.",
            "url_slug": "universal-magnetic-mount-kit",
            "keywords": ["putter mount", "magnetic golf mount", "niteputter mount", "golf light mount"]
        },
        "average_rating": 4.7,
        "review_count": 124
    },
    {
        "sku": "NPP-ACC-TARGETS-001",
        "name": "LED Target Cup Set (6 Pack)",
        "slug": "led-target-cup-set",
        "category": ProductCategory.ACCESSORIES,
        "status": ProductStatus.ACTIVE,
        "short_description": "Illuminated practice cups with auto-return feature for night putting drills",
        "description": """
        <h3>Perfect Your Aim Day or Night</h3>
        <p>Transform any practice area into a professional training ground with our LED Target Cup Set. 
        Each cup features bright LED illumination and an auto-return mechanism that sends the ball back 
        to you after successful putts.</p>
        
        <h4>Smart Training Features:</h4>
        <ul>
            <li>6 different colored LEDs for varied drills</li>
            <li>Auto-return ball mechanism</li>
            <li>Adjustable LED brightness</li>
            <li>Regulation cup size (4.25 inches)</li>
            <li>Indoor/outdoor compatible</li>
        </ul>
        """,
        "features": [
            "6 illuminated cups",
            "Auto-return mechanism",
            "6 color options",
            "Adjustable brightness",
            "Regulation size",
            "Rechargeable batteries",
            "Weather resistant",
            "Storage case included"
        ],
        "whats_included": [
            "6 LED Target Cups",
            "USB Charging Hub",
            "Protective Storage Case",
            "Training Guide"
        ],
        "price": Decimal("149.99"),
        "compare_at_price": Decimal("179.99"),
        "cost_per_unit": Decimal("52.00"),
        "images": [
            {
                "url": "/images/products/target-cups-main.jpg",
                "alt_text": "LED Target Cup Set illuminated",
                "is_primary": True,
                "display_order": 0
            }
        ],
        "specifications": {
            "battery_life": "8-10 hours per charge",
            "charging_time": "2 hours",
            "led_brightness": "Adjustable",
            "weight": "2.4 lbs (set)",
            "material": "Impact-resistant polymer",
            "water_resistance": "IPX5 rated",
            "warranty": "2 year warranty"
        },
        "shipping": {
            "weight": 3.0,
            "length": 12,
            "width": 8,
            "height": 6,
            "ships_separately": False
        },
        "inventory": {
            "quantity": 100,
            "reserved_quantity": 0,
            "low_stock_threshold": 15,
            "track_inventory": True,
            "allow_backorder": True
        },
        "seo": {
            "meta_title": "LED Target Cup Set | Illuminated Putting Practice Cups",
            "meta_description": "6-pack LED target cups with auto-return for night putting practice. Adjustable brightness, multiple colors, regulation size.",
            "url_slug": "led-target-cup-set",
            "keywords": ["putting cups", "LED golf cups", "practice cups", "putting targets", "golf training aids"]
        },
        "average_rating": 4.8,
        "review_count": 92
    }
]

async def seed_products():
    """Seed the database with NitePutter products"""
    try:
        await connect_to_mongodb()
        db = await get_database()
        
        # Clear existing products (optional - comment out in production)
        await db.products.delete_many({})
        logger.info("Cleared existing products")
        
        # Insert products
        inserted_count = 0
        for product_data_orig in NITEPUTTER_PRODUCTS:
            # Create a copy to avoid modifying original data
            product_data = product_data_orig.copy()
            
            # Convert dictionaries to proper model instances
            product_data["images"] = [ProductImage(**img) for img in product_data_orig["images"]]
            product_data["specifications"] = ProductSpecification(**product_data_orig["specifications"])
            product_data["shipping"] = ShippingInfo(**product_data_orig["shipping"])
            product_data["inventory"] = InventoryInfo(**product_data_orig["inventory"])
            product_data["seo"] = SEOInfo(**product_data_orig["seo"])
            
            # Create product instance
            product = Product(**product_data)
            
            # Convert to dict and handle Decimal conversion
            product_dict = product.model_dump(by_alias=True)
            
            # Convert all Decimal values to float for MongoDB
            def convert_decimals(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_decimals(item) for item in obj]
                return obj
            
            product_dict = convert_decimals(product_dict)
            
            # Insert into database
            result = await db.products.insert_one(product_dict)
            
            if result.inserted_id:
                inserted_count += 1
                logger.info(f"Inserted product: {product.name} (SKU: {product.sku})")
        
        logger.info(f"Successfully seeded {inserted_count} products")
        
        # Create some sample inventory records
        for product_data_raw in NITEPUTTER_PRODUCTS:
            inventory_record = {
                "product_id": product_data_raw["sku"],
                "quantity": product_data_raw["inventory"]["quantity"],
                "reserved_quantity": 0,
                "low_stock_threshold": product_data_raw["inventory"]["low_stock_threshold"],
                "last_restocked": datetime.utcnow(),
                "restock_quantity": 100,
                "supplier": "NitePutter Manufacturing",
                "location": "Warehouse A",
                "notes": "Initial stock"
            }
            await db.inventory.insert_one(inventory_record)
            
        logger.info("Created inventory records")
        
        # Verify the seeding
        count = await db.products.count_documents({})
        logger.info(f"Total products in database: {count}")
        
        # Display summary
        for category in ProductCategory:
            count = await db.products.count_documents({"category": category.value})
            logger.info(f"  {category.value}: {count} products")
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding products: {e}")
        raise

async def main():
    """Run the seeder"""
    success = await seed_products()
    if success:
        logger.info("Product seeding completed successfully!")
    else:
        logger.error("Product seeding failed")

if __name__ == "__main__":
    asyncio.run(main())