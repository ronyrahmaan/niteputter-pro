"""
Script to setup initial content data including blog categories, posts, documentation sections, and SEO pages
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to the Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from models.content import (
    BlogCategory, BlogPost, BlogStatus, DocumentationSection, DocumentationType,
    DocumentationPage, SEOPage, MediaFile, MediaType
)
from database.content_repository import ContentRepository

load_dotenv(ROOT_DIR / '.env')

# Sample blog categories
BLOG_CATEGORIES = [
    {
        "name": "Golf Tips & Techniques",
        "slug": "golf-tips",
        "description": "Expert advice and techniques to improve your golf game",
        "color": "#28a745",
        "sort_order": 1
    },
    {
        "name": "Product Updates",
        "slug": "product-updates", 
        "description": "Latest news and updates about our Nite Putter Pro products",
        "color": "#007bff",
        "sort_order": 2
    },
    {
        "name": "Installation Guides",
        "slug": "installation-guides",
        "description": "Step-by-step guides for installing your lighting system",
        "color": "#fd7e14",
        "sort_order": 3
    },
    {
        "name": "Success Stories",
        "slug": "success-stories",
        "description": "Customer testimonials and success stories",
        "color": "#6f42c1",
        "sort_order": 4
    }
]

# Sample blog posts
BLOG_POSTS = [
    {
        "title": "5 Essential Night Putting Tips for Better Scores",
        "slug": "5-essential-night-putting-tips",
        "excerpt": "Master the art of nighttime putting with these proven techniques that will lower your scores and boost your confidence on the green.",
        "content": """
# 5 Essential Night Putting Tips for Better Scores

Playing golf at night presents unique challenges, but with the right techniques and equipment, you can maintain your putting accuracy even in low-light conditions. Here are five essential tips to help you excel at night putting.

## 1. Focus on Feel Over Sight

When visibility is limited, your sense of touch becomes your greatest asset. Practice putting with your eyes closed during the day to develop a better feel for distance and speed control.

**Pro Tip:** Use consistent pre-shot routines to build muscle memory that doesn't rely on visual cues.

## 2. Invest in Quality Lighting

Proper illumination is crucial for night putting success. The Nite Putter Pro Complete System provides even, glare-free lighting that enhances visibility without creating shadows or hot spots.

**Key Features:**
- Patented POLY LIGHT CASING technology
- Multi-level drainage system
- Hardwired 12v system for reliability

## 3. Read Greens During Daylight

Study the greens during daylight hours to understand slopes, breaks, and grain direction. This knowledge becomes invaluable when playing at night.

## 4. Use Alignment Aids

In low-light conditions, alignment becomes more challenging. Use putting alignment sticks or laser guides to ensure proper setup and ball position.

## 5. Practice Tempo and Rhythm

Consistent tempo is even more important at night when visual feedback is limited. Practice with a metronome to develop a steady putting rhythm.

## Conclusion

Night putting doesn't have to hurt your game. With proper preparation, quality lighting, and focused practice, you can maintain your putting excellence regardless of the time of day.

Ready to take your night game to the next level? Explore our complete lighting solutions at [Nite Putter Pro](/shop).
        """,
        "category_slug": "golf-tips",
        "tags": ["putting", "night-golf", "tips", "technique"],
        "is_featured": True,
        "meta_title": "5 Essential Night Putting Tips | Nite Putter Pro",
        "meta_description": "Master nighttime putting with these 5 proven techniques. Improve your scores with expert tips for night golf putting success."
    },
    {
        "title": "Introducing Smart Life Bulb System 2.0",
        "slug": "smart-life-bulb-system-2-0",
        "excerpt": "Our latest Smart Life Bulb System features enhanced Bluetooth connectivity, expanded color options, and improved app integration for the ultimate putting experience.",
        "content": """
# Introducing Smart Life Bulb System 2.0

We're excited to announce the launch of our revolutionary Smart Life Bulb System 2.0, bringing cutting-edge technology to your putting green lighting experience.

## What's New in Version 2.0?

### Enhanced Bluetooth Connectivity
- **Extended Range:** Up to 100 feet connection distance
- **Faster Pairing:** Connect in under 3 seconds
- **Multiple Device Support:** Control from up to 4 devices simultaneously

### Expanded Color Palette
- **16 Million Colors:** Choose from virtually unlimited color combinations
- **Preset Themes:** 20+ professionally designed lighting themes
- **Dynamic Effects:** Moving patterns and color transitions

