"""
Migration script to move hardcoded products to database
Run this script to populate the products database with initial data
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
from models.product import ProductCreate, ProductCategory, ProductStatus, ProductImage
from database.product_repository import ProductRepository

load_dotenv(ROOT_DIR / '.env')

# Hardcoded products to migrate
LEGACY_PRODUCTS = {
    "nite_putter_complete": {
        "name": "Nite Putter Pro Complete System",
        "price": 299.00,
        "description": "Complete illuminated golf cup system with patented POLY LIGHT CASING technology. This comprehensive system includes everything needed for a professional nighttime putting experience with advanced drainage and lighting technology.",
        "features": ["Patented POLY LIGHT CASING", "Multi-level drainage", "Hardwired 12v system", "Professional installation"]
    },
    "smart_bulb_system": {
        "name": "Smart Life Bulb System", 
        "price": 89.00,
        "description": "Bluetooth-enabled MR16 bulb with color customization capabilities. Control your putting green lighting with smartphone app integration and create the perfect ambiance for your game.",
        "features": ["Bluetooth connectivity", "Color customization", "Smart Life app control", "Easy installation"]
    },
    "installation_service": {
        "name": "Professional Installation Service",
        "price": 150.00,
        "description": "Expert installation by our veteran-owned team with ongoing support. Our certified technicians ensure proper setup, testing, and provide comprehensive training on system operation.",
        "features": ["Professional setup", "System testing", "Training included", "Ongoing support"]
    },
    "custom_course": {
        "name": "Custom Course Integration",
        "price": 500.00,
        "description": "Complete golf course lighting solutions for professional installations. Designed for commercial golf facilities requiring multi-hole illumination with centralized control systems.",
        "features": ["Multi-hole systems", "Landscape integration", "Control systems", "Maintenance plans"]
    }
}

async def migrate_products():
    """Migrate hardcoded products to database"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Initialize product repository
        product_repo = ProductRepository(db)
        
        # Create indexes
        await product_repo.create_indexes()
        print("✅ Product indexes created")
        
        # Check if products already exist
        existing_products = await product_repo.get_products()
        if existing_products[1] > 0:  # Check total count
            print(f"⚠️  {existing_products[1]} products already exist in database")
            response = input("Do you want to continue and add these products anyway? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                return
        
        # Migrate each product
        migrated_count = 0
        for product_id, product_data in LEGACY_PRODUCTS.items():
            try:
                # Determine category based on product type
                if "complete" in product_id.lower() or "system" in product_data["name"].lower():
                    category = ProductCategory.COMPLETE_SYSTEMS
                elif "service" in product_id.lower() or "installation" in product_data["name"].lower():
                    category = ProductCategory.SERVICES
                elif "bulb" in product_id.lower() or "smart" in product_data["name"].lower():
                    category = ProductCategory.COMPONENTS
                else:
                    category = ProductCategory.ACCESSORIES
                
                # Create product images (using placeholder URLs for now)
                images = [
                    ProductImage(
                        url=f"https://niteputterpro.com/images/{product_id}-1.jpg",
                        alt_text=f"{product_data['name']} - Main Image",
                        is_primary=True,
                        sort_order=0
                    ),
                    ProductImage(
                        url=f"https://niteputterpro.com/images/{product_id}-2.jpg", 
                        alt_text=f"{product_data['name']} - Detail View",
                        is_primary=False,
                        sort_order=1
                    )
                ]
                
                # Create product
                product_create = ProductCreate(
                    name=product_data["name"],
                    description=product_data["description"],
                    short_description=f"{product_data['name']} - {product_data['description'][:100]}...",
                    category=category,
                    status=ProductStatus.ACTIVE,
                    base_price=product_data["price"],
                    sku=product_id.upper().replace("_", "-"),
                    inventory_count=100,  # Initial stock
                    low_stock_threshold=10,
                    features=product_data["features"],
                    tags=["nite-putter", "golf", "lighting", category.value],
                    is_featured=(product_id == "nite_putter_complete"),  # Make the main product featured
                    images=images,
                    meta_title=f"{product_data['name']} | Nite Putter Pro",
                    meta_description=product_data["description"][:160]
                )
                
                # Check if product with this SKU already exists
                existing = await product_repo.get_product_by_sku(product_create.sku)
                if existing:
                    print(f"⚠️  Product with SKU {product_create.sku} already exists, skipping...")
                    continue
                
                # Create the product
                created_product = await product_repo.create_product(product_create, created_by="migration_script")
                
                if created_product:
                    print(f"✅ Migrated: {product_data['name']} (SKU: {product_create.sku})")
                    migrated_count += 1
                else:
                    print(f"❌ Failed to migrate: {product_data['name']}")
                    
            except Exception as e:
                print(f"❌ Error migrating {product_id}: {e}")
        
        print(f"\n🎉 Migration completed! {migrated_count} products migrated successfully.")
        
        # Display summary
        all_products, total_count = await product_repo.get_products()
        print(f"📊 Total products in database: {total_count}")
        
        categories = await product_repo.get_categories_with_counts()
        print("\n📋 Products by category:")
        for category, count in categories.items():
            print(f"  - {category}: {count} products")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting product migration...")
    asyncio.run(migrate_products())