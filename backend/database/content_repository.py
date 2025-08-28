from motor.motor_asyncio import AsyncIOMotorDatabase
from models.content import (
    BlogCategory, BlogPost, BlogPostCreate, BlogPostUpdate, BlogStatus, BlogComment,
    DocumentationSection, DocumentationPage, DocumentationType,
    SEOPage, SEOAnalytics, MediaFile, MediaType,
    LandingPage, LandingPageComponent, LandingPageSection,
    EmailCampaign
)
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

class ContentRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        
        # Collections
        self.blog_categories_collection = database.blog_categories
        self.blog_posts_collection = database.blog_posts
        self.blog_comments_collection = database.blog_comments
        self.documentation_sections_collection = database.documentation_sections
        self.documentation_pages_collection = database.documentation_pages
        self.seo_pages_collection = database.seo_pages
        self.seo_analytics_collection = database.seo_analytics
        self.media_files_collection = database.media_files
        self.landing_pages_collection = database.landing_pages
        self.landing_components_collection = database.landing_components
        self.email_campaigns_collection = database.email_campaigns
        
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Blog indexes
            await self.blog_categories_collection.create_index("slug", unique=True)
            await self.blog_categories_collection.create_index("is_active")
            
            await self.blog_posts_collection.create_index("slug", unique=True)
            await self.blog_posts_collection.create_index("status")
            await self.blog_posts_collection.create_index("published_at")
            await self.blog_posts_collection.create_index("category_id")
            await self.blog_posts_collection.create_index("tags")
            await self.blog_posts_collection.create_index("is_featured")
            await self.blog_posts_collection.create_index([("title", "text"), ("content", "text")])
            
            await self.blog_comments_collection.create_index("post_id")
            await self.blog_comments_collection.create_index("is_approved")
            await self.blog_comments_collection.create_index("created_at")
            
            # Documentation indexes
            await self.documentation_sections_collection.create_index("slug", unique=True)
            await self.documentation_sections_collection.create_index("doc_type")
            await self.documentation_sections_collection.create_index("parent_id")
            
            await self.documentation_pages_collection.create_index("slug", unique=True)
            await self.documentation_pages_collection.create_index("section_id")
            await self.documentation_pages_collection.create_index("is_published")
            await self.documentation_pages_collection.create_index([("title", "text"), ("content", "text")])
            
            # SEO indexes
            await self.seo_pages_collection.create_index("url_path", unique=True)
            await self.seo_pages_collection.create_index("last_crawled")
            
            await self.seo_analytics_collection.create_index([("url_path", 1), ("date", 1)], unique=True)
            await self.seo_analytics_collection.create_index("date")
            
            # Media indexes
            await self.media_files_collection.create_index("filename")
            await self.media_files_collection.create_index("media_type")
            await self.media_files_collection.create_index("uploaded_by")
            await self.media_files_collection.create_index("created_at")
            await self.media_files_collection.create_index("tags")
            
            # Landing pages indexes
            await self.landing_pages_collection.create_index("slug", unique=True)
            await self.landing_pages_collection.create_index("is_published")
            
            await self.landing_components_collection.create_index("section_type")
            await self.landing_components_collection.create_index("is_active")
            
            # Email campaigns indexes
            await self.email_campaigns_collection.create_index("status")
            await self.email_campaigns_collection.create_index("send_at")
            await self.email_campaigns_collection.create_index("created_by")
            
            logger.info("Content management collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create content indexes: {e}")
    
    # Blog Management
    async def create_blog_category(self, category: BlogCategory) -> Optional[BlogCategory]:
        """Create blog category"""
        try:
            await self.blog_categories_collection.insert_one(category.dict())
            return category
        except Exception as e:
            logger.error(f"Failed to create blog category: {e}")
            return None
    
    async def get_blog_categories(self, active_only: bool = True) -> List[BlogCategory]:
        """Get blog categories"""
        try:
            query = {}
            if active_only:
                query["is_active"] = True
            
            cursor = self.blog_categories_collection.find(query).sort("sort_order", 1)
            category_docs = await cursor.to_list(length=None)
            
            return [BlogCategory(**doc) for doc in category_docs]
        except Exception as e:
            logger.error(f"Failed to get blog categories: {e}")
            return []
    
    async def create_blog_post(self, post: BlogPostCreate, author_id: Optional[str] = None, author_name: Optional[str] = None) -> Optional[BlogPost]:
        """Create blog post"""
        try:
            post_dict = post.dict()
            post_dict['author_id'] = author_id
            post_dict['author_name'] = author_name
            
            # Set published_at if status is published
            if post.status == BlogStatus.PUBLISHED:
                post_dict['published_at'] = datetime.utcnow()
            
            blog_post = BlogPost(**post_dict)
            
            await self.blog_posts_collection.insert_one(blog_post.dict())
            return blog_post
        except Exception as e:
            logger.error(f"Failed to create blog post: {e}")
            return None
    
    async def get_blog_posts(
        self,
        status: Optional[BlogStatus] = None,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        featured_only: bool = False,
        published_only: bool = True,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[BlogPost], int]:
        """Get blog posts with filtering and pagination"""
        try:
            query = {}
            
            if status:
                query["status"] = status
            elif published_only:
                query["status"] = BlogStatus.PUBLISHED
                query["published_at"] = {"$lte": datetime.utcnow()}
            
            if category_id:
                query["category_id"] = category_id
            
            if tags:
                query["tags"] = {"$in": tags}
            
            if featured_only:
                query["is_featured"] = True
            
            # Get total count
            total_count = await self.blog_posts_collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Execute query
            cursor = self.blog_posts_collection.find(query).sort("published_at", -1).skip(skip).limit(page_size)
            post_docs = await cursor.to_list(length=page_size)
            
            posts = [BlogPost(**doc) for doc in post_docs]
            
            return posts, total_count
            
        except Exception as e:
            logger.error(f"Failed to get blog posts: {e}")
            return [], 0
    
    async def get_blog_post(self, post_id: str = None, slug: str = None) -> Optional[BlogPost]:
        """Get blog post by ID or slug"""
        try:
            query = {}
            if post_id:
                query["id"] = post_id
            elif slug:
                query["slug"] = slug
            else:
                return None
            
            post_doc = await self.blog_posts_collection.find_one(query)
            if post_doc:
                return BlogPost(**post_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get blog post: {e}")
            return None
    
    async def update_blog_post(self, post_id: str, post_update: BlogPostUpdate) -> Optional[BlogPost]:
        """Update blog post"""
        try:
            update_dict = post_update.dict(exclude_unset=True)
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                # Set published_at if status changed to published
                if update_dict.get("status") == BlogStatus.PUBLISHED:
                    existing_post = await self.get_blog_post(post_id)
                    if existing_post and existing_post.published_at is None:
                        update_dict["published_at"] = datetime.utcnow()
                
                result = await self.blog_posts_collection.update_one(
                    {"id": post_id},
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    return await self.get_blog_post(post_id)
            
            return None
        except Exception as e:
            logger.error(f"Failed to update blog post: {e}")
            return None
    
    async def increment_blog_post_view(self, post_id: str) -> bool:
        """Increment blog post view count"""
        try:
            result = await self.blog_posts_collection.update_one(
                {"id": post_id},
                {"$inc": {"view_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment blog post view: {e}")
            return False
    
    async def search_blog_posts(self, query: str, limit: int = 10) -> List[BlogPost]:
        """Search blog posts"""
        try:
            search_results = await self.blog_posts_collection.find(
                {
                    "$text": {"$search": query},
                    "status": BlogStatus.PUBLISHED,
                    "published_at": {"$lte": datetime.utcnow()}
                },
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit).to_list(length=limit)
            
            return [BlogPost(**doc) for doc in search_results]
        except Exception as e:
            logger.error(f"Failed to search blog posts: {e}")
            return []
    
    # Blog Comments
    async def create_blog_comment(self, comment: BlogComment) -> Optional[BlogComment]:
        """Create blog comment"""
        try:
            await self.blog_comments_collection.insert_one(comment.dict())
            
            # Increment comment count on post
            await self.blog_posts_collection.update_one(
                {"id": comment.post_id},
                {"$inc": {"comment_count": 1}}
            )
            
            return comment
        except Exception as e:
            logger.error(f"Failed to create blog comment: {e}")
            return None
    
    async def get_blog_comments(self, post_id: str, approved_only: bool = True) -> List[BlogComment]:
        """Get blog comments for a post"""
        try:
            query = {"post_id": post_id}
            if approved_only:
                query["is_approved"] = True
            
            cursor = self.blog_comments_collection.find(query).sort("created_at", 1)
            comment_docs = await cursor.to_list(length=None)
            
            return [BlogComment(**doc) for doc in comment_docs]
        except Exception as e:
            logger.error(f"Failed to get blog comments: {e}")
            return []
    
    # Documentation Management
    async def create_documentation_section(self, section: DocumentationSection) -> Optional[DocumentationSection]:
        """Create documentation section"""
        try:
            await self.documentation_sections_collection.insert_one(section.dict())
            return section
        except Exception as e:
            logger.error(f"Failed to create documentation section: {e}")
            return None
    
    async def get_documentation_sections(self, doc_type: Optional[DocumentationType] = None, active_only: bool = True) -> List[DocumentationSection]:
        """Get documentation sections"""
        try:
            query = {}
            if doc_type:
                query["doc_type"] = doc_type
            if active_only:
                query["is_active"] = True
            
            cursor = self.documentation_sections_collection.find(query).sort("sort_order", 1)
            section_docs = await cursor.to_list(length=None)
            
            return [DocumentationSection(**doc) for doc in section_docs]
        except Exception as e:
            logger.error(f"Failed to get documentation sections: {e}")
            return []
    
    async def create_documentation_page(self, page: DocumentationPage, author_id: Optional[str] = None) -> Optional[DocumentationPage]:
        """Create documentation page"""
        try:
            page_dict = page.dict()
            page_dict['author_id'] = author_id
            
            doc_page = DocumentationPage(**page_dict)
            
            await self.documentation_pages_collection.insert_one(doc_page.dict())
            return doc_page
        except Exception as e:
            logger.error(f"Failed to create documentation page: {e}")
            return None
    
    async def get_documentation_pages(self, section_id: Optional[str] = None, published_only: bool = True) -> List[DocumentationPage]:
        """Get documentation pages"""
        try:
            query = {}
            if section_id:
                query["section_id"] = section_id
            if published_only:
                query["is_published"] = True
            
            cursor = self.documentation_pages_collection.find(query).sort("sort_order", 1)
            page_docs = await cursor.to_list(length=None)
            
            return [DocumentationPage(**doc) for doc in page_docs]
        except Exception as e:
            logger.error(f"Failed to get documentation pages: {e}")
            return []
    
    # SEO Management
    async def create_seo_page(self, seo_page: SEOPage) -> Optional[SEOPage]:
        """Create SEO page configuration"""
        try:
            await self.seo_pages_collection.insert_one(seo_page.dict())
            return seo_page
        except Exception as e:
            logger.error(f"Failed to create SEO page: {e}")
            return None
    
    async def get_seo_page(self, url_path: str) -> Optional[SEOPage]:
        """Get SEO configuration for URL path"""
        try:
            seo_doc = await self.seo_pages_collection.find_one({"url_path": url_path})
            if seo_doc:
                return SEOPage(**seo_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get SEO page: {e}")
            return None
    
    async def update_seo_page(self, url_path: str, seo_data: Dict[str, Any]) -> bool:
        """Update SEO page configuration"""
        try:
            seo_data["updated_at"] = datetime.utcnow()
            
            result = await self.seo_pages_collection.update_one(
                {"url_path": url_path},
                {"$set": seo_data},
                upsert=True
            )
            
            return result.upserted_id is not None or result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update SEO page: {e}")
            return False
    
    # Media Management
    async def create_media_file(self, media_file: MediaFile, uploaded_by: Optional[str] = None) -> Optional[MediaFile]:
        """Create media file record"""
        try:
            media_dict = media_file.dict()
            media_dict['uploaded_by'] = uploaded_by
            
            media_obj = MediaFile(**media_dict)
            
            await self.media_files_collection.insert_one(media_obj.dict())
            return media_obj
        except Exception as e:
            logger.error(f"Failed to create media file: {e}")
            return None
    
    async def get_media_files(
        self,
        media_type: Optional[MediaType] = None,
        folder_path: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[MediaFile], int]:
        """Get media files with filtering and pagination"""
        try:
            query = {"is_public": True}
            
            if media_type:
                query["media_type"] = media_type
            if folder_path:
                query["folder_path"] = folder_path
            
            # Get total count
            total_count = await self.media_files_collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Execute query
            cursor = self.media_files_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            media_docs = await cursor.to_list(length=page_size)
            
            media_files = [MediaFile(**doc) for doc in media_docs]
            
            return media_files, total_count
            
        except Exception as e:
            logger.error(f"Failed to get media files: {e}")
            return [], 0
    
    async def increment_media_usage(self, file_id: str) -> bool:
        """Increment media file usage count"""
        try:
            result = await self.media_files_collection.update_one(
                {"id": file_id},
                {
                    "$inc": {"usage_count": 1},
                    "$set": {"last_used": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment media usage: {e}")
            return False
    
    # Landing Pages Management
    async def create_landing_page(self, landing_page: LandingPage, created_by: Optional[str] = None) -> Optional[LandingPage]:
        """Create landing page"""
        try:
            landing_dict = landing_page.dict()
            landing_dict['created_by'] = created_by
            
            landing_obj = LandingPage(**landing_dict)
            
            await self.landing_pages_collection.insert_one(landing_obj.dict())
            return landing_obj
        except Exception as e:
            logger.error(f"Failed to create landing page: {e}")
            return None
    
    async def get_landing_pages(self, published_only: bool = True) -> List[LandingPage]:
        """Get landing pages"""
        try:
            query = {}
            if published_only:
                query["is_published"] = True
            
            cursor = self.landing_pages_collection.find(query).sort("created_at", -1)
            page_docs = await cursor.to_list(length=None)
            
            return [LandingPage(**doc) for doc in page_docs]
        except Exception as e:
            logger.error(f"Failed to get landing pages: {e}")
            return []
    
    async def get_landing_page(self, page_id: str = None, slug: str = None) -> Optional[LandingPage]:
        """Get landing page by ID or slug"""
        try:
            query = {}
            if page_id:
                query["id"] = page_id
            elif slug:
                query["slug"] = slug
            else:
                return None
            
            page_doc = await self.landing_pages_collection.find_one(query)
            if page_doc:
                return LandingPage(**page_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get landing page: {e}")
            return None
    
    # Content Analytics
    async def get_content_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get content analytics summary"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            analytics = {}
            
            # Blog analytics
            total_posts = await self.blog_posts_collection.count_documents({"status": BlogStatus.PUBLISHED})
            posts_this_month = await self.blog_posts_collection.count_documents({
                "status": BlogStatus.PUBLISHED,
                "published_at": {"$gte": start_date}
            })
            
            # Top posts by views
            top_posts_pipeline = [
                {"$match": {"status": BlogStatus.PUBLISHED}},
                {"$sort": {"view_count": -1}},
                {"$limit": 5},
                {"$project": {"title": 1, "slug": 1, "view_count": 1, "_id": 0}}  # Exclude _id to avoid ObjectId issues
            ]
            top_posts = await self.blog_posts_collection.aggregate(top_posts_pipeline).to_list(5)
            
            analytics["blog"] = {
                "total_posts": total_posts,
                "posts_this_month": posts_this_month,
                "top_posts": top_posts
            }
            
            # Documentation analytics
            total_docs = await self.documentation_pages_collection.count_documents({"is_published": True})
            docs_this_month = await self.documentation_pages_collection.count_documents({
                "is_published": True,
                "created_at": {"$gte": start_date}
            })
            
            analytics["documentation"] = {
                "total_pages": total_docs,
                "pages_this_month": docs_this_month
            }
            
            # Media analytics
            total_media = await self.media_files_collection.count_documents({})
            media_this_month = await self.media_files_collection.count_documents({
                "created_at": {"$gte": start_date}
            })
            
            # Media usage
            media_usage_pipeline = [
                {"$group": {"_id": "$media_type", "count": {"$sum": 1}, "total_usage": {"$sum": "$usage_count"}}},
                {"$sort": {"count": -1}},
                {"$project": {"media_type": "$_id", "count": 1, "total_usage": 1, "_id": 0}}  # Convert _id to media_type field
            ]
            media_usage = await self.media_files_collection.aggregate(media_usage_pipeline).to_list(None)
            
            analytics["media"] = {
                "total_files": total_media,
                "files_this_month": media_this_month,
                "usage_by_type": media_usage
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get content analytics: {e}")
            return {}
    
    # Sitemap Generation
    async def generate_sitemap_data(self) -> List[Dict[str, Any]]:
        """Generate sitemap data for all content"""
        try:
            sitemap_urls = []
            
            # Add blog posts
            blog_posts = await self.blog_posts_collection.find({
                "status": BlogStatus.PUBLISHED,
                "published_at": {"$lte": datetime.utcnow()}
            }).to_list(None)
            
            for post in blog_posts:
                sitemap_urls.append({
                    "loc": f"/blog/{post['slug']}",
                    "lastmod": post.get("updated_at", post.get("published_at", post["created_at"])),
                    "changefreq": "weekly",
                    "priority": 0.8
                })
            
            # Add documentation pages
            doc_pages = await self.documentation_pages_collection.find({
                "is_published": True
            }).to_list(None)
            
            for page in doc_pages:
                sitemap_urls.append({
                    "loc": f"/docs/{page['slug']}",
                    "lastmod": page.get("updated_at", page["created_at"]),
                    "changefreq": "monthly",
                    "priority": 0.7
                })
            
            # Add landing pages
            landing_pages = await self.landing_pages_collection.find({
                "is_published": True
            }).to_list(None)
            
            for page in landing_pages:
                sitemap_urls.append({
                    "loc": f"/{page['slug']}",
                    "lastmod": page.get("updated_at", page["created_at"]),
                    "changefreq": "monthly",
                    "priority": 0.9
                })
            
            return sitemap_urls
            
        except Exception as e:
            logger.error(f"Failed to generate sitemap data: {e}")
            return []