### Improved Smart Life App
- **Intuitive Interface:** Redesigned for easier navigation
- **Voice Control:** Compatible with Alexa and Google Assistant
- **Scheduling:** Set automated lighting schedules
- **Energy Monitoring:** Track power consumption and optimize usage

## Installation Made Simple

The Smart Life Bulb System 2.0 maintains our commitment to easy installation:

1. **Replace existing MR16 bulbs** with Smart Life bulbs
2. **Download the app** from App Store or Google Play
3. **Pair your bulbs** using Bluetooth
4. **Start customizing** your lighting experience

## Perfect for Every Occasion

Whether you're practicing your putting, hosting a golf party, or simply enjoying your outdoor space, the Smart Life Bulb System 2.0 adapts to every situation.

### Practice Mode
- Bright, focused lighting for serious practice sessions
- Adjustable intensity based on skill level
- Timer functionality for structured practice

### Entertainment Mode
- Festive colors for parties and gatherings
- Music sync capabilities (coming in Q2 2024)
- Guest control features

### Relaxation Mode
- Warm, ambient lighting for peaceful evenings
- Gradual dimming and sunrise/sunset simulation
- Sleep timer functionality

## Availability and Pricing

The Smart Life Bulb System 2.0 is available now for $129 (upgrade from $89 for the original system). Existing customers can upgrade with a 20% discount using code SMART20.

[Order your Smart Life Bulb System 2.0 today](/shop) and transform your putting green into a smart, connected experience.
        """,
        "category_slug": "product-updates",
        "tags": ["smart-life", "bluetooth", "app", "upgrade"],
        "is_featured": True,
        "meta_title": "Smart Life Bulb System 2.0 Launch | Nite Putter Pro",
        "meta_description": "Discover the new Smart Life Bulb System 2.0 with enhanced Bluetooth, 16M colors, and improved app integration for your putting green."
    },
    {
        "title": "Complete Installation Guide: Professional Setup in 6 Steps",
        "slug": "complete-installation-guide-professional-setup",
        "excerpt": "Follow our comprehensive installation guide to properly set up your Nite Putter Pro Complete System for optimal performance and longevity.",
        "content": """
# Complete Installation Guide: Professional Setup in 6 Steps

Installing your Nite Putter Pro Complete System correctly ensures optimal performance, safety, and longevity. This comprehensive guide walks you through each step of the professional installation process.

## Before You Begin

### Required Tools
- Shovel or trenching tool
- Wire strippers
- Voltage tester
- Waterproof wire nuts
- Electrical tape
- Level

### Safety First
- Turn off power at the circuit breaker
- Check local electrical codes
- Consider hiring a licensed electrician for complex installations

## Step 1: Planning Your Layout

### Assess Your Putting Green
- Measure the area to be lit
- Identify optimal light placement points
- Plan cable routing to avoid obstacles
- Mark utility lines (call 811 before digging)

### Calculate Power Requirements
- Each Nite Putter Pro unit requires 12V, 3W
- Plan transformer placement within 100 feet of lights
- Ensure adequate power supply for all units

## Step 2: Installing the Transformer

### Location Selection
- Choose a dry, ventilated area
- Mount at least 12 inches above ground
- Ensure easy access for maintenance
- Protect from direct weather exposure

### Electrical Connection
- Connect to GFCI-protected circuit
- Use weatherproof electrical box
- Follow local electrical codes
- Test connection before proceeding

## Step 3: Trenching and Cable Installation

### Digging Guidelines
- Trench depth: 6-8 inches minimum
- Width: 4-6 inches
- Slope trenches away from lights for drainage
- Use sand bedding for cable protection

### Cable Routing
- Use only low-voltage landscape cable
- Install warning tape 4 inches above cable
- Maintain 6-inch separation from other utilities
- Plan service loops at each light location

## Step 4: Installing the POLY LIGHT CASING

### Preparation
- Ensure level installation surface
- Check drainage around installation area
- Have all components ready before starting

### Installation Process
1. **Position the casing** in the desired location
2. **Level the unit** using the built-in adjustment system
3. **Connect drainage pipes** following the multi-level design
4. **Secure mounting hardware** according to specifications
5. **Test fit all components** before final installation

### Key Features to Verify
- ✅ Proper drainage flow
- ✅ Level installation
- ✅ Secure mounting
- ✅ Access for maintenance

## Step 5: Electrical Connections

### Safety Procedures
- Verify power is off at the transformer
- Use only approved waterproof connectors
- Apply dielectric grease to all connections
- Follow color-coded wiring diagrams

### Connection Process
1. **Strip cable ends** to manufacturer specifications
2. **Connect positive and negative leads** using wire nuts
3. **Apply weatherproof sealing** to all connections
4. **Test continuity** before burying connections
5. **Document wire routing** for future reference

## Step 6: Testing and Final Setup

### Initial Power-Up
- Turn on power at the transformer
- Check all lights for proper operation
- Verify even light distribution
- Test any smart controls or apps

### Performance Verification
- **Brightness Test:** Ensure adequate illumination
- **Drainage Test:** Pour water to verify proper drainage
- **Control Test:** Verify all switching and dimming functions
- **Safety Test:** Check all electrical connections

### Documentation
- Record transformer location and specifications
- Map cable routing and connection points
- Create maintenance schedule
- Provide user manual and warranty information

## Maintenance Tips

### Regular Inspections
- Check lights monthly for damage or dimming
- Inspect connections annually
- Clean lenses as needed for optimal light output
- Test GFCI protection quarterly

### Seasonal Care
- **Spring:** Check for winter damage, test full system
- **Summer:** Monitor for overheating, ensure proper ventilation
- **Fall:** Clear debris from lights and drainage areas
- **Winter:** Protect exposed components from freezing

## Troubleshooting Common Issues

### Lights Not Working
1. Check transformer power and fuses
2. Verify GFCI hasn't tripped
3. Test voltage at light connections
4. Inspect for damaged cables

### Uneven Lighting
1. Clean dirty lenses
2. Check for loose connections
3. Verify proper bulb installation
4. Adjust light positioning if needed

### Drainage Problems
1. Clear debris from drainage ports
2. Check slope and grading
3. Verify drainage pipe connections
4. Consider additional drainage if needed

## Professional Installation Services

While this guide enables DIY installation, our professional installation service ensures:
- **Expert setup** by certified technicians
- **Warranty protection** for installation
- **System optimization** for your specific green
- **Ongoing support** and maintenance

[Schedule professional installation](/contact) or [order your system](/shop) today.

## Conclusion

Proper installation is crucial for optimal performance and longevity of your Nite Putter Pro system. Take your time, follow safety procedures, and don't hesitate to consult with professionals when needed.

For technical support or installation questions, contact our expert team at (469) 642-7171 or [support@niteputterpro.com](mailto:support@niteputterpro.com).
        """,
        "category_slug": "installation-guides",
        "tags": ["installation", "guide", "diy", "professional", "setup"],
        "is_featured": False,
        "meta_title": "Installation Guide | Nite Putter Pro Setup",
        "meta_description": "Step-by-step installation guide for Nite Putter Pro Complete System. Professional setup tips, safety guidelines, and troubleshooting."
    }
]

# Documentation sections
DOCUMENTATION_SECTIONS = [
    {
        "name": "Getting Started",
        "slug": "getting-started",
        "description": "Everything you need to know to get started with Nite Putter Pro",
        "doc_type": DocumentationType.USER_GUIDE,
        "sort_order": 1
    },
    {
        "name": "Product Specifications",
        "slug": "product-specifications", 
        "description": "Detailed technical specifications for all products",
        "doc_type": DocumentationType.TECHNICAL,
        "sort_order": 2
    },
    {
        "name": "Troubleshooting",
        "slug": "troubleshooting",
        "description": "Common issues and solutions",
        "doc_type": DocumentationType.FAQ,
        "sort_order": 3
    }
]

# SEO pages
SEO_PAGES = [
    {
        "url_path": "/",
        "page_title": "Nite Putter Pro - Professional Golf Lighting Systems",
        "meta_description": "Transform your putting green with Nite Putter Pro's professional lighting systems. Patented technology, smart controls, and expert installation.",
        "meta_keywords": "golf lighting, putting green lights, night golf, professional installation",
        "og_title": "Nite Putter Pro - Turn Nite Time Into Tee Time",
        "og_description": "Professional golf lighting systems with patented POLY LIGHT CASING technology and smart controls.",
        "sitemap_priority": 1.0,
        "sitemap_changefreq": "weekly"
    },
    {
        "url_path": "/shop",
        "page_title": "Shop Golf Lighting Systems | Nite Putter Pro",
        "meta_description": "Browse our complete selection of golf lighting systems, smart bulbs, and professional installation services. Free shipping on orders over $200.",
        "meta_keywords": "buy golf lights, shop putting green lighting, smart bulbs, installation service",
        "og_title": "Shop Professional Golf Lighting | Nite Putter Pro",
        "og_description": "Complete selection of golf lighting systems with smart controls and professional installation.",
        "sitemap_priority": 0.9,
        "sitemap_changefreq": "daily"
    },
    {
        "url_path": "/blog",
        "page_title": "Golf Tips & Product News | Nite Putter Pro Blog",
        "meta_description": "Expert golf tips, product updates, and installation guides. Stay informed with the latest from Nite Putter Pro.",
        "meta_keywords": "golf blog, putting tips, product news, installation guides",
        "og_title": "Golf Tips & News | Nite Putter Pro Blog",
        "og_description": "Expert advice, product updates, and installation guides for golf lighting enthusiasts.",
        "sitemap_priority": 0.8,
        "sitemap_changefreq": "daily"
    }
]

async def setup_content_data():
    """Setup initial content data"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Initialize content repository
        content_repo = ContentRepository(db)
        
        # Create indexes
        await content_repo.create_indexes()
        print("✅ Content indexes created")
        
        # Create blog categories
        print("\n📝 Setting up Blog Categories...")
        category_map = {}
        
        for cat_data in BLOG_CATEGORIES:
            category = BlogCategory(**cat_data)
            created_category = await content_repo.create_blog_category(category)
            
            if created_category:
                category_map[cat_data["slug"]] = created_category.id
                print(f"✅ Created blog category: {cat_data['name']}")
            else:
                print(f"❌ Failed to create category: {cat_data['name']}")
        
        # Create blog posts
        print("\n📰 Setting up Blog Posts...")
        post_count = 0
        
        for post_data in BLOG_POSTS:
            # Map category slug to ID
            category_slug = post_data.pop("category_slug")
            category_id = category_map.get(category_slug)
            
            if category_id:
                post_data["category_id"] = category_id
            
            # Create blog post
            from models.content import BlogPostCreate
            post_create = BlogPostCreate(**post_data)
            
            created_post = await content_repo.create_blog_post(
                post_create, 
                author_id="system", 
                author_name="Nite Putter Pro Team"
            )
            
            if created_post:
                print(f"✅ Created blog post: {post_data['title']}")
                post_count += 1
            else:
                print(f"❌ Failed to create post: {post_data['title']}")
        
        # Create documentation sections
        print("\n📚 Setting up Documentation Sections...")
        section_count = 0
        
        for section_data in DOCUMENTATION_SECTIONS:
            section = DocumentationSection(**section_data)
            created_section = await content_repo.create_documentation_section(section)
            
            if created_section:
                print(f"✅ Created documentation section: {section_data['name']}")
                section_count += 1
            else:
                print(f"❌ Failed to create section: {section_data['name']}")
        
        # Create SEO pages
        print("\n🔍 Setting up SEO Pages...")
        seo_count = 0
        
        for seo_data in SEO_PAGES:
            seo_page = SEOPage(**seo_data)
            created_seo = await content_repo.create_seo_page(seo_page)
            
            if created_seo:
                print(f"✅ Created SEO page: {seo_data['url_path']}")
                seo_count += 1
            else:
                print(f"❌ Failed to create SEO page: {seo_data['url_path']}")
        
        # Display summary
        print(f"\n🎉 Content setup completed!")
        print(f"📝 Blog categories: {len(category_map)}")
        print(f"📰 Blog posts: {post_count}")
        print(f"📚 Documentation sections: {section_count}")
        print(f"🔍 SEO pages: {seo_count}")
        
        # Get content analytics
        analytics = await content_repo.get_content_analytics(days=30)
        print(f"\n📊 Content System Stats:")
        print(f"  - Blog posts: {analytics.get('blog', {}).get('total_posts', 0)}")
        print(f"  - Documentation pages: {analytics.get('documentation', {}).get('total_pages', 0)}")
        print(f"  - Media files: {analytics.get('media', {}).get('total_files', 0)}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Content setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Setting up Content Management Data...")
    asyncio.run(setup_content_data